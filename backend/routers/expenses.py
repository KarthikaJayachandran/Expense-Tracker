from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from database import get_db
from models import Expense
from schemas import (
    Category,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    MonthlySummaryResponse,
)

router = APIRouter(prefix="/expenses", tags=["expenses"])

# ── All valid categories (for summary zeroing) ────────────────────────────────
ALL_CATEGORIES = [c.value for c in Category]


# ── Helper ────────────────────────────────────────────────────────────────────

def get_expense_or_404(expense_id: int, db: Session) -> Expense:
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id {expense_id} not found",
        )
    return expense


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/summary/monthly", response_model=MonthlySummaryResponse)
def get_monthly_summary(
    year: Optional[int] = Query(None, ge=2000, le=9999),
    month: Optional[int] = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
):
    """Return total spend and category breakdown for a given month."""
    from datetime import date as date_cls
    today = date_cls.today()
    target_year = year or today.year
    target_month = month or today.month

    rows = (
        db.query(Expense.category, func.sum(Expense.amount).label("total"))
        .filter(
            extract("year", Expense.date) == target_year,
            extract("month", Expense.date) == target_month,
        )
        .group_by(Expense.category)
        .all()
    )

    by_category: dict[str, float] = {cat: 0.0 for cat in ALL_CATEGORIES}
    grand_total = 0.0
    for row in rows:
        by_category[row.category] = round(row.total, 2)
        grand_total += row.total

    return MonthlySummaryResponse(
        year=target_year,
        month=target_month,
        total=round(grand_total, 2),
        by_category=by_category,
    )


@router.get("", response_model=list[ExpenseResponse])
def list_expenses(
    category: Optional[Category] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
    db: Session = Depends(get_db),
):
    """Return all expenses with optional filters, sorted latest first."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date_from must be less than or equal to date_to",
        )

    query = db.query(Expense)

    if category:
        query = query.filter(Expense.category == category.value)
    if date_from:
        query = query.filter(Expense.date >= date_from)
    if date_to:
        query = query.filter(Expense.date <= date_to)
    if search and search.strip():
        query = query.filter(Expense.title.ilike(f"%{search.strip()}%"))

    expenses = query.order_by(Expense.date.desc(), Expense.created_at.desc()).all()
    return expenses


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense record."""
    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Fetch a single expense by ID."""
    return get_expense_or_404(expense_id, db)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)
):
    """Fully replace an existing expense."""
    expense = get_expense_or_404(expense_id, db)
    for field, value in payload.model_dump().items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense by ID."""
    expense = get_expense_or_404(expense_id, db)
    db.delete(expense)
    db.commit()
