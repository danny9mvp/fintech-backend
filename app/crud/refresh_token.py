from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.model.refresh_token import RefreshToken


class RefreshTokenCRUD(CRUDBase):
    def get_by_token_hash(self, db: Session, token_hash: str) -> RefreshToken | None:
        return (
            db.query(self.model)
            .filter(self.model.token_hash == token_hash)
            .first()
        )


refresh_token_crud = RefreshTokenCRUD(RefreshToken)
