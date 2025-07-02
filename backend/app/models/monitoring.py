from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class AgenteMonitoramento(Base):
    __tablename__ = "agente_monitoramento"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    
    # Status do agente
    status_atual = Column(String(50), default="disponivel", nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Configurações
    max_chamadas_simultaneas = Column(Integer, default=1, nullable=False)
    chamadas_atuais = Column(Integer, default=0, nullable=False)
    
    # Contato e informações
    email = Column(String(150), nullable=True)
    telefone = Column(String(20), nullable=True)
    departamento = Column(String(100), nullable=True)
    
    # Timestamps
    ultimo_login = Column(DateTime, nullable=True)
    ultimo_heartbeat = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sessions = relationship("SessionMonitoramento", back_populates="agente", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AgenteMonitoramento(id={self.id}, nome={self.nome}, status={self.status_atual})>"

class EventoSistema(Base):
    __tablename__ = "evento_sistema"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid_evento = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Tipo e categoria do evento
    tipo_evento = Column(String(50), nullable=False)
    categoria = Column(String(50), nullable=False)
    severidade = Column(String(20), default="info", nullable=False)  # info, warning, error, critical
    
    # Descrição do evento
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Contexto
    componente = Column(String(100), nullable=True)
    agente_id = Column(Integer, ForeignKey("agente_monitoramento.id"), nullable=True)
    chamada_id = Column(String(100), nullable=True)
    campanha_id = Column(Integer, nullable=True)
    
    # Dados técnicos
    dados_extras = Column(Text, nullable=True)  # JSON string
    stack_trace = Column(Text, nullable=True)
    
    # Status
    resolvido = Column(Boolean, default=False, nullable=False)
    timestamp_evento = Column(DateTime, default=func.now(), nullable=False)
    timestamp_resolucao = Column(DateTime, nullable=True)
    
    # Relationships
    agente = relationship("AgenteMonitoramento")
    
    def __repr__(self):
        return f"<EventoSistema(id={self.id}, tipo={self.tipo_evento}, severidade={self.severidade})>"

class SessionMonitoramento(Base):
    __tablename__ = "session_monitoramento"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid_session = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Agente relacionado
    agente_id = Column(Integer, ForeignKey("agente_monitoramento.id"), nullable=False)
    
    # Dados da sessão
    ip_origem = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    tipo_acesso = Column(String(50), default="web", nullable=False)
    
    # Status da sessão
    status_session = Column(String(50), default="ativa", nullable=False)
    ultima_atividade = Column(DateTime, default=func.now(), nullable=False)
    
    # Métricas da sessão
    total_chamadas = Column(Integer, default=0, nullable=False)
    total_eventos = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    timestamp_inicio = Column(DateTime, default=func.now(), nullable=False)
    timestamp_fim = Column(DateTime, nullable=True)
    
    # Dados extras
    configuracoes_session = Column(Text, nullable=True)
    
    # Relationships
    agente = relationship("AgenteMonitoramento", back_populates="sessions")
    
    def __repr__(self):
        return f"<SessionMonitoramento(id={self.id}, agente_id={self.agente_id}, status={self.status_session})>" 