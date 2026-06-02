from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Category(str, Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    SHOPPING = "Shopping"
    BILLS = "Bills"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"


# ── Request Schemas ──────────────────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0, description="Must be a positive number")
    category: Category
    date: date
    note: Optional[str] = Field(None, max_length=500)

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be blank or whitespace")
        return stripped

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float) -> float:
        return round(v, 2)

    @field_validator("note")
    @classmethod
    def strip_note(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return v


class ExpenseUpdate(ExpenseCreate):
    """Full replacement — same fields as create."""
    pass


# ── Response Schemas ─────────────────────────────────────────────────────────

class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: Category
    date: date
    note: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MonthlySummaryResponse(BaseModel):
    year: int
    month: int
    total: float
    by_category: dict[str, float]
