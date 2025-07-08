#!/usr/bin/env python3
"""
Rotas para controle do sistema de discagem preditiva
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging

from ..services.dialer_worker import get_dialer_worker
from ..services.asterisk_manager import asterisk_ami
from ..services.predictive_algorithm import get_predictive_dialer

router = APIRouter()
logger = logging.getLogger(__name__)

# Schemas
class CampaignControlRequest(BaseModel):
    campaign_id: int
    action: str  # start, pause, resume, stop
    cli_number: Optional[str] = None

class DialerConfigRequest(BaseModel):
    max_calls_per_second: Optional[int] = None
    min_calls_per_second: Optional[int] = None
    target_answer_rate: Optional[float] = None
    agent_capacity: Optional[int] = None

@router.post("/dialer/start")
async def start_dialer(background_tasks: BackgroundTasks):
    """
    Inicia o sistema de discagem preditiva
    """
    try:
        worker = get_dialer_worker()
        
        if worker.running:
            return JSONResponse(
                content={"message": "Sistema de discagem já está ativo", "status": "running"},
                status_code=200
            )
        
        # Iniciar em background
        background_tasks.add_task(worker.start)
        
        logger.info("🚀 Sistema de discagem iniciado via API")
        
        return JSONResponse(
            content={
                "message": "Sistema de discagem iniciado com sucesso",
                "status": "starting"
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar discador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dialer/stop")
async def stop_dialer(background_tasks: BackgroundTasks):
    """
    Para o sistema de discagem preditiva
    """
    try:
        worker = get_dialer_worker()
        
        if not worker.running:
            return JSONResponse(
                content={"message": "Sistema de discagem já está parado", "status": "stopped"},
                status_code=200
            )
        
        # Parar em background
        background_tasks.add_task(worker.stop)
        
        logger.info("🛑 Sistema de discagem parado via API")
        
        return JSONResponse(
            content={
                "message": "Sistema de discagem parado com sucesso",
                "status": "stopping"
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao parar discador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dialer/status")
async def get_dialer_status():
    """
    Retorna o status atual do sistema de discagem
    """
    try:
        worker = get_dialer_worker()
        predictive = get_predictive_dialer()
        
        status = worker.get_status()
        
        # Adicionar informações do Asterisk
        status["asterisk_connected"] = asterisk_ami.connected
        status["asterisk_authenticated"] = asterisk_ami.authenticated
        
        # Adicionar informações das chamadas ativas
        active_calls = await asterisk_ami.get_active_calls()
        status["asterisk_active_calls"] = len(active_calls)
        
        return JSONResponse(content=status, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dialer/campaign/control")
async def control_campaign(request: CampaignControlRequest):
    """
    Controla uma campanha específica (iniciar, pausar, parar)
    """
    try:
        worker = get_dialer_worker()
        
        if request.action == "start":
            # Buscar dados da campanha
            from ..database import get_db_connection
            
            conn = await get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, cli_number FROM campaigns 
                WHERE id = ?
            """, (request.campaign_id,))
            
            campaign_data = cursor.fetchone()
            conn.close()
            
            if not campaign_data:
                raise HTTPException(status_code=404, detail="Campanha não encontrada")
            
            # Adicionar campanha ao worker
            await worker.add_campaign(
                campaign_id=request.campaign_id,
                name=campaign_data[0],
                cli_number=request.cli_number or campaign_data[1] or "+5511999999999"
            )
            
            message = f"Campanha {request.campaign_id} iniciada"
            
        elif request.action == "pause":
            await worker.pause_campaign(request.campaign_id)
            message = f"Campanha {request.campaign_id} pausada"
            
        elif request.action == "resume":
            await worker.resume_campaign(request.campaign_id)
            message = f"Campanha {request.campaign_id} retomada"
            
        elif request.action == "stop":
            await worker.remove_campaign(request.campaign_id)
            message = f"Campanha {request.campaign_id} parada"
            
        else:
            raise HTTPException(status_code=400, detail="Ação inválida")
        
        logger.info(f"📋 Controle de campanha: {message}")
        
        return JSONResponse(
            content={"message": message, "campaign_id": request.campaign_id},
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao controlar campanha: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dialer/campaigns")
async def get_active_campaigns():
    """
    Lista campanhas ativas no discador
    """
    try:
        worker = get_dialer_worker()
        
        campaigns = []
        for campaign_id, config in worker.active_campaigns.items():
            campaigns.append({
                "campaign_id": campaign_id,
                "name": config.name,
                "status": "active" if config.active else "paused",
                "cli_number": config.cli_number
            })
        
        return JSONResponse(content={"campaigns": campaigns}, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar campanhas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dialer/stats")
async def get_dialer_stats():
    """
    Retorna estatísticas detalhadas do discador
    """
    try:
        predictive = get_predictive_dialer()
        
        stats = {
            "current_stats": predictive.get_current_stats(),
            "hourly_stats": predictive.get_hourly_stats(),
            "recent_performance": predictive._get_recent_metrics().__dict__
        }
        
        return JSONResponse(content=stats, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dialer/config")
async def update_dialer_config(request: DialerConfigRequest):
    """
    Atualiza configurações do algoritmo preditivo
    """
    try:
        predictive = get_predictive_dialer()
        
        # Atualizar configurações
        if request.max_calls_per_second is not None:
            predictive.config.max_calls_per_second = request.max_calls_per_second
            
        if request.min_calls_per_second is not None:
            predictive.config.min_calls_per_second = request.min_calls_per_second
            
        if request.target_answer_rate is not None:
            predictive.config.target_answer_rate = request.target_answer_rate
            
        if request.agent_capacity is not None:
            predictive.config.agent_capacity = request.agent_capacity
            predictive.update_agent_status(request.agent_capacity)
        
        logger.info("⚙️ Configurações do discador atualizadas")
        
        return JSONResponse(
            content={
                "message": "Configurações atualizadas com sucesso",
                "config": {
                    "max_calls_per_second": predictive.config.max_calls_per_second,
                    "min_calls_per_second": predictive.config.min_calls_per_second,
                    "target_answer_rate": predictive.config.target_answer_rate,
                    "agent_capacity": predictive.config.agent_capacity
                }
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar configurações: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dialer/active-calls")
async def get_active_calls():
    """
    Lista todas as chamadas ativas
    """
    try:
        active_calls = await asterisk_ami.get_active_calls()
        
        calls_data = []
        for call in active_calls:
            calls_data.append({
                "call_id": call.call_id,
                "phone_number": call.phone_number,
                "campaign_id": call.campaign_id,
                "status": call.status.value,
                "duration": int(time.time() - call.timestamp),
                "dtmf_pressed": call.dtmf_pressed,
                "transferred": call.transferred
            })
        
        return JSONResponse(content={"active_calls": calls_data}, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter chamadas ativas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dialer/hangup/{call_id}")
async def hangup_call(call_id: str):
    """
    Finaliza uma chamada específica
    """
    try:
        success = await asterisk_ami.hangup_call(call_id)
        
        if success:
            return JSONResponse(
                content={"message": f"Chamada {call_id} finalizada com sucesso"},
                status_code=200
            )
        else:
            raise HTTPException(status_code=404, detail="Chamada não encontrada")
            
    except Exception as e:
        logger.error(f"❌ Erro ao finalizar chamada: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dialer/health")
async def health_check():
    """
    Verifica saúde do sistema de discagem
    """
    try:
        worker = get_dialer_worker()
        
        health = {
            "status": "healthy" if worker.running else "stopped",
            "components": {
                "worker": worker.running,
                "asterisk": asterisk_ami.connected,
                "predictive_algorithm": True
            },
            "timestamp": time.time()
        }
        
        # Verificar se há problemas
        issues = []
        if not worker.running:
            issues.append("Worker não está executando")
        if not asterisk_ami.connected:
            issues.append("Asterisk não conectado")
        if len(worker.active_campaigns) == 0:
            issues.append("Nenhuma campanha ativa")
        
        health["issues"] = issues
        health["healthy"] = len(issues) == 0
        
        return JSONResponse(content=health, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Erro no health check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Incluir time no escopo
import time 