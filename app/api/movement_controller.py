from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.model.user import User
from app.schemas.movement import BalanceResponse, MovementCreate, MovementResponse, MovementUpdate
from app.schemas.paginated import PaginatedResponse
from app.service.movement_service import MovementService

router = APIRouter(prefix="/movements", tags=["movements"])


@router.get(
    "/",
    response_model=PaginatedResponse[MovementResponse],
    response_model_exclude_none=True,
)
def list_movements(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    movement_type: str | None = Query(None),
    category_id: int | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    service = MovementService(db, current_user)
    return service.list(
        page=page, page_size=page_size,
        movement_type=movement_type, category_id=category_id,
        date_from=date_from, date_to=date_to,
    )


@router.post("/", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
def create_movement(
    body: MovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MovementService(db, current_user)
    try:
        movement = service.create(body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return movement


@router.get("/balance", response_model=BalanceResponse)
def get_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MovementService(db, current_user)
    return service.get_balance()


@router.get("/{movement_id}", response_model=MovementResponse)
def get_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MovementService(db, current_user)
    movement = service.get(movement_id)
    if not movement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return movement


@router.patch("/{movement_id}", response_model=MovementResponse)
def update_movement(
    movement_id: int,
    body: MovementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MovementService(db, current_user)
    movement = service.update(movement_id, body)
    if not movement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return movement


@router.delete("/{movement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MovementService(db, current_user)
    if not service.delete(movement_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
