from dataclasses import asdict, dataclass


@dataclass
class Transaccion:
    id: str
    tipo: str
    monto: float
    categoria: str
    descripcion: str
    fecha: str
    moneda: str

    def to_dict(self):
        return asdict(self)


def icon_fa(tipo):
    iconos = {
        "ingreso": "\U0001f7e2",
        "gasto": "\U0001f534",
        "robot": "\U0001f916",
        "bienvenida": "\u2728",
        "mensaje": "\U0001f4ac",
        "enviar": "\U0001f4e4",
        "check": "\u2705",
        "warning": "\u26a0\ufe0f",
        "error": "\u274c",
        "ingresos_titulo": "\U0001f7e2",
        "gastos_titulo": "\U0001f534",
        "presupuesto_ok": "\u2705",
        "presupuesto_warn": "\u26a0\ufe0f",
        "presupuesto_alert": "\U0001f6a8",
        "online": "\U0001f7e2",
        "offline": "\U0001f534",
    }
    return iconos.get(tipo, "")


def icono_tipo_transaccion(tipo):
    return "\U0001f7e2" if tipo == "Ingreso" else "\U0001f534"
