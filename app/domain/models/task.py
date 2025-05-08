from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base
from app.domain.models.enums import TaskStatus, TaskPriority
import uuid
from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.pending, nullable=False)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.medium, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Clave foránea para el creador de la tarea
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Clave foránea para el usuario asignado
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Establecer relaciones con nombres específicos y foreign_keys explícitas
    # El user es el creador de la tarea
    user = relationship("User", foreign_keys=[user_id], back_populates="created_tasks")
    
    # El assigned_to es el usuario al que se le asigna la tarea
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")
    
    # ID de la tarea en Celery (si es una tarea asíncrona)
    celery_task_id = Column(String(255), nullable=True) 