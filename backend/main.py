from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import expenses

# ── Create DB tables on startup ───────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Personal Expense Tracker API",
    description="REST API for managing personal expenses",
    version="1.0.0",
)

# ── CORS — allow Vite dev server ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(expenses.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
