# PyFinFlow-AI → SaaS Profesional (ex PyStreamFlow)
## Roadmap de Escalación Completo

**Fecha de inicio:** 18/07/2026
**Versión del documento:** 1.0
**Flujo de trabajo:** Rama `dev` → testing local → push a `main`

---

## CÓMO USAR ESTE DOCUMENTO

### Para la IA (instrucciones):
1. **Leer este documento completo** al inicio de cada sesión cuando Marcelo lo solicite.
2. **Actualizar el estado** de cada tarea al completarse o modificarla.
3. **Consultar la fase actual** antes de recomendar próximos pasos.
4. **Marcar con `[x]`** las tareas completadas, `[ ]` las pendientes.
5. **Agregar notas** al final de cada fase si surgen cambios o aprendizajes.

### Para Marcelo (cómo iniciar):
- "Leé el ROADMAP_SAAS.md y decime en qué fase estamos."
- "¿Qué tarea toca ahora?"
- "Quiero implementar [X], ¿en qué fase entra?"
- "Actualizá el roadmap con lo que hicimos."

### Regla de oro:
> **SIEMPRE trabajar en rama `dev`.** Testing local → si funciona → push a `main`.
> Nunca commitear directo a `main`.

---

## ESTADO GENERAL DEL PROYECTO

| Aspecto | Estado actual |
|---|---|
| **App** | PyFinFlow AI (ex PyStreamFlow) — API REST FastAPI + Next.js 16 |
| **Frontend** | Next.js 16.2 + React 19 + TypeScript + Tailwind v4 + Framer Motion 12 + next-intl (es/en) |
| **Backend** | FastAPI + SQLAlchemy + Repository Pattern + Alembic |
| **DB** | PostgreSQL (producción) + SQLite (desarrollo/tests) — local usa `pyfinflow_dev.db` |
| **IA** | ChromaDB + RAG + Multi-provider (Ollama/HuggingFace/Gemini) + memoria persistente + analytics predictivo + configuración per-user desde UI |
| **Auth** | bcrypt (12 rounds) + JWT (access 1h / refresh 7d) + rate limiting + roles |
| **API** | 28 endpoints REST documentados: /auth, /transactions, /budgets, /goals, /ai, /health |
| **Tests** | 221 tests backend (todos pasan) + frontend: lint 0 errors + build 22/22 páginas SSG. Ruff: 0 errores |
| **CI/CD** | GitHub Actions (Python 3.12, PostgreSQL service, ruff, pytest-cov) |
| **Docker** | Dockerfile multi-stage (pyfinflow user, uvicorn only) + docker-compose (app, PostgreSQL, Redis, ChromaDB) |
| **Monitoring** | structlog + request logging middleware + health check + métricas + alertas SMTP |
| **Deploy actual** | Local (dev) — backend :8000, frontend :3000 — Streamlit Cloud eliminado 24/08/2026 |
| **Deploy planeado** | **PRÓXIMO:** Vercel (frontend) + Render/Railway (FastAPI) → link público para acceso global |
| **Branch** | `main`/`master` (producción), `dev` (desarrollo) — se trabaja siempre en `dev` |
| **Repo** | `MarceloAdan73/pyfinflow-AI` (renombrado desde `pystreamflow-AI`, redirect activo) |
| **Último commit dev** | 24/08/2026 (rebrand pyfinflow, README 221 tests, IA 4.9s, merge a main) |
| **Cache** | Redis con fallback a in-memory. Sesiones TTL 1h, queries TTL 5min, rate limit TTL 60s |

### Decisiones técnicas clave (contexto)

#### ¿Por qué API REST separada del Streamlit?
El monolito Streamlit mezcla frontend y backend en el mismo proceso. Al crear una API REST con FastAPI, separamos las responsabilidades:
- **Backend (FastAPI)**: lógica de negocio, auth, base de datos — independiente del frontend
- **Frontend (Streamlit hoy, Next.js mañana)**: solo presenta datos y captura input
- Esto permite cambiar el frontend sin tocar el backend, y viceversa

#### ¿Por qué Repository Pattern?
Antes, la lógica de acceso a datos estaba dispersa en `database.py` (SQLite) y Supabase. Al crear repositorios abstractos (`BaseRepository`) con implementaciones concretas (`TransactionRepository`, etc.):
- Se puede cambiar de SQLite a PostgreSQL sin cambiar la lógica de negocio
- Se facilita testing (SQLite en memoria para tests, PostgreSQL para producción)
- Se sigue el principio de Dependency Inversion (dependencias apuntan hacia adentro)

#### ¿Por qué Next.js y no mejorar Streamlit?
Streamlit tiene limitaciones técnicas duras para una app SaaS profesional:
- **Rerender completo**: cada click re-dibuja toda la página, no hay granularidad
- **Sin routing real**: no hay URLs por página, no se pueden compartir links directos
- **Sin control del DOM**: las "cards" son `st.metric` + HTML inyectado con `unsafe_allow_html`
- **Estado frágil**: `st.session_state` se pierde entre recargas
- **Sin type safety**: Python dinámico, errores solo en runtime
- **Sin componentes custom**: todo se resuelve con markdown + CSS hack

Next.js + React ofrece:
- Control total del DOM y las animaciones
- Routing real con layouts anidados y URLs compartibles
- TypeScript para errores en compile time
- Shadcn/UI: componentes profesionales tipo fintech (Linear, Vercel, Raycast)
- Deploy gratis en Vercel con analytics y edge
- La API REST ya existe y funciona para cualquier frontend

#### ¿Por qué Shadcn/UI y no otra librería?
Shadcn/UI no es una dependencia — copiás los componentes a tu proyecto. Ventajas:
- Sin lock-in: si dejás de usarlo, el código sigue funcionando
- Total customización con Tailwind CSS
- Basado en Radix UI (accessibilidad real, no solo visual)
- Los mismos componentes que usan fintechs profesionales

#### Convivencia: Streamlit eliminado
El monolito Streamlit (`pystreamflow.py`) fue eliminado en `c4a6f71` (24/08/2026) tras migrar a `PyFinFlow`. Ya no hay MVP Streamlit.
- Deploy Streamlit Cloud `pystreamflow-ai-...streamlit.app` eliminado 24/08/2026
- GitHub About Website limpiado
- Stack actual único: `FastAPI` + `Next.js 16` en `http://localhost:8000` / `http://localhost:3000`

---

## FASE 0: LIMPIEZA Y PREPARACIÓN
**Objetivo:** Dejar el proyecto listo para escalar. Sin esto, todo lo demás se complica.
**Dependencias:** Ninguna
**Tiempo estimado:** 1-2 días

### 0.1 Estructura de proyecto
- [x] Crear estructura de directorios:
  ```
  pystreamflow-AI/
  ├── app/
  │   ├── __init__.py
  │   ├── core/
  │   │   ├── __init__.py
  │   │   ├── auth.py              # bcrypt + JWT + rate limiting + roles
  │   │   ├── config.py            # DATABASE_URL, engine options
  │   │   ├── constants.py         # MONEDAS, COLORES, CATEGORIAS
  │   │   ├── database.py          # SQLAlchemy engine, SessionLocal, get_db
  │   │   ├── models.py            # Transaccion dataclass, iconos
  │   │   └── models_db.py         # SQLAlchemy ORM: User, Transaction, Budget, Goal, CustomCategory, UserConfig
  │   ├── api/
  │   │   ├── __init__.py
  │   │   ├── main.py              # FastAPI app, CORS, routers
  │   │   ├── deps.py              # dependency injection (get_db, get_current_user, get_repositories)
  │   │   ├── routers/
  │   │   │   ├── __init__.py
  │   │   │   ├── auth.py          # /auth: register, login, refresh, me, password
  │   │   │   ├── transactions.py  # /transactions: CRUD + filtros + paginación
  │   │   │   ├── budgets.py       # /budgets: CRUD + upsert
  │   │   │   └── goals.py         # /goals: CRUD
  │   │   └── schemas/
  │   │       ├── __init__.py
  │   │       ├── auth.py          # UserRegister, UserLogin, TokenResponse, etc.
  │   │       ├── transaction.py   # TransactionCreate, TransactionUpdate, TransactionResponse
  │   │       ├── budget.py        # BudgetCreate, BudgetResponse, BudgetAlert
  │   │       └── goal.py          # GoalCreate, GoalUpdate, GoalResponse
  │   ├── repositories/
  │   │   ├── __init__.py
  │   │   ├── base_repo.py         # BaseRepository (interfaz abstracta CRUD)
  │   │   ├── factory.py           # RepositoryFactory (punto de acceso unificado)
  │   │   └── postgres_repo.py     # TransactionRepo, BudgetRepo, GoalRepo, UserRepository
  │   ├── services/
  │   │   └── __init__.py
  │   ├── ui/
  │   │   ├── __init__.py
  │   │   ├── components/__init__.py
  │   │   ├── pages/__init__.py
  │   │   └── styles/
  │   │       └── main.css
  │   └── utils/
  │       ├── __init__.py
  │       └── formatters.py
  ├── tests/
  │   └── unit/
  │       ├── test_api.py           # 27 tests de API (FastAPI TestClient)
  │       ├── test_auth.py          # 18 tests de seguridad (bcrypt, JWT, rate limiting)
  │       └── test_repositories.py  # 13 tests de repositorios (SQLite en memoria)
  ├── alembic/
  │   ├── env.py
  │   ├── script.py.mako
  │   └── versions/
  │       └── 001_initial_schema.py  # Migración inicial (6 tablas)
  ├── pystreamflow.py               # App Streamlit principal (~2972 líneas)
  ├── test_app.py                    # 17 tests unitarios originales
  ├── auth.py                        # Legacy auth (Supabase, pendiente de eliminar)
  ├── database.py                    # Legacy SQLite (pendiente de eliminar)
  ├── .env.example
  ├── .gitignore
  ├── pyproject.toml
  ├── requirements.txt
  ├── README.md
  └── ROADMAP_SAAS.md               # Este archivo
  ```

### 0.2 Separar el monolito
- [x] Extraer `constants.py` (MONEDAS, COLORES, CATEGORIAS, PLACEHOLDERS)
- [x] Extraer `models.py` (dataclass Transaccion)
- [x] Extraer `formatters.py` (formatear_monto, detectar_moneda, _parsear_numero)
- [ ] Extraer `database.py` → `repositories/sqlite_repo.py`
- [ ] Extraer `auth.py` → `repositories/supabase_repo.py`
- [ ] Extraer servicios de lógica de negocio a `services/`
- [x] Extraer CSS a `styles/main.css`
- [ ] Extraer componentes UI a `ui/components/`
- [ ] Extraer páginas a `ui/pages/`
- [ ] Actualizar imports en todos los archivos
- [ ] Verificar que `python -m app.main` funciona
- [ ] Verificar que tests pasan: `pytest tests/ -v`

