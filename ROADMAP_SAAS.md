# PyStreamFlow-AI → SaaS Profesional
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
| **App** | Streamlit monolítico (~2800 líneas) |
| **DB** | SQLite (local) + Supabase (cloud) |
| **IA** | HuggingFace Zephyr-7b + fallback reglas |
| **Auth** | SHA256 sin sal (básico) |
| **Tests** | 12 unitarios (pytest) |
| **CI/CD** | GitHub Actions configurado |
| **Deploy** | Streamlit Cloud |
| **Branch** | `master` (producción), `dev` (desarrollo) |

---

## FASE 0: LIMPIEZA Y PREPARACIÓN
**Objetivo:** Dejar el proyecto listo para escalar. Sin esto, todo lo demás se complica.
**Dependencias:** Ninguna
**Tiempo estimado:** 1-2 días

### 0.1 Estructura de proyecto
- [ ] Crear estructura de directorios:
  ```
  pystreamflow-AI/
  ├── app/
  │   ├── __init__.py
  │   ├── core/
  │   │   ├── __init__.py
  │   │   ├── config.py          # Constantes, settings
  │   │   ├── models.py          # Dataclasses, schemas
  │   │   └── constants.py       # MONEDAS, COLORES, CATEGORIAS
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── transaction_service.py
  │   │   ├── budget_service.py
  │   │   ├── goal_service.py
  │   │   └── ai_service.py
  │   ├── repositories/
  │   │   ├── __init__.py
  │   │   ├── sqlite_repo.py
  │   │   └── supabase_repo.py
  │   ├── ui/
  │   │   ├── __init__.py
  │   │   ├── components/
  │   │   │   ├── chat.py
  │   │   │   ├── sidebar.py
  │   │   │   ├── navigation.py
  │   │   │   └── cards.py
  │   │   ├── pages/
  │   │   │   ├── dashboard.py
  │   │   │   ├── new_transaction.py
  │   │   │   ├── history.py
  │   │   │   ├── charts.py
  │   │   │   ├── budgets.py
  │   │   │   ├── goals.py
  │   │   │   └── migrate.py
  │   │   └── styles/
  │   │       └── main.css
  │   └── utils/
  │       ├── __init__.py
  │       ├── formatters.py
  │       ├── validators.py
  │       └── pdf_generator.py
  ├── tests/
  │   ├── __init__.py
  │   ├── unit/
  │   │   ├── test_formatters.py
  │   │   ├── test_models.py
  │   │   └── test_services.py
  │   └── integration/
  │       └── test_database.py
  ├── config/
  │   ├── .env.example
  │   └── streamlit/
  │       └── config.toml
  ├── scripts/
  │   ├── run.sh
  │   └── run.bat
  ├── assets/
  ├── static/
  ├── .github/
  │   └── workflows/
  ├── ROADMAP_SAAS.md            # Este archivo
  ├── pyproject.toml
  ├── requirements.txt
  ├── requirements-dev.txt
  ├── Dockerfile
  ├── docker-compose.yml
  └── README.md
  ```

### 0.2 Separar el monolito
- [ ] Extraer `constants.py` (MONEDAS, COLORES, CATEGORIAS, PLACEHOLDERS)
- [ ] Extraer `models.py` (dataclass Transaccion)
- [ ] Extraer `formatters.py` (formatear_monto, detectar_moneda, _parsear_numero)
- [ ] Extraer `database.py` → `repositories/sqlite_repo.py`
- [ ] Extraer `auth.py` → `repositories/supabase_repo.py`
- [ ] Extraer servicios de lógica de negocio a `services/`
- [ ] Extraer CSS a `styles/main.css`
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
- [ ] Crear rama `dev` desde `master` si no existe
- [ ] Configurar `.gitignore` actualizado (agregar `__pycache__/`, `.env`, `*.db`, `dist/`, `build/`)
- [ ] Commitear toda la reestructuración en `dev`
- [ ] Verificar que la app funciona igual que antes
- [ ] Push a `dev`

