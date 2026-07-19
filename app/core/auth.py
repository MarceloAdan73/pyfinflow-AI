import os
import time
import hashlib
import secrets
from enum import Enum
from typing import Optional

import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

# Configuración
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_EXPIRY = 3600  # 1 hora
JWT_REFRESH_EXPIRY = 604800  # 7 días

# Intentar cargar desde secrets de Streamlit
try:
    import streamlit as st
    SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]
except Exception:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    VIEWER = "VIEWER"


# ============================
# PASSWORD HASHING (bcrypt)
# ============================

def hash_password(password: str) -> str:
    """Hashea contraseña con bcrypt (incluye sal única por usuario)"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    """Verifica contraseña contra hash bcrypt"""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def hash_password_sha256(password: str) -> str:
    """Legacy: hash SHA256 (solo para migración, no usar en nuevos usuarios)"""
    return hashlib.sha256(password.encode()).hexdigest()


# ============================
# JWT TOKENS
# ============================

def crear_access_token(user_id: str, username: str, role: str = "USER") -> str:
    """Crea access token JWT (1 hora de duración)"""
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "type": "access",
        "iat": time.time(),
        "exp": time.time() + JWT_ACCESS_EXPIRY,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def crear_refresh_token(user_id: str) -> str:
    """Crea refresh token JWT (7 días de duración)"""
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": time.time(),
        "exp": time.time() + JWT_REFRESH_EXPIRY,
        "jti": secrets.token_hex(16),  # ID único del token
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verificar_token(token: str) -> Optional[dict]:
    """Verifica y decodifica un token JWT. Retorna payload o None si es inválido."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verificar_access_token(token: str) -> Optional[dict]:
    """Verifica que sea un access token válido"""
    payload = verificar_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def verificar_refresh_token(token: str) -> Optional[dict]:
    """Verifica que sea un refresh token válido"""
    payload = verificar_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None


# ============================
# RATE LIMITING (simple, en memoria)
# ============================

_login_attempts: dict[str, list[float]] = {}
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW = 60  # segundos


def _cleanup_attempts(ip: str):
    """Limpia intentos antiguos fuera de la ventana"""
    now = time.time()
    if ip in _login_attempts:
        _login_attempts[ip] = [
            t for t in _login_attempts[ip] if now - t < LOGIN_WINDOW
        ]


def registrar_intento_login(ip: str) -> bool:
    """Registra un intento de login. Retorna False si excedió el límite."""
    _cleanup_attempts(ip)
    if len(_login_attempts.get(ip, [])) >= MAX_LOGIN_ATTEMPTS:
        return False
    _login_attempts.setdefault(ip, []).append(time.time())
    return True


def esta_bloqueado(ip: str) -> bool:
    """Verifica si una IP está bloqueada por intentos fallidos"""
    _cleanup_attempts(ip)
    return len(_login_attempts.get(ip, [])) >= MAX_LOGIN_ATTEMPTS


def limpiar_intento(ip: str):
    """Limpia los intentos después de login exitoso"""
    _login_attempts.pop(ip, None)


# ============================
# SUPABASE CLIENT
# ============================

def get_supabase_client():
    from supabase import create_client, Client
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY en .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================
# AUTH OPERATIONS
# ============================

def login_usuario(username: str, password: str, ip: str = "unknown") -> dict:
    """Login con rate limiting, bcrypt y JWT"""
    if esta_bloqueado(ip):
        return {
            "success": False,
            "error": f"Demasiados intentos. Esperá {LOGIN_WINDOW}s.",
        }

    if not registrar_intento_login(ip):
        return {
            "success": False,
            "error": f"Demasiados intentos fallidos. Intentá de nuevo en {LOGIN_WINDOW}s.",
        }

    try:
        client = get_supabase_client()
        response = client.table("usuarios").select("*").eq("username", username).execute()

        if not response.data:
            limpiar_intento(ip)
            return {"success": False, "error": "Usuario o contraseña incorrectos"}

        usuario = response.data[0]
        stored_hash = usuario["password_hash"]

        # Intentar verificar con bcrypt primero
        password_valida = False
        if stored_hash.startswith("$2"):
            # Hash es bcrypt
            password_valida = verificar_password(password, stored_hash)
        else:
            # Legacy SHA256 - migrar a bcrypt
            if hash_password_sha256(password) == stored_hash:
                password_valida = True
                # Migrar a bcrypt
                nuevo_hash = hash_password(password)
                client.table("usuarios").update({"password_hash": nuevo_hash}).eq(
                    "id", usuario["id"]
                ).execute()

        if not password_valida:
            return {"success": False, "error": "Usuario o contraseña incorrectos"}

        limpiar_intento(ip)

        role = usuario.get("role", "USER")
        access_token = crear_access_token(usuario["id"], usuario["username"], role)
        refresh_token = crear_refresh_token(usuario["id"])

        return {
            "success": True,
            "user_id": usuario["id"],
            "username": usuario["username"],
            "role": role,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def registrar_usuario(username: str, password: str) -> dict:
    """Registra usuario nuevo con bcrypt"""
    try:
        client = get_supabase_client()

        # Validaciones básicas
        if len(username) < 3:
            return {"success": False, "error": "Usuario debe tener al menos 3 caracteres"}
        if len(password) < 6:
            return {"success": False, "error": "Contraseña debe tener al menos 6 caracteres"}

        password_hashed = hash_password(password)

        existing = client.table("usuarios").select("id").eq("username", username).execute()
        if existing.data:
            return {"success": False, "error": "El usuario ya existe"}

        response = (
            client.table("usuarios")
            .insert({
                "username": username,
                "password_hash": password_hashed,
                "role": "USER",
            })
            .execute()
        )

        if response.data:
            user_id = response.data[0]["id"]
            access_token = crear_access_token(user_id, username, "USER")
            refresh_token = crear_refresh_token(user_id)
            return {
                "success": True,
                "user_id": user_id,
                "username": username,
                "role": "USER",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        return {"success": False, "error": "Error al crear usuario"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def refresh_access_token(refresh_token_str: str) -> dict:
    """Genera nuevo access token desde refresh token"""
    payload = verificar_refresh_token(refresh_token_str)
    if not payload:
        return {"success": False, "error": "Refresh token inválido o expirado"}

    try:
        client = get_supabase_client()
        response = client.table("usuarios").select("*").eq("id", payload["sub"]).execute()

        if not response.data:
            return {"success": False, "error": "Usuario no encontrado"}

        usuario = response.data[0]
        role = usuario.get("role", "USER")
        nuevo_access = crear_access_token(usuario["id"], usuario["username"], role)

        return {
            "success": True,
            "access_token": nuevo_access,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
