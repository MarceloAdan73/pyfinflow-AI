from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session


class BaseRepository(ABC):
    """Interfaz abstracta para repositories"""

    def __init__(self, db: Session):
        self.db = db

    @abstractmethod
    def create(self, data: dict) -> dict:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[dict]:
        pass

    @abstractmethod
    def get_all(self, filters: dict = None) -> list[dict]:
        pass

    @abstractmethod
    def update(self, id: str, data: dict) -> Optional[dict]:
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        pass
