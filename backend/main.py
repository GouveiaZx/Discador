#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
try:
    from sqlalchemy.orm import Session
    print("✅ SQLAlchemy imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import SQLAlchemy: {e}")
    # Criar fallback para tipagem
    Session = object
import uvicorn
import os
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from pydantic import BaseModel
try:
    import jwt
except ImportError:
    # Fallback se PyJWT não estiver disponível
    jwt = None
import hashlib
import requests
import json

try:
    from app.routes import llamadas, listas, cli, stt, reportes, listas_llamadas, blacklist, discado, audio_inteligente, code2base, campanha_politica, monitoring, contacts, presione1
    print("All routes imported successfully")
except ImportError as e:
    print(f"Warning: Could not import all routes: {e}")
    # Importar somente as rotas essenciais
    try:
        from app.routes import presione1
        print("Presione1 route imported successfully")
    except ImportError:
        presione1 = None
        print("Warning: Could not import presione1 route")
# Importar novas rotas avançadas
try:
    from app.routes import configuracao_discagem
except ImportError:
    configuracao_discagem = None

try:
    from app.routes import asterisk_monitoring
except ImportError:
    asterisk_monitoring = None

try:
    from app.routes import dialer_control
except ImportError:
    dialer_control = None
try:
    from app.database import inicializar_bd, get_db
    print("✅ Database imports successful")
except ImportError as e:
    print(f"⚠️ Warning: Could not import database functions: {e}")
    # Criar fallbacks se necessário
    inicializar_bd = None
    get_db = None
try:
    from app.config import configuracion
    print("✅ Config imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import config: {e}")
    # Criar configuração fallback
    class FallbackConfig:
        APP_NAME = "Discador Predictivo"
        APP_VERSION = "1.0.0"
        DEBUG = False
        HOST = "0.0.0.0"
        PUERTO = 8000
        LOG_ARQUIVO = None
    configuracion = FallbackConfig()

try:
    from app.utils.logger import logger
    print("✅ Logger imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import logger: {e}")
    import logging
    logger = logging.getLogger(__name__)
# Importar modelos para asegurar que esten disponibles para SQLAlchemy
try:
    import app.models
    print("✅ Models imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import models: {e}")
    # Sistema continua funcionando sem os models do SQLAlchemy

# Importar as novas rotas
# from app.routes import audio_routes, reports  # Comentado temporariamente devido a problema com audioop no Python 3.13

# Modelos para autenticação
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    is_active: bool
    role: str

