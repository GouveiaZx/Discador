import os
from typing import Optional, Literal, Union
from pydantic import PostgresDsn, validator, AnyUrl
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

class Configuracion(BaseSettings):
    """
    Clase de configuracion usando Pydantic.
    Carga las variables de entorno y proporciona valores por defecto.
    """
    # Configuracion general
    APP_NAME: str = "Discador Predictivo"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configuracion del servidor
    PUERTO: int = 8000
    HOST: str = "0.0.0.0"
    
    # Configuracion de la base de datos
    DB_URL: Optional[Union[PostgresDsn, AnyUrl]] = None
    DB_HOST: str = "localhost"
    DB_PUERTO: int = 5432
    DB_USUARIO: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NOMBRE: str = "discador"
    
    # Configuracion de Asterisk
    ASTERISK_HOST: str = "localhost"
    ASTERISK_PUERTO: int = 5038
    ASTERISK_USUARIO: str = "admin"
    ASTERISK_PASSWORD: str = "admin"
    
    # Configuracion de STT (Vosk)
    VOSK_MODEL_PATH: str = "./vosk-model-en-us-0.22"
    
    # Configuracion de logs
    LOG_NIVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMATO: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_ARCHIVO: Optional[str] = "logs/discador.log"
    LOG_ROTACION: bool = True
    LOG_MAX_TAMANO_MB: int = 10
    LOG_COPIAS_RESPALDO: int = 5

    @validator("DB_URL", pre=True)
    def validar_db_url(cls, v, values):
        """
        Genera la URL de conexion si no se proporciona explicitamente.
        Aceita URLs SQLite e PostgreSQL.
        """
        if isinstance(v, str):
            # Se a URL é SQLite, retorna como está
            if v.startswith('sqlite'):
                return v
            # Se é PostgreSQL, retorna como está
            if v.startswith('postgres'):
            return v
        
        # Se não tem URL configurada, usar Supabase em produção
        if not values.get("DEBUG", False):
            return "postgresql://postgres:password@db.orxxocptgaeoyrtlxwkv.supabase.co:5432/postgres"
        
        # Construir a URL de conexion a partir de los componentes (PostgreSQL)
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DB_USUARIO"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=str(values.get("DB_PUERTO")),
            path=f"/{values.get('DB_NOMBRE') or ''}",
        )
    
    class Config:
        """Configuracion de Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Permite campos extras

# Crear instancia de configuracion
configuracion = Configuracion()

# Para compatibilidad con codigo existente
DATABASE_URL = configuracion.DB_URL
ASTERISK_HOST = configuracion.ASTERISK_HOST
ASTERISK_PORT = configuracion.ASTERISK_PUERTO
ASTERISK_USERNAME = configuracion.ASTERISK_USUARIO
ASTERISK_PASSWORD = configuracion.ASTERISK_PASSWORD
VOSK_MODEL_PATH = configuracion.VOSK_MODEL_PATH
SERVER_HOST = configuracion.HOST
SERVER_PORT = configuracion.PUERTO

def recargar_configuracion(archivo_env: str = ".env") -> Configuracion:
    """
    Recarga la configuracion desde el archivo .env especificado.
    
    Args:
        archivo_env: Ruta al archivo .env a cargar
        
    Returns:
        Configuracion: Nueva instancia de configuracion
    """
    # Recargar el archivo .env
    load_dotenv(archivo_env, override=True)
    
    # Crear nueva instancia de configuracion
    nueva_config = Configuracion()
    
    # Actualizar variables globales para compatibilidad
    global configuracion, DATABASE_URL, ASTERISK_HOST, ASTERISK_PORT
    global ASTERISK_USERNAME, ASTERISK_PASSWORD, VOSK_MODEL_PATH
    global SERVER_HOST, SERVER_PORT
    
    configuracion = nueva_config
    DATABASE_URL = configuracion.DB_URL
    ASTERISK_HOST = configuracion.ASTERISK_HOST
    ASTERISK_PORT = configuracion.ASTERISK_PUERTO
    ASTERISK_USERNAME = configuracion.ASTERISK_USUARIO
    ASTERISK_PASSWORD = configuracion.ASTERISK_PASSWORD
    VOSK_MODEL_PATH = configuracion.VOSK_MODEL_PATH
    SERVER_HOST = configuracion.HOST
    SERVER_PORT = configuracion.PUERTO
    
    return nueva_config 