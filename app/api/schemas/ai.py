from pydantic import BaseModel, Field
from typing import Optional


class AIRequest(BaseModel):
    """Solicitud de chat con el asistente IA."""

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
    """Respuesta del asistente IA con metadatos."""

    respuesta: str = Field(
        ...,
        examples=["Este mes gastaste $45,000 en comida, lo cual es un 12% más que el mes anterior."],
        description="Respuesta generada por el asistente",
    )
    provider: str = Field(
        ...,
        examples=["ollama"],
        description="Provider que respondió (ollama, huggingface, gemini, local_rules)",
    )
    contexto_usado: int = Field(
        ...,
        examples=[3],
        description="Cantidad de transacciones usadas como contexto RAG",
    )
    latency_ms: float = Field(
        ...,
        examples=[1250.5],
        description="Latencia de la respuesta en milisegundos",
    )


class ChatMessageResponse(BaseModel):
    """Mensaje del historial de conversación."""

    id: str = Field(..., examples=["chat_a1b2c3d4e5f6g7h8"], description="ID único del mensaje")
    user_id: str = Field(..., examples=["user_a1b2c3d4e5f6g7h8"], description="ID del usuario")
    role: str = Field(..., examples=["user"], description="Rol: 'user' o 'assistant'")
    content: str = Field(..., examples=["¿Cuánto gasté en comida?"], description="Contenido del mensaje")
    provider: Optional[str] = Field(None, examples=["ollama"], description="Provider IA que respondió")
    tokens_used: int = Field(0, examples=[150], description="Tokens consumidos en el mensaje")
    created_at: Optional[str] = Field(None, examples=["2026-07-19T14:30:00"], description="Timestamp del mensaje")


class InsightTrend(BaseModel):
    """Tendencia de gasto por categoría."""

    trend: str = Field(..., examples=["up"], description="Dirección: 'up' (sube), 'down' (baja), 'stable' (estable)")
    change_pct: float = Field(..., examples=[15.3], description="Porcentaje de cambio vs período anterior")
    promedio: float = Field(..., examples=[25000.0], description="Promedio mensual de la categoría")


class InsightPrediction(BaseModel):
    """Predicción de gasto mensual."""

    prediccion: float = Field(..., examples=[180000.0], description="Gasto mensual estimado en la moneda del usuario")
    confianza: float = Field(..., examples=[0.75], description="Nivel de confianza (0.0 a 1.0)")
    metodo: str = Field(..., examples=["weighted_avg_3m"], description="Método de predicción utilizado")
    historico: dict = Field(default_factory=dict, description="Datos históricos usados para la predicción")


class InsightAnomaly(BaseModel):
    """Gasto anómalo detectado por z-score."""

    id: Optional[str] = Field(None, examples=["txn_a1b2c3d4e5f6g7h8"], description="ID de la transacción anómala")
    categoria: str = Field(..., examples=["Transporte"], description="Categoría del gasto anómalo")
    monto: float = Field(..., examples=[85000], description="Monto del gasto inusual")
    fecha: Optional[str] = Field(None, examples=["2026-07-15"], description="Fecha del gasto")
    z_score: float = Field(..., examples=[2.8], description="Desviaciones estándar sobre la media")
    reason: str = Field(..., examples=["Monto 2.8x superior al promedio histórico"], description="Explicación de la anomalía")


class InsightResponse(BaseModel):
    """Análisis predictivo completo del usuario."""

    tendencias: dict = Field(default_factory=dict, description="Tendencias de gasto por categoría (sube/baja/estable)")
    prediccion: InsightPrediction = Field(..., description="Predicción de gasto mensual")
    anomalias: list[InsightAnomaly] = Field(default_factory=list, description="Gastos anómalos detectados")
    insights: list[str] = Field(default_factory=list, description="Resumen en lenguaje natural con recomendaciones")


class ProviderStatus(BaseModel):
    """Estado de un provider de IA."""

    name: str = Field(..., examples=["ollama"], description="Nombre del provider")
    available: bool = Field(..., examples=[True], description="Si el provider está disponible")


class AIStatusResponse(BaseModel):
    """Estado general del sistema IA."""

    providers: list[ProviderStatus] = Field(..., description="Lista de providers y su disponibilidad")
    active_provider: str = Field(..., examples=["ollama"], description="Provider activo (primero disponible)")
    chromadb_available: bool = Field(..., examples=[True], description="Si ChromaDB está operativo")


class AIProviderSettingsRequest(BaseModel):
    """Configuración de providers IA (actualización parcial)."""

    provider_priority: Optional[str] = Field(None, examples=["ollama,huggingface,gemini"], description="Orden de prioridad de providers")
    ollama_url: Optional[str] = Field(None, examples=["http://localhost:11434"], description="URL del servidor Ollama")
    ollama_model: Optional[str] = Field(None, examples=["qwen3.5:9b"], description="Modelo de Ollama")
    hf_token: Optional[str] = Field(None, examples=["hf_xxx"], description="Token de HuggingFace")
    hf_model: Optional[str] = Field(None, examples=["HuggingFaceH4/zephyr-7b-beta"], description="Modelo de HuggingFace")
    gemini_api_key: Optional[str] = Field(None, examples=["AIza..."], description="API key de Google Gemini")
    gemini_model: Optional[str] = Field(None, examples=["gemini-2.0-flash"], description="Modelo de Gemini")
    embedding_model: Optional[str] = Field(None, examples=["all-MiniLM-L6-v2"], description="Modelo de embeddings para ChromaDB")
    max_tokens: Optional[int] = Field(None, ge=50, le=2000, examples=[500], description="Máximo de tokens por respuesta")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, examples=[0.7], description="Temperatura de generación (0.0-2.0)")
    context_window: Optional[int] = Field(None, ge=1, le=100, examples=[20], description="Cantidad de mensajes de contexto")


class AIProviderSettingsResponse(BaseModel):
    """Configuración de providers IA del usuario."""

    provider_priority: str = Field(..., examples=["ollama,huggingface,gemini"], description="Orden de prioridad")
    ollama_url: str = Field(..., examples=["http://localhost:11434"], description="URL de Ollama")
    ollama_model: str = Field(..., examples=["qwen3.5:9b"], description="Modelo de Ollama")
    hf_token: str = Field(..., examples=["hf_xxx"], description="Token de HuggingFace (oculto en UI)")
    hf_model: str = Field(..., examples=["HuggingFaceH4/zephyr-7b-beta"], description="Modelo de HuggingFace")
    gemini_api_key: str = Field(..., examples=["AIza..."], description="API key de Gemini (oculta en UI)")
    gemini_model: str = Field(..., examples=["gemini-2.0-flash"], description="Modelo de Gemini")
    embedding_model: str = Field(..., examples=["all-MiniLM-L6-v2"], description="Modelo de embeddings")
    max_tokens: int = Field(..., examples=[500], description="Máximo de tokens por respuesta")
    temperature: float = Field(..., examples=[0.7], description="Temperatura de generación")
    context_window: int = Field(..., examples=[20], description="Ventana de contexto en mensajes")
    updated_at: Optional[str] = Field(None, examples=["2026-07-19T14:30:00"], description="Última actualización")
