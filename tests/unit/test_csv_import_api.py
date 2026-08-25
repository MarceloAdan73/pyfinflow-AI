
def _register(client, username):
    reg = client.post("/auth/register", json={"username": username, "password": "testpass123"})
    assert reg.status_code == 201
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


def test_import_unauthorized(client):
    csv = b"fecha,tipo,monto,categoria\n2026-07-19,Gasto,100,Comida\n"
    r = client.post("/transactions/import", files={"file": ("test.csv", csv, "text/csv")})
    assert r.status_code in (401, 403)


def test_import_ok(client):
    headers = _register(client, "csv_ok")
    csv = "fecha,tipo,monto,categoria,descripcion\n2026-07-19,Gasto,1500,Comida,Almuerzo\n2026-07-20,Ingreso,50000,Salario,Sueldo\n".encode()
    r = client.post("/transactions/import", files={"file": ("test.csv", csv, "text/csv")}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["imported"] == 2
    assert data["skipped"] == 0
    assert data["total_rows"] == 2
    # verificar que se crearon
    lst = client.get("/transactions", headers=headers).json()
    assert len(lst) == 2


def test_import_con_errores_parciales(client):
    headers = _register(client, "csv_partial")
    csv = "fecha,tipo,monto,categoria\n2026-07-19,Gasto,,Comida\n2026-07-20,Gasto,200,Comida\n".encode()
    r = client.post("/transactions/import", files={"file": ("test.csv", csv, "text/csv")}, headers=headers)
    assert r.status_code == 200
    assert r.json()["imported"] == 1
    assert r.json()["skipped"] == 1
    assert len(r.json()["errors"]) == 1


def test_import_vacio_400(client):
    headers = _register(client, "csv_empty")
    r = client.post("/transactions/import", files={"file": ("empty.csv", b"", "text/csv")}, headers=headers)
    assert r.status_code in (400, 200)  # si pasa parser, retorna 200 con error fila 0
    # si es 200, debe reportar error
    if r.status_code == 200:
        assert r.json()["skipped"] >= 1


def test_import_no_mezcla_usuarios(client):
    h1 = _register(client, "csv_user1")
    h2 = _register(client, "csv_user2")
    csv = "fecha,tipo,monto,categoria\n2026-07-19,Gasto,100,Comida\n".encode()
    client.post("/transactions/import", files={"file": ("test.csv", csv, "text/csv")}, headers=h1)
    lst2 = client.get("/transactions", headers=h2).json()
    assert len(lst2) == 0
    lst1 = client.get("/transactions", headers=h1).json()
    assert len(lst1) == 1


def test_import_delimitador_punto_coma_y_fecha_ddmmyyyy(client):
    headers = _register(client, "csv_semicolon")
    csv = "fecha;tipo;monto;categoria\n19/07/2026;Gasto;1.500,50;Comida\n".encode()
    r = client.post("/transactions/import", files={"file": ("test.csv", csv, "text/csv")}, headers=headers)
    assert r.json()["imported"] == 1
    txn = client.get("/transactions", headers=headers).json()[0]
    assert txn["monto"] == 1500.5
    assert txn["fecha"] == "2026-07-19"


def test_import_falta_columna_requerida(client):
    headers = _register(client, "csv_missing_col")
    csv = "fecha,monto,categoria\n2026-07-19,100,Comida\n".encode()
    r = client.post("/transactions/import", files={"file": ("test.csv", csv, "text/csv")}, headers=headers)
    assert r.status_code == 200
    assert r.json()["imported"] == 0
    assert r.json()["skipped"] >= 1
