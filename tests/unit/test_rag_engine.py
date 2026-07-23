import pytest
from unittest.mock import patch, MagicMock
from app.ai.rag_engine import RAGEngine


# ============================
# _build_messages
# ============================

def test_build_messages_basico():
    engine = RAGEngine()
    messages = engine._build_messages(
        "¿Cuánto gasté?",
        {"ingresos": 500000, "gastos": 200000, "balance": 300000, "top_categoria": "Comida", "total_transacciones": 30},
        [],
    )
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "¿Cuánto gasté?" in messages[1]["content"]
    assert "$500,000" in messages[1]["content"]
    assert "$200,000" in messages[1]["content"]
    assert "$300,000" in messages[1]["content"]
    assert "Comida" in messages[1]["content"]


def test_build_messages_con_transacciones():
    engine = RAGEngine()
    txns = [
        {"texto": "Gasto de $15,000 en Comida", "relevancia": 0.9},
        {"texto": "Gasto de $5,000 en Transporte", "relevancia": 0.7},
    ]
    messages = engine._build_messages(
        "¿Cuánto gasté en comida?",
        {"ingresos": 0, "gastos": 0, "balance": 0, "top_categoria": "N/A", "total_transacciones": 0},
        txns,
    )
    assert "Transacciones relevantes" in messages[1]["content"]
    assert "Gasto de $15,000 en Comida" in messages[1]["content"]
    assert "relevancia: 0.9" in messages[1]["content"]


def test_build_messages_contexto_vacio():
    engine = RAGEngine()
    messages = engine._build_messages(
        "test",
        {},
        [],
    )
    assert "$0" in messages[1]["content"]


# ============================
# consultar (mocked)
# ============================

@patch.object(RAGEngine, "_build_messages")
@patch("app.ai.rag_engine.ProviderFactory")
@patch("app.ai.rag_engine.ChromaDBStore")
@patch("app.ai.rag_engine.metrics_collector")
def test_consultar_success(mock_metrics, mock_store_cls, mock_factory_cls, mock_build):
    mock_store = MagicMock()
    mock_store.buscar_contexto.return_value = [{"texto": "test", "relevancia": 0.9}]
    mock_store_cls.return_value = mock_store

    mock_factory = MagicMock()
    mock_factory.chat.return_value = ("Respuesta test", "ollama")
    mock_factory_cls.return_value = mock_factory

    mock_build.return_value = [{"role": "user", "content": "test"}]

    engine = RAGEngine(vector_store=mock_store, provider_factory=mock_factory)
    result = engine.consultar("user_1", "¿Cuánto gasté?", {"ingresos": 100})

    assert result["respuesta"] == "Respuesta test"
    assert result["provider"] == "ollama"
    assert result["contexto_usado"] == 1
    assert "latency_ms" in result
    mock_store.buscar_contexto.assert_called_once_with("user_1", "¿Cuánto gasté?", top_k=5)
    mock_factory.chat.assert_called_once()
    mock_metrics.record_ai_latency.assert_called_once()


@patch.object(RAGEngine, "_build_messages")
@patch("app.ai.rag_engine.ProviderFactory")
@patch("app.ai.rag_engine.ChromaDBStore")
@patch("app.ai.rag_engine.metrics_collector")
def test_consultar_sin_contexto(mock_metrics, mock_store_cls, mock_factory_cls, mock_build):
    mock_store = MagicMock()
    mock_store.buscar_contexto.return_value = []
    mock_store_cls.return_value = mock_store

    mock_factory = MagicMock()
    mock_factory.chat.return_value = ("No tengo datos", "local_rules")
    mock_factory_cls.return_value = mock_factory

    mock_build.return_value = [{"role": "user", "content": "test"}]

    engine = RAGEngine(vector_store=mock_store, provider_factory=mock_factory)
    result = engine.consultar("user_1", "test", {})

    assert result["contexto_usado"] == 0
    assert result["provider"] == "local_rules"
