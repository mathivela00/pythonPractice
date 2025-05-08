from sqlalchemy.orm import Session
from app.domain.models.user import User
from app.domain.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from typing import List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self) -> List[User]:
        return self.db.query(User).all()

    def create(self, user: UserCreate) -> User:
        try:
            db_user = User(
                email=user.email,
                hashed_password=get_password_hash(user.password),
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                gender=user.gender,
                roles=user.roles
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise

    def update(self, user_id: UUID, user: UserUpdate) -> Optional[User]:
        try:
            db_user = self.get_by_id(user_id)
            if not db_user:
                return None

            update_data = user.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)

            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise

    def delete(self, user_id: UUID) -> bool:
        try:
            db_user = self.get_by_id(user_id)
            if not db_user:
                return False

            self.db.delete(db_user)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise 