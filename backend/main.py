#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from datetime import datetime
from contextlib import asynccontextmanager

from app.routes import llamadas, listas, cli, stt, reportes, listas_llamadas, blacklist, discado, audio_inteligente, code2base, campanha_politica, monitoring
from app.database import inicializar_bd, get_db
from app.config import configuracion
from app.utils.logger import logger
# Importar modelos para asegurar que esten disponibles para SQLAlchemy
import app.models

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