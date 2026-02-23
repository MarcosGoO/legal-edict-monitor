# Edict Guardian

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-orange.svg)](https://github.com/astral-sh/ruff)

**Mission-critical backend for scraping, processing, and analyzing Colombian legal gazettes and court edicts to provide real-time alerts to lawyers.**

## Overview

Edict Guardian monitors official Colombian court portals, extracts legal entities from PDF documents using OCR and NLP, and notifies law firms when their clients are mentioned in legal proceedings.

### Key Features

- **Smart OCR Pipeline** - Multi-engine OCR with automatic fallback (Native → Tesseract → AWS Textract)
- **Colombian Entity Extraction** - Specialized parser for Radicados, NITs, Cédulas, and names
- **Real-time Matching** - High-efficiency watchlist matching engine
- **Multi-channel Notifications** - WhatsApp, Email, and SMS alerts
- **Idempotent Processing** - Deduplication at every layer

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Court Portals  │────▶│  Ingestion Engine │────▶│  Smart OCR      │
│  (Rama Judicial)│     │  (Celery Crawler) │     │  (Tesseract)    │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌──────────────────┐     ┌───────▼─────────┐
│   WhatsApp/     │◀────│  Match & Alert   │◀────│  Entity Parser  │
│   Email/SMS     │     │  Engine          │     │  (spaCy NER)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Tesseract OCR (with Spanish language pack)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/edict-guardian.git
cd edict-guardian

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install spaCy Spanish model
python -m spacy download es_core_news_lg

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

### Running the Application

```bash
# Start the API server
uvicorn app.main:app --reload

# Start the Celery worker (in another terminal)
celery -A app.workers.celery_app worker --loglevel=info

# Start the Celery beat scheduler (in another terminal)
celery -A app.workers.celery_app beat --loglevel=info
```

The API documentation will be available at `http://localhost:8000/docs`

## Database Schema

The system uses PostgreSQL with the following core tables:

| Table | Description |
|-------|-------------|
| `law_firms` | Law firm accounts |
| `users` | Law firm staff members |
| `clients` | People/entities to monitor |
| `watchlist_entries` | Monitoring configurations |
| `raw_documents` | Ingested PDF documents |
| `extracted_entities` | Entities found in documents |
| `detected_edicts` | Matched edicts |
| `notifications` | Notification records |

See [plans/architecture.md](plans/architecture.md) for the complete schema.

## API Endpoints

### Document Processing

```bash
# Process a PDF document
curl -X POST "http://localhost:8000/api/v1/documents/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"

# Parse text for entities
curl -X POST "http://localhost:8000/api/v1/documents/parse-text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Radicado 2023-00123-45-67-890-12..."}'
```

### Client Management

```bash
# List clients
curl "http://localhost:8000/api/v1/clients"

# Create a client
curl -X POST "http://localhost:8000/api/v1/clients" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "JOSÉ GARCÍA", "document_type": "CC", "document_number": "12345678"}'
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_parser.py -v
```

## Configuration

Key environment variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `TESSERACT_LANG` | OCR language | `spa` |
| `SPACY_MODEL` | spaCy model name | `es_core_news_lg` |
| `TWILIO_ACCOUNT_SID` | Twilio account for WhatsApp/SMS | Optional |
| `SENDGRID_API_KEY` | SendGrid for email | Optional |

## Project Structure

```
edict-guardian/
├── app/
│   ├── api/v1/endpoints/     # REST API endpoints
│   ├── models/               # SQLAlchemy ORM models
│   ├── services/
│   │   ├── ocr/              # Smart OCR wrapper
│   │   └── parser/           # Colombian entity parser
│   ├── config.py             # Settings management
│   ├── database.py           # Database configuration
│   └── main.py               # FastAPI application
├── tests/                    # Test suite
├── plans/                    # Architecture documentation
├── pyproject.toml            # Project configuration
└── .env.example              # Environment template
```

## Security

- Use `.env.example` as template
- **API keys and secrets** - Store in AWS Secrets Manager or similar
- **PII data** - Encrypt sensitive fields in database
- **Rate limiting** - Implement per-user and per-IP limits

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Rama Judicial de Colombia](https://www.ramajudicial.gov.co/) - Public court information
- [spaCy](https://spacy.io/) - Industrial-strength NLP
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Open-source OCR engine
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

---

**⚠️ Disclaimer**: This tool is for informational purposes only. Always verify legal information with official sources. The developers are not responsible for any decisions made based on notifications from this system.