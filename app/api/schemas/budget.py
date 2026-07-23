from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    """Datos para crear o actualizar un presupuesto."""

    categoria: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["Comida"],
        description="Categoría del presupuesto",
    )
    limite: float = Field(
        ...,
        gt=0,
        examples=[50000],
        description="Monto máximo permitido para la categoría",
    )
    mes: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}$",
        examples=["2026-07"],
        description="Período en formato YYYY-MM",
    )


class BudgetResponse(BaseModel):
    """Presupuesto retornado por la API."""

    id: str = Field(..., examples=["bud_a1b2c3d4e5f6g7h8"], description="ID único del presupuesto")
    user_id: str = Field(..., examples=["user_a1b2c3d4e5f6g7h8"], description="ID del propietario")
    categoria: str = Field(..., examples=["Comida"], description="Categoría del presupuesto")
    limite: float = Field(..., examples=[50000], description="Límite máximo en la moneda indicada")
    mes: str = Field(..., examples=["2026-07"], description="Período YYYY-MM")


class BudgetAlert(BaseModel):
    """Alerta de presupuesto excedido o próximo a exceder."""

    categoria: str = Field(..., examples=["Comida"], description="Categoría con alerta")
    limite: float = Field(..., examples=[50000], description="Límite del presupuesto")
    gastado: float = Field(..., examples=[42000], description="Monto gastado en la categoría")
    porcentaje: float = Field(..., examples=[84.0], description="Porcentaje del límite usado")
    excedido: bool = Field(..., examples=[False], description="True si se excedió el límite")
