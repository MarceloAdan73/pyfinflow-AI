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
    """
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
