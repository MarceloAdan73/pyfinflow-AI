import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_repositories
from app.api.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from app.repositories.factory import RepositoryFactory

router = APIRouter(prefix="/goals", tags=["Metas de Ahorro"])


@router.get(
    "",
    response_model=list[GoalResponse],
    summary="Listar metas de ahorro",
    response_description="Lista de metas del usuario",
)
def list_goals(
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Lista todas las metas de ahorro del usuario autenticado.

    Cada meta incluye nombre, objetivo, monto ahorrado actual,
    fecha límite (opcional) y categoría (opcional).
    """
    return repos.goals.get_all({"user_id": current_user["id"]})


@router.post(
    "",
    response_model=GoalResponse,
    status_code=201,
    summary="Crear meta de ahorro",
    response_description="Meta creada",
)
def create_goal(
    data: GoalCreate,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Crea una nueva meta de ahorro.

    - **nombre**: nombre de la meta (ej: "Vacaciones")
    - **objetivo**: monto a alcanzar
    - **fecha_limite**: fecha límite opcional (`YYYY-MM-DD`)
    - **categoria**: categoría opcional para agrupar metas
    """
    return repos.goals.create({
        "id": f"goal_{uuid.uuid4().hex[:16]}",
        "user_id": current_user["id"],
        "nombre": data.nombre,
        "objetivo": data.objetivo,
        "fecha_limite": data.fecha_limite,
        "categoria": data.categoria,
    })


@router.put(
    "/{goal_id}",
    response_model=GoalResponse,
    summary="Actualizar meta de ahorro",
    response_description="Meta actualizada",
)
def update_goal(
    goal_id: str,
    data: GoalUpdate,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Actualiza parcialmente una meta de ahorro.

    Permite modificar nombre, objetivo, monto ahorrado, fecha límite y categoría.
    Solo actualiza los campos enviados. La meta debe pertenecer al usuario.
    """
    goal = repos.goals.get_by_id(goal_id)
    if not goal or goal["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Meta no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    return repos.goals.update(goal_id, update_data)


@router.delete(
    "/{goal_id}",
    status_code=204,
    summary="Eliminar meta de ahorro",
)
def delete_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Elimina una meta de ahorro por su ID.

    La meta debe pertenecer al usuario autenticado.
    Retorna 204 sin contenido si se eliminó correctamente.
    """
    goal = repos.goals.get_by_id(goal_id)
    if not goal or goal["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
    repos.goals.delete(goal_id)
