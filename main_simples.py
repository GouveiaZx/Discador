#!/usr/bin/env python3
"""
Main simplificado para deploy no Railway - TOTALMENTE INDEPENDENTE
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn
import os
import io
import csv
from datetime import datetime
import re

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

# Mock data para campanhas
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

@app.post("/api/v1/campaigns/{campaign_id}/upload-contacts")
async def upload_contacts(campaign_id: int, file: UploadFile = File(...)):
    """Upload e processamento de lista de contatos"""
    try:
        # Verificar se campanha existe
        campaign = next((c for c in MOCK_CAMPAIGNS if c["id"] == campaign_id), None)
        if not campaign:
            return {"error": "Campanha não encontrada"}, 404
        
        # Verificar tipo de arquivo
        if not file.filename.lower().endswith(('.csv', '.txt')):
            return {"error": "Formato de arquivo não suportado. Use CSV ou TXT."}, 400
        
        # Ler conteúdo do arquivo
        content = await file.read()
        text = content.decode('utf-8')
        
        # Processar linhas
        lines = text.strip().split('\n')
        contacts_processed = []
        valid_contacts = 0
        invalid_contacts = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            # Detectar separador e dividir colunas
            if ',' in line:
                columns = [col.strip() for col in line.split(',')]
            elif ';' in line:
                columns = [col.strip() for col in line.split(';')]
            elif '|' in line:
                columns = [col.strip() for col in line.split('|')]
            elif '\t' in line:
                columns = [col.strip() for col in line.split('\t')]
            else:
                columns = [line.strip()]
            
            # Extrair telefone e nome
            phone = columns[0] if columns else ''
            name = columns[1] if len(columns) > 1 else ''
            
            # Validar telefone (regex básica)
            phone_cleaned = re.sub(r'[^\d\+]', '', phone)
            if len(phone_cleaned) >= 8 and len(phone_cleaned) <= 20:
                contact = {
                    "line": line_num,
                    "phone": phone,
                    "name": name,
                    "status": "pending",
                    "campaign_id": campaign_id
                }
                contacts_processed.append(contact)
                valid_contacts += 1
            else:
                invalid_contacts += 1
        
        # Simular salvamento no banco (quando tiver Supabase será real)
        # Por enquanto só retornamos estatísticas
        
        # Atualizar contador da campanha
        campaign["total_contacts"] = campaign.get("total_contacts", 0) + valid_contacts
        
        return {
            "status": "success",
            "message": "Lista processada com sucesso",
            "filename": file.filename,
            "total_lines": len(lines),
            "total_contacts": len(contacts_processed),
            "valid_contacts": valid_contacts,
            "invalid_contacts": invalid_contacts,
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"]
        }
        
    except Exception as e:
        return {"error": f"Erro no processamento: {str(e)}"}, 500

@app.get("/api/v1/campaigns/{campaign_id}/contacts")
async def get_campaign_contacts(campaign_id: int):
    """Listar contatos de uma campanha"""
    campaign = next((c for c in MOCK_CAMPAIGNS if c["id"] == campaign_id), None)
    if not campaign:
        return {"error": "Campanha não encontrada"}, 404
    
    # Mock de contatos (quando tiver Supabase será consulta real)
    mock_contacts = [
        {
            "id": 1,
            "phone": "+54 11 1234-5678",
            "name": "Juan Pérez",
            "status": "pending",
            "attempts": 0,
            "created_at": "2025-01-30T10:00:00Z"
        },
        {
            "id": 2,
            "phone": "+54 11 8765-4321", 
            "name": "María García",
            "status": "contacted",
            "attempts": 1,
            "created_at": "2025-01-30T10:05:00Z"
        }
    ]
    
    return {
        "contacts": mock_contacts,
        "total": len(mock_contacts),
        "campaign": campaign
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_level="info"
    ) 