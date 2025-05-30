#!/usr/bin/env python3
"""
Main simplificado para deploy no Railway - TOTALMENTE INDEPENDENTE
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn
import os
import io
import csv
from datetime import datetime

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
                "telefono": "+55 11 99999-0001",
                "usuario": "Cliente Teste 1",
                "estado": "en_progreso",
                "fecha_inicio": "2025-01-30T15:30:00Z",
                "duracion_segundos": 165,
                "duracion": "00:02:45"
            },
            {
                "id": 2,
                "telefono": "+55 11 99999-0002",
                "usuario": "Cliente Teste 2",
                "estado": "en_progreso",
                "fecha_inicio": "2025-01-30T15:28:15Z",
                "duracion_segundos": 312,
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
                "telefono": "+55 11 99999-0003",
                "usuario": "Cliente Teste 3",
                "estado": "finalizada",
                "resultado": "contacto_efectivo",
                "fecha_inicio": "2025-01-30T14:30:00Z",
                "fecha_fin": "2025-01-30T14:32:30Z",
                "duracion_segundos": 150,
                "duracion": "00:02:30"
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 10
    }

@app.get("/api/v1/llamadas/historico/export")
async def exportar_historico_csv(export: str = None):
    """Exportar histórico para CSV"""
    # Dados mock para exportação
    datos = [
        {
            "ID": 3,
            "Teléfono": "+55 11 99999-0003",
            "Usuario": "Cliente Teste 3",
            "Estado": "finalizada",
            "Resultado": "contacto_efectivo",
            "Inicio": "2025-01-30T14:30:00Z",
            "Fin": "2025-01-30T14:32:30Z",
            "Duración": "00:02:30"
        },
        {
            "ID": 4,
            "Teléfono": "+55 11 99999-0004",
            "Usuario": "Cliente Teste 4",
            "Estado": "finalizada",
            "Resultado": "ocupado",
            "Inicio": "2025-01-30T13:30:00Z",
            "Fin": "2025-01-30T13:30:15Z",
            "Duración": "00:00:15"
        }
    ]
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=datos[0].keys())
    writer.writeheader()
    writer.writerows(datos)
    
    csv_content = output.getvalue()
    output.close()
    
    # Retornar como archivo CSV
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=historial-llamadas.csv"}
    )

@app.post("/api/v1/llamadas/finalizar")
async def finalizar_llamada():
    """Mock: Finalizar chamada"""
    return {
        "status": "success",
        "mensaje": "Llamada finalizada correctamente"
    }

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

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_level="info"
    ) 