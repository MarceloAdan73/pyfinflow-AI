from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.ai.analytics import FinancialAnalytics
from app.ai.chat_memory import ChatMemoryService
from app.ai.provider_factory import ProviderFactory
from app.ai.rag_engine import RAGEngine
from app.ai.rate_limiter import AI_RATE_LIMIT, check_ai_rate_limit
from app.ai.vector_store import ChromaDBStore
from app.api.deps import get_current_user, get_repositories
from app.api.schemas.ai import (
    AIProviderSettingsRequest,
    AIProviderSettingsResponse,
    AIRequest,
    AIResponse,
    AIStatusResponse,
    ChatMessageResponse,
    InsightAnomaly,
    InsightPrediction,
    InsightResponse,
    ProviderStatus,
)
from app.repositories.factory import RepositoryFactory

router = APIRouter(prefix="/ai", tags=["IA"])


def _obtener_contexto_financiero(user_id: str, repos: RepositoryFactory) -> dict:
    txns = repos.transactions.get_all({"user_id": user_id})
    if not txns:
        return {
            "ingresos": 0,
            "gastos": 0,
            "balance": 0,
            "top_categoria": "Sin datos",
            "total_transacciones": 0,
        }

    ingresos = sum(t["monto"] for t in txns if t["tipo"] == "Ingreso")
    gastos = sum(t["monto"] for t in txns if t["tipo"] == "Gasto")

    gastos_por_cat = {}
    for t in txns:
        if t["tipo"] == "Gasto":
            cat = t["categoria"]
            gastos_por_cat[cat] = gastos_por_cat.get(cat, 0) + t["monto"]

    top_cat = max(gastos_por_cat, key=gastos_por_cat.get) if gastos_por_cat else "Sin gastos"

    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "balance": ingresos - gastos,
        "top_categoria": top_cat,
        "total_transacciones": len(txns),
    }


