# 💰 PyFinFlow

<div align="center">

![CI](https://github.com/MarceloAdan73/pyfinflow-AI/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/MarceloAdan73/pyfinflow-AI?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-221%20passed-brightgreen?style=for-the-badge)

**🚀 Personal finance management web app with integrated AI**

[📱 Demo](#-demo) • [📋 Features](#-features) • [🛠️ Installation](#-installation) • [📖 Technical Docs](#-technical-documentation) • [🤝 Contribute](#-contribute)

</div>

---

## 🌟 Why PyFinFlow?

| Feature | Description |
|---------|-------------|
| 🎯 **Smart** | Automatic amount detection (US/EU format) |
| 📊 **Visual** | Interactive charts with Plotly |
| 🤖 **AI** | Financial assistant with RAG + multi-provider (Ollama, HuggingFace, Gemini) |
| 💾 **Persistent** | PostgreSQL (prod) + SQLite (dev) with Repository Pattern |
| 🔒 **Secure** | bcrypt + JWT + rate limiting + role-based access |
| 🧪 **Tested** | 221 tests passing (unit + integration) |
| 📖 **Documented** | Full Swagger/ReDoc API documentation |
| 🌍 **i18n** | Spanish, English |
| 💱 **Multi-currency** | ARS, USD, EUR, BRL with live conversion |

---

## 📱 Demo

> **Demo actual:** local (`http://localhost:3000` + `http://localhost:8000/docs`) — deploy público Vercel/Render pendiente (Fase 10).
> Legacy Streamlit: `https://pystreamflow-ai-ufg7wsp8pcxpatqt3lxrsk.streamlit.app/` (deprecado).

---

## 📸 Screenshots

<div align="center">

| Desktop - Dashboard | Desktop - New Transaction | Desktop - History |
|---------------------|-------------------------|-------------------|
| <img src="assets/desktop1.png" width="250"> | <img src="assets/desktop2.png" width="250"> | <img src="assets/desktop3.png" width="250"> |

| Desktop - Charts | Desktop - Budgets | Mobile |
|--------------------|----------------------|-------|
| <img src="assets/desktop4.png" width="250"> | <img src="assets/desktop5.png" width="250"> | <img src="assets/mobile.png" width="200"> |

</div>

---

```
┌─────────────────────────────────────────────────────────────┐
│  💰 PyFinFlow                                 [Dashboard]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│   │   INGRESOS   │  │    GASTOS    │  │   BALANCE    │    │
│   │  $ 150,000   │  │   $ 45,000   │  │  $ 105,000   │    │
│   └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│   📈 Evolución de Gastos    |    🍰 Por Categoría         │
│   ┌──────────────────┐      |    ┌──────────────────┐     │
│   │  ▓▓▓▓▓▓░░░░░░    │      │    │   ████░░░░░░    │     │
│   │  ▓▓▓▓▓▓▓▓░░░░    │      │    │   ██████░░░░    │     │
│   └──────────────────┘      |    └──────────────────┘     │
│                                                             │
│   📝 Transacciones Recientes                              │
│   ┌─────────────────────────────────────────────────────┐│
│   │ 🟢 Salario        $ 80,000    15/03/2024            ││
│   │ 🔴 Supermercado   $ 15,000    14/03/2024            ││
│   │ 🔴 Transporte     $ 5,000     14/03/2024            ││
│   └─────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🏠 Core
- ✅ Transaction recording with **smart amount detection**
- ✅ **Dashboard** with real-time metrics
- ✅ **Currency: Argentine Pesos (ARS)**
- ✅ Date filters with validation
- ✅ Interactive Plotly charts with tooltips
- ✅ Pagination in history (1000+ transactions)

### 💰 Financial Management
- ✅ **Monthly budgets** per category with visual alerts
- ✅ **Savings goals** with visual progress
- ✅ In-app alerts when budget exceeded
- ✅ Complete history with search, filters, editing

### 💾 Data & Sync
- ✅ Local **SQLite** persistence
- ✅ Backup/Import **JSON**
- ✅ **PDF** report export
- ✅ **Supabase** authentication (optional)
- ✅ Offline mode without account

### 🏷️ Categories
- ✅ Predefined: Food, Housing, Transport, etc.
- ✅ **Custom**: Create your own categories

### 🤖 AI Assistant
- ✅ Floating chat with personalized responses
- ✅ **HuggingFace Zephyr** for intelligent analysis
- ✅ **Local fallback** without internet

### 🎨 UI/UX
- ✅ **Responsive** design (mobile + desktop)
- ✅ **Animations** micro-interactions
- ✅ **Onboarding** tutorial
- ✅ Skeleton loaders
- ✅ **PWA** installable as app

### ⌨️ Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl + N` | New transaction |
| `Ctrl + H` | Go to History |
| `Ctrl + D` | Go to Dashboard |

---

## 🛠️ Installation

### Requirements
- Python 3.12+ / Node 20+
- PostgreSQL 16 (opcional, SQLite por defecto) + pip + npm

### Step by step

```bash
# 1. Clone
git clone https://github.com/MarceloAdan73/pyfinflow-AI.git
cd pyfinflow-AI

# 2. Backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # configurar DATABASE_URL, JWT_SECRET, OLLAMA_URL
uvicorn app.api.main:app --reload --port 8000
# Swagger: http://localhost:8000/docs

# 3. Frontend
cd frontend
npm install
npm run dev
# App: http://localhost:3000 (login: demo/demo123)

# 4. Datos demo (opcional)
python scripts/seed_demo.py
```

### 🚀 Deploy

* **Frontend:** Vercel (`frontend/` → Next.js 16)
* **Backend:** Render/Railway/Fly (`uvicorn app.api.main:app --host 0.0.0.0`)
* **Legacy Streamlit** deprecado (no recomendado)

---

## 🏗️ Technical Architecture

```
pyfinflow-AI/
├── app/
│   ├── api/              # FastAPI + routers (auth, transactions, budgets, goals, ai) + schemas
│   ├── core/             # config, auth (bcrypt/JWT), database (SQLAlchemy), cache, metrics
│   ├── ai/               # RAG, vector_store (ChromaDB), providers (Ollama/HF/Gemini)
│   ├── services/         # budget_alerts, csv_import
│   └── repositories/     # Repository Pattern (postgres_repo, factory)
├── frontend/             # Next.js 16 + React 19 + Tailwind v4 + next-intl (es/en)
├── alembic/              # Migraciones (001_initial_schema, 002_chat_messages)
├── tests/unit/           # 221 tests
├── scripts/seed_demo.py  # Datos demo (~70 txns, presupuestos, metas)
├── docker-compose.yml    # app + PostgreSQL + Redis + ChromaDB
├── pyproject.toml        # ruff + pytest
└── ROADMAP_SAAS.md       # Roadmap Fases 0-10
```

---

## 📖 Technical Documentation

### Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Backend** | FastAPI + SQLAlchemy + Alembic | 0.139 / 2.0 / 1.13 |
| **Frontend** | Next.js + React + Tailwind + next-intl | 16.2 / 19 / 4 |
| **DB** | PostgreSQL 16 (prod) / SQLite (dev) | 16 |
| **AI** | Ollama + ChromaDB + HuggingFace + Gemini | local/cloud |
| **Auth** | bcrypt + JWT + rate limiting | 12 rounds / 1h access |
| **Cache** | Redis (fallback in-memory) | 7 |
| **Testing** | Pytest + Ruff | 8 / 0.2 |

### Database Schema

```sql
-- Transactions
CREATE TABLE transacciones (
    id TEXT PRIMARY KEY,
    tipo TEXT NOT NULL,
    monto REAL NOT NULL,
    categoria TEXT NOT NULL,
    descripcion TEXT,
    fecha TEXT NOT NULL,
    moneda TEXT DEFAULT 'ARS',
    user_id TEXT,
    created_at TEXT
);

-- Budgets
CREATE TABLE presupuestos (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    categoria TEXT NOT NULL,
    limite REAL NOT NULL
);

-- Savings Goals
CREATE TABLE metas_ahorro (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    nombre TEXT NOT NULL,
    objetivo REAL NOT NULL,
    ahorrado REAL DEFAULT 0,
    fecha_limite TEXT,
    categoria TEXT
);

-- Custom Categories
CREATE TABLE categorias_custom (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    tipo TEXT NOT NULL,
    nombre TEXT NOT NULL
);
```

### Smart Amount Detection

The app automatically detects formats:
```python
"15000"           → 15000    # Simple
"15000 ARS"       → 15000    # With text
"1.500,50"       → 1500.50  # European
"1500.50"        → 1500.50  # American
```

### AI Assistant API

```python
# Query HuggingFace
response = consultar_ia("How much did I spend on food?", context)

# Local fallback (no internet)
response = consultar_ia_local(question, context)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_formatters.py -v
```

**Results:** 221 tests passing ✅

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_auth.py` | 18 | bcrypt, JWT, rate limiting, roles |
| `test_api.py` | 30 | All REST endpoints (auth, transactions, budgets, goals, metrics) |
| `test_ai_api.py` | 10 | AI endpoints (chat, history, insights, suggestions, status) |
| `test_ai.py` | 30 | Providers, fallback, analytics, chat memory |
| `test_repositories.py` | 13 | CRUD operations (users, transactions, budgets, goals) |
| `test_formatters.py` | 22 | Number parsing, currency formatting, ID generation |
| `test_vector_store.py` | 14 | ChromaDB indexing, search, deletion |
| `test_rag_engine.py` | 5 | RAG pipeline, message building |
| `test_alerts.py` | 5 | SMTP alerts, critical errors |
| `test_config.py` | 11 | Settings types and defaults |
| `test_cache.py` | 7 | Redis fallback, rate limiting |
| `test_metrics.py` | 6 | Request tracking, Prometheus format |
| `test_budget_alerts.py` + `test_budget_alerts_api.py` | 21 | Alertas 80%/100% presupuesto |
| `test_csv_import.py` + `test_csv_import_api.py` | 18 | Import CSV (EU/US, ;/, aliases) |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL/SQLite connection string | `sqlite:///./pyfinflow_dev.db` |
| `JWT_SECRET` | Secret key for JWT tokens | `change-me-in-production` |
| `OLLAMA_URL` | Ollama server URL | `http://localhost:11434` |
| `HF_TOKEN` | HuggingFace token (optional) | - |
| `GEMINI_API_KEY` | Google Gemini key (optional) | - |
| `SMTP_HOST` | SMTP server for alerts | - |
| `ALERT_EMAIL_TO` | Alert recipient email | - |

### Seed Demo Data

```bash
python scripts/seed_demo.py
# Creates: 2 users (admin/demo), ~70 transactions, budgets, goals
# Login: POST /auth/login → {"username": "demo", "password": "demo123"}
```

### API Documentation

Once running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 🔮 Roadmap

- [x] Multi-currency (ARS, USD, EUR, BRL) — Fase 7
- [x] API documentation (Swagger/ReDoc) — Fase 3
- [x] Demo seed data — `scripts/seed_demo.py`
- [x] 221 tests + Ruff 0 — Fase 4-5
- [x] Alerts presupuesto 80%/100% — Fase 8.1
- [x] Import CSV (EU/US, 2MB/1000 filas) — Fase 8.2
- [ ] Deploy a producción (Vercel + Render) — Fase 10
- [ ] PWA offline — Fase 8.3
- [ ] Export Excel/PDF — Fase 8.2

---

## 🤝 Contribute

```bash
# 1. Fork
# 2. Create branch
git checkout -b feature/new-feature

# 3. Commit
git commit -am 'Add new feature'

# 4. Push
git push origin feature/new-feature

# 5. Pull Request
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - REST API Framework
- [Next.js](https://nextjs.org/) - Frontend Framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [PostgreSQL](https://www.postgresql.org/) - Database
- [ChromaDB](https://www.trychroma.com/) - Vector Store for RAG
- [Ollama](https://ollama.ai/) - Local AI inference
- [HuggingFace](https://huggingface.co/) - AI Models
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [Shadcn/UI](https://ui.shadcn.com/) - UI Components

---

<div align="center">

⭐ **If you like the project, give it a star!**

Made with ❤️ by PyFinFlow Team

</div>
