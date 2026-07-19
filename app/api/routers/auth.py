import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.auth import (
    hash_password,
    verificar_password,
    crear_access_token,
    crear_refresh_token,
    verificar_refresh_token,
    registrar_intento_login,
    esta_bloqueado,
    limpiar_intento,
    JWT_REFRESH_EXPIRY,
)
from app.api.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshRequest,
    RefreshResponse,
    UserResponse,
    PasswordChange,
)
from app.api.deps import get_repositories, get_current_user
from app.repositories.factory import RepositoryFactory

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    data: UserRegister,
    request: Request,
    repos: RepositoryFactory = Depends(get_repositories),
):
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


@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLogin,
    request: Request,
    repos: RepositoryFactory = Depends(get_repositories),
):
    ip = request.client.host if request.client else "unknown"

    if esta_bloqueado(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos. Esperá 60s.",
        )

    if not registrar_intento_login(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos fallidos. Intentá de nuevo en 60s.",
        )

    user = repos.users.get_by_username(data.username)
    if not user:
        limpiar_intento(ip)
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
        limpiar_intento(ip)
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


@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    data: RefreshRequest,
    repos: RepositoryFactory = Depends(get_repositories),
):
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


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        role=current_user.get("role", "USER"),
    )


@router.put("/password")
def change_password(
    data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories),
):
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
