"""
routers/expenses.py
-------------------
FastAPI router for all expense CRUD endpoints.

Routes:
    POST   /expenses          -- Create a new expense
    GET    /expenses          -- List all expenses (with optional filters)
    GET    /expenses/{id}     -- Get a single expense by ID
    PUT    /expenses/{id}     -- Fully replace an existing expense
    DELETE /expenses/{id}     -- Delete an expense

Design:
    - Routers are intentionally thin: validate input, call crud, return response.
    - All business logic and data access are delegated to crud.py.
    - Dependency injection provides the DB session per request.
    - Tags and response_model enable clean Swagger UI documentation.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app import crud
from app.database import get_db
from app.schemas import (
    Category,
    ExpenseCreate,
    ExpenseFilters,
    ExpenseResponse,
    ExpenseUpdate,
)

# All routes in this router are prefixed with /expenses
router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


# ── POST /expenses ────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense",
    description=(
        "Add a new expense record. "
        "Title is required and must not be blank. "
        "Amount must be greater than zero. "
        "Category must be one of: Food, Transport, Shopping, Bills, Entertainment, Other."
    ),
)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
) -> ExpenseResponse:
    """
    Create a new expense record.

    - **title**: Required, 1–100 chars, whitespace-stripped
    - **amount**: Required, positive float, rounded to 2 decimal places
    - **category**: Must be one of the 6 valid categories
    - **date**: ISO date (YYYY-MM-DD)
    - **note**: Optional, max 500 chars
    """
    return crud.create_expense(db=db, payload=payload)


# ── GET /expenses ─────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[ExpenseResponse],
    summary="List all expenses",
    description=(
        "Retrieve all expenses, sorted by date descending (newest first). "
        "Optionally filter by category, title search, or date range."
    ),
)
def list_expenses(
    # Query parameters are declared individually for Swagger UI visibility
    category: Optional[Category] = Query(
        default=None,
        description="Filter by expense category",
    ),
    search: Optional[str] = Query(
        default=None,
        max_length=100,
        description="Partial case-insensitive search on title",
    ),
    from_date: Optional[date] = Query(
        default=None,
        description="Return expenses on or after this date (YYYY-MM-DD)",
    ),
    to_date: Optional[date] = Query(
        default=None,
        description="Return expenses on or before this date (YYYY-MM-DD)",
    ),
    db: Session = Depends(get_db),
) -> list[ExpenseResponse]:
    """
    List all expenses with optional filtering:

    - **category**: Exact match (e.g. `Food`, `Transport`)
    - **search**: Partial match on title (case-insensitive)
    - **from_date**: Only include expenses on or after this date
    - **to_date**: Only include expenses on or before this date

    All filters are optional and combinable.
    Results are always sorted: newest date first, then newest creation time.
    """
    # Build the filter model — Pydantic validates date range consistency
    filters = ExpenseFilters(
        category=category,
        search=search,
        from_date=from_date,
        to_date=to_date,
    )
    return crud.get_expenses(db=db, filters=filters)


# ── GET /expenses/{id} ────────────────────────────────────────────────────────

@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Get a single expense by ID",
    responses={
        404: {
            "description": "Expense not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "ExpenseNotFound",
                        "message": "Expense with id 99 was not found",
                        "detail": {"expense_id": 99},
                    }
                }
            },
        }
    },
)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
) -> ExpenseResponse:
    """
    Retrieve a single expense by its unique ID.

    Returns **404 Not Found** if no expense with the given ID exists.
    """
    return crud.get_expense_by_id(db=db, expense_id=expense_id)


# ── PUT /expenses/{id} ────────────────────────────────────────────────────────

@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Update (fully replace) an expense",
    description=(
        "Perform a full replacement of all expense fields. "
        "All fields are required — this is PUT, not PATCH. "
        "Returns 404 if the expense does not exist."
    ),
    responses={
        404: {"description": "Expense not found"},
        422: {"description": "Validation error"},
    },
)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
) -> ExpenseResponse:
    """
    Fully replace an existing expense's fields.

    All fields in the request body are required.
    Returns the updated expense on success.
    Returns **404 Not Found** if the ID does not exist.
    """
    return crud.update_expense(db=db, expense_id=expense_id, payload=payload)


# ── DELETE /expenses/{id} ─────────────────────────────────────────────────────

@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense",
    description="Permanently delete an expense by ID. Returns 204 on success.",
    responses={
        204: {"description": "Expense deleted successfully"},
        404: {"description": "Expense not found"},
    },
)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete an expense permanently.

    Returns **204 No Content** on success (no response body).
    Returns **404 Not Found** if the ID does not exist.
    """
    crud.delete_expense(db=db, expense_id=expense_id)
