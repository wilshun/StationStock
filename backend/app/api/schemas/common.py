import math
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
    pages: int = Field(ge=0)

    @classmethod
    def create(
        cls,
        *,
        items: list[T],
        pagination: PaginationParams,
        total: int,
    ) -> "Page[T]":
        pages = math.ceil(total / pagination.page_size) if total else 0
        return cls(
            items=items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
            pages=pages,
        )
