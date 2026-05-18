from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.model.user import User
from app.schemas.budget_warning import BudgetSummaryItem, BudgetWarningResponse
from app.schemas.movement_category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.service.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db, current_user)
    return service.list(offset=offset, limit=limit)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    body: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db, current_user)
    try:
        return service.create(body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/budget-summary", response_model=list[BudgetSummaryItem])
def get_budget_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db, current_user)
    return service.get_budget_summary()


@router.get("/{category_id}/check-budget", response_model=BudgetWarningResponse)
def get_budget_warning(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db, current_user)
    warning = service.get_budget_warning(category_id)
    if not warning:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return warning


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db, current_user)
    category = service.get(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    body: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db, current_user)
    try:
        category = service.update(category_id, body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db, current_user)
    if not service.delete(category_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
