import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.models_db import Base
from app.core.database import Base as Base2
from app.repositories.postgres_repo import (
    TransactionRepository, BudgetRepository, GoalRepository, UserRepository
)


@pytest.fixture(scope="function")
def db_session():
    """Crea sesión de testing con SQLite en memoria"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


# ============================
# TESTS DE USER REPOSITORY
# ============================

def test_user_create(db_session):
    repo = UserRepository(db_session)
    user = repo.create({
        "id": "user_test_1",
        "username": "marcelo",
        "password_hash": "hashed_password",
        "role": "USER",
    })
    assert user["id"] == "user_test_1"
    assert user["username"] == "marcelo"
    assert user["role"] == "USER"


def test_user_get_by_id(db_session):
    repo = UserRepository(db_session)
    repo.create({
        "id": "user_test_2",
        "username": "marcelo2",
        "password_hash": "hash",
    })
    user = repo.get_by_id("user_test_2")
    assert user is not None
    assert user["username"] == "marcelo2"


def test_user_get_by_username(db_session):
    repo = UserRepository(db_session)
    repo.create({
        "id": "user_test_3",
        "username": "marcelo3",
        "password_hash": "hash",
    })
    user = repo.get_by_username("marcelo3")
    assert user is not None
    assert user["id"] == "user_test_3"


def test_user_not_found(db_session):
    repo = UserRepository(db_session)
    assert repo.get_by_id("nonexistent") is None
    assert repo.get_by_username("nonexistent") is None


# ============================
# TESTS DE TRANSACTION REPOSITORY
# ============================

def test_transaction_create(db_session):
    repo = TransactionRepository(db_session)
    txn = repo.create({
        "id": "txn_test_1",
        "user_id": "user_1",
        "tipo": "Ingreso",
        "monto": 50000,
        "categoria": "Salario",
        "fecha": "2026-07-18",
    })
    assert txn["id"] == "txn_test_1"
    assert txn["monto"] == 50000
    assert txn["tipo"] == "Ingreso"


def test_transaction_get_all_filters(db_session):
    repo = TransactionRepository(db_session)
    repo.create({"user_id": "u1", "tipo": "Ingreso", "monto": 1000, "categoria": "Salario", "fecha": "2026-07-01"})
    repo.create({"user_id": "u1", "tipo": "Gasto", "monto": 500, "categoria": "Comida", "fecha": "2026-07-02"})
    repo.create({"user_id": "u2", "tipo": "Ingreso", "monto": 2000, "categoria": "Salario", "fecha": "2026-07-03"})

    all_u1 = repo.get_all({"user_id": "u1"})
    assert len(all_u1) == 2

    only_ingresos = repo.get_all({"user_id": "u1", "tipo": "Ingreso"})
    assert len(only_ingresos) == 1
    assert only_ingresos[0]["monto"] == 1000


def test_transaction_update(db_session):
    repo = TransactionRepository(db_session)
    repo.create({"id": "txn_upd", "user_id": "u1", "tipo": "Gasto", "monto": 100, "categoria": "Comida", "fecha": "2026-07-01"})
    updated = repo.update("txn_upd", {"monto": 200})
    assert updated["monto"] == 200


def test_transaction_delete(db_session):
    repo = TransactionRepository(db_session)
    repo.create({"id": "txn_del", "user_id": "u1", "tipo": "Gasto", "monto": 100, "categoria": "Comida", "fecha": "2026-07-01"})
    assert repo.delete("txn_del") is True
    assert repo.get_by_id("txn_del") is None


def test_transaction_delete_all_for_user(db_session):
    repo = TransactionRepository(db_session)
    repo.create({"user_id": "u_del", "tipo": "Gasto", "monto": 100, "categoria": "Comida", "fecha": "2026-07-01"})
    repo.create({"user_id": "u_del", "tipo": "Ingreso", "monto": 200, "categoria": "Salario", "fecha": "2026-07-02"})
    repo.create({"user_id": "u_other", "tipo": "Gasto", "monto": 300, "categoria": "Comida", "fecha": "2026-07-01"})

    deleted = repo.delete_all_for_user("u_del")
    assert deleted == 2
    assert len(repo.get_all({"user_id": "u_del"})) == 0
    assert len(repo.get_all({"user_id": "u_other"})) == 1


# ============================
# TESTS DE BUDGET REPOSITORY
# ============================

def test_budget_upsert_create(db_session):
    repo = BudgetRepository(db_session)
    budget = repo.upsert("u1", "Comida", "2026-07", 50000)
    assert budget["categoria"] == "Comida"
    assert budget["limite"] == 50000


def test_budget_upsert_update(db_session):
    repo = BudgetRepository(db_session)
    repo.upsert("u1", "Comida", "2026-07", 50000)
    updated = repo.upsert("u1", "Comida", "2026-07", 75000)
    assert updated["limite"] == 75000
    budgets = repo.get_all({"user_id": "u1", "mes": "2026-07"})
    assert len(budgets) == 1


# ============================
# TESTS DE GOAL REPOSITORY
# ============================

def test_goal_create_and_get(db_session):
    repo = GoalRepository(db_session)
    goal = repo.create({
        "id": "goal_1",
        "user_id": "u1",
        "nombre": "Vacaciones",
        "objetivo": 500000,
        "categoria": "Viajes",
    })
    assert goal["nombre"] == "Vacaciones"
    assert goal["objetivo"] == 500000
    assert goal["ahorrado"] == 0.0


def test_goal_update_ahorrado(db_session):
    repo = GoalRepository(db_session)
    repo.create({
        "id": "goal_upd",
        "user_id": "u1",
        "nombre": "Auto",
        "objetivo": 2000000,
    })
    updated = repo.update("goal_upd", {"ahorrado": 500000})
    assert updated["ahorrado"] == 500000
