#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schemas Pydantic para o Sistema de Monitoramento em Tempo Real
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum

# ================================================
# ENUMS
# ================================================

class StatusAgente(str, Enum):
    LIVRE = "livre"
    EM_CHAMADA = "em_chamada"
    AUSENTE = "ausente"
    PAUSADO = "pausado"
    OFFLINE = "offline"

class StatusChamada(str, Enum):
    PENDENTE = "pendente"
    MARCANDO = "marcando"
    TOCANDO = "tocando"
    ATENDIDA = "atendida"
    EM_ANDAMENTO = "em_andamento"
    TRANSFERIDA = "transferida"
    FINALIZADA = "finalizada"
    ERRO = "erro"
    ABANDONADA = "abandonada"

class TipoEventoMonitoramento(str, Enum):
    CHAMADA_INICIADA = "chamada_iniciada"
    CHAMADA_ATENDIDA = "chamada_atendida"
    CHAMADA_FINALIZADA = "chamada_finalizada"
    AGENTE_LOGIN = "agente_login"
    AGENTE_LOGOUT = "agente_logout"
    AGENTE_PAUSA = "agente_pausa"
    CAMPANHA_INICIADA = "campanha_iniciada"
    CAMPANHA_PAUSADA = "campanha_pausada"
    PROVEDOR_FALHA = "provedor_falha"
    PROVEDOR_RECUPERADO = "provedor_recuperado"

# ================================================
# SCHEMAS DE AGENTES
# ================================================

class AgenteBase(BaseModel):
    nome_agente: str = Field(..., max_length=100, description="Nome do agente")
    codigo_agente: str = Field(..., max_length=20, description="Codigo unico do agente")
    extensao_sip: Optional[str] = Field(None, max_length=50, description="Extensao SIP")
    email: Optional[str] = Field(None, max_length=100, description="Email do agente")
    max_chamadas_simultaneas: int = Field(1, ge=1, le=10, description="Max chamadas simultaneas")
    skills: Optional[Dict[str, Any]] = Field(None, description="Habilidades do agente")

class AgenteCreate(AgenteBase):
    pass

class AgenteUpdate(BaseModel):
    nome_agente: Optional[str] = Field(None, max_length=100)
    extensao_sip: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    max_chamadas_simultaneas: Optional[int] = Field(None, ge=1, le=10)
    skills: Optional[Dict[str, Any]] = None
    activo: Optional[bool] = None

class AgenteResponse(AgenteBase):
    id: int
    status_atual: StatusAgente
    ultima_atualizacao: datetime
    login_timestamp: Optional[datetime]
    chamada_atual_id: Optional[str]
    tempo_em_chamada: int
    total_chamadas_atendidas: int
    tempo_total_atendimento: int
    tempo_total_pausa: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class AgenteStatusUpdate(BaseModel):
    """Para atualizar status do agente"""
    status_atual: StatusAgente
    chamada_atual_id: Optional[str] = None

# ================================================
# SCHEMAS DE CHAMADAS
# ================================================

class ChamadaBase(BaseModel):
    numero_origem: Optional[str] = Field(None, max_length=20)
    numero_destino: str = Field(..., max_length=20, description="Numero de destino")
    campanha_id: Optional[int] = Field(None, description="ID da campanha")
    provedor_sip_id: Optional[int] = Field(None, description="ID do provedor SIP")
    provedor_nome: Optional[str] = Field(None, max_length=100)

class ChamadaCreate(ChamadaBase):
    call_id_asterisk: Optional[str] = Field(None, max_length=100)

class ChamadaUpdate(BaseModel):
    status_atual: Optional[StatusChamada] = None
    timestamp_atendida: Optional[datetime] = None
    timestamp_finalizada: Optional[datetime] = None
    duracao_total: Optional[int] = None
    tempo_espera: Optional[int] = None
    agente_id: Optional[int] = None
    resultado_chamada: Optional[str] = Field(None, max_length=50)
    dtmf_recebido: Optional[str] = Field(None, max_length=10)
    transferida_para: Optional[str] = Field(None, max_length=50)
    canal_asterisk: Optional[str] = Field(None, max_length=100)
    codec_utilizado: Optional[str] = Field(None, max_length=20)
    qualidade_audio: Optional[float] = Field(None, ge=0.0, le=5.0)
    dados_extras: Optional[Dict[str, Any]] = None

