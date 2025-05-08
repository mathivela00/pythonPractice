from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.interfaces.api.controllers import user_controller, task_controller
from app.core.config import settings
from app.infrastructure.database import engine, Base
from app.core.logging_config import setup_logging

# Configurar el sistema de logging
setup_logging()

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(
    user_controller.router,
    prefix=settings.API_V1_STR,
    tags=["users"]
)

app.include_router(
    task_controller.router,
    prefix=settings.API_V1_STR,
    tags=["tasks"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)