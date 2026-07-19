from pydantic import BaseModel, Field
from typing import Optional


class TransactionCreate(BaseModel):
    tipo: str = Field(..., pattern="^(Ingreso|Gasto)$", examples=["Ingreso"])
    monto: float = Field(..., gt=0, examples=[50000])
    categoria: str = Field(..., min_length=1, max_length=50, examples=["Salario"])
    descripcion: str = Field("", max_length=200)
    fecha: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2026-07-19"])
    moneda: str = Field("ARS", max_length=10)


class TransactionUpdate(BaseModel):
    tipo: Optional[str] = Field(None, pattern="^(Ingreso|Gasto)$")
    monto: Optional[float] = Field(None, gt=0)
    categoria: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=200)
    fecha: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    moneda: Optional[str] = Field(None, max_length=10)


class TransactionResponse(BaseModel):
    id: str
    user_id: str
    tipo: str
    monto: float
    categoria: str
    descripcion: str
    fecha: str
    moneda: str
    created_at: Optional[str] = None


class TransactionFilter(BaseModel):
    tipo: Optional[str] = None
    categoria: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
