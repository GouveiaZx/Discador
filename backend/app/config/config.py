import os
from typing import Optional, Literal, Union
from pydantic import PostgresDsn, validator, AnyUrl
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

class Configuracion(BaseSettings):
    """
    Classe de configuração usando Pydantic.
    Carrega as variáveis de ambiente e fornece valores padrão.
    """
    # Configuracao general
    APP_NAME: str = "Discador Predictivo"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configuracao del servidor
    PUERTO: int = int(os.environ.get("PORT", 8000))
    HOST: str = "0.0.0.0"
    
    # Configuracao de la base de datos
    DB_URL: Optional[Union[PostgresDsn, AnyUrl]] = None
    DB_HOST: str = "localhost"
    DB_PUERTO: int = 5432
    DB_USUARIO: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NOMBRE: str = "discador"
    
    # Configuracao de Asterisk
    ASTERISK_HOST: str = "localhost"
    ASTERISK_PUERTO: int = 5038
    ASTERISK_USUARIO: str = "admin"
    ASTERISK_PASSWORD: str = "admin"
    
    # Configuracao de logs
    LOG_NIVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMATO: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_ARQUIVO: Optional[str] = "logs/discador.log"
    LOG_ROTACION: bool = True
    LOG_MAX_TAMANO_MB: int = 10
    LOG_COPIAS_RESPALDO: int = 5

    @validator("DB_URL", pre=True)
    def validar_db_url(cls, v, values):
        """
        Gera a URL de conexão se não for fornecida explicitamente.
        Aceita URLs SQLite e PostgreSQL.
        """
        if isinstance(v, str):
            # Se a URL é SQLite, retorna como está
            if v.startswith('sqlite'):
                return v
            # Se é PostgreSQL, retorna como está
            if v.startswith('postgres'):
                return v
        
        # Usar URL do Supabase por padrão
        return "postgresql://postgres.orxxocptgaeoyrtlxwkv:%21Gouveia1@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    
    class Config:
        """Configuração do Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Permite campos extras

# Crear instancia de configuracion
configuracion = Configuracion()

# Para compatibilidad com código existente
DATABASE_URL = configuracion.DB_URL
ASTERISK_HOST = configuracion.ASTERISK_HOST
ASTERISK_PORT = configuracion.ASTERISK_PUERTO
ASTERISK_USERNAME = configuracion.ASTERISK_USUARIO
ASTERISK_PASSWORD = configuracion.ASTERISK_PASSWORD
SERVER_HOST = configuracion.HOST
SERVER_PORT = configuracion.PUERTO

def recargar_configuracion(archivo_env: str = ".env") -> Configuracion:
    """
    Recarrega a configuração do arquivo .env especificado.
    
    Args:
        archivo_env: Caminho para o arquivo .env a carregar
        
    Returns:
        Configuracion: Nova instância de configuração
    """
    # Recarregar o arquivo .env
    load_dotenv(archivo_env, override=True)
    
    # Criar nova instância de configuração
    nueva_config = Configuracion()
    
    # Atualizar variáveis globais para compatibilidade
    global configuracion, DATABASE_URL, ASTERISK_HOST, ASTERISK_PORT
    global ASTERISK_USERNAME, ASTERISK_PASSWORD
    global SERVER_HOST, SERVER_PORT
    
    configuracion = nueva_config
    DATABASE_URL = configuracion.DB_URL
    ASTERISK_HOST = configuracion.ASTERISK_HOST
    ASTERISK_PORT = configuracion.ASTERISK_PUERTO
    ASTERISK_USERNAME = configuracion.ASTERISK_USUARIO
    ASTERISK_PASSWORD = configuracion.ASTERISK_PASSWORD
    SERVER_HOST = configuracion.HOST
    SERVER_PORT = configuracion.PUERTO
    
    return nueva_config