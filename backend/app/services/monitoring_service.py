#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servico de Monitoramento em Tempo Real
Coleta e processa metricas do sistema de discagem preditiva
"""

import json
import asyncio
import redis
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from fastapi import HTTPException
import logging

from app.database import get_db
from app.models.monitoring import (
    AgenteMonitoramento, ChamadaMonitoramento, EventoSistema, 
    SessionMonitoramento, CacheMetricas, StatusAgente, StatusChamada
)
from app.models.multi_sip import ProvedorSip, LogSelecaoProvedor
from app.schemas.monitoring import (
    DashboardResumo, DashboardDetalhado, MetricaCampanha,
    MetricaProvedor, MetricaAgente, EventoSistemaCreate,
    ChamadaResponse, AgenteResponse, FiltroMonitoramento
)

logger = logging.getLogger(__name__)

class MonitoringService:
    """Servico principal de monitoramento"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = None
        self._init_redis()
        
        # Cache interno para performance
        self._cache_local = {}
        self._cache_timestamp = {}
        self._cache_ttl = 10  # 10 segundos para cache local
        
        # Configuracoes
        self.redis_ttl = 60  # 1 minuto para cache Redis
        self.metrics_ttl = 300  # 5 minutos para metricas calculadas
    
    def _init_redis(self):
        """Inicializa conexao Redis"""
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Teste de conexao
            self.redis_client.ping()
            logger.info("Conexao Redis estabelecida com sucesso")
        except Exception as e:
            logger.warning(f"Falha ao conectar no Redis: {e}")
            self.redis_client = None
    
    def _get_cache_key(self, prefix: str, *args) -> str:
        """Gera chave de cache"""
        return f"monitoring:{prefix}:" + ":".join(str(arg) for arg in args)
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Busca no cache (Redis primeiro, depois local)"""
        try:
            # Cache local primeiro
            if key in self._cache_local:
                timestamp = self._cache_timestamp.get(key, 0)
                if datetime.now().timestamp() - timestamp < self._cache_ttl:
                    return self._cache_local[key]
                else:
                    del self._cache_local[key]
                    del self._cache_timestamp[key]
            
            # Cache Redis
            if self.redis_client:
                cached = self.redis_client.get(key)
                if cached:
                    data = json.loads(cached)
                    # Armazenar no cache local
                    self._cache_local[key] = data
                    self._cache_timestamp[key] = datetime.now().timestamp()
                    return data
                    
        except Exception as e:
            logger.error(f"Erro ao buscar cache {key}: {e}")
        
        return None
    
    def _set_cache(self, key: str, data: Any, ttl: int = None) -> None:
        """Armazena no cache"""
        try:
            # Cache local
            self._cache_local[key] = data
            self._cache_timestamp[key] = datetime.now().timestamp()
            
            # Cache Redis
            if self.redis_client:
                ttl = ttl or self.redis_ttl
                self.redis_client.setex(
                    key, 
                    ttl, 
                    json.dumps(data, default=str)
                )
                
        except Exception as e:
            logger.error(f"Erro ao armazenar cache {key}: {e}")
    
    def _invalidate_cache(self, pattern: str) -> None:
        """Invalida cache por padrao"""
        try:
            # Cache local
            keys_to_remove = [k for k in self._cache_local.keys() if pattern in k]
            for key in keys_to_remove:
                if key in self._cache_local:
                    del self._cache_local[key]
                if key in self._cache_timestamp:
                    del self._cache_timestamp[key]
            
            # Cache Redis
            if self.redis_client:
                keys = self.redis_client.keys(f"*{pattern}*")
                if keys:
                    self.redis_client.delete(*keys)
                    
        except Exception as e:
            logger.error(f"Erro ao invalidar cache {pattern}: {e}")

    # ================================================
    # METRICAS DE CAMPANHAS
    # ================================================
    
    def obter_metricas_campanhas(self, apenas_ativas: bool = True) -> List[MetricaCampanha]:
        """Obtem metricas de todas as campanhas"""
        cache_key = self._get_cache_key("campanhas", apenas_ativas)
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return [MetricaCampanha(**item) for item in cached]
        
        try:
            # Buscar campanhas (usando tabela existente)
            from app.models.presione1 import CampanaPresione1, LlamadaPresione1
            
            query = self.db.query(CampanaPresione1)
            if apenas_ativas:
                query = query.filter(CampanaPresione1.activa == True)
            
            campanhas = query.all()
            metricas = []
            
            for campanha in campanhas:
                # Calcular metricas
                total_llamadas = self.db.query(LlamadaPresione1).filter(
                    LlamadaPresione1.campana_id == campanha.id
                ).count()
                
                llamadas_atendidas = self.db.query(LlamadaPresione1).filter(
                    LlamadaPresione1.campana_id == campanha.id,
                    LlamadaPresione1.fecha_contestada.isnot(None)
                ).count()
                
                llamadas_ativas = self.db.query(LlamadaPresione1).filter(
                    LlamadaPresione1.campana_id == campanha.id,
                    LlamadaPresione1.estado.in_(['marcando', 'contestada', 'audio_reproducido', 'esperando_dtmf'])
                ).count()
                
                llamadas_erro = self.db.query(LlamadaPresione1).filter(
                    LlamadaPresione1.campana_id == campanha.id,
                    LlamadaPresione1.estado == 'error'
                ).count()
                
                # Calcular taxas
                taxa_atendimento = (llamadas_atendidas / total_llamadas * 100) if total_llamadas > 0 else 0
                taxa_sucesso = 0  # TODO: Implementar baseado em presiono_1
                
                # Tempo medio
                tempo_medio = self.db.query(func.avg(LlamadaPresione1.duracion_total)).filter(
                    LlamadaPresione1.campana_id == campanha.id,
                    LlamadaPresione1.duracion_total.isnot(None)
                ).scalar()
                
                # Provedores utilizados
                provedores = self.db.query(LogSelecaoProvedor.provedor_nome).filter(
                    LogSelecaoProvedor.campanha_id == campanha.id
                ).distinct().all()
                
                metrica = MetricaCampanha(
                    campanha_id=campanha.id,
                    nome_campanha=campanha.nombre,
                    status_campanha="ativa" if campanha.activa else "parada",
                    total_contatos=0,  # TODO: Obter da lista de numeros
                    chamadas_realizadas=total_llamadas,
                    chamadas_ativas=llamadas_ativas,
                    chamadas_finalizadas=total_llamadas - llamadas_ativas,
                    chamadas_atendidas=llamadas_atendidas,
                    chamadas_abandonadas=0,  # TODO: Implementar
                    chamadas_erro=llamadas_erro,
                    taxa_atendimento=round(taxa_atendimento, 2),
                    taxa_abandono=0.0,
                    taxa_sucesso=round(taxa_sucesso, 2),
                    tempo_medio_atendimento=tempo_medio,
                    tempo_medio_chamada=tempo_medio,
                    provedores_utilizados=[p[0] for p in provedores if p[0]]
                )
                
                metricas.append(metrica)
            
            # Cache do resultado
            self._set_cache(cache_key, [m.dict() for m in metricas], ttl=30)
            
            return metricas
            
        except Exception as e:
            logger.error(f"Erro ao obter metricas de campanhas: {e}")
            return []
    
    # ================================================
    # METRICAS DE PROVEDORES SIP
    # ================================================
    
    def obter_metricas_provedores(self) -> List[MetricaProvedor]:
        """Obtem metricas de todos os provedores SIP"""
        cache_key = self._get_cache_key("provedores")
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return [MetricaProvedor(**item) for item in cached]
        
        try:
            provedores = self.db.query(ProvedorSip).filter(
                ProvedorSip.ativo == True
            ).all()
            
            metricas = []
            hoje = datetime.now().date()
            
            for provedor in provedores:
                # Chamadas de hoje
                chamadas_hoje = self.db.query(LogSelecaoProvedor).filter(
                    LogSelecaoProvedor.provedor_id == provedor.id,
                    func.date(LogSelecaoProvedor.timestamp_selecao) == hoje
                ).count()
                
                # Falhas de hoje
                falhas_hoje = self.db.query(LogSelecaoProvedor).filter(
                    LogSelecaoProvedor.provedor_id == provedor.id,
                    LogSelecaoProvedor.sucesso == False,
                    func.date(LogSelecaoProvedor.timestamp_selecao) == hoje
                ).count()
                
                # Taxa de sucesso
                taxa_sucesso = ((chamadas_hoje - falhas_hoje) / chamadas_hoje * 100) if chamadas_hoje > 0 else 100
                
                # Latencia media
                latencia_media = self.db.query(func.avg(LogSelecaoProvedor.latencia_ms)).filter(
                    LogSelecaoProvedor.provedor_id == provedor.id,
                    func.date(LogSelecaoProvedor.timestamp_selecao) == hoje,
                    LogSelecaoProvedor.latencia_ms.isnot(None)
                ).scalar()
                
                metrica = MetricaProvedor(
                    provedor_id=provedor.id,
                    nome_provedor=provedor.nome,
                    status_conexao=provedor.status_conexao,
                    chamadas_ativas=0,  # TODO: Implementar consulta real-time
                    chamadas_hoje=chamadas_hoje,
                    total_falhas=falhas_hoje,
                    latencia_media=latencia_media,
                    taxa_sucesso=round(taxa_sucesso, 2),
                    uptime_percentual=95.0,  # TODO: Calcular real
                    ultima_verificacao=provedor.ultima_verificacao,
                    tempo_resposta=int(latencia_media) if latencia_media else None
                )
                
                metricas.append(metrica)
            
            # Cache do resultado
            self._set_cache(cache_key, [m.dict() for m in metricas], ttl=60)
            
            return metricas
            
        except Exception as e:
            logger.error(f"Erro ao obter metricas de provedores: {e}")
            return []
    
    # ================================================
    # METRICAS DE AGENTES
    # ================================================
    
    def obter_metricas_agentes(self) -> List[MetricaAgente]:
        """Obtem metricas de todos os agentes"""
        cache_key = self._get_cache_key("agentes")
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return [MetricaAgente(**item) for item in cached]
        
        try:
            agentes = self.db.query(AgenteMonitoramento).filter(
                AgenteMonitoramento.activo == True
            ).all()
            
            metricas = []
            
            for agente in agentes:
                # Calcular tempo medio de atendimento
                tempo_medio = None
                if agente.total_chamadas_atendidas > 0:
                    tempo_medio = agente.tempo_total_atendimento / agente.total_chamadas_atendidas
                
                # Taxa de atendimento (percentual do tempo online em chamada)
                taxa_atendimento = 0.0
                if agente.login_timestamp:
                    tempo_online = (datetime.utcnow() - agente.login_timestamp).total_seconds()
                    if tempo_online > 0:
                        taxa_atendimento = (agente.tempo_total_atendimento / tempo_online) * 100
                
                metrica = MetricaAgente(
                    agente_id=agente.id,
                    nome_agente=agente.nome_agente,
                    codigo_agente=agente.codigo_agente,
                    status_atual=StatusAgente(agente.status_atual),
                    online_desde=agente.login_timestamp,
                    chamada_atual=agente.chamada_atual_id,
                    chamadas_atendidas=agente.total_chamadas_atendidas,
                    tempo_em_chamadas=agente.tempo_total_atendimento,
                    tempo_em_pausa=agente.tempo_total_pausa,
                    tempo_medio_atendimento=tempo_medio,
                    taxa_atendimento=round(taxa_atendimento, 2)
                )
                
                metricas.append(metrica)
            
            # Cache do resultado
            self._set_cache(cache_key, [m.dict() for m in metricas], ttl=30)
            
            return metricas
            
        except Exception as e:
            logger.error(f"Erro ao obter metricas de agentes: {e}")
            return []
    
    # ================================================
    # DASHBOARD CONSOLIDADO
    # ================================================
    
    def obter_dashboard_resumo(self) -> DashboardResumo:
        """Obtem dashboard resumido para supervisores"""
        cache_key = self._get_cache_key("dashboard_resumo")
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return DashboardResumo(**cached)
        
        try:
            # Metricas basicas
            campanhas = self.obter_metricas_campanhas(apenas_ativas=True)
            provedores = self.obter_metricas_provedores()
            agentes = self.obter_metricas_agentes()
            
            # Consolidar dados
            total_campanhas_ativas = len(campanhas)
            total_chamadas_ativas = sum(c.chamadas_ativas for c in campanhas)
            total_agentes_online = len([a for a in agentes if a.status_atual != StatusAgente.OFFLINE])
            total_provedores_ativos = len([p for p in provedores if p.status_conexao == "conectado"])
            
            # Chamadas por status
            chamadas_por_status = {}
            for campanha in campanhas:
                # TODO: Implementar contagem detalhada por status
                pass
            
            # Agentes por status
            agentes_por_status = {}
            for status in StatusAgente:
                agentes_por_status[status.value] = len([a for a in agentes if a.status_atual == status])
            
            # Taxa de atendimento geral
            total_realizadas = sum(c.chamadas_realizadas for c in campanhas)
            total_atendidas = sum(c.chamadas_atendidas for c in campanhas)
            taxa_atendimento_geral = (total_atendidas / total_realizadas * 100) if total_realizadas > 0 else 0
            
            # Alertas recentes
            uma_hora_atras = datetime.utcnow() - timedelta(hours=1)
            alertas_criticos = self.db.query(EventoSistema).filter(
                EventoSistema.nivel_severidade == "critical",
                EventoSistema.timestamp_evento >= uma_hora_atras,
                EventoSistema.resolvido == False
            ).count()
            
            alertas_warning = self.db.query(EventoSistema).filter(
                EventoSistema.nivel_severidade == "warning",
                EventoSistema.timestamp_evento >= uma_hora_atras,
                EventoSistema.resolvido == False
            ).count()
            
            dashboard = DashboardResumo(
                timestamp_consulta=datetime.utcnow(),
                total_campanhas_ativas=total_campanhas_ativas,
                total_chamadas_ativas=total_chamadas_ativas,
                total_agentes_online=total_agentes_online,
                total_provedores_ativos=total_provedores_ativos,
                chamadas_por_status=chamadas_por_status,
                chamadas_ultima_hora=0,  # TODO: Implementar
                taxa_atendimento_geral=round(taxa_atendimento_geral, 2),
                agentes_por_status=agentes_por_status,
                status_provedores=provedores,
                alertas_criticos=alertas_criticos,
                alertas_warning=alertas_warning
            )
            
            # Cache do resultado
            self._set_cache(cache_key, dashboard.dict(), ttl=20)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Erro ao obter dashboard resumo: {e}")
            # Retornar dashboard vazio em caso de erro
            return DashboardResumo(
                timestamp_consulta=datetime.utcnow(),
                total_campanhas_ativas=0,
                total_chamadas_ativas=0,
                total_agentes_online=0,
                total_provedores_ativos=0
            )
    
    def obter_dashboard_detalhado(self) -> DashboardDetalhado:
        """Obtem dashboard detalhado com todas as metricas"""
        try:
            dashboard_resumo = self.obter_dashboard_resumo()
            
            # Dados detalhados
            campanhas = self.obter_metricas_campanhas(apenas_ativas=True)
            agentes = self.obter_metricas_agentes()
            
            # Chamadas ativas (simulacao)
            chamadas_ativas = []  # TODO: Implementar consulta real
            
            # Eventos recentes
            eventos_recentes = []  # TODO: Implementar consulta
            
            # Performance do sistema
            performance_sistema = {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 23.4,
                "network_latency": 12.5
            }
            
            dashboard = DashboardDetalhado(
                **dashboard_resumo.dict(),
                campanhas=campanhas,
                agentes=agentes,
                chamadas_ativas=chamadas_ativas,
                eventos_recentes=eventos_recentes,
                performance_sistema=performance_sistema
            )
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Erro ao obter dashboard detalhado: {e}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")
    
    # ================================================
    # EVENTOS E LOGS
    # ================================================
    
    def registrar_evento(self, evento: EventoSistemaCreate) -> None:
        """Registra um evento no sistema"""
        try:
            novo_evento = EventoSistema(**evento.dict())
            self.db.add(novo_evento)
            self.db.commit()
            
            # Invalidar cache de eventos
            self._invalidate_cache("eventos")
            
            logger.info(f"Evento registrado: {evento.titulo}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar evento: {e}")
            self.db.rollback()
    
    def atualizar_agente_status(self, agente_id: int, status: StatusAgente, chamada_id: str = None) -> None:
        """Atualiza status de um agente"""
        try:
            agente = self.db.query(AgenteMonitoramento).filter(
                AgenteMonitoramento.id == agente_id
            ).first()
            
            if agente:
                agente.status_atual = status
                agente.ultima_atualizacao = datetime.utcnow()
                
                if chamada_id:
                    agente.chamada_atual_id = chamada_id
                
                self.db.commit()
                
                # Invalidar cache de agentes
                self._invalidate_cache("agentes")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar status do agente {agente_id}: {e}")
            self.db.rollback()
    
    # ================================================
    # LIMPEZA E MANUTENCAO
    # ================================================
    
    def limpar_cache_expirado(self) -> None:
        """Remove entradas expiradas do cache"""
        try:
            now = datetime.now().timestamp()
            
            # Cache local
            keys_to_remove = [
                k for k, timestamp in self._cache_timestamp.items()
                if now - timestamp > self._cache_ttl
            ]
            
            for key in keys_to_remove:
                if key in self._cache_local:
                    del self._cache_local[key]
                if key in self._cache_timestamp:
                    del self._cache_timestamp[key]
            
            logger.debug(f"Removidas {len(keys_to_remove)} entradas do cache local")
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache expirado: {e}")

# ================================================
# FACTORY FUNCTION
# ================================================

def get_monitoring_service(db: Session = None) -> MonitoringService:
    """Factory function para criar instancia do servico"""
    if not db:
        db = next(get_db())
    return MonitoringService(db) 