class ChamadaResponse(ChamadaBase):
    id: int
    uuid_chamada: str
    call_id_asterisk: Optional[str]
    status_atual: StatusChamada
    timestamp_inicio: datetime
    timestamp_atendida: Optional[datetime]
    timestamp_finalizada: Optional[datetime]
    duracao_total: Optional[int]
    tempo_espera: Optional[int]
    agente_id: Optional[int]
    resultado_chamada: Optional[str]
    dtmf_recebido: Optional[str]
    transferida_para: Optional[str]
    canal_asterisk: Optional[str]
    codec_utilizado: Optional[str]
    qualidade_audio: Optional[float]
    dados_extras: Optional[Dict[str, Any]]
    fecha_creacion: datetime

    # Dados calculados
    duracao_atual: Optional[int] = Field(None, description="Duracao atual em segundos")
    tempo_desde_inicio: Optional[int] = Field(None, description="Tempo desde inicio em segundos")

    class Config:
        from_attributes = True

# ================================================
# SCHEMAS DE EVENTOS
# ================================================

class EventoSistemaBase(BaseModel):
    tipo_evento: TipoEventoMonitoramento
    titulo: str = Field(..., max_length=200, description="Titulo do evento")
    descricao: Optional[str] = Field(None, description="Descricao detalhada")
    dados_evento: Optional[Dict[str, Any]] = Field(None, description="Dados extras do evento")
    campanha_id: Optional[int] = None
    agente_id: Optional[int] = None
    chamada_id: Optional[str] = Field(None, max_length=100)
    nivel_severidade: str = Field("info", pattern="^(info|warning|error|critical)$")

class EventoSistemaCreate(EventoSistemaBase):
    pass

class EventoSistemaResponse(EventoSistemaBase):
    id: int
    uuid_evento: str
    resolvido: bool
    timestamp_evento: datetime
    visualizado_por: Optional[List[int]]

    class Config:
        from_attributes = True

# ================================================
# SCHEMAS DE DASHBOARDS
# ================================================

class MetricaCampanha(BaseModel):
    """Metricas de uma campanha especifica"""
    campanha_id: int
    nome_campanha: str
    status_campanha: str
    
    # Contadores
    total_contatos: int = 0
    chamadas_realizadas: int = 0
    chamadas_ativas: int = 0
    chamadas_finalizadas: int = 0
    
    # Por status
    chamadas_atendidas: int = 0
    chamadas_abandonadas: int = 0
    chamadas_erro: int = 0
    
    # Taxas (percentuais)
    taxa_atendimento: float = 0.0
    taxa_abandono: float = 0.0
    taxa_sucesso: float = 0.0
    
    # Tempos (segundos)
    tempo_medio_atendimento: Optional[float] = None
    tempo_medio_chamada: Optional[float] = None
    
    # Provedores utilizados
    provedores_utilizados: List[str] = []

class MetricaProvedor(BaseModel):
    """Metricas de um provedor SIP"""
    provedor_id: int
    nome_provedor: str
    status_conexao: str
    
    # Contadores
    chamadas_ativas: int = 0
    chamadas_hoje: int = 0
    total_falhas: int = 0
    
    # Performance
    latencia_media: Optional[float] = None  # ms
    taxa_sucesso: float = 0.0  # %
    uptime_percentual: float = 0.0  # %
    
    # Ultima verificacao
    ultima_verificacao: Optional[datetime] = None
    tempo_resposta: Optional[int] = None  # ms

