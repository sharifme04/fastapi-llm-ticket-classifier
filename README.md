# 🎫 Customer Support Ticket Classifier & Suggester

A production-ready FastAPI service that automatically classifies incoming customer support tickets using Anthropic Claude, generates suggested responses via SSE streaming, and tracks API costs.

## Architecture

```
┌─────────────────┐
│   Client/UI     │
└────────┬────────┘
         │ POST /tickets
         ▼
┌─────────────────────────────┐
│  FastAPI Server             │
│  ┌──────────────────────┐   │
│  │ Route: /tickets      │   │
│  └──────────────────────┘   │
│  ┌──────────────────────┐   │
│  │ Service: Classify    │   │
│  │ (check Redis first)  │   │
│  │ (calls Claude API)   │   │
│  └──────────────────────┘   │
│  ┌──────────────────────┐   │
│  │ Service: Suggest     │   │
│  │ (streams response)   │   │
│  └──────────────────────┘   │
└────┬──────────────────────────┘
     │
     ├─ PostgreSQL (tickets, classifications, costs)
     ├─ Redis (LLM response cache)
     └─ Anthropic API (Claude calls)
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI + Uvicorn |
| Database | PostgreSQL + asyncpg |
| Cache | Redis (LLM response caching) |
| ORM | SQLAlchemy 2.0 (async) |
| LLM | Anthropic Claude Sonnet |
| Validation | Pydantic v2 + pydantic-settings |
| Rate Limiting | slowapi |
| Testing | pytest + pytest-asyncio |
| Logging | python-json-logger (structured JSON) |
| Containerisation | Docker Compose |

## Features

- ✅ **Automatic Classification** — Classifies tickets into: Bug, Feature Request, Billing, General Inquiry, Urgent
- ✅ **Redis Caching** — Hash(subject+description) → skip API call if seen within 1 hour
- ✅ **SSE Streaming** — Suggested responses streamed token-by-token via Server-Sent Events
- ✅ **Cost Tracking** — Logs tokens per request, calculates cost, daily budget alerts
- ✅ **Analytics Dashboard** — Tickets by category, avg confidence, monthly cost summary
- ✅ **Structured Logging** — JSON logs with request_id, duration_ms, level
- ✅ **Rate Limiting** — Protects LLM endpoints from abuse
- ✅ **Health Checks** — Verifies DB + Redis connectivity

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check (DB + Redis status) |
| POST | `/tickets` | Create new ticket + auto-classify |
| GET | `/tickets/{id}` | Get ticket details + classification |
| GET | `/tickets/{id}/suggest` | Stream suggested response (SSE) |
| POST | `/tickets/{id}/feedback` | Mark suggestion as helpful/not |
| GET | `/analytics/summary` | Classification stats + cost summary |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Anthropic API key ([get one here](https://console.anthropic.com/))

### 1. Clone & Configure

```bash
cd project-1-ticket-classifier
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Start Services

```bash
docker-compose up --build
```

This starts:
- **API** at `http://localhost:8000`
- **PostgreSQL** at `localhost:5432`
- **Redis** at `localhost:6379`

### 3. Test It

```bash
# Health check
curl http://localhost:8000/health

# Create a ticket
curl -X POST http://localhost:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Cannot login to my account",
    "description": "I have been trying to login for 2 hours. I keep getting an invalid credentials error even though I reset my password.",
    "priority": "high"
  }'

# Get analytics
curl http://localhost:8000/analytics/summary

# Stream a suggestion (SSE)
curl -N http://localhost:8000/tickets/1/suggest
```

### 4. API Docs

Visit `http://localhost:8000/docs` for interactive Swagger UI.

## Local Development (without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make sure PostgreSQL and Redis are running locally
# Update .env with your local connection strings

# Run the server
uvicorn app.main:app --reload --port 8000
```

## Run Tests

```bash
# Install test dependencies
pip install aiosqlite

# Run tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

## Example Request & Response

### Create Ticket

**Request:**
```json
POST /tickets
{
  "subject": "App crashes when uploading large files",
  "description": "Every time I try to upload a file larger than 50MB, the app crashes with a white screen. I'm using Chrome 120 on macOS.",
  "priority": "high"
}
```

**Response (201):**
```json
{
  "id": 1,
  "subject": "App crashes when uploading large files",
  "description": "Every time I try to upload a file larger than 50MB...",
  "priority": "high",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "classification": {
    "category": "Bug",
    "confidence": 0.95,
    "reasoning": "The ticket describes a software crash triggered by a specific user action.",
    "cache_hit": false,
    "created_at": "2025-01-15T10:30:01Z"
  }
}
```

## Project Structure

```
project-1-ticket-classifier/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, middleware, exception handlers
│   ├── config.py             # pydantic-settings configuration
│   ├── database.py           # Async SQLAlchemy engine + session
│   ├── redis_client.py       # Redis connection pool
│   ├── models/               # SQLAlchemy models
│   │   ├── ticket.py         # Ticket model
│   │   ├── classification.py # Classification model
│   │   └── api_cost.py       # Daily cost tracking
│   ├── schemas/              # Pydantic validation schemas
│   │   ├── ticket.py         # Request/response schemas
│   │   ├── classification.py # LLM output validation
│   │   └── analytics.py      # Analytics response
│   ├── routers/              # API endpoint handlers
│   │   ├── health.py         # GET /health
│   │   ├── tickets.py        # Ticket CRUD + SSE streaming
│   │   └── analytics.py      # GET /analytics/summary
│   ├── services/             # Business logic
│   │   ├── classifier.py     # Claude classification + Redis cache
│   │   ├── suggester.py      # Claude suggestion streaming
│   │   └── cost_tracker.py   # Token/cost logging + budget alerts
│   └── utils/
│       ├── logging.py        # Structured JSON logging
│       └── exceptions.py     # Global exception handlers
├── tests/
│   ├── conftest.py           # Test fixtures
│   ├── test_health.py
│   ├── test_tickets.py
│   ├── test_classifier.py
│   └── test_analytics.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pyproject.toml
├── .env.example
└── .gitignore
```

## Cost Control

- Token usage logged per request (input + output)
- Costs calculated using configurable Anthropic pricing (env vars, not hardcoded)
- Daily cost aggregated in `api_costs` table
- **Budget alert**: If daily cost exceeds `DAILY_COST_LIMIT` ($10 default), further LLM calls are blocked with HTTP 429
- Redis caching reduces LLM calls for identical tickets by ~30%

## License

MIT
# fastapi-llm-ticket-classifier
