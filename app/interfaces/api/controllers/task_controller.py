from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.repositories.task_repository import TaskRepository
from app.application.services.task_service import TaskService
from app.domain.schemas.task import (
    Task, TaskCreate, TaskUpdate, 
    CreateTaskCommand, UpdateTaskCommand, DeleteTaskCommand,
    AssignTaskCommand, CompleteTaskCommand,
    GetTaskQuery, GetTasksQuery
)
from app.domain.schemas.user import User
from app.interfaces.api.controllers.user_controller import get_current_user
from typing import List
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    repository = TaskRepository(db)
    return TaskService(repository)

# Endpoint para crear una tarea
@router.post("/tasks", response_model=Task)
async def create_task(
    task: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user)
):
    try:
        command = CreateTaskCommand(
            title=task.title,
            description=task.description,
            priority=task.priority,
            user_id=current_user.id,
            assigned_to_id=task.assigned_to_id,
            needs_background_processing=False,
            processing_params={}
        )
        return task_service.handle_create_task(command)
    except Exception as e:
        logger.error(f"Error al crear tarea: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Endpoint para obtener todas las tareas (con filtros)
@router.get("/tasks", response_model=List[Task])
async def get_tasks(
    status: str = None,
    priority: str = None,
    skip: int = 0,
    limit: int = 100,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user)
):
    try:
        query = GetTasksQuery(
            user_id=current_user.id if current_user.roles != "admin" else None,
            status=status,
            priority=priority,
            skip=skip,
            limit=limit
        )
        return task_service.handle_get_tasks(query)
    except Exception as e:
        logger.error(f"Error al obtener tareas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Endpoint para obtener una tarea por ID
@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user)
):
    try:
        query = GetTaskQuery(
            task_id=task_id,
            user_id=current_user.id,
            is_admin=(current_user.roles == "admin")
        )
        task = task_service.handle_get_task(query)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        return task
    except ValueError as e:
        logger.warning(f"Acceso no autorizado a tarea {task_id} por usuario {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al obtener tarea {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Endpoint para actualizar una tarea
@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user)
):
    try:
        command = UpdateTaskCommand(
            task_id=task_id,
            user_id=current_user.id,
            title=task_update.title,
            description=task_update.description,
            status=task_update.status,
            priority=task_update.priority,
            assigned_to_id=task_update.assigned_to_id,
            is_admin=(current_user.roles == "admin")
        )
        updated_task = task_service.handle_update_task(command)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        return updated_task
    except ValueError as e:
        logger.warning(f"Acceso no autorizado para actualizar tarea {task_id} por usuario {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al actualizar tarea {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Endpoint para eliminar una tarea
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user)
):
    try:
        command = DeleteTaskCommand(
            task_id=task_id,
            user_id=current_user.id,
            is_admin=(current_user.roles == "admin")
        )
        result = task_service.handle_delete_task(command)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        return None
    except ValueError as e:
        logger.warning(f"Acceso no autorizado para eliminar tarea {task_id} por usuario {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al eliminar tarea {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Endpoint para asignar una tarea a un usuario
@router.post("/tasks/{task_id}/assign", response_model=Task)
async def assign_task(
    task_id: UUID,
    assignee_id: UUID,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user)
):
    try:
        command = AssignTaskCommand(
            task_id=task_id,
            assigner_id=current_user.id,
            assignee_id=assignee_id,
            is_admin=(current_user.roles == "admin")
        )
        updated_task = task_service.handle_assign_task(command)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        return updated_task
    except ValueError as e:
        logger.warning(f"Acceso no autorizado para asignar tarea {task_id} por usuario {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al asignar tarea {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Endpoint para marcar una tarea como completada
@router.post("/tasks/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user)
):
    try:
        command = CompleteTaskCommand(
            task_id=task_id,
            user_id=current_user.id,
            is_admin=(current_user.roles == "admin")
        )
        completed_task = task_service.handle_complete_task(command)
        if not completed_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        return completed_task
    except ValueError as e:
        logger.warning(f"Acceso no autorizado para completar tarea {task_id} por usuario {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al completar tarea {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 