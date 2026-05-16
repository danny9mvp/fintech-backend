from datetime import datetime

from pydantic import BaseModel


class BalanceResponse(BaseModel):
    total_income: float
    total_expense: float
    balance: float


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
    movement_category_id: int
    category_name: str
    created_at: datetime

    model_config = {"from_attributes": True}
