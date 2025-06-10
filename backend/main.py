#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from app.routes import llamadas, listas, cli, stt, reportes, listas_llamadas, blacklist, discado, presione1, audio_inteligente, code2base, campanha_politica, multi_sip, monitoring
from app.database import inicializar_bd
from app.config import configuracion
from app.utils.logger import logger
# Importar modelos para asegurar que esten disponibles para SQLAlchemy
import app.models

# Crear la aplicacion FastAPI
app = FastAPI(
    title=configuracion.APP_NAME,
    description="Sistema de discado predictivo con funcionalidades de manejo de llamadas, listas, blacklist, reconocimiento de voz, discado preditivo Presione 1 y multiples provedores SIP",
    version=configuracion.APP_VERSION,
    docs_url="/documentacion",
    redoc_url="/redoc",
    debug=configuracion.DEBUG
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
app.include_router(cli.router, prefix=f"{api_prefix}/cli")
app.include_router(stt.router, prefix=f"{api_prefix}/stt")
app.include_router(reportes.router, prefix=f"{api_prefix}/reportes")
app.include_router(presione1.router, prefix=f"{api_prefix}")
app.include_router(audio_inteligente.router, prefix=f"{api_prefix}")
app.include_router(code2base.router, prefix=f"{api_prefix}/code2base")
app.include_router(campanha_politica.router, prefix=f"{api_prefix}/campanha-politica")
app.include_router(multi_sip.router)  # Multi-SIP tem seu proprio prefixo
app.include_router(monitoring.router)  # Monitoramento em tempo real

@app.get("/")
async def raiz():
    logger.info("Solicitud a la ruta principal")
    return {
        "mensaje": f"API de {configuracion.APP_NAME}",
        "version": configuracion.APP_VERSION,
        "estado": "activo",
        "funcionalidades": [
            "Discado predictivo con blacklist",
            "Multiples listas de llamadas",
            "Upload de archivos CSV/TXT",
            "Gestion de lista negra",
            "Estadisticas y reportes",
            "CLI aleatorio",
            "Discado preditivo Presione 1",
            "Sistema de Audio Inteligente",
            "Sistema CODE2BASE - Selecao Inteligente de CLIs",
            "Sistema de Campanhas Politicas - Conformidade Eleitoral",
            "Sistema Multi-SIP - Multiplos Provedores VoIP",
            "Sistema de Monitoramento em Tempo Real - Dashboard e WebSocket"
        ],
        "documentacion": "/documentacion"
    }

@app.on_event("startup")
async def evento_inicio():
    """Evento que se ejecuta al iniciar la aplicacion"""
    # Crear directorio de logs si no existe y esta configurado
    if configuracion.LOG_ARCHIVO:
        os.makedirs(os.path.dirname(configuracion.LOG_ARCHIVO), exist_ok=True)
        
    # Inicializar la base de datos
    logger.info("Iniciando la aplicacion")
    logger.info(f"Configuracion cargada. Modo debug: {configuracion.DEBUG}")
    logger.info(f"Inicializando base de datos en {configuracion.DB_HOST}")
    
    try:
        inicializar_bd()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        raise

@app.on_event("shutdown")
async def evento_cierre():
    """Evento que se ejecuta al cerrar la aplicacion"""
    logger.info("Apagando la aplicacion")

if __name__ == "__main__":
    logger.info(f"Iniciando servidor en {configuracion.HOST}:{configuracion.PUERTO}")
    uvicorn.run(
        "main:app", 
        host=configuracion.HOST, 
        port=configuracion.PUERTO, 
        reload=configuracion.DEBUG
    ) 