#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime
from contextlib import asynccontextmanager

from app.routes import llamadas, listas, cli, stt, reportes, listas_llamadas, blacklist, discado, audio_inteligente, code2base, campanha_politica, multi_sip, monitoring
from app.database import inicializar_bd
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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En produccion, restringir a origenes especificos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(multi_sip.router, prefix=f"{api_prefix}")
app.include_router(monitoring.router, prefix=f"{api_prefix}")

# Router para rotas ausentes
missing_routes = APIRouter()

@missing_routes.get("/multi-sip/provedores")
async def listar_provedores():
    """Lista provedores SIP disponíveis"""
    provedores = [
        {
            "id": 1,
            "nome": "Provedor Principal",
            "servidor_sip": "sip.exemplo.com",
            "porta": 5060,
            "status": "ativo",
            "prioridade": 1,
            "max_chamadas_simultaneas": 50,
            "chamadas_ativas": 0,
            "ultima_verificacao": datetime.now().isoformat()
        },
        {
            "id": 2,
            "nome": "Provedor Backup", 
            "servidor_sip": "backup.sip.com",
            "porta": 5061,
            "status": "standby",
            "prioridade": 2,
            "max_chamadas_simultaneas": 30,
            "chamadas_ativas": 0,
            "ultima_verificacao": datetime.now().isoformat()
        }
    ]
    return {
        "status": "success",
        "provedores": provedores,
        "total": len(provedores)
    }

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

@missing_routes.get("/audio/contextos")
async def listar_contextos_audio():
    """Lista contextos de áudio"""
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
        }
    ]
    return {
        "status": "success",
        "contextos": contextos,
        "total": len(contextos)
    }

# Incluir rotas ausentes
app.include_router(missing_routes, prefix=f"{api_prefix}")

# Health check endpoints para Render.com
@app.get("/")
@app.head("/")
async def raiz():
    logger.info("Solicitud a la ruta principal")
    return {
        "mensaje": f"API de {configuracion.APP_NAME}",
        "version": configuracion.APP_VERSION,
        "estado": "activo",
        "funcionalidades": [
            "Discado predictivo com blacklist",
            "Multiples listas de chamadas",
            "Upload de arquivos CSV/TXT",
            "Gestão de lista negra",
            "Estatísticas e reportes",
            "CLI aleatorio",
            "Sistema de Audio Inteligente",
            "CODE2BASE - Seleção inteligente de CLI",
            "Campanhas Políticas com compliance",
            "Multi-SIP com failover",
            "Monitoramento em tempo real"
        ],
        "documentacao": "/documentacao"
    }

@app.get("/health")
@app.head("/health")
async def health_check():
    """Endpoint dedicado para health checks"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/ping")
@app.head("/ping")
async def ping():
    """Endpoint simples para verificação de conectividade"""
    return {"message": "pong"}

if __name__ == "__main__":
    logger.info(f"Iniciando servidor en {configuracion.HOST}:{configuracion.PUERTO}")
    uvicorn.run(
        "main:app", 
        host=configuracion.HOST, 
        port=configuracion.PUERTO, 
        reload=configuracion.DEBUG
    ) 