**Criterio de aceptación:** La app funciona idéntica al antes, pero con código modular. Tests pasan.

---

## FASE 1: SEGURIDAD BÁSICA
**Objetivo:** Auth segura y base sólida para multi-usuario.
**Dependencias:** Fase 0 completada
**Tiempo estimado:** 2-3 días

### 1.1 Auth mejorada
- [ ] Implementar bcrypt para hashing de contraseñas (reemplazar SHA256)
- [ ] Agregar sal único por usuario
- [ ] Implementar JWT tokens para sesiones
- [ ] Agregar refresh tokens
- [ ] Crear middleware de autenticación
- [ ] Implementar rate limiting en login (máx 5 intentos/minuto)

### 1.2 Roles y permisos
- [ ] Crear enum de roles: `ADMIN`, `USER`, `VIEWER`
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
- [ ] Test: Login fallido después de 5 intentos
- [ ] Test: JWT expirado rechazado
- [ ] Test: Usuario normal no accede a admin
- [ ] Test: Inputs maliciosos rechazados

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

### 2.2 SQLAlchemy + Alembic
- [ ] Instalar `sqlalchemy`, `alembic`, `psycopg2-binary`
- [ ] Crear `app/core/database.py` con connection pool
- [ ] Definir modelos SQLAlchemy:
  - [ ] `User` (id, username, password_hash, role, created_at)
  - [ ] `Transaction` (id, user_id, tipo, monto, categoria, descripcion, fecha, moneda)
  - [ ] `Budget` (id, user_id, categoria, limite, mes)
  - [ ] `Goal` (id, user_id, nombre, objetivo, ahorrado, fecha_limite, categoria)
  - [ ] `CustomCategory` (id, user_id, tipo, nombre)
  - [ ] `Config` (user_id, moneda_activa, filtro_fecha_inicio, filtro_fecha_fin)
- [ ] Configurar Alembic para migraciones
- [ ] Crear migración inicial
- [ ] Probar migración en `pystreamflow_dev`

### 2.3 Repository Pattern
- [ ] Crear `app/repositories/base_repo.py` (interfaz abstracta)
- [ ] Implementar `PostgresRepo` con SQLAlchemy
- [ ] Crear `app/repositories/factory.py` para seleccionar DB según entorno
- [ ] Mantener SQLiteRepo para desarrollo offline
- [ ] Actualizar servicios para usar repository pattern

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
- [ ] Test: CRUD completo de transacciones
- [ ] Test: Múltiples usuarios no mezclan datos
- [ ] Test: Connection pool funciona bajo carga
- [ ] Test: Migraciones aplican correctamente

**Criterio de aceptación:** PostgreSQL funcionando con SQLAlchemy. Migraciones aplican. Tests de integración pasan.

---

## FASE 3: API REST
**Objetivo:** Separar backend de frontend para escalar independientemente.
**Dependencias:** Fase 2 completada
**Tiempo estimado:** 4-5 días

### 3.1 FastAPI setup
- [ ] Instalar `fastapi`, `uvicorn`, `pydantic`
- [ ] Crear `app/api/main.py` con FastAPI app
- [ ] Configurar CORS (origin: localhost para dev)
- [ ] Crear `app/api/deps.py` para dependency injection
- [ ] Crear estructura de routers:
  ```
  app/api/
  ├── main.py
  ├── deps.py
  ├── routers/
  │   ├── __init__.py
  │   ├── auth.py
  │   ├── transactions.py
  │   ├── budgets.py
  │   ├── goals.py
  │   └── reports.py
  └── schemas/
      ├── __init__.py
      ├── auth.py
      ├── transaction.py
      ├── budget.py
      └── goal.py
  ```

