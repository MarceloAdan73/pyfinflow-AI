import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, transactions, budgets, goals, ai
from app.core.config import settings
from app.core.metrics import metrics_collector
from app.core.alerts import alert_critical_error

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.database import init_db
    logger.info("startup", message="PyStreamFlow API starting", version="2.0.0")
    init_db()
    logger.info("startup", message="Database tables ensured")
    yield
    logger.info("shutdown", message="PyStreamFlow API shutting down")


app = FastAPI(
    title="PyStreamFlow API",
    description="API REST para gestión de finanzas personales con IA",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
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


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health/detailed")
def health_check_detailed():
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


@app.get("/metrics")
def metrics():
    return metrics_collector.get_metrics()


@app.get("/metrics/prometheus")
def metrics_prometheus():
    return Response(
        content=metrics_collector.get_prometheus_text(),
        media_type="text/plain",
    )
