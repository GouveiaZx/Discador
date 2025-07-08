#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas REST para o Painel de Monitoramento em Tempo Real
Endpoints para dashboards, metricas e controle de campanhas
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json
import csv
import io

from app.database import get_db
from app.services.monitoring_service import MonitoringService, get_monitoring_service
from app.models.monitoring import AgenteMonitoramento, EventoSistema, SessionMonitoramento
from app.schemas.monitoring import (
    DashboardResumo, DashboardDetalhado, MetricaCampanha, MetricaProvedor,
    MetricaAgente, AgenteResponse, AgenteCreate, AgenteUpdate, AgenteStatusUpdate,
    EventoSistemaResponse, EventoSistemaCreate, ChamadaResponse,
    FiltroMonitoramento, ExportRequest, ResponseSucesso, ResponseErro,
    WebSocketMessage, StatusAgente, StatusChamada, TipoEventoMonitoramento
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["Monitoramento"])

# ================================================
# CONEXOES WEBSOCKET ATIVAS
# ================================================

class ConnectionManager:
    """Gerenciador de conexoes WebSocket"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
    
    async def send_to_user(self, user_id: int, message: dict):
        """Envia mensagem para usuario especifico"""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message, default=str))
                except Exception as e:
                    logger.error(f"Erro ao enviar mensagem WebSocket para usuario {user_id}: {e}")
    
    async def broadcast(self, message: dict):
        """Envia mensagem para todas as conexoes"""
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.error(f"Erro ao enviar broadcast WebSocket: {e}")

manager = ConnectionManager()

# ================================================
# DASHBOARDS PRINCIPAIS
# ================================================

@router.get("/dashboard/resumo", response_model=DashboardResumo)
async def obter_dashboard_resumo(
    service: MonitoringService = Depends(get_monitoring_service)
):
    """
    Obtem dashboard resumido para supervisores
    
    **Dados incluidos:**
    - Campanhas ativas
    - Chamadas em andamento
    - Status de agentes
    - Status de provedores SIP
    - Alertas recentes
    """
    try:
        dashboard = service.obter_dashboard_resumo()
        return dashboard
        
    except Exception as e:
        logger.error(f"Erro ao obter dashboard resumo: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/dashboard/detalhado", response_model=DashboardDetalhado)
async def obter_dashboard_detalhado(
    service: MonitoringService = Depends(get_monitoring_service)
):
    """
    Obtem dashboard detalhado com todas as metricas
    
    **Dados incluidos:**
    - Todas as metricas do dashboard resumido
    - Campanhas detalhadas
    - Agentes detalhados
    - Chamadas ativas
    - Eventos recentes
    - Performance do sistema
    """
    try:
        dashboard = service.obter_dashboard_detalhado()
        return dashboard
        
    except Exception as e:
        logger.error(f"Erro ao obter dashboard detalhado: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ================================================
# METRICAS ESPECIFICAS
# ================================================

@router.get("/campanhas", response_model=List[MetricaCampanha])
async def obter_metricas_campanhas(
    apenas_ativas: bool = Query(True, description="Filtrar apenas campanhas ativas"),
    service: MonitoringService = Depends(get_monitoring_service)
):
    """
    Obtem metricas de campanhas
    
    **Metricas incluidas:**
    - Total de contatos e chamadas
    - Status das chamadas (ativas, finalizadas, erro)
    - Taxas de atendimento e sucesso
    - Tempos medios
    - Provedores utilizados
    """
    try:
        campanhas = service.obter_metricas_campanhas(apenas_ativas=apenas_ativas)
        return campanhas
        
    except Exception as e:
        logger.error(f"Erro ao obter metricas de campanhas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/provedores", response_model=List[MetricaProvedor])
async def obter_metricas_provedores(
    service: MonitoringService = Depends(get_monitoring_service)
):
    """
    Obtem metricas de provedores SIP
    
    **Metricas incluidas:**
    - Status de conexao
    - Chamadas ativas e do dia
    - Taxa de sucesso e falhas
    - Latencia media
    - Uptime percentual
    """
    try:
        provedores = service.obter_metricas_provedores()
        return provedores
        
    except Exception as e:
        logger.error(f"Erro ao obter metricas de provedores: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/agentes", response_model=List[MetricaAgente])
async def obter_metricas_agentes(
    service: MonitoringService = Depends(get_monitoring_service)
):
    """
    Obtem metricas de agentes
    
    **Metricas incluidas:**
    - Status atual (livre, em chamada, ausente, etc.)
    - Tempo online e em chamadas
    - Chamadas atendidas no dia
    - Performance individual
    """
    try:
        agentes = service.obter_metricas_agentes()
        return agentes
        
    except Exception as e:
        logger.error(f"Erro ao obter metricas de agentes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ================================================
# GESTAO DE AGENTES
# ================================================

@router.post("/agentes", response_model=AgenteResponse)
async def criar_agente(
    agente: AgenteCreate,
    db: Session = Depends(get_db),
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Cria um novo agente para monitoramento"""
    try:
        # Verificar se codigo ja existe
        agente_existente = db.query(AgenteMonitoramento).filter(
            AgenteMonitoramento.codigo_agente == agente.codigo_agente
        ).first()
        
        if agente_existente:
            raise HTTPException(
                status_code=400,
                detail="Codigo de agente ja existe"
            )
        
        # Criar agente
        novo_agente = AgenteMonitoramento(**agente.dict())
        db.add(novo_agente)
        db.commit()
        db.refresh(novo_agente)
        
        # Invalidar cache
        service._invalidate_cache("agentes")
        
        # Registrar evento
        evento = EventoSistemaCreate(
            tipo_evento="agente_login",
            titulo=f"Novo agente cadastrado: {agente.nome_agente}",
            agente_id=novo_agente.id,
            nivel_severidade="info"
        )
        service.registrar_evento(evento)
        
        return novo_agente
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar agente: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/agentes/{agente_id}/status", response_model=ResponseSucesso)
async def atualizar_status_agente(
    agente_id: int,
    status_update: AgenteStatusUpdate,
    db: Session = Depends(get_db),
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Atualiza status de um agente"""
    try:
        agente = db.query(AgenteMonitoramento).filter(
            AgenteMonitoramento.id == agente_id
        ).first()
        
        if not agente:
            raise HTTPException(status_code=404, detail="Agente nao encontrado")
        
        # Atualizar status
        service.atualizar_agente_status(
            agente_id=agente_id,
            status=status_update.status_atual,
            chamada_id=status_update.chamada_atual_id
        )
        
        # Enviar atualizacao via WebSocket
        await manager.broadcast({
            "tipo": "agente_status_update",
            "dados": {
                "agente_id": agente_id,
                "status": status_update.status_atual.value,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        return ResponseSucesso(
            mensagem=f"Status do agente {agente.nome_agente} atualizado para {status_update.status_atual.value}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar status do agente {agente_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ================================================
# EVENTOS E LOGS
# ================================================

@router.get("/eventos", response_model=List[EventoSistemaResponse])
async def listar_eventos(
    limit: int = Query(50, le=200, description="Limite de eventos"),
    nivel: Optional[str] = Query(None, description="Filtrar por nivel de severidade"),
    ultimas_horas: Optional[int] = Query(24, ge=1, le=168, description="Eventos das ultimas N horas"),
    db: Session = Depends(get_db)
):
    """Lista eventos do sistema com filtros"""
    try:
        query = db.query(EventoSistema)
        
        # Filtro temporal
        if ultimas_horas:
            data_limite = datetime.utcnow() - timedelta(hours=ultimas_horas)
            query = query.filter(EventoSistema.timestamp_evento >= data_limite)
        
        # Filtro por nivel
        if nivel:
            query = query.filter(EventoSistema.nivel_severidade == nivel)
        
        # Ordenar por mais recente
        eventos = query.order_by(EventoSistema.timestamp_evento.desc()).limit(limit).all()
        
        return eventos
        
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/eventos", response_model=ResponseSucesso)
async def criar_evento(
    evento: EventoSistemaCreate,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Registra um novo evento no sistema"""
    try:
        service.registrar_evento(evento)
        
        # Enviar via WebSocket se for critico
        if evento.nivel_severidade in ["critical", "error"]:
            await manager.broadcast({
                "tipo": "evento_critico",
                "dados": {
                    "titulo": evento.titulo,
                    "descricao": evento.descricao,
                    "nivel": evento.nivel_severidade,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
        
        return ResponseSucesso(
            mensagem="Evento registrado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao registrar evento: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ================================================
# EXPORTACAO DE DADOS
# ================================================

@router.post("/export/csv")
async def exportar_dados_csv(
    export_request: ExportRequest,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Exporta dados de monitoramento em CSV"""
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Campanhas
        if export_request.incluir_chamadas:
            campanhas = service.obter_metricas_campanhas(apenas_ativas=False)
            
            if export_request.incluir_cabecalhos:
                writer.writerow([
                    "ID Campanha", "Nome", "Status", "Total Contatos",
                    "Chamadas Realizadas", "Chamadas Ativas", "Taxa Atendimento",
                    "Taxa Sucesso", "Tempo Medio"
                ])
            
            for campanha in campanhas:
                writer.writerow([
                    campanha.campanha_id,
                    campanha.nome_campanha,
                    campanha.status_campanha,
                    campanha.total_contatos,
                    campanha.chamadas_realizadas,
                    campanha.chamadas_ativas,
                    campanha.taxa_atendimento,
                    campanha.taxa_sucesso,
                    campanha.tempo_medio_chamada
                ])
        
        # Agentes
        if export_request.incluir_agentes:
            agentes = service.obter_metricas_agentes()
            
            writer.writerow([])  # Linha vazia
            if export_request.incluir_cabecalhos:
                writer.writerow([
                    "ID Agente", "Nome", "Codigo", "Status",
                    "Online Desde", "Chamadas Atendidas", "Tempo em Chamadas",
                    "Taxa Atendimento"
                ])
            
            for agente in agentes:
                writer.writerow([
                    agente.agente_id,
                    agente.nome_agente,
                    agente.codigo_agente,
                    agente.status_atual.value,
                    agente.online_desde.isoformat() if agente.online_desde else "",
                    agente.chamadas_atendidas,
                    agente.tempo_em_chamadas,
                    agente.taxa_atendimento
                ])
        
        # Preparar resposta
        output.seek(0)
        response = StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=monitoramento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Erro ao exportar CSV: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ================================================
# WEBSOCKET PARA ATUALIZACOES EM TEMPO REAL
# ================================================

@router.websocket("/ws/{user_id}")
async def websocket_monitoring(websocket: WebSocket, user_id: int):
    """
    WebSocket para atualizacoes em tempo real
    
    **Tipos de mensagem enviadas:**
    - `dashboard_update`: Atualizacoes do dashboard
    - `agente_status_update`: Mudancas de status de agentes
    - `chamada_update`: Atualizacoes de chamadas
    - `evento_critico`: Eventos criticos do sistema
    """
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Aguardar mensagem do cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Processar comando do cliente
            if message.get("tipo") == "ping":
                await websocket.send_text(json.dumps({
                    "tipo": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            
            elif message.get("tipo") == "solicitar_dashboard":
                # Enviar dashboard atualizado
                service = get_monitoring_service()
                dashboard = service.obter_dashboard_resumo()
                
                await websocket.send_text(json.dumps({
                    "tipo": "dashboard_update",
                    "dados": dashboard.dict(),
                    "timestamp": datetime.utcnow().isoformat()
                }, default=str))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"Erro no WebSocket para usuario {user_id}: {e}")
        manager.disconnect(websocket, user_id)

# ================================================
# TASK BACKGROUND PARA ATUALIZACOES AUTOMATICAS
# ================================================

@router.post("/start-updates", response_model=ResponseSucesso)
async def iniciar_atualizacoes_automaticas(
    background_tasks: BackgroundTasks,
    intervalo_segundos: int = Query(3, ge=1, le=60, description="Intervalo em segundos")
):
    """Inicia atualizacoes automaticas via WebSocket"""
    
    async def enviar_atualizacoes_periodicas():
        """Task que envia atualizacoes periodicas"""
        while True:
            try:
                service = get_monitoring_service()
                dashboard = service.obter_dashboard_resumo()
                
                await manager.broadcast({
                    "tipo": "dashboard_update",
                    "dados": dashboard.dict(),
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                await asyncio.sleep(intervalo_segundos)
                
            except Exception as e:
                logger.error(f"Erro em atualizacoes periodicas: {e}")
                await asyncio.sleep(10)  # Aguardar antes de tentar novamente
    
    background_tasks.add_task(enviar_atualizacoes_periodicas)
    
    return ResponseSucesso(
        mensagem=f"Atualizacoes automaticas iniciadas com intervalo de {intervalo_segundos}s"
    )

# ================================================
# ENDPOINTS DE SAUDE E STATUS
# ================================================

@router.get("/health")
async def health_check():
    """Verifica saude do sistema de monitoramento"""
    try:
        service = get_monitoring_service()
        
        # Testar conexao com banco
        campanhas = service.obter_metricas_campanhas(apenas_ativas=True)
        
        # Testar Redis
        redis_status = "connected" if service.redis_client else "disconnected"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "redis": redis_status,
            "campanhas_ativas": len(campanhas),
            "conexoes_websocket": len(manager.active_connections)
        }
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/cache/clear", response_model=ResponseSucesso)
async def limpar_cache(
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Forca limpeza do cache de monitoramento"""
    try:
        service._invalidate_cache("")  # Limpar todo o cache
        
        return ResponseSucesso(
            mensagem="Cache de monitoramento limpo com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 

@router.get("/active_calls", response_model=List[Dict[str, Any]])
def listar_chamadas_ativas(service: MonitoringService = Depends(get_monitoring_service)):
    """Retorna lista detalhada de chamadas ativas para o painel em tempo real"""
    try:
        return service.listar_chamadas_ativas()
    except Exception as e:
        logger.error(f"Erro ao listar chamadas ativas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar chamadas ativas")

@router.get("/call_history", response_model=List[Dict[str, Any]])
def listar_historico_chamadas(limit: int = 100, service: MonitoringService = Depends(get_monitoring_service)):
    """Retorna histórico das últimas chamadas realizadas"""
    try:
        return service.listar_historico_chamadas(limit=limit)
    except Exception as e:
        logger.error(f"Erro ao listar histórico de chamadas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar histórico de chamadas") 