### 3.2 Pydantic schemas
- [ ] Crear schemas de request/response para cada entidad
- [ ] Implementar validación con pydantic v2
- [ ] Agregar documentación con descriptions y examples
- [ ] Configurar OpenAPI tags y metadata

### 3.3 Endpoints de autenticación
- [ ] `POST /auth/register` - Registro
- [ ] `POST /auth/login` - Login (retorna JWT)
- [ ] `POST /auth/refresh` - Refresh token
- [ ] `GET /auth/me` - Usuario actual
- [ ] `PUT /auth/password` - Cambiar contraseña

### 3.4 Endpoints de transacciones
- [ ] `GET /transactions` - Listar (con filtros, paginación)
- [ ] `POST /transactions` - Crear
- [ ] `GET /transactions/{id}` - Obtener una
- [ ] `PUT /transactions/{id}` - Actualizar
- [ ] `DELETE /transactions/{id}` - Eliminar
- [ ] `POST /transactions/import` - Importar CSV/JSON
- [ ] `GET /transactions/export` - Exportar CSV/JSON/PDF

### 3.5 Endpoints de presupuestos
- [ ] `GET /budgets` - Listar presupuestos del mes
- [ ] `POST /budgets` - Crear/actualizar
- [ ] `DELETE /budgets/{categoria}` - Eliminar
- [ ] `GET /budgets/alerts` - Alertas de excedido

### 3.6 Endpoints de metas
- [ ] `GET /goals` - Listar metas
- [ ] `POST /goals` - Crear meta
- [ ] `PUT /goals/{id}` - Actualizar (ahorrado)
- [ ] `DELETE /goals/{id}` - Eliminar

### 3.7 Endpoints de reportes
- [ ] `GET /reports/summary` - Resumen del período
- [ ] `GET /reports/monthly` - Comparativa mensual
- [ ] `GET /reports/by-category` - Por categoría
- [ ] `GET /reports/pdf` - Generar PDF

### 3.8 Testing de API
- [ ] Configurar `httpx` para tests de API
- [ ] Test: Registro + Login + Token
- [ ] Test: CRUD transacciones autenticado
- [ ] Test: 401 sin token
- [ ] Test: 403 sin permisos
- [ ] Test: Validación de inputs inválidos
- [ ] Test: Rate limiting funciona

### 3.9 Documentación
- [ ] Configurar Swagger UI (`/docs`)
- [ ] Configurar ReDoc (`/redoc`)
- [ ] Agregar ejemplos en cada endpoint
- [ ] Generar SDK opcional con openapi-generator

**Criterio de aceptación:** API REST funcional con todos los endpoints. Documentación Swagger completa. Tests pasan.

---

## FASE 4: INTELIGENCIA ARTIFICIAL PROFESIONAL
**Objetivo:** Transformar el chatbot de reglas en un sistema IA real con RAG.
**Dependencias:** Fase 3 completada
**Tiempo estimado:** 5-7 días

### 4.1 ChromaDB para embeddings
- [ ] Instalar `chromadb`
- [ ] Crear `app/ai/vector_store.py`
- [ ] Implementar indexación de transacciones como embeddings
- [ ] Configurar embedding model: `nomic-embed-text` vía Ollama
- [ ] Crear función `indexar_transacciones(user_id)`
- [ ] Crear función `buscar_contexto(user_id, query, top_k=5)`

### 4.2 RAG (Retrieval-Augmented Generation)
- [ ] Crear `app/ai/rag_engine.py`
- [ ] Flujo:
  ```
  1. Usuario pregunta algo
  2. Buscar transacciones relevantes en ChromaDB
  3. Construir prompt con contexto + datos encontrados
  4. Enviar a LLM (Ollama o HuggingFace)
  5. Retornar respuesta contextualizada
  ```
- [ ] Implementar `consultar_ia_rag(user_id, pregunta)`
- [ ] Mantener fallback a reglas si ChromaDB/LM falla

