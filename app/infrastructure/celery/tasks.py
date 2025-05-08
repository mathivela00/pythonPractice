import time
from app.infrastructure.celery.celery_app import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task(bind=True)
def process_task(self, task_id: str, params: dict = None):
    """
    Tarea asíncrona para procesar una tarea.
    Puede ser una tarea de larga duración.
    """
    logger.info(f"Comenzando procesamiento de tarea {task_id}")
    
    # Simular procesamiento de larga duración
    time.sleep(5)
    
    logger.info(f"Procesamiento de tarea {task_id} completado")
    return {"task_id": task_id, "status": "completed"}

@celery_app.task(bind=True)
def send_task_notification(self, user_id: str, task_id: str, notification_type: str):
    """
    Tarea asíncrona para enviar notificaciones relacionadas con tareas.
    """
    logger.info(f"Enviando notificación de tipo {notification_type} para la tarea {task_id} al usuario {user_id}")
    
    # Aquí iría la lógica para enviar notificaciones (email, push, etc.)
    time.sleep(2)
    
    logger.info(f"Notificación enviada para la tarea {task_id}")
    return {"user_id": user_id, "task_id": task_id, "status": "sent"} 