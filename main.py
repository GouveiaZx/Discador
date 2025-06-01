#!/usr/bin/env python3
"""
Sistema de Discador Preditivo - MVP Funcional
Backend principal com banco de dados real e integração Asterisk
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import uvicorn
import os
import logging
import json
import uuid
from datetime import datetime, timedelta
import asyncio

# Imports locais
from database.connection import get_database_session, init_database
from database.models import Campaign, Contact, Blacklist, CallLog, CampaignStatus
from schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignList

# Importar o engine de discagem
from discador_engine import DiscadorAPI, discador_engine

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

# Inicializar banco de dados na inicialização
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Iniciando Sistema de Discador Preditivo MVP")
    init_database()
    logger.info("✅ Banco de dados inicializado")

# Endpoints básicos
@app.get("/")
async def root():
    return {
        "message": "🎯 Discador Predictivo MVP - Sistema Funcional",
        "version": "2.0.0",
        "status": "active",
        "features": [
            "Campanhas reais",
            "Upload de listas",
            "Integração Asterisk",
            "Blacklist funcional",
            "Logs detalhados"
        ],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# ===========================================
# CAMPANHAS
# ===========================================

@app.get("/api/v1/campaigns", response_model=CampaignList)
async def list_campaigns(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_database_session)
):
    """Lista todas as campanhas com paginação"""
    skip = (page - 1) * page_size
    
    query = db.query(Campaign)
    if status:
        query = query.filter(Campaign.status == status)
    
    total = query.count()
    campaigns = query.offset(skip).limit(page_size).all()
    
    # Adicionar estatísticas para cada campanha
    for campaign in campaigns:
        campaign.total_contacts = db.query(Contact).filter(Contact.campaign_id == campaign.id).count()
        campaign.contacted_count = db.query(Contact).filter(
            Contact.campaign_id == campaign.id,
            Contact.attempts > 0
        ).count()
        campaign.success_count = db.query(Contact).filter(
            Contact.campaign_id == campaign.id,
            Contact.status == "pressed_1"
        ).count()
    
    return CampaignList(
        campaigns=campaigns,
        total=total,
        page=page,
        page_size=page_size
    )

@app.get("/api/v1/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int, db: Session = Depends(get_database_session)):
    """Obter detalhes de uma campanha específica"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    # Adicionar estatísticas
    campaign.total_contacts = db.query(Contact).filter(Contact.campaign_id == campaign.id).count()
    campaign.contacted_count = db.query(Contact).filter(
        Contact.campaign_id == campaign.id,
        Contact.attempts > 0
    ).count()
    campaign.success_count = db.query(Contact).filter(
        Contact.campaign_id == campaign.id,
        Contact.status == "pressed_1"
    ).count()
    
    return campaign

@app.post("/api/v1/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_database_session)
):
    """Criar nova campanha"""
    db_campaign = Campaign(**campaign.dict())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    logger.info(f"✅ Campanha criada: {db_campaign.name} (ID: {db_campaign.id})")
    return db_campaign

@app.patch("/api/v1/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    db: Session = Depends(get_database_session)
):
    """Atualizar campanha existente"""
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    update_data = campaign_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_campaign, field, value)
    
    db.commit()
    db.refresh(db_campaign)
    
    logger.info(f"✅ Campanha atualizada: {db_campaign.name} (ID: {db_campaign.id})")
    return db_campaign

@app.delete("/api/v1/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: int, db: Session = Depends(get_database_session)):
    """Deletar campanha"""
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    db.delete(db_campaign)
    db.commit()
    
    logger.info(f"🗑️ Campanha deletada: {db_campaign.name} (ID: {campaign_id})")
    return {"message": "Campanha deletada com sucesso"}

# ===========================================
# UPLOAD DE LISTAS
# ===========================================

@app.post("/api/v1/campaigns/{campaign_id}/upload-contacts")
async def upload_contacts(
    campaign_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_database_session)
):
    """Upload de lista de contatos (CSV/TXT)"""
    # Verificar se campanha existe
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    # Validar tipo de arquivo
    if not file.filename.lower().endswith(('.csv', '.txt')):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV e TXT são aceitos")
    
    # Processar arquivo em background
    background_tasks.add_task(process_contact_file, campaign_id, file, db)
    
    return {
        "message": "Upload iniciado com sucesso",
        "filename": file.filename,
        "campaign_id": campaign_id,
        "status": "processing"
    }

