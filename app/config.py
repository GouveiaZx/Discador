import os
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, field_validator
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

class Configuracion(BaseSettings):
    """
    Classe de configuração usando Pydantic.
    Carrega as variáveis de ambiente e fornece valores padrão.
    """
    # Configuração geral
    APP_NAME: str = "Discador Predictivo"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configuração do servidor
    PUERTO: int = 8000
    HOST: str = "0.0.0.0"
    
    # Configuração da base de dados
    DB_URL: Optional[PostgresDsn] = None
    DB_HOST: str = "localhost"
    DB_PUERTO: int = 5432
    DB_USUARIO: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NOMBRE: str = "discador"
    
    # Configuração do Asterisk
    ASTERISK_HOST: str = "localhost"
    ASTERISK_PUERTO: int = 5038
    ASTERISK_USUARIO: str = "admin"
    ASTERISK_PASSWORD: str = "admin"
    
    # Configuração de STT (Vosk)
    VOSK_MODEL_PATH: str = "./vosk-model-en-us-0.22"
    
    # Configuração de logs
    LOG_NIVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMATO: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_ARCHIVO: Optional[str] = "logs/discador.log"
    LOG_ROTACION: bool = True
    LOG_MAX_TAMANO_MB: int = 10
    LOG_COPIAS_RESPALDO: int = 5

    @field_validator("DB_URL", mode="before")
    @classmethod
    def validar_db_url(cls, v, info=None):
        """
        Gera a URL de conexão se não for fornecida explicitamente.
        """
        if v is not None and isinstance(v, str):
            return v
        
        # Para desenvolvimento local, usar SQLite por padrão
        return "sqlite:///./discador.db"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }

# Crear instancia de configuración
configuracion = Configuracion()

# Para compatibilidad con código existente
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
    Recarga la configuración desde el archivo .env especificado.
    
    Args:
        archivo_env: Ruta al archivo .env a cargar
        
    Returns:
        Configuracion: Nueva instancia de configuración
    """
    # Recargar el archivo .env
    load_dotenv(archivo_env, override=True)
    
    # Crear nueva instancia de configuración
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