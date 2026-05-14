from datetime import datetime

from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    budget: float | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    budget: float | None = None


class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
