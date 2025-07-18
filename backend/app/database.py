from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from contextlib import contextmanager
import sqlite3

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

# Alias para compatibilidade
def get_db() -> Generator[Session, None, None]:
    """
    Alias para obtener_sesion para compatibilidade com código existente.
    
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
    
    Exemplo:
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
    try:
        # Em desenvolvimento, recriar todas as tabelas
        if configuracion.DEBUG:
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
        else:
            # Em produção, apenas criar se não existir com timeout reduzido
            Base.metadata.create_all(bind=engine, checkfirst=True)
    except Exception as e:
        # Log do erro mas não falha a aplicação
        from app.utils.logger import configurar_logger
        logger = configurar_logger("database")
        logger.warning(f"Aviso ao inicializar banco de dados: {str(e)}")
        # Continua sem falhar

# Funcion para cerrar la conexion a la base de datos
def cerrar_conexion() -> None:
    """
    Cierra la conexion del motor de base de datos.
    """
    if engine:
        engine.dispose()

# Função para obter conexão SQLite direta (para compatibilidade)
def get_db_connection():
    """
    Obtém uma conexão SQLite direta para operações que não usam SQLAlchemy.
    Usado principalmente para compatibilidade com código legado.
    """
    db_url = str(configuracion.DB_URL)
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        return sqlite3.connect(db_path)
    else:
        # Para outros tipos de banco, usar SQLAlchemy
        return engine.raw_connection()