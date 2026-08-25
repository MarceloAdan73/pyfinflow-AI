from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.auth import verificar_access_token
from app.core.database import get_db
from app.repositories.factory import RepositoryFactory

security = HTTPBearer()


def get_repositories(db: Session = Depends(get_db)) -> RepositoryFactory:
    return RepositoryFactory(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    repos: RepositoryFactory = Depends(get_repositories),
) -> dict:
    token = credentials.credentials
    payload = verificar_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = repos.users.get_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    return user


def get_current_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )
    return current_user
