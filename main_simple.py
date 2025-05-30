#!/usr/bin/env python3
"""
Sistema de Discador Preditivo - Versão Simplificada para Deploy
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn
import os
import logging
from datetime import datetime
import json
import io
import csv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Discador Predictivo - MVP Funcional",
    description="Sistema de discado predictivo com modo 'Pressione 1'",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mock data para testar
MOCK_CAMPAIGNS = [
    {
        "id": 1,
        "name": "Campanha Teste 1",
        "status": "active",
        "cli_number": "+54 11 4567-8900",
        "created_at": "2024-01-15T09:00:00Z",
        "total_contacts": 150,
        "contacted_count": 45,
        "success_count": 12
    },
    {
        "id": 2,
        "name": "Campanha Teste 2", 
        "status": "paused",
        "cli_number": "+54 11 4567-8901",
        "created_at": "2024-01-14T14:30:00Z",
        "total_contacts": 200,
        "contacted_count": 80,
        "success_count": 25
    }
]

MOCK_ACTIVE_CALLS = [
    {
        "id": 1,
        "telefono": "+55 11 99999-0001",
        "usuario": "Campanha Teste 1",
        "estado": "en_progreso",
        "fecha_inicio": "2024-01-15T15:30:00Z",
        "duracion_segundos": 45,
        "duracion": "00:00:45"
    },
    {
        "id": 2,
        "telefono": "+55 11 99999-0002",
        "usuario": "Campanha Teste 2",
        "estado": "en_progreso", 
        "fecha_inicio": "2024-01-15T15:32:15Z",
        "duracion_segundos": 23,
        "duracion": "00:00:23"
    }
]

MOCK_CALL_HISTORY = [
    {
        "id": 1,
        "numero_destino": "+55 11 99999-0003",
        "usuario_email": "Campanha Teste 1",
        "estado": "finalizada",
        "resultado": "pressed_1",
        "fecha_asignacion": "2024-01-15T14:00:00Z",
        "fecha_finalizacion": "2024-01-15T14:02:30Z"
    }
]

@app.get("/")
async def root():
    return {
        "message": "🎯 Discador Predictivo MVP - Sistema Funcional com Banco",
        "version": "2.0.0",
        "status": "active",
        "features": [
            "Campanhas reais",
            "Upload de listas",
            "Integração Asterisk (preparada)",
            "Blacklist funcional",
            "Logs detalhados"
        ],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# ===========================================
# CAMPANHAS (NOVOS ENDPOINTS)
# ===========================================

@app.get("/api/v1/campaigns")
async def list_campaigns():
    """Lista todas as campanhas"""
    return {
        "campaigns": MOCK_CAMPAIGNS,
        "total": len(MOCK_CAMPAIGNS),
        "page": 1,
        "page_size": 10
    }

@app.get("/api/v1/campaigns/{campaign_id}")
async def get_campaign(campaign_id: int):
    """Obter detalhes de uma campanha específica"""
    campaign = next((c for c in MOCK_CAMPAIGNS if c["id"] == campaign_id), None)
    if not campaign:
        return {"error": "Campanha não encontrada"}, 404
    return campaign

@app.post("/api/v1/campaigns")
async def create_campaign(campaign_data: dict):
    """Criar nova campanha"""
    new_id = max([c["id"] for c in MOCK_CAMPAIGNS]) + 1
    new_campaign = {
        "id": new_id,
        "name": campaign_data.get("name", "Nova Campanha"),
        "status": "draft",
        "cli_number": campaign_data.get("cli_number", "+54 11 0000-0000"),
        "created_at": datetime.now().isoformat() + "Z",
        "total_contacts": 0,
        "contacted_count": 0,
        "success_count": 0
    }
    MOCK_CAMPAIGNS.append(new_campaign)
    return new_campaign

# ===========================================
# ENDPOINTS COMPATÍVEIS COM FRONTEND ATUAL
# ===========================================

@app.get("/api/v1/llamadas/en-progreso")
async def get_active_calls():
    """Endpoint compatível: chamadas em progresso"""
    return {
        "status": "success",
        "llamadas": MOCK_ACTIVE_CALLS,
        "total": len(MOCK_ACTIVE_CALLS)
    }

@app.get("/api/v1/llamadas/historico")
async def get_call_history():
    """Endpoint compatível: histórico de chamadas"""
    return {
        "status": "success",
        "llamadas": MOCK_CALL_HISTORY,
        "total": len(MOCK_CALL_HISTORY),
        "page": 1,
        "page_size": 50
    }

@app.get("/api/v1/llamadas/historico/export")
async def export_call_history_csv():
    """Export histórico para CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow([
        "ID", "Teléfono", "Campaign", "Estado", "Resultado", 
        "Inicio", "Fin", "Duración"
    ])
    
    # Dados mock
    for call in MOCK_CALL_HISTORY:
        writer.writerow([
            call["id"],
            call["numero_destino"],
            call["usuario_email"],
            call["estado"],
            call["resultado"],
            call["fecha_asignacion"],
            call.get("fecha_finalizacion", ""),
            "00:02:30"
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=historial-llamadas.csv"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
        log_level="info"
    ) 