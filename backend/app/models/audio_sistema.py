from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, func, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base

# Enums para o sistema de áudio
class EstadoAudio(enum.Enum):
    """Estados possíveis do sistema de áudio"""
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
    """Operadores para regras do sistema"""
    IGUAL = "igual"
    DIFERENTE = "diferente"
    MAIOR_QUE = "maior_que"
    MENOR_QUE = "menor_que"
    CONTEM = "contem"
    NAO_CONTEM = "nao_contem"
    ENTRE = "entre"
    EXISTE = "existe"

class TipoEvento(Base):
    __tablename__ = "tipo_evento"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True)
    codigo = Column(String(20), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    
    # Configurações do evento
    permite_audio = Column(Boolean, default=True, nullable=False)
    audio_obrigatorio = Column(Boolean, default=False, nullable=False)
    
    # Status
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<TipoEvento(id={self.id}, nome={self.nome}, codigo={self.codigo})>"

class AudioSistema(Base):
    __tablename__ = "audio_sistema"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo_evento_id = Column(Integer, ForeignKey("tipo_evento.id"), nullable=False)
    
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
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    tipo_evento = relationship("TipoEvento")
    
    def __repr__(self):
        return f"<AudioSistema(id={self.id}, nome={self.nome}, tipo_evento_id={self.tipo_evento_id})>"

class AudioContexto(Base):
    __tablename__ = "audio_contexto"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    campanha_id = Column(Integer, ForeignKey("campanas.id"), nullable=True)
    
    # Configurações padrão
    audio_inicial_url = Column(String(255), nullable=False)
    timeout_dtmf = Column(Integer, default=10, nullable=False)  # segundos
    detectar_voicemail = Column(Boolean, default=True, nullable=False)
    max_tentativas = Column(Integer, default=3, nullable=False)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    regras = relationship("AudioRegra", back_populates="contexto", cascade="all, delete-orphan")
    sessoes = relationship("AudioSessao", back_populates="contexto")
    templates = relationship("AudioTemplate", back_populates="contexto")
    
    def __repr__(self):
        return f"<AudioContexto(id={self.id}, nome={self.nome})>"

class AudioRegra(Base):
    __tablename__ = "audio_regra"
    
    id = Column(Integer, primary_key=True, index=True)
    contexto_id = Column(Integer, ForeignKey("audio_contexto.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Estados
    estado_origem = Column(Enum(EstadoAudio), nullable=False)
    estado_destino = Column(Enum(EstadoAudio), nullable=False)
    
    # Evento disparador (opcional)
    evento_disparador = Column(String(50), nullable=True)
    
    # Condições adicionais (JSON)
    condicoes = Column(JSON, nullable=True)
    
    # Ações
    audio_url = Column(String(255), nullable=True)
    parametros_acao = Column(JSON, nullable=True)
    
    # Prioridade (maior valor = maior prioridade)
    prioridade = Column(Integer, default=0, nullable=False)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relationships
    contexto = relationship("AudioContexto", back_populates="regras")
    eventos = relationship("AudioEvento", back_populates="regra_aplicada")
    
    def __repr__(self):
        return f"<AudioRegra(id={self.id}, nome={self.nome}, prioridade={self.prioridade})>"

class AudioSessao(Base):
    __tablename__ = "audio_sessao"
    
    id = Column(Integer, primary_key=True, index=True)
    llamada_id = Column(Integer, ForeignKey("llamadas.id"), nullable=False, unique=True)
    contexto_id = Column(Integer, ForeignKey("audio_contexto.id"), nullable=False)
    
    # Estados
    estado_atual = Column(Enum(EstadoAudio), nullable=False, default=EstadoAudio.INICIANDO)
    estado_anterior = Column(Enum(EstadoAudio), nullable=True)
    
    # Áudio atual
    audio_atual_url = Column(String(255), nullable=True)
    
    # Configurações da sessão
    timeout_dtmf = Column(Integer, nullable=True)
    detectar_voicemail = Column(Boolean, default=True, nullable=False)
    tentativas_realizadas = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    iniciado_em = Column(DateTime, default=func.now(), nullable=False)
    finalizado_em = Column(DateTime, nullable=True)
    ultima_mudanca_estado = Column(DateTime, default=func.now(), nullable=False)
    
    # Dados do contexto
    dados_contexto = Column(JSON, nullable=True)
    
    # Relationships
    contexto = relationship("AudioContexto", back_populates="sessoes")
    eventos = relationship("AudioEvento", back_populates="sessao", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AudioSessao(id={self.id}, llamada_id={self.llamada_id}, estado={self.estado_atual})>"

class AudioEvento(Base):
    __tablename__ = "audio_evento"
    
    id = Column(Integer, primary_key=True, index=True)
    sessao_id = Column(Integer, ForeignKey("audio_sessao.id"), nullable=False)
    
    # Evento
    tipo_evento = Column(String(50), nullable=False)
    timestamp_evento = Column(DateTime, default=func.now(), nullable=False)
    
    # Estados
    estado_origem = Column(Enum(EstadoAudio), nullable=True)
    estado_destino = Column(Enum(EstadoAudio), nullable=True)
    
    # Dados do evento
    dados_evento = Column(JSON, nullable=True)
    
    # Regra aplicada
    regra_aplicada_id = Column(Integer, ForeignKey("audio_regra.id"), nullable=True)
    
    # Relationships
    sessao = relationship("AudioSessao", back_populates="eventos")
    regra_aplicada = relationship("AudioRegra", back_populates="eventos")
    
    def __repr__(self):
        return f"<AudioEvento(id={self.id}, tipo={self.tipo_evento}, sessao_id={self.sessao_id})>"

class AudioTemplate(Base):
    __tablename__ = "audio_template"
    
    id = Column(Integer, primary_key=True, index=True)
    contexto_id = Column(Integer, ForeignKey("audio_contexto.id"), nullable=False)
    
    # Informações do template
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    tipo_template = Column(String(50), nullable=False)  # voicemail, ivr, campanha, etc.
    
    # Configurações padrão
    configuracoes_padrao = Column(JSON, nullable=True)
    regras_padrao = Column(JSON, nullable=True)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    contexto = relationship("AudioContexto", back_populates="templates")
    
    def __repr__(self):
        return f"<AudioTemplate(id={self.id}, nome={self.nome}, tipo={self.tipo_template})>" 