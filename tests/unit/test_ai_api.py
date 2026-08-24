from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.main import app
from app.core.database import get_db
from app.core.models_db import Base


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield session
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    return TestClient(app)


def _get_auth_header(client):
    response = client.post("/auth/register", json={
        "username": "ai_test_user",
        "password": "testpass123",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================
# AI: CHAT
# ============================

@patch("app.api.routers.ai.RAGEngine")
def test_ai_chat_success(mock_rag_cls, client):
    header = _get_auth_header(client)

    mock_engine = MagicMock()
    mock_engine.consultar.return_value = {
        "respuesta": "Tu gasto en comida fue $45,000",
        "provider": "local_rules",
        "contexto_usado": 3,
        "latency_ms": 150.0,
    }
    mock_rag_cls.return_value = mock_engine

    response = client.post("/ai/chat", json={
        "pregunta": "¿Cuánto gasté en comida?"
    }, headers=header)
    assert response.status_code == 200
    data = response.json()
    assert "respuesta" in data
    assert data["provider"] == "local_rules"


def test_ai_chat_unauthorized(client):
    response = client.post("/ai/chat", json={
        "pregunta": "test"
    })
    assert response.status_code == 401


def test_ai_chat_empty_question(client):
    header = _get_auth_header(client)
    response = client.post("/ai/chat", json={
        "pregunta": ""
    }, headers=header)
    assert response.status_code == 422


@patch("app.api.routers.ai.RAGEngine")
def test_ai_chat_rate_limiting(mock_rag_cls, client):
    """Después del límite configurado, /ai/chat retorna 429 (roadmap 5.7)."""
    from app.ai.rate_limiter import AI_RATE_LIMIT, reset_ai_rate_limit

    header = _get_auth_header(client)

    mock_engine = MagicMock()
    mock_engine.consultar.return_value = {
        "respuesta": "ok",
        "provider": "local_rules",
        "contexto_usado": 0,
        "latency_ms": 1.0,
    }
    mock_rag_cls.return_value = mock_engine

    me = client.get("/auth/me", headers=header)
    user_id = me.json()["id"]
    reset_ai_rate_limit(user_id)

    try:
        codes = []
        for _ in range(AI_RATE_LIMIT + 1):
            r = client.post("/ai/chat", json={"pregunta": "test"}, headers=header)
            codes.append(r.status_code)
        assert all(c == 200 for c in codes[:AI_RATE_LIMIT])
        assert codes[AI_RATE_LIMIT] == 429
    finally:
        reset_ai_rate_limit(user_id)


# ============================
# AI: HISTORY
# ============================

@patch("app.api.routers.ai.ChatMemoryService")
def test_ai_history_success(mock_memory_cls, client):
    header = _get_auth_header(client)

    mock_memory = MagicMock()
    mock_memory.cargar_historial.return_value = [
        {"id": "1", "user_id": "u1", "role": "user", "content": "Hola", "provider": None, "tokens_used": 0, "created_at": "2026-07-20"},
    ]
    mock_memory_cls.return_value = mock_memory

    response = client.get("/ai/history", headers=header)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@patch("app.api.routers.ai.ChatMemoryService")
def test_ai_history_clear(mock_memory_cls, client):
    header = _get_auth_header(client)

    mock_memory = MagicMock()
    mock_memory.limpiar_historial.return_value = 5
    mock_memory_cls.return_value = mock_memory

    response = client.delete("/ai/history", headers=header)
    assert response.status_code == 204


# ============================
# AI: INSIGHTS
# ============================

def test_ai_insights_success(client):
    header = _get_auth_header(client)
    response = client.get("/ai/insights", headers=header)
    assert response.status_code == 200
    data = response.json()
    assert "tendencias" in data
    assert "prediccion" in data
    assert "anomalias" in data
    assert "insights" in data


def test_ai_insights_unauthorized(client):
    response = client.get("/ai/insights")
    assert response.status_code == 401


# ============================
# AI: SUGGESTIONS
# ============================

def test_ai_suggestions_success(client):
    header = _get_auth_header(client)
    response = client.get("/ai/suggestions", headers=header)
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0


def test_ai_suggestions_unauthorized(client):
    response = client.get("/ai/suggestions")
    assert response.status_code == 401


# ============================
# AI: STATUS
# ============================

def test_ai_status_success(client):
    response = client.get("/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "active_provider" in data
    assert "chromadb_available" in data