@router.post(
    "/chat",
    response_model=AIResponse,
    summary="Chat con asistente IA",
    response_description="Respuesta del asistente con metadatos",
)
def chat_with_ai(
    data: AIRequest,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Envía una pregunta al asistente IA y recibe una respuesta contextualizada.

    Flujo RAG:
    1. Se busca contexto relevante en ChromaDB (transacciones similares)
    2. Se construye un prompt con el contexto financiero del usuario
    3. Se envía al provider IA configurado (Ollama → HuggingFace → Gemini)
    4. Si ningún provider está disponible, usa reglas locales

    El mensaje se guarda en el historial de conversación automáticamente.

    Rate limiting: máximo configurable vía AI_RATE_LIMIT_PER_MIN (default 30/min).
    """
    user_id = current_user["id"]

    if not check_ai_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiadas consultas IA. Esperá un momento (límite: {AI_RATE_LIMIT}/min).",
        )

    chat_memory = ChatMemoryService(repos.chats)
    chat_memory.guardar_mensaje(user_id, "user", data.pregunta)

    contexto_financiero = _obtener_contexto_financiero(user_id, repos)
    rag_engine = RAGEngine()
    result = rag_engine.consultar(user_id, data.pregunta, contexto_financiero)

    chat_memory.guardar_mensaje(
        user_id,
        "assistant",
        result["respuesta"],
        provider=result["provider"],
        context={"contexto_usado": result["contexto_usado"]},
    )

    return AIResponse(
        respuesta=result["respuesta"],
        provider=result["provider"],
        contexto_usado=result["contexto_usado"],
        latency_ms=result["latency_ms"],
    )


@router.get(
    "/history",
    response_model=list[ChatMessageResponse],
    summary="Historial de conversación",
    response_description="Mensajes del chat",
)
def get_chat_history(
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de mensajes (1-100)"),
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Retorna el historial de conversación del usuario.

    Retorna los últimos N mensajes (default: 20, máximo: 100).
    Incluye mensajes del usuario y del asistente con metadatos
    (provider usado, tokens consumidos, timestamp).
    """
    chat_memory = ChatMemoryService(repos.chats)
    messages = chat_memory.cargar_historial(current_user["id"], limit=limit)
    return messages


@router.delete(
    "/history",
    status_code=204,
    summary="Limpiar historial de chat",
)
def clear_chat_history(
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Elimina todo el historial de conversación del usuario.

    Esta acción es irreversible. Los mensajes se eliminan
    permanentemente de la base de datos.
    """
    chat_memory = ChatMemoryService(repos.chats)
    chat_memory.limpiar_historial(current_user["id"])


@router.get(
    "/insights",
    response_model=InsightResponse,
    summary="Análisis predictivo financiero",
    response_description="Insights, predicciones y anomalías",
)
def get_insights(
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Genera análisis predictivo basado en el histórico de transacciones.

    Incluye:
    - **Tendencias**: dirección del gasto por categoría (↑ sube, ↓ baja, → estable)
    - **Predicción**: gasto mensual estimado con nivel de confianza
    - **Anomalías**: gastos inusuales detectados con z-score (>2 desviaciones)
    - **Insights**: resumen en lenguaje natural con recomendaciones
    """
    user_id = current_user["id"]
    txns = repos.transactions.get_all({"user_id": user_id})

    analytics = FinancialAnalytics()

    tendencias = analytics.analizar_tendencias(txns)
    prediccion_data = analytics.predecir_gasto_mensual(txns)
    anomalias_data = analytics.detectar_anomalias(txns)
    insights = analytics.generar_insights(txns)

    prediccion = InsightPrediction(**prediccion_data)
    anomalias = [InsightAnomaly(**a) for a in anomalias_data]

    return InsightResponse(
        tendencias=tendencias,
        prediccion=prediccion,
        anomalias=anomalias,
        insights=insights,
    )


@router.get(
    "/suggestions",
    summary="Preguntas sugeridas",
    response_description="Lista de preguntas recomendadas",
)
def get_suggestions(
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Retorna preguntas sugeridas basadas en los datos del usuario.

    Las sugerencias se personalizan según las categorías de gasto
    y el estado de presupuestos y metas del usuario.
    Retorna un máximo de 6 sugerencias.
    """
    user_id = current_user["id"]
    txns = repos.transactions.get_all({"user_id": user_id})

    suggestions = [
        "¿Cuánto gasté este mes?",
        "¿Cuáles son mis categorías con más gastos?",
        "¿Cómo voy con mis presupuestos?",
        "Dame un resumen de mis ingresos",
        "¿Qué metas de ahorro tengo?",
    ]

    if txns:
        gastos = [t for t in txns if t["tipo"] == "Gasto"]
        if gastos:
            cats = set(t["categoria"] for t in gastos)
            for cat in list(cats)[:2]:
                suggestions.append(f"¿Cuánto gasté en {cat}?")

    return {"suggestions": suggestions[:6]}


@router.get(
    "/status",
    response_model=AIStatusResponse,
    summary="Estado del sistema IA",
    response_description="Disponibilidad de providers y ChromaDB",
)
def get_ai_status():
    """Retorna el estado actual de los providers de IA y ChromaDB.

    Útil para diagnosticar:
    - Qué providers están disponibles (Ollama, HuggingFace, Gemini)
    - Cuál está activo (primero disponible en la cadena de fallback)
    - Si ChromaDB está operativo para búsqueda semántica
    """
    factory = ProviderFactory()
    providers = [
        ProviderStatus(name=p.name, available=p.is_available())
        for p in factory.providers
    ]

    active = "local_rules"
    for p in factory.providers:
        if p.is_available():
            active = p.name
            break

    chromadb_ok = False
    try:
        store = ChromaDBStore()
        chromadb_ok = store._get_client() is not None
    except Exception:
        pass

    return AIStatusResponse(
        providers=providers,
        active_provider=active,
        chromadb_available=chromadb_ok,
    )


@router.get(
    "/settings",
    response_model=AIProviderSettingsResponse,
    summary="Obtener configuración IA del usuario",
    response_description="Configuración actual de providers",
)
def get_ai_settings(
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Retorna la configuración de providers IA del usuario.

    Incluye: prioridad de providers, URLs, modelos, API keys,
    parámetros de generación (max_tokens, temperature, context_window)
    y modelo de embeddings.

    Si no existe configuración, retorna los valores por defecto.
    """
    config = repos.ai_config.get_by_user(current_user["id"])
    if not config:
        config = repos.ai_config.upsert(current_user["id"], {})
    return AIProviderSettingsResponse(**config)


@router.put(
    "/settings",
    response_model=AIProviderSettingsResponse,
    summary="Actualizar configuración IA del usuario",
    response_description="Configuración actualizada",
)
def update_ai_settings(
    data: AIProviderSettingsRequest,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Actualiza la configuración de providers IA del usuario.

    Solo se actualizan los campos enviados (PATCH paracial).
    Los campos no enviados mantienen su valor actual.

    Permite configurar desde la UI sin tocar variables de entorno.
    """
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    config = repos.ai_config.upsert(current_user["id"], update_data)
    return AIProviderSettingsResponse(**config)
