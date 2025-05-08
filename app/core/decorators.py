import functools
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def transactional(method):
    """
    Decorador para manejar transacciones automáticamente.
    Realiza commit si la función termina correctamente, rollback si hay una excepción.
    
    Uso:
        @transactional
        def mi_metodo(self, db, ...):
            # Código que manipula la base de datos
            
    El parámetro 'db' debe ser una sesión de SQLAlchemy.
    """
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        # Intentamos encontrar el parámetro de la base de datos
        db = None
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        
        if 'db' in kwargs and isinstance(kwargs['db'], Session):
            db = kwargs['db']
            
        if db is None:
            # Si no encontramos el objeto de sesión, simplemente ejecutamos el método original
            logger.warning(f"No database session found for transactional method {method.__name__}")
            return method(*args, **kwargs)
        
        try:
            result = method(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Transaction rolled back in {method.__name__}: {str(e)}")
            raise
    
    return wrapper 