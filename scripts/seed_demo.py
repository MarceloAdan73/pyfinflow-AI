"""
Seed script para datos demo de PyStreamFlow-AI.

Uso:
    python scripts/seed_demo.py

Crea:
    - 2 usuarios (1 admin + 1 user normal)
    - ~70 transacciones en 6 meses (ingresos y gastos variados)
    - 6 presupuestos mensuales
    - 3 metas de ahorro con diferentes progresos
    - Configuraciones de usuario y AI por defecto

La contraseña de ambos usuarios es: demo123
"""

import random
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

from app.core.auth import hash_password
from app.core.database import get_db_session, init_db
from app.core.models_db import (
    AIProviderConfig,
    Budget,
    ChatMessage,
    CustomCategory,
    Goal,
    Transaction,
    User,
    UserConfig,
)


def generar_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def fecha_aleatoria(mes: int, anio: int = 2026) -> str:
    """Genera una fecha aleatoria dentro del mes dado."""
    dia = random.randint(1, 28)
    return f"{anio}-{mes:02d}-{dia:02d}"


def crear_usuarios(session):
    """Crea 2 usuarios: admin y demo."""
    usuarios = []

    admin = User(
        id=generar_id("user"),
        username="admin",
        password_hash=hash_password("demo123"),
        role="ADMIN",
    )
    usuarios.append(admin)

    demo = User(
        id=generar_id("user"),
        username="demo",
        password_hash=hash_password("demo123"),
        role="USER",
    )
    usuarios.append(demo)

    session.add_all(usuarios)
    session.flush()
    print("  Usuarios creados: admin (ADMIN), demo (USER)")
    return usuarios


def crear_transactions(session, user_id: str):
    """Crea ~70 transacciones variadas en 6 meses."""
    txns = []

    # Ingresos fijos mensuales (Salario)
    for mes in range(1, 7):
        txns.append(Transaction(
            id=generar_id("txn"),
            user_id=user_id,
            tipo="Ingreso",
            monto=random.uniform(450000, 550000),
            categoria="Salario",
            descripcion=f"Sueldo mes {mes}",
            fecha=fecha_aleatoria(mes),
            moneda="ARS",
        ))

    # Ingresos extra esporádicos
    ingresos_extra = [
        ("Freelance", 80000, "Diseño web para cliente"),
        ("Freelance", 120000, "Desarrollo de app móvil"),
        ("Inversiones", 15000, "Rendimiento FCI money market"),
        ("Regalos", 20000, "Plata de cumpleaños"),
    ]
    for cat, monto, desc in ingresos_extra:
        txns.append(Transaction(
            id=generar_id("txn"),
            user_id=user_id,
            tipo="Ingreso",
            monto=monto + random.uniform(-5000, 5000),
            categoria=cat,
            descripcion=desc,
            fecha=fecha_aleatoria(random.randint(1, 6)),
            moneda="ARS",
        ))

    # Gastos recurrentes mensuales
    gastos_recurrentes = [
        ("Vivienda", 180000, "Alquiler departamento"),
        ("Vivienda", 25000, "Expensas"),
        ("Servicios", 12000, "Internet fibra óptica"),
        ("Servicios", 8000, "Electricidad"),
        ("Servicios", 4000, "Agua"),
        ("Servicios", 6000, "Gas"),
        ("Salud", 15000, "Obra social médico familiar"),
        ("Educación", 25000, "Curso online Udemy"),
    ]

    for mes in range(1, 7):
        for cat, monto_base, desc in gastos_recurrentes:
            variacion = random.uniform(0.85, 1.15)
            txns.append(Transaction(
                id=generar_id("txn"),
                user_id=user_id,
                tipo="Gasto",
                monto=round(monto_base * variacion, 2),
                categoria=cat,
                descripcion=desc,
                fecha=fecha_aleatoria(mes),
                moneda="ARS",
            ))

    # Gastos variables (comida, transporte, ocio, salud)
    gastos_variables = [
        ("Comida", "Supermercado mensual", 35000, 55000),
        ("Comida", "Restaurante con amigos", 8000, 20000),
        ("Comida", "Delivery rappi", 5000, 12000),
        ("Transporte", "Uber viajes", 3000, 10000),
        ("Transporte", "Nafta estación", 15000, 25000),
        ("Transporte", "Sube colectivo", 4000, 6000),
        ("Ocio", "Cine + snacks", 5000, 8000),
        ("Ocio", "Salida boliche", 10000, 25000),
        ("Ocio", "Suscripción Netflix", 2500, 2500),
        ("Ocio", "Suscripción Spotify", 1200, 1200),
        ("Salud", "Farmacia", 5000, 15000),
        ("Salud", "Consulta médica", 8000, 15000),
    ]

    for mes in range(1, 7):
        # 2-4 transacciones de comida por mes
        for _ in range(random.randint(2, 4)):
            cat, desc, min_monto, max_monto = random.choice([g for g in gastos_variables if g[0] == "Comida"])
            txns.append(Transaction(
                id=generar_id("txn"),
                user_id=user_id,
                tipo="Gasto",
                monto=round(random.uniform(min_monto, max_monto), 2),
                categoria=cat,
                descripcion=desc,
                fecha=fecha_aleatoria(mes),
                moneda="ARS",
            ))

        # 1-2 transportes
        for _ in range(random.randint(1, 2)):
            cat, desc, min_monto, max_monto = random.choice([g for g in gastos_variables if g[0] == "Transporte"])
            txns.append(Transaction(
                id=generar_id("txn"),
                user_id=user_id,
                tipo="Gasto",
                monto=round(random.uniform(min_monto, max_monto), 2),
                categoria=cat,
                descripcion=desc,
                fecha=fecha_aleatoria(mes),
                moneda="ARS",
            ))

        # 1-2 ocio
        for _ in range(random.randint(1, 2)):
            cat, desc, min_monto, max_monto = random.choice([g for g in gastos_variables if g[0] == "Ocio"])
            txns.append(Transaction(
                id=generar_id("txn"),
                user_id=user_id,
                tipo="Gasto",
                monto=round(random.uniform(min_monto, max_monto), 2),
                categoria=cat,
                descripcion=desc,
                fecha=fecha_aleatoria(mes),
                moneda="ARS",
            ))

        # 1 salud ocasionales
        if random.random() > 0.4:
            cat, desc, min_monto, max_monto = random.choice([g for g in gastos_variables if g[0] == "Salud"])
            txns.append(Transaction(
                id=generar_id("txn"),
                user_id=user_id,
                tipo="Gasto",
                monto=round(random.uniform(min_monto, max_monto), 2),
                categoria=cat,
                descripcion=desc,
                fecha=fecha_aleatoria(mes),
                moneda="ARS",
            ))

    session.add_all(txns)
    session.flush()
    print(f"  Transacciones creadas: {len(txns)} ({sum(1 for t in txns if t.tipo == 'Ingreso')} ingresos, {sum(1 for t in txns if t.tipo == 'Gasto')} gastos)")
    return txns


