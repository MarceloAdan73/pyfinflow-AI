from pydantic import BaseModel, Field
from typing import Optional


class AIRequest(BaseModel):
    pregunta: str = Field(
        ...,
        min_length=1,
        max_length=500,
        alias="mensaje",
        examples=["¿Cuánto gasté en comida este mes?"],
        description="Pregunta del usuario al asistente IA",
    )

    model_config = {"populate_by_name": True}


class AIResponse(BaseModel):
    respuesta: str = Field(
        ...,
        examples=["Este mes gastaste $45,000 en comida..."],
    )
    provider: str = Field(
        ...,
        examples=["ollama"],
        description="Provider que respondió (ollama, huggingface, gemini, local_rules)",
    )
    contexto_usado: int = Field(
        ...,
        examples=[3],
        description="Cantidad de transacciones usadas como contexto",
    )
    latency_ms: float = Field(
        ...,
        examples=[1250.5],
        description="Latencia de la respuesta en milisegundos",
    )


class ChatMessageResponse(BaseModel):
    id: str
    user_id: str
    role: str = Field(..., examples=["user"])
    content: str
    provider: Optional[str] = None
    tokens_used: int = 0
    created_at: Optional[str] = None


class InsightTrend(BaseModel):
    trend: str = Field(..., examples=["up"])
    change_pct: float = Field(..., examples=[15.3])
    promedio: float = Field(..., examples=[25000.0])


class InsightPrediction(BaseModel):
    prediccion: float = Field(..., examples=[180000.0])
    confianza: float = Field(..., examples=[0.75])
    metodo: str = Field(..., examples=["weighted_avg_3m"])
    historico: dict = Field(default_factory=dict)


class InsightAnomaly(BaseModel):
    id: Optional[str] = None
    categoria: str
    monto: float
    fecha: Optional[str] = None
    z_score: float
    reason: str


class InsightResponse(BaseModel):
    tendencias: dict = Field(default_factory=dict)
    prediccion: InsightPrediction
    anomalias: list[InsightAnomaly] = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)


class ProviderStatus(BaseModel):
    name: str
    available: bool


class AIStatusResponse(BaseModel):
    providers: list[ProviderStatus]
    active_provider: str
    chromadb_available: bool


class AIProviderSettingsRequest(BaseModel):
    provider_priority: Optional[str] = Field(None, examples=["ollama,huggingface,gemini"])
    ollama_url: Optional[str] = Field(None, examples=["http://localhost:11434"])
    ollama_model: Optional[str] = Field(None, examples=["qwen2.5-coder:7b"])
    hf_token: Optional[str] = Field(None, examples=["hf_xxx"])
    hf_model: Optional[str] = Field(None, examples=["HuggingFaceH4/zephyr-7b-beta"])
    gemini_api_key: Optional[str] = Field(None, examples=["AIza..."])
    gemini_model: Optional[str] = Field(None, examples=["gemini-2.0-flash"])
    embedding_model: Optional[str] = Field(None, examples=["all-MiniLM-L6-v2"])
    max_tokens: Optional[int] = Field(None, ge=50, le=2000, examples=[500])
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, examples=[0.7])
    context_window: Optional[int] = Field(None, ge=1, le=100, examples=[20])


class AIProviderSettingsResponse(BaseModel):
    provider_priority: str
    ollama_url: str
    ollama_model: str
    hf_token: str
    hf_model: str
    gemini_api_key: str
    gemini_model: str
    embedding_model: str
    max_tokens: int
    temperature: float
    context_window: int
    updated_at: Optional[str] = None
