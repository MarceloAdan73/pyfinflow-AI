from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.ai import (
    AIRequest,
    AIResponse,
    ChatMessageResponse,
    InsightResponse,
    InsightPrediction,
    InsightAnomaly,
    AIStatusResponse,
    ProviderStatus,
)
from app.api.deps import get_current_user, get_repositories
from app.repositories.factory import RepositoryFactory
from app.ai.rag_engine import RAGEngine
from app.ai.chat_memory import ChatMemoryService
from app.ai.analytics import FinancialAnalytics
from app.ai.vector_store import ChromaDBStore
from app.ai.provider_factory import ProviderFactory

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


@router.post("/chat", response_model=AIResponse)
def chat_with_ai(
    data: AIRequest,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    user_id = current_user["id"]

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


@router.get("/history", response_model=list[ChatMessageResponse])
def get_chat_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    chat_memory = ChatMemoryService(repos.chats)
    messages = chat_memory.cargar_historial(current_user["id"], limit=limit)
    return messages


@router.delete("/history", status_code=204)
def clear_chat_history(
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    chat_memory = ChatMemoryService(repos.chats)
    chat_memory.limpiar_historial(current_user["id"])


@router.get("/insights", response_model=InsightResponse)
def get_insights(
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
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


@router.get("/suggestions")
def get_suggestions(
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
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


@router.get("/status", response_model=AIStatusResponse)
def get_ai_status():
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
