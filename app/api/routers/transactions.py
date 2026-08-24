import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user, get_repositories
from app.api.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.repositories.factory import RepositoryFactory

router = APIRouter(prefix="/transactions", tags=["Transacciones"])


@router.get(
    "",
    response_model=list[TransactionResponse],
    summary="Listar transacciones",
    response_description="Lista de transacciones del usuario",
)
def list_transactions(
    tipo: str | None = Query(None, description="Filtrar por tipo: 'Ingreso' o 'Gasto'"),
    categoria: str | None = Query(None, description="Filtrar por categoría exacta"),
    fecha_inicio: str | None = Query(None, alias="fecha_inicio", description="Fecha desde (YYYY-MM-DD)"),
    fecha_fin: str | None = Query(None, alias="fecha_fin", description="Fecha hasta (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Resultados por página (1-100)"),
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Lista transacciones del usuario autenticado con filtros opcionales.

    Soporta filtrado por tipo (`Ingreso`/`Gasto`), categoría y rango de fechas.
    Resultados paginados (default: 20 por página, máximo 100).
    """
    filters = {"user_id": current_user["id"]}
    if tipo:
        filters["tipo"] = tipo
    if categoria:
        filters["categoria"] = categoria
    if fecha_inicio:
        filters["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        filters["fecha_fin"] = fecha_fin

    all_txns = repos.transactions.get_all(filters)
    start = (page - 1) * per_page
    return all_txns[start : start + per_page]


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=201,
    summary="Crear transacción",
    response_description="Transacción creada",
)
def create_transaction(
    data: TransactionCreate,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Crea una nueva transacción (ingreso o gasto).

    - **tipo**: `"Ingreso"` o `"Gasto"`
    - **monto**: monto positivo en la moneda indicada
    - **categoria**: categoría predefinida o custom
    - **fecha**: formato `YYYY-MM-DD`
    - **moneda**: default `"ARS"`
    """
    txn = repos.transactions.create({
        "id": f"txn_{uuid.uuid4().hex[:16]}",
        "user_id": current_user["id"],
        "tipo": data.tipo,
        "monto": data.monto,
        "categoria": data.categoria,
        "descripcion": data.descripcion,
        "fecha": data.fecha,
        "moneda": data.moneda,
    })
    # F8.1a: chequeo no-bloqueante de presupuesto (solo Gastos)
    if data.tipo == "Gasto":
        try:
            from app.core.alerts import alert_budget_exceeded, alert_budget_warning
            from app.services.budget_alerts import get_budget_alerts_for_user

            mes = data.fecha[:7]  # YYYY-MM
            alerts = get_budget_alerts_for_user(repos, current_user["id"], mes)
            for a in alerts:
                if a["categoria"] != data.categoria:
                    continue
                if a["excedido"]:
                    alert_budget_exceeded(
                        a["categoria"], a["limite"], a["gastado"], a["porcentaje"], mes
                    )
                elif a["porcentaje"] >= 80:
                    alert_budget_warning(
                        a["categoria"], a["limite"], a["gastado"], a["porcentaje"], mes
                    )
                break
        except Exception:
            # Nunca romper la creación de transacción por un fallo de alerta
            pass
    return txn


@router.get(
    "/{txn_id}",
    response_model=TransactionResponse,
    summary="Obtener transacción",
    response_description="Detalle de la transacción",
)
def get_transaction(
    txn_id: str,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Obtiene una transacción por su ID.

    Solo retorna la transacción si pertenece al usuario autenticado.
    Si no existe o no pertenece al usuario, retorna 404.
    """
    txn = repos.transactions.get_by_id(txn_id)
    if not txn or txn["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return txn


@router.put(
    "/{txn_id}",
    response_model=TransactionResponse,
    summary="Actualizar transacción",
    response_description="Transacción actualizada",
)
def update_transaction(
    txn_id: str,
    data: TransactionUpdate,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Actualiza parcialmente una transacción.

    Solo actualiza los campos enviados (PATCH parcial).
    La transacción debe pertenecer al usuario autenticado.
    """
    txn = repos.transactions.get_by_id(txn_id)
    if not txn or txn["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    updated = repos.transactions.update(txn_id, update_data)
    return updated


@router.delete(
    "/{txn_id}",
    status_code=204,
    summary="Eliminar transacción",
)
def delete_transaction(
    txn_id: str,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Elimina una transacción por su ID.

    La transacción debe pertenecer al usuario autenticado.
    Retorna 204 sin contenido si se eliminó correctamente.
    """
    txn = repos.transactions.get_by_id(txn_id)
    if not txn or txn["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    repos.transactions.delete(txn_id)
