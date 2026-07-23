from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    """Datos para registrar un nuevo usuario."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["marcelo"],
        description="Nombre de usuario único (3-50 caracteres)",
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        examples=["secreto123"],
        description="Contraseña (mínimo 6 caracteres, hasheada con bcrypt)",
    )


class UserLogin(BaseModel):
    """Credenciales de inicio de sesión."""

    username: str = Field(..., examples=["marcelo"], description="Nombre de usuario")
    password: str = Field(..., examples=["secreto123"], description="Contraseña")


class TokenResponse(BaseModel):
    """Tokens de autenticación JWT."""

    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIs..."], description="Token de acceso (expira en 1 hora)")
    refresh_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIs..."], description="Token de renovación (expira en 7 días)")
    token_type: str = Field("bearer", description="Tipo de token")


class RefreshRequest(BaseModel):
    """Solicitud de renovación de token."""

    refresh_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIs..."], description="Refresh token válido")


class RefreshResponse(BaseModel):
    """Respuesta con nuevo access token."""

    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIs..."], description="Nuevo access token")
    token_type: str = Field("bearer", description="Tipo de token")


class UserResponse(BaseModel):
    """Datos del usuario autenticado."""

    id: str = Field(..., examples=["user_a1b2c3d4e5f6g7h8"], description="ID único del usuario")
    username: str = Field(..., examples=["marcelo"], description="Nombre de usuario")
    role: str = Field(..., examples=["USER"], description="Rol: ADMIN, USER o VIEWER")


class PasswordChange(BaseModel):
    """Solicitud de cambio de contraseña."""

    current_password: str = Field(..., min_length=6, examples=["secreto123"], description="Contraseña actual")
    new_password: str = Field(..., min_length=6, examples=["nueva456"], description="Nueva contraseña (mínimo 6 caracteres)")
