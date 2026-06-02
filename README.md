# Inventory & Order Management — Backend

A production-ready FastAPI + PostgreSQL REST API for managing inventory and orders with user authentication, role-based access, and business logic enforcement. Built with **SOLID principles**, async/await patterns, and clean architecture.

**Tech Stack:** FastAPI · SQLAlchemy (async) · PostgreSQL · Pydantic · JWT Auth · Alembic Migrations · Poetry

---

## 📋 Project Structure

```
backend/
├── alembic/                          # Database migrations
│   ├── versions/                     # Migration scripts
│   │   └── ff6f6104d71a_initial.py  # Initial schema
│   ├── env.py                        # Alembic configuration
│   └── script.py.mako                # Migration template
│
├── app/
│   ├── main.py                       # FastAPI app factory & startup
│   │
│   ├── api/v1/
│   │   ├── router.py                 # Route aggregator (includes all routers)
│   │   └── endpoints/                # HTTP controllers (thin layer)
│   │       ├── auth.py               # Register, login, token refresh
│   │       ├── users.py              # User CRUD & profile management
│   │       ├── products.py           # Product CRUD & inventory
│   │       ├── orders.py             # Order CRUD, checkout, cancellation
│   │       └── dashboard.py          # Analytics & reporting
│   │
│   ├── core/                         # Cross-cutting concerns
│   │   ├── config.py                 # Pydantic Settings (env vars, secrets)
│   │   ├── dependencies.py           # FastAPI dependency injection providers
│   │   ├── exception_handlers.py     # Global error handling & response formatting
│   │   └── security.py               # Password hashing, JWT token creation/validation
│   │
│   ├── db/
│   │   └── database.py               # Async SQLAlchemy engine & session factory
│   │
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── user.py                   # User(id, email, role, password, ...)
│   │   ├── product.py                # Product(id, sku, name, price, stock, seller_id)
│   │   └── order.py                  # Order & OrderItem (relationships, totals)
│   │
│   ├── schemas/                      # Pydantic request/response DTOs
│   │   ├── auth.py                   # LoginRequest, RegisterRequest, TokenResponse
│   │   ├── product.py                # ProductCreate, ProductResponse, etc.
│   │   ├── order.py                  # OrderCreate, OrderResponse, OrderItem
│   │   ├── user.py                   # UserResponse, UserUpdate
│   │   └── dashboard.py              # DashboardMetrics, OrderStats, etc.
│   │
│   ├── services/                     # Business logic layer (domain services)
│   │   ├── auth_service.py           # Register, login, password verification
│   │   ├── user_service.py           # User CRUD, profile updates, role checks
│   │   ├── product_service.py        # Product CRUD, SKU validation, stock queries
│   │   ├── order_service.py          # Order creation, stock validation, cancellation
│   │   └── dashboard_service.py      # Analytics aggregation, metrics computation
│   │
│   ├── repositories/                 # Data access layer (Repository Pattern)
│   │   ├── base.py                   # AbstractRepository[T] generic base class
│   │   ├── user_repository.py        # User queries (get_by_email, get_by_id, etc.)
│   │   ├── product_repository.py     # Product queries, stock updates, SKU lookups
│   │   └── order_repository.py       # Order queries, status updates, item retrieval
│   │
│   └── exceptions/
│       └── app_exceptions.py         # Custom exceptions (BadRequest, NotFound, etc.)
│
├── pyproject.toml                    # Poetry dependencies & project metadata
├── alembic.ini                       # Alembic configuration
├── entrypoint.sh                     # Docker startup script
├── Dockerfile                        # Container image definition
└── README.md                         # This file
```

---

## 🏗️ Architecture & Design Patterns

### Layered Architecture
```
HTTP Request
    ↓
[API Endpoints] — Route parsing, request validation
    ↓
[Services] — Business logic, domain rules, validation
    ↓
[Repositories] — Data access, SQL queries
    ↓
[Database] — Persistence
```

## 📁 Core Modules Explained

### `app/main.py`
- Creates FastAPI app instance
- Registers middleware (CORS)
- Registers global exception handlers
- Includes API routers
- Provides `/health` endpoint

