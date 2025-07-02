from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, func, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base

# Enums para o sistema de áudio
class EstadoAudio(enum.Enum):
    INICIANDO = "iniciando"
    TOCANDO = "tocando"
    AGUARDANDO_DTMF = "aguardando_dtmf"
    DETECTANDO_VOICEMAIL = "detectando_voicemail"
    REPRODUZINDO_VOICEMAIL = "reproduzindo_voicemail"
    AGUARDANDO_HUMANO = "aguardando_humano"
    CONECTADO = "conectado"
    TRANSFERINDO = "transferindo"
    ERRO = "erro"
    FINALIZADO = "finalizado"

class TipoOperadorRegra(enum.Enum):
    IGUAL = "igual"
    DIFERENTE = "diferente"
    MAIOR_QUE = "maior_que"
    MENOR_QUE = "menor_que"
    CONTEM = "contem"
    NAO_CONTEM = "nao_contem"
    ENTRE = "entre"
    REGEX = "regex"

# Modelos do sistema de áudio inteligente
class TipoEvento(Base):
    __tablename__ = "tipos_evento_audio"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True)
    codigo = Column(String(20), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    
    # Configurações do evento
    permite_audio = Column(Boolean, default=True, nullable=False)
    audio_obrigatorio = Column(Boolean, default=False, nullable=False)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=func.now())
    
    # Relationships
    eventos = relationship("AudioEvento", back_populates="tipo_evento")
    
    def __repr__(self):
        return f"<TipoEvento(id={self.id}, nome={self.nome}, codigo={self.codigo})>"

class AudioContexto(Base):
    __tablename__ = "audio_contextos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Configurações do contexto
    configuracoes = Column(JSON, default={})
    variaveis_contexto = Column(JSON, default={})
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sessoes = relationship("AudioSessao", back_populates="contexto")
    regras = relationship("AudioRegra", back_populates="contexto")
    
    def __repr__(self):
        return f"<AudioContexto(id={self.id}, nome={self.nome})>"

class AudioTemplate(Base):
    __tablename__ = "audio_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Configurações do template
    template_config = Column(JSON, default={})
    variaveis_template = Column(JSON, default={})
    
    # Arquivo de áudio associado
    arquivo_path = Column(String(255), nullable=True)
    formato = Column(String(10), default="wav")
    duracao_segundos = Column(Integer, nullable=True)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    regras = relationship("AudioRegra", back_populates="template")
    
    def __repr__(self):
        return f"<AudioTemplate(id={self.id}, nome={self.nome})>"

class AudioRegra(Base):
    __tablename__ = "audio_regras"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Associações
    contexto_id = Column(Integer, ForeignKey("audio_contextos.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("audio_templates.id"), nullable=True)
    
    # Configurações da regra
    condicoes = Column(JSON, default=[])  # Lista de condições
    acoes = Column(JSON, default=[])  # Lista de ações
    prioridade = Column(Integer, default=0)
    
    # Status
    ativa = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    contexto = relationship("AudioContexto", back_populates="regras")
    template = relationship("AudioTemplate", back_populates="regras")
    eventos = relationship("AudioEvento", back_populates="regra_aplicada")
    
    def __repr__(self):
        return f"<AudioRegra(id={self.id}, nome={self.nome}, contexto_id={self.contexto_id})>"

class AudioSessao(Base):
    __tablename__ = "audio_sessoes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Associações
    llamada_id = Column(Integer, ForeignKey("llamadas.id"), nullable=False)
    contexto_id = Column(Integer, ForeignKey("audio_contextos.id"), nullable=False)
    
    # Estados
    estado_atual = Column(SQLEnum(EstadoAudio), default=EstadoAudio.INICIANDO, nullable=False)
    estado_anterior = Column(SQLEnum(EstadoAudio), nullable=True)
    
    # Dados da sessão
    dados_sessao = Column(JSON, default={})
    configuracoes_personalizadas = Column(JSON, default={})
    
    # Timestamps
    iniciado_em = Column(DateTime, default=func.now())
    finalizado_em = Column(DateTime, nullable=True)
    ultima_mudanca_estado = Column(DateTime, default=func.now())
    
    # Relationships
    llamada = relationship("Llamada")
    contexto = relationship("AudioContexto", back_populates="sessoes")
    eventos = relationship("AudioEvento", back_populates="sessao")
    
    def __repr__(self):
        return f"<AudioSessao(id={self.id}, llamada_id={self.llamada_id}, estado={self.estado_atual})>"

class AudioEvento(Base):
    __tablename__ = "audio_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Associações
    sessao_id = Column(Integer, ForeignKey("audio_sessoes.id"), nullable=False)
    tipo_evento_id = Column(Integer, ForeignKey("tipos_evento_audio.id"), nullable=False)
    regra_aplicada_id = Column(Integer, ForeignKey("audio_regras.id"), nullable=True)
    
    # Estados
    estado_origem = Column(SQLEnum(EstadoAudio), nullable=True)
    estado_destino = Column(SQLEnum(EstadoAudio), nullable=False)
    
    # Dados do evento
    dados_evento = Column(JSON, default={})
    resultado = Column(Text, nullable=True)
    
    # Timestamp
    ocorrido_em = Column(DateTime, default=func.now())
    
    # Relationships
    sessao = relationship("AudioSessao", back_populates="eventos")
    tipo_evento = relationship("TipoEvento", back_populates="eventos")
    regra_aplicada = relationship("AudioRegra", back_populates="eventos")
    
    def __repr__(self):
        return f"<AudioEvento(id={self.id}, sessao_id={self.sessao_id}, tipo_evento_id={self.tipo_evento_id})>"

# Manter compatibilidade com código existente
class AudioSistema(Base):
    __tablename__ = "audio_sistema"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo_evento_id = Column(Integer, ForeignKey("tipos_evento_audio.id"), nullable=False)
    
    # Arquivo de áudio
    arquivo_path = Column(String(255), nullable=False)
    formato = Column(String(10), default="wav", nullable=False)
    duracao_segundos = Column(Integer, nullable=True)
    tamanho_bytes = Column(Integer, nullable=True)
    
    # Configurações
    volume = Column(Integer, default=100, nullable=False)  # 0-100
    loop_audio = Column(Boolean, default=False, nullable=False)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    tipo_evento = relationship("TipoEvento")
    
    def __repr__(self):
        return f"<AudioSistema(id={self.id}, nome={self.nome}, tipo_evento_id={self.tipo_evento_id})>" 