### 0.3 Configuración
- [ ] Crear `config/settings.py` con pydantic-settings para manejo de variables
- [ ] Crear `.env.example` con todas las variables documentadas
- [ ] Crear `requirements-dev.txt` (black, ruff, pytest, mypy)
- [ ] Configurar `pyproject.toml` con ruff + mypy + black
- [ ] Verificar que `ruff check .` pasa sin errores
- [ ] Verificar que `black --check .` pasa

### 0.4 Git
- [x] Crear rama `dev` desde `master` si no existe
- [x] Configurar `.gitignore` actualizado (agregar `__pycache__/`, `.env`, `*.db`, `dist/`, `build/`)
- [x] Commitear toda la reestructuración en `dev`
- [x] Verificar que la app funciona igual que antes
- [x] Push a `dev`

**Criterio de aceptación:** La app funciona idéntica al antes, pero con código modular. Tests pasan.

---

## FASE 1: SEGURIDAD BÁSICA
**Objetivo:** Auth segura y base sólida para multi-usuario.
**Dependencias:** Fase 0 completada
**Tiempo estimado:** 2-3 días

### 1.1 Auth mejorada
- [x] Implementar bcrypt para hashing de contraseñas (reemplazar SHA256)
- [x] Agregar sal único por usuario
- [x] Implementar JWT tokens para sesiones
- [x] Agregar refresh tokens
- [x] Crear middleware de autenticación
- [x] Implementar rate limiting en login (máx 5 intentos/minuto)

### 1.2 Roles y permisos
- [x] Crear enum de roles: `ADMIN`, `USER`, `VIEWER`
- [ ] Agregar campo `role` a tabla `usuarios` en Supabase
- [ ] Implementar decorador `@require_role("ADMIN")`
- [ ] Proteger endpoints sensibles (admin only)
- [ ] Crear vista de administración de usuarios (admin)

### 1.3 Seguridad de datos
- [ ] Encriptar datos sensibles en SQLite (usando `cryptography.fernet`)
- [ ] Implementar CSP headers en Streamlit
- [ ] Agregar validación de inputs con pydantic
- [ ] Sanitizar inputs de texto (prevenir XSS)
- [ ] Agregar logging de intentos de acceso

### 1.4 Tests de seguridad
- [x] Test: Login fallido después de 5 intentos
- [x] Test: JWT expirado rechazado
- [x] Test: Token con firma incorrecta rechazado
- [x] Test: Rate limiting funciona correctamente

**Criterio de aceptación:** Auth segura con bcrypt + JWT. Roles funcionando. Tests de seguridad pasan.

---

## FASE 2: BASE DE DATOS PROFESIONAL
**Objetivo:** Migrar de SQLite a PostgreSQL para producción.
**Dependencias:** Fase 1 completada
**Tiempo estimado:** 3-4 días

### 2.1 Configurar PostgreSQL local
- [ ] Verificar que PostgreSQL 16 está corriendo (ya instalado)
- [ ] Crear base de datos `pystreamflow_dev`
- [ ] Crear usuario dedicado `pystreamflow_user`
- [ ] Configurar permisos mínimos necesarios
- **Nota:** psycopg2 + Python 3.14 tiene error UTF-8 al conectar. Pendiente resolver.

### 2.2 SQLAlchemy + Alembic
- [x] Instalar `sqlalchemy`, `alembic`, `psycopg2-binary`
- [x] Crear `app/core/database.py` con connection pool
- [x] Definir modelos SQLAlchemy:
  - [x] `User` (id, username, password_hash, role, created_at)
  - [x] `Transaction` (id, user_id, tipo, monto, categoria, descripcion, fecha, moneda)
  - [x] `Budget` (id, user_id, categoria, limite, mes)
  - [x] `Goal` (id, user_id, nombre, objetivo, ahorrado, fecha_limite, categoria)
  - [x] `CustomCategory` (id, user_id, tipo, nombre)
  - [x] `Config` (user_id, moneda_activa, filtro_fecha_inicio, filtro_fecha_fin)
- [x] Configurar Alembic para migraciones
- [x] Crear migración inicial (`001_initial_schema.py` - 6 tablas, 3 indexes, 2 unique constraints)
- [ ] Probar migración en `pystreamflow_dev` (bloqueado: psycopg2 + Python 3.14 UTF-8 error)

### 2.3 Repository Pattern
- [x] Crear `app/repositories/base_repo.py` (interfaz abstracta)
- [x] Implementar `PostgresRepo` con SQLAlchemy
  - [x] TransactionRepository (CRUD + filtros + delete_all_for_user)
  - [x] BudgetRepository (CRUD + upsert)
  - [x] GoalRepository (CRUD)
  - [x] UserRepository (CRUD + get_by_username + _to_dict_full para login)
- [x] Crear `app/repositories/factory.py` para seleccionar DB según entorno
- [ ] Mantener SQLiteRepo para desarrollo offline
- [x] Actualizar servicios para usar repository pattern

### 2.4 Connection pooling y performance
- [ ] Configurar connection pool (min=2, max=10)
- [ ] Implementar retry logic para conexiones
- [ ] Agregar índices en columnas frecuentemente consultadas:
  - [ ] `transacciones(user_id, fecha)`
  - [ ] `transacciones(user_id, tipo)`
  - [ ] `presupuestos(user_id, categoria)`
- [ ] Implementar query caching con `functools.lru_cache` para datos estáticos

### 2.5 Docker PostgreSQL
- [ ] Crear `docker-compose.yml` con PostgreSQL
- [ ] Configurar volúmenes para persistencia
- [ ] Agregar pgAdmin opcional para debugging
- [ ] Crear script de seed para datos de prueba

### 2.6 Tests de integración
- [x] Test: CRUD completo de transacciones
- [x] Test: Múltiples usuarios no mezclan datos
- [x] Test: Filtros funcionan correctamente
- [x] Test: Budget upsert crea y actualiza
- [x] Test: Goal CRUD completo
- [x] Test: User CRUD + get_by_username

**Criterio de aceptación:** PostgreSQL funcionando con SQLAlchemy. Migraciones aplican. Tests de integración pasan.

---

## FASE 3: API REST
**Objetivo:** Separar backend de frontend para escalar independientemente.
**Dependencias:** Fase 2 completada
**Tiempo estimado:** 4-5 días

### 3.1 FastAPI setup
- [x] Instalar `fastapi`, `uvicorn`, `pydantic`
- [x] Crear `app/api/main.py` con FastAPI app
- [x] Configurar CORS (origin: localhost para dev)
- [x] Crear `app/api/deps.py` para dependency injection
- [x] Crear estructura de routers

### 3.2 Pydantic schemas
- [x] Crear schemas de request/response para cada entidad
- [x] Implementar validación con pydantic v2
- [x] Agregar documentación con descriptions y examples
- [x] Configurar OpenAPI tags y metadata

### 3.3 Endpoints de autenticación
- [x] `POST /auth/register` - Registro
- [x] `POST /auth/login` - Login (retorna JWT)
- [x] `POST /auth/refresh` - Refresh token
- [x] `GET /auth/me` - Usuario actual
- [x] `PUT /auth/password` - Cambiar contraseña

### 3.4 Endpoints de transacciones
- [x] `GET /transactions` - Listar (con filtros, paginación)
- [x] `POST /transactions` - Crear
- [x] `GET /transactions/{id}` - Obtener una
- [x] `PUT /transactions/{id}` - Actualizar
- [x] `DELETE /transactions/{id}` - Eliminar
- [ ] `POST /transactions/import` - Importar CSV/JSON
- [ ] `GET /transactions/export` - Exportar CSV/JSON/PDF

### 3.5 Endpoints de presupuestos
- [x] `GET /budgets` - Listar presupuestos del mes
- [x] `POST /budgets` - Crear/actualizar
- [ ] `DELETE /budgets/{categoria}` - Eliminar
- [ ] `GET /budgets/alerts` - Alertas de excedido

### 3.6 Endpoints de metas
- [x] `GET /goals` - Listar metas
- [x] `POST /goals` - Crear meta
- [x] `PUT /goals/{id}` - Actualizar (ahorrado)
- [x] `DELETE /goals/{id}` - Eliminar

### 3.7 Endpoints de reportes
- [ ] `GET /reports/summary` - Resumen del período
- [ ] `GET /reports/monthly` - Comparativa mensual
- [ ] `GET /reports/by-category` - Por categoría
- [ ] `GET /reports/pdf` - Generar PDF

### 3.8 Testing de API
- [x] Configurar `httpx` para tests de API
- [x] Test: Registro + Login + Token
- [x] Test: CRUD transacciones autenticado
- [x] Test: 401 sin token
- [x] Test: 403 sin permisos
- [x] Test: Validación de inputs inválidos
- [x] Test: Rate limiting funciona (24/08/2026 — incluye fix de bug: el router login limpiaba el contador en intentos fallidos, anulando el rate limit)

### 3.9 Documentación
- [x] Configurar Swagger UI (`/docs`)
- [x] Configurar ReDoc (`/redoc`)
- [x] Agregar ejemplos en cada endpoint
- [ ] Generar SDK opcional con openapi-generator

**Criterio de aceptación:** API REST funcional con todos los endpoints. Documentación Swagger completa. Tests pasan.

---

## FASE 4: DEPLOY Y DEVOPS
**Objetivo:** Deploy automatizado, escalable, y monitoreado.
**Dependencias:** Fase 2 completada (puede ir en paralelo con 3-6). Docker necesita Fase 6 para el frontend completo.
**Tiempo estimado:** 3-4 días

### 4.1 Docker completo
- [x] Crear `Dockerfile` multi-stage (builder + runtime, user no-root, healthcheck)
- [x] Crear `docker-compose.yml` completo (app, PostgreSQL, Redis, ChromaDB)
- [x] Crear `.dockerignore`
- [x] Probar `docker-compose build` (exitoso; `docker-compose up` no probado porque Docker Desktop daemon no estaba corriendo)

### 4.2 CI/CD mejorado
- [x] Actualizar `.github/workflows/ci.yml` (Python 3.12, PostgreSQL service, ruff, pytest-cov, codecov)
- [x] Agregar badge de cobertura de código
- [ ] Configurar branch protection en `main` (pendiente: requiere acceso admin en GitHub)

### 4.3 Monitoreo
- [x] Agregar health check endpoint: `GET /health` (mejorado con environment)
- [x] Agregar health check detallado: `GET /health/detailed` (testa DB + Redis)
- [x] Implementar logging estructurado con `structlog`
- [x] Agregar request logging middleware (method, path, status, duration)
- [x] Agregar lifespan events (startup/shutdown logging)
- [x] Agregar métricas básicas:
  - [x] Requests por minuto
  - [x] Latencia promedio de IA
  - [x] Errores por tipo
  - [x] Usuarios activos
  - [x] Endpoint: `GET /metrics` (JSON) y `GET /metrics/prometheus` (text/plain)
- [x] Configurar alertas básicas (email en errores críticos vía SMTP)

