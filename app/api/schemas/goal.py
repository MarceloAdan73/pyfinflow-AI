from pydantic import BaseModel, Field
from typing import Optional


class GoalCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Vacaciones"])
    objetivo: float = Field(..., gt=0, examples=[500000])
    fecha_limite: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    categoria: Optional[str] = Field(None, max_length=50)


class GoalUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    objetivo: Optional[float] = Field(None, gt=0)
    ahorrado: Optional[float] = Field(None, ge=0)
    fecha_limite: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    categoria: Optional[str] = Field(None, max_length=50)


class GoalResponse(BaseModel):
    id: str
    user_id: str
    nombre: str
    objetivo: float
    ahorrado: float
    fecha_limite: Optional[str] = None
    categoria: Optional[str] = None
