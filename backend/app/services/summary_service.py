"""
services/summary_service.py
---------------------------
Business logic layer for the Monthly Summary feature.

Responsibility:
    Orchestrate data retrieval (via crud.py) and apply business rules
    to produce the MonthlySummaryResponse. Keeps the router thin and
    the business logic testable in isolation.

Why a service layer?
    The summary is not a simple CRUD operation — it requires:
      1. Defaulting year/month to "current" when not provided.
      2. Aggregating per-category totals from raw DB rows.
      3. Ensuring ALL 6 categories are always present (even with £0).
      4. Computing a grand total by summing category totals.
    This logic belongs in a service, not a router or CRUD function.
"""

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.schemas import Category, MonthlySummaryResponse


def get_monthly_summary(
    db: Session,
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> MonthlySummaryResponse:
    """
    Build the monthly summary for a given year and month.

    Args:
        db:    Active database session (injected by FastAPI).
        year:  Target year. Defaults to the current calendar year.
        month: Target month (1–12). Defaults to the current calendar month.

    Returns:
        MonthlySummaryResponse with total_spent and per-category breakdown.
        All 6 categories are always present; categories with no spending show 0.0.

    Business rules:
        - If year/month are not provided, the current date is used.
        - Amounts are rounded to 2 decimal places.
        - Grand total = sum of all category totals (not a separate DB query).
    """
    today = date.today()
    target_year = year if year is not None else today.year
    target_month = month if month is not None else today.month

    # Fetch raw aggregated rows from the database
    # Returns only categories that have at least one expense this month
    raw_rows: list[tuple[str, float]] = crud.get_monthly_totals_by_category(
        db=db,
        year=target_year,
        month=target_month,
    )

    # Build a category → amount mapping from the raw rows
    totals_by_category: dict[str, float] = {cat: amount for cat, amount in raw_rows}

    # Ensure all 6 categories are always represented (missing = 0.0)
    # This guarantees a consistent response shape regardless of data sparsity
    all_categories: dict[str, float] = {
        cat.value: totals_by_category.get(cat.value, 0.0)
        for cat in Category
    }

    # Grand total = sum of per-category amounts (avoids a second DB query)
    grand_total = round(sum(all_categories.values()), 2)

    # Build the breakdown as a plain dict — matches MonthlySummaryResponse schema
    breakdown = {
        "Food": all_categories["Food"],
        "Transport": all_categories["Transport"],
        "Shopping": all_categories["Shopping"],
        "Bills": all_categories["Bills"],
        "Entertainment": all_categories["Entertainment"],
        "Other": all_categories["Other"],
    }

    return MonthlySummaryResponse(
        year=target_year,
        month=target_month,
        total_spent=grand_total,
        category_breakdown=breakdown,
    )
