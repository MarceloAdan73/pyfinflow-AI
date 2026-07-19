import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.models_db import (
    User, Transaction, Budget, Goal, CustomCategory, UserConfig
)
from app.repositories.base_repo import BaseRepository


class TransactionRepository(BaseRepository):
    """Repository para transacciones"""

    def create(self, data: dict) -> dict:
        txn = Transaction(
            id=data.get("id", f"txn_{uuid.uuid4().hex[:16]}"),
            user_id=data["user_id"],
            tipo=data["tipo"],
            monto=data["monto"],
            categoria=data["categoria"],
            descripcion=data.get("descripcion", ""),
            fecha=data["fecha"],
            moneda=data.get("moneda", "ARS"),
        )
        self.db.add(txn)
        self.db.flush()
        return self._to_dict(txn)

    def get_by_id(self, id: str) -> Optional[dict]:
        txn = self.db.query(Transaction).filter(Transaction.id == id).first()
        return self._to_dict(txn) if txn else None

    def get_all(self, filters: dict = None) -> list[dict]:
        query = self.db.query(Transaction)
        if filters:
            if filters.get("user_id"):
                query = query.filter(Transaction.user_id == filters["user_id"])
            if filters.get("tipo"):
                query = query.filter(Transaction.tipo == filters["tipo"])
            if filters.get("categoria"):
                query = query.filter(Transaction.categoria == filters["categoria"])
            if filters.get("fecha_inicio"):
                query = query.filter(Transaction.fecha >= filters["fecha_inicio"])
            if filters.get("fecha_fin"):
                query = query.filter(Transaction.fecha <= filters["fecha_fin"])
        return [self._to_dict(t) for t in query.all()]

    def update(self, id: str, data: dict) -> Optional[dict]:
        txn = self.db.query(Transaction).filter(Transaction.id == id).first()
        if not txn:
            return None
        for key, value in data.items():
            if hasattr(txn, key):
                setattr(txn, key, value)
        self.db.flush()
        return self._to_dict(txn)

    def delete(self, id: str) -> bool:
        txn = self.db.query(Transaction).filter(Transaction.id == id).first()
        if not txn:
            return False
        self.db.delete(txn)
        return True

    def delete_all_for_user(self, user_id: str) -> int:
        count = self.db.query(Transaction).filter(Transaction.user_id == user_id).delete()
        return count

    def _to_dict(self, txn: Transaction) -> dict:
        return {
            "id": txn.id,
            "user_id": txn.user_id,
            "tipo": txn.tipo,
            "monto": txn.monto,
            "categoria": txn.categoria,
            "descripcion": txn.descripcion,
            "fecha": txn.fecha,
            "moneda": txn.moneda,
            "created_at": txn.created_at.isoformat() if txn.created_at else None,
        }


class BudgetRepository(BaseRepository):
    """Repository para presupuestos"""

    def create(self, data: dict) -> dict:
        budget = Budget(
            id=data.get("id", f"bud_{uuid.uuid4().hex[:16]}"),
            user_id=data["user_id"],
            categoria=data["categoria"],
            limite=data["limite"],
            mes=data["mes"],
        )
        self.db.add(budget)
        self.db.flush()
        return self._to_dict(budget)

    def get_by_id(self, id: str) -> Optional[dict]:
        budget = self.db.query(Budget).filter(Budget.id == id).first()
        return self._to_dict(budget) if budget else None

    def get_all(self, filters: dict = None) -> list[dict]:
        query = self.db.query(Budget)
        if filters:
            if filters.get("user_id"):
                query = query.filter(Budget.user_id == filters["user_id"])
            if filters.get("mes"):
                query = query.filter(Budget.mes == filters["mes"])
        return [self._to_dict(b) for b in query.all()]

    def update(self, id: str, data: dict) -> Optional[dict]:
        budget = self.db.query(Budget).filter(Budget.id == id).first()
        if not budget:
            return None
        for key, value in data.items():
            if hasattr(budget, key):
                setattr(budget, key, value)
        self.db.flush()
        return self._to_dict(budget)

    def delete(self, id: str) -> bool:
        budget = self.db.query(Budget).filter(Budget.id == id).first()
        if not budget:
            return False
        self.db.delete(budget)
        return True

    def upsert(self, user_id: str, categoria: str, mes: str, limite: float) -> dict:
        """Inserta o actualiza presupuesto"""
        budget = self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.categoria == categoria,
            Budget.mes == mes,
        ).first()

        if budget:
            budget.limite = limite
        else:
            budget = Budget(
                id=f"bud_{uuid.uuid4().hex[:16]}",
                user_id=user_id,
                categoria=categoria,
                limite=limite,
                mes=mes,
            )
            self.db.add(budget)
        self.db.flush()
        return self._to_dict(budget)

    def _to_dict(self, budget: Budget) -> dict:
        return {
            "id": budget.id,
            "user_id": budget.user_id,
            "categoria": budget.categoria,
            "limite": budget.limite,
            "mes": budget.mes,
        }


class GoalRepository(BaseRepository):
    """Repository para metas de ahorro"""

    def create(self, data: dict) -> dict:
        goal = Goal(
            id=data.get("id", f"goal_{uuid.uuid4().hex[:16]}"),
            user_id=data["user_id"],
            nombre=data["nombre"],
            objetivo=data["objetivo"],
            ahorrado=data.get("ahorrado", 0.0),
            fecha_limite=data.get("fecha_limite"),
            categoria=data.get("categoria"),
        )
        self.db.add(goal)
        self.db.flush()
        return self._to_dict(goal)

    def get_by_id(self, id: str) -> Optional[dict]:
        goal = self.db.query(Goal).filter(Goal.id == id).first()
        return self._to_dict(goal) if goal else None

    def get_all(self, filters: dict = None) -> list[dict]:
        query = self.db.query(Goal)
        if filters and filters.get("user_id"):
            query = query.filter(Goal.user_id == filters["user_id"])
        return [self._to_dict(g) for g in query.all()]

    def update(self, id: str, data: dict) -> Optional[dict]:
        goal = self.db.query(Goal).filter(Goal.id == id).first()
        if not goal:
            return None
        for key, value in data.items():
            if hasattr(goal, key):
                setattr(goal, key, value)
        self.db.flush()
        return self._to_dict(goal)

    def delete(self, id: str) -> bool:
        goal = self.db.query(Goal).filter(Goal.id == id).first()
        if not goal:
            return False
        self.db.delete(goal)
        return True

    def _to_dict(self, goal: Goal) -> dict:
        return {
            "id": goal.id,
            "user_id": goal.user_id,
            "nombre": goal.nombre,
            "objetivo": goal.objetivo,
            "ahorrado": goal.ahorrado,
            "fecha_limite": goal.fecha_limite,
            "categoria": goal.categoria,
        }


class UserRepository(BaseRepository):
    """Repository para usuarios"""

    def create(self, data: dict) -> dict:
        user = User(
            id=data.get("id", f"user_{uuid.uuid4().hex[:16]}"),
            username=data["username"],
            password_hash=data["password_hash"],
            role=data.get("role", "USER"),
        )
        self.db.add(user)
        self.db.flush()
        return self._to_dict(user)

    def get_by_id(self, id: str) -> Optional[dict]:
        user = self.db.query(User).filter(User.id == id).first()
        return self._to_dict(user) if user else None

    def get_by_username(self, username: str) -> Optional[dict]:
        user = self.db.query(User).filter(User.username == username).first()
        return self._to_dict_full(user) if user else None

    def get_all(self, filters: dict = None) -> list[dict]:
        return [self._to_dict(u) for u in self.db.query(User).all()]

    def update(self, id: str, data: dict) -> Optional[dict]:
        user = self.db.query(User).filter(User.id == id).first()
        if not user:
            return None
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.db.flush()
        return self._to_dict(user)

    def delete(self, id: str) -> bool:
        user = self.db.query(User).filter(User.id == id).first()
        if not user:
            return False
        self.db.delete(user)
        return True

    def _to_dict(self, user: User) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    def _to_dict_full(self, user: User) -> dict:
        d = self._to_dict(user)
        d["password_hash"] = user.password_hash
        return d
