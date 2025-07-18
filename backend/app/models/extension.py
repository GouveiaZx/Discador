from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Extension(Base):
    """
    Modelo para extensões de discagem
    """
    __tablename__ = "extensions"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False)
    campanha_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Configurações técnicas da extensão (JSON)
    configuracoes = Column(JSON, nullable=True)
    
    # Horário de funcionamento (JSON)
    horario_funcionamento = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    
    # Relacionamentos
    # campanha = relationship("Campaign", back_populates="extensions")
    stats = relationship("ExtensionStats", back_populates="extension", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Extension(numero='{self.numero}', nome='{self.nome}', ativo={self.ativo})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'nome': self.nome,
            'campanha_id': self.campanha_id,
            'ativo': self.ativo,
            'configuracoes': self.configuracoes,
            'horario_funcionamento': self.horario_funcionamento,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ExtensionStats(Base):
    """
    Modelo para estatísticas de extensões
    """
    __tablename__ = "extension_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    extension_id = Column(Integer, ForeignKey("extensions.id"), nullable=False)
    
    # Estatísticas de chamadas
    total_calls = Column(Integer, default=0, nullable=False)
    successful_calls = Column(Integer, default=0, nullable=False)
    failed_calls = Column(Integer, default=0, nullable=False)
    active_calls = Column(Integer, default=0, nullable=False)
    
    # Tempos de chamada (em segundos)
    total_talk_time = Column(Integer, default=0, nullable=False)
    avg_talk_time = Column(Integer, default=0, nullable=False)
    
    # Status de conexão
    online = Column(Boolean, default=False, nullable=False)
    last_activity = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 ou IPv6
    user_agent = Column(String(255), nullable=True)
    
    # Período das estatísticas
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    
    # Relacionamentos
    extension = relationship("Extension", back_populates="stats")
    
    def __repr__(self):
        return f"<ExtensionStats(extension_id={self.extension_id}, total_calls={self.total_calls}, online={self.online})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'extension_id': self.extension_id,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'active_calls': self.active_calls,
            'total_talk_time': self.total_talk_time,
            'avg_talk_time': self.avg_talk_time,
            'online': self.online,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ExtensionLog(Base):
    """
    Modelo para logs de atividades das extensões
    """
    __tablename__ = "extension_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    extension_id = Column(Integer, ForeignKey("extensions.id"), nullable=False)
    
    # Tipo de evento
    event_type = Column(String(50), nullable=False)  # 'call_start', 'call_end', 'register', 'unregister', etc.
    
    # Detalhes do evento
    description = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)  # Dados adicionais em JSON
    
    # Informações da chamada (se aplicável)
    call_id = Column(String(100), nullable=True)
    caller_number = Column(String(20), nullable=True)
    called_number = Column(String(20), nullable=True)
    duration = Column(Integer, nullable=True)  # Duração em segundos
    
    # Status do evento
    status = Column(String(20), nullable=True)  # 'success', 'failed', 'timeout', etc.
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    extension = relationship("Extension")
    
    def __repr__(self):
        return f"<ExtensionLog(extension_id={self.extension_id}, event_type='{self.event_type}', timestamp={self.timestamp})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'extension_id': self.extension_id,
            'event_type': self.event_type,
            'description': self.description,
            'details': self.details,
            'call_id': self.call_id,
            'caller_number': self.caller_number,
            'called_number': self.called_number,
            'duration': self.duration,
            'status': self.status,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class ExtensionConfig(Base):
    """
    Modelo para configurações avançadas de extensões
    """
    __tablename__ = "extension_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    extension_id = Column(Integer, ForeignKey("extensions.id"), nullable=False)
    
    # Configurações SIP
    sip_username = Column(String(50), nullable=True)
    sip_password = Column(String(100), nullable=True)
    sip_domain = Column(String(100), nullable=True)
    sip_proxy = Column(String(100), nullable=True)
    sip_port = Column(Integer, default=5060, nullable=True)
    
    # Configurações de codec
    preferred_codec = Column(String(20), default='ulaw', nullable=True)
    allowed_codecs = Column(String(200), default='ulaw,alaw,gsm', nullable=True)
    
    # Configurações de NAT
    nat_enabled = Column(Boolean, default=True, nullable=False)
    stun_server = Column(String(100), nullable=True)
    
    # Configurações de qualidade
    qualify_enabled = Column(Boolean, default=True, nullable=False)
    qualify_frequency = Column(Integer, default=60, nullable=True)  # segundos
    
    # Configurações de DTMF
    dtmf_mode = Column(String(20), default='rfc2833', nullable=True)
    
    # Configurações de chamada
    call_limit = Column(Integer, default=5, nullable=True)
    call_timeout = Column(Integer, default=30, nullable=True)  # segundos
    
    # Configurações de contexto
    context = Column(String(50), default='default', nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    
    # Relacionamentos
    extension = relationship("Extension")
    
    def __repr__(self):
        return f"<ExtensionConfig(extension_id={self.extension_id}, sip_username='{self.sip_username}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'extension_id': self.extension_id,
            'sip_username': self.sip_username,
            'sip_password': self.sip_password,
            'sip_domain': self.sip_domain,
            'sip_proxy': self.sip_proxy,
            'sip_port': self.sip_port,
            'preferred_codec': self.preferred_codec,
            'allowed_codecs': self.allowed_codecs,
            'nat_enabled': self.nat_enabled,
            'stun_server': self.stun_server,
            'qualify_enabled': self.qualify_enabled,
            'qualify_frequency': self.qualify_frequency,
            'dtmf_mode': self.dtmf_mode,
            'call_limit': self.call_limit,
            'call_timeout': self.call_timeout,
            'context': self.context,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }