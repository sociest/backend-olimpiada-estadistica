from typing import Generic, List, TypeVar
from pydantic import BaseModel
T = TypeVar("T")

class ResponseBase(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: str

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int

class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    meta: PaginationMeta

class PaginatedResponse(ResponseBase[PaginatedData[T]]):
    pass
