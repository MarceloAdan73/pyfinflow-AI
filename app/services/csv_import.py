"""Parser CSV para import de transacciones (Fase 8.2a).

Formato demo-friendly: headers flexibles (fecha, tipo, monto, categoria, descripcion, moneda)
Soporta delimitador , o ; , encoding utf-8-sig, fechas YYYY-MM-DD / DD/MM/YYYY / DD-MM-YYYY,
montos con formato US/EU via _parsear_numero.
"""

import csv
import io
from datetime import datetime

from app.utils.formatters import _parsear_numero

# límites demo
MAX_ROWS = 1000
MAX_SIZE_BYTES = 2 * 1024 * 1024  # 2MB

REQUIRED_FIELDS = {"fecha", "tipo", "monto", "categoria"}
OPTIONAL_FIELDS = {"descripcion", "moneda"}

# normalización headers
HEADER_ALIASES = {
    "fecha": {"fecha", "date", "data"},
    "tipo": {"tipo", "type", "movimiento"},
    "monto": {"monto", "importe", "amount", "valor", "value"},
    "categoria": {"categoria", "categoría", "category", "cat"},
    "descripcion": {"descripcion", "descripción", "description", "desc", "detalle", "concepto"},
    "moneda": {"moneda", "currency", "divisa"},
}

TIPO_MAP = {
    "ingreso": "Ingreso",
    "income": "Ingreso",
    "entrada": "Ingreso",
    "gasto": "Gasto",
    "expense": "Gasto",
    "egreso": "Gasto",
    "salida": "Gasto",
}


def _normalize_header(h: str) -> str:
    h = h.strip().lower()
    # remover acentos básicos para mapeo
    h = h.replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o").replace("ú", "u")
    for canonical, aliases in HEADER_ALIASES.items():
        # comparar sin acentos también
        norm_aliases = {a.replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o").replace("ú", "u") for a in aliases}
        if h in norm_aliases or h == canonical:
            return canonical
    return h  # desconocido, se ignora luego


def _parse_fecha(raw: str) -> str | None:
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    # intentar ISO con hora: 2026-07-19T00:00:00
    try:
        dt = datetime.fromisoformat(raw.replace("Z", ""))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def _parse_tipo(raw: str) -> str | None:
    key = raw.strip().lower()
    return TIPO_MAP.get(key)


def _validate_row(row: dict, row_num: int) -> tuple[dict | None, str | None]:
    """Valida fila normalizada, retorna (data, error)."""
    # campos requeridos presentes
    for field in REQUIRED_FIELDS:
        if field not in row or not str(row[field]).strip():
            return None, f"fila {row_num}: falta campo requerido '{field}'"

    fecha_norm = _parse_fecha(str(row["fecha"]))
    if not fecha_norm:
        return None, f"fila {row_num}: fecha inválida '{row['fecha']}' (use YYYY-MM-DD o DD/MM/YYYY)"

    tipo_norm = _parse_tipo(str(row["tipo"]))
    if not tipo_norm:
        return None, f"fila {row_num}: tipo inválido '{row['tipo']}' (use Ingreso/Gasto)"

    monto_val = _parsear_numero(str(row["monto"]))
    if monto_val is None or monto_val <= 0:
        return None, f"fila {row_num}: monto inválido '{row['monto']}'"

    categoria = str(row["categoria"]).strip()
    if not categoria or len(categoria) > 50:
        return None, f"fila {row_num}: categoría inválida"

    descripcion = str(row.get("descripcion", "")).strip()[:200]
    moneda = str(row.get("moneda", "ARS")).strip() or "ARS"
    if len(moneda) > 10:
        moneda = "ARS"
    moneda = moneda.upper()

    return {
        "tipo": tipo_norm,
        "monto": float(monto_val),
        "categoria": categoria,
        "descripcion": descripcion,
        "fecha": fecha_norm,
        "moneda": moneda,
    }, None


def parse_csv_bytes(content: bytes) -> tuple[list[dict], list[dict]]:
    """Parsea bytes CSV, retorna (valid_rows, errors).

    Cada error: {"row": int, "detail": str}
    """
    if len(content) > MAX_SIZE_BYTES:
        return [], [{"row": 0, "detail": f"archivo excede {MAX_SIZE_BYTES // 1024}KB"}]

    # decode utf-8-sig (maneja BOM)
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = content.decode("latin-1")
        except UnicodeDecodeError:
            return [], [{"row": 0, "detail": "encoding no soportado (use UTF-8)"}]

    if not text.strip():
        return [], [{"row": 0, "detail": "archivo vacío"}]

    # detectar delimitador
    sample = text[:2048]
    delimiter = ";" if sample.count(";") > sample.count(",") else ","

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not reader.fieldnames:
        return [], [{"row": 0, "detail": "sin encabezados"}]

    # normalizar headers
    original_fields = reader.fieldnames
    norm_map = {_normalize_header(h): h for h in original_fields}
    # verificar requeridos presentes (por alias)
    present = set(norm_map.keys())
    missing = REQUIRED_FIELDS - present
    if missing:
        return [], [{"row": 0, "detail": f"faltan columnas requeridas: {', '.join(sorted(missing))}"}]

    valid: list[dict] = []
    errors: list[dict] = []

    for idx, raw_row in enumerate(reader, start=2):  # start 2: 1 header + 1-index
        if len(valid) + len(errors) >= MAX_ROWS:
            errors.append({"row": idx, "detail": f"límite {MAX_ROWS} filas alcanzado, resto ignorado"})
            break
        # construir row normalizado
        norm_row: dict = {}
        for canon, orig in norm_map.items():
            if canon in REQUIRED_FIELDS | OPTIONAL_FIELDS:
                norm_row[canon] = raw_row.get(orig, "")
        # ignorar filas totalmente vacías
        if not any(str(v).strip() for v in norm_row.values()):
            continue
        data, err = _validate_row(norm_row, idx)
        if err:
            errors.append({"row": idx, "detail": err})
        else:
            valid.append(data)

    return valid, errors


# compat para tests que pasan str
def parse_csv_text(text: str) -> tuple[list[dict], list[dict]]:
    return parse_csv_bytes(text.encode("utf-8-sig"))
