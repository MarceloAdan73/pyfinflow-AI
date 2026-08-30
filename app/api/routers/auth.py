import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import get_current_user, get_repositories
from app.api.schemas.auth import (
    PasswordChange,
    RefreshRequest,
    RefreshResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.core.auth import (
    crear_access_token,
    crear_refresh_token,
    esta_bloqueado,
    hash_password,
    limpiar_intento,
    registrar_intento_login,
    verificar_password,
    verificar_refresh_token,
)
from app.core.config import settings
from app.core.metrics import metrics_collector
from app.repositories.factory import RepositoryFactory

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
    summary="Registrar nuevo usuario",
    response_description="Tokens de acceso y refresh",
)
def register(
    data: UserRegister,
    request: Request,
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Registra un nuevo usuario y retorna tokens JWT.

    - **username**: 3-50 caracteres, único en el sistema
    - **password**: mínimo 6 caracteres, hasheado con bcrypt (12 rounds)

    Si el usuario ya existe, retorna 409 Conflict.
    En producción (`ALLOW_REGISTRATION=false`) el registro público está
    deshabilitado: se devuelve 403 y el acceso es vía `/auth/demo`.
    """
    if not settings.ALLOW_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El registro está deshabilitado en esta demostración. Usá el acceso de demostración.",
        )

    existing = repos.users.get_by_username(data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El usuario ya existe",
        )

    user = repos.users.create({
        "id": f"user_{uuid.uuid4().hex[:16]}",
        "username": data.username,
        "password_hash": hash_password(data.password),
        "role": "USER",
    })

    access_token = crear_access_token(user["id"], user["username"], user["role"])
    refresh_token = crear_refresh_token(user["id"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo123"


def _seed_demo_data(user_id: str, repos: RepositoryFactory):
    """Carga datos de ejemplo para la cuenta demo (solo si no tiene transacciones)."""
    import random
    from datetime import date, timedelta

    if repos.transactions.get_all({"user_id": user_id}):
        return

    today = date.today()
    mes = today.strftime("%Y-%m")

    ingresos = [
        ("Salario", 850000.0, "Salario mensual"),
        ("Freelance", 120000.0, "Proyecto freelance"),
        ("Inversiones", 35000.0, "Dividendos"),
    ]
    gastos = [
        ("Comida", 180000.0, "Supermercado mensual"),
        ("Vivienda", 220000.0, "Alquiler"),
        ("Transporte", 45000.0, "Nafta y transporte"),
        ("Servicios", 60000.0, "Luz, agua, internet"),
        ("Ocio", 30000.0, "Salidas y entretenimiento"),
    ]

    for categoria, monto, desc in ingresos:
        repos.transactions.create({
            "user_id": user_id,
            "tipo": "Ingreso",
            "monto": monto,
            "categoria": categoria,
            "descripcion": desc,
            "fecha": (today - timedelta(days=random.randint(0, 12))).strftime("%Y-%m-%d"),
        })

    for categoria, monto, desc in gastos:
        repos.transactions.create({
            "user_id": user_id,
            "tipo": "Gasto",
            "monto": monto,
            "categoria": categoria,
            "descripcion": desc,
            "fecha": (today - timedelta(days=random.randint(0, 20))).strftime("%Y-%m-%d"),
        })

    repos.budgets.upsert(user_id, "Comida", mes, 200000.0)
    repos.budgets.upsert(user_id, "Vivienda", mes, 250000.0)
    repos.budgets.upsert(user_id, "Transporte", mes, 60000.0)
    repos.budgets.upsert(user_id, "Ocio", mes, 50000.0)

    repos.goals.create({
        "user_id": user_id,
        "nombre": "Fondo de emergencia",
        "objetivo": 1000000.0,
        "ahorrado": 450000.0,
        "fecha_limite": (today + timedelta(days=180)).strftime("%Y-%m-%d"),
        "categoria": "Ahorro",
    })
    repos.goals.create({
        "user_id": user_id,
        "nombre": "Viaje a Europa",
        "objetivo": 2500000.0,
        "ahorrado": 800000.0,
        "fecha_limite": (today + timedelta(days=365)).strftime("%Y-%m-%d"),
        "categoria": "Viajes",
    })


@router.post(
    "/demo",
    response_model=TokenResponse,
    summary="Iniciar sesión demonístración (cuenta demo)",
    response_description="Tokens JWT de la cuenta demo",
)
def demo_login(
    request: Request,
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Loguea (o crea y loguea) la cuenta demo con datos de ejemplo.

    Devuelve tokens JWT listos para usar. La cuenta `demo/demo123` se crea
    automáticamente con transacciones, presupuestos y metas de ejemplo en
    la primera llamada.
    """
    existing = repos.users.get_by_username(DEMO_USERNAME)
    if existing:
        user_id = existing["id"]
    else:
        user = repos.users.create({
            "id": f"user_{uuid.uuid4().hex[:16]}",
            "username": DEMO_USERNAME,
            "password_hash": hash_password(DEMO_PASSWORD),
            "role": "USER",
        })
        user_id = user["id"]

    _seed_demo_data(user_id, repos)

    role = "USER"
    access_token = crear_access_token(user_id, DEMO_USERNAME, role)
    refresh_token = crear_refresh_token(user_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    response_description="Tokens de acceso y refresh",
)
def login(
    data: UserLogin,
    request: Request,
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Autentica un usuario y retorna tokens JWT.

    - **Access token**: expira en 1 hora
    - **Refresh token**: expira en 7 días

    Implementa rate limiting: máximo 5 intentos fallidos por IP por minuto.
    Soporte automático de migración SHA256 → bcrypt.
    """
    ip = request.client.host if request.client else "unknown"

    if esta_bloqueado(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Esperá 60s.",
        )

    if not registrar_intento_login(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Intentá de nuevo en 60s.",
        )

    user = repos.users.get_by_username(data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    stored_hash = user["password_hash"]
    password_valid = False

    if stored_hash.startswith("$2"):
        password_valid = verificar_password(data.password, stored_hash)
    else:
        from app.core.auth import hash_password_sha256
        if hash_password_sha256(data.password) == stored_hash:
            password_valid = True
            repos.users.update(user["id"], {"password_hash": hash_password(data.password)})

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    limpiar_intento(ip)

    access_token = crear_access_token(user["id"], user["username"], user.get("role", "USER"))
    refresh_token = crear_refresh_token(user["id"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Renovar access token",
    response_description="Nuevo access token",
)
def refresh(
    data: RefreshRequest,
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Renueva el access token usando un refresh token válido.

    El refresh token expira en 7 días. Si es inválido o expirado,
    retorna 401 Unauthorized.
    """
    payload = verificar_refresh_token(data.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )

    user = repos.users.get_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    access_token = crear_access_token(user["id"], user["username"], user.get("role", "USER"))
    return RefreshResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual",
    response_description="Datos del usuario autenticado",
)
def get_me(current_user: dict = Depends(get_current_user)):
    """Retorna los datos del usuario autenticado.

    Requiere un access token válido en el header `Authorization: Bearer <token>`.
    Registra actividad del usuario para métricas.
    """
    metrics_collector.record_user_activity(current_user["id"])
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        role=current_user.get("role", "USER"),
    )


@router.put(
    "/password",
    summary="Cambiar contraseña",
    response_description="Confirmación de cambio",
)
def change_password(
    data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
    """Cambia la contraseña del usuario autenticado.

    - **current_password**: contraseña actual (requerida para verificación)
    - **new_password**: nueva contraseña (mínimo 6 caracteres)

    La nueva contraseña es hasheada con bcrypt automáticamente.
    """
    stored_hash = current_user["password_hash"]
    if not verificar_password(data.current_password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta",
        )

    repos.users.update(current_user["id"], {
        "password_hash": hash_password(data.new_password),
    })

    return {"detail": "Contraseña actualizada"}
