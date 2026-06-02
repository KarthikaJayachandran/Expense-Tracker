"""
main.py
-------
FastAPI application entry point.

Responsibilities:
    1. Create the FastAPI application instance with metadata.
    2. Register all exception handlers (centralized in exceptions.py).
    3. Configure CORS middleware for the frontend dev server.
    4. Initialize the SQLite database (create tables if they don't exist).
    5. Include all routers.
    6. Expose a health check endpoint.

Run with:
    uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.exceptions import register_exception_handlers
from app.routers import expenses, summary


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    On startup:  Create all database tables if they don't already exist.
                 This is safe to call multiple times (uses CREATE TABLE IF NOT EXISTS).
    On shutdown: Any cleanup logic goes here (connection pool teardown, etc.)
    """
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown (nothing to clean up for SQLite)


# ── Application Instance ──────────────────────────────────────────────────────

app = FastAPI(
    title="Personal Expense Tracker API",
    description=(
        "A clean REST API for managing personal expenses.\n\n"
        "## Features\n"
        "- **CRUD** operations on expenses\n"
        "- **Filtering** by category, date range, and title search\n"
        "- **Monthly Summary** with per-category spending breakdown\n"
        "- **Validation** via Pydantic with descriptive error messages\n"
        "- **Centralized error handling** with consistent JSON error shapes\n\n"
        "## Categories\n"
        "`Food` · `Transport` · `Shopping` · `Bills` · `Entertainment` · `Other`"
    ),
    version="1.0.0",
    contact={
        "name": "Expense Tracker",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
    # Customize Swagger UI
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ── Exception Handlers ────────────────────────────────────────────────────────

register_exception_handlers(app)


# ── CORS Middleware ───────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    # In production, replace with the specific frontend domain.
    # For local development, Vite runs on port 5173.
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(expenses.router)
app.include_router(summary.router)


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Returns HTTP 200 with status 'ok' if the API is running.",
    response_model=dict,
)
def health_check() -> dict:
    """
    Simple health check endpoint.
    Use this to verify the API server is reachable before running tests.
    """
    return {"status": "ok", "api_version": "1.0.0"}
