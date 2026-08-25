import re
from datetime import datetime
from random import randint

from app.core.constants import MONEDAS


def generar_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    random_part = randint(100, 999)
    return f"txn_{timestamp}_{random_part}"


def formatear_monto(valor, moneda="ARS"):
    info = MONEDAS[moneda]
    if valor == int(valor):
        return f"{info['simbolo']} {int(valor):,}"
    return f"{info['simbolo']} {valor:,.2f}"


def _parsear_numero(texto_numero):
    texto = texto_numero.strip()

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        partes = texto.split(",")
        if len(partes) == 2:
            parte_decimal = partes[1]
            parte_entera = partes[0]

            if len(parte_decimal) == 3 and parte_entera.replace(".", "").isdigit():
                texto = texto.replace(",", "")
            elif len(parte_decimal) <= 2:
                texto = texto.replace(",", ".")
            else:
                texto = texto.replace(",", "")
        elif texto.count(",") > 1:
            texto = texto.replace(",", "")

    try:
        return float(texto)
    except ValueError:
        return None


def detectar_moneda(texto):
    if not texto:
        return None, None

    nums = re.findall(r"[\d.,]+", texto)
    if nums:
        numero = _parsear_numero(nums[0])
        if numero is not None:
            return numero, "ARS"

    return None, None
