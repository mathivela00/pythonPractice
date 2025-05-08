from app.infrastructure.repositories.user_repository import UserRepository
from app.domain.schemas.user import UserCreate, UserUpdate, User
from app.core.security import verify_password, create_access_token
from app.core.decorators import transactional
from datetime import timedelta
from app.core.config import settings
from typing import Optional, List
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, user_id: UUID) -> Optional[User]:
        return self.repository.get_by_id(user_id)

    def get_users(self) -> List[User]:
        return self.repository.get_all()

    @transactional
    def create_user(self, user: UserCreate) -> User:
        # Verificar si el usuario ya existe
        existing_user = self.repository.get_by_email(user.email)
        if existing_user:
            logger.warning(f"Intento de crear usuario con email ya existente: {user.email}")
            raise ValueError(f"Usuario con email {user.email} ya existe")
        
        return self.repository.create(user)

    @transactional
    def update_user(self, user_id: UUID, user: UserUpdate) -> Optional[User]:
        # Verificar si existe el usuario
        existing_user = self.repository.get_by_id(user_id)
        if not existing_user:
            logger.warning(f"Intento de actualizar usuario inexistente: {user_id}")
            return None
            
        # Si se está actualizando el email, verificar que no exista otro usuario con ese email
        if user.email and user.email != existing_user.email:
            user_with_email = self.repository.get_by_email(user.email)
            if user_with_email:
                logger.warning(f"Intento de actualizar usuario con email ya existente: {user.email}")
                raise ValueError(f"Usuario con email {user.email} ya existe")
                
        return self.repository.update(user_id, user)

    @transactional
    def delete_user(self, user_id: UUID) -> bool:
        return self.repository.delete(user_id)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.repository.get_by_email(email)
        if not user:
            logger.warning(f"Intento de autenticación con email inexistente: {email}")
            return None
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Intento de autenticación fallido para usuario: {email}")
            return None
        return user

    def create_access_token_for_user(self, user: User) -> str:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        ) 