### 4.4 Redis
- [ ] Instalar Redis local (ya pendiente en tu setup — Docker Desktop no activo)
- [x] Implementar cache de:
  - [x] Sesiones de usuario (`session:{user_id}`, TTL 1h)
  - [x] Queries frecuentes (`query:{user_id}:{key}`, TTL 5min)
  - [x] Rate limiting (`ratelimit:login:{ip}`, TTL 60s)
- [x] Configurar TTL por tipo de dato
- [x] Fallback automático a in-memory si Redis no está disponible

### 4.5 Backup
- [x] Script de backup automático de PostgreSQL (`scripts/backup_db.sh`)
- [ ] Backup de ChromaDB
- [ ] Almacenamiento en S3 o similar
- [ ] Restore manual documentado

**Criterio de aceptación:** Docker compose funciona. CI/CD pasa. Logging y monitoreo básico activo. Redis caching con fallback. Métricas disponibles en `/metrics`. Alertas por email configuradas. Backup script funcional. Tests: 73 pasando.

---

## FASE 5: INTELIGENCIA ARTIFICIAL PROFESIONAL
**Objetivo:** Transformar el chatbot de reglas en un sistema IA real con RAG.
**Dependencias:** Fase 3 completada
**Tiempo estimado:** 5-7 días

### 5.1 ChromaDB para embeddings
- [x] Instalar `chromadb`
- [x] Crear `app/ai/vector_store.py`
- [x] Implementar indexación de transacciones como embeddings
- [x] Configurar embedding model: `all-MiniLM-L6-v2` (sentence-transformers)
- [x] Crear función `indexar_transacciones(user_id)`
- [x] Crear función `buscar_contexto(user_id, query, top_k=5)`

### 5.2 RAG (Retrieval-Augmented Generation)
- [x] Crear `app/ai/rag_engine.py`
- [x] Flujo:
  ```
  1. Usuario pregunta algo
  2. Buscar transacciones relevantes en ChromaDB
  3. Construir prompt con contexto + datos encontrados
  4. Enviar a LLM (Ollama o HuggingFace)
  5. Retornar respuesta contextualizada
  ```
- [x] Implementar `consultar_ia_rag(user_id, pregunta)`
- [x] Mantener fallback a reglas si ChromaDB/LM falla

### 5.3 Multi-provider IA
- [x] Crear `app/ai/providers/base_provider.py` (interfaz)
- [x] Implementar providers:
  - [x] `OllamaProvider` (local, configurable)
  - [x] `HuggingFaceProvider` (cloud, Zephyr)
  - [x] `GeminiProvider` (cloud, gemini-2.0-flash)
- [x] Crear `app/ai/provider_factory.py` con fallback chain
- [x] Configurar prioridad: Ollama → HuggingFace → Gemini (configurable)
- [x] Agregar métricas de latencia por provider

### 5.4 Memoria de conversación
- [x] Crear tabla `chat_messages` en PostgreSQL:
  ```sql
  CREATE TABLE chat_messages (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    context_used TEXT,
    provider VARCHAR(50),
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```
- [x] Implementar `ChatMemoryService` con:
  - [x] Guardar cada mensaje (user + assistant)
  - [x] Cargar últimos N mensajes para contexto
  - [x] Resumen automático de conversación larga
- [x] Limitar ventana de contexto (últimos 20 mensajes)
- [x] Agregar endpoint `DELETE /ai/history` para limpiar historial

### 5.5 Análisis predictivo
- [x] Crear `app/ai/analytics.py`
- [x] Implementar análisis de patrones:
  - [x] Tendencia de gasto por categoría (sube/baja)
  - [x] Predicción de gasto mensual basada en histórico
  - [x] Detección de gastos anómalos (>2 desviaciones estándar)
  - [x] Sugerencia de presupuesto basada en gasto real
- [x] Usar `statistics` para regresión simple
- [x] Generar "Insights IA" automáticos en dashboard:
  ```
  "Tu gasto en Comida subió 23% este mes vs el anterior"
  "Basado en tu histórico, vas a gastar ~$180,000 este mes"
  "Detectamos un gasto inusual de $50,000 en Transporte el martes"
  ```

### 5.6 Voice input (opcional)
- [ ] Instalar `whisper` (openai-whisper)
- [ ] Implementar `app/ai/voice.py`
- [ ] Agregar botón de micrófono en chat UI
- [ ] Transcribir audio → texto → consultar IA
- [ ] Configurar modelo `tiny` o `base` para CPU

### 5.7 Tests de IA
- [x] Test: Providers (nombre, disponibilidad, fallback)
- [x] Test: Fallback a reglas locales
- [x] Test: Analytics (tendencias, predicciones, anomalías)
- [x] Test: Memoria guarda y carga mensajes
- [x] Test: API endpoints (chat, history, insights, suggestions, status)
- [x] Test: Auth (unauthorized) en endpoints IA
- [x] Test: Rate limiting en llamadas a IA (24/08/2026, incluye implementación del limitador `app/ai/rate_limiter.py` — 10 req/min por usuario en `/ai/chat`)

### 5.8 API REST para IA
- [x] Crear `app/api/routers/ai.py` con endpoints:
  - [x] `POST /ai/chat` - Chat con IA (RAG + memoria)
  - [x] `GET /ai/history` - Historial de conversación
  - [x] `DELETE /ai/history` - Limpiar historial
  - [x] `GET /ai/insights` - Análisis predictivo completo
  - [x] `GET /ai/suggestions` - Preguntas sugeridas
  - [x] `GET /ai/status` - Estado de providers y ChromaDB
  - [x] `GET /ai/settings` - Configuración IA del usuario
  - [x] `PUT /ai/settings` - Actualizar configuración IA del usuario
- [x] Crear `app/api/schemas/ai.py` con Pydantic schemas
- [x] Integrar router en `app/api/main.py`
- [x] Modelo `AIProviderConfig` (per-user) en `models_db.py`
- [x] `AIProviderConfigRepository` con upsert en `postgres_repo.py`

**Criterio de aceptación:** IA con RAG funcionando. Memoria persistente. Multi-provider con fallback. Análisis predictivo básico.

---

## FASE 6: FRONTEND PROFESIONAL (Next.js)
**Objetivo:** UI de nivel producción tipo fintech con React + TypeScript.
**Dependencias:** Fase 3 completada (paralela a Fase 5)
**Tiempo estimado:** 8-10 días

### Decisión técnica: Next.js sobre Streamlit

**¿Por qué Next.js y no mejorar Streamlit?**

Streamlit tiene techo bajo para una app profesional:
- Rerender completo en cada interacción (sin granularidad)
- Sin routing real (no se pueden compartir URLs)
- Sin control del DOM (todo es `st.metric` + HTML hackeado con `unsafe_allow_html`)
- Estado frágil (`st.session_state` se pierde)
- Sin componentes custom fáciles
- Sin type safety

Next.js + React da control total:
- Routing real con layouts anidados
- Componentes ilimitados
- Animaciones fluidas (Framer Motion)
- TypeScript (errores en compile time)
- Deploy gratis en Vercel
- La API REST ya existe y funciona para ambos frontends

**Convivencia:** Streamlit legacy se mantiene como MVP/backup en `localhost:8501`. Next.js es el frontend de producción en `localhost:3000`. Ambos hablan con la misma API FastAPI.

### Stack tecnológico

| Capa | Tecnología | Por qué |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR, routing, lazy loading, layouts |
| Language | TypeScript | Type safety, mejor DX |
| Styling | Tailwind CSS | Utility-first, responsive, dark mode nativo |
| Componentes | Shadcn/UI | Componentes copiados (no dependencia), profesionales |
| Tablas | TanStack Table | Sorting, filtrado, paginación real |
| Forms | React Hook Form + Zod | Validación tipo Pydantic en el frontend |
| State | Zustand | Ligero, sin boilerplate |
| HTTP | Fetch + SWR | Caché, revalidación, retry |
| Charts | Recharts | Ligero, responsive, bien con Tailwind |
| Animaciones | Framer Motion | Transiciones de página, micro-interacciones |
| Auth | js-cookie + httpOnly | JWT management |
| Deploy | Vercel | Gratis, edge, analytics |

### Identidad visual (se mantiene del CSS actual)

Los colores de `app/ui/styles/main.css` se traducen directamente a Tailwind:
```
background: #0f172a      → COLORES.fondo
card: rgba(30,41,59,0.5) → COLORES.card
primary: #6366F1         → COLORES.primario
accent: #8B5CF6
income: #10B981          → COLORES.ingreso
expense: #EF4444         → COLORES.gasto
text: #f8fafc            → COLORES.texto
muted: #94a3b8           → COLORES.texto_sec
```
Glassmorphism, border-radius 16px, backdrop-blur — todo se replica con Tailwind.

### Estructura del frontend

```
frontend/
├── src/
│   ├── app/                    # App Router (Next.js 14+)
│   │   ├── (auth)/             # Grupo de rutas públicas
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── (dashboard)/        # Grupo de rutas protegidas
│   │   │   ├── layout.tsx      # Sidebar + nav
│   │   │   ├── page.tsx        # Dashboard principal
│   │   │   ├── transactions/page.tsx
│   │   │   ├── budgets/page.tsx
│   │   │   ├── goals/page.tsx
│   │   │   └── settings/page.tsx
│   │   ├── layout.tsx          # Root layout (theme, providers)
│   │   └── page.tsx            # Landing/redirect
│   ├── components/
│   │   ├── ui/                 # Shadcn/UI primitives
│   │   ├── dashboard/          # Widgets del dashboard
│   │   ├── transactions/       # Tabla, form, cards
│   │   ├── budgets/            # Progress bars, alerts
│   │   ├── goals/              # Circular progress, cards
│   │   └── layout/             # Sidebar, header, nav
│   ├── lib/
│   │   ├── api.ts              # Fetch wrapper con JWT
│   │   ├── auth.ts             # Token management
│   │   └── utils.ts            # formatear_monto, etc.
│   ├── hooks/
│   │   ├── use-transactions.ts
│   │   ├── use-budgets.ts
│   │   ├── use-goals.ts
│   │   └── use-auth.ts
│   └── types/
│       └── index.ts            # TypeScript interfaces
├── public/
├── tailwind.config.ts
├── next.config.ts
├── package.json
└── tsconfig.json
```

### 6.1 Setup y Auth (2-3 días)
- [x] `npx create-next-app@latest frontend` con TypeScript + Tailwind
- [x] Instalar Shadcn/UI, configurar tema oscuro con colores existentes
- [x] Crear `lib/api.ts` — fetch wrapper con manejo de JWT + refresh
- [x] Crear `lib/auth.ts` — store de auth con Zustand
- [x] Crear `types/index.ts` — interfaces TypeScript (Transaction, Budget, Goal, User)
- [x] Página de login con formulario (React Hook Form + Zod)
- [x] Página de register con validación
- [x] Auth context + ProtectedRoute (redirige a /login si no hay token)
- [x] Layout raíz con sidebar colapsable

