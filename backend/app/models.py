"""
models.py
---------
SQLAlchemy ORM model for the `expenses` table.
Defines column types, constraints, and indexes for efficient querying.
"""

from datetime import date, datetime
from sqlalchemy import String, Float, Text, Date, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Expense(Base):
    """
    ORM model representing a single expense record.

    Columns:
        id          -- Auto-incrementing primary key
        title       -- Short description (max 100 chars)
        amount      -- Positive float, stored as 2 decimal precision
        category    -- One of 6 fixed categories (enforced by Pydantic)
        date        -- The date the expense occurred (ISO date)
        note        -- Optional free-text note (max 500 chars)
        created_at  -- Server-side timestamp when record was created
        updated_at  -- Server-side timestamp, updated on every change
    """

    __tablename__ = "expenses"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Core fields
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Audit timestamps — set by the database server, not application code
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Composite index to speed up the most common query:
    # "get all expenses for a given month, sorted by date DESC"
    __table_args__ = (
        Index("idx_expenses_date_category", "date", "category"),
    )

    def __repr__(self) -> str:
        return (
            f"<Expense id={self.id} title={self.title!r} "
            f"amount={self.amount} category={self.category} date={self.date}>"
        )
