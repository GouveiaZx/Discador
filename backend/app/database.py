from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from contextlib import contextmanager

from app.config import configuracion

# Crear motor SQLAlchemy
engine = create_engine(
    str(configuracion.DB_URL),
    echo=configuracion.DEBUG,  # Mostrar consultas SQL en modo debug
    pool_pre_ping=True,  # Verificar conexion antes de usarla
    pool_recycle=3600,  # Reciclar conexiones despues de 1 hora
    pool_size=5,  # Tamano inicial del pool de conexiones
    max_overflow=10  # Conexiones adicionales permitidas
)

# Crear metadatos
metadata = MetaData()

# Crear clase de sesion
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear clase base para los modelos ORM
Base = declarative_base(metadata=metadata)

# Funcion para obtener una sesion de base de datos como dependency en FastAPI
def obtener_sesion() -> Generator[Session, None, None]:
    """
    Obtiene una sesion de base de datos para usar en las rutas FastAPI.
    Esta funcion esta disenada para ser usada con el parametro Depends de FastAPI.
    
    Yields:
        Session: Sesion de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Funcion para obtener una sesion como context manager
@contextmanager
def obtener_sesion_context() -> Generator[Session, None, None]:
    """
    Obtiene una sesion de base de datos para usar con 'with'.
    
    Ejemplo:
        with obtener_sesion_context() as db:
            resultado = db.query(Modelo).all()
    
    Yields:
        Session: Sesion de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Funcion para inicializar la base de datos
def inicializar_bd() -> None:
    """
    Crea todas las tablas definidas en los modelos.
    """
    Base.metadata.create_all(bind=engine)

# Funcion para cerrar la conexion a la base de datos
def cerrar_conexion() -> None:
    """
    Cierra la conexion del motor de base de datos.
    """
    if engine:
        engine.dispose() 