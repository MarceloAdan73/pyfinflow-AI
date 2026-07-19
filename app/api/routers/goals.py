import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from app.api.deps import get_current_user, get_repositories
from app.repositories.factory import RepositoryFactory

router = APIRouter(prefix="/goals", tags=["Metas de Ahorro"])


@router.get("", response_model=list[GoalResponse])
def list_goals(
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    return repos.goals.get_all({"user_id": current_user["id"]})


@router.post("", response_model=GoalResponse, status_code=201)
def create_goal(
    data: GoalCreate,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    return repos.goals.create({
        "id": f"goal_{uuid.uuid4().hex[:16]}",
        "user_id": current_user["id"],
        "nombre": data.nombre,
        "objetivo": data.objetivo,
        "fecha_limite": data.fecha_limite,
        "categoria": data.categoria,
    })


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: str,
    data: GoalUpdate,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    goal = repos.goals.get_by_id(goal_id)
    if not goal or goal["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Meta no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    return repos.goals.update(goal_id, update_data)


@router.delete("/{goal_id}", status_code=204)
def delete_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    goal = repos.goals.get_by_id(goal_id)
    if not goal or goal["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
    repos.goals.delete(goal_id)
