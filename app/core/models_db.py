from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, String, Float, Integer, Text, DateTime, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="USER")
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    custom_categories = relationship("CustomCategory", back_populates="user", cascade="all, delete-orphan")
    config = relationship("UserConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
    ai_config = relationship("AIProviderConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    tipo = Column(String(20), nullable=False)
    monto = Column(Float, nullable=False)
    categoria = Column(String(50), nullable=False)
    descripcion = Column(Text, default="")
    fecha = Column(String(10), nullable=False)
    moneda = Column(String(10), nullable=False, default="ARS")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index("idx_transactions_user_fecha", "user_id", "fecha"),
        Index("idx_transactions_user_tipo", "user_id", "tipo"),
    )


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    categoria = Column(String(50), nullable=False)
    limite = Column(Float, nullable=False)
    mes = Column(String(7), nullable=False)  # YYYY-MM
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="budgets")

    __table_args__ = (
        UniqueConstraint("user_id", "categoria", "mes", name="uq_budget_user_cat_mes"),
    )


class Goal(Base):
    __tablename__ = "goals"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    objetivo = Column(Float, nullable=False)
    ahorrado = Column(Float, default=0.0)
    fecha_limite = Column(String(10))
    categoria = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="goals")


class CustomCategory(Base):
    __tablename__ = "custom_categories"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    tipo = Column(String(20), nullable=False)
    nombre = Column(String(50), nullable=False)

    user = relationship("User", back_populates="custom_categories")

    __table_args__ = (
        UniqueConstraint("user_id", "tipo", "nombre", name="uq_custom_cat"),
    )


class UserConfig(Base):
    __tablename__ = "user_configs"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    moneda_activa = Column(String(10), default="ARS")
    filtro_fecha_inicio = Column(String(10))
    filtro_fecha_fin = Column(String(10))

    user = relationship("User", back_populates="config")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    context_used = Column(Text)
    provider = Column(String(50))
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")

    __table_args__ = (
        Index("idx_chat_messages_user_created", "user_id", "created_at"),
    )


class AIProviderConfig(Base):
    __tablename__ = "ai_provider_configs"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    provider_priority = Column(String(200), default="ollama,huggingface,gemini")
    ollama_url = Column(String(255), default="http://localhost:11434")
    ollama_model = Column(String(100), default="qwen2.5-coder:7b")
    hf_token = Column(String(255), default="")
    hf_model = Column(String(100), default="HuggingFaceH4/zephyr-7b-beta")
    gemini_api_key = Column(String(255), default="")
    gemini_model = Column(String(100), default="gemini-2.0-flash")
    embedding_model = Column(String(100), default="all-MiniLM-L6-v2")
    max_tokens = Column(Integer, default=500)
    temperature = Column(Float, default=0.7)
    context_window = Column(Integer, default=20)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="ai_config")
