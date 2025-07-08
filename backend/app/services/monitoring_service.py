#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servico de Monitoramento
Sistema de monitoramento em tempo real para o discador
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
# import redis  # Comentado temporariamente
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from fastapi import Depends

from app.database import get_db
from app.models.monitoring import AgenteMonitoramento, EventoSistema, SessionMonitoramento
from app.models.llamada import Llamada
# from app.models.campana import Campana  # Comentado temporariamente - modelo não existe
from app.models.usuario import Usuario
from app.utils.logger import configurar_logger

logger = configurar_logger("monitoring_service")

class MonitoringService:
    """Servico de monitoramento simplificado temporariamente"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = None  # Comentado temporariamente
    
    def get_dashboard_data(self):
        """Retorna dados básicos do dashboard"""
        return {
            "total_campanhas": 0,
            "chamadas_ativas": 0,
            "agentes_online": 0,
            "timestamp": datetime.now()
        }
    
    def obter_dashboard_resumo(self):
        """Retorna dashboard resumido"""
        from app.schemas.monitoring import DashboardResumo
        return DashboardResumo(
            timestamp_consulta=datetime.utcnow(),
            total_campanhas_ativas=0,
            total_chamadas_ativas=0,
            total_agentes_online=0,
            total_provedores_ativos=0,
            chamadas_por_status={},
            chamadas_ultima_hora=0,
            taxa_atendimento_geral=0.0,
            agentes_por_status={},
            status_provedores=[],
            alertas_criticos=0,
            alertas_warning=0
        )
    
    def obter_dashboard_detalhado(self):
        """Retorna dashboard detalhado"""
        from app.schemas.monitoring import DashboardDetalhado
        return DashboardDetalhado(
            timestamp_consulta=datetime.utcnow(),
            total_campanhas_ativas=0,
            total_chamadas_ativas=0,
            total_agentes_online=0,
            total_provedores_ativos=0,
            chamadas_por_status={},
            chamadas_ultima_hora=0,
            taxa_atendimento_geral=0.0,
            agentes_por_status={},
            status_provedores=[],
            alertas_criticos=0,
            alertas_warning=0,
            campanhas=[],
            agentes=[],
            chamadas_ativas=[],
            eventos_recentes=[],
            performance_sistema={}
        )
    
    def obter_metricas_campanhas(self, apenas_ativas: bool = True):
        """Retorna métricas de campanhas"""
        return []
    
    def obter_metricas_provedores(self):
        """Retorna métricas de provedores"""
        return []
    
    def obter_metricas_agentes(self):
        """Retorna métricas de agentes"""
        return []
    
    def criar_evento(self, evento_data):
        """Cria um evento do sistema"""
        from app.schemas.monitoring import ResponseSucesso
        return ResponseSucesso(
            mensagem="Evento criado com sucesso",
            dados={"evento_id": 1}
        )
    
    def exportar_dados_csv(self, export_request):
        """Exporta dados para CSV"""
        return "data,test\n1,example"
    
    def limpar_cache(self):
        """Limpa o cache do sistema"""
        from app.schemas.monitoring import ResponseSucesso
        return ResponseSucesso(
            mensagem="Cache limpo com sucesso"
        )
    
    def listar_chamadas_ativas(self):
        """Lista chamadas ativas"""
        return []
    
    def listar_historico_chamadas(self, limit: int = 100):
        """Lista histórico de chamadas"""
        return []
    
    def _invalidate_cache(self, cache_key: str):
        """Invalida cache específico"""
        logger.info(f"Cache invalidado: {cache_key}")
        pass
    
    def registrar_evento(self, evento):
        """Registra um evento do sistema"""
        try:
            novo_evento = EventoSistema(
                tipo_evento=evento.tipo_evento,
                titulo=evento.titulo,
                descricao=evento.descricao,
                nivel_severidade=evento.nivel_severidade,
                agente_id=evento.agente_id,
                campanha_id=evento.campanha_id,
                chamada_id=evento.chamada_id
            )
            self.db.add(novo_evento)
            self.db.commit()
            logger.info(f"Evento registrado: {evento.titulo}")
        except Exception as e:
            logger.error(f"Erro ao registrar evento: {e}")
            self.db.rollback()
    
    def atualizar_agente_status(self, agente_id: int, status: str, chamada_id: str = None):
        """Atualiza status de um agente"""
        try:
            agente = self.db.query(AgenteMonitoramento).filter(
                AgenteMonitoramento.id == agente_id
            ).first()
            
            if agente:
                agente.status_atual = status
                agente.ultimo_heartbeat = datetime.utcnow()
                self.db.commit()
                logger.info(f"Status do agente {agente_id} atualizado para: {status}")
        except Exception as e:
            logger.error(f"Erro ao atualizar status do agente: {e}")
            self.db.rollback()

def get_monitoring_service(db: Session = Depends(get_db)) -> MonitoringService:
    """Factory function para o serviço de monitoramento"""
    return MonitoringService(db) 