class MetricaAgente(BaseModel):
    """Metricas de um agente"""
    agente_id: int
    nome_agente: str
    codigo_agente: str
    status_atual: StatusAgente
    
    # Status da sessao
    online_desde: Optional[datetime] = None
    chamada_atual: Optional[str] = None
    
    # Estatisticas do dia
    chamadas_atendidas: int = 0
    tempo_em_chamadas: int = 0  # segundos
    tempo_em_pausa: int = 0  # segundos
    
    # Performance
    tempo_medio_atendimento: Optional[float] = None
    taxa_atendimento: float = 0.0

class DashboardResumo(BaseModel):
    """Dashboard resumido para supervisores"""
    
    # Timestamp da consulta
    timestamp_consulta: datetime
    
    # Metricas gerais
    total_campanhas_ativas: int = 0
    total_chamadas_ativas: int = 0
    total_agentes_online: int = 0
    total_provedores_ativos: int = 0
    
    # Chamadas
    chamadas_por_status: Dict[str, int] = {}
    chamadas_ultima_hora: int = 0
    taxa_atendimento_geral: float = 0.0
    
    # Agentes
    agentes_por_status: Dict[str, int] = {}
    
    # Provedores
    status_provedores: List[MetricaProvedor] = []
    
    # Alertas recentes
    alertas_criticos: int = 0
    alertas_warning: int = 0

class DashboardDetalhado(DashboardResumo):
    """Dashboard detalhado com todas as metricas"""
    
    # Campanhas detalhadas
    campanhas: List[MetricaCampanha] = []
    
    # Agentes detalhados
    agentes: List[MetricaAgente] = []
    
    # Chamadas ativas detalhadas
    chamadas_ativas: List[ChamadaResponse] = []
    
    # Eventos recentes
    eventos_recentes: List[EventoSistemaResponse] = []
    
    # Performance do sistema
    performance_sistema: Dict[str, Any] = {}

# ================================================
# SCHEMAS DE FILTROS E CONSULTAS
# ================================================

class FiltroMonitoramento(BaseModel):
    """Filtros para consultas de monitoramento"""
    
    # Filtros temporais
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    ultimas_horas: Optional[int] = Field(None, ge=1, le=168)  # Maximo 1 semana
    
    # Filtros por entidade
    campanha_ids: Optional[List[int]] = None
    agente_ids: Optional[List[int]] = None
    provedor_ids: Optional[List[int]] = None
    
    # Filtros por status
    status_chamadas: Optional[List[StatusChamada]] = None
    status_agentes: Optional[List[StatusAgente]] = None
    
    # Filtros de severidade
    niveis_severidade: Optional[List[str]] = None
    apenas_alertas: bool = False
    
    # Paginacao
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=500)

class ExportRequest(BaseModel):
    """Request para exportacao de dados"""
    
    # Tipo de exportacao
    tipo_export: str = Field(..., pattern="^(csv|xlsx|json)$")
    
    # Dados a exportar
    incluir_chamadas: bool = True
    incluir_agentes: bool = True
    incluir_eventos: bool = False
    
    # Filtros
    filtros: Optional[FiltroMonitoramento] = None
    
    # Configuracoes
    incluir_cabecalhos: bool = True
    formato_data: str = Field("iso", pattern="^(iso|br|us)$")

class WebSocketMessage(BaseModel):
    """Mensagem para WebSocket"""
    
    # Tipo da mensagem
    tipo: str = Field(..., description="Tipo da mensagem")
    
    # Dados
    dados: Dict[str, Any] = Field(..., description="Dados da mensagem")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadados
    session_id: Optional[str] = None
    usuario_id: Optional[int] = None

# ================================================
# SCHEMAS DE RESPOSTA
# ================================================

class ResponsePaginado(BaseModel):
    """Response paginado generico"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

class ResponseSucesso(BaseModel):
    """Response de sucesso generico"""
    sucesso: bool = True
    mensagem: str
    dados: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ResponseErro(BaseModel):
    """Response de erro generico"""
    sucesso: bool = False
    erro: str
    detalhes: Optional[str] = None
    codigo_erro: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 
