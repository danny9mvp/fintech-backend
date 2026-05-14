from datetime import datetime

from pydantic import BaseModel


class MovementBase(BaseModel):
    type: str
    amount: float
    description: str | None = None


class MovementCreate(MovementBase):
    movement_category_id: int


class MovementUpdate(BaseModel):
    type: str | None = None
    amount: float | None = None
    description: str | None = None
    movement_category_id: int | None = None


class MovementResponse(MovementBase):
    id: int
    user_id: int
    movement_category_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