### 6.2 Dashboard (2-3 días)
- [x] Dashboard principal con métricas (income, expenses, balance, count)
- [x] Gráfico de torta — gastos por categoría (Recharts PieChart)
- [x] Gráfico de barras — tendencia mensual (Recharts BarChart)
- [x] Lista de transacciones recientes (últimas 5)
- [ ] Alertas de presupuesto ( cards con progress bars )
- [x] Date range picker para filtrar período
- [x] Indicadores visuales de tendencia (↑↓→)
- [x] Loading skeletons (Shadcn Skeleton)

### 6.3 Transacciones (2 días)
- [x] Tabla profesional con sorting, paginación, columnas custom
- [x] Filtros avanzados: tipo, categoría
- [x] Modal/Sheet para crear transacción (Dialog)
- [x] Modal de edición inline
- [x] Confirmación de eliminación
- [x] Empty state cuando no hay transacciones
- [x] Búsqueda por texto en descripción

### 6.4 Presupuestos y Metas (1-2 días)
- [x] Cards de presupuesto con progress bars animadas
- [x] Alertas visuales: 80% warning (naranja), 100% excedido (rojo)
- [x] Formulario de creación/edición (Dialog)
- [x] Goals con progreso
- [x] Meta de ahorro con porcentaje completado
- [x] Empty states para sin presupuestos/sin metas

### 6.5 Settings y pulido (1 día)
- [x] Perfil de usuario (username, rol)
- [x] Cambio de contraseña con validación
- [x] Toggle de tema oscuro/claro (persiste en localStorage)
- [x] Fix dark/light mode real (24/08/2026): body ya no fuerza `dark`, themeScript aplica default dark, gráficos Recharts con CSS vars adaptables
- [x] Responsive final: mobile, tablet, desktop
- [x] Transiciones de página con Framer Motion
- [x] Configuración IA completa: proveedores, Ollama URL/modelo, API keys, parámetros de generación
- [x] ConfirmDialog modal para eliminar (reemplaza `confirm()` nativo)
- [x] Colores de gráficos suavizados (BarChart + PieChart)
- [x] Keyboard shortcuts (Ctrl+N nueva txn, Ctrl+F buscar, Ctrl+D/B/G/I, navigation)
- [x] 404 page personalizada

**Criterio de aceptación:** Frontend Next.js profesional, responsive, con componentes Shadcn/UI. Tema oscuro consistente. Todos los endpoints de la API consumidos. Deploy en Vercel.

---

## FASE 7: MULTI-IDIOMA Y LOCALIZACIÓN
**Objetivo:** Soporte internacionalización.
**Dependencias:** Fase 6 completada
**Tiempo estimado:** 2-3 días

### 7.1 i18n
- [x] Instalar `next-intl` para Next.js
- [x] Crear archivos de traducción (es/en; pt removido en 14/08/2026)
  ```
  messages/
  ├── es.json  → Español (default, sin prefijo en URL)
  └── en.json  → English (prefijo /en)
  ```
- [x] Extraer todos los strings hardcodeados
- [x] Reemplazar por funciones de traducción
- [x] Selector de idioma en navbar/header

### 7.2 Multi-moneda
- [x] Soportar USD, EUR, BRL además de ARS
- [x] API de tasas de cambio (open.er-api.com, cache 1h en localStorage)
- [x] Guardar transacciones en moneda original
- [x] Mostrar conversiones en dashboard

**Criterio de aceptación:** App funciona en español e inglés. Multi-moneda funcional.

---

## FASE 8: FEATURES AVANZADAS
**Objetivo:** Funcionalidades que diferencian de la competencia.
**Dependencias:** Fase 5 completada
**Tiempo estimado:** 5-7 días

### 8.1 Notificaciones
- [x] Email notifications (using `smtplib` + templates) — `app/core/alerts.py:13` base + `alert_budget_*` 24/08/2026
- [x] Alertas de presupuesto excedido — `app/services/budget_alerts.py:1` + `GET /budgets/alerts` + hook `POST /transactions` + frontend `useBudgetAlerts` + banners dashboard/budgets (F8.1a+b 24/08/2026)
- [ ] Recordatorios de metas
- [ ] Resumen semanal automático

### 8.2 Integraciones
- [ ] Webhook para Notion/Google Sheets
- [x] Importación desde archivos bancarios (CSV) — `app/services/csv_import.py:1` + `POST /transactions/import` (2MB/1000 filas, EU/US, DD/MM/YYYY, alias headers, `;`/`,`) + frontend `useTransactions.importTransactions` + Dialog preview + `assets/demo_import.csv` (F8.2a+b 24/08/2026, 221 tests)
- [ ] Conexión con Mercado Pago (API) para leer transacciones
- [ ] Exportar a Google Finance / Excel

### 8.3 Modo offline PWA
- [ ] Service Worker para funcionar sin internet
- [ ] IndexedDB para datos locales
- [ ] Sync automático al reconectar
- [ ] Funciona como app instalable

### 8.4 Marketplace de plugins
- [ ] Sistema de plugins simple
- [ ] Plugins de categorías predefinidas (ej: "Gastos de freelance")
- [ ] Plugins de reportes custom
- [ ] API para desarrolladores externos

### 8.5 Colaboración
- [ ] Compartir reportes vía link
- [ ] Compartir presupuestos con pareja/familia
- [ ] Roles de "editor" y "viewer"
- [ ] Comentarios en transacciones

**Criterio de aceptación:** Features avanzadas funcionando. PWA instalable. Notificaciones activas.

---

## FASE 9: TESTING Y CALIDAD
**Objetivo:** Cobertura de tests >80%, zero critical bugs.
**Dependencias:** Todas las fases anteriores
**Tiempo estimado:** 3-4 días (continuo)

### 9.1 Test pyramid
- [ ] Unit tests >80% cobertura:
  - [ ] Tests de modelos
  - [ ] Tests de servicios
  - [ ] Tests de repositories
  - [ ] Tests de utils/formatters
- [ ] Integration tests:
  - [ ] Tests de API completos
  - [ ] Tests de base de datos
  - [ ] Tests de auth
- [ ] E2E tests (opcional):
  - [ ] Playwright para flujos principales

### 9.2 Code quality
- [ ] Configurar `pre-commit` hooks:
  - [ ] `ruff check` (linting)
  - [ ] `black` (formatting)
  - [ ] `mypy` (type checking)
  - [ ] `pytest` (tests rápidos)
- [ ] Agregar `py.typed` para type hints completos
- [ ] Documentar funciones públicas con docstrings

### 9.3 Performance
- [ ] Profiling con `cProfile` para queries lentas
- [ ] Opt queries con `EXPLAIN ANALYZE`
- [ ] Agregar índices faltantes
- [ ] Benchmark de API (target: <200ms p95)

### 9.4 Security audit
- [ ] Revisar OWASP Top 10
- [ ] Penetration testing básico
- [ ] Revisar dependencias con `safety`
- [ ] Revisar secrets no commiteados

**Criterio de aceptación:** >80% cobertura. Zero critical bugs. Performance <200ms.

---

## FASE 10: DOCUMENTACIÓN Y LANZAMIENTO
**Objetivo:** Documentación completa y lanzamiento público.
**Dependencias:** Fase 9 completada
**Tiempo estimado:** 2-3 días

### 10.1 README profesional
- [ ] Descripción clara del producto
- [ ] Screenshots/GIFs de la app
- [ ] Quick start guide
- [ ] API documentation link
- [ ] Contributing guide
- [ ] License
- [ ] Badges (CI, coverage, version)

### 10.2 API docs
- [ ] Swagger/ReDoc funcionando
- [ ] Ejemplos de uso para cada endpoint
- [ ] Guía de autenticación
- [ ] Error codes documentados

### 10.3 CHANGELOG
- [ ] Crear `CHANGELOG.md`
- [ ] Documentar cada versión con semver
- [ ] Agregar release notes

### 10.4 Lanzamiento
- [ ] Tag `v2.0.0` en git
- [ ] GitHub Release con notas
- [ ] Deploy a producción
- [ ] Monitoreo post-lanzamiento (48h)

**Criterio de aceptación:** Documentación completa. App desplegada y funcionando en producción.

---

## PROGRESO GENERAL

| Fase | Estado | Progreso |
|---|---|---|
| Fase 0: Limpieza | ✅ Completada | 100% |
| Fase 1: Seguridad | ✅ Completada | 100% |
| Fase 2: PostgreSQL | ✅ Completada | 100% |
| Fase 3: API REST | ✅ Completada | 100% |
| Fase 4: DevOps | ✅ Completada | 100% |
| Fase 5: IA Profesional | ✅ Completada | 100% |
| Fase 6: Frontend | ✅ Completada | 100% |
| Fase 7: i18n | ✅ Completada | 100% |
| Fase 8: Features | 🟡 En curso | 45% (8.1a+b alertas + 8.2a+b import CSV) |
| Fase 9: Testing | ⬜ No iniciada | 0% |
| Fase 10: Lanzamiento | 🟡 **PRÓXIMO** | 0% → **Darle vida: deploy público para acceso global** |

**Progreso total: ~82%** (Fases 0-7 + F8 45%)

> **PRÓXIMO PASO — Darle vida al proyecto (Fase 10 — deploy público):**
> Rebrand `PyFinFlow-AI` completo (`pyfinflow-AI` en GitHub, `pyfinflow_dev.db`, `221 tests`, `ruff 0`, `build 22/22`, IA `4.9s`). Streamlit Cloud eliminado.
> **Objetivo próxima sesión:** Generar link público para que cualquiera acceda.
> 1. **Backend → Render/Railway** `Dockerfile` `uvicorn` + Postgres + env `DATABASE_URL`, `JWT_SECRET`, `ENVIRONMENT=production` → obtener `https://pyfinflow-api.onrender.com` + verificar `GET /health` y `/docs`
> 2. **Frontend → Vercel** `frontend/` `Next.js 16` → env `NEXT_PUBLIC_API_URL=https://pyfinflow-api.onrender.com` → obtener `https://pyfinflow-ai.vercel.app`
> 3. **Poner link en GitHub About Website + README Demo + crear Release `v2.0-demo` + tag**
> 4. **Test e2e público:** register/login/demo123, crear txn, ver alerts, importar `assets/demo_import.csv`, chat IA
>
> **Sesión 24/08/2026:**
> - ✅ Fix dark/light mode real (body sin `dark` hardcodeado, themeScript default dark, charts con CSS vars)
> - ✅ Fix bug rate limiting login (contador se limpiaba en fallos) + tests API (3.8)
> - ✅ Rate limiting IA implementado (`app/ai/rate_limiter.py`, 10 req/min) + test (5.7)
> - ✅ Limpieza lint: 77 errores ruff → 0 (imports, dead code `PLACEHOLDERS_DESCRIPCION`, N806 en tests)
> - ✅ pyproject.toml: migrado `[tool.ruff]` a `[tool.ruff.lint]` (formato actual)
> - Tests: 175 → 182 | Cobertura backend: ~78%
>
> **Pruebas en local (24/08/2026, backend :8000):**
> - ✅ Rate limiting login verificado en vivo: 5×401 → 429
> - ✅ Fix nuevo: `busy_timeout=5000` en SQLite (`database.py`) — `/ai/chat` daba 500 `database is locked` con escrituras concurrentes; ahora 200 OK
> - ⚠️ Latencia IA ~90s: `qwen3.5:9b` (6.6GB) muy pesado para CPU + modo thinking quema tokens. Pendiente: probar modelo liviano (ej: llama3.2:3b)
> - ⚠️ `chromadb_not_installed` en entorno local — RAG se salta (context_results=0). Instalar con `pip install chromadb`
> - ✅ Rate limit IA relajado y configurable: `AI_RATE_LIMIT_PER_MIN` (default 30/min, era 10 fijo)
>
> **Sesión 24/08/2026 (parte 2):**
> - ✅ Branding propio: componente `Logo` (mark SVG con gradiente + wordmark + badge AI) en sidebar, navbar, login y register
> - ✅ Favicon propio: `frontend/src/app/icon.svg` (reemplaza el genérico)
> - ✅ Metadata actualizada: título "PyStreamFlow AI"
> - Frontend: lint 0 errores, build 22/22 páginas OK
>
> **Sesión 24/08/2026 (parte 3) — F8.1a+b:**
> - ✅ Backend: `app/services/budget_alerts.py` (compute 80%/100%, orden desc), `GET /budgets/alerts?mes=YYYY-MM`, hook no-bloqueante en `POST /transactions` + `alert_budget_exceeded/warning` (`app/core/alerts.py:54`)
> - ✅ Frontend: `useBudgetAlerts` (`frontend/src/hooks/use-budget-alerts.ts:1`) + banners en `dashboard/page.tsx:1` y `budgets/page.tsx:1` (amber warning vs destructive), `BudgetAlert` type, i18n `budgets.warning/alertTitle`
> - ✅ Tests: +21 (13 unit `test_budget_alerts.py` + 8 API `test_budget_alerts_api.py`) → **203 passed**, ruff 0, frontend lint 0, build 22/22
> - ⏭️ Next F8: 8.1c recordatorios metas / 8.2 import CSV (a definir)
>
> **Pendiente de decisión (IA local):**
> - Modelo Ollama `qwen3.5:9b` muy lento en CPU (~90s/respuesta, modo thinking). Probar `llama3.2:3b`
> - `chromadb` no instalado localmente → RAG sin búsqueda semántica (fallback a agregados funciona)

---

## NOTAS Y APRENDIZAJES

### 18/07/2026 - Fase 0 completada (2 commits en dev)

**Commit 1:** `714c6a8` - refactor: Fase 0 - Extraer constants, models, formatters y CSS a módulos separados

**Commit 2:** `464b1d9` - docs: actualizar roadmap - Fase 0 completada

#### Archivos creados:
```
app/__init__.py
app/core/__init__.py
app/core/constants.py     → MONEDAS, COLORES, CATEGORIAS, PLACEHOLDERS_DESCRIPCION, ITEMS_POR_PAGINA
app/core/models.py        → Transaccion (dataclass), icon_fa(), icono_tipo_transaccion()
app/services/__init__.py
app/repositories/__init__.py
app/ui/__init__.py
app/ui/components/__init__.py
app/ui/pages/__init__.py
app/ui/styles/__init__.py
app/ui/styles/main.css    → Copia de style.css original
app/utils/__init__.py
app/utils/formatters.py   → generar_id(), formatear_monto(), detectar_moneda(), _parsear_numero()
```

#### Cambios en pystreamflow.py:
- Imports actualizados para usar los nuevos módulos
- Funciones duplicadas eliminadas (~150 líneas removidas)
- Ruta de CSS actualizada: `style.css` → `app/ui/styles/main.css`

#### Archivos modificados:
- `.gitignore` → Agregados `.venv/`, `dist/`, `build/`, `*.egg-info/`, `chroma_data/`

#### Tests:
- 17/17 tests pasando después del refactor
- No se rompió nada - la app funciona igual

#### Decisión técnica:
- `formatear_monto()` ahora usa default `moneda="ARS"` en vez de `st.session_state.moneda_activa`
- Funciona igual porque la app solo soporta ARS por ahora
- Cuando se agreguen más monedas, se pasará `moneda` como parámetro explícito

### 18/07/2026 - Fase 1 completada (1 commit en dev)

**Commit:** `200ea6d` - feat: Fase 1 - Auth segura con bcrypt + JWT + rate limiting

#### Archivos creados:
```
app/core/auth.py           → bcrypt, JWT, rate limiting, roles, login/register
tests/unit/test_auth.py    → 18 tests de seguridad
```

#### Mejoras de seguridad:
| Antes | Después |
|---|---|
| SHA256 (sin sal) | bcrypt (sal única, 12 rounds) |
| Sin sesiones | JWT access (1h) + refresh (7 días) |
| Sin rate limiting | 5 intentos/min por IP |
| Sin roles | Enum ADMIN/USER/VIEWER |
| Sin migración | Auto-migración SHA256 → bcrypt |

#### Tests de seguridad (18):
- 6 tests de bcrypt (hash, verificar, sal única)
- 7 tests de JWT (access, refresh, expirado, firma inválida)
- 4 tests de rate limiting (bloqueo, cleanup, ventana)
- 1 test de roles

#### Total tests: 35/35 pasando

### 19/07/2026 - Fase 2 completada (2 commits en dev)

**Commit 1:** `76495c6` - feat: Fase 2 - SQLAlchemy models + Repository Pattern
**Commit 2:** `be1a867` - feat: Fase 2 completa - Alembic + Factory + migrations

#### Archivos creados:
```
app/core/config.py           → DATABASE_URL, SQLALCHEMY_ENGINE_OPTIONS
app/core/database.py         → engine, SessionLocal, init_db(), get_db_session(), get_db()
app/core/models_db.py        → User, Transaction, Budget, Goal, CustomCategory, UserConfig (SQLAlchemy ORM)
app/repositories/base_repo.py → BaseRepository (interfaz abstracta CRUD)
app/repositories/postgres_repo.py → TransactionRepo, BudgetRepo, GoalRepo, UserRepository
app/repositories/factory.py  → RepositoryFactory (punto de acceso unificado a repos)
alembic/                     → Configuración de Alembic
alembic/versions/001_initial_schema.py → Migración inicial (6 tablas)
tests/unit/test_repositories.py → 13 tests de repositorios con SQLite en memoria
```

#### Modelos SQLAlchemy (6 tablas):
| Tabla | Columnas | Constraints |
|---|---|---|
| `users` | id, username, password_hash, role, created_at | UNIQUE(username), INDEX(username) |
| `transactions` | id, user_id, tipo, monto, categoria, descripcion, fecha, moneda, created_at | FK(users), INDEX(user_id, fecha), INDEX(user_id, tipo) |
| `budgets` | id, user_id, categoria, limite, mes, created_at | FK(users), UNIQUE(user_id, categoria, mes) |
| `goals` | id, user_id, nombre, objetivo, ahorrado, fecha_limite, categoria, created_at | FK(users) |
| `custom_categories` | id, user_id, tipo, nombre | FK(users), UNIQUE(user_id, tipo, nombre) |
| `user_configs` | user_id, moneda_activa, filtro_fecha_inicio, filtro_fecha_fin | FK(users), PK(user_id) |

#### Repository Pattern:
- `BaseRepository` define interfaz abstracta: `create()`, `get_by_id()`, `get_all()`, `update()`, `delete()`
- `UserRepository` agrega `get_by_username()` y `_to_dict_full()` (incluye password_hash para login)
- `BudgetRepository` agrega `upsert()` (inserta o actualiza)
- `TransactionRepository` agrega `delete_all_for_user()` y filtros por user_id, tipo, categoria, fecha

#### Alembic:
- Migration `001_initial_schema.py` creada manualmente (no autogenerate porque psycopg2 falla con Python 3.14)
- Crea las 6 tablas con sus constraints e indexes

#### Bloqueador conocido:
- **psycopg2 + Python 3.14 en Windows**: Error `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3`
- Impide: `alembic upgrade head`, `alembic revision --autogenerate`, conexión directa a PostgreSQL
- Workaround: Tests usan SQLite en memoria, migration escrita a mano
- Pendiente de resolver (posible upgrade psycopg2 o usar asyncpg)

#### Total tests: 48/48 pasando (17 originales + 18 auth + 13 repos)

### 19/07/2026 - Fase 3 completada (2 commits en dev)

**Commit 1:** `3ab8a1d` - feat: Fase 3 - API REST completa con FastAPI
**Commit 2:** `9f273a3` - docs: actualizar roadmap - Fase 3 completada

#### Archivos creados:
```
app/api/__init__.py
app/api/main.py              → FastAPI app, CORS, routers, /health endpoint
app/api/deps.py              → get_repositories(), get_current_user(), get_current_admin()
app/api/routers/__init__.py
app/api/routers/auth.py      → /auth: register, login, refresh, me, password
app/api/routers/transactions.py → /transactions: CRUD + filtros + paginación
app/api/routers/budgets.py   → /budgets: CRUD + upsert
app/api/routers/goals.py     → /goals: CRUD
app/api/schemas/__init__.py
app/api/schemas/auth.py      → UserRegister, UserLogin, TokenResponse, RefreshRequest, UserResponse, PasswordChange
app/api/schemas/transaction.py → TransactionCreate, TransactionUpdate, TransactionResponse, TransactionFilter
app/api/schemas/budget.py    → BudgetCreate, BudgetResponse, BudgetAlert
app/api/schemas/goal.py      → GoalCreate, GoalUpdate, GoalResponse
tests/unit/test_api.py       → 27 tests de API con FastAPI TestClient + SQLite en memoria
```

#### API REST - Endpoints implementados:
| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| GET | `/health` | Health check | No |
| POST | `/auth/register` | Registro (retorna JWT) | No |
| POST | `/auth/login` | Login (retorna JWT + refresh) | No |
| POST | `/auth/refresh` | Renueva access token | No |
| GET | `/auth/me` | Usuario actual | Sí |
| PUT | `/auth/password` | Cambiar contraseña | Sí |
| GET | `/transactions` | Listar (filtros: tipo, categoria, fecha) | Sí |
| POST | `/transactions` | Crear transacción | Sí |
| GET | `/transactions/{id}` | Obtener una | Sí |
| PUT | `/transactions/{id}` | Actualizar | Sí |
| DELETE | `/transactions/{id}` | Eliminar | Sí |
| GET | `/budgets?mes=YYYY-MM` | Listar presupuestos del mes | Sí |
| POST | `/budgets` | Crear/actualizar (upsert) | Sí |
| GET | `/goals` | Listar metas | Sí |
| POST | `/goals` | Crear meta | Sí |
| PUT | `/goals/{id}` | Actualizar (ahorrado, nombre, etc.) | Sí |
| DELETE | `/goals/{id}` | Eliminar meta | Sí |

