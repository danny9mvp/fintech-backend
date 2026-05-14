from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud.user import user_crud
from app.model.user import User
from app.schemas.user import UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_crud.get(db, user_id)

@router.patch("/me", status_code=status.HTTP_204_NO_CONTENT)
def update_me(body: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_crud.update(db, current_user, **body.model_dump())
