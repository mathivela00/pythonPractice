from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.application.services.user_service import UserService
from app.domain.schemas.user import User, UserCreate, UserUpdate, Token
from typing import List
from uuid import UUID
from jose import JWTError, jwt
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user(UUID(user_id))
    if user is None:
        raise credentials_exception
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Intento de login fallido para usuario: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = user_service.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=User)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    try:
        return user_service.create_user(user)
    except ValueError as e:
        logger.warning(f"Error al crear usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/users", response_model=List[User])
async def read_users(
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    return user_service.get_users()

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users/{user_id}", response_model=User)
async def read_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    user = user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: UUID,
    user: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    try:
        updated_user = user_service.update_user(user_id, user)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        logger.warning(f"Error al actualizar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    result = user_service.delete_user(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return None 