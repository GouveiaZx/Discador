#!/usr/bin/env python3
"""
Servidor simplificado para testar o Discador Preditivo
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Criar aplicação FastAPI simples
app = FastAPI(
    title="Discador Predictivo - Teste",
    description="Sistema de discado predictivo (versão de teste)",
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
        "mensagem": "🚀 Discador Predictivo está funcionando!",
        "status": "ativo",
        "documentacao": "http://localhost:8000/docs",
        "versao": "1.0.0"
    }

@app.get("/api/v1/status")
async def status():
    """Status da API"""
    return {
        "status": "ok",
        "servico": "Discador Predictivo",
        "versao": "1.0.0",
        "ambiente": "desenvolvimento"
    }

@app.get("/api/v1/test")
async def teste():
    """Endpoint de teste"""
    return {
        "teste": "sucesso",
        "mensagem": "A API está funcionando corretamente!"
    }

if __name__ == "__main__":
    print("🚀 Iniciando Discador Predictivo - Servidor de Teste")
    print("📍 URL: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    print("⏹️  Para parar: Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 