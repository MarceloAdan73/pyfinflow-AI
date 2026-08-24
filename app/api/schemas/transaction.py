from typing import Optional

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    """Datos para crear una nueva transacción."""

    tipo: str = Field(
        ...,
        pattern="^(Ingreso|Gasto)$",
        examples=["Ingreso"],
        description="Tipo de transacción: 'Ingreso' o 'Gasto'",
    )
    monto: float = Field(
        ...,
        gt=0,
        examples=[50000],
        description="Monto positivo en la moneda indicada",
    )
    categoria: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["Salario"],
        description="Categoría predefinida o custom del usuario",
    )
    descripcion: str = Field(
        "",
        max_length=200,
        examples=["Sueldo mensual de julio"],
        description="Descripción opcional (máximo 200 caracteres)",
    )
    fecha: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2026-07-19"],
        description="Fecha en formato YYYY-MM-DD",
    )
    moneda: str = Field(
        "ARS",
        max_length=10,
        examples=["ARS"],
        description="Código de moneda (default: ARS)",
    )


class TransactionUpdate(BaseModel):
    """Datos para actualizar parcialmente una transacción (PATCH)."""

    tipo: Optional[str] = Field(None, pattern="^(Ingreso|Gasto)$", description="Nuevo tipo")
    monto: Optional[float] = Field(None, gt=0, description="Nuevo monto")
    categoria: Optional[str] = Field(None, min_length=1, max_length=50, description="Nueva categoría")
    descripcion: Optional[str] = Field(None, max_length=200, description="Nueva descripción")
    fecha: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Nueva fecha")
    moneda: Optional[str] = Field(None, max_length=10, description="Nueva moneda")


class TransactionResponse(BaseModel):
    """Transacción retornada por la API."""

    id: str = Field(..., examples=["txn_a1b2c3d4e5f6g7h8"], description="ID único de la transacción")
    user_id: str = Field(..., examples=["user_a1b2c3d4e5f6g7h8"], description="ID del propietario")
    tipo: str = Field(..., examples=["Gasto"], description="Tipo: Ingreso o Gasto")
    monto: float = Field(..., examples=[15000], description="Monto de la transacción")
    categoria: str = Field(..., examples=["Comida"], description="Categoría")
    descripcion: str = Field(..., examples=["Almuerzo en restaurant"], description="Descripción")
    fecha: str = Field(..., examples=["2026-07-19"], description="Fecha YYYY-MM-DD")
    moneda: str = Field(..., examples=["ARS"], description="Moneda")
    created_at: Optional[str] = Field(None, examples=["2026-07-19T14:30:00"], description="Timestamp de creación")


class TransactionFilter(BaseModel):
    """Filtros para buscar transacciones."""

    tipo: Optional[str] = Field(None, description="Filtrar por tipo: Ingreso o Gasto")
    categoria: Optional[str] = Field(None, description="Filtrar por categoría exacta")
    fecha_inicio: Optional[str] = Field(None, description="Fecha desde YYYY-MM-DD")
    fecha_fin: Optional[str] = Field(None, description="Fecha hasta YYYY-MM-DD")
    page: int = Field(1, ge=1, description="Página actual")
    per_page: int = Field(20, ge=1, le=100, description="Resultados por página")
