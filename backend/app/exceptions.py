"""
exceptions.py
-------------
Centralized custom exception classes and FastAPI exception handlers.

Design:
    - AppException is the base class for all domain exceptions.
    - Each specific exception carries its own HTTP status code and message.
    - register_exception_handlers() wires all handlers into the FastAPI app,
      ensuring consistent JSON error responses across the entire API.

Error response format (all errors):
    {
        "error": "ErrorType",
        "message": "Human-readable description",
        "detail": <optional extra context>
    }
"""

from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


# ── Base Exception ────────────────────────────────────────────────────────────

class AppException(Exception):
    """
    Base class for all application-level exceptions.
    Carries an HTTP status code and a descriptive message.
    """

    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        detail: Optional[Any] = None,
    ) -> None:
        self.status_code = status_code
        self.error = error
        self.message = message
        self.detail = detail
        super().__init__(message)


# ── Specific Exceptions ───────────────────────────────────────────────────────

class ExpenseNotFoundError(AppException):
    """Raised when an expense with the given ID does not exist in the DB."""

    def __init__(self, expense_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="ExpenseNotFound",
            message=f"Expense with id {expense_id} was not found",
            detail={"expense_id": expense_id},
        )


class InvalidCategoryError(AppException):
    """Raised when a category value is not in the allowed set."""

    def __init__(self, category: str) -> None:
        from app.schemas import Category  # local import avoids circular dependency

        valid = [c.value for c in Category]
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error="InvalidCategory",
            message=f"'{category}' is not a valid category",
            detail={"provided": category, "valid_categories": valid},
        )


class InvalidDateRangeError(AppException):
    """Raised when from_date is later than to_date in filter parameters."""

    def __init__(self, from_date: str, to_date: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error="InvalidDateRange",
            message=f"from_date ({from_date}) must be on or before to_date ({to_date})",
            detail={"from_date": from_date, "to_date": to_date},
        )


class DatabaseOperationError(AppException):
    """Raised when a database operation fails unexpectedly."""

    def __init__(self, operation: str, original_error: str) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="DatabaseOperationError",
            message=f"Database error during '{operation}'",
            detail={"operation": operation, "original_error": original_error},
        )


# ── Exception Handlers ────────────────────────────────────────────────────────

def _error_response(
    status_code: int,
    error: str,
    message: str,
    detail: Optional[Any] = None,
) -> JSONResponse:
    """Build a standardized JSON error response."""
    body: dict[str, Any] = {"error": error, "message": message}
    if detail is not None:
        body["detail"] = detail
    return JSONResponse(status_code=status_code, content=body)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all AppException subclasses with a uniform response shape."""
    return _error_response(
        status_code=exc.status_code,
        error=exc.error,
        message=exc.message,
        detail=exc.detail,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors from request bodies and query params.
    Flattens FastAPI's nested error structure into a readable list.
    """
    errors = []
    for err in exc.errors():
        field = " → ".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append({"field": field or "body", "message": err["msg"]})

    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error="ValidationError",
        message="Request validation failed",
        detail=errors,
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """
    Catch unhandled SQLAlchemy errors as a safety net.
    Avoids leaking raw SQL error messages to API consumers.
    """
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="DatabaseError",
        message="An unexpected database error occurred",
        detail=str(exc.__class__.__name__),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for any unhandled exception."""
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="InternalServerError",
        message="An unexpected error occurred",
    )


# ── Registration Helper ───────────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers on the FastAPI application instance.
    Call this once during app startup in main.py.
    """
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)
