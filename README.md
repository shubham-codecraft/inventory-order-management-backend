# Inventory & Order Management — Backend

FastAPI + PostgreSQL + Poetry backend following **SOLID principles**.

## Architecture

```
app/
├── api/v1/endpoints/     # Thin controllers — HTTP in/out only
│   ├── products.py
│   ├── customers.py
│   ├── orders.py
│   └── dashboard.py
├── core/
│   ├── config.py         # Pydantic Settings — env vars
│   ├── dependencies.py   # FastAPI DI providers
│   └── exception_handlers.py
├── db/
│   └── database.py       # Async SQLAlchemy engine + session
├── models/               # SQLAlchemy ORM models
├── repositories/         # Data access layer (Repository Pattern)
├── schemas/              # Pydantic request/response schemas
├── services/             # Business logic layer
└── exceptions/           # Custom exception hierarchy
```

## SOLID Principles Applied

| Principle | Where |
|---|---|
| **S** — Single Responsibility | Each service handles exactly one domain |
| **O** — Open/Closed | New features extend services, not modify them |
| **L** — Liskov Substitution | Repositories implement `AbstractRepository[T]` |
| **I** — Interface Segregation | Repos expose only what each service needs |
| **D** — Dependency Inversion | Services depend on repo abstractions via DI |

## Business Logic

- ✅ SKU uniqueness enforced at service layer
- ✅ Customer email uniqueness enforced at service layer
- ✅ Stock cannot go negative (DB constraint + service check)
- ✅ Orders validated for stock before any state change
- ✅ Stock decremented atomically when order is created
- ✅ Stock restored when order is cancelled
- ✅ Total amount always calculated by backend (never trusted from client)
- ✅ Unit price snapshotted at order time (price changes don't affect old orders)

## Getting Started

```bash
# Install deps
poetry install

# Copy env
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## Docker

```bash
# From project root
docker compose up --build
```

API docs available at: `http://localhost:8000/docs`
