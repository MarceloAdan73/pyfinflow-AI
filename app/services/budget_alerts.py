"""Servicio de alertas de presupuesto (Fase 8.1a).

Calcula para un usuario/mes qué categorías superan thresholds:
- warning  >= 80% del límite
- excedido >= 100%

No envía emails: solo computa datos. El envío se hace en capa router/alerts.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.repositories.factory import RepositoryFactory

WARNING_THRESHOLD = 80.0
EXCEEDED_THRESHOLD = 100.0


def _month_bounds(mes: str) -> tuple[str, str]:
    """Retorna (fecha_inicio, fecha_fin) para un mes YYYY-MM."""
    # YYYY-MM -> YYYY-MM-01 / YYYY-MM-31 (cubre todos los días, comparación lexicográfica ISO)
    return f"{mes}-01", f"{mes}-31"


def compute_budget_alerts(
    budgets: list[dict],
    transactions: list[dict],
    *,
    warning_threshold: float = WARNING_THRESHOLD,
) -> list[dict]:
    """Dado budgets y transactions ya filtrados por user+mes, retorna alertas.

    Solo retorna categorías donde porcentaje >= warning_threshold.
    Cada alerta: {categoria, limite, gastado, porcentaje, excedido}
    """
    alerts: list[dict] = []
    # Agregado por categoría (solo gastos, pero caller ya filtra tipo Gasto)
    spent_by_cat: dict[str, float] = {}
    for txn in transactions:
        if txn.get("tipo") != "Gasto":
            continue
        cat = txn.get("categoria", "")
        spent_by_cat[cat] = spent_by_cat.get(cat, 0.0) + float(txn.get("monto", 0))

    for bud in budgets:
        cat = bud["categoria"]
        limite = float(bud["limite"])
        gastado = float(spent_by_cat.get(cat, 0.0))
        if limite <= 0:
            continue
        porcentaje = round((gastado / limite) * 100, 2)
        if porcentaje >= warning_threshold:
            alerts.append(
                {
                    "categoria": cat,
                    "limite": limite,
                    "gastado": round(gastado, 2),
                    "porcentaje": porcentaje,
                    "excedido": porcentaje >= EXCEEDED_THRESHOLD,
                }
            )
    # Ordenar por porcentaje descendente (más crítico primero)
    alerts.sort(key=lambda a: a["porcentaje"], reverse=True)
    return alerts


def get_budget_alerts_for_user(
    repos: "RepositoryFactory",
    user_id: str,
    mes: str,
    *,
    warning_threshold: float = WARNING_THRESHOLD,
) -> list[dict]:
    """Orquesta repos -> compute. Filtra transacciones por rango del mes."""
    budgets = repos.budgets.get_all({"user_id": user_id, "mes": mes})
    if not budgets:
        return []

    fecha_inicio, fecha_fin = _month_bounds(mes)
    transactions = repos.transactions.get_all(
        {
            "user_id": user_id,
            "tipo": "Gasto",
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        }
    )
    return compute_budget_alerts(budgets, transactions, warning_threshold=warning_threshold)
