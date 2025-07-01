#!/usr/bin/env python3
"""
Configuração de produção robusta para o Sistema Discador Preditivo
Integração completa com Supabase PostgreSQL
"""
import os
import logging
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class ConfiguracaoProducao(BaseSettings):
    """
    Configuração completa para produção com Supabase
    """
    
    # ================================
    # INFORMAÇÕES DO PROJETO
    # ================================
    APP_NAME: str = "Sistema Discador Preditivo"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Sistema profissional de discagem preditiva para call centers"
    ENVIRONMENT: str = "production"
    
    # ================================
    # CONFIGURAÇÃO SUPABASE 
    # ================================
    SUPABASE_URL: str = "https://orxxocptgaeoyrtlxwkv.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjVzdbZcnlN_jiT1mNijqWEWylVrhdQ"
    SUPABASE_PROJECT_ID: str = "orxxocptgaeoyrtlxwkv"
    
    # ================================
    # BANCO DE DADOS
    # ================================
    DATABASE_URL: str = "postgresql://postgres:PASSWORD@db.orxxocptgaeoyrtlxwkv.supabase.co:5432/postgres"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False  # Logs SQL em produção = False
    
    # ================================
    # SERVIDOR FASTAPI
    # ================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    RELOAD: bool = False
    SECRET_KEY: str = "sua_chave_secreta_super_segura_discador_preditivo_2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ================================
    # CONFIGURAÇÕES ASTERISK/VOIP
    # ================================
    ASTERISK_HOST: str = "localhost"
    ASTERISK_PORT: int = 5038
    ASTERISK_USERNAME: str = "admin"
    ASTERISK_PASSWORD: str = "admin"
    ASTERISK_TIMEOUT: int = 10
    
    # ================================
    # CONFIGURAÇÕES DE DISCAGEM
    # ================================
    DEFAULT_TIMEZONE: str = "America/Argentina/Buenos_Aires"
    DEFAULT_CLI_PREFIX: str = "+54"
    DEFAULT_PHONE_FORMAT: str = "international"
    MAX_CONCURRENT_CALLS: int = 50
    CALL_TIMEOUT_SECONDS: int = 30
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY_MINUTES: int = 30
    
    # ================================
    # CONFIGURAÇÕES DE LOGGING
    # ================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "logs/discador_producao.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # ================================
    # CONFIGURAÇÕES DE CACHE/REDIS
    # ================================
    REDIS_URL: Optional[str] = None
    CACHE_TTL_SECONDS: int = 300
    
    # ================================
    # CONFIGURAÇÕES DE SEGURANÇA
    # ================================
    ALLOWED_HOSTS: List[str] = ["*"]  # Configurar adequadamente em produção
    CORS_ORIGINS: List[str] = [
        "https://discador.vercel.app",
        "https://web-production-c192b.up.railway.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    # ================================
    # CONFIGURAÇÕES DE EMAIL/NOTIFICAÇÕES
    # ================================
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    NOTIFICATION_EMAIL: Optional[str] = None
    
    # ================================
    # CONFIGURAÇÕES DE UPLOAD
    # ================================
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".txt"]
    UPLOAD_PATH: str = "uploads/"
    
    # ================================
    # WEBHOOK E INTEGRAÇÕES
    # ================================
    WEBHOOK_SECRET: str = "7a8b9c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f"
    API_RATE_LIMIT: str = "100/minute"
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v):
        """Valida e configura URL do banco"""
        if v and "PASSWORD" in v:
            # Em produção, deve ser configurada a senha real
            password = os.getenv("SUPABASE_DB_PASSWORD", "sua_senha_aqui")
            v = v.replace("PASSWORD", password)
        return v
    
    @field_validator("LOG_LEVEL", mode="before")
    @classmethod 
    def validate_log_level(cls, v):
        """Valida nível de log"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            return "INFO"
        return v.upper()
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow"
    }


# ================================
# CONFIGURAÇÃO GLOBAL
# ================================
config = ConfiguracaoProducao()

def setup_logging():
    """Configura logging para produção"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.LOG_FILE) if config.LOG_FILE else logging.NullHandler()
        ]
    )

def get_database_url() -> str:
    """Retorna URL do banco configurada"""
    return config.DATABASE_URL

def get_cors_config() -> dict:
    """Retorna configuração CORS"""
    return {
        "allow_origins": config.CORS_ORIGINS,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"]
    }

def get_supabase_config() -> dict:
    """Retorna configuração Supabase"""
    return {
        "url": config.SUPABASE_URL,
        "key": config.SUPABASE_ANON_KEY,
        "project_id": config.SUPABASE_PROJECT_ID
    }

# ================================
# VALIDAÇÃO DE CONFIGURAÇÃO
# ================================
def validate_config():
    """Valida configuração de produção"""
    errors = []
    
    # Validar Supabase
    if not config.SUPABASE_URL.startswith("https://"):
        errors.append("SUPABASE_URL deve começar com https://")
    
    if len(config.SUPABASE_ANON_KEY) < 100:
        errors.append("SUPABASE_ANON_KEY parece inválida")
    
    # Validar banco
    if "PASSWORD" in config.DATABASE_URL:
        errors.append("DATABASE_URL ainda contém placeholder PASSWORD")
    
    # Validar segurança
    if config.SECRET_KEY == "sua_chave_secreta_super_segura_discador_preditivo_2024":
        errors.append("SECRET_KEY deve ser alterada em produção")
    
    if errors:
        raise ValueError(f"Erros de configuração: {'; '.join(errors)}")
    
    return True

if __name__ == "__main__":
    try:
        validate_config()
        setup_logging()
        print("✅ Configuração de produção validada com sucesso!")
        print(f"🗄️ Banco: {config.DATABASE_URL[:50]}...")
        print(f"🌐 Supabase: {config.SUPABASE_URL}")
        print(f"🔒 Segurança: CORS configurado para {len(config.CORS_ORIGINS)} domínios")
    except ValueError as e:
        print(f"❌ Erro na configuração: {e}") 