# 🔧 Expense Tracker — Backend

FastAPI + SQLAlchemy + SQLite REST API for the Personal Expense Tracker.

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                   ← FastAPI app, CORS, lifespan, routers
│   ├── database.py               ← SQLAlchemy engine, session, get_db dependency
│   ├── models.py                 ← Expense ORM model (SQLAlchemy)
│   ├── schemas.py                ← Pydantic schemas + CategoryEnum
│   ├── crud.py                   ← Data access layer (all DB operations)
│   ├── exceptions.py             ← Custom exceptions + centralized handlers
│   ├── routers/
│   │   ├── expenses.py           ← CRUD endpoints: POST/GET/PUT/DELETE /expenses
│   │   └── summary.py            ← GET /summary/current-month
│   └── services/
│       └── summary_service.py    ← Business logic for monthly summary
├── requirements.txt
├── expenses.db                   ← SQLite DB (auto-created on first run)
└── README_BACKEND.md
```

---

## 🚀 Setup & Run

### Prerequisites
- Python >= 3.10 (tested on 3.14)

### Commands

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the development server
uvicorn app.main:app --reload --port 8000
```

### Verify it's running

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status": "ok", "api_version": "1.0.0"}
```

---

## 📖 Interactive API Docs

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Swagger UI (try all endpoints) |
| http://localhost:8000/redoc | ReDoc (readable API reference) |
| http://localhost:8000/openapi.json | Raw OpenAPI schema |

---

## 🔌 API Reference

### Expenses

| Method | Route              | Description                     | Body Required |
|--------|--------------------|---------------------------------|---------------|
| POST   | /expenses          | Create a new expense            | ✅ Yes        |
| GET    | /expenses          | List all (with optional filters)| ❌ No         |
| GET    | /expenses/{id}     | Get single expense by ID        | ❌ No         |
| PUT    | /expenses/{id}     | Fully update an expense         | ✅ Yes        |
| DELETE | /expenses/{id}     | Delete an expense               | ❌ No         |

### Summary

| Method | Route                     | Description                     |
|--------|---------------------------|---------------------------------|
| GET    | /summary/current-month    | Monthly summary with breakdown  |

---

## 📝 Sample API Requests & Responses

### ✅ Create an Expense

**Request:**
```http
POST /expenses
Content-Type: application/json

{
  "title": "Weekly groceries",
  "amount": 45.50,
  "category": "Food",
  "date": "2026-06-02",
  "note": "Vegetables and fruits"
}
```

**Response `201 Created`:**
```json
{
  "id": 1,
  "title": "Weekly groceries",
  "amount": 45.50,
  "category": "Food",
  "date": "2026-06-02",
  "note": "Vegetables and fruits",
  "created_at": "2026-06-02T10:00:00",
  "updated_at": "2026-06-02T10:00:00"
}
```

---

### ✅ List Expenses with Filters

**Request:**
```http
GET /expenses?category=Food&from_date=2026-06-01&to_date=2026-06-30&search=grocer
```

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "title": "Weekly groceries",
    "amount": 45.50,
    "category": "Food",
    "date": "2026-06-02",
    "note": "Vegetables and fruits",
    "created_at": "2026-06-02T10:00:00",
    "updated_at": "2026-06-02T10:00:00"
  }
]
```

---

### ✅ Get Expense by ID

**Request:**
```http
GET /expenses/1
```

**Response `200 OK`:** *(same as above, single object)*

**Response `404 Not Found`:**
```json
{
  "error": "ExpenseNotFound",
  "message": "Expense with id 99 was not found",
  "detail": { "expense_id": 99 }
}
```

---

### ✅ Update an Expense

**Request:**
```http
PUT /expenses/1
Content-Type: application/json

{
  "title": "Big grocery run",
  "amount": 89.00,
  "category": "Food",
  "date": "2026-06-02",
  "note": "Monthly stock-up"
}
```

**Response `200 OK`:** *(updated expense object)*

---

### ✅ Delete an Expense

**Request:**
```http
DELETE /expenses/1
```

**Response `204 No Content`:** *(empty body)*

---

### ✅ Monthly Summary

**Request:**
```http
GET /summary/current-month
# Or specify a month:
GET /summary/current-month?year=2026&month=6
```

**Response `200 OK`:**
```json
{
  "year": 2026,
  "month": 6,
  "total_spent": 342.75,
  "category_breakdown": {
    "Food": 120.00,
    "Transport": 45.00,
    "Shopping": 0.00,
    "Bills": 177.75,
    "Entertainment": 0.00,
    "Other": 0.00
  }
}
```

---

### ❌ Validation Error (example)

**Request:**
```http
POST /expenses
Content-Type: application/json

{ "title": "", "amount": -5, "category": "Lunch", "date": "2026-06-02" }
```

**Response `422 Unprocessable Entity`:**
```json
{
  "error": "ValidationError",
  "message": "Request validation failed",
  "detail": [
    { "field": "title", "message": "Title cannot be blank or contain only whitespace" },
    { "field": "amount", "message": "Input should be greater than 0" },
    { "field": "category", "message": "Input should be 'Food', 'Transport', 'Shopping', 'Bills', 'Entertainment' or 'Other'" }
  ]
}
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE expenses (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    title      VARCHAR(100) NOT NULL,
    amount     FLOAT        NOT NULL,
    category   VARCHAR(20)  NOT NULL,
    date       DATE         NOT NULL,
    note       TEXT,
    created_at DATETIME     NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    updated_at DATETIME     NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE INDEX idx_expenses_title    ON expenses(title);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_date     ON expenses(date);
CREATE INDEX idx_expenses_date_category ON expenses(date, category);
```

---

## ✅ Validation Rules

| Field    | Rules |
|----------|-------|
| title    | Required, 1–100 chars, no blank/whitespace-only |
| amount   | Required, > 0, rounded to 2 decimal places |
| category | Required, one of: Food, Transport, Shopping, Bills, Entertainment, Other |
| date     | Required, valid ISO date (YYYY-MM-DD) |
| note     | Optional, max 500 chars, stripped of leading/trailing whitespace |

---

## ⚖️ Architecture Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| CRUD layer | `crud.py` | Separates DB logic from HTTP routing |
| Service layer | `services/summary_service.py` | Business logic isolated from both DB and HTTP |
| Exception handling | Centralized in `exceptions.py` | Single place to change error format |
| PUT vs PATCH | Full PUT | Form always sends all fields; simpler to implement |
| DB init | `create_all()` in lifespan | Zero-config for local development |
| SQLite WAL mode | Enabled | Better read concurrency |
