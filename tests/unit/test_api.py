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


# ============================
# HEALTH CHECK
# ============================

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ============================
# AUTH: REGISTER
# ============================

def test_register_success(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "testpass123",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate(client):
    client.post("/auth/register", json={"username": "dup", "password": "testpass123"})
    response = client.post("/auth/register", json={"username": "dup", "password": "testpass123"})
    assert response.status_code == 409


def test_register_short_username(client):
    response = client.post("/auth/register", json={"username": "ab", "password": "testpass123"})
    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post("/auth/register", json={"username": "validuser", "password": "123"})
    assert response.status_code == 422


def test_register_deshabilitado_en_produccion(client, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "ALLOW_REGISTRATION", False)
    response = client.post("/auth/register", json={"username": "blocked", "password": "testpass123"})
    assert response.status_code == 403# ============================
# AUTH: LOGIN
# ============================

def test_login_success(client):
    client.post("/auth/register", json={"username": "logintest", "password": "testpass123"})
    response = client.post("/auth/login", json={
        "username": "logintest",
        "password": "testpass123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "wrongpw", "password": "testpass123"})
    response = client.post("/auth/login", json={
        "username": "wrongpw",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={
        "username": "ghost",
        "password": "testpass123",
    })
    assert response.status_code == 401


def test_login_rate_limiting(client):
    """5 intentos fallidos permitidos, el 6to retorna 429 (roadmap 3.8)."""
    from app.core.auth import limpiar_intento

    client.post("/auth/register", json={"username": "rluser", "password": "testpass123"})
    limpiar_intento("testclient")

    try:
        codes = []
        for _ in range(6):
            r = client.post("/auth/login", json={
                "username": "rluser",
                "password": "wrongpassword",
            })
            codes.append(r.status_code)
        assert codes[:5] == [401] * 5
        assert codes[5] == 429
    finally:
        limpiar_intento("testclient")


def test_login_success_resetea_contador(client):
    """Después de un login exitoso el contador de intentos se limpia."""
    from app.core.auth import limpiar_intento

    client.post("/auth/register", json={"username": "rlreset", "password": "testpass123"})
    limpiar_intento("testclient")

    try:
        for _ in range(4):
            client.post("/auth/login", json={"username": "rlreset", "password": "bad"})
        ok = client.post("/auth/login", json={"username": "rlreset", "password": "testpass123"})
        assert ok.status_code == 200

        for _ in range(4):
            r = client.post("/auth/login", json={"username": "rlreset", "password": "bad"})
            assert r.status_code == 401
    finally:
        limpiar_intento("testclient")


# ============================
# AUTH: REFRESH
# ============================

def test_refresh_success(client):
    reg = client.post("/auth/register", json={"username": "refreshtest", "password": "testpass123"})
    refresh_token = reg.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_invalid_token(client):
    response = client.post("/auth/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == 401


# ============================
# AUTH: ME
# ============================

def test_get_me(client):
    reg = client.post("/auth/register", json={"username": "metest", "password": "testpass123"})
    token = reg.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "metest"
    assert response.json()["role"] == "USER"


def test_get_me_no_token(client):
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_get_me_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401


# ============================
# TRANSACTIONS: CRUD
# ============================

def get_auth_header(client):
    reg = client.post("/auth/register", json={"username": "txnuser", "password": "testpass123"})
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


def test_create_transaction(client):
    headers = get_auth_header(client)
    response = client.post("/transactions", json={
        "tipo": "Ingreso",
        "monto": 50000,
        "categoria": "Salario",
        "fecha": "2026-07-19",
    }, headers=headers)
    assert response.status_code == 201
    assert response.json()["tipo"] == "Ingreso"
    assert response.json()["monto"] == 50000


def test_list_transactions(client):
    headers = get_auth_header(client)
    client.post("/transactions", json={
        "tipo": "Ingreso", "monto": 1000, "categoria": "Salario", "fecha": "2026-07-01",
    }, headers=headers)
    client.post("/transactions", json={
        "tipo": "Gasto", "monto": 500, "categoria": "Comida", "fecha": "2026-07-02",
    }, headers=headers)

    response = client.get("/transactions", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_transactions_filter_tipo(client):
    headers = get_auth_header(client)
    client.post("/transactions", json={
        "tipo": "Ingreso", "monto": 1000, "categoria": "Salario", "fecha": "2026-07-01",
    }, headers=headers)
    client.post("/transactions", json={
        "tipo": "Gasto", "monto": 500, "categoria": "Comida", "fecha": "2026-07-02",
    }, headers=headers)

    response = client.get("/transactions?tipo=Ingreso", headers=headers)
    assert len(response.json()) == 1
    assert response.json()[0]["tipo"] == "Ingreso"


def test_get_transaction_by_id(client):
    headers = get_auth_header(client)
    created = client.post("/transactions", json={
        "tipo": "Gasto", "monto": 200, "categoria": "Comida", "fecha": "2026-07-19",
    }, headers=headers)
    txn_id = created.json()["id"]

    response = client.get(f"/transactions/{txn_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == txn_id


def test_update_transaction(client):
    headers = get_auth_header(client)
    created = client.post("/transactions", json={
        "tipo": "Gasto", "monto": 200, "categoria": "Comida", "fecha": "2026-07-19",
    }, headers=headers)
    txn_id = created.json()["id"]

    response = client.put(f"/transactions/{txn_id}", json={"monto": 350}, headers=headers)
    assert response.status_code == 200
    assert response.json()["monto"] == 350


def test_delete_transaction(client):
    headers = get_auth_header(client)
    created = client.post("/transactions", json={
        "tipo": "Gasto", "monto": 200, "categoria": "Comida", "fecha": "2026-07-19",
    }, headers=headers)
    txn_id = created.json()["id"]

    response = client.delete(f"/transactions/{txn_id}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/transactions/{txn_id}", headers=headers)
    assert response.status_code == 404


def test_unauthorized_transaction(client):
    response = client.get("/transactions")
    assert response.status_code in (401, 403)


# ============================
# BUDGETS
# ============================

def get_budget_auth_header(client):
    reg = client.post("/auth/register", json={"username": "budgetuser", "password": "testpass123"})
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


def test_create_budget(client):
    headers = get_budget_auth_header(client)
    response = client.post("/budgets", json={
        "categoria": "Comida",
        "limite": 50000,
        "mes": "2026-07",
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["limite"] == 50000


def test_upsert_budget_updates(client):
    headers = get_budget_auth_header(client)
    client.post("/budgets", json={
        "categoria": "Comida", "limite": 50000, "mes": "2026-07",
    }, headers=headers)

    response = client.post("/budgets", json={
        "categoria": "Comida", "limite": 75000, "mes": "2026-07",
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["limite"] == 75000


def test_list_budgets(client):
    headers = get_budget_auth_header(client)
    client.post("/budgets", json={
        "categoria": "Comida", "limite": 50000, "mes": "2026-07",
    }, headers=headers)
    client.post("/budgets", json={
        "categoria": "Transporte", "limite": 20000, "mes": "2026-07",
    }, headers=headers)

    response = client.get("/budgets?mes=2026-07", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


# ============================
# GOALS
# ============================

def get_goal_auth_header(client):
    reg = client.post("/auth/register", json={"username": "goaluser", "password": "testpass123"})
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


def test_create_goal(client):
    headers = get_goal_auth_header(client)
    response = client.post("/goals", json={
        "nombre": "Vacaciones",
        "objetivo": 500000,
        "categoria": "Viajes",
    }, headers=headers)
    assert response.status_code == 201
    assert response.json()["nombre"] == "Vacaciones"
    assert response.json()["ahorrado"] == 0.0


def test_update_goal(client):
    headers = get_goal_auth_header(client)
    created = client.post("/goals", json={
        "nombre": "Auto", "objetivo": 2000000,
    }, headers=headers)
    goal_id = created.json()["id"]

    response = client.put(f"/goals/{goal_id}", json={"ahorrado": 500000}, headers=headers)
    assert response.status_code == 200
    assert response.json()["ahorrado"] == 500000


def test_delete_goal(client):
    headers = get_goal_auth_header(client)
    created = client.post("/goals", json={
        "nombre": "Auto", "objetivo": 2000000,
    }, headers=headers)
    goal_id = created.json()["id"]

    response = client.delete(f"/goals/{goal_id}", headers=headers)
    assert response.status_code == 204


def test_list_goals(client):
    headers = get_goal_auth_header(client)
    client.post("/goals", json={"nombre": "Viaje", "objetivo": 300000}, headers=headers)
    client.post("/goals", json={"nombre": "Auto", "objetivo": 2000000}, headers=headers)

    response = client.get("/goals", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


# ============================
# METRICS
# ============================

def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "requests_per_minute" in data
    assert "errors" in data


def test_metrics_prometheus(client):
    response = client.get("/metrics/prometheus")
    assert response.status_code == 200
    assert response.text.startswith("# HELP")
    assert "pyfinflow_uptime_seconds" in response.text


# ============================
# DEMO LOGIN
# ============================

def test_demo_login_crea_usuario_y_devuelve_tokens(client):
    response = client.post("/auth/demo")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_demo_seed_crea_datos_de_ejemplo(client):
    from datetime import date

    headers = get_demo_auth_header(client)
    txns = client.get("/transactions", headers=headers)
    assert txns.status_code == 200
    assert len(txns.json()) > 0

    mes = date.today().strftime("%Y-%m")
    budgets = client.get(f"/budgets?mes={mes}", headers=headers)
    assert budgets.status_code == 200
    assert len(budgets.json()) > 0

    goals = client.get("/goals", headers=headers)
    assert goals.status_code == 200
    assert len(goals.json()) > 0


def get_demo_auth_header(client):
    demo = client.post("/auth/demo")
    token = demo.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
