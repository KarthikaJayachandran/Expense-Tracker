"""
routers/summary.py
------------------
FastAPI router for the Monthly Summary endpoint.

Routes:
    GET /summary/current-month   -- Spending summary for the current (or specified) month

Design:
    - Delegates all computation to `services/summary_service.py`.
    - Supports optional `year` and `month` query parameters to query any month.
    - Defaults to the current calendar month when no params are provided.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MonthlySummaryResponse
from app.services import summary_service

router = APIRouter(
    prefix="/summary",
    tags=["Summary"],
)


@router.get(
    "/current-month",
    response_model=MonthlySummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get monthly spending summary",
    description=(
        "Returns total spending and a per-category breakdown for the specified month. "
        "Defaults to the current calendar month if year/month are not provided. "
        "All 6 categories are always present in the response — categories "
        "with no spending show 0.0."
    ),
)
def get_monthly_summary(
    year: Optional[int] = Query(
        default=None,
        ge=2000,
        le=9999,
        description="Calendar year (e.g. 2026). Defaults to current year.",
    ),
    month: Optional[int] = Query(
        default=None,
        ge=1,
        le=12,
        description="Calendar month 1–12 (e.g. 6 for June). Defaults to current month.",
    ),
    db: Session = Depends(get_db),
) -> MonthlySummaryResponse:
    """
    Retrieve a spending summary for a calendar month.

    - **year**: Optional. Defaults to the current year.
    - **month**: Optional (1–12). Defaults to the current month.

    **Response always includes**:
    - `total_spent`: Sum of all expenses in the month
    - `category_breakdown`: Per-category totals for all 6 categories
      (categories with no spending show `0.0`)

    **Example response** (June 2026):
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
    """
    return summary_service.get_monthly_summary(db=db, year=year, month=month)
