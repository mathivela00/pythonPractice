from sqlalchemy.orm import Session
from app.domain.models.task import Task
from app.domain.schemas.task import TaskCreate, TaskUpdate, GetTasksQuery
from app.domain.models.enums import TaskStatus
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: UUID) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_by_celery_task_id(self, celery_task_id: str) -> Optional[Task]:
        return self.db.query(Task).filter(Task.celery_task_id == celery_task_id).first()

    def get_all(self, query: GetTasksQuery) -> List[Task]:
        db_query = self.db.query(Task)
        
        if query.user_id:
            db_query = db_query.filter(Task.user_id == query.user_id)
        
        if query.assigned_to_id:
            db_query = db_query.filter(Task.assigned_to_id == query.assigned_to_id)
        
        if query.status:
            db_query = db_query.filter(Task.status == query.status)
        
        if query.priority:
            db_query = db_query.filter(Task.priority == query.priority)
            
        return db_query.offset(query.skip).limit(query.limit).all()

    def create(self, task: TaskCreate, user_id: UUID) -> Task:
        try:
            db_task = Task(
                title=task.title,
                description=task.description,
                priority=task.priority,
                user_id=user_id,
                assigned_to_id=task.assigned_to_id
            )
            self.db.add(db_task)
            self.db.commit()
            self.db.refresh(db_task)
            return db_task
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating task: {str(e)}")
            raise

    def update(self, task_id: UUID, task_update: TaskUpdate) -> Optional[Task]:
        try:
            db_task = self.get_by_id(task_id)
            if not db_task:
                return None

            update_data = task_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)

            self.db.commit()
            self.db.refresh(db_task)
            return db_task
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating task {task_id}: {str(e)}")
            raise

    def delete(self, task_id: UUID) -> bool:
        try:
            db_task = self.get_by_id(task_id)
            if not db_task:
                return False

            self.db.delete(db_task)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise
        
    def complete_task(self, task_id: UUID) -> Optional[Task]:
        try:
            db_task = self.get_by_id(task_id)
            if not db_task:
                return None
                
            db_task.status = TaskStatus.completed
            db_task.completed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_task)
            return db_task
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error completing task {task_id}: {str(e)}")
            raise
        
    def update_celery_task_id(self, task_id: UUID, celery_task_id: str) -> Optional[Task]:
        try:
            db_task = self.get_by_id(task_id)
            if not db_task:
                return None
                
            db_task.celery_task_id = celery_task_id
            
            self.db.commit()
            self.db.refresh(db_task)
            return db_task
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating celery task ID for task {task_id}: {str(e)}")
            raise 