### 4.3 Multi-provider IA
- [ ] Crear `app/ai/providers/base_provider.py` (interfaz)
- [ ] Implementar providers:
  - [ ] `OllamaProvider` (local, `qwen2.5-coder:7b`)
  - [ ] `HuggingFaceProvider` (cloud, Zephyr)
  - [ ] `GeminiProvider` (cloud, gemini-2.0-flash)
- [ ] Crear `app/ai/provider_factory.py` con fallback chain
- [ ] Configurar prioridad: Ollama → HuggingFace → Gemini
- [ ] Agregar métricas de latencia por provider

### 4.4 Memoria de conversación
- [ ] Crear tabla `chat_history` en PostgreSQL:
  ```sql
  CREATE TABLE chat_history (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    role VARCHAR(20) NOT NULL,  -- 'user' o 'assistant'
    content TEXT NOT NULL,
    context JSONB,              -- datos financieros usados
    provider VARCHAR(50),       -- qué IA respondió
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```
- [ ] Implementar `ChatMemoryService` con:
  - [ ] Guardar cada mensaje (user + assistant)
  - [ ] Cargar últimos N mensajes para contexto
  - [ ] Resumen automático de conversación larga
- [ ] Limitar ventana de contexto (últimos 20 mensajes)
- [ ] Agregar botón "Limpiar historial de chat"

### 4.5 Análisis predictivo
- [ ] Crear `app/ai/analytics.py`
- [ ] Implementar análisis de patrones:
  - [ ] Tendencia de gasto por categoría (sube/baja)
  - [ ] Predicción de gasto mensual basada en histórico
  - [ ] Detección de gastos anómalos (>2 desviaciones estándar)
  - [ ] Sugerencia de presupuesto basada en gasto real
- [ ] Usar `numpy` + `scikit-learn` para regresión simple
- [ ] Generar "Insights IA" automáticos en dashboard:
  ```
  "Tu gasto en Comida subió 23% este mes vs el anterior"
  "Basado en tu histórico, vas a gastar ~$180,000 este mes"
  " detectamos un gasto inusual de $50,000 en Transporte el martes"
  ```

### 4.6 Voice input (opcional)
- [ ] Instalar `whisper` (openai-whisper)
- [ ] Implementar `app/ai/voice.py`
- [ ] Agregar botón de micrófono en chat UI
- [ ] Transcribir audio → texto → consultar IA
- [ ] Configurar modelo `tiny` o `base` para CPU

### 4.7 Tests de IA
- [ ] Test: RAG retorna contexto relevante
- [ ] Test: Fallback a HuggingFace si Ollama falla
- [ ] Test: Fallback a reglas si todo falla
- [ ] Test: Memoria guarda y carga mensajes
- [ ] Test: Análisis predictivo genera resultados
- [ ] Test: Rate limiting en llamadas a IA

**Criterio de aceptación:** IA con RAG funcionando. Memoria persistente. Multi-provider con fallback. Análisis predictivo básico.

---

## FASE 5: FRONTEND PROFESIONAL
**Objetivo:** UI de nivel producción con componentes reutilizables.
**Dependencias:** Fase 3 completada (paralela a Fase 4)
**Tiempo estimado:** 4-5 días

### 5.1 Componentes reutilizables
- [ ] Crear `app/ui/components/` con:
  - [ ] `metric_card.py` - Tarjeta de métrica reutilizable
  - [ ] `data_table.py` - Tabla con sorting, filtros, paginación
  - [ ] `chart_container.py` - Wrapper de Plotly con tema consistente
  - [ ] `form_builder.py` - Builder de formularios con validación
  - [ ] `modal.py` - Modales reutilizables
  - [ ] `toast.py` - Notificaciones toast
  - [ ] `loading.py` - Skeletons y spinners

### 5.2 Dashboard mejorado
- [ ] Rediseñar dashboard con widgets configurables
- [ ] Agregar "date range picker" profesional
- [ ] Implementar drag-and-drop de widgets (con `streamlit-sortables`)
- [ ] Agregar widget de "Resumen IA" con insights automáticos
- [ ] Mostrar tendencias con indicadores visuales (↑↓→)

### 5.3 Chat IA mejorado
- [ ] Streaming de respuestas (token por token)
- [ ] Markdown rendering en respuestas
- [ ] Botones de "regenerar respuesta"
- [ ] Indicador de "escribiendo..." animado
- [ ] Historial de conversaciones guardadas
- [ ] Selector de provider IA (Ollama/HF/Gemini)

### 5.4 Responsive design
- [ ] Optimizar para móvil (CSS media queries)
- [ ] Sidebar colapsable en móvil
- [ ] Touch-friendly buttons
- [ ] Layout adaptativo

### 5.5 Temas
- [ ] Implementar toggle oscer/claro
- [ ] Guardar preferencia en config
- [ ] CSS variables para fácil customización

### 5.6 Onboarding
- [ ] Wizard de primeros pasos
- [ ] Tooltips explicativos
- [ ] Empty states ilustrados
- [ ] Keyboard shortcuts help modal

**Criterio de aceptación:** UI profesional, responsive, con componentes reutilizables. Chat con streaming.

---

## FASE 6: DEPLOY Y DEVOPS
**Objetivo:** Deploy automatizado, escalable, y monitoreado.
**Dependencias:** Fase 2 completada (puede ir en paralelo con 3-5)
**Tiempo estimado:** 3-4 días

### 6.1 Docker completo
- [ ] Crear `Dockerfile` multi-stage:
  ```dockerfile
  # Build stage
  FROM python:3.12-slim AS builder
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  # Runtime stage
  FROM python:3.12-slim
  WORKDIR /app
  COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
  COPY . .
  EXPOSE 8501
  CMD ["streamlit", "run", "app/main.py"]
  ```
- [ ] Crear `docker-compose.yml` completo:
  ```yaml
  services:
    app:
      build: .
      ports: ["8501:8501"]
      depends_on: [db, redis]
      environment:
        - DATABASE_URL=postgresql://...
        - REDIS_URL=redis://redis:6379

    db:
      image: postgres:16-alpine
      volumes: [pgdata:/var/lib/postgresql/data]
      environment:
        POSTGRES_DB: pystreamflow
        POSTGRES_USER: pystreamflow
        POSTGRES_PASSWORD: ${DB_PASSWORD}

    redis:
      image: redis:7-alpine
      volumes: [redisdata:/data]

    chromadb:
      image: chromadb/chroma:latest
      ports: ["8000:8000"]
      volumes: [chromadata:/chroma/chroma]

  volumes:
    pgdata:
    redisdata:
    chromadata:
  ```
- [ ] Crear `.dockerignore`
- [ ] Probar `docker-compose up` localmente

### 6.2 CI/CD mejorado
- [ ] Actualizar `.github/workflows/ci.yml`:
  ```yaml
  name: CI/CD
  on:
    push:
      branches: [main, dev]
    pull_request:
      branches: [main]

  jobs:
    test:
      runs-on: ubuntu-latest
      services:
        postgres:
          image: postgres:16
          env:
            POSTGRES_DB: test_db
            POSTGRES_USER: test
            POSTGRES_PASSWORD: test
          ports: [5432:5432]
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: "3.12"
        - run: pip install -r requirements.txt -r requirements-dev.txt
        - run: ruff check .
        - run: black --check .
        - run: mypy app/
        - run: pytest tests/ -v --cov=app --cov-report=xml
        - uses: codecov/codecov-action@v4

    deploy:
      needs: test
      if: github.ref == 'refs/heads/main'
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Deploy to Streamlit Cloud
          # Configurar secrets en GitHub
  ```
- [ ] Agregar badge de cobertura de código
- [ ] Configurar branch protection en `main`

