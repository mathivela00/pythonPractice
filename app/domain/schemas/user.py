from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from app.domain.models.enums import Gender, Role

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    gender: Gender
    roles: Role

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    gender: Optional[Gender] = None
    roles: Optional[Role] = None

class UserInDB(UserBase):
    id: UUID
    hashed_password: str

    class Config:
        from_attributes = True

class User(UserBase):
    id: UUID

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 