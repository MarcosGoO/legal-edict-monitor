# Edict Guardian

[![Deploy Frontend](https://github.com/MarcosGoO/legal-edict-monitor/actions/workflows/deploy-frontend.yml/badge.svg)](https://github.com/MarcosGoO/legal-edict-monitor/actions/workflows/deploy-frontend.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Herramienta de monitoreo de edictos judiciales colombianos para firmas de abogados.**

Extrae entidades legales (radicados, NITs, cédulas, nombres, juzgados) de documentos PDF mediante OCR y NLP especializado en español, y las cruza contra listas de vigilancia de clientes para generar alertas automáticas.

🌐 **[Ver demo en vivo](https://MarcosGoO.github.io/legal-edict-monitor/)** · 📖 **[API Docs](https://legal-edict-monitor.onrender.com/docs)**

---

## Stack

| Capa | Tecnología |
| ---- | ---------- |
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS + Radix UI |
| Backend | FastAPI + SQLAlchemy (async) + Pydantic v2 |
| OCR | PyMuPDF (nativo) → Tesseract → AWS Textract (fallback) |
| NLP | spaCy `es_core_news_sm` + regex patterns colombianos |
| Base de datos | PostgreSQL (Neon) |
| Caché | Redis (Upstash) |
| Deploy | GitHub Pages (frontend) + Render (backend, Docker) |

---

## Funcionalidades

### Procesamiento de documentos

- **Upload PDF** con drag & drop — extrae texto vía OCR multi-engine
- **Paste de texto** — análisis directo con NLP
- Detección de 5 tipos de entidades legales colombianas:
  - **Radicado** — número de proceso (23 dígitos)
  - **NIT** — identificación tributaria empresarial
  - **Cédula** — documento de identidad personal
  - **Nombre** — personas naturales
  - **Juzgado** — despacho judicial

### Gestión de clientes

- CRUD completo de clientes con validación
- Listas de vigilancia por cliente (radicados + juzgados)
- Canales de notificación configurables (email / WhatsApp)

### Dashboard

- Estado en tiempo real del sistema (API, BD, Redis)
- Accesos rápidos a las funciones principales

---

## Correr localmente

### Requisitos

- Docker Desktop (para Postgres + Redis)
- Python 3.11+
- Node.js 20+

### 1. Servicios de infraestructura

```bash
docker-compose up -d
```

### 2. Backend

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download es_core_news_sm

uvicorn app.main:app --reload --port 8000
```

API en `http://localhost:8000` · Docs en `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI en `http://localhost:3000`

---

## Deploy en producción (stack gratuito permanente)

| Servicio | Plataforma | Tier |
| -------- | ---------- | ---- |
| Frontend | GitHub Pages | Gratis ∞ |
| Backend | Render (Docker) | Gratis ∞* |
| PostgreSQL | Neon | Gratis ∞ |
| Redis | Upstash | Gratis ∞ |

*Render free hace spin-down tras 15 min de inactividad (~30s en primera request).

### Pasos

1. **Neon** — crear proyecto PostgreSQL, copiar connection string
2. **Upstash** — crear Redis Regional, copiar URL TLS
3. **Render** — conectar repo, runtime Docker, agregar env vars:
   - `DATABASE_URL` → `postgresql+asyncpg://...neon.tech/...?ssl=true`
   - `REDIS_URL` → `rediss://...upstash.io:6379`
   - `CORS_ORIGINS` → `["https://MarcosGoO.github.io"]`
   - `SECRET_KEY` y `JWT_SECRET_KEY` → strings aleatorios de 32+ chars
4. **GitHub Secret** → `VITE_API_URL` = URL del servicio Render
5. Push a `main` → GitHub Actions despliega el frontend automáticamente

---

## Estructura del proyecto

```text
legal-edict-monitor/
├── app/                          # Backend FastAPI
│   ├── api/v1/endpoints/         # Endpoints REST
│   │   ├── clients.py            # CRUD clientes + watchlist
│   │   └── documents.py          # OCR + NLP processing
│   ├── models/                   # SQLAlchemy ORM
│   ├── services/
│   │   ├── ocr/                  # Pipeline OCR multi-engine
│   │   └── parser/               # Extractor de entidades colombianas
│   ├── config.py                 # Configuración centralizada
│   ├── database.py               # Engine async + sesiones
│   └── main.py                   # App FastAPI + lifespan
├── frontend/                     # Frontend React
│   └── src/
│       ├── api/                  # Axios calls tipados
│       ├── components/
│       │   ├── layout/           # AppShell, Sidebar, TopBar
│       │   └── ui/               # Card, Toast, MonoValue, etc.
│       ├── hooks/                # TanStack Query wrappers
│       ├── pages/
│       │   ├── Dashboard/        # Status del sistema
│       │   ├── Clients/          # Lista, detalle, formularios
│       │   └── Documents/        # Upload PDF + resultados
│       └── types/                # Interfaces TypeScript
├── tests/                        # Test suite (pytest)
├── Dockerfile                    # Imagen Python 3.11 para Render
├── docker-compose.yml            # Postgres + Redis para desarrollo local
├── render.yaml                   # Infra como código para Render
└── requirements.txt              # Dependencias de producción
```

---

## API Reference

### Documentos

```bash
# Procesar PDF
POST /api/v1/documents/process
# Content-Type: multipart/form-data  |  field: file

# Analizar texto
POST /api/v1/documents/parse-text
# Body: {"text": "El radicado 11001310300120230012300 corresponde a..."}
```

### Clientes

```bash
GET    /api/v1/clients                 # Listar (paginado, búsqueda)
POST   /api/v1/clients                 # Crear
GET    /api/v1/clients/{id}            # Detalle
PUT    /api/v1/clients/{id}            # Actualizar
DELETE /api/v1/clients/{id}            # Eliminar
POST   /api/v1/clients/{id}/watchlist  # Agregar vigilancia
```

### Health

```bash
GET /health   # Estado de la API
GET /ready    # Estado de DB + Redis
GET /docs     # Swagger UI (solo en development)
```

---

## Testing

```bash
pytest                              # Suite completa
pytest --cov=app --cov-report=html  # Con cobertura
pytest tests/test_parser.py -v      # Módulo específico
```

---

## Licencia

MIT — ver [LICENSE](LICENSE)

---

> **Aviso**: Esta herramienta es de uso informativo. Verificar siempre la información legal en fuentes oficiales ([Rama Judicial de Colombia](https://www.ramajudicial.gov.co/)).
