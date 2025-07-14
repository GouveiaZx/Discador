#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Minimal Backend Server")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Minimal server is running"}

@app.get("/api/v1/health")
async def health_v1():
    return {"status": "ok", "message": "Minimal server is running", "version": "v1"}

@app.get("/")
async def root():
    return {"message": "Minimal backend server"}

# Presione1 endpoints
@app.post("/api/v1/presione1/campanhas/{campaign_id}/iniciar")
async def start_campaign(campaign_id: int):
    return {
        "success": True,
        "message": f"Campaign {campaign_id} started successfully",
        "campaign_id": campaign_id
    }

@app.post("/api/v1/presione1/campanhas/{campaign_id}/pausar")
async def pause_campaign(campaign_id: int):
    return {
        "success": True,
        "message": f"Campaign {campaign_id} paused successfully",
        "campaign_id": campaign_id
    }

@app.post("/api/v1/presione1/campanhas/{campaign_id}/retomar")
async def resume_campaign(campaign_id: int):
    return {
        "success": True,
        "message": f"Campaign {campaign_id} resumed successfully",
        "campaign_id": campaign_id
    }

@app.post("/api/v1/presione1/campanhas/{campaign_id}/parar")
async def stop_campaign(campaign_id: int):
    return {
        "success": True,
        "message": f"Campaign {campaign_id} stopped successfully",
        "campaign_id": campaign_id
    }

@app.get("/api/v1/presione1/campanhas")
async def list_campaigns():
    # Retornar array diretamente como esperado pelo frontend
    return [
        {
            "id": 1,
            "nombre": "Campaña de Prueba 1",
            "descripcion": "Descripción de la campaña 1",
            "campaign_id": 1,
            "activa": True,
            "pausada": False,
            "llamadas_simultaneas": 5,
            "tiempo_entre_llamadas": 30,
            "fecha_creacion": "2024-01-15T10:00:00Z",
            "fecha_actualizacion": "2024-01-15T10:00:00Z"
        },
        {
            "id": 2,
            "nombre": "Campaña de Prueba 2",
            "descripcion": "Descripción de la campaña 2",
            "campaign_id": 2,
            "activa": False,
            "pausada": True,
            "llamadas_simultaneas": 3,
            "tiempo_entre_llamadas": 45,
            "fecha_creacion": "2024-01-14T15:30:00Z",
            "fecha_actualizacion": "2024-01-15T09:15:00Z"
        },
        {
            "id": 3,
            "nombre": "Campaña de Prueba 3",
            "descripcion": "Descripción de la campaña 3",
            "campaign_id": 3,
            "activa": False,
            "pausada": False,
            "llamadas_simultaneas": 2,
            "tiempo_entre_llamadas": 60,
            "fecha_creacion": "2024-01-13T08:45:00Z",
            "fecha_actualizacion": "2024-01-14T16:20:00Z"
        }
    ]

@app.get("/api/v1/presione1/campanhas/{campaign_id}")
async def get_campaign(campaign_id: int):
    return {
        "success": True,
        "campaign": {
            "id": campaign_id,
            "name": f"Campaign {campaign_id}",
            "status": "active",
            "calls_made": 150,
            "calls_answered": 45
        }
    }

@app.get("/api/v1/presione1/campanhas/{campaign_id}/estatisticas")
async def get_campaign_stats(campaign_id: int):
    return {
        "success": True,
        "statistics": {
            "campaign_id": campaign_id,
            "total_calls": 200,
            "answered_calls": 60,
            "busy_calls": 80,
            "no_answer_calls": 60,
            "success_rate": 30.0
        }
    }

# Endpoint para campanhas principais
@app.get("/api/v1/campaigns")
async def list_main_campaigns():
    return {
        "success": True,
        "campaigns": [
            {
                "id": 1,
                "name": "Campaña Principal 1",
                "description": "Descripción de la campaña principal 1",
                "cli_number": "1155512345",
                "contacts_total": 1500,
                "max_concurrent_calls": 5,
                "max_attempts": 3,
                "retry_interval": 300,
                "status": "active",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": 2,
                "name": "Campaña Principal 2",
                "description": "Descripción de la campaña principal 2",
                "cli_number": "1155567890",
                "contacts_total": 800,
                "max_concurrent_calls": 3,
                "max_attempts": 2,
                "retry_interval": 450,
                "status": "paused",
                "created_at": "2024-01-14T15:30:00Z",
                "updated_at": "2024-01-15T09:15:00Z"
            },
            {
                "id": 3,
                "name": "Campaña Principal 3",
                "description": "Descripción de la campaña principal 3",
                "cli_number": "1155598765",
                "contacts_total": 2200,
                "max_concurrent_calls": 2,
                "max_attempts": 4,
                "retry_interval": 600,
                "status": "draft",
                "created_at": "2024-01-13T08:45:00Z",
                "updated_at": "2024-01-14T16:20:00Z"
            }
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting minimal server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)