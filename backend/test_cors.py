#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples para verificar configuração de CORS
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ast

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI(title="Teste CORS")

# Configuração de CORS idêntica ao main.py
cors_origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:5173","https://discador.vercel.app"]')
print(f"🔍 CORS_ORIGINS string: {cors_origins_str}")

try:
    cors_origins = ast.literal_eval(cors_origins_str)
    print(f"✅ CORS origins parsed: {cors_origins}")
except Exception as e:
    print(f"❌ Error parsing CORS origins: {e}")
    cors_origins = ["http://localhost:3000", "http://localhost:5173", "https://discador.vercel.app"]

# Adicionar origens extras
cors_origins.extend([
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://localhost:5173",
    "*"  # Permitir todas as origens temporariamente
])

print(f"🌐 Final CORS origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
async def root():
    return {
        "message": "Teste CORS funcionando",
        "cors_origins": cors_origins,
        "cors_origins_env": os.getenv("CORS_ORIGINS", "NOT_SET")
    }

@app.get("/api/v1/test")
async def test_api():
    return {
        "status": "success",
        "message": "API endpoint funcionando com CORS",
        "cors_configured": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)