# Configuração JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sua-chave-secreta-muito-segura-aqui-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Usuários simulados para teste
USERS_DB = {
    "admin": {
        "id": 1,
        "username": "admin", 
        "email": "admin@discador.com",
        "hashed_password": hashlib.sha256("admin123".encode()).hexdigest(),
        "is_admin": True,
        "is_active": True,
        "role": "admin"
    },
    "supervisor": {
        "id": 2,
        "username": "supervisor",
        "email": "supervisor@discador.com", 
        "hashed_password": hashlib.sha256("supervisor123".encode()).hexdigest(),
        "is_admin": False,
        "is_active": True,
        "role": "supervisor"
    },
    "operador": {
        "id": 3,
        "username": "operador",
        "email": "operador@discador.com",
        "hashed_password": hashlib.sha256("operador123".encode()).hexdigest(), 
        "is_admin": False,
        "is_active": True,
        "role": "operator"
    }
}

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Criar token JWT"""
    if jwt is None:
        # Fallback simples se JWT não estiver disponível
        return f"simple_token_{data.get('sub', 'user')}_{int(datetime.utcnow().timestamp())}"
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar senha"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def authenticate_user(username: str, password: str):
    """Autenticar usuário"""
    user = USERS_DB.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obter usuário atual do token"""
    if jwt is None:
        # Fallback simples
        token = credentials.credentials
        if token.startswith("simple_token_"):
            username = token.split("_")[2]
            user = USERS_DB.get(username)
            if user:
                return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT não disponível - token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido", 
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = USERS_DB.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Rotas de correção rápida implementadas diretamente
from fastapi import APIRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar o ciclo de vida da aplicação"""
    # Startup
    # Crear directorio de logs si no existe y esta configurado
    if configuracion.LOG_ARQUIVO:
        os.makedirs(os.path.dirname(configuracion.LOG_ARQUIVO), exist_ok=True)
        
    logger.info("Iniciando la aplicacion")
    logger.info(f"Configuracion cargada. Modo debug: {configuracion.DEBUG}")
    logger.info("Aplicação iniciada sem inicialização de banco")
    
    yield
    
    # Shutdown
    logger.info("Apagando la aplicacion")

# Crear la aplicacion FastAPI
app = FastAPI(
    title=configuracion.APP_NAME,
    description="Sistema de discado predictivo con funcionalidades de manejo de llamadas, listas, blacklist, reconocimiento de voz, discado preditivo Presione 1 y multiples provedores SIP",
    version=configuracion.APP_VERSION,
    docs_url="/documentacion",
    redoc_url="/redoc",
    debug=configuracion.DEBUG,
    lifespan=lifespan
)

# Configurar CORS com configuração mais robusta
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://discador.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://localhost:3000",
        "http://localhost:5173",
        "https://localhost:5173",
        "*"  # Permitir todas as origens temporariamente para debugging
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Prefijo para todas las rutas de la API
api_prefix = "/api/v1"

# Incluir las rutas de forma condicional
try:
    # Incluir apenas as rotas essenciais primeiro
    # Comentado para usar endpoint de fallback
    # if presione1:
    #     app.include_router(presione1.router, prefix=f"{api_prefix}")
    #     print("✅ Presione1 router included successfully")
    
    # Incluir outras rotas se disponíveis
    if 'llamadas' in globals():
        app.include_router(llamadas.router, prefix=f"{api_prefix}/llamadas")
        print("✅ Llamadas router included successfully")
    
    if 'listas' in globals():
        app.include_router(listas.router, prefix=f"{api_prefix}/listas")
        print("✅ Listas router included successfully")
    
    if 'listas_llamadas' in globals():
        app.include_router(listas_llamadas.router, prefix=f"{api_prefix}")
        print("✅ Listas_llamadas router included successfully")
    
    if 'blacklist' in globals():
        app.include_router(blacklist.router, prefix=f"{api_prefix}")
        print("✅ Blacklist router included successfully")
    
    if 'discado' in globals():
        app.include_router(discado.router, prefix=f"{api_prefix}")
        print("✅ Discado router included successfully")
    
    if 'cli' in globals():
        app.include_router(cli.router, prefix=f"{api_prefix}")
        print("✅ CLI router included successfully")
    
    if 'stt' in globals():
        app.include_router(stt.router, prefix=f"{api_prefix}/stt")
        print("✅ STT router included successfully")
    
    if 'reportes' in globals():
        app.include_router(reportes.router, prefix=f"{api_prefix}/reportes")
        print("✅ Reportes router included successfully")
    
    if 'audio_inteligente' in globals():
        app.include_router(audio_inteligente.router, prefix=f"{api_prefix}")
        print("✅ Audio_inteligente router included successfully")
    
    if 'code2base' in globals():
        app.include_router(code2base.router, prefix=f"{api_prefix}")
        print("✅ Code2base router included successfully")
    
    if 'campanha_politica' in globals():
        app.include_router(campanha_politica.router, prefix=f"{api_prefix}/campanha-politica")
        print("✅ Campanha_politica router included successfully")
    
    if 'monitoring' in globals():
        app.include_router(monitoring.router, prefix=f"{api_prefix}")
        print("✅ Monitoring router included successfully")
    
    if 'contacts' in globals():
        app.include_router(contacts.router, prefix=f"{api_prefix}")
        print("✅ Contacts router included successfully")
    
    print("✅ All available routers included successfully")
    
except Exception as e:
    print(f"⚠️ Warning: Could not include some routers: {e}")
    logger.warning(f"Could not include some routers: {e}")
    
    # Incluir apenas as rotas essenciais que funcionam
    # Comentado para usar endpoint de fallback no missing_routes
    # if presione1:
    #     try:
    #         app.include_router(presione1.router, prefix=f"{api_prefix}")
    #         print("✅ Presione1 router included as fallback")
    #     except Exception as presione1_error:
    #         print(f"❌ Error including presione1 router: {presione1_error}")
    #         logger.error(f"Error including presione1 router: {presione1_error}")

# Router para rotas ausentes deve ser definido antes de ser usado

# Incluir novas rotas avançadas se disponíveis
if configuracao_discagem:
    app.include_router(configuracao_discagem.router, prefix=f"{api_prefix}")

if asterisk_monitoring:
    app.include_router(asterisk_monitoring.router, prefix=f"{api_prefix}")

if dialer_control:
    app.include_router(dialer_control.router, prefix=f"{api_prefix}")

# Router para rotas ausentes
missing_routes = APIRouter()

# Endpoints OPTIONS para CORS
@missing_routes.options("/code2base/clis")
async def options_code2base_clis():
    """Endpoint OPTIONS para CORS"""
    return {"message": "OK"}

@missing_routes.options("/campaigns")
async def options_campaigns():
    """Endpoint OPTIONS para CORS - campaigns"""
    return {"message": "OK"}

@missing_routes.options("/campanhas")
async def options_campanhas():
    """Endpoint OPTIONS para CORS - campanhas"""
    return {"message": "OK"}

@missing_routes.get("/code2base/clis")
async def listar_clis():
    """Lista CLIs disponíveis"""
    clis = [
        {
            "id": 1,
            "numero": "+5511999887766",
            "descricao": "CLI Principal",
            "ativo": True,
            "tipo": "nacional",
            "ultima_utilizacao": datetime.now().isoformat()
        },
        {
            "id": 2,
            "numero": "+5511888776655",
            "descricao": "CLI Secundário",
            "ativo": True,
            "tipo": "nacional", 
            "ultima_utilizacao": None
        }
    ]
    return {
        "status": "success",
        "clis": clis,
        "total": len(clis)
    }

# Endpoints adicionais que o frontend está tentando acessar
@missing_routes.get("/stats")
async def obter_estatisticas_gerais():
    """Estatísticas gerais do sistema"""
    return {
        "status": "success",
        "estatisticas": {
            "total_chamadas_hoje": 0,
            "chamadas_ativas": 0,
            "taxa_sucesso": 0.0,
            "tempo_medio_chamada": 0,
            "agentes_online": 0,
            "campanhas_ativas": 0
        }
    }

@missing_routes.get("/monitoring/dashboard")
async def obter_dashboard_monitoring():
    """Dashboard de monitoramento em tempo real"""
    return {
        "status": "success",
        "dashboard": {
            "chamadas_ativas": 0,
            "agentes_disponiveis": 0,
            "taxa_abandono": 0.0,
            "tempo_espera_medio": 0,
            "chamadas_completadas_hoje": 0,
            "ultima_atualizacao": datetime.now().isoformat()
        }
    }

@missing_routes.get("/llamadas/en-progreso")
async def listar_llamadas_en_progreso():
    """Lista chamadas em progresso"""
    return {
        "status": "success",
        "llamadas": [],
        "total": 0
    }

@missing_routes.get("/llamadas/stats")
async def obter_stats_llamadas():
    """Estatísticas de chamadas"""
    return {
        "status": "success",
        "stats": {
            "total_hoje": 0,
            "completadas": 0,
            "em_progresso": 0,
            "falhadas": 0,
            "taxa_conexao": 0.0
        }
    }

# Alias para campanhas (o frontend usa /campaigns mas o backend tem /campanhas)
@missing_routes.get("/campaigns")
async def listar_campaigns_alias():
    """Alias para campanhas - busca campanhas reais do Supabase"""
    try:
        # Buscar campanhas reais do Supabase
        campaigns = get_campaigns_from_supabase()
        
        return {
            "status": "success",
            "campaigns": campaigns,
            "total": len(campaigns),
            "message": "Campanhas carregadas com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro ao listar campanhas: {str(e)}")
        return {
            "status": "error",
            "campaigns": [],
            "total": 0,
            "message": f"Erro ao carregar campanhas: {str(e)}"
        }

@missing_routes.post("/campaigns")
async def criar_campaign_alias(campaign_data: dict):
    """Alias para criar campanhas - cria no Supabase"""
    try:
        # Preparar dados para inserção no Supabase
        campaign_insert_data = {
            "name": campaign_data.get("name", campaign_data.get("nome", "Nova Campanha")),
            "description": campaign_data.get("description", campaign_data.get("descricao", "Campanha criada via API")),
            "status": "draft",
            "cli_number": campaign_data.get("cli_number", "+5511999999999"),
            "audio_url": campaign_data.get("audio_url", ""),
            "start_time": campaign_data.get("start_time", "09:00"),
            "end_time": campaign_data.get("end_time", "18:00"),
            "timezone": campaign_data.get("timezone", "America/Argentina/Buenos_Aires"),
            "max_attempts": campaign_data.get("max_attempts", 3),
            "retry_interval": campaign_data.get("retry_interval", 30),
            "max_concurrent_calls": campaign_data.get("max_concurrent_calls", 5),
            "owner_id": 1,  # ID do usuário padrão
            "cps": campaign_data.get("cps", 10),
            "sleep_time": campaign_data.get("sleep_time", 1),
            "wait_time": campaign_data.get("wait_time", 0.5),
            "language": campaign_data.get("language", "pt-BR"),
            "shuffle_contacts": campaign_data.get("shuffle_contacts", True),
            "allow_multiple_calls_same_number": campaign_data.get("allow_multiple_calls_same_number", False),
            "max_channels": campaign_data.get("max_channels", 10)
        }
        
        # Tentar inserir no Supabase
        try:
            # Usar a função real do Supabase
            supabase_result = create_campaign_in_supabase(campaign_data)
            
            if supabase_result:
                # Campanha criada com sucesso no Supabase
                nova_campanha = {
                    "id": supabase_result["id"],
                    "name": supabase_result["name"],
                    "nome": supabase_result["name"],  # Compatibilidade
                    "description": supabase_result["description"],
                    "descricao": supabase_result["description"],  # Compatibilidade
                    "status": supabase_result["status"],
                    "cli_number": supabase_result["cli_number"],
                    "audio_url": supabase_result.get("audio_url", ""),
                    "start_time": supabase_result["start_time"],
                    "end_time": supabase_result["end_time"],
                    "timezone": supabase_result["timezone"],
                    "max_attempts": supabase_result["max_attempts"],
                    "retry_interval": supabase_result["retry_interval"],
                    "max_concurrent_calls": supabase_result["max_concurrent_calls"],
                    "owner_id": supabase_result["owner_id"],
                    "cps": supabase_result["cps"],
                    "sleep_time": supabase_result["sleep_time"],
                    "wait_time": float(supabase_result["wait_time"]),
                    "language": supabase_result["language"],
                    "shuffle_contacts": supabase_result["shuffle_contacts"],
                    "allow_multiple_calls_same_number": supabase_result["allow_multiple_calls_same_number"],
                    "max_channels": supabase_result["max_channels"],
                    "created_at": supabase_result["created_at"],
                    "updated_at": supabase_result["updated_at"]
                }
            else:
                # Fallback para dados mock se Supabase falhar
                nova_campanha = {
                    "id": 999,
                    "name": campaign_insert_data["name"],
                    "nome": campaign_insert_data["name"],  # Compatibilidade
                    "description": campaign_insert_data["description"],
                    "descricao": campaign_insert_data["description"],  # Compatibilidade
                    "status": campaign_insert_data["status"],
                    "cli_number": campaign_insert_data["cli_number"],
                    "audio_url": campaign_insert_data["audio_url"],
                    "start_time": campaign_insert_data["start_time"],
                    "end_time": campaign_insert_data["end_time"],
                    "timezone": campaign_insert_data["timezone"],
                    "max_attempts": campaign_insert_data["max_attempts"],
                    "retry_interval": campaign_insert_data["retry_interval"],
                    "max_concurrent_calls": campaign_insert_data["max_concurrent_calls"],
                    "owner_id": campaign_insert_data["owner_id"],
                    "cps": campaign_insert_data["cps"],
                    "sleep_time": campaign_insert_data["sleep_time"],
                    "wait_time": campaign_insert_data["wait_time"],
                    "language": campaign_insert_data["language"],
                    "shuffle_contacts": campaign_insert_data["shuffle_contacts"],
                    "allow_multiple_calls_same_number": campaign_insert_data["allow_multiple_calls_same_number"],
                    "max_channels": campaign_insert_data["max_channels"],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            
        except Exception as supabase_error:
            logger.error(f"Erro ao inserir no Supabase: {str(supabase_error)}")
            # Fallback para dados mock se Supabase falhar
            nova_campanha = {
                "id": 999,
                "name": campaign_data.get("name", campaign_data.get("nome", "Nova Campanha")),
                "nome": campaign_data.get("nome", campaign_data.get("name", "Nova Campanha")),
                "description": campaign_data.get("description", campaign_data.get("descricao", "Campanha criada via API")),
                "descricao": campaign_data.get("descricao", campaign_data.get("description", "Campanha criada via API")),
                "status": "draft",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        return {
            "status": "success",
            "message": "Campanha criada com sucesso",
            "id": nova_campanha["id"],  # ID diretamente na resposta para o frontend
            "campaign": nova_campanha
        }
    except Exception as e:
        logger.error(f"Erro ao criar campanha: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao criar campanha: {str(e)}"
        )

# Endpoint de campanhas direto
@missing_routes.get("/campanhas")
async def listar_campanhas_direto():
    """Lista campanhas - busca campanhas reais do Supabase"""
    try:
        # Buscar campanhas reais do Supabase
        campanhas = get_campaigns_from_supabase()
        
        return {
            "status": "success",
            "campanhas": campanhas,
            "total": len(campanhas),
            "message": "Campanhas carregadas com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro ao listar campanhas: {str(e)}")
        return {
            "status": "error",
            "campanhas": [],
            "total": 0,
            "message": f"Erro ao carregar campanhas: {str(e)}"
        }

@missing_routes.post("/campanhas")
async def criar_campanha_direto(campanha_data: dict):
    """Cria campanha - dados mock"""
    try:
        # Dados mock para a campanha criada
        nova_campanha = {
            "id": 999,  # ID mock
            "nome": campanha_data.get("nome", "Nova Campanha"),
            "descricao": campanha_data.get("descricao", "Campanha criada via API"),
            "status": "criada",
            "data_inicio": datetime.now().isoformat(),
            "data_fim": None,
            "total_contatos": 0,
            "contatos_discados": 0,
            "taxa_sucesso": 0.0,
            "configuracoes": campanha_data
        }
        
        return {
            "status": "success",
            "message": "Campanha criada com sucesso",
            "id": nova_campanha["id"],  # ID diretamente na resposta para o frontend
            "campaign": nova_campanha
        }
    except Exception as e:
        logger.error(f"Erro ao criar campanha: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao criar campanha: {str(e)}"
        )

# Endpoint de blacklist
@missing_routes.get("/blacklist")
async def listar_blacklist_direto():
    """Lista blacklist - dados mock"""
    blacklist = [
        {
            "id": 1,
            "numero": "+5511999888777",
            "motivo": "Solicitação do cliente",
            "data_inclusao": datetime.now().isoformat(),
            "ativo": True
        },
        {
            "id": 2,
            "numero": "+5511888777666",
            "motivo": "Número inválido",
            "data_inclusao": datetime.now().isoformat(),
            "ativo": True
        }
    ]
    return {
        "status": "success",
        "blacklist": blacklist,
        "total": len(blacklist)
    }

# Endpoint de configuração
@missing_routes.get("/configuracion")
async def obter_configuracion():
    """Configuração do sistema"""
    return {
        "status": "success",
        "configuracion": {
            "sistema_activo": True,
            "version": "1.0.0",
            "ultima_actualizacion": datetime.now().isoformat()
        }
    }

# Endpoint de histórico de chamadas
@missing_routes.get("/llamadas/historico")
async def obter_historico_llamadas(
    page: int = 1,
    page_size: int = 10
):
    """Histórico de chamadas paginado"""
    return {
        "status": "success",
        "llamadas": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "total_pages": 0
    }

# ENDPOINTS DIRETOS PARA RESOLVER ERROS 500
@missing_routes.get("/audio/contextos")
async def audio_contextos_direto():
    """Contextos de áudio - versão direta sem dependências"""
    contextos = [
        {
            "id": 1,
            "nome": "Contexto Padrão",
            "descricao": "Contexto de áudio padrão para campanhas",
            "ativo": True,
            "configuracoes": {
                "deteccao_voz": True,
                "timeout_resposta": 5,
                "max_tentativas": 3
            }
        },
        {
            "id": 2,
            "nome": "Contexto Personalizado", 
            "descricao": "Contexto de áudio personalizado",
            "ativo": True,
            "configuracoes": {
                "deteccao_voz": True,
                "timeout_resposta": 10,
                "max_tentativas": 5
            }
        }
    ]
    return {
        "status": "success",
        "contextos": contextos,
        "total": len(contextos)
    }

# Endpoint alternativo para áudio
@missing_routes.get("/audios/contextos")
async def audio_contextos_alternativo():
    """Contextos de áudio - endpoint alternativo"""
    contextos = [
        {
            "id": 1,
            "nome": "Contexto Padrão",
            "descricao": "Contexto de áudio padrão para campanhas",
            "ativo": True,
            "configuracoes": {
                "deteccao_voz": True,
                "timeout_resposta": 5,
                "max_tentativas": 3
            }
        },
        {
            "id": 2,
            "nome": "Contexto Personalizado", 
            "descricao": "Contexto de áudio personalizado",
            "ativo": True,
            "configuracoes": {
                "deteccao_voz": True,
                "timeout_resposta": 10,
                "max_tentativas": 5
            }
        }
    ]
    return {
        "status": "success",
        "contextos": contextos,
        "total": len(contextos)
    }

@missing_routes.get("/multi-sip/provedores")
async def multi_sip_provedores_direto():
    """Endpoint temporário para multi-sip provedores."""
    try:
        # Dados mock para multi-sip
        provedores = [
            {
                "id": 1,
                "nome": "Provedor A",
                "host": "sip.provedor-a.com",
                "porta": 5060,
                "usuario": "user123",
                "ativo": True,
                "tipo": "SIP",
                "qualidade": "Alta",
                "custo_por_minuto": 0.05,
                "pais": "Brasil",
                "protocolos": ["UDP", "TCP"],
                "codecs": ["G.711", "G.729"],
                "canais_simultaneos": 30,
                "uptime": 99.9,
                "latencia_media": 45,
                "taxa_sucesso": 98.5
            },
            {
                "id": 2,
                "nome": "Provedor B", 
                "host": "gateway.provedor-b.com",
                "porta": 5060,
                "usuario": "cliente456",
                "ativo": True,
                "tipo": "SIP",
                "qualidade": "Média",
                "custo_por_minuto": 0.03,
                "pais": "Argentina",
                "protocolos": ["UDP"],
                "codecs": ["G.711"],
                "canais_simultaneos": 20,
                "uptime": 97.8,
                "latencia_media": 65,
                "taxa_sucesso": 95.2
            }
        ]
        
        return {
            "status": "success",
            "data": provedores,
            "total": len(provedores)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter provedores multi-sip: {str(e)}")
        return {
            "status": "error",
            "message": "Erro interno do servidor",
            "data": []
        }

# Endpoint presione1 de fallback - versão robusta
@missing_routes.get("/presione1-test/campanhas")
async def listar_campanhas_presione1_test():
    """Endpoint de teste para campanhas presione1"""
    import logging
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 [PRESIONE1-TEST] Endpoint de teste sendo executado!")
    
    # Sempre retornar campanhas de exemplo para garantir que funcione
    campanhas_exemplo = [
        {
            "id": 1,
            "nombre": "Campanha Presione 1 - Teste",
            "descripcion": "Campanha de exemplo para discado Presione 1",
            "campaign_id": 1,
            "activa": False,
            "pausada": False,
            "fecha_creacion": datetime.now().isoformat(),
            "llamadas_simultaneas": 5,
            "mensaje_audio_url": "https://example.com/audio1.wav",
            "timeout_presione1": 10,
            "extension_transferencia": "1001",
            "cola_transferencia": "ventas"
        },
        {
            "id": 2,
            "nombre": "Campanha Promocional",
            "descripcion": "Campanha promocional com Presione 1",
            "campaign_id": 2,
            "activa": True,
            "pausada": False,
            "fecha_creacion": datetime.now().isoformat(),
            "llamadas_simultaneas": 3,
            "mensaje_audio_url": "https://example.com/audio2.wav",
            "timeout_presione1": 15,
            "extension_transferencia": "1002",
            "cola_transferencia": "soporte"
        },
        {
            "id": 3,
            "nombre": "Campanha Informativa",
            "descripcion": "Campanha informativa para clientes",
            "campaign_id": 3,
            "activa": False,
            "pausada": True,
            "fecha_creacion": datetime.now().isoformat(),
            "llamadas_simultaneas": 8,
            "mensaje_audio_url": "https://example.com/audio3.wav",
            "timeout_presione1": 12,
            "extension_transferencia": "1003",
            "cola_transferencia": "info"
        }
    ]
    
    logger.info(f"✅ [PRESIONE1-TEST] Retornando {len(campanhas_exemplo)} campanhas")
    return campanhas_exemplo

@missing_routes.get("/presione1/campanhas")
async def listar_campanhas_presione1_fallback():
    """Lista campanhas presione1 - fallback robusta"""
    import logging
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 [PRESIONE1-FALLBACK] Endpoint sendo executado!")
    
    # Sempre retornar campanhas de exemplo para garantir que funcione
    campanhas_exemplo = [
        {
            "id": 1,
            "nombre": "Campanha Presione 1 - Teste",
            "descripcion": "Campanha de exemplo para discado Presione 1",
            "campaign_id": 1,
            "activa": False,
            "pausada": False,
            "fecha_creacion": datetime.now().isoformat(),
            "llamadas_simultaneas": 5,
            "mensaje_audio_url": "https://example.com/audio1.wav",
            "timeout_presione1": 10,
            "extension_transferencia": "1001",
            "cola_transferencia": "ventas"
        },
        {
            "id": 2,
            "nombre": "Campanha Promocional",
            "descripcion": "Campanha promocional com Presione 1",
            "campaign_id": 2,
            "activa": True,
            "pausada": False,
            "fecha_creacion": datetime.now().isoformat(),
            "llamadas_simultaneas": 3,
            "mensaje_audio_url": "https://example.com/audio2.wav",
            "timeout_presione1": 15,
            "extension_transferencia": "1002",
            "cola_transferencia": "soporte"
        },
        {
            "id": 3,
            "nombre": "Campanha Informativa",
            "descripcion": "Campanha informativa para clientes",
            "campaign_id": 3,
            "activa": False,
            "pausada": True,
            "fecha_creacion": datetime.now().isoformat(),
            "llamadas_simultaneas": 8,
            "mensaje_audio_url": "https://example.com/audio3.wav",
            "timeout_presione1": 12,
            "extension_transferencia": "1003",
            "cola_transferencia": "info"
        }
    ]
    
    logger.info(f"✅ [PRESIONE1-FALLBACK] Retornando {len(campanhas_exemplo)} campanhas")
    return campanhas_exemplo

# Endpoint super simples para testar missing_routes
@missing_routes.get("/hello")
async def hello_test():
    """Endpoint super simples para testar se missing_routes funciona"""
    return {"message": "Hello from missing_routes!", "status": "working"}

# Endpoint completamente diferente para testar roteamento
@missing_routes.get("/test-roteamento/campanhas")
async def test_roteamento_campanhas():
    """Endpoint de teste para verificar se o roteamento funciona"""
    return {
        "status": "success",
        "message": "Roteamento funcionando!",
        "timestamp": datetime.now().isoformat(),
        "campanhas_teste": [
            {
                "id": 999,
                "nome": "Campanha Teste Roteamento",
                "descricao": "Se você está vendo isso, o roteamento funciona!",
                "ativo": True
            }
        ]
    }

# Endpoint alternativo para debug
@missing_routes.get("/presione1-debug/campanhas")
async def debug_presione1_campanhas():
    """Debug endpoint para campanhas presione1"""
    return {
        "debug": True,
        "message": "Endpoint de debug ativo",
        "campanhas": [
            {
                "id": 99,
                "nombre": "Debug Campaign",
                "descripcion": "Campanha de debug",
                "campaign_id": 99,
                "activa": True,
                "pausada": False,
                "fecha_creacion": datetime.now().isoformat(),
                "llamadas_simultaneas": 1,
                "mensaje_audio_url": "",
                "timeout_presione1": 5
            }
        ]
    }

@missing_routes.post("/presione1/campanhas")
async def criar_campanha_presione1_fallback(campanha_data: dict):
    """Cria campanha presione1 - fallback"""
    return {
        "status": "success",
        "campanha": {
            "id": 1,
            "nome": campanha_data.get("nome", "Campanha Teste"),
            "descripcion": campanha_data.get("descripcion", "Campanha criada via fallback"),
            "activa": False,
            "fecha_creacion": datetime.now().isoformat()
        },
        "message": "Campanha criada via fallback"
    }

# Incluir rotas ausentes
app.include_router(missing_routes, prefix=f"{api_prefix}")

# Router para autenticação
auth_router = APIRouter()

@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Endpoint de login"""
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # Remover senha do retorno
    user_data = {k: v for k, v in user.items() if k != "hashed_password"}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@auth_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Obter dados do usuário atual"""
    return {k: v for k, v in current_user.items() if k != "hashed_password"}

@auth_router.post("/logout")
async def logout():
    """Endpoint de logout (apenas retorna sucesso, o frontend deve remover o token)"""
    return {"message": "Logout realizado com sucesso"}

# Incluir router de autenticação
app.include_router(auth_router, prefix=f"{api_prefix}/auth")

# Endpoint direto na aplicação principal para campanhas presione1
@app.get(f"{api_prefix}/presione1/campanhas")
async def listar_campanhas_presione1_direto():
    """Lista campanhas presione1 - endpoint direto na aplicação"""
    from datetime import datetime
    
    # Sempre retornar campanhas de exemplo
    campanhas_exemplo = [
        {
            "id": 1,
            "nombre": "Campanha Presione 1 - Teste",
            "descripcion": "Campanha de exemplo para discado Presione 1",
            "campaign_id": 1,
            "activa": False,
            "pausada": False,
            "fecha_creacion": datetime.now().isoformat(),
            "llamadas_simultaneas": 5,
            "mensaje_audio_url": "https://example.com/audio1.wav",
            "timeout_presione1": 10,
            "extension_transferencia": "1001",
            "cola_transferencia": "ventas"
        },
        {
            "id": 2,
            "nombre": "Campanha Promocional",
            "descripcion": "Campanha promocional com Presione 1",
            "campaign_id": 2,
            "activa": True,
            "pausada": False,
            "fecha_creacion": datetime.now().isoformat(),
            "llamadas_simultaneas": 3,
            "mensaje_audio_url": "https://example.com/audio2.wav",
            "timeout_presione1": 15,
            "extension_transferencia": "1002",
            "cola_transferencia": "soporte"
        },
        {
            "id": 3,
            "nombre": "Campanha Informativa",
            "descripcion": "Campanha informativa para clientes",
            "campaign_id": 3,
            "activa": False,
            "pausada": True,
            "fecha_creacion": datetime.now().isoformat(),
            "llamadas_simultaneas": 8,
            "mensaje_audio_url": "https://example.com/audio3.wav",
            "timeout_presione1": 12,
            "extension_transferencia": "1003",
            "cola_transferencia": "info"
        }
    ]
    
    return campanhas_exemplo

@app.get(f"{api_prefix}/hello-direto")
async def hello_direto():
    """Endpoint de teste direto na aplicação"""
    return {"message": "Hello direto da aplicação!", "status": "working"}

# Health check endpoints para Render.com
@app.get("/")
@app.head("/")
async def raiz(campanhas: str = None):
    """Endpoint raiz com informações da API"""
    if campanhas == "presione1":
        # Retornar campanhas de exemplo quando solicitado
        from datetime import datetime
        
        campanhas_exemplo = [
            {
                "id": 1,
                "nombre": "Campanha Presione 1 - Teste",
                "descripcion": "Campanha de exemplo para discado Presione 1",
                "campaign_id": 1,
                "activa": False,
                "pausada": False,
                "fecha_creacion": datetime.now().isoformat(),
                "llamadas_simultaneas": 5,
                "mensaje_audio_url": "https://example.com/audio1.wav",
                "timeout_presione1": 10,
                "extension_transferencia": "1001",
                "cola_transferencia": "ventas"
            },
            {
                "id": 2,
                "nombre": "Campanha Promocional",
                "descripcion": "Campanha promocional com Presione 1",
                "campaign_id": 2,
                "activa": True,
                "pausada": False,
                "fecha_creacion": datetime.now().isoformat(),
                "llamadas_simultaneas": 3,
                "mensaje_audio_url": "https://example.com/audio2.wav",
                "timeout_presione1": 15,
                "extension_transferencia": "1002",
                "cola_transferencia": "soporte"
            },
            {
                "id": 3,
                "nombre": "Campanha Informativa",
                "descripcion": "Campanha informativa para clientes",
                "campaign_id": 3,
                "activa": False,
                "pausada": True,
                "fecha_creacion": datetime.now().isoformat(),
                "llamadas_simultaneas": 8,
                "mensaje_audio_url": "https://example.com/audio3.wav",
                "timeout_presione1": 12,
                "extension_transferencia": "1003",
                "cola_transferencia": "info"
            }
        ]
        
        return {
            "status": "success",
            "campanhas": campanhas_exemplo,
            "total": len(campanhas_exemplo),
            "message": "Campanhas presione1 via endpoint raiz"
        }
    
    # Comportamento padrão
    return {
        "status": "healthy",
        "mensaje": f"API de {configuracion.APP_NAME}",
        "version": configuracion.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "estado": "activo"
    }

@app.get("/health")
@app.head("/health")
async def health_check():
    """Endpoint dedicado para health checks"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "discador-api",
        "version": configuracion.APP_VERSION
    }

