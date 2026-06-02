"""
crud.py
-------
Data Access Layer — all database read/write operations for the Expense model.

Design principles:
    - Pure database logic only. No HTTP, no response formatting.
    - Every function receives a `db: Session` injected by FastAPI.
    - Raises domain exceptions (from exceptions.py), not HTTP exceptions.
    - Callers (routers) are responsible for committing or rolling back.

Functions:
    create_expense      -- Insert a new expense record
    get_expense_by_id   -- Fetch one expense or raise ExpenseNotFoundError
    get_expenses        -- Fetch filtered + sorted list of expenses
    update_expense      -- Full replace of an existing expense
    delete_expense      -- Remove an expense from the database
"""

from datetime import date
from typing import Optional

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.exceptions import DatabaseOperationError, ExpenseNotFoundError
from app.models import Expense
from app.schemas import Category, ExpenseCreate, ExpenseFilters, ExpenseUpdate


# ── Create ────────────────────────────────────────────────────────────────────

def create_expense(db: Session, payload: ExpenseCreate) -> Expense:
    """
    Insert a new expense into the database.

    Args:
        db:      Active database session.
        payload: Validated ExpenseCreate schema.

    Returns:
        The newly created Expense ORM instance (with id and timestamps).

    Raises:
        DatabaseOperationError: If the insert fails at the DB level.
    """
    try:
        expense = Expense(**payload.model_dump_for_db())
        db.add(expense)
        db.commit()
        db.refresh(expense)  # Reload to get server-generated fields (id, created_at)
        return expense
    except Exception as exc:
        db.rollback()
        raise DatabaseOperationError("create_expense", str(exc)) from exc


# ── Read ──────────────────────────────────────────────────────────────────────

def get_expense_by_id(db: Session, expense_id: int) -> Expense:
    """
    Fetch a single expense by primary key.

    Args:
        db:         Active database session.
        expense_id: The integer ID to look up.

    Returns:
        The matching Expense ORM instance.

    Raises:
        ExpenseNotFoundError: If no expense exists with the given ID.
    """
    expense = db.get(Expense, expense_id)
    if not expense:
        raise ExpenseNotFoundError(expense_id)
    return expense


def get_expenses(db: Session, filters: ExpenseFilters) -> list[Expense]:
    """
    Fetch all expenses with optional filtering and fixed sort order.

    Filter logic (all filters are AND-combined):
        - category:   Exact match on the category field
        - search:     Case-insensitive partial match on title (LIKE %search%)
        - from_date:  Only expenses with date >= from_date
        - to_date:    Only expenses with date <= to_date

    Sort order: date DESC, then created_at DESC as a tiebreaker
    (so two expenses on the same day are ordered by insertion time).

    Args:
        db:      Active database session.
        filters: Validated ExpenseFilters query parameter model.

    Returns:
        A list of Expense ORM instances (may be empty).
    """
    query = db.query(Expense)

    # Category filter — exact match using enum value
    if filters.category:
        query = query.filter(Expense.category == filters.category.value)

    # Title search — case-insensitive partial match
    if filters.search and filters.search.strip():
        query = query.filter(
            Expense.title.ilike(f"%{filters.search.strip()}%")
        )

    # Date range filters
    if filters.from_date:
        query = query.filter(Expense.date >= filters.from_date)
    if filters.to_date:
        query = query.filter(Expense.date <= filters.to_date)

    # Sort: newest date first; tiebreaker = most recently created
    query = query.order_by(Expense.date.desc(), Expense.created_at.desc())

    return query.all()


# ── Update ────────────────────────────────────────────────────────────────────

def update_expense(db: Session, expense_id: int, payload: ExpenseUpdate) -> Expense:
    """
    Fully replace an existing expense's fields.

    This is a PUT (full replacement), not PATCH (partial update).
    All fields from the payload overwrite the stored values.

    Args:
        db:         Active database session.
        expense_id: ID of the expense to update.
        payload:    Validated ExpenseUpdate schema with new values.

    Returns:
        The updated Expense ORM instance.

    Raises:
        ExpenseNotFoundError:   If no expense with the given ID exists.
        DatabaseOperationError: If the update fails at the DB level.
    """
    expense = get_expense_by_id(db, expense_id)  # Raises 404 if not found
    try:
        # Apply all fields from the payload to the ORM model
        # Use model_dump_for_db() to get `date` key instead of `expense_date`
        for field, value in payload.model_dump_for_db().items():
            setattr(expense, field, value)
        db.commit()
        db.refresh(expense)
        return expense
    except Exception as exc:
        db.rollback()
        raise DatabaseOperationError("update_expense", str(exc)) from exc


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_expense(db: Session, expense_id: int) -> None:
    """
    Remove an expense from the database permanently.

    Args:
        db:         Active database session.
        expense_id: ID of the expense to delete.

    Returns:
        None (HTTP 204 No Content — nothing to return on success).

    Raises:
        ExpenseNotFoundError:   If no expense with the given ID exists.
        DatabaseOperationError: If the delete fails at the DB level.
    """
    expense = get_expense_by_id(db, expense_id)  # Raises 404 if not found
    try:
        db.delete(expense)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise DatabaseOperationError("delete_expense", str(exc)) from exc


# ── Aggregation (used by summary service) ─────────────────────────────────────

def get_monthly_totals_by_category(
    db: Session, year: int, month: int
) -> list[tuple[str, float]]:
    """
    Return per-category spending totals for a given year/month.

    Used exclusively by `services/summary_service.py`.

    Args:
        db:    Active database session.
        year:  Calendar year (e.g. 2026).
        month: Calendar month 1–12.

    Returns:
        List of (category, total_amount) tuples.
        Only categories with at least one expense in the period are returned;
        the summary service fills in zeros for the rest.
    """
    rows = (
        db.query(
            Expense.category,
            func.round(func.sum(Expense.amount), 2).label("total"),
        )
        .filter(
            extract("year", Expense.date) == year,
            extract("month", Expense.date) == month,
        )
        .group_by(Expense.category)
        .all()
    )
    return [(row.category, float(row.total)) for row in rows]
