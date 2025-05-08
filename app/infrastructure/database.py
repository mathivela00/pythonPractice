from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import urllib.parse

# Crear el motor SQL
engine = create_engine(settings.DATABASE_URL, echo=True)

# Configurar opciones específicas para SQL Server
@event.listens_for(engine, "connect")
def configure_connection(dbapi_connection, connection_record):
    # Configurar opciones específicas de SQL Server si es necesario
    cursor = dbapi_connection.cursor()
    cursor.execute("SET NOCOUNT ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 