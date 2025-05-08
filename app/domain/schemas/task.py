from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.domain.models.enums import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium

class TaskCreate(TaskBase):
    assigned_to_id: Optional[UUID] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to_id: Optional[UUID] = None

class TaskInDB(TaskBase):
    id: UUID
    status: TaskStatus
    user_id: UUID
    assigned_to_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    celery_task_id: Optional[str] = None

    class Config:
        from_attributes = True

class Task(TaskInDB):
    pass

# Esquemas para CQRS - Comandos
class CreateTaskCommand(TaskCreate):
    user_id: UUID

class UpdateTaskCommand(TaskUpdate):
    task_id: UUID

class DeleteTaskCommand(BaseModel):
    task_id: UUID

class AssignTaskCommand(BaseModel):
    task_id: UUID
    assigned_to_id: UUID

class CompleteTaskCommand(BaseModel):
    task_id: UUID

# Esquemas para CQRS - Consultas
class GetTaskQuery(BaseModel):
    task_id: UUID

class GetTasksQuery(BaseModel):
    user_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    skip: int = 0
    limit: int = 100 