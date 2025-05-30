#!/usr/bin/env python3
"""
Main simplificado para deploy no Railway
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Importações básicas
from app.config import configuracion

# Criar aplicação FastAPI simples
app = FastAPI(
    title="Discador Predictivo - Railway",
    description="Sistema de discado predictivo (deploy Railway)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def inicio():
    """Página inicial"""
    return {
        "mensagem": "🚀 Discador Predictivo funcionando no Railway!",
        "status": "ativo",
        "versao": "1.0.0",
        "ambiente": "Railway",
        "documentacao": "/docs"
    }

@app.get("/api/v1/status")
async def status():
    """Status da API"""
    return {
        "status": "ok",
        "servico": "Discador Predictivo",
        "versao": "1.0.0",
        "ambiente": "Railway",
        "configuracao": {
            "host": configuracion.HOST,
            "puerto": configuracao.PUERTO,
            "debug": configuracao.DEBUG
        }
    }

@app.get("/api/v1/test")
async def teste():
    """Endpoint de teste"""
    return {
        "teste": "sucesso",
        "mensagem": "A API está funcionando no Railway!",
        "railway": True
    }

@app.get("/health")
async def health_check():
    """Health check para Railway"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_level="info"
    ) 