def crear_presupuestos(session, user_id: str):
    """Crea presupuestos para el mes actual."""
    presupuestos = []

    limits = {
        "Comida": 80000,
        "Vivienda": 220000,
        "Transporte": 30000,
        "Servicios": 40000,
        "Ocio": 25000,
        "Salud": 20000,
        "Educación": 30000,
    }

    mes_actual = "2026-07"
    mes_anterior = "2026-06"

    for mes in [mes_anterior, mes_actual]:
        for cat, limite in limits.items():
            presupuestos.append(Budget(
                id=generar_id("bud"),
                user_id=user_id,
                categoria=cat,
                limite=limite + random.uniform(-5000, 5000),
                mes=mes,
            ))

    session.add_all(presupuestos)
    session.flush()
    print(f"  Presupuestos creados: {len(presupuestos)} ({len(limits)} categorías × 2 meses)")
    return presupuestos


def crear_metas(session, user_id: str):
    """Crea 3 metas de ahorro con diferentes progresos."""
    metas = [
        Goal(
            id=generar_id("goal"),
            user_id=user_id,
            nombre="Vacaciones Europa",
            objetivo=800000,
            ahorrado=200000,
            fecha_limite="2026-12-31",
            categoria="Viajes",
        ),
        Goal(
            id=generar_id("goal"),
            user_id=user_id,
            nombre="Fondo de emergencia",
            objetivo=500000,
            ahorrado=350000,
            fecha_limite=None,
            categoria="Ahorro",
        ),
        Goal(
            id=generar_id("goal"),
            user_id=user_id,
            nombre="Notebook nueva",
            objetivo=350000,
            ahorrado=320000,
            fecha_limite="2026-09-30",
            categoria="Tecnología",
        ),
    ]

    session.add_all(metas)
    session.flush()
    for m in metas:
        pct = round(m.ahorrado / m.objetivo * 100, 1)
        print(f"  Meta: {m.nombre} → ${m.ahorrado:,.0f} / ${m.objetivo:,.0f} ({pct}%)")
    return metas


def crear_configs(session, usuarios):
    """Crea configuraciones de usuario y AI por defecto."""
    configs = []
    ai_configs = []

    for user in usuarios:
        configs.append(UserConfig(
            user_id=user.id,
            moneda_activa="ARS",
        ))
        ai_configs.append(AIProviderConfig(
            user_id=user.id,
        ))

    session.add_all(configs + ai_configs)
    session.flush()
    print(f"  Configs creados: {len(configs)} usuarios + {len(ai_configs)} AI configs")


def main():
    print("=" * 60)
    print("  PyStreamFlow-AI — Seed de datos demo")
    print("=" * 60)
    print()

    print("1. Creando tablas...")
    init_db()

    with get_db_session() as session:
        # Limpiar datos existentes
        print("2. Limpiando datos existentes...")
        session.query(ChatMessage).delete()
        session.query(AIProviderConfig).delete()
        session.query(UserConfig).delete()
        session.query(Goal).delete()
        session.query(Budget).delete()
        session.query(Transaction).delete()
        session.query(CustomCategory).delete()
        session.query(User).delete()
        session.commit()
        print("  Datos eliminados.")

        print("3. Creando usuarios...")
        usuarios = crear_usuarios(session)

        print("4. Creando transacciones...")
        for user in usuarios:
            print(f"\n  Usuario: {user.username}")
            crear_transactions(session, user.id)

        print("\n5. Creando presupuestos...")
        for user in usuarios:
            print(f"\n  Usuario: {user.username}")
            crear_presupuestos(session, user.id)

        print("\n6. Creando metas de ahorro...")
        for user in usuarios:
            print(f"\n  Usuario: {user.username}")
            crear_metas(session, user.id)

        print("\n7. Creando configuraciones...")
        crear_configs(session, usuarios)

        session.commit()

    print()
    print("=" * 60)
    print("  ¡Seed completado exitosamente!")
    print("=" * 60)
    print()
    print("  Usuarios creados:")
    print("    - admin / demo123 (rol: ADMIN)")
    print("    - demo  / demo123 (rol: USER)")
    print()
    print("  Para probar la API:")
    print("    uvicorn app.api.main:app --reload --port 8000")
    print("    POST /auth/login → {\"username\": \"demo\", \"password\": \"demo123\"}")
    print()
    print("  Swagger UI:")
    print("    http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
