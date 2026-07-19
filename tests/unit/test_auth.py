import time
import pytest
from app.core.auth import (
    hash_password,
    verificar_password,
    hash_password_sha256,
    crear_access_token,
    crear_refresh_token,
    verificar_access_token,
    verificar_refresh_token,
    verificar_token,
    registrar_intento_login,
    esta_bloqueado,
    limpiar_intento,
    UserRole,
    MAX_LOGIN_ATTEMPTS,
    LOGIN_WINDOW,
)


# ============================
# TESTS DE BCRYPT
# ============================

def test_hash_password_genera_hash_bcrypt():
    pwd = "mi_password_segura"
    hashed = hash_password(pwd)
    assert hashed.startswith("$2")
    assert hashed != pwd


def test_hash_password_diferente_cada_vez():
    pwd = "misma_password"
    h1 = hash_password(pwd)
    h2 = hash_password(pwd)
    assert h1 != h2  # Sal diferente cada vez


def test_verificar_password_correcta():
    pwd = "test123456"
    hashed = hash_password(pwd)
    assert verificar_password(pwd, hashed) is True


def test_verificar_password_incorrecta():
    pwd = "test123456"
    hashed = hash_password(pwd)
    assert verificar_password("otra_password", hashed) is False


def test_verificar_password_hash_invalido():
    assert verificar_password("cualquiera", "hash_invalido") is False


def test_hash_sha256_legacy():
    """Test del hash legacy para migración"""
    pwd = "password123"
    sha_hash = hash_password_sha256(pwd)
    assert len(sha_hash) == 64  # SHA256 produce 64 hex chars


# ============================
# TESTS DE JWT
# ============================

def test_crear_y_verificar_access_token():
    token = crear_access_token("user123", "marcelo", "USER")
    payload = verificar_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["username"] == "marcelo"
    assert payload["role"] == "USER"
    assert payload["type"] == "access"


def test_crear_y_verificar_refresh_token():
    token = crear_refresh_token("user123")
    payload = verificar_refresh_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["type"] == "refresh"
    assert "jti" in payload  # ID único


def test_access_token_no_es_refresh():
    token = crear_access_token("user123", "marcelo")
    payload = verificar_refresh_token(token)
    assert payload is None  # Tipo incorrecto


def test_refresh_token_no_es_access():
    token = crear_refresh_token("user123")
    payload = verificar_access_token(token)
    assert payload is None  # Tipo incorrecto


def test_token_invalido():
    assert verificar_token("token_falso") is None
    assert verificar_token("") is None


def test_token_expirado():
    """Simula token expiriendo (con exp en el pasado)"""
    import jwt
    from app.core.auth import JWT_SECRET, JWT_ALGORITHM

    payload = {
        "sub": "user123",
        "type": "access",
        "iat": time.time() - 10000,
        "exp": time.time() - 1,  # Expiró hace 1 segundo
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    assert verificar_token(token) is None


def test_token_con_firma_incorrecta():
    """Token firmado con otro secret debe ser rechazado"""
    import jwt
    from app.core.auth import JWT_ALGORITHM

    payload = {
        "sub": "user123",
        "type": "access",
        "iat": time.time(),
        "exp": time.time() + 3600,
    }
    # Firmar con secret incorrecto
    token_falso = jwt.encode(payload, "secret_incorrecto", algorithm=JWT_ALGORITHM)
    assert verificar_token(token_falso) is None


# ============================
# TESTS DE RATE LIMITING
# ============================

def test_rate_limit_permitir_primeros_intentos():
    ip = "192.168.1.100"
    limpiar_intento(ip)
    for _ in range(MAX_LOGIN_ATTEMPTS - 1):
        assert registrar_intento_login(ip) is True
    limpiar_intento(ip)


def test_rate_limit_bloquear_despues_de_max():
    ip = "192.168.1.101"
    limpiar_intento(ip)
    for _ in range(MAX_LOGIN_ATTEMPTS):
        registrar_intento_login(ip)
    assert esta_bloqueado(ip) is True
    assert registrar_intento_login(ip) is False
    limpiar_intento(ip)


def test_rate_limit_cleanup_por_ventana():
    ip = "192.168.1.102"
    limpiar_intento(ip)
    # Simular intentos viejos
    from app.core.auth import _login_attempts
    _login_attempts[ip] = [time.time() - LOGIN_WINDOW - 1]  # Fuera de ventana
    assert esta_bloqueado(ip) is False
    limpiar_intento(ip)


def test_limpiar_intento_despues_de_exito():
    ip = "192.168.1.103"
    registrar_intento_login(ip)
    registrar_intento_login(ip)
    limpiar_intento(ip)
    assert esta_bloqueado(ip) is False


# ============================
# TESTS DE ROLES
# ============================

def test_user_roles():
    assert UserRole.ADMIN.value == "ADMIN"
    assert UserRole.USER.value == "USER"
    assert UserRole.VIEWER.value == "VIEWER"