### 6.3 Monitoreo
- [ ] Agregar health check endpoint: `GET /health`
- [ ] Implementar logging estructurado con `structlog`
- [ ] Agregar métricas básicas:
  - [ ] Requests por minuto
  - [ ] Latencia promedio de IA
  - [ ] Errores por tipo
  - [ ] Usuarios activos
- [ ] Configurar alertas básicas (email en errores críticos)

### 6.4 Redis
- [ ] Instalar Redis local (ya pendiente en tu setup)
- [ ] Implementar cache de:
  - [ ] Sesiones de usuario
  - [ ] Queries frecuentes (resúmenes)
  - [ ] Rate limiting
- [ ] Configurar TTL por tipo de dato

### 6.5 Backup
- [ ] Script de backup automático de PostgreSQL
- [ ] Backup de ChromaDB
- [ ] Almacenamiento en S3 o similar
- [ ] Restore manual documentado

**Criterio de aceptación:** Docker compose funciona. CI/CD pasa. Logging y monitoreo básico activo.

---

## FASE 7: MULTI-IDIOMA Y LOCALIZACIÓN
**Objetivo:** Soporte internacionalización.
**Dependencias:** Fase 5 completada
**Tiempo estimado:** 2-3 días

### 7.1 i18n
- [ ] Instalar `streamlit-i18n` o usar `gettext`
- [ ] Crear archivos de traducción:
  ```
  locales/
  ├── es_AR.json
  ├── en_US.json
  └── pt_BR.json
  ```
- [ ] Extraer todos los strings hardcodeados
- [ ] Reemplazar por funciones de traducción
- [ ] Selector de idioma en sidebar

### 7.2 Multi-moneda
- [ ] Soportar USD, EUR, BRL además de ARS
- [ ] API de tasas de cambio (exchangerate-api.com)
- [ ] Guardar transacciones en moneda original
- [ ] Mostrar conversiones en dashboard

**Criterio de aceptación:** App funciona en español e inglés. Multi-moneda funcional.

---

## FASE 8: FEATURES AVANZADAS
**Objetivo:** Funcionalidades que diferencian de la competencia.
**Dependencias:** Fase 4 completada
**Tiempo estimado:** 5-7 días

### 8.1 Notificaciones
- [ ] Email notifications (using `smtplib` + templates)
- [ ] Alertas de presupuesto excedido
- [ ] Recordatorios de metas
- [ ] Resumen semanal automático

### 8.2 Integraciones
- [ ] Webhook para Notion/Google Sheets
- [ ] Importación desde archivos bancarios (CSV)
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
| Fase 0: Limpieza | ⬜ No iniciada | 0% |
| Fase 1: Seguridad | ⬜ No iniciada | 0% |
| Fase 2: PostgreSQL | ⬜ No iniciada | 0% |
| Fase 3: API REST | ⬜ No iniciada | 0% |
| Fase 4: IA Profesional | ⬜ No iniciada | 0% |
| Fase 5: Frontend | ⬜ No iniciada | 0% |
| Fase 6: DevOps | ⬜ No iniciada | 0% |
| Fase 7: i18n | ⬜ No iniciada | 0% |
| Fase 8: Features | ⬜ No iniciada | 0% |
| Fase 9: Testing | ⬜ No iniciada | 0% |
| Fase 10: Lanzamiento | ⬜ No iniciada | 0% |

**Progreso total: 0%**

---

## NOTAS Y APRENDIZAJES

### [Fecha] - Nota
> Agregar aquí aprendizajes, cambios de dirección, bloqueos, etc.

---

## COMANDOS RÁPIDOS

### Desarrollo
```bash
# Activar entorno
conda activate pystreamflow  # o venv

# Ejecutar app
streamlit run app/main.py

# Ejecutar API
uvicorn app.api.main:app --reload --port 8000

# Docker
docker-compose up -d
```

### Testing
```bash
# Todos los tests
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
*Última actualización: 18/07/2026.*