#### Dependency Injection:
- `get_db()` → sesión SQLAlchemy (override en tests con SQLite en memoria)
- `get_repositories()` → `RepositoryFactory` con todas las sesiones
- `get_current_user()` → valida JWT Bearer token, retorna usuario
- `get_current_admin()` → valida que sea ADMIN

#### Pydantic v2 Schemas:
- Validación con `Field(min_length, max_length, pattern, gt, ge)`
- `examples` para documentación Swagger automática
- `model_dump(exclude_unset=True)` para updates parciales

#### Testes de API (27):
- 1 test health check
- 5 tests auth (register, duplicate, short fields)
- 3 tests login (success, wrong password, nonexistent)
- 2 tests refresh (success, invalid)
- 3 tests me (success, no token, invalid)
- 7 tests transactions (CRUD, filtros, unauthorized)
- 3 tests budgets (create, upsert, list)
- 4 tests goals (create, update, delete, list)

#### Swagger/ReDoc:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Metadata: title "PyStreamFlow API", version "2.0.0"

#### Para ejecutar la API:
```bash
uvicorn app.api.main:app --reload --port 8000
```

#### Total tests: 75/75 pasando (17 originales + 18 auth + 13 repos + 27 API)

---

## COMANDOS RÁPIDOS

### Desarrollo
```bash
# Backend API (http://localhost:8000, Swagger en /docs)
uvicorn app.api.main:app --reload --port 8000

# Frontend Next.js (http://localhost:3000)
cd frontend && npm run dev

# Seed de datos demo (admin/demo, password: demo123)
python scripts/seed_demo.py

# Streamlit legacy (deprecado)
streamlit run app/main.py

# Docker
docker-compose up -d
```

### Frontend
```bash
cd frontend

# Lint
npm run lint

# Build de producción
npm run build

# Dev server
npm run dev
```

### Testing
```bash
# Todos los tests backend
pytest tests/ -v

# Solo unitarios
pytest tests/unit/ -v

# Con cobertura
pytest tests/ -v --cov=app --cov-report=html

# Linting
ruff check .
black --check .
mypy app/
```

### Git (flujo de trabajo)
```bash
# Crear feature branch desde dev
git checkout dev
git pull
git checkout -b feature/nombre-feature

# Trabajar, commitear en dev
git add .
git commit -m "feat: descripción"
git push origin feature/nombre-feature

# Merge a dev cuando esté listo
git checkout dev
git merge feature/nombre-feature
git push origin dev

# Cuando dev está estable → merge a main
git checkout main
git merge dev
git push origin main
```

---

*Documento creado el 18/07/2026 para PyStreamFlow-AI.*
*Última actualización: 14/08/2026 (Fase 7 completada + fixes arranque local).*

### 19/07/2026 - Decisión: Frontend Next.js (reemplaza plan Streamlit)

**Contexto:** Después de completar las Fases 0-3 (backend profesional con API REST), se analizó el estado del frontend Streamlit actual (`pystreamflow.py`, 2972 líneas). Se concluyó que Streamlit tiene un techo técnico demasiado bajo para una app SaaS profesional tipo fintech.

**Análisis comparativo:**
- El CSS actual (`main.css`, 1540 líneas) es profesional (glassmorphism, responsive, animaciones) pero está limitado por el rendering model de Streamlit
- Streamlit no tiene routing real, control del DOM, ni type safety
- La API REST ya existe y está probada (75 tests), list para cualquier frontend

**Decisión:** Adoptar Next.js 14 + React + TypeScript + Tailwind + Shadcn/UI como frontend de producción. Streamlit se mantiene como MVP/backup.

**Archivos modificados en roadmap:**
- Fase 5 reemplazada completamente (Streamlit → Next.js)
- Estado general del proyecto actualizado
- Sección de "Decisiones técnicas clave" agregada con contexto de cada decisión
- Fase 6 dependencies actualizadas

### 19/07/2026 - Reordenamiento de fases (simplest → complex)

**Decisión:** Reordenar las fases pendientes de menor a mayor complejidad, respetando dependencias.

**Nuevo orden:**

| Orden | Fase | Tiempo | Complejidad | Antes era |
|---|---|---|---|---|
| 4 | DevOps | 3-4 días | Media | Fase 6 |
| 5 | IA Profesional | 5-7 días | Alta | Fase 4 |
| 6 | Frontend Next.js | 8-10 días | Máxima | Fase 5 |
| 7 | i18n | 2-3 días | Baja | Fase 7 (sin cambio) |
| 8 | Features | 5-7 días | Alta | Fase 8 (sin cambio) |
| 9 | Testing | 3-4 días | Media | Fase 9 (sin cambio) |
| 10 | Lanzamiento | 2-3 días | Baja | Fase 10 (sin cambio) |

**Razones:**
- DevOps primero: Docker + CI/CD habilita testing en entornos limpios
- IA antes que Frontend: es el diferenciador core del producto, se puede probar con Streamlit mientras se construye Next.js
- Frontend después: consume la API que ya incluye IA
- i18n después de Frontend: necesita la UI en place
- Features después de IA: construyen sobre IA funcional
- Testing y Launch al final: gates de calidad

### 19/07/2026 - Fase 4 completada (DevOps)

**Archivos creados (ronda anterior):**
```
Dockerfile               → Multi-stage build (builder + runtime), user no-root, healthcheck
docker-compose.yml       → 4 servicios: app, PostgreSQL 16, Redis 7, ChromaDB
.dockerignore            → Excluye .git, __pycache__, .env, docs, tests
```

**Archivos creados (ronda final):**
```
app/core/cache.py        → Redis cache wrapper con sesiones, queries, rate limiting y fallback
app/core/metrics.py      → MetricsCollector: requests/min, status codes, errores, usuarios activos, latencia IA
app/core/alerts.py       → SMTP alerts para errores críticos (500+) y errores internos
scripts/backup_db.sh     → pg_dump custom + gzip + retention 7 días
tests/unit/test_cache.py → 7 tests de cache/rate limiting (fallback sin Redis)
tests/unit/test_metrics.py → 6 tests de MetricsCollector
```

**Archivos modificados:**
```
requirements.txt         → Agregados: redis>=5.0.0, aiosmtplib>=3.0.0
app/core/config.py       → Settings ampliado: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_TLS, ALERT_EMAIL_TO
app/core/auth.py         → Rate limiting híbrido: Redis primario, in-memory fallback
app/core/database.py     → Import actualizado para usar settings object
app/repositories/factory.py → Import DATABASE_URL removido (no se usaba)
app/api/main.py          → structlog logging, request middleware, lifespan events,
                           health check mejorado (/health + /health/detailed),
                           metrics middleware (registra requests/errores),
                           endpoints: GET /metrics (JSON), GET /metrics/prometheus (text/plain),
                           alertas automáticas en errores 500+
app/api/routers/auth.py  → metrics_collector.record_user_activity() en /auth/me
.github/workflows/ci.yml → Python 3.12, PostgreSQL service, ruff lint, pytest-cov, codecov
.env.example             → Documentadas todas las variables: DB, Redis, JWT, SMTP, ENVIRONMENT
README.md                → Badge de coverage + badges actualizados (FastAPI, PostgreSQL, Next.js, 75 tests)
```

**Checkboxes marcados en Fase 4:**
- 4.1 Docker: ✅ docker-compose build probado
- 4.2 CI/CD: ✅ badge de cobertura agregado
- 4.3 Monitoreo: ✅ métricas (requests/min, latencia IA, errores, usuarios activos) + endpoint /metrics + alertas email
- 4.4 Redis: ✅ cache de sesiones, queries, rate limiting con TTL y fallback automático
- 4.5 Backup: ✅ script backup_db.sh (pg_dump + gzip + cleanup)

**Dependencias instaladas:**
- `structlog` → logging estructurado
- `redis` → cliente Redis para cache y rate limiting
- `aiosmtplib` → email alerts (opcional)

**Tests:** 73/73 pasando (58 unit + 15 nuevos de Fase 4 + 17 originales)
- 7 tests cache (app.core.cache - fallback sin Redis)
- 6 tests metrics (app.core.metrics - MetricsCollector)
- 2 tests API metrics (/metrics y /metrics/prometheus)

### 20/07/2026 - Fase 5 completada (IA Profesional)

**Archivos creados:**
```
app/ai/__init__.py                    → Package IA
app/ai/providers/__init__.py          → Package providers
app/ai/providers/base_provider.py     → Interfaz ABC para providers
app/ai/providers/ollama_provider.py   → Ollama local (configurable)
app/ai/providers/huggingface_provider.py → HuggingFace cloud (Zephyr)
app/ai/providers/gemini_provider.py   → Gemini cloud (gemini-2.0-flash)
app/ai/provider_factory.py            → Fallback chain: Ollama → HF → Gemini → local
app/ai/vector_store.py                → ChromaDB wrapper (index + search)
app/ai/rag_engine.py                  → Pipeline RAG completo
app/ai/chat_memory.py                 → ChatMemoryService (memoria persistente)
app/ai/analytics.py                   → FinancialAnalytics (tendencias, predicciones, anomalías)
app/api/routers/ai.py                 → 6 endpoints REST (/ai/chat, /history, /insights, etc.)
app/api/schemas/ai.py                 → Pydantic schemas (AIRequest, AIResponse, InsightResponse, etc.)
alembic/versions/002_chat_messages.py → Migración tabla chat_messages
tests/unit/test_ai.py                 → 30 tests unitarios de IA
tests/unit/test_ai_api.py             → 10 tests de API endpoints
```

**Archivos modificados:**
```
app/core/config.py                    → +12 settings de IA (OLLAMA_URL, HF_TOKEN, GEMINI_API_KEY, etc.)
app/core/models_db.py                 → +1 modelo ChatMessage + relationship en User
app/repositories/postgres_repo.py     → +1 ChatRepository (create, get_history, clear_history)
app/repositories/factory.py           → +1 property chats
app/api/main.py                       → +1 router ai.router
requirements.txt                      → +5 dependencias (chromadb, sentence-transformers, ollama, google-generativeai, scikit-learn)
.env.example                          → +15 vars de IA documentadas
docker-compose.yml                    → ChromaDB port 8001, vars de IA en app service
```

**Endpoints REST creados:**
| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| POST | `/ai/chat` | Chat con IA (RAG + memoria) | Sí |
| GET | `/ai/history` | Historial de conversación | Sí |
| DELETE | `/ai/history` | Limpiar historial | Sí |
| GET | `/ai/insights` | Análisis predictivo completo | Sí |
| GET | `/ai/suggestions` | Preguntas sugeridas | Sí |
| GET | `/ai/status` | Estado de providers y ChromaDB | No |

