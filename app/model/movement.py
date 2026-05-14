from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Movement(Base):
    __tablename__ = "movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    movement_category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movement_categories.id"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="movements")
    category: Mapped["MovementCategory"] = relationship(back_populates="movements")

    @property
    def category_name(self) -> str | None:
        return self.category.name if self.category else None
