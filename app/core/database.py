from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from app.core.config import settings
from app.core.models_db import Base


engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    **settings.SQLALCHEMY_ENGINE_OPTIONS,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Crea todas las tablas (solo para desarrollo/testing)"""
    Base.metadata.create_all(bind=engine)


def drop_all():
    """Elimina todas las tablas (solo testing)"""
    Base.metadata.drop_all(bind=engine)


def get_db():
    """Generador de sesiones para dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Context manager para sesiones (fuera de FastAPI)"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
