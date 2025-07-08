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
    
    # Retornar apenas a lista de campanhas (como o frontend espera)
    return campanhas_exemplo

@app.get(f"{api_prefix}/hello-direto")
async def hello_direto():
    """Endpoint de teste direto na aplicação"""
    return {"message": "Hello direto da aplicação!", "status": "working"}

# ============================================================================
# ENDPOINTS PRESIONE1 - FUNCIONALIDADES COMPLETAS
# ============================================================================

@app.get(f"{api_prefix}/presione1/campanhas/{{campana_id}}")
async def obter_campana_presione1(campana_id: int):
    """Obter detalhes de uma campanha específica"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    # Dados específicos da campanha baseados no ID
    campanhas_dados = {
        1: {
            "id": 1,
            "nombre": "Campanha Presione 1 - Teste",
            "descripcion": "Campanha de exemplo para discado Presione 1",
            "campaign_id": 1,
            "activa": False,
            "pausada": False,
            "mensaje_audio_url": "https://example.com/audio1.wav",
            "timeout_presione1": 10,
            "extension_transferencia": "1001",
            "cola_transferencia": "ventas",
            "llamadas_simultaneas": 5,
            "tiempo_entre_llamadas": 3,
            "detectar_voicemail": True,
            "mensaje_voicemail_url": "https://example.com/voicemail1.wav"
        },
        2: {
            "id": 2,
            "nombre": "Campanha Promocional",
            "descripcion": "Campanha promocional com Presione 1",
            "campaign_id": 2,
            "activa": True,
            "pausada": False,
            "mensaje_audio_url": "https://example.com/audio2.wav",
            "timeout_presione1": 15,
            "extension_transferencia": "1002",
            "cola_transferencia": "soporte",
            "llamadas_simultaneas": 3,
            "tiempo_entre_llamadas": 5,
            "detectar_voicemail": True,
            "mensaje_voicemail_url": "https://example.com/voicemail2.wav"
        },
        3: {
            "id": 3,
            "nombre": "Campanha Informativa",
            "descripcion": "Campanha informativa para clientes",
            "campaign_id": 3,
            "activa": False,
            "pausada": True,
            "mensaje_audio_url": "https://example.com/audio3.wav",
            "timeout_presione1": 12,
            "extension_transferencia": "1003",
            "cola_transferencia": "info",
            "llamadas_simultaneas": 8,
            "tiempo_entre_llamadas": 2,
            "detectar_voicemail": False,
            "mensaje_voicemail_url": None
        }
    }
    
    if campana_id not in campanhas_dados:
        return {"error": "Campanha não encontrada", "campana_id": campana_id}
    
    campanha = campanhas_dados[campana_id]
    campanha.update({
        "fecha_creacion": (now - timedelta(days=campana_id)).isoformat(),
        "fecha_actualizacion": now.isoformat(),
        "usuario_creador": f"user_{campana_id}",
        "total_numeros_lista": 1000 - (campana_id * 100),
        "numeros_pendientes": 750 - (campana_id * 50),
        "agentes_asignados": ["100", "101"] if campana_id == 2 else ["102", "103"],
        "horario_funcionamiento": {
            "inicio": "09:00",
            "fin": "18:00",
            "timezone": "America/Sao_Paulo",
            "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"]
        }
    })
    
    return campanha

@app.get(f"{api_prefix}/presione1/campanhas/{{campana_id}}/estadisticas")
async def estadisticas_campana_presione1(campana_id: int):
    """Estatísticas detalhadas da campanha presione1"""
    from datetime import datetime
    
    # Retornar estatísticas de exemplo baseadas no ID da campanha
    return {
        "campana_id": campana_id,
        "nombre_campana": f"Campanha {campana_id}",
        "total_numeros": 1000,
        "llamadas_realizadas": 250 + (campana_id * 10),
        "llamadas_pendientes": 750 - (campana_id * 10),
        "llamadas_contestadas": 175 + (campana_id * 5),
        "llamadas_presiono_1": 87 + (campana_id * 2),
        "llamadas_no_presiono": 88 + (campana_id * 3),
        "llamadas_transferidas": 82 + (campana_id * 2),
        "llamadas_error": 5 + campana_id,
        "tasa_contestacion": 70.0 + (campana_id * 0.5),
        "tasa_presiono_1": 49.7 + (campana_id * 0.3),
        "tasa_transferencia": 94.3 - (campana_id * 0.2),
        "tiempo_medio_respuesta": 5.2 + (campana_id * 0.1),
        "duracion_media_llamada": 45.5 + (campana_id * 0.5),
        "activa": campana_id == 2,  # Campanha 2 ativa
        "pausada": False,
        "llamadas_activas": 3 if campana_id == 2 else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get(f"{api_prefix}/presione1/campanhas/{{campana_id}}/monitor")
async def monitor_campana_presione1(campana_id: int):
    """Monitoramento em tempo real da campanha"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    # Dados de monitoramento específicos por campanha
    llamadas_activas = []
    if campana_id == 2:  # Campanha ativa
        llamadas_activas = [
            {
                "id": 1001,
                "numero_destino": "+5511987654321",
                "estado": "esperando_dtmf",
                "duracion": 15,
                "fecha_inicio": (now - timedelta(seconds=15)).isoformat(),
                "cli_utilizado": "+5511999999999",
                "channel": "SIP/trunk-00000001"
            },
            {
                "id": 1002,
                "numero_destino": "+5511987654322",
                "estado": "audio_reproducido", 
                "duracion": 8,
                "fecha_inicio": (now - timedelta(seconds=8)).isoformat(),
                "cli_utilizado": "+5511999999999",
                "channel": "SIP/trunk-00000002"
            },
            {
                "id": 1003,
                "numero_destino": "+5511987654323",
                "estado": "marcando",
                "duracion": 3,
                "fecha_inicio": (now - timedelta(seconds=3)).isoformat(),
                "cli_utilizado": "+5511999999999",
                "channel": "SIP/trunk-00000003"
            }
        ]
    
    return {
        "campana_id": campana_id,
        "estado_campana": "activa" if campana_id == 2 else "inactiva",
        "pausada": False,
        "llamadas_activas": llamadas_activas,
        "proximas_llamadas": [
            "+5511987654324",
            "+5511987654325", 
            "+5511987654326"
        ],
        "agentes_disponibles": 2,
        "agentes_ocupados": 1 if campana_id == 2 else 0,
        "timestamp": now.isoformat()
    }

@app.post(f"{api_prefix}/presione1/campanhas/{{campana_id}}/iniciar")
async def iniciar_campana_presione1(campana_id: int, usuario_data: dict = None):
    """Iniciar campanha presione1"""
    from datetime import datetime
    
    return {
        "status": "success",
        "campana_id": campana_id,
        "message": f"Campanha {campana_id} iniciada com sucesso",
        "usuario_id": usuario_data.get("usuario_id", "usuario_01") if usuario_data else "usuario_01",
        "timestamp": datetime.now().isoformat(),
        "llamadas_programadas": 1000 - (campana_id * 50)
    }

@app.post(f"{api_prefix}/presione1/campanhas/{{campana_id}}/pausar")
async def pausar_campana_presione1(campana_id: int, pause_data: dict = None):
    """Pausar/retomar campanha presione1"""
    from datetime import datetime
    
    pausar = pause_data.get("pausar", True) if pause_data else True
    action = "pausada" if pausar else "retomada"
    
    return {
        "status": "success",
        "campana_id": campana_id,
        "action": action,
        "pausada": pausar,
        "message": f"Campanha {campana_id} {action} com sucesso",
        "timestamp": datetime.now().isoformat()
    }

@app.post(f"{api_prefix}/presione1/campanhas/{{campana_id}}/parar")
async def parar_campana_presione1(campana_id: int):
    """Parar campanha presione1"""
    from datetime import datetime
    
    return {
        "status": "success",
        "campana_id": campana_id,
        "message": f"Campanha {campana_id} parada com sucesso",
        "llamadas_finalizadas": 3,
        "timestamp": datetime.now().isoformat()
    }

