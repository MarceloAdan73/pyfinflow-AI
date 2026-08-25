
from app.services.csv_import import parse_csv_bytes, parse_csv_text


def test_parse_simple_ok():
    csv = "fecha,tipo,monto,categoria,descripcion\n2026-07-19,Gasto,1500,Comida,Almuerzo\n2026-07-20,Ingreso,50000,Salario,Sueldo\n"
    valid, errors = parse_csv_text(csv)
    assert len(valid) == 2
    assert errors == []
    assert valid[0]["tipo"] == "Gasto"
    assert valid[0]["monto"] == 1500
    assert valid[0]["fecha"] == "2026-07-19"
    assert valid[1]["tipo"] == "Ingreso"


def test_headers_alias_y_delimitador_punto_coma():
    csv = "date;type;amount;category\n19/07/2026;Gasto;1.500,50;Comida\n"
    valid, errors = parse_csv_text(csv)
    assert len(valid) == 1
    assert valid[0]["monto"] == 1500.5
    assert valid[0]["fecha"] == "2026-07-19"


def test_fechas_varias():
    csv = "fecha,tipo,monto,categoria\n19/07/2026,Gasto,100,Comida\n2026-07-20,Ingreso,200,Salario\n19-07-2026,Gasto,300,Transporte\n"
    valid, errors = parse_csv_text(csv)
    assert len(valid) == 3
    assert [v["fecha"] for v in valid] == ["2026-07-19", "2026-07-20", "2026-07-19"]


def test_tipo_case_insensitive():
    csv = "fecha,tipo,monto,categoria\ningreso,INGRESO,100,Salario\n2026-07-19,gasto,50,Comida\n"
    # first row has invalid fecha -> will be error, but tipo parsing should work for second
    valid, errors = parse_csv_text(csv)
    assert len(valid) == 1
    assert valid[0]["tipo"] == "Gasto"


def test_falta_columna_requerida():
    csv = "fecha,monto,categoria\n2026-07-19,100,Comida\n"
    valid, errors = parse_csv_text(csv)
    assert valid == []
    assert any("faltan columnas" in e["detail"] for e in errors)


def test_fila_invalida_reportada_no_aborta():
    csv = "fecha,tipo,monto,categoria\n2026-07-19,Gasto,,Comida\n2026-07-20,Gasto,200,Comida\nbad-date,Gasto,100,Comida\n"
    valid, errors = parse_csv_text(csv)
    assert len(valid) == 1
    assert len(errors) == 2
    assert valid[0]["monto"] == 200


def test_montos_eu_us():
    csv = "fecha,tipo,monto,categoria\n2026-07-19,Gasto,\"1.500,50\",Comida\n2026-07-20,Gasto,1500.50,Comida\n"
    valid, errors = parse_csv_text(csv)
    assert len(valid) == 2
    assert valid[0]["monto"] == 1500.5
    assert valid[1]["monto"] == 1500.5


def test_moneda_default_y_custom():
    csv = "fecha,tipo,monto,categoria,moneda\n2026-07-19,Gasto,100,Comida,\n2026-07-20,Gasto,100,Comida,USD\n"
    valid, errors = parse_csv_text(csv)
    assert valid[0]["moneda"] == "ARS"
    assert valid[1]["moneda"] == "USD"


def test_vacio_y_sin_headers():
    valid, errors = parse_csv_bytes(b"")
    assert valid == []
    valid, errors = parse_csv_bytes(b"col1,col2\n1,2\n")
    assert any("faltan columnas" in e["detail"] for e in errors)


def test_limite_filas():
    header = "fecha,tipo,monto,categoria\n"
    rows = "\n".join(["2026-07-19,Gasto,10,Comida"] * 1005)
    csv = header + rows
    valid, errors = parse_csv_text(csv)
    # max 1000, rest error
    assert len(valid) + len(errors) <= 1001
    assert any("límite" in e["detail"] for e in errors)


def test_archivo_grande_rechazado():
    big = b"a" * (2 * 1024 * 1024 + 1)
    valid, errors = parse_csv_bytes(big)
    assert valid == []
    assert "excede" in errors[0]["detail"]