### `app/core/config.py`
- Loads environment variables via Pydantic Settings
- Centralizes configuration (DB URL, JWT secrets, CORS origins, etc.)
- Single source of truth for app constants

### `app/core/security.py`
- `hash_password(plain)` — bcrypt hashing
- `verify_password(plain, hashed)` — password comparison
- `create_access_token(subject, extra_claims)` — JWT generation
- `verify_token(token)` — JWT validation

### `app/core/dependencies.py`
- FastAPI dependency providers
- `get_db()` — async database session factory
- `get_current_user()` — JWT token extraction & validation
- Service factory functions (`get_auth_service()`, `get_order_service()`, etc.)

### `app/core/exception_handlers.py`
- Registers custom exception handlers
- Converts domain exceptions to HTTP responses
- Ensures consistent error format across API

### `app/db/database.py`
- AsyncSession factory for SQLAlchemy
- Database engine initialization
- Base class for all ORM models

### `app/models/*.py`

**User** (`user.py`)
```
- id (PK)
- email (unique)
- hashed_password
- full_name
- phone_number
- role (admin, seller, customer)
- is_active
- created_at
- Relationships: products (as seller), orders (as customer)
```

**Product** (`product.py`)
```
- id (PK)
- user_id (FK → User, seller)
- name
- sku (unique)
- price (Decimal, ≥ 0)
- quantity_in_stock (≥ 0, enforced by CHECK constraint)
- Relationships: seller (User), order_items (OrderItem)
```

**Order** (`order.py`)
```
- id (PK)
- user_id (FK → User, customer)
- status (pending, confirmed, cancelled)
- total_amount (Decimal, calculated by backend)
- created_at, updated_at
- Relationships: customer (User), order_items (OrderItem cascade delete)

OrderItem:
- id (PK)
- order_id (FK → Order, CASCADE delete)
- product_id (FK → Product, RESTRICT delete)
- quantity
- unit_price (snapshot at order time, not affected by price changes)
```

### `app/schemas/*.py`
Request/response DTOs with validation:
- `auth.py` — LoginRequest, RegisterRequest, TokenResponse, UserResponse
- `product.py` — ProductCreate, ProductUpdate, ProductResponse, ProductInOrder
- `order.py` — OrderCreate, OrderItemCreate, OrderResponse, OrderSummary
- `user.py` — UserResponse, UserUpdate
- `dashboard.py` — DashboardMetrics, OrderStats

### `app/services/*.py`
Domain business logic (no HTTP concerns):

**AuthService** (`auth_service.py`)
- Register user (email uniqueness check, password hashing)
- Login (credentials validation, JWT generation)

**UserService** (`user_service.py`)
- CRUD operations
- Profile updates
- Role-based checks (admin, seller, customer)

**ProductService** (`product_service.py`)
- Create/update/delete products
- SKU uniqueness enforcement
- Stock level queries
- Only sellers can manage products

**OrderService** (`order_service.py`)
- Create order (validate customer, check stock for ALL items before committing)
- Calculate order total atomically
- Snapshot unit prices at order time
- Decrement stock on order creation
- Restore stock on cancellation
- Status transitions (pending → confirmed → cancelled)

**DashboardService** (`dashboard_service.py`)
- Aggregate order metrics
- Calculate total revenue
- Track order counts by status
- User activity analysis

### `app/repositories/*.py`
Data access layer with Repository Pattern:

**AbstractRepository[T]** (`base.py`)
- Generic base class enforcing interface
- Methods: `get_by_id()`, `get_all()`, `create()`, `delete()`

**UserRepository**
- `get_by_email(email)` — unique email lookup
- Inherits CRUD from base

**ProductRepository**
- `get_by_sku(sku)` — SKU lookup
- `get_by_seller(seller_id)` — products by seller
- `update_stock(product_id, quantity_delta)` — atomic stock updates
- Inherits CRUD from base

**OrderRepository**
- `get_by_status(status)` — orders by status
- `get_customer_orders(user_id)` — customer order history
- `update_status(order_id, status)` — status transitions
- Inherits CRUD from base

### `app/api/v1/router.py`
Route aggregator — includes all endpoint routers:
```
/api/v1/auth     → auth.router
/api/v1/products → products.router
/api/v1/orders   → orders.router
/api/v1/users    → users.router
/api/v1/dashboard → dashboard.router
```