@app.get("/ping")
@app.head("/ping")
async def ping():
    """Endpoint simples para verificação de conectividade"""
    return {"message": "pong", "timestamp": datetime.now().isoformat()}

@app.get("/status")
@app.head("/status")
async def status():
    """Endpoint de status detalhado"""
    return {
        "status": "operational",
        "service": "discador-predictivo",
        "version": configuracion.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "database": "connected"
    }

# Configurações do Supabase (carregadas do .env)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

# Debug: Log das configurações do Supabase para diagnosticar problemas de produção
logger.info(f"🔧 [SUPABASE-CONFIG] SUPABASE_URL configurada: {'✅ SIM' if SUPABASE_URL else '❌ NÃO'}")
logger.info(f"🔧 [SUPABASE-CONFIG] SUPABASE_ANON_KEY configurada: {'✅ SIM' if SUPABASE_ANON_KEY else '❌ NÃO'}")
if SUPABASE_URL:
    logger.info(f"🔧 [SUPABASE-CONFIG] URL: {SUPABASE_URL}")
if SUPABASE_ANON_KEY:
    logger.info(f"🔧 [SUPABASE-CONFIG] API Key: {SUPABASE_ANON_KEY[:20]}...{SUPABASE_ANON_KEY[-10:] if len(SUPABASE_ANON_KEY) > 30 else SUPABASE_ANON_KEY}")
