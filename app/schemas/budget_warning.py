from pydantic import BaseModel


class BudgetWarningResponse(BaseModel):
    category_id: int
    category_name: str
    budget: float | None
    total_expense: float
    usage_percentage: float | None
    warning_level: str
    message: str


class BudgetSummaryItem(BaseModel):
    category_id: int
    category_name: str
    budget: float | None
    total_expense: float
    usage_percentage: float | None
