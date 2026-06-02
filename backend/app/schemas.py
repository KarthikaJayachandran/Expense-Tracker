"""
schemas.py
----------
Pydantic v2 schemas for request validation and response serialization.
Compatible with Pydantic >= 2.10 and Python 3.14.

NOTE on Python 3.14 compatibility:
    A field named `date: date` causes Pydantic to fail because the field name
    shadows the `date` type annotation at class-body evaluation time.
    We use `expense_date` internally with alias="date" so the JSON API still
    uses the key "date" as expected by clients.
"""

from datetime import date as date_type
from datetime import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ── Category Enum ─────────────────────────────────────────────────────────────

class Category(str, Enum):
    """Valid expense categories. Adding new categories requires a DB migration."""
    FOOD = "Food"
    TRANSPORT = "Transport"
    SHOPPING = "Shopping"
    BILLS = "Bills"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"


# ── Base Schema (shared validation logic) ─────────────────────────────────────

class ExpenseBase(BaseModel):
    """
    Shared fields and validators used by both Create and Update schemas.
    All business validation rules live here as the single source of truth.

    Field naming note:
        `expense_date` is the Python attribute name; JSON key is "date" via alias.
        This avoids Python 3.14 name-shadowing issue with `date: date`.
    """

    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Short descriptive title for the expense",
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Expense amount — must be a positive number greater than zero",
    )
    category: Category = Field(
        ...,
        description="Expense category. Must be one of the predefined values.",
    )
    expense_date: date_type = Field(
        default_factory=date_type.today,
        alias="date",
        description="Date the expense occurred (ISO 8601 format: YYYY-MM-DD). Defaults to today.",
    )
    note: Union[str, None] = Field(
        default=None,
        max_length=500,
        description="Optional additional details about the expense",
    )

    # ── Field Validators ──────────────────────────────────────────────────────

    @field_validator("title", mode="before")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        """Strip whitespace and reject titles that are only whitespace."""
        stripped = str(v).strip()
        if not stripped:
            raise ValueError("Title cannot be blank or contain only whitespace")
        return stripped

    @field_validator("amount", mode="before")
    @classmethod
    def round_amount_to_two_decimals(cls, v: float) -> float:
        """Normalize amount to 2 decimal places to avoid floating-point drift."""
        return round(float(v), 2)

    @field_validator("note", mode="before")
    @classmethod
    def clean_note(cls, v: Union[str, None]) -> Union[str, None]:
        """Strip whitespace from note; return None if result is empty."""
        if v is None:
            return None
        stripped = str(v).strip()
        return stripped if stripped else None

    def model_dump_for_db(self) -> dict:
        """
        Return a dict with the actual DB column name `date` (not `expense_date`).
        Used by CRUD functions when creating/updating ORM model instances.
        """
        data = self.model_dump(by_alias=False)
        # Rename expense_date → date to match the SQLAlchemy column name
        data["date"] = data.pop("expense_date")
        return data


# ── Request Schemas ───────────────────────────────────────────────────────────

class ExpenseCreate(ExpenseBase):
    """Schema for POST /expenses — creates a new expense."""
    pass


class ExpenseUpdate(ExpenseBase):
    """
    Schema for PUT /expenses/{id} — full replacement of an expense.
    Inherits all fields and validators from ExpenseBase.
    """
    pass


# ── Response Schema ───────────────────────────────────────────────────────────

class ExpenseResponse(BaseModel):
    """
    Schema returned by all endpoints.
    Declares all fields directly (no inheritance) to avoid the date name clash.
    `from_attributes=True` enables ORM mode.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(..., description="Unique identifier")
    title: str = Field(..., description="Expense title")
    amount: float = Field(..., description="Expense amount")
    category: Category = Field(..., description="Expense category")
    date: Union[date_type, None] = Field(  # Reading FROM ORM — no shadowing here
        default=None,
        description="Date the expense occurred",
    )
    note: Union[str, None] = Field(default=None, description="Optional note")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last-updated timestamp")


# ── Filter / Query Parameter Schema ──────────────────────────────────────────

class ExpenseFilters(BaseModel):
    """
    Query parameters for GET /expenses.
    All fields are optional — omitting a filter means no restriction on that field.
    """

    category: Union[Category, None] = Field(
        default=None,
        description="Filter by expense category",
    )
    search: Union[str, None] = Field(
        default=None,
        max_length=100,
        description="Partial case-insensitive match on title",
    )
    from_date: Union[date_type, None] = Field(
        default=None,
        description="Return expenses on or after this date (YYYY-MM-DD)",
    )
    to_date: Union[date_type, None] = Field(
        default=None,
        description="Return expenses on or before this date (YYYY-MM-DD)",
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> "ExpenseFilters":
        """Ensure from_date is not later than to_date when both are provided."""
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError(
                f"from_date ({self.from_date}) must be on or before "
                f"to_date ({self.to_date})"
            )
        return self


# ── Summary Schemas ───────────────────────────────────────────────────────────

class MonthlySummaryResponse(BaseModel):
    """Response schema for GET /summary/current-month."""

    year: int = Field(..., description="Calendar year of the summary")
    month: int = Field(..., description="Calendar month of the summary (1-12)")
    total_spent: float = Field(..., description="Total amount spent in the month")
    category_breakdown: dict = Field(
        ..., description="Per-category spending totals (all 6 categories always present)"
    )
