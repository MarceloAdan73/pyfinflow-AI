from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    categoria: str = Field(..., min_length=1, max_length=50, examples=["Comida"])
    limite: float = Field(..., gt=0, examples=[50000])
    mes: str = Field(..., pattern=r"^\d{4}-\d{2}$", examples=["2026-07"])


class BudgetResponse(BaseModel):
    id: str
    user_id: str
    categoria: str
    limite: float
    mes: str


class BudgetAlert(BaseModel):
    categoria: str
    limite: float
    gastado: float
    porcentaje: float
    excedido: bool
