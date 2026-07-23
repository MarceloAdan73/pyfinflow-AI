from pydantic import BaseModel, Field
from typing import Optional


class GoalCreate(BaseModel):
    """Datos para crear una nueva meta de ahorro."""

    nombre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Vacaciones"],
        description="Nombre descriptivo de la meta",
    )
    objetivo: float = Field(
        ...,
        gt=0,
        examples=[500000],
        description="Monto objetivo a alcanzar",
    )
    fecha_limite: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2026-12-31"],
        description="Fecha límite opcional (YYYY-MM-DD)",
    )
    categoria: Optional[str] = Field(
        None,
        max_length=50,
        examples=["Viajes"],
        description="Categoría para agrupar metas",
    )


class GoalUpdate(BaseModel):
    """Datos para actualizar parcialmente una meta de ahorro."""

    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nuevo nombre")
    objetivo: Optional[float] = Field(None, gt=0, description="Nuevo monto objetivo")
    ahorrado: Optional[float] = Field(None, ge=0, description="Monto ahorrado actualizado")
    fecha_limite: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Nueva fecha límite")
    categoria: Optional[str] = Field(None, max_length=50, description="Nueva categoría")


class GoalResponse(BaseModel):
    """Meta de ahorro retornada por la API."""

    id: str = Field(..., examples=["goal_a1b2c3d4e5f6g7h8"], description="ID único de la meta")
    user_id: str = Field(..., examples=["user_a1b2c3d4e5f6g7h8"], description="ID del propietario")
    nombre: str = Field(..., examples=["Vacaciones Europa"], description="Nombre de la meta")
    objetivo: float = Field(..., examples=[500000], description="Monto objetivo")
    ahorrado: float = Field(..., examples=[125000], description="Monto ahorrado actualmente")
    fecha_limite: Optional[str] = Field(None, examples=["2026-12-31"], description="Fecha límite")
    categoria: Optional[str] = Field(None, examples=["Viajes"], description="Categoría")