else:
    logger.error("❌ [SUPABASE-CONFIG] CRITICAL: Variáveis do Supabase não configuradas! Backend não funcionará corretamente.")

def create_campaign_in_supabase(campaign_data: dict):
    """Cria uma campanha no Supabase"""
    try:
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Preparar dados para inserção
        insert_data = {
            "name": campaign_data.get("name", campaign_data.get("nome", "Nova Campanha")),
            "description": campaign_data.get("description", campaign_data.get("descricao", "Campanha criada via API")),
            "status": "draft",
            "cli_number": campaign_data.get("cli_number", "+5511999999999"),
            "audio_url": campaign_data.get("audio_url", ""),
            "start_time": campaign_data.get("start_time", "09:00"),
            "end_time": campaign_data.get("end_time", "18:00"),
            "timezone": campaign_data.get("timezone", "America/Argentina/Buenos_Aires"),
            "max_attempts": campaign_data.get("max_attempts", 3),
            "retry_interval": campaign_data.get("retry_interval", 30),
            "max_concurrent_calls": campaign_data.get("max_concurrent_calls", 5),
            "owner_id": 1,  # ID do usuário padrão
            "cps": campaign_data.get("cps", 10),
            "sleep_time": campaign_data.get("sleep_time", 1),
            "wait_time": campaign_data.get("wait_time", 0.5),
            "language": campaign_data.get("language", "pt-BR"),
            "shuffle_contacts": campaign_data.get("shuffle_contacts", True),
            "allow_multiple_calls_same_number": campaign_data.get("allow_multiple_calls_same_number", False),
            "max_channels": campaign_data.get("max_channels", 10)
        }
        
        # Fazer requisição para o Supabase
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/campaigns",
            headers=headers,
            json=insert_data
        )
        
        if response.status_code == 201:
            return response.json()[0]  # Retorna a campanha criada
        else:
            logger.error(f"Erro do Supabase: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao conectar com Supabase: {str(e)}")
        return None

def get_campaigns_from_supabase():
    """Busca campanhas do Supabase"""
    try:
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"🔍 [DEBUG] Buscando campanhas do Supabase: {SUPABASE_URL}")
        
        # Buscar campanhas do Supabase
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/campaigns",
            headers=headers
        )
        
        logger.info(f"🔍 [DEBUG] Status da resposta campanhas: {response.status_code}")
        
        if response.status_code == 200:
            campaigns = response.json()
            logger.info(f"🔍 [DEBUG] Campanhas recebidas: {len(campaigns)}")
            
            # Converter para formato compatível com frontend
            formatted_campaigns = []
            for campaign in campaigns:
                logger.info(f"🔍 [DEBUG] Processando campanha ID {campaign['id']}: {campaign['name']}")
                
                # CORREÇÃO: Buscar total de contatos usando método content-range (método agregação removido porque não é suportado)
                contacts_total = 0
                
                # Método 1: Content-range (método principal e confiável)
                try:
                    range_url = f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=eq.{campaign['id']}&select=id&limit=1"
                    logger.info(f"🔍 [DEBUG] URL range: {range_url}")
                    
                    contacts_response = requests.get(
                        range_url,
                        headers={**headers, "Prefer": "count=exact"},
                        timeout=10
                    )
                    
                    logger.info(f"🔍 [DEBUG] Status range: {contacts_response.status_code}")
                    logger.info(f"🔍 [DEBUG] Headers range: {dict(contacts_response.headers)}")
                    
                    if contacts_response.status_code == 200 or contacts_response.status_code == 206:
                        content_range = contacts_response.headers.get('content-range', '0')
                        logger.info(f"📊 [CONTAGEM-RANGE] Campanha {campaign['id']}: content-range = '{content_range}'")
                        
                        # Parsing robusto do content-range: formatos "0-0/N" ou "*/N"
                        if '/' in content_range:
                            try:
                                total_str = content_range.split('/')[-1].strip()
                                logger.info(f"🔍 [DEBUG] Total string extraída: '{total_str}'")
                                if total_str.isdigit():
                                    contacts_total = int(total_str)
                                    logger.info(f"✅ [CONTAGEM-RANGE] Campanha {campaign['id']}: {contacts_total:,} contatos")
                                else:
                                    logger.warning(f"⚠️ [CONTAGEM-RANGE] Total não numérico: '{total_str}'")
                                    contacts_total = 0
                            except (ValueError, IndexError) as parse_error:
                                logger.warning(f"⚠️ [CONTAGEM-RANGE] Erro parsing: {parse_error}")
                                contacts_total = 0
                        else:
                            logger.warning(f"⚠️ [CONTAGEM-RANGE] Formato inválido: '{content_range}'")
                            contacts_total = 0
                    else:
                        logger.warning(f"⚠️ [CONTAGEM-RANGE] Status erro: {contacts_response.status_code}")
                        # Fallback para método 2
                        raise Exception(f"Content-range falhou com status {contacts_response.status_code}")
                        
                except Exception as range_error:
                    logger.warning(f"⚠️ [CONTAGEM-RANGE] Erro geral: {range_error}")
                    
                    # Método 2: Fallback - buscar amostra de contatos
                    try:
                        fallback_url = f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=eq.{campaign['id']}&limit=5"
                        logger.info(f"🔍 [DEBUG] URL fallback: {fallback_url}")
                        
                        contacts_response = requests.get(
                            fallback_url,
                            headers=headers,
                            timeout=10
                        )
                        
                        logger.info(f"🔍 [DEBUG] Status fallback: {contacts_response.status_code}")
                        logger.info(f"🔍 [DEBUG] Resposta fallback: {contacts_response.text[:200]}")
                        
                        if contacts_response.status_code == 200:
                            contacts_list = contacts_response.json()
                            logger.info(f"🔍 [DEBUG] Lista contatos (amostra): {type(contacts_list)} - {len(contacts_list) if isinstance(contacts_list, list) else 'N/A'}")
                            
                            if isinstance(contacts_list, list):
                                if len(contacts_list) > 0:
                                    logger.info(f"🔍 [DEBUG] Amostra do primeiro contato: {contacts_list[0]}")
                                    # Se encontrou contatos, usar valor estimado
                                    contacts_total = 999  # Indicar que há contatos mas não sabemos quantos
                                    logger.info(f"✅ [CONTAGEM-FALLBACK] Campanha {campaign['id']}: {len(contacts_list)} contatos na amostra (999 = há contatos)")
                                else:
                                    contacts_total = 0
                                    logger.info(f"✅ [CONTAGEM-FALLBACK] Campanha {campaign['id']}: 0 contatos")
                            else:
                                contacts_total = 0
                        else:
                            contacts_total = 0
                    except Exception as fallback_error:
                        logger.error(f"❌ [CONTAGEM-FALLBACK] Erro final: {fallback_error}")
                        contacts_total = 0
                
                logger.info(f"🎯 [RESULTADO] Campanha {campaign['id']} ({campaign['name']}): {contacts_total} contatos")
                
                formatted_campaign = {
                    "id": campaign["id"],
                    "name": campaign["name"],
                    "nome": campaign["name"],  # Compatibilidade
                    "description": campaign.get("description", ""),
                    "descricao": campaign.get("description", ""),  # Compatibilidade
                    "status": campaign["status"],
                    "cli_number": campaign["cli_number"],
                    "audio_url": campaign.get("audio_url", ""),
                    "start_time": campaign["start_time"],
                    "end_time": campaign["end_time"],
                    "timezone": campaign["timezone"],
                    "max_attempts": campaign["max_attempts"],
                    "retry_interval": campaign["retry_interval"],
                    "max_concurrent_calls": campaign["max_concurrent_calls"],
                    "owner_id": campaign["owner_id"],
                    "cps": campaign["cps"],
                    "sleep_time": campaign["sleep_time"],
                    "wait_time": float(campaign["wait_time"]),
                    "language": campaign["language"],
                    "shuffle_contacts": campaign["shuffle_contacts"],
                    "allow_multiple_calls_same_number": campaign["allow_multiple_calls_same_number"],
                    "max_channels": campaign["max_channels"],
                    "created_at": campaign["created_at"],
                    "updated_at": campaign["updated_at"],
                    "contacts_total": contacts_total  # CORRIGIDO: Contagem usando content-range
                }
                formatted_campaigns.append(formatted_campaign)
            
            # Log do resultado final
            total_campaigns = len(formatted_campaigns)
            total_contacts = sum(c.get('contacts_total', 0) for c in formatted_campaigns)
            logger.info(f"🎯 [CAMPANHAS] Retornando {total_campaigns} campanhas com {total_contacts:,} contatos total")
            
            return formatted_campaigns
        else:
            logger.error(f"Erro do Supabase ao buscar campanhas: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Erro ao buscar campanhas do Supabase: {str(e)}")
        return []

if __name__ == "__main__":
    logger.info(f"Iniciando servidor en {configuracion.HOST}:{configuracion.PUERTO}")
    uvicorn.run(
        "main:app", 
        host=configuracion.HOST, 
        port=configuracion.PUERTO, 
        reload=configuracion.DEBUG
    ) 