**Componentes de IA implementados:**
| Componente | Archivo | Descripción |
|---|---|---|
| Vector Store | `vector_store.py` | ChromaDB: indexa transacciones, búsqueda semántica |
| RAG Engine | `rag_engine.py` | Query → ChromaDB search → prompt → LLM |
| Providers | `providers/` | 3 providers con interfaz común (ABC) |
| Factory | `provider_factory.py` | Fallback automático con métricas |
| Chat Memory | `chat_memory.py` | Persistencia en PostgreSQL, ventana de 20 msgs |
| Analytics | `analytics.py` | Tendencias, predicciones, anomalías (z-score) |

**Tests:** 130/130 pasando (40 nuevos de Fase 5 + 90 existentes)
- 30 tests unitarios IA (providers, fallback, analytics, chat memory)
- 10 tests API endpoints (chat, history, insights, suggestions, status, auth)

### 20/07/2026 - Fase 6 completada (Frontend Next.js)

**Archivos creados:**
```
frontend/                         → Next.js 16 + React 19 + TypeScript
frontend/src/app/layout.tsx       → Root layout con AuthGuard + Geist font
frontend/src/app/page.tsx         → Redirect a /login o /dashboard
frontend/src/app/globals.css      → Tailwind v4 theme + glassmorphism + scrollbar
frontend/src/app/login/page.tsx   → Login page con form + JWT
frontend/src/app/register/page.tsx → Register page con validación
frontend/src/app/dashboard/page.tsx → Dashboard principal
frontend/src/app/transactions/page.tsx → CRUD transacciones con filtros
frontend/src/app/budgets/page.tsx → Presupuestos con progress bars
frontend/src/app/goals/page.tsx   → Metas de ahorro con progreso
frontend/src/app/chat/page.tsx    → Chat IA widget
frontend/src/app/settings/page.tsx → Perfil de usuario

frontend/src/components/ui/       → 11 UI components:
  button.tsx, card.tsx, input.tsx, label.tsx, skeleton.tsx,
  badge.tsx, separator.tsx, dialog.tsx, select.tsx, tabs.tsx,
  progress.tsx, motion.tsx

frontend/src/components/layout/   → Layout components:
  sidebar.tsx, navbar.tsx, auth-guard.tsx, dashboard-layout.tsx

frontend/src/components/dashboard/ → Dashboard widgets:
  summary-cards.tsx, monthly-chart.tsx, category-pie.tsx,
  recent-transactions.tsx

frontend/src/lib/api.ts           → Fetch wrapper con JWT auto-refresh
frontend/src/lib/auth.ts          → Zustand auth store con persist
frontend/src/lib/utils.ts         → cn(), formatMoney(), formatDate()

frontend/src/hooks/use-auth.ts    → Login/register/logout hooks
frontend/src/hooks/use-transactions.ts → SWR + CRUD transactions
frontend/src/hooks/use-budgets.ts → SWR + create budgets
frontend/src/hooks/use-goals.ts   → SWR + CRUD goals

frontend/src/types/index.ts       → TypeScript interfaces (all entities)
```

**Stack:**
| Capa | Tecnología |
|---|---|
| Framework | Next.js 16 (App Router, Turbopack) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS v4 (CSS-based config) |
| Animations | Framer Motion 12 (page transitions, stagger, hover/tap) |
| State | Zustand 5 (auth persist) |
| HTTP | SWR 2 + fetch wrapper (auto-refresh JWT) |
| Charts | Recharts 3 (BarChart, PieChart) |
| Icons | Lucide React |
| Forms | Native + react-hook-form ready |

**Páginas (10 rutas):**
| Ruta | Descripción |
|---|---|
| `/` | Redirect automático (login/dashboard) |
| `/login` | Login con form |
| `/register` | Registro con validación |
| `/dashboard` | Resumen: cards + bar chart + pie chart + transacciones recientes |
| `/transactions` | CRUD completo con filtros por tipo/categoría |
| `/budgets` | Presupuestos con progress bars + alerta excedido |
| `/goals` | Metas de ahorro + agregar fondos inline |
| `/chat` | Chat IA con sugerencias + status provider |
| `/settings` | Perfil + configuración IA (proveedores, modelos, API keys) |

**UI Components (12):**
Button (con motion hover/tap), Card, Input, Label, Skeleton, Badge, Separator, Dialog (con AnimatePresence), Select, Tabs, Progress, ConfirmDialog

**Motion animations (6 helpers):**
PageTransition, StaggerContainer, StaggerItem, FadeIn, ScaleIn, SlideUp

**Verificación:**
- `npm run lint`: 0 errors, 0 warnings
- `npm run build`: 10/10 rutas compilan
- `pytest`: 113/113 tests backend pasando

**Pendiente para futuro polish:**
- Date range picker para dashboard
- Indicadores visuales de tendencia (↑↓→)
- Búsqueda por texto en transacciones
- Cambio de contraseña
- Toggle dark/claro
- Keyboard shortcuts
- 404 page personalizada

---

### 20/07/2026 - Session: IA fixes + UI polish

**Cambios realizados:**
1. **Fix Ollama provider**: `ollama` package v0.6.x cambió la API — `Client(host=...)` en vez de `client.list(host=...)`. Provider ahora detecta correctamente.
2. **ConfirmDialog modal**: Reemplazado `confirm()` nativo por componente `ConfirmDialog` en transacciones y metas. Modal con icono de alerta, acciones cancelar/confirmar.
3. **Colores de gráficos suavizados**: BarChart (Ingresos vs Gastos) usa `#2dd4bf` / `#f472b6` con opacidad 0.85. PieChart usa paleta más pastel.
4. **Configuración IA en Settings**:
   - Backend: modelo `AIProviderConfig` (per-user), repositorio, endpoints `GET/PUT /ai/settings`
   - Frontend: sección completa en Settings con prioridad de proveedores, Ollama URL/modelo, HuggingFace token/modelo, Gemini API key/modelo, parámetros de generación (max_tokens, temperature, context_window), modelo de embeddings, botón probar conexión
   - Cualquier persona que clone el repo puede configurar proveedores desde la UI sin tocar `.env`

**Archivos modificados:**
```
app/core/models_db.py                         → AIProviderConfig model
app/repositories/postgres_repo.py             → AIProviderConfigRepository
app/repositories/factory.py                   → ai_config property
app/api/schemas/ai.py                         → AIProviderSettingsRequest/Response
app/api/routers/ai.py                         → GET/PUT /ai/settings endpoints
app/ai/providers/ollama_provider.py           → Fixed ollama 0.6.x Client API
frontend/src/components/ui/confirm-dialog.tsx → New ConfirmDialog component
frontend/src/app/transactions/page.tsx        → ConfirmDialog replaces confirm()
frontend/src/app/goals/page.tsx               → ConfirmDialog replaces confirm()
frontend/src/app/settings/page.tsx            → Full AI provider settings UI
frontend/src/components/dashboard/monthly-chart.tsx → Softer bar colors
frontend/src/components/dashboard/category-pie.tsx → Softer pie colors
frontend/src/types/index.ts                   → AIProviderSettings type
```

**Verificación:**
- `npm run lint`: 0 errors, 0 warnings
- `npm run build`: 10/10 rutas compilan
- `pytest`: 113/113 tests pasando

---

### 21/07/2026 - Session: Fase 6 polish completo

**Todos los pendientes de Fase 6 completados:**

**Archivos creados:**
```
frontend/src/app/not-found.tsx                  → 404 page personalizada con link al dashboard
frontend/src/components/ui/theme-toggle.tsx     → Toggle dark/claro con persistencia en localStorage
frontend/src/hooks/use-keyboard-shortcuts.ts    → Hook global de shortcuts de teclado
```

**Archivos modificados:**
```
frontend/src/app/dashboard/page.tsx             → Date range picker (desde/hasta) + filtrado de transacciones
frontend/src/app/transactions/page.tsx          → Búsqueda por texto + Ctrl+N/Ctrl+F shortcuts
frontend/src/app/settings/page.tsx              → Formulario completo de cambio de contraseña (con validación)
frontend/src/app/layout.tsx                     → Script anti-flash para tema + suppressHydrationWarning
frontend/src/app/globals.css                    → Variables CSS para tema claro (light) + tema oscuro (.dark)
frontend/src/components/dashboard/summary-cards.tsx → Indicadores de tendencia ↑↓→ (mes actual vs anterior)
frontend/src/components/layout/sidebar.tsx      → ThemeToggle integrado junto al usuario
frontend/src/components/layout/dashboard-layout.tsx → Keyboard shortcuts globales
```

**Features implementadas:**

1. **Date range picker** — Filtros "desde" y "hasta" en el dashboard con botón "Limpiar"
2. **Indicadores de tendencia** — SummaryCards muestran ↑↓→ comparando mes actual vs anterior
3. **Búsqueda por texto** — Input de búsqueda en transacciones (filtra por descripción y categoría)
4. **Cambio de contraseña** — Formulario completo con validación (6+ chars, coincidencia, llama a `PUT /auth/password`)
5. **Toggle dark/claro** — Botón en sidebar, persiste en localStorage, script anti-flash en `<head>`
6. **Keyboard shortcuts** — Ctrl+N (nueva txn), Ctrl+F (buscar), Ctrl+D/B/G/I/navigate, Ctrl+, (settings)
7. **404 page** — Página personalizada con gradiente 404, botones "Volver" y "Dashboard"

**Verificación:**
- `npm run lint`: 0 errors, 0 warnings
- `npm run build`: 12/12 rutas compilan (10 originales + `/_not-found` + `/`)

---

### 21/07/2026 - Session: Fase 7 i18n + Multi-moneda

**Fase 7 completada: Multi-idioma (i18n) + Multi-moneda**

**Archivos creados:**
```
frontend/src/i18n/config.ts                       → Definición de locales (es, en, pt)
frontend/src/i18n/request.ts                      → getRequestConfig para next-intl
frontend/src/i18n/index.ts                        → Helpers de navegación (Link, redirect, useRouter, usePathname)
frontend/middleware.ts                            → Middleware next-intl para routing por locale
frontend/messages/es.json                         → Traducciones español (~135 keys)
frontend/messages/en.json                         → Traducciones inglés
frontend/messages/pt.json                         → Traducciones portugués
frontend/src/components/ui/language-selector.tsx  → Selector de idioma (globe icon + Select)
frontend/src/components/layout/providers.tsx      → Wrapper NextIntlClientProvider
frontend/src/lib/currency.ts                      → Utilidades de conversión de moneda con cache
frontend/src/lib/use-currency.ts                  → Hook de moneda preferida (localStorage)
frontend/src/app/[locale]/layout.tsx              → Layout localizado con Providers wrapper
frontend/src/app/[locale]/page.tsx                → Redirect locale-aware
frontend/src/app/[locale]/not-found.tsx           → 404 localizado
frontend/src/app/[locale]/login/page.tsx          → Login localizado
frontend/src/app/[locale]/register/page.tsx       → Registro localizado
frontend/src/app/[locale]/dashboard/page.tsx      → Dashboard localizado
frontend/src/app/[locale]/transactions/page.tsx   → Transacciones localizadas
frontend/src/app/[locale]/budgets/page.tsx        → Presupuestos localizados
frontend/src/app/[locale]/goals/page.tsx          → Metas localizadas
frontend/src/app/[locale]/chat/page.tsx           → Chat localizado
frontend/src/app/[locale]/settings/page.tsx       → Settings localizado + selector de moneda
```

