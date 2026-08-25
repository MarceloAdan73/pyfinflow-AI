"""Tests API para GET /budgets/alerts (F8.1a)."""

def _register(client, username):
    reg = client.post("/auth/register", json={"username": username, "password": "testpass123"})
    assert reg.status_code == 201
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


def test_alerts_unauthorized(client):
    r = client.get("/budgets/alerts?mes=2026-07")
    assert r.status_code in (401, 403)


def test_alerts_vacio_sin_presupuestos(client):
    headers = _register(client, "alert_api_empty")
    r = client.get("/budgets/alerts?mes=2026-07", headers=headers)
    assert r.status_code == 200
    assert r.json() == []


def test_alerts_warning_y_excedido(client):
    headers = _register(client, "alert_api_warn")
    # presupuestos
    client.post("/budgets", json={"categoria": "Comida", "limite": 10000, "mes": "2026-07"}, headers=headers)
    client.post("/budgets", json={"categoria": "Transporte", "limite": 10000, "mes": "2026-07"}, headers=headers)
    # gastos
    client.post("/transactions", json={"tipo": "Gasto", "monto": 8500, "categoria": "Comida", "fecha": "2026-07-10"}, headers=headers)
    client.post("/transactions", json={"tipo": "Gasto", "monto": 12000, "categoria": "Transporte", "fecha": "2026-07-12"}, headers=headers)

    r = client.get("/budgets/alerts?mes=2026-07", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    # orden descendente por porcentaje: Transporte 120% primero
    assert data[0]["categoria"] == "Transporte"
    assert data[0]["excedido"] is True
    assert data[0]["porcentaje"] == 120.0
    assert data[1]["categoria"] == "Comida"
    assert data[1]["excedido"] is False


def test_alerts_no_incluye_bajo_80(client):
    headers = _register(client, "alert_api_low")
    client.post("/budgets", json={"categoria": "Comida", "limite": 10000, "mes": "2026-07"}, headers=headers)
    client.post("/transactions", json={"tipo": "Gasto", "monto": 5000, "categoria": "Comida", "fecha": "2026-07-10"}, headers=headers)
    r = client.get("/budgets/alerts?mes=2026-07", headers=headers)
    assert r.json() == []


def test_alerts_otro_mes_no_cuenta(client):
    headers = _register(client, "alert_api_otro_mes")
    client.post("/budgets", json={"categoria": "Comida", "limite": 10000, "mes": "2026-07"}, headers=headers)
    # gasto en agosto no debe activar alerta de julio
    client.post("/transactions", json={"tipo": "Gasto", "monto": 12000, "categoria": "Comida", "fecha": "2026-08-01"}, headers=headers)
    r = client.get("/budgets/alerts?mes=2026-07", headers=headers)
    assert r.json() == []
    r2 = client.get("/budgets/alerts?mes=2026-08", headers=headers)
    # agosto no tiene presupuesto, tampoco alerta
    assert r2.json() == []


def test_alerts_mes_invalido_422(client):
    headers = _register(client, "alert_api_422")
    r = client.get("/budgets/alerts?mes=2026-7", headers=headers)
    assert r.status_code == 422


def test_alerts_no_mezcla_usuarios(client):
    h1 = _register(client, "alert_user1")
    h2 = _register(client, "alert_user2")
    client.post("/budgets", json={"categoria": "Comida", "limite": 10000, "mes": "2026-07"}, headers=h1)
    client.post("/transactions", json={"tipo": "Gasto", "monto": 12000, "categoria": "Comida", "fecha": "2026-07-10"}, headers=h1)
    r = client.get("/budgets/alerts?mes=2026-07", headers=h2)
    assert r.json() == []


def test_create_transaction_dispara_email_no_bloqueante(client, monkeypatch):
    """POST /transactions con gasto excedido intenta enviar email pero no falla si SMTP falla."""
    from app.core import alerts as alert_mod
    called = {}

    def fake_exceeded(*a, **kw):
        called["exceeded"] = True
        return True

    monkeypatch.setattr(alert_mod, "send_alert_email", lambda *a, **kw: True)
    monkeypatch.setattr("app.core.alerts.send_alert_email", lambda *a, **kw: True)
    # monkeypatch dentro del flujo: el router importa alerts dentro de la función, así que patch app.core.alerts
    monkeypatch.setattr(alert_mod, "alert_budget_exceeded", fake_exceeded)
    monkeypatch.setattr(alert_mod, "alert_budget_warning", lambda *a, **kw: False)

    headers = _register(client, "alert_hook_user")
    client.post("/budgets", json={"categoria": "Comida", "limite": 10000, "mes": "2026-07"}, headers=headers)
    # gasto que excede
    r = client.post("/transactions", json={"tipo": "Gasto", "monto": 12000, "categoria": "Comida", "fecha": "2026-07-15"}, headers=headers)
    assert r.status_code == 201
    assert called.get("exceeded") is True

    # si el envío falla, la transacción igual se crea
    def raising(*a, **kw):
        raise RuntimeError("smtp down")

    monkeypatch.setattr(alert_mod, "alert_budget_exceeded", raising)
    r2 = client.post("/transactions", json={"tipo": "Gasto", "monto": 1000, "categoria": "Comida", "fecha": "2026-07-16"}, headers=headers)
    assert r2.status_code == 201
