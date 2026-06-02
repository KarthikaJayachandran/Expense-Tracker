"""
database.py
-----------
SQLAlchemy engine setup, session factory, and the `get_db` dependency
used by FastAPI's dependency injection system.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# SQLite database file stored in the backend root directory
DATABASE_URL = "sqlite:///./expenses.db"

# `check_same_thread=False` is required for SQLite with FastAPI
# because requests may be handled by different threads.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # Set True to log all SQL queries during development
)

# Enable WAL mode for better SQLite concurrency (multiple readers, one writer)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Session factory — each request gets its own session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""
    pass


def get_db():
    """
    FastAPI dependency that provides a database session per request.
    Guarantees the session is closed after the request completes,
    even if an exception is raised.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
