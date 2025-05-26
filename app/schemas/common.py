from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

class ListResponseModel(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    total: int
    items: List[T]

class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 10
    order_by: Optional[str] = None
    order: Optional[str] = "desc"  # asc or desc 