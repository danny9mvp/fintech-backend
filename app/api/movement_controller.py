from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud.movement import movement_crud
from app.crud.movement_category import category_crud
from app.model.user import User
from app.schemas.movement import MovementCreate, MovementResponse, MovementUpdate
from schemas.paginated import PaginatedResponse

router = APIRouter(prefix="/movements", tags=["movements"])


@router.get(
    "/",
    response_model=PaginatedResponse[MovementResponse],
    response_model_exclude_none=True,
)
def list_movements(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    offset = (page - 1) * page_size
    user_movements_count = movement_crud.count_user_movements(db, user_id=current_user.id)
    user_movements = (
        movement_crud.get_by_user(db, user_id=current_user.id, offset=offset, limit=page_size)
    )

    total_pages = ceil(user_movements_count / page_size)

    return PaginatedResponse(
        items=user_movements,
        total=user_movements_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


@router.post("/", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
def create_movement(
    body: MovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = category_crud.get(db, body.movement_category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return movement_crud.create(
        db, user_id=current_user.id, **body.model_dump()
    )


@router.get("/{movement_id}", response_model=MovementResponse)
def get_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    movement = movement_crud.get(db, movement_id)
    if not movement or movement.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return movement


@router.patch("/{movement_id}", response_model=MovementResponse)
def update_movement(
    movement_id: int,
    body: MovementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    movement = movement_crud.get(db, movement_id)
    if not movement or movement.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return movement_crud.update(db, movement, **body.model_dump())


@router.delete("/{movement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    movement = movement_crud.get(db, movement_id)
    if not movement or movement.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    movement_crud.remove(db, movement_id)
