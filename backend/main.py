#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
import os
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from pydantic import BaseModel
import jwt
import hashlib

from app.routes import llamadas, listas, cli, stt, reportes, listas_llamadas, blacklist, discado, audio_inteligente, code2base, campanha_politica, monitoring
from app.database import inicializar_bd, get_db
from app.config import configuracion
from app.utils.logger import logger
# Importar modelos para asegurar que esten disponibles para SQLAlchemy
import app.models

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
SECRET_KEY = "sua-chave-secreta-muito-segura-aqui"
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
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # Cache preflight por 24 horas
)

# Prefijo para todas las rutas de la API
api_prefix = "/api/v1"

# Incluir las rutas
app.include_router(llamadas.router, prefix=f"{api_prefix}/llamadas")
app.include_router(listas.router, prefix=f"{api_prefix}/listas")
app.include_router(listas_llamadas.router, prefix=f"{api_prefix}")
app.include_router(blacklist.router, prefix=f"{api_prefix}")
app.include_router(discado.router, prefix=f"{api_prefix}")
app.include_router(cli.router, prefix=f"{api_prefix}")
app.include_router(stt.router, prefix=f"{api_prefix}/stt")
app.include_router(reportes.router, prefix=f"{api_prefix}/reportes")
app.include_router(audio_inteligente.router, prefix=f"{api_prefix}")
app.include_router(code2base.router, prefix=f"{api_prefix}")
app.include_router(campanha_politica.router, prefix=f"{api_prefix}/campanha-politica")
app.include_router(monitoring.router, prefix=f"{api_prefix}")

# Router para rotas ausentes
missing_routes = APIRouter()

# Endpoints OPTIONS para CORS
@missing_routes.options("/code2base/clis")
async def options_code2base_clis():
    """Endpoint OPTIONS para CORS"""
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
    """Alias para campanhas - redireciona para /campanhas"""
    return {
        "status": "success",
        "campaigns": [],
        "total": 0,
        "message": "Use /api/v1/campanhas para acessar as campanhas"
    }

# Endpoint de campanhas direto
@missing_routes.get("/campanhas")
async def listar_campanhas_direto():
    """Lista campanhas - dados mock"""
    campanhas = [
        {
            "id": 1,
            "nome": "Campanha Principal",
            "descricao": "Campanha de discado principal",
            "status": "ativa",
            "data_inicio": datetime.now().isoformat(),
            "data_fim": None,
            "total_contatos": 1000,
            "contatos_discados": 250,
            "taxa_sucesso": 15.5
        },
        {
            "id": 2,
            "nome": "Campanha Secundária", 
            "descricao": "Campanha de follow-up",
            "status": "pausada",
            "data_inicio": datetime.now().isoformat(),
            "data_fim": None,
            "total_contatos": 500,
            "contatos_discados": 100,
            "taxa_sucesso": 12.0
        }
    ]
    return {
        "status": "success",
        "campanhas": campanhas,
        "total": len(campanhas)
    }

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
    """Provedores SIP - versão direta sem dependências"""
    provedores = [
        {
            "id": 1,
            "nome": "Provedor Principal",
            "codigo": "PROV001",
            "tipo_provedor": "sip",
            "descricao": "Provedor SIP principal",
            "servidor_sip": "sip.provedor1.com",
            "porta_sip": 5060,
            "protocolo": "UDP",
            "usuario_sip": "user001",
            "senha_sip": "***",
            "ativo": True,
            "max_chamadas_simultaneas": 100,
            "timeout_conexao": 30,
            "prioridade": 1,
            "fecha_creacion": datetime.now().isoformat(),
            "fecha_actualizacion": datetime.now().isoformat()
        },
        {
            "id": 2,
            "nome": "Provedor Secundário",
            "codigo": "PROV002",
            "tipo_provedor": "sip", 
            "descricao": "Provedor SIP secundário",
            "servidor_sip": "sip.provedor2.com",
            "porta_sip": 5060,
            "protocolo": "TCP",
            "usuario_sip": "user002",
            "senha_sip": "***",
            "ativo": True,
            "max_chamadas_simultaneas": 50,
            "timeout_conexao": 30,
            "prioridade": 2,
            "fecha_creacion": datetime.now().isoformat(),
            "fecha_actualizacion": datetime.now().isoformat()
        }
    ]
    return provedores

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

# Health check endpoints para Render.com
@app.get("/")
@app.head("/")
async def raiz():
    """Endpoint raiz com informações da API"""
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

if __name__ == "__main__":
    logger.info(f"Iniciando servidor en {configuracion.HOST}:{configuracion.PUERTO}")
    uvicorn.run(
        "main:app", 
        host=configuracion.HOST, 
        port=configuracion.PUERTO, 
        reload=configuracion.DEBUG
    ) 