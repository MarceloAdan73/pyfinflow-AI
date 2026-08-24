from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_repositories
from app.api.schemas.budget import BudgetCreate, BudgetResponse
from app.repositories.factory import RepositoryFactory

router = APIRouter(prefix="/budgets", tags=["Presupuestos"])


@router.get(
    "",
    response_model=list[BudgetResponse],
    summary="Listar presupuestos del mes",
    response_description="Presupuestos del período solicitado",
)
def list_budgets(
    mes: str = Query(
        ...,
        pattern=r"^\d{4}-\d{2}$",
        description="Período en formato YYYY-MM (ej: 2026-07)",
        examples=["2026-07"],
    ),
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Lista los presupuestos del usuario para un mes específico.

    Retorna todos los presupuestos configurados para el mes indicado.
    Cada presupuesto incluye categoría, límite y porcentaje de uso.
    """
    return repos.budgets.get_all({"user_id": current_user["id"], "mes": mes})


@router.post(
    "",
    response_model=BudgetResponse,
    summary="Crear o actualizar presupuesto",
    response_description="Presupuesto creado o actualizado",
)
def upsert_budget(
    data: BudgetCreate,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Crea o actualiza un presupuesto (upsert).

    Si ya existe un presupuesto para la misma categoría y mes,
    actualiza el límite. Si no existe, lo crea.

    - **categoria**: categoría del presupuesto
    - **límite**: monto máximo permitido en la moneda indicada
    - **mes**: período en formato `YYYY-MM`
    """
    return repos.budgets.upsert(
        user_id=current_user["id"],
        categoria=data.categoria,
        limite=data.limite,
        mes=data.mes,
    )
