import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/pystreamflow_dev"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    SQLALCHEMY_DATABASE_URL = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
    }

    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"
    ALERT_EMAIL_TO: str = os.getenv("ALERT_EMAIL_TO", "")

    # AI Settings
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    HF_MODEL: str = os.getenv("HF_MODEL", "HuggingFaceH4/zephyr-7b-beta")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    CHROMADB_PATH: str = os.getenv("CHROMADB_PATH", "./chroma_data")
    AI_PROVIDER_PRIORITY: str = os.getenv("AI_PROVIDER_PRIORITY", "ollama,huggingface,gemini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "500"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_CONTEXT_WINDOW: int = int(os.getenv("AI_CONTEXT_WINDOW", "20"))
    AI_RATE_LIMIT_PER_MIN: int = int(os.getenv("AI_RATE_LIMIT_PER_MIN", "30"))


settings = Settings()
