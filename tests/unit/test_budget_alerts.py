
from app.services.budget_alerts import compute_budget_alerts, get_budget_alerts_for_user

# --- unit: compute_budget_alerts ---

def test_no_budgets_returns_empty():
    assert compute_budget_alerts([], []) == []


def test_sin_gastos_no_alerta():
    budgets = [{"categoria": "Comida", "limite": 50000, "mes": "2026-07"}]
    txns = []
    assert compute_budget_alerts(budgets, txns) == []


def test_gasto_bajo_threshold_no_alerta():
    budgets = [{"categoria": "Comida", "limite": 10000, "mes": "2026-07"}]
    txns = [{"tipo": "Gasto", "categoria": "Comida", "monto": 5000}]
    assert compute_budget_alerts(budgets, txns) == []


def test_warning_80_por_ciento():
    budgets = [{"categoria": "Comida", "limite": 10000, "mes": "2026-07"}]
    txns = [{"tipo": "Gasto", "categoria": "Comida", "monto": 8500}]
    alerts = compute_budget_alerts(budgets, txns)
    assert len(alerts) == 1
    assert alerts[0]["categoria"] == "Comida"
    assert alerts[0]["porcentaje"] == 85.0
    assert alerts[0]["excedido"] is False
    assert alerts[0]["gastado"] == 8500


def test_excedido_100():
    budgets = [{"categoria": "Comida", "limite": 10000, "mes": "2026-07"}]
    txns = [{"tipo": "Gasto", "categoria": "Comida", "monto": 12000}]
    alerts = compute_budget_alerts(budgets, txns)
    assert alerts[0]["porcentaje"] == 120.0
    assert alerts[0]["excedido"] is True


def test_exact_80_incluido():
    budgets = [{"categoria": "Comida", "limite": 10000, "mes": "2026-07"}]
    txns = [{"tipo": "Gasto", "categoria": "Comida", "monto": 8000}]
    alerts = compute_budget_alerts(budgets, txns)
    assert len(alerts) == 1
    assert alerts[0]["porcentaje"] == 80.0


def test_ingresos_no_cuentan():
    budgets = [{"categoria": "Comida", "limite": 10000, "mes": "2026-07"}]
    txns = [
        {"tipo": "Ingreso", "categoria": "Comida", "monto": 50000},
        {"tipo": "Gasto", "categoria": "Comida", "monto": 5000},
    ]
    assert compute_budget_alerts(budgets, txns) == []


def test_multiples_categorias_ordenado_desc():
    budgets = [
        {"categoria": "Comida", "limite": 10000, "mes": "2026-07"},
        {"categoria": "Transporte", "limite": 10000, "mes": "2026-07"},
    ]
    txns = [
        {"tipo": "Gasto", "categoria": "Comida", "monto": 8200},
        {"tipo": "Gasto", "categoria": "Transporte", "monto": 9500},
    ]
    alerts = compute_budget_alerts(budgets, txns)
    assert len(alerts) == 2
    assert alerts[0]["categoria"] == "Transporte"  # 95% > 82%
    assert alerts[1]["categoria"] == "Comida"


def test_limite_cero_ignorado():
    budgets = [{"categoria": "Comida", "limite": 0, "mes": "2026-07"}]
    txns = [{"tipo": "Gasto", "categoria": "Comida", "monto": 5000}]
    assert compute_budget_alerts(budgets, txns) == []


# --- integration con repos (db_session) ---

def test_get_budget_alerts_for_user_integration(client, db_session):
    # usa conftest: client + db_session con override
    # registramos y creamos budget + txns via repos directamente
    from app.repositories.factory import RepositoryFactory

    reg = client.post("/auth/register", json={"username": "alerttest", "password": "testpass123"})
    # obtener user_id via /auth/me
    token = reg.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    user_id = me["id"]

    factory = RepositoryFactory(db_session)
    factory.budgets.upsert(user_id, "Comida", "2026-07", 10000)
    factory.transactions.create({
        "id": "txn_test1", "user_id": user_id, "tipo": "Gasto",
        "monto": 8500, "categoria": "Comida", "descripcion": "", "fecha": "2026-07-15",
    })
    db_session.commit()

    alerts = get_budget_alerts_for_user(factory, user_id, "2026-07")
    assert len(alerts) == 1
    assert alerts[0]["categoria"] == "Comida"


def test_get_budget_alerts_sin_budgets(db_session):
    from app.repositories.factory import RepositoryFactory
    factory = RepositoryFactory(db_session)
    assert get_budget_alerts_for_user(factory, "user_fake", "2026-07") == []


# --- alerts email helpers ---

def test_alert_budget_exceeded_no_smtp(monkeypatch):
    from app.core import alerts as alert_mod
    monkeypatch.setattr(alert_mod.settings, "ALERT_EMAIL_TO", "")
    assert alert_mod.alert_budget_exceeded("Comida", 10000, 12000, 120, "2026-07") is False
    assert alert_mod.alert_budget_warning("Comida", 10000, 8500, 85, "2026-07") is False


def test_alert_budget_exceeded_con_smtp_mock(monkeypatch):
    from app.core import alerts as alert_mod

    monkeypatch.setattr(alert_mod.settings, "ALERT_EMAIL_TO", "to@example.com")
    monkeypatch.setattr(alert_mod.settings, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(alert_mod.settings, "SMTP_PORT", 587)
    monkeypatch.setattr(alert_mod.settings, "SMTP_TLS", False)
    monkeypatch.setattr(alert_mod.settings, "SMTP_USER", "")
    monkeypatch.setattr(alert_mod.settings, "SMTP_PASSWORD", "")

    sent = {}

    class FakeSMTP:
        def __init__(self, *a, **kw):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *exc):
            return False
        def starttls(self, context=None):
            pass
        def login(self, u, p):
            pass
        def send_message(self, msg):
            sent["subject"] = msg["Subject"]

    monkeypatch.setattr(alert_mod.smtplib, "SMTP", FakeSMTP)
    assert alert_mod.alert_budget_exceeded("Comida", 10000, 12000, 120, "2026-07") is True
    assert "Presupuesto excedido" in sent["subject"]
    sent.clear()
    assert alert_mod.alert_budget_warning("Comida", 10000, 8500, 85, "2026-07") is True
    assert "Alerta presupuesto" in sent["subject"]