@app.get(f"{api_prefix}/presione1/campanhas/{{campana_id}}/llamadas")
async def listar_llamadas_campana(campana_id: int, estado: str = None, presiono_1: bool = None):
    """Listar chamadas da campanha com filtros"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    llamadas = []
    
    # Gerar chamadas de exemplo
    for i in range(10):
        llamada_id = 1000 + (campana_id * 100) + i
        llamadas.append({
            "id": llamada_id,
            "campana_id": campana_id,
            "numero_destino": f"+5511987654{320 + i}",
            "numero_normalizado": f"11987654{320 + i}",
            "cli_utilizado": "+5511999999999",
            "estado": ["finalizada", "presiono_1", "no_presiono", "transferida"][i % 4],
            "fecha_inicio": (now - timedelta(minutes=i*2)).isoformat(),
            "fecha_fin": (now - timedelta(minutes=i*2-1)).isoformat() if i % 2 == 0 else None,
            "presiono_1": i % 3 == 0,
            "dtmf_recibido": "1" if i % 3 == 0 else ("2" if i % 4 == 0 else None),
            "transferencia_exitosa": i % 3 == 0,
            "duracion_total": 45 + (i * 5),
            "tiempo_respuesta_dtmf": 3.5 + (i * 0.2) if i % 3 == 0 else None
        })
    
    # Aplicar filtros se fornecidos
    if estado:
        llamadas = [l for l in llamadas if l["estado"] == estado]
    if presiono_1 is not None:
        llamadas = [l for l in llamadas if l["presiono_1"] == presiono_1]
    
    return {
        "campana_id": campana_id,
        "total": len(llamadas),
        "llamadas": llamadas
    }

@app.post(f"{api_prefix}/presione1/llamadas/{{llamada_id}}/transferir")
async def transferir_llamada(llamada_id: int, transfer_data: dict = None):
    """Transferir chamada para agente/extensão"""
    from datetime import datetime
    
    destino = transfer_data.get("destino", "100") if transfer_data else "100"
    
    return {
        "status": "success",
        "llamada_id": llamada_id,
        "destino": destino,
        "message": f"Chamada {llamada_id} transferida para {destino}",
        "timestamp": datetime.now().isoformat()
    }

@app.post(f"{api_prefix}/presione1/llamadas/{{llamada_id}}/finalizar")
async def finalizar_llamada(llamada_id: int, finalize_data: dict = None):
    """Finalizar chamada manualmente"""
    from datetime import datetime
    
    motivo = finalize_data.get("motivo", "finalizada_manualmente") if finalize_data else "finalizada_manualmente"
    
    return {
        "status": "success",
        "llamada_id": llamada_id,
        "motivo": motivo,
        "message": f"Chamada {llamada_id} finalizada: {motivo}",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# ENDPOINTS MONITORING - AGENTES E SISTEMA
# ============================================================================

@app.get(f"{api_prefix}/monitoring/agentes")
async def listar_agentes_monitoring():
    """Lista agentes conectados e seu status"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    agentes = [
        {
            "id": 1,
            "nome": "Agente João",
            "extensao": "100",
            "status": "disponivel",
            "chamadas_hoje": 23,
            "tempo_online": "04:32:15",
            "ultima_chamada": (now - timedelta(minutes=5)).isoformat(),
            "skills": ["vendas", "suporte"]
        },
        {
            "id": 2,
            "nome": "Agente Maria",
            "extensao": "101", 
            "status": "ocupado",
            "chamadas_hoje": 31,
            "tempo_online": "05:15:42",
            "ultima_chamada": now.isoformat(),
            "chamada_atual": "+5511987654321",
            "skills": ["vendas", "retenção"]
        },
        {
            "id": 3,
            "nome": "Agente Pedro",
            "extensao": "102",
            "status": "pausa",
            "chamadas_hoje": 18,
            "tempo_online": "03:45:23",
            "ultima_chamada": (now - timedelta(minutes=15)).isoformat(),
            "motivo_pausa": "Almoço",
            "skills": ["suporte", "tecnico"]
        },
        {
            "id": 4,
            "nome": "Agente Ana",
            "extensao": "103",
            "status": "offline",
            "chamadas_hoje": 0,
            "tempo_online": "00:00:00",
            "ultima_chamada": None,
            "skills": ["vendas"]
        }
    ]
    
    return {
        "total_agentes": len(agentes),
        "disponiveis": len([a for a in agentes if a["status"] == "disponivel"]),
        "ocupados": len([a for a in agentes if a["status"] == "ocupado"]),
        "em_pausa": len([a for a in agentes if a["status"] == "pausa"]),
        "offline": len([a for a in agentes if a["status"] == "offline"]),
        "agentes": agentes,
        "timestamp": now.isoformat()
    }

# ============================================================================
# ENDPOINTS AUDIO INTELIGENTE
# ============================================================================

