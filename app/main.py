from fastapi import FastAPI

from app.api.auth_controller import router as auth_router
from app.api.category_controller import router as categories_router
from app.api.movement_controller import router as movements_router
from app.api.user_controller import router as users_router
from app.core.database import engine
from app.model import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fintech Backend")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(movements_router)
