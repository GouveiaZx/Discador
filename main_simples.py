#!/usr/bin/env python3
"""
Main simplificado para deploy no Railway - TOTALMENTE INDEPENDENTE
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Criar aplicação FastAPI simples SEM dependências externas
app = FastAPI(
    title="Discador Predictivo - Railway",
    description="Sistema de discado predictivo (deploy Railway)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS mais permissivo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Métodos explícitos
    allow_headers=["*"],  # Todos os headers
    expose_headers=["*"]  # Expor todos os headers
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
            "host": "0.0.0.0",
            "puerto": os.environ.get("PORT", 8000),
            "debug": False
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

# Endpoints mock para o frontend
@app.get("/api/v1/llamadas/en-progreso")
async def llamadas_en_progreso():
    """Mock: Chamadas em progresso"""
    return {
        "status": "success",
        "llamadas": [
            {
                "id": 1,
                "numero": "+55 11 99999-0001",
                "nombre": "Cliente Teste 1",
                "estado": "en_progreso",
                "inicio": "2025-01-30T15:30:00",
                "duracion": "00:02:45"
            },
            {
                "id": 2,
                "numero": "+55 11 99999-0002", 
                "nombre": "Cliente Teste 2",
                "estado": "en_progreso",
                "inicio": "2025-01-30T15:28:15",
                "duracion": "00:05:12"
            }
        ],
        "total": 2
    }

@app.get("/api/v1/llamadas/historico")
async def historico_llamadas():
    """Mock: Histórico de chamadas"""
    return {
        "status": "success",
        "llamadas": [
            {
                "id": 3,
                "numero": "+55 11 99999-0003",
                "nombre": "Cliente Teste 3", 
                "estado": "finalizada",
                "resultado": "contacto_efectivo",
                "inicio": "2025-01-30T14:30:00",
                "fin": "2025-01-30T14:32:30",
                "duracion": "00:02:30"
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 10
    }

@app.post("/api/v1/llamadas/finalizar")
async def finalizar_llamada():
    """Mock: Finalizar chamada"""
    return {
        "status": "success",
        "mensaje": "Llamada finalizada correctamente"
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_level="info"
    ) 