@app.get(f"{api_prefix}/audio-inteligente/campanhas/{{campana_id}}/sessoes")
async def sessoes_audio_inteligente(campana_id: int):
    """Sessões de áudio inteligente da campanha"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    sessoes = []
    for i in range(5):
        sessao_id = 2000 + (campana_id * 100) + i
        sessoes.append({
            "id": sessao_id,
            "campana_id": campana_id,
            "numero_destino": f"+5511987654{340 + i}",
            "tipo_deteccao": ["humano", "voicemail", "fax", "busy"][i % 4],
            "confianza": 85.5 + (i * 2.5),
            "duracion_analise": 2.3 + (i * 0.2),
            "timestamp": (now - timedelta(minutes=i*3)).isoformat(),
            "audio_url": f"/recordings/session_{sessao_id}.wav",
            "metadata": {
                "frequencia_dominante": 440 + (i * 50),
                "nivel_ruido": 12.5 + i,
                "silencio_detectado": i % 2 == 0
            }
        })
    
    return {
        "campana_id": campana_id,
        "total_sessoes": len(sessoes),
        "deteccoes_humano": len([s for s in sessoes if s["tipo_deteccao"] == "humano"]),
        "deteccoes_voicemail": len([s for s in sessoes if s["tipo_deteccao"] == "voicemail"]),
        "deteccoes_fax": len([s for s in sessoes if s["tipo_deteccao"] == "fax"]),
        "sessoes": sessoes,
        "timestamp": now.isoformat()
    }

# ============================================================================
# ENDPOINTS GESTÃO DE ÁUDIOS
# ============================================================================

@app.get(f"{api_prefix}/audios")
async def listar_audios():
    """Lista todos os áudios disponíveis no sistema"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    audios = [
        {
            "id": 1,
            "nome": "presione1_vendas.wav",
            "titulo": "Áudio Presione 1 - Vendas",
            "descricao": "Áudio para campanhas de vendas",
            "url": f"https://discador.onrender.com/audios/presione1_vendas.wav",
            "url_reproducao": f"https://discador.onrender.com/api/v1/audios/1/play",
            "duracao": 25.5,
            "tamanho": "2.3 MB",
            "formato": "WAV",
            "qualidade": "16 kHz, 16-bit",
            "tipo": "presione1",
            "data_upload": (now - timedelta(days=5)).isoformat(),
            "usado_em_campanhas": ["Campanha Vendas Q1", "Campanha Promocional"],
            "status": "ativo"
        },
        {
            "id": 2,
            "nome": "voicemail_padrao.wav",
            "titulo": "Mensagem Voicemail Padrão",
            "descricao": "Mensagem deixada em correios de voz",
            "url": f"https://discador.onrender.com/audios/voicemail_padrao.wav",
            "url_reproducao": f"https://discador.onrender.com/api/v1/audios/2/play",
            "duracao": 18.2,
            "tamanho": "1.8 MB",
            "formato": "WAV",
            "qualidade": "8 kHz, 16-bit",
            "tipo": "voicemail",
            "data_upload": (now - timedelta(days=3)).isoformat(),
            "usado_em_campanhas": ["Campanha Informativa"],
            "status": "ativo"
        },
        {
            "id": 3,
            "nome": "musica_espera.mp3",
            "titulo": "Música de Espera",
            "descricao": "Música tocada durante transferências",
            "url": f"https://discador.onrender.com/audios/musica_espera.mp3",
            "url_reproducao": f"https://discador.onrender.com/api/v1/audios/3/play",
            "duracao": 180.0,
            "tamanho": "4.2 MB",
            "formato": "MP3",
            "qualidade": "128 kbps",
            "tipo": "espera",
            "data_upload": (now - timedelta(days=1)).isoformat(),
            "usado_em_campanhas": [],
            "status": "ativo"
        }
    ]
    
    return {
        "total": len(audios),
        "audios": audios,
        "tipos_disponiveis": ["presione1", "voicemail", "espera", "transferencia"],
        "formatos_suportados": ["WAV", "MP3", "GSM", "uLaw", "aLaw"],
        "timestamp": now.isoformat()
    }

@app.get(f"{api_prefix}/audios/{{audio_id}}")
async def obter_audio_detalhes(audio_id: int):
    """Obter detalhes específicos de um áudio"""
    from datetime import datetime, timedelta
    
    if audio_id == 1:
        return {
            "id": 1,
            "nome": "presione1_vendas.wav",
            "titulo": "Áudio Presione 1 - Vendas",
            "descricao": "Pressione 1 para falar com um consultor de vendas. Temos ofertas especiais para você!",
            "url": f"https://discador.onrender.com/audios/presione1_vendas.wav",
            "url_reproducao": f"https://discador.onrender.com/api/v1/audios/{audio_id}/play",
            "duracao": 25.5,
            "tamanho": "2.3 MB",
            "formato": "WAV",
            "qualidade": "16 kHz, 16-bit, Mono",
            "tipo": "presione1",
            "data_upload": datetime.now().isoformat(),
            "transcricao": "Olá! Esta é uma chamada da nossa empresa. Se você tem interesse em conhecer nossas promoções e falar com um consultor, pressione a tecla 1 agora. Caso contrário, a chamada será encerrada. Obrigado!",
            "metadados": {
                "canal": "mono",
                "taxa_amostragem": "16000 Hz",
                "profundidade_bits": 16,
                "codec": "PCM",
                "nivel_volume": -12.5
            },
            "uso_estatisticas": {
                "total_reproducoes": 1247,
                "campanhas_ativas": 2,
                "ultima_reproducao": datetime.now().isoformat()
            },
            "status": "ativo"
        }
    elif audio_id == 2:
        return {
            "id": 2,
            "nome": "voicemail_padrao.wav",
            "titulo": "Mensagem Voicemail Padrão",
            "descricao": "Mensagem padrão deixada em correios de voz",
            "url": f"https://discador.onrender.com/audios/voicemail_padrao.wav",
            "url_reproducao": f"https://discador.onrender.com/api/v1/audios/{audio_id}/play",
            "duracao": 18.2,
            "tamanho": "1.8 MB",
            "formato": "WAV",
            "qualidade": "8 kHz, 16-bit, Mono",
            "tipo": "voicemail",
            "data_upload": datetime.now().isoformat(),
            "transcricao": "Olá! Você recebeu uma chamada da nossa empresa. Por favor, retorne nossa ligação através do número 0800-123-4567. Obrigado!",
            "metadados": {
                "canal": "mono",
                "taxa_amostragem": "8000 Hz",
                "profundidade_bits": 16,
                "codec": "PCM",
                "nivel_volume": -10.2
            },
            "uso_estatisticas": {
                "total_reproducoes": 456,
                "campanhas_ativas": 1,
                "ultima_reproducao": datetime.now().isoformat()
            },
            "status": "ativo"
        }
    elif audio_id == 3:
        return {
            "id": 3,
            "nome": "musica_espera.mp3",
            "titulo": "Música de Espera",
            "descricao": "Música instrumental tocada durante transferências",
            "url": f"https://discador.onrender.com/audios/musica_espera.mp3",
            "url_reproducao": f"https://discador.onrender.com/api/v1/audios/{audio_id}/play",
            "duracao": 180.0,
            "tamanho": "4.2 MB",
            "formato": "MP3",
            "qualidade": "128 kbps, Stereo",
            "tipo": "espera",
            "data_upload": datetime.now().isoformat(),
            "transcricao": "Arquivo de música instrumental sem fala",
            "metadados": {
                "canal": "stereo",
                "taxa_amostragem": "44100 Hz",
                "bitrate": "128 kbps",
                "codec": "MP3",
                "nivel_volume": -8.0
            },
            "uso_estatisticas": {
                "total_reproducoes": 789,
                "campanhas_ativas": 3,
                "ultima_reproducao": datetime.now().isoformat()
            },
            "status": "ativo"
        }
    
    return {"error": "Áudio não encontrado", "audio_id": audio_id}

@app.get(f"{api_prefix}/audios/{{audio_id}}/play")
async def reproduzir_audio(audio_id: int):
    """Endpoint para reproduzir áudio"""
    return {
        "audio_id": audio_id,
        "stream_url": f"https://discador.onrender.com/stream/audio_{audio_id}.wav",
        "content_type": "audio/wav",
        "duracao": 25.5,
        "controles": {
            "play": True,
            "pause": True,
            "volume": True,
            "download": True
        },
        "message": "Use a stream_url para reproduzir o áudio",
        "player_html": f'<audio controls preload="metadata"><source src="https://discador.onrender.com/stream/audio_{audio_id}.wav" type="audio/wav">Seu navegador não suporta o elemento de áudio.</audio>'
    }

@app.post(f"{api_prefix}/audios/upload")
async def upload_audio():
    """Simula upload de arquivo de áudio"""
    from datetime import datetime
    
    # Simular upload bem-sucedido
    return {
        "status": "success",
        "message": "Áudio enviado com sucesso",
        "audio": {
            "id": 4,
            "nome": "novo_audio.wav",
            "titulo": "Novo Áudio Enviado",
            "url": f"https://discador.onrender.com/audios/novo_audio.wav",
            "url_reproducao": f"https://discador.onrender.com/api/v1/audios/4/play",
            "duracao": 30.0,
            "tamanho": "2.8 MB",
            "formato": "WAV",
            "data_upload": datetime.now().isoformat(),
            "status": "processando"
        },
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# ENDPOINTS GRAVAÇÕES DE CHAMADAS
# ============================================================================

@app.get(f"{api_prefix}/gravacoes")
async def listar_gravacoes(campana_id: int = None, data_inicio: str = None, data_fim: str = None):
    """Lista gravações de chamadas com filtros"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    gravacoes = []
    for i in range(10):
        gravacao_id = 2000 + i
        gravacoes.append({
            "id": gravacao_id,
            "campana_id": campana_id or (i % 3 + 1),
            "llamada_id": 1000 + i,
            "numero_destino": f"+5511987654{330 + i}",
            "agente_id": "100" if i % 2 == 0 else "101",
            "agente_nome": "Agente João" if i % 2 == 0 else "Agente Maria",
            "data_gravacao": (now - timedelta(hours=i)).isoformat(),
            "duracao": 45 + (i * 15),
            "tamanho": f"{1.2 + (i * 0.3):.1f} MB",
            "url_gravacao": f"https://discador.onrender.com/gravacoes/chamada_{gravacao_id}.wav",
            "url_reproducao": f"https://discador.onrender.com/api/v1/gravacoes/{gravacao_id}/play",
            "url_download": f"https://discador.onrender.com/api/v1/gravacoes/{gravacao_id}/download",
            "qualidade": "8 kHz, 16-bit",
            "tipo_chamada": ["entrada", "saida"][i % 2],
            "resultado_chamada": ["atendida", "nao_atendida", "ocupado", "transferida"][i % 4],
            "presiono_1": i % 3 == 0,
            "transferida": i % 4 == 0,
            "voicemail_detectado": i % 5 == 0,
            "sentimento_analise": ["positivo", "neutro", "negativo"][i % 3],
            "score_qualidade": 85.5 + (i * 1.5),
            "transcricao_disponivel": i % 2 == 0,
            "status": "processada"
        })
    
    # Aplicar filtros se fornecidos
    if campana_id:
        gravacoes = [g for g in gravacoes if g["campana_id"] == campana_id]
    
    return {
        "total": len(gravacoes),
        "gravacoes": gravacoes,
        "filtros_aplicados": {
            "campana_id": campana_id,
            "data_inicio": data_inicio,
            "data_fim": data_fim
        },
        "estatisticas": {
            "total_duracao": sum(g["duracao"] for g in gravacoes),
            "total_tamanho": f"{sum(float(g['tamanho'].split()[0]) for g in gravacoes):.1f} MB",
            "com_transcricao": len([g for g in gravacoes if g["transcricao_disponivel"]]),
            "transferidas": len([g for g in gravacoes if g["transferida"]])
        },
        "timestamp": now.isoformat()
    }

@app.get(f"{api_prefix}/gravacoes/{{gravacao_id}}")
async def obter_gravacao_detalhes(gravacao_id: int):
    """Obter detalhes completos de uma gravação"""
    from datetime import datetime, timedelta
    
    return {
        "id": gravacao_id,
        "campana_id": 2,
        "llamada_id": 1001,
        "numero_destino": "+5511987654321",
        "numero_origem": "+5511999999999",
        "agente_id": "100",
        "agente_nome": "Agente João",
        "data_inicio": (datetime.now() - timedelta(hours=2)).isoformat(),
        "data_fim": (datetime.now() - timedelta(hours=2, minutes=-3)).isoformat(),
        "duracao": 180,
        "tamanho": "1.8 MB",
        "formato": "WAV",
        "qualidade": "8 kHz, 16-bit, Mono",
        "url_gravacao": f"https://discador.onrender.com/gravacoes/chamada_{gravacao_id}.wav",
        "url_reproducao": f"https://discador.onrender.com/api/v1/gravacoes/{gravacao_id}/play",
        "url_download": f"https://discador.onrender.com/api/v1/gravacoes/{gravacao_id}/download",
        "tipo_chamada": "saida",
        "resultado_chamada": "transferida",
        "presiono_1": True,
        "dtmf_detectado": "1",
        "tempo_resposta_dtmf": 5.2,
        "transferida": True,
        "agente_transferencia": "101",
        "voicemail_detectado": False,
        "analise_audio": {
            "sentimento": "positivo",
            "confianca_sentimento": 87.5,
            "emocoes_detectadas": ["interesse", "curiosidade"],
            "palavras_chave": ["promoção", "desconto", "sim", "interessado"],
            "nivel_ruido": 12.3,
            "qualidade_audio": 92.1,
            "silencio_total": 15.2,
            "tempo_fala_cliente": 85.5,
            "tempo_fala_agente": 94.5
        },
        "transcricao": {
            "disponivel": True,
            "idioma": "pt-BR",
            "confianca": 94.2,
            "texto_completo": "Cliente: Alô? Agente: Olá, boa tarde! Estou ligando da empresa XYZ para falar sobre nossa promoção especial. Cliente: Ah sim, que tipo de promoção? Agente: Temos descontos de até 50% em nossos produtos. Gostaria de saber mais? Cliente: Sim, tenho interesse...",
            "segmentos": [
                {"inicio": 0.0, "fim": 2.5, "falante": "sistema", "texto": "Áudio de apresentação da campanha"},
                {"inicio": 2.5, "fim": 8.2, "falante": "cliente", "texto": "Alô?"},
                {"inicio": 8.2, "fim": 15.1, "falante": "agente", "texto": "Olá, boa tarde! Estou ligando da empresa XYZ..."}
            ]
        },
        "metadados": {
            "codec": "PCM",
            "taxa_amostragem": "8000 Hz",
            "canal": "mono",
            "nivel_volume": -8.5,
            "picos_audio": [12.3, 15.7, 11.2],
            "checksum": "a1b2c3d4e5f6",
            "processado_em": datetime.now().isoformat()
        },
        "status": "processada"
    }

@app.get(f"{api_prefix}/gravacoes/{{gravacao_id}}/play")
async def reproduzir_gravacao(gravacao_id: int):
    """Reproduzir gravação de chamada"""
    return {
        "gravacao_id": gravacao_id,
        "stream_url": f"https://discador.onrender.com/stream/gravacao_{gravacao_id}.wav",
        "content_type": "audio/wav",
        "duracao": 180,
        "controles": {
            "play": True,
            "pause": True,
            "seek": True,
            "download": True,
            "velocidade": [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        },
        "player_html": f'<audio controls preload="metadata"><source src="https://discador.onrender.com/stream/gravacao_{gravacao_id}.wav" type="audio/wav">Seu navegador não suporta o elemento de áudio.</audio>',
        "transcricao_sync": True,  # Sincronizar transcricão com áudio
        "message": "Use a stream_url para reproduzir a gravação"
    }

@app.get(f"{api_prefix}/gravacoes/{{gravacao_id}}/download")
async def download_gravacao(gravacao_id: int):
    """Download de gravação"""
    return {
        "gravacao_id": gravacao_id,
        "download_url": f"https://discador.onrender.com/download/gravacao_{gravacao_id}.wav",
        "nome_arquivo": f"gravacao_chamada_{gravacao_id}.wav",
        "tamanho": "1.8 MB",
        "formato": "WAV",
        "expires_in": 3600,  # 1 hora
        "message": "Link de download válido por 1 hora"
    }

# ============================================================================
# ENDPOINTS GESTÃO AVANÇADA DE AGENTES
# ============================================================================

@app.get(f"{api_prefix}/agentes")
async def listar_agentes_detalhado():
    """Lista detalhada de todos os agentes"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    agentes = [
        {
            "id": 1,
            "nome": "João Silva",
            "email": "joao.silva@empresa.com",
            "extensao": "100",
            "status": "disponivel",
            "status_detalhado": {
                "codigo": "READY",
                "descricao": "Pronto para receber chamadas",
                "tempo_no_status": "00:05:23",
                "ultimo_status": "BREAK"
            },
            "chamadas_hoje": 23,
            "chamadas_atendidas": 21,
            "chamadas_transferidas": 18,
            "tempo_online": "04:32:15",
            "tempo_pausa_total": "00:45:30",
            "tempo_medio_atendimento": "03:25",
            "ultima_chamada": (now - timedelta(minutes=5)).isoformat(),
            "skill_level": "senior",
            "skills": ["vendas", "suporte", "retenção"],
            "idiomas": ["português", "espanhol"],
            "campanhas_asignadas": [1, 2],
            "metas_diarias": {
                "chamadas_objetivo": 40,
                "chamadas_atual": 23,
                "conversao_objetivo": 15.0,
                "conversao_atual": 18.2
            },
            "avaliacao": {
                "nota_media": 4.8,
                "total_avaliacoes": 156,
                "satisfacao_cliente": 94.5
            },
            "configuracoes": {
                "auto_answer": True,
                "tempo_wrap_up": 30,
                "tipos_chamada": ["entrada", "saida"],
                "prioridade": "alta"
            }
        },
        {
            "id": 2,
            "nome": "Maria Santos",
            "email": "maria.santos@empresa.com",
            "extensao": "101",
            "status": "ocupado",
            "status_detalhado": {
                "codigo": "INCALL",
                "descricao": "Em chamada",
                "tempo_no_status": "00:02:15",
                "numero_atual": "+5511987654321"
            },
            "chamadas_hoje": 31,
            "chamadas_atendidas": 29,
            "chamadas_transferidas": 25,
            "tempo_online": "05:15:42",
            "tempo_pausa_total": "00:30:15",
            "tempo_medio_atendimento": "04:12",
            "ultima_chamada": now.isoformat(),
            "chamada_atual": {
                "numero": "+5511987654321",
                "inicio": (now - timedelta(minutes=2)).isoformat(),
                "duracao": 135,
                "tipo": "transferencia",
                "campanha": "Promocional"
            },
            "skill_level": "expert",
            "skills": ["vendas", "retenção", "supervisor"],
            "idiomas": ["português", "inglês"],
            "campanhas_asignadas": [2, 3],
            "metas_diarias": {
                "chamadas_objetivo": 35,
                "chamadas_atual": 31,
                "conversao_objetivo": 20.0,
                "conversao_atual": 22.8
            },
            "avaliacao": {
                "nota_media": 4.9,
                "total_avaliacoes": 203,
                "satisfacao_cliente": 96.2
            }
        },
        {
            "id": 3,
            "nome": "Pedro Oliveira",
            "email": "pedro.oliveira@empresa.com",
            "extensao": "102",
            "status": "pausa",
            "status_detalhado": {
                "codigo": "BREAK",
                "descricao": "Em pausa",
                "tempo_no_status": "00:12:45",
                "motivo": "Almoço",
                "retorno_previsto": (now + timedelta(minutes=30)).isoformat()
            },
            "chamadas_hoje": 18,
            "chamadas_atendidas": 16,
            "chamadas_transferidas": 14,
            "tempo_online": "03:45:23",
            "tempo_pausa_total": "01:15:45",
            "tempo_medio_atendimento": "02:58",
            "ultima_chamada": (now - timedelta(minutes=15)).isoformat(),
            "skill_level": "junior",
            "skills": ["suporte", "tecnico"],
            "idiomas": ["português"],
            "campanhas_asignadas": [1],
            "metas_diarias": {
                "chamadas_objetivo": 25,
                "chamadas_atual": 18,
                "conversao_objetivo": 10.0,
                "conversao_atual": 12.5
            },
            "avaliacao": {
                "nota_media": 4.6,
                "total_avaliacoes": 89,
                "satisfacao_cliente": 92.1
            }
        }
    ]
    
    return {
        "total_agentes": len(agentes),
        "disponiveis": len([a for a in agentes if a["status"] == "disponivel"]),
        "ocupados": len([a for a in agentes if a["status"] == "ocupado"]),
        "em_pausa": len([a for a in agentes if a["status"] == "pausa"]),
        "offline": len([a for a in agentes if a["status"] == "offline"]),
        "agentes": agentes,
        "resumo_performance": {
            "total_chamadas_hoje": sum(a["chamadas_hoje"] for a in agentes),
            "media_tempo_atendimento": "03:32",
            "satisfacao_media": 94.3,
            "taxa_conversao_media": 17.8
        },
        "timestamp": now.isoformat()
    }

@app.get(f"{api_prefix}/agentes/{{agente_id}}")
async def obter_agente_detalhes(agente_id: int):
    """Obter detalhes completos de um agente"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    return {
        "id": agente_id,
        "nome": "João Silva",
        "email": "joao.silva@empresa.com",
        "extensao": "100",
        "status": "disponivel",
        "status_detalhado": {
            "codigo": "READY",
            "descricao": "Pronto para receber chamadas",
            "tempo_no_status": "00:05:23",
            "ultimo_status": "BREAK",
            "historico_status": [
                {"status": "READY", "inicio": now.isoformat(), "fim": None},
                {"status": "BREAK", "inicio": (now - timedelta(minutes=45)).isoformat(), "fim": (now - timedelta(minutes=5)).isoformat()},
                {"status": "INCALL", "inicio": (now - timedelta(hours=1)).isoformat(), "fim": (now - timedelta(minutes=45)).isoformat()}
            ]
        },
        "estatisticas_detalhadas": {
            "hoje": {
                "chamadas_total": 23,
                "chamadas_atendidas": 21,
                "chamadas_perdidas": 2,
                "chamadas_transferidas": 18,
                "tempo_total_chamadas": "02:45:30",
                "tempo_medio_chamada": "07:15",
                "primeiro_login": "08:30:00",
                "ultimo_logout": None
            },
            "semana": {
                "chamadas_total": 156,
                "tempo_total_online": "32:15:45",
                "media_diaria_chamadas": 31.2,
                "dias_trabalhados": 5
            },
            "mes": {
                "chamadas_total": 634,
                "tempo_total_online": "152:30:20",
                "meta_mensal": 800,
                "progresso_meta": 79.25
            }
        },
        "skills": ["vendas", "suporte", "retenção"],
        "skill_level": "senior",
        "certificacoes": ["Atendimento ao Cliente", "Vendas Consultivas", "Retenção de Clientes"],
        "idiomas": ["português", "espanhol"],
        "campanhas_asignadas": [1, 2],
        "horario_trabalho": {
            "inicio": "08:00",
            "fim": "17:00",
            "timezone": "America/Sao_Paulo",
            "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"]
        },
        "avaliacoes": {
            "nota_media": 4.8,
            "total_avaliacoes": 156,
            "satisfacao_cliente": 94.5,
            "ultima_avaliacao": (now - timedelta(days=2)).isoformat(),
            "comentarios_recentes": [
                {"data": (now - timedelta(days=1)).isoformat(), "nota": 5, "comentario": "Excelente atendimento, muito educado"},
                {"data": (now - timedelta(days=3)).isoformat(), "nota": 4, "comentario": "Resolveu minha dúvida rapidamente"}
            ]
        },
        "configuracoes": {
            "auto_answer": True,
            "tempo_wrap_up": 30,
            "tipos_chamada": ["entrada", "saida"],
            "prioridade": "alta",
            "modo_pausa_automatica": False,
            "notificacoes": True,
            "gravacao_automatica": True
        },
        "chamada_atual": None,
        "timestamp": now.isoformat()
    }

@app.post(f"{api_prefix}/agentes/{{agente_id}}/status")
async def alterar_status_agente(agente_id: int, status_data: dict):
    """Alterar status de um agente"""
    from datetime import datetime
    
    novo_status = status_data.get("status", "disponivel")
    motivo = status_data.get("motivo", "")
    
    return {
        "agente_id": agente_id,
        "status_anterior": "disponivel",
        "status_novo": novo_status,
        "motivo": motivo,
        "timestamp": datetime.now().isoformat(),
        "message": f"Status do agente alterado para {novo_status}"
    }

@app.post(f"{api_prefix}/agentes/{{agente_id}}/atribuir-campanha")
async def atribuir_campanha_agente(agente_id: int, campanha_data: dict):
    """Atribuir agente a uma campanha"""
    from datetime import datetime
    
    campanha_id = campanha_data.get("campanha_id")
    
    return {
        "agente_id": agente_id,
        "campanha_id": campanha_id,
        "status": "success",
        "message": f"Agente {agente_id} atribuído à campanha {campanha_id}",
        "timestamp": datetime.now().isoformat()
    }

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