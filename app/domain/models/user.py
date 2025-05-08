from sqlalchemy import Column, String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base
from app.domain.models.enums import Gender, Role
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=False)
    roles = Column(SQLEnum(Role), nullable=False)
    
    # Relación con las tareas creadas por el usuario (usuario como creador)
    created_tasks = relationship("Task", foreign_keys="Task.user_id", back_populates="user", cascade="all, delete-orphan")
    
    # Relación con las tareas asignadas al usuario (usuario como responsable)
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to_id", back_populates="assigned_to") 