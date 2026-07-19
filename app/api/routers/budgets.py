from fastapi import APIRouter, Depends, Query

from app.api.schemas.budget import BudgetCreate, BudgetResponse
from app.api.deps import get_current_user, get_repositories
from app.repositories.factory import RepositoryFactory

router = APIRouter(prefix="/budgets", tags=["Presupuestos"])


@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    mes: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    return repos.budgets.get_all({"user_id": current_user["id"], "mes": mes})


@router.post("", response_model=BudgetResponse)
def upsert_budget(
    data: BudgetCreate,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    return repos.budgets.upsert(
        user_id=current_user["id"],
        categoria=data.categoria,
        limite=data.limite,
        mes=data.mes,
    )
