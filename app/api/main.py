import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import ai, auth, budgets, goals, transactions
from app.core.alerts import alert_critical_error
from app.core.config import settings
from app.core.metrics import metrics_collector

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.database import init_db
    logger.info("startup", message="PyFinFlow API starting", version="2.0.0")
    init_db()
    logger.info("startup", message="Database tables ensured")
    yield
    logger.info("shutdown", message="PyFinFlow API shutting down")


OPENAPI_TAGS = [
    {
        "name": "Autenticación",
        "description": "Registro, login, refresh tokens y gestión de contraseña.",
    },
    {
        "name": "Transacciones",
        "description": "CRUD de ingresos y gastos con filtros por tipo, categoría y fecha.",
    },
    {
        "name": "Presupuestos",
        "description": "Gestión de presupuestos mensuales por categoría con upsert.",
    },
    {
        "name": "Metas de Ahorro",
        "description": "Creación, seguimiento y eliminación de metas de ahorro.",
    },
    {
        "name": "IA",
        "description": "Chat con asistente IA (RAG), insights predictivos, historial y configuración de providers.",
    },
    {
        "name": "Sistema",
        "description": "Health checks, métricas y monitoreo de la API.",
    },
]

app = FastAPI(
    title="PyFinFlow API",
    description=(
        "API REST para gestión de finanzas personales con inteligencia artificial.\n\n"
        "## Funcionalidades\n"
        "- **Auth**: Registro, login JWT, refresh tokens, rate limiting\n"
        "- **Transacciones**: CRUD completo con filtros por tipo, categoría y rango de fechas\n"
        "- **Presupuestos**: Límites mensuales por categoría con alertas de excedido\n"
        "- **Metas de ahorro**: Seguimiento de progreso con fecha límite\n"
        "- **IA**: Chat RAG con multi-provider (Ollama, HuggingFace, Gemini), análisis predictivo y detección de anomalías\n"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
    contact={
        "name": "PyFinFlow Team",
        "url": "https://github.com/MarceloAdan73/pyfinflow-AI",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Desarrollo local"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "http_request_error",
            method=request.method,
            path=request.url.path,
            error=str(e),
            duration_ms=round(duration * 1000, 2),
        )
        metrics_collector.record_request(
            request.method, request.url.path, 500, round(duration * 1000, 2)
        )
        alert_critical_error("InternalServerError", str(e), request.url.path)
        raise

    duration = time.time() - start_time

    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2),
    )

    metrics_collector.record_request(
        request.method, request.url.path, response.status_code, round(duration * 1000, 2)
    )

    if response.status_code >= 500:
        alert_critical_error(
            f"HTTP {response.status_code}",
            f"Server error on {request.method} {request.url.path}",
            request.url.path,
        )

    return response


app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(goals.router)
app.include_router(ai.router)


@app.get("/health", tags=["Sistema"], summary="Health check básico")
def health_check():
    """Verifica que la API esté operativa.

    Retorna el estado, versión y entorno actual.
    Útil como endpoint de monitoreo para load balancers y alertas.
    """
    return {
        "status": "ok",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health/detailed", tags=["Sistema"], summary="Health check detallado")
def health_check_detailed():
    """Verifica la conectividad con servicios dependientes.

    Testea:
    - **Database**: Conexión SQLAlchemy a PostgreSQL/SQLite
    - **Redis**: Disponibilidad del cache (fallback a in-memory si no está)

    Retorna el estado de cada servicio y un status general (`ok` o `degraded`).
    """
    checks = {}

    try:
        from sqlalchemy import text

        from app.core.database import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    try:
        from app.core.cache import get_redis
        r = get_redis()
        if r:
            checks["redis"] = "ok"
        else:
            checks["redis"] = "unavailable"
    except Exception:
        checks["redis"] = "unavailable"

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"

    return {
        "status": overall,
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "checks": checks,
    }


@app.get("/metrics", tags=["Sistema"], summary="Métricas en JSON")
def metrics():
    """Retorna métricas de la aplicación en formato JSON.

    Incluye:
    - Requests por minuto y por endpoint
    - Distribución de status codes
    - Latencia promedio de llamadas a IA
    - Errores por tipo
    - Usuarios activos
    """
    return metrics_collector.get_metrics()


@app.get("/metrics/prometheus", tags=["Sistema"], summary="Métricas en formato Prometheus")
def metrics_prometheus():
    """Retorna métricas en formato de texto Prometheus (text/plain).

    Compatible con Prometheus, Grafana y cualquier collector
    que soporte el formato estándar de métricas.
    """
    return Response(
        content=metrics_collector.get_prometheus_text(),
        media_type="text/plain",
    )