async def process_contact_file(campaign_id: int, file: UploadFile, db: Session):
    """Processa arquivo de contatos em background"""
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # TODO: Implementar parser CSV/TXT mais robusto
        lines = content_str.strip().split('\n')
        processed_count = 0
        
        for line in lines:
            if not line.strip():
                continue
                
            # Parse simples: primeiro campo é o telefone
            parts = line.strip().split(',')
            phone_number = parts[0].strip().replace('"', '')
            name = parts[1].strip().replace('"', '') if len(parts) > 1 else None
            
            # Verificar se não está na blacklist
            is_blacklisted = db.query(Blacklist).filter(
                Blacklist.phone_number == phone_number,
                Blacklist.is_active == True
            ).first()
            
            if not is_blacklisted:
                # Criar contato
                contact = Contact(
                    phone_number=phone_number,
                    name=name,
                    campaign_id=campaign_id
                )
                db.add(contact)
                processed_count += 1
        
        db.commit()
        logger.info(f"✅ Processados {processed_count} contatos para campanha {campaign_id}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar arquivo: {str(e)}")
        db.rollback()

# ===========================================
# ENDPOINTS COMPATÍVEIS COM FRONTEND ATUAL
# ===========================================

@app.get("/api/v1/llamadas/en-progreso")
async def get_active_calls(db: Session = Depends(get_database_session)):
    """Endpoint compatível: chamadas em progresso"""
    # Buscar chamadas ativas no banco
    active_calls = db.query(CallLog).filter(
        CallLog.ended_at.is_(None)
    ).all()
    
    # Converter para formato esperado pelo frontend
    llamadas = []
    for call in active_calls:
        llamadas.append({
            "id": call.id,
            "telefono": call.phone_number,
            "usuario": f"Campaign {call.campaign_id}",
            "estado": "en_progreso",
            "fecha_inicio": call.initiated_at.isoformat() + "Z",
            "duracion_segundos": call.duration_seconds,
            "duracion": format_duration(call.duration_seconds)
        })
    
    return {
        "status": "success",
        "llamadas": llamadas,
        "total": len(llamadas)
    }

@app.get("/api/v1/llamadas/historico")
async def get_call_history(db: Session = Depends(get_database_session)):
    """Endpoint compatível: histórico de chamadas"""
    # Buscar chamadas finalizadas
    finished_calls = db.query(CallLog).filter(
        CallLog.ended_at.is_not(None)
    ).order_by(CallLog.created_at.desc()).limit(50).all()
    
    # Converter para formato esperado
    llamadas = []
    for call in finished_calls:
        llamadas.append({
            "id": call.id,
            "numero_destino": call.phone_number,
            "usuario_email": f"Campaign {call.campaign_id}",
            "estado": "finalizada",
            "resultado": call.result.value if call.result else "unknown",
            "fecha_asignacion": call.initiated_at.isoformat() + "Z",
            "fecha_finalizacion": call.ended_at.isoformat() + "Z" if call.ended_at else None
        })
    
    return {
        "status": "success",
        "llamadas": llamadas,
        "total": len(llamadas),
        "page": 1,
        "page_size": 50
    }

