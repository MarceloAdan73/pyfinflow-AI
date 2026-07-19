import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
)
from app.api.deps import get_current_user, get_repositories
from app.repositories.factory import RepositoryFactory

router = APIRouter(prefix="/transactions", tags=["Transacciones"])


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    tipo: str | None = Query(None),
    categoria: str | None = Query(None),
    fecha_inicio: str | None = Query(None, alias="fecha_inicio"),
    fecha_fin: str | None = Query(None, alias="fecha_fin"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    filters = {"user_id": current_user["id"]}
    if tipo:
        filters["tipo"] = tipo
    if categoria:
        filters["categoria"] = categoria
    if fecha_inicio:
        filters["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        filters["fecha_fin"] = fecha_fin

    all_txns = repos.transactions.get_all(filters)
    start = (page - 1) * per_page
    return all_txns[start : start + per_page]


@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(
    data: TransactionCreate,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    txn = repos.transactions.create({
        "id": f"txn_{uuid.uuid4().hex[:16]}",
        "user_id": current_user["id"],
        "tipo": data.tipo,
        "monto": data.monto,
        "categoria": data.categoria,
        "descripcion": data.descripcion,
        "fecha": data.fecha,
        "moneda": data.moneda,
    })
    return txn


@router.get("/{txn_id}", response_model=TransactionResponse)
def get_transaction(
    txn_id: str,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    txn = repos.transactions.get_by_id(txn_id)
    if not txn or txn["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return txn


@router.put("/{txn_id}", response_model=TransactionResponse)
def update_transaction(
    txn_id: str,
    data: TransactionUpdate,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    txn = repos.transactions.get_by_id(txn_id)
    if not txn or txn["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    updated = repos.transactions.update(txn_id, update_data)
    return updated


@router.delete("/{txn_id}", status_code=204)
def delete_transaction(
    txn_id: str,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    txn = repos.transactions.get_by_id(txn_id)
    if not txn or txn["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    repos.transactions.delete(txn_id)