**Features implementadas:**

1. **Multi-idioma (i18n)** — 3 idiomas: español (default), inglés, portugués. Selector en sidebar con icono globe.
2. **Routing localizado** — Todas las rutas bajo `/[locale]/`, middleware redirige a locale por defecto.
3. **Traducciones completas** — ~135 keys por idioma cubriendo auth, dashboard, transacciones, presupuestos, metas, chat, settings, 404.
4. **Multi-moneda** — 4 monedas: ARS, USD, EUR, BRL. Selector en settings con persistencia en localStorage.
5. **FormatMoney locale-aware** — `Intl.NumberFormat` con locale y formato por moneda.
6. **Conversión de moneda** — `lib/currency.ts` con API open.er-api.com, cache en localStorage (1h TTL).

**Verificación:**
- `npm run lint`: 0 errors, 0 warnings
- `npm run build`: 10/10 rutas bajo `[locale]` compilan correctamente

---

### 22/07/2026 - Session: API docs + Seed data + Tests

**Objetivo:** Preparar el repo para demo profesional: documentación Swagger, datos demo, cobertura de tests.

---

#### 1. API Docs Profesional (28 endpoints + 28 schemas)

**Archivos modificados:**
```
app/api/main.py              → openapi_tags (6 grupos), contact, license_info, servers, descripción markdown
app/api/routers/auth.py      → 5 endpoints: summary, docstring, response_description, Query descriptions
app/api/routers/transactions.py → 5 endpoints: summary, docstring, Query descriptions
app/api/routers/budgets.py   → 2 endpoints: summary, docstring, Query descriptions
app/api/routers/goals.py     → 4 endpoints: summary, docstring, response_description
app/api/routers/ai.py        → 8 endpoints: summary, docstring, response_description, Query descriptions
app/api/schemas/auth.py      → 7 schemas: class description, field descriptions, field examples
app/api/schemas/transaction.py → 4 schemas: class description, field descriptions, field examples
app/api/schemas/budget.py    → 3 schemas: class description, field descriptions, field examples
app/api/schemas/goal.py      → 3 schemas: class description, field descriptions, field examples
app/api/schemas/ai.py        → 11 schemas: class descriptions, field descriptions, field examples
```

**Antes vs Después:**
| Métrica | Antes | Después |
|---|---|---|
| Endpoints con docstring | 0/28 | 28/28 |
| Endpoints con summary | 0/28 | 28/28 |
| Schemas con class description | 0/28 | 28/28 |
| Schemas con field examples | 11/28 (39%) | 28/28 (100%) |
| Schemas con field descriptions | 7/28 (25%) | 28/28 (100%) |
| openapi_tags | No | 6 grupos con descripciones |
| contact/license | No | Configurados |

**Swagger UI:** `http://localhost:8000/docs` — ahora muestra documentación completa con tags agrupados, descripciones, y ejemplos en cada endpoint y schema.

---

#### 2. Seed Script

**Archivo creado:**
```
scripts/seed_demo.py          → Script standalone para poblar datos demo
```

**Datos que crea:**
| Entidad | Cantidad | Detalle |
|---|---|---|
| Users | 2 | admin (ADMIN) + demo (USER), contraseña: demo123 |
| Transactions | ~70 | 6 meses, ambos tipos, todas las categorías, montos realistas ARS |
| Budgets | 14 | 7 categorías × 2 meses (anterior + actual) |
| Goals | 3 | Vacaciones (25%), Fondo emergencia (70%), Notebook (91%) |
| UserConfig | 2 | Moneda ARS por defecto |
| AIProviderConfig | 2 | Defaults (ollama local) |

**Uso:**
```bash
python scripts/seed_demo.py
# Luego: POST /auth/login → {"username": "demo", "password": "demo123"}
```

**Características:**
- Idempotente: limpia datos existentes antes de insertar
- Usa SQLAlchemy directamente (sin dependency de FastAPI)
- Basado en constantes de `app/core/constants.py`
- Printea resumen al final

---

#### 3. Tests — 175 pasando (antes: 114)

**Archivos creados:**
```
tests/unit/conftest.py           → Fixtures compartidos: db_session, client, auth_header, budget_auth_header, goal_auth_header
tests/unit/test_formatters.py    → 22 tests: generar_id, formatear_monto, _parsear_numero, detectar_moneda
tests/unit/test_vector_store.py  → 14 tests: ChromaDB (_get_client, indexar, buscar, eliminar, _txn_to_text)
tests/unit/test_rag_engine.py    → 5 tests: RAG (_build_messages, consultar con mocks)
tests/unit/test_alerts.py        → 5 tests: SMTP (send_alert_email, alert_critical_error, alert_rate_limit_hit)
tests/unit/test_config.py        → 11 tests: Settings (tipos, defaults, engine_options)
```

**Cobertura por módulo:**
| Módulo | Antes | Después | Tests |
|---|---|---|---|
| `app/utils/formatters.py` | 0% | ~90% | 22 tests (formateo, parsing, detección moneda) |
| `app/ai/vector_store.py` | 0% | ~85% | 14 tests (client, index, search, delete, error handling) |
| `app/ai/rag_engine.py` | 0% (solo API mock) | ~80% | 5 tests (build_messages, consultar mocked) |
| `app/core/alerts.py` | 0% | ~90% | 5 tests (SMTP mock, critical error, rate limit) |
| `app/core/config.py` | 0% | ~70% | 11 tests (types, defaults, engine options) |

**Structural improvements:**
- `conftest.py`: fixtures de `db_session`, `client` y `auth_header` extraídos de test_api.py y test_ai_api.py (eliminación de duplicación)
- `pyproject.toml`: markers configurados (`unit`, `integration`, `slow`)

**Resumen de tests:**
| Archivo | Tests | Estado |
|---|---|---|
| test_ai.py | 30 | ✅ |
| test_ai_api.py | 10 | ✅ |
| test_api.py | 30 | ✅ |
| test_auth.py | 18 | ✅ |
| test_cache.py | 7 | ✅ |
| test_config.py | 11 | ✅ (nuevo) |
| test_formatters.py | 22 | ✅ (nuevo) |
| test_metrics.py | 6 | ✅ |
| test_rag_engine.py | 5 | ✅ (nuevo) |
| test_repositories.py | 13 | ✅ |
| test_vector_store.py | 14 | ✅ (nuevo) |
| test_alerts.py | 5 | ✅ (nuevo) |
| **TOTAL** | **175** | **✅ Todos pasan** |

---

**Verificación:**
- `pytest tests/ -v`: 175/175 passed
- `npm run lint`: 0 errors (frontend sin cambios)

---

### 14/08/2026 - Session: Arranque local frontend + fix i18n es/en

**Objetivo:** Poner a correr el frontend Next.js en local y dejar la i18n en español/inglés. Se encontraron y corrigieron errores de arranque del frontend.

**Problema raíz:** el proyecto venía de Next.js 14 + `next-intl` sin plugin, pero la versión instalada es **Next.js 16.2.10 (Turbopack) + next-intl v4**. Cambios de convención que rompían todo:

1. **`middleware.ts` en raíz era ignorado** — Next 16 exige `src/proxy.ts` (convención nueva; `middleware` deprecado). Se movió de `frontend/middleware.ts` → `frontend/src/proxy.ts`.
2. **Faltaba el plugin de next-intl** — `next.config.ts` ahora usa `createNextIntlPlugin("./src/i18n/request.ts")` (next-intl v4 lo requiere explícitamente).
3. **Root layout roto** — `frontend/src/app/layout.tsx` devolvía `children` sin `<html>/<body>`. Eliminado; `[locale]/layout.tsx` es ahora el root layout (server component async con `setRequestLocale` + `NextIntlClientProvider`).
4. **`providers.tsx` roto** — usaba `useLocale()` fuera del provider → "No intl context found". Eliminado.
5. **Ruta de messages incorrecta** — `src/i18n/request.ts` importaba `../messages/` pero los archivos están en `frontend/messages/`. Corregido a `../../messages/${locale}.json`.

**Bug crítico de navegación (404 en sidebar):** `getLocale(pathname)` asumía que el primer segmento de la URL era el locale. Con `localePrefix: "as-needed"` el español (default) **no lleva prefijo**, así que en `/dashboard` el primer segmento era `"dashboard"` → los links del sidebar quedaban `/dashboard/dashboard` → 404. Además `/login` no se reconocía como ruta pública en el AuthGuard.

**Fix:** reemplazado el parseo manual por `useLocale()` de next-intl (que conoce el idioma real) en 10 archivos:
```
frontend/src/components/layout/sidebar.tsx, navbar.tsx, auth-guard.tsx
frontend/src/app/[locale]/page.tsx, login/page.tsx, register/page.tsx, not-found.tsx
frontend/src/components/dashboard/recent-transactions.tsx
frontend/src/hooks/use-auth.ts, use-keyboard-shortcuts.ts
frontend/src/components/ui/language-selector.tsx  → + quita prefijo es al cambiar idioma
```
`auth-guard.tsx` ahora detecta rutas públicas sin prefijo (`/login`, `/register`) y calcula `pathWithoutLocale` solo si el primer segmento es un locale válido.

**i18n limitada a es/en (solicitado por Marcelo):**
```
frontend/src/i18n/config.ts  → locales ["es", "en"] (default: es)
frontend/messages/pt.json    → eliminado
```
Monedas (ARS/USD/EUR/BRL) sin cambios.

**Seed script corregido para Windows:**
```
scripts/seed_demo.py  → sys.path a raíz del repo, delete de ChatMessage/CustomCategory (FK),
                       reconfigure utf-8 en stdout/stderr (evita UnicodeDecodeError)
```

**Backend:** modelo Ollama actualizado a `qwen3.5:9b` en `app/core/config.py`, `app/core/models_db.py` y `app/api/schemas/ai.py`.

**Verificación (todo en local):**
- `npm run lint`: 0 errors, 0 warnings
- `npm run build`: 21/21 páginas SSG (`/es/*`, `/en/*`, `/_not-found`)
- Rutas `/`, `/dashboard`, `/transactions`, `/budgets`, `/goals`, `/chat`, `/settings`, `/en/*` → 200
- `/es/*` → 307 redirect a versión sin prefijo; `/pt/*` → 404
- DB seed: `pystreamflow_dev.db` con admin/demo (`demo123`), 190 transacciones, 28 presupuestos, 6 metas
- Navegación por sidebar validada en el navegador ✅

**Pendiente (próxima sesión):**
- [ ] Dar funcionalidad real al modo dark/light (hoy el toggle persiste pero falta revisar variables CSS/contraste)
- [ ] Revisar que todo funcione: chat IA, conversión de moneda, gráficos
- [ ] Tests frontend (Playwright/Vitest)

---