### `app/api/v1/endpoints/*.py`
Thin HTTP controllers (request parsing → service call → response):

**auth.py**
- `POST /auth/register` — create account
- `POST /auth/login` — get JWT token
- `POST /auth/refresh` — refresh token

**users.py**
- `GET /users/{id}` — user profile
- `PUT /users/{id}` — update profile
- `GET /users` — list all users (admin only)
- `DELETE /users/{id}` — delete user (admin only)

**products.py**
- `POST /products` — create product (seller only)
- `GET /products` — list all products
- `GET /products/{id}` — product details
- `PUT /products/{id}` — update product (seller only)
- `DELETE /products/{id}` — delete product (seller only)
- `GET /products/sku/{sku}` — product by SKU

**orders.py**
- `POST /orders` — create order (validate stock, decrement inventory)
- `GET /orders` — list user's orders
- `GET /orders/{id}` — order details
- `PUT /orders/{id}/status` — change status (pending → confirmed → cancelled)
- `POST /orders/{id}/cancel` — cancel order (restore stock)

**dashboard.py**
- `GET /dashboard/metrics` — order counts, revenue, user stats
- `GET /dashboard/top-products` — best-selling products
- `GET /dashboard/sales-trend` — revenue over time

---

## 🔒 Business Logic & Constraints

✅ **Email Uniqueness** — Enforced at service layer + DB constraint  
✅ **SKU Uniqueness** — Enforced at service layer + DB unique index  
✅ **Stock Non-Negative** — CHECK constraint at DB level + service validation  
✅ **Stock Validation Before Order** — ALL items validated before any database mutation  
✅ **Atomic Stock Decrement** — Stock reduced when order is created  
✅ **Stock Restoration** — Stock refunded when order is cancelled  
✅ **Total Amount Calculated by Backend** — Never trusted from client  
✅ **Unit Price Snapshot** — Captured at order time, price changes don't affect old orders  
✅ **Role-Based Access** — Users, sellers, admins have different permissions  
✅ **Password Security** — Bcrypt hashing + salt  
✅ **JWT Token Auth** — 24-hour expiration, HS256 signing  

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Poetry (package manager)

### Installation

```bash
# Install dependencies
poetry install

# Create .env file (copy from example)
cp .env.example .env

# Update DATABASE_URL in .env with your PostgreSQL credentials
# Example: postgresql+asyncpg://postgres:password@localhost:5432/inventory_db

# Run database migrations
alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/health`

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker compose up --build

# Or build image only
docker build -t inventory-api:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@db:5432/inventory_db" \
  -e JWT_SECRET_KEY="your-secret-key" \
  inventory-api:latest
```

---

## 📦 Dependencies

**Production:**
- `fastapi` — Web framework
- `uvicorn[standard]` — ASGI server
- `sqlalchemy` — ORM
- `asyncpg` — PostgreSQL async driver
- `pydantic` — Data validation
- `pydantic-settings` — Environment configuration
- `python-jose[cryptography]` — JWT tokens
- `passlib[bcrypt]` — Password hashing
- `alembic` — Database migrations

**Development:**
- `pytest` — Unit testing
- `pytest-asyncio` — Async test support
- `httpx` — HTTP client for testing
- `pytest-cov` — Coverage reports

---

## 🔧 Environment Variables

Create `.env` file:
```
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/inventory_db
DATABASE_SYNC_URL=postgresql://postgres:password@localhost:5432/inventory_db

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# App
APP_ENV=development
APP_TITLE=Inventory & Order Management API
APP_VERSION=1.0.0
```

---

## 📝 Example API Flows

### 1. User Registration & Login
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure123",
    "full_name": "John Doe",
    "role": "customer"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure123"
  }'
# Response: { "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...", "token_type": "bearer" }
```

### 2. Create Product (Seller)
```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "sku": "LAPTOP-001",
    "price": 999.99,
    "quantity_in_stock": 10
  }'
```

### 3. Place Order (Customer)
```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ]
  }'
```

---

## 📊 Migration & Database Schema

Run migrations with Alembic:
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply pending migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1

# View migration history
alembic history
```

---


## 👤 Author

Shubham Mane — Production-ready inventory management system