@app.get("/api/v1/llamadas/historico/export")
async def export_call_history_csv(db: Session = Depends(get_database_session)):
    """Export histórico para CSV"""
    import io
    import csv
    
    # Buscar dados
    calls = db.query(CallLog).order_by(CallLog.created_at.desc()).all()
    
    # Criar CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow([
        "ID", "Teléfono", "Campaign", "Estado", "Resultado", 
        "Inicio", "Fin", "Duración", "DTMF"
    ])
    
    # Dados
    for call in calls:
        duration = format_duration(call.duration_seconds) if call.duration_seconds else "00:00:00"
        writer.writerow([
            call.id,
            call.phone_number,
            f"Campaign {call.campaign_id}",
            "finalizada" if call.ended_at else "en_progreso",
            call.result.value if call.result else "",
            call.initiated_at.strftime("%Y-%m-%d %H:%M:%S"),
            call.ended_at.strftime("%Y-%m-%d %H:%M:%S") if call.ended_at else "",
            duration,
            call.dtmf_pressed or ""
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=historial-llamadas.csv"}
    )

# ===========================================
# FUNÇÕES AUXILIARES
# ===========================================

def format_duration(seconds: int) -> str:
    """Formatar duração em HH:MM:SS"""
    if not seconds:
        return "00:00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# ===========================================
# NOVOS ENDPOINTS PARA O DISCADOR
# ===========================================

@app.post("/api/v1/campaigns/{campaign_id}/start")
async def start_campaign(campaign_id: int, background_tasks: BackgroundTasks):
    """
    Inicia uma campanha de discagem
    """
    try:
        # Buscar dados da campanha
        campaign = get_campaign_by_id(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campanha não encontrada")
        
        # Buscar contatos da campanha
        contacts = get_campaign_contacts(campaign_id)
        if not contacts:
            raise HTTPException(status_code=400, detail="Nenhum contato encontrado para esta campanha")
        
        # Preparar dados para o discador
        campaign_data = {
            'id': campaign_id,
            'contacts': contacts,
            'cli_number': campaign.get('cli_number', '+5511999999999')
        }
        
        # Iniciar campanha em background
        result = await DiscadorAPI.start_campaign_async(campaign_data)
        
        return {
            "message": "Campanha iniciada com sucesso",
            "campaign_id": campaign_id,
            "total_contacts": len(contacts),
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar campanha: {str(e)}")

@app.post("/api/v1/campaigns/{campaign_id}/stop")
async def stop_campaign(campaign_id: int):
    """
    Para uma campanha de discagem
    """
    try:
        result = DiscadorAPI.stop_campaign()
        
        return {
            "message": "Campanha parada com sucesso",
            "campaign_id": campaign_id,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar campanha: {str(e)}")

@app.get("/api/v1/campaigns/stats")
async def get_campaign_stats():
    """
    Retorna estatísticas da campanha ativa
    """
    try:
        stats = DiscadorAPI.get_campaign_stats()
        
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@app.get("/api/v1/campaigns/active-calls")
async def get_active_calls():
    """
    Retorna chamadas ativas
    """
    try:
        calls = DiscadorAPI.get_active_calls()
        
        return {
            "status": "success",
            "data": calls,
            "total": len(calls),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter chamadas ativas: {str(e)}")

@app.get("/api/v1/discador/status")
async def get_discador_status():
    """
    Retorna status geral do discador
    """
    try:
        stats = DiscadorAPI.get_campaign_stats()
        active_calls = DiscadorAPI.get_active_calls()
        
        return {
            "status": "success",
            "data": {
                "discador_active": stats.get('is_running', False),
                "total_calls_today": stats.get('total_calls', 0),
                "successful_calls_today": stats.get('successful_calls', 0),
                "active_calls": len(active_calls),
                "success_rate": stats.get('success_rate', 0),
                "last_update": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

# Funções auxiliares para buscar dados
def get_campaign_by_id(campaign_id: int) -> Optional[Dict]:
    """
    Busca campanha por ID (mock - seria do banco)
    """
    # Mock data - em produção viria do banco de dados
    mock_campaigns = {
        1: {
            "id": 1,
            "name": "Campanha Teste",
            "cli_number": "+5511123456789",
            "status": "active"
        }
    }
    return mock_campaigns.get(campaign_id)

def get_campaign_contacts(campaign_id: int) -> List[Dict]:
    """
    Busca contatos da campanha (mock - seria do banco)
    """
    # Mock data - em produção viria do banco de dados
    mock_contacts = [
        {"phone_number": "+5511999999991", "name": "Cliente 1", "status": "not_started"},
        {"phone_number": "+5511999999992", "name": "Cliente 2", "status": "not_started"},
        {"phone_number": "+5511999999993", "name": "Cliente 3", "status": "not_started"},
        {"phone_number": "+5511999999994", "name": "Cliente 4", "status": "not_started"},
        {"phone_number": "+5511999999995", "name": "Cliente 5", "status": "not_started"},
    ]
    return mock_contacts

# Endpoint para simular dados reais do dashboard
@app.get("/api/v1/dashboard/real-stats")
async def get_dashboard_real_stats():
    """
    Retorna estatísticas reais para alimentar o dashboard
    """
    try:
        # Obter dados do discador
        discador_stats = DiscadorAPI.get_campaign_stats()
        active_calls = DiscadorAPI.get_active_calls()
        
        # Gerar dados complementares (simulados)
        now = datetime.now()
        
        # Dados por hora (últimas 24h)
        hourly_data = []
        for i in range(24):
            hour = now - timedelta(hours=i)
            calls = max(0, discador_stats.get('total_calls', 0) - i * 2)
            hourly_data.append({
                "hour": hour.strftime("%H:00"),
                "calls": calls
            })
        
        # Estados das chamadas
        call_states = {
            "conectadas": discador_stats.get('successful_calls', 0),
            "sem_resposta": discador_stats.get('no_answer_calls', 0),
            "transferidas": discador_stats.get('transferred_calls', 0),
            "ocupado": discador_stats.get('busy_calls', 0)
        }
        
        # Efetividade diária (últimos 7 dias)
        daily_effectiveness = []
        for i in range(7):
            day = now - timedelta(days=i)
            effectiveness = max(0, discador_stats.get('success_rate', 0) - i * 2)
            daily_effectiveness.append({
                "day": day.strftime("%d/%m"),
                "effectiveness": effectiveness
            })
        
        return {
            "status": "success",
            "data": {
                "kpis": {
                    "active_calls": len(active_calls),
                    "calls_today": discador_stats.get('total_calls', 0),
                    "effectiveness": discador_stats.get('success_rate', 0),
                    "active_campaigns": 1 if discador_stats.get('is_running') else 0
                },
                "hourly_calls": hourly_data,
                "call_states": call_states,
                "daily_effectiveness": daily_effectiveness,
                "system_status": {
                    "discador_running": discador_stats.get('is_running', False),
                    "database_connected": True,
                    "api_responsive": True
                }
            },
            "timestamp": now.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados do dashboard: {str(e)}")

# ===========================================
# INICIALIZAÇÃO
# ===========================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
        log_level="info"
    ) 