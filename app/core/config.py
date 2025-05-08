from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI DDD"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here"  # Cambiar en producción
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "mssql+pyodbc://user:password@server/database?driver=ODBC+Driver+17+for+SQL+Server"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 