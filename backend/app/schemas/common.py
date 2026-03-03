# Source: Doc 07 §11.1 — Ortak API response şemaları
"""Ortak API response şemaları."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = {}


class APIResponse(BaseModel, Generic[T]):
    """Standart API yanıt formatı.

    {
        "success": true/false,
        "data": { ... },
        "meta": { ... } (opsiyonel)
    }
    """

    success: bool
    data: T | None = None
    error: ErrorDetail | None = None
    meta: PaginationMeta | None = None
