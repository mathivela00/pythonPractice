from app.infrastructure.repositories.task_repository import TaskRepository
from app.domain.schemas.task import (
    Task, TaskCreate, TaskUpdate, 
    CreateTaskCommand, UpdateTaskCommand, DeleteTaskCommand,
    AssignTaskCommand, CompleteTaskCommand,
    GetTaskQuery, GetTasksQuery
)
from app.infrastructure.celery.tasks import process_task, send_task_notification
from app.core.decorators import transactional
from typing import List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    # Command Handlers
    @transactional
    def handle_create_task(self, command: CreateTaskCommand) -> Task:
        task = self.repository.create(TaskCreate(
            title=command.title,
            description=command.description,
            priority=command.priority,
            assigned_to_id=command.assigned_to_id
        ), command.user_id)
        
        # Si la tarea requiere procesamiento en segundo plano
        if command.needs_background_processing:
            celery_task = process_task.delay(str(task.id), command.processing_params)
            self.repository.update_celery_task_id(task.id, celery_task.id)
            
            # Enviar notificación de creación
            send_task_notification.delay(
                str(command.user_id), 
                str(task.id), 
                "created"
            )
            
        return task

    @transactional
    def handle_update_task(self, command: UpdateTaskCommand) -> Optional[Task]:
        # Verificar si el usuario tiene permisos para actualizar la tarea
        task = self.repository.get_by_id(command.task_id)
        if not task:
            logger.warning(f"Intentando actualizar tarea inexistente: {command.task_id}")
            return None
            
        if task.user_id != command.user_id and not command.is_admin:
            logger.warning(f"Usuario {command.user_id} no autorizado para actualizar tarea {command.task_id}")
            raise ValueError("No tienes permisos para actualizar esta tarea")
        
        # Crear el objeto de actualización
        task_update = TaskUpdate(
            title=command.title,
            description=command.description,
            status=command.status,
            priority=command.priority,
            assigned_to_id=command.assigned_to_id
        )
        
        updated_task = self.repository.update(command.task_id, task_update)
        
        # Enviar notificación de actualización
        if updated_task:
            send_task_notification.delay(
                str(command.user_id), 
                str(updated_task.id), 
                "updated"
            )
            
        return updated_task

    @transactional
    def handle_delete_task(self, command: DeleteTaskCommand) -> bool:
        # Verificar si el usuario tiene permisos para eliminar la tarea
        task = self.repository.get_by_id(command.task_id)
        if not task:
            logger.warning(f"Intentando eliminar tarea inexistente: {command.task_id}")
            return False
            
        if task.user_id != command.user_id and not command.is_admin:
            logger.warning(f"Usuario {command.user_id} no autorizado para eliminar tarea {command.task_id}")
            raise ValueError("No tienes permisos para eliminar esta tarea")
        
        result = self.repository.delete(command.task_id)
        
        # Enviar notificación de eliminación
        if result:
            send_task_notification.delay(
                str(command.user_id), 
                str(command.task_id), 
                "deleted"
            )
            
        return result

    @transactional
    def handle_assign_task(self, command: AssignTaskCommand) -> Optional[Task]:
        # Verificar si la tarea existe
        task = self.repository.get_by_id(command.task_id)
        if not task:
            logger.warning(f"Intentando asignar tarea inexistente: {command.task_id}")
            return None
            
        # Verificar permisos para asignar
        if task.user_id != command.assigner_id and not command.is_admin:
            logger.warning(f"Usuario {command.assigner_id} no autorizado para asignar tarea {command.task_id}")
            raise ValueError("No tienes permisos para asignar esta tarea")
        
        # Actualizar la asignación
        task_update = TaskUpdate(assigned_to_id=command.assignee_id)
        updated_task = self.repository.update(command.task_id, task_update)
        
        # Enviar notificación de asignación
        if updated_task:
            send_task_notification.delay(
                str(command.assignee_id), 
                str(updated_task.id), 
                "assigned"
            )
            
        return updated_task

    @transactional
    def handle_complete_task(self, command: CompleteTaskCommand) -> Optional[Task]:
        # Verificar si la tarea existe
        task = self.repository.get_by_id(command.task_id)
        if not task:
            logger.warning(f"Intentando completar tarea inexistente: {command.task_id}")
            return None
            
        # Verificar permisos para completar
        if task.assigned_to_id != command.user_id and task.user_id != command.user_id and not command.is_admin:
            logger.warning(f"Usuario {command.user_id} no autorizado para completar tarea {command.task_id}")
            raise ValueError("No tienes permisos para completar esta tarea")
        
        # Completar la tarea
        completed_task = self.repository.complete_task(command.task_id)
        
        # Enviar notificación de finalización
        if completed_task:
            send_task_notification.delay(
                str(task.user_id), 
                str(completed_task.id), 
                "completed"
            )
            
        return completed_task

    # Query Handlers
    def handle_get_task(self, query: GetTaskQuery) -> Optional[Task]:
        task = self.repository.get_by_id(query.task_id)
        
        # Verificar permisos para ver la tarea
        if task and not query.is_admin:
            if task.user_id != query.user_id and task.assigned_to_id != query.user_id:
                logger.warning(f"Usuario {query.user_id} no autorizado para ver tarea {query.task_id}")
                raise ValueError("No tienes permisos para ver esta tarea")
                
        return task

    def handle_get_tasks(self, query: GetTasksQuery) -> List[Task]:
        return self.repository.get_all(query) 