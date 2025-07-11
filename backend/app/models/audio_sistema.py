"""
Modelos SQLAlchemy para o Sistema de Audio Inteligente
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from enum import Enum

Base = declarative_base()

# Enums para tipos de dados
class TipoEvento(Enum):
    CHAMADA_INICIADA = "chamada_iniciada"
    AUDIO_INICIADO = "audio_iniciado"
    DTMF_RECEBIDO = "dtmf_recebido"
    VOICEMAIL_DETECTADO = "voicemail_detectado"
    HUMANO_DETECTADO = "humano_detectado"
    CONEXAO_ESTABELECIDA = "conexao_estabelecida"
    TRANSFERENCIA_INICIADA = "transferencia_iniciada"
    CHAMADA_FINALIZADA = "chamada_finalizada"
    ERRO_OCORRIDO = "erro_ocorrido"
    TIMEOUT_ATINGIDO = "timeout_atingido"

class EstadoAudio(Enum):
    INICIANDO = "iniciando"
    TOCANDO = "tocando"
    AGUARDANDO_DTMF = "aguardando_dtmf"
    DETECTANDO_VOICEMAIL = "detectando_voicemail"
    REPRODUZINDO_VOICEMAIL = "reproduzindo_voicemail"
    AGUARDANDO_HUMANO = "aguardando_humano"
    CONECTADO = "conectado"
    TRANSFERINDO = "transferindo"
    FINALIZADO = "finalizado"
    ERRO = "erro"

class TipoOperadorRegra(Enum):
    IGUAL = "igual"
    DIFERENTE = "diferente"
    MAIOR_QUE = "maior_que"
    MENOR_QUE = "menor_que"
    CONTEM = "contem"
    NAO_CONTEM = "nao_contem"
    REGEX = "regex"

class TipoAcaoRegra(Enum):
    ALTERAR_ESTADO = "alterar_estado"
    EXECUTAR_TEMPLATE = "executar_template"
    TRANSFERIR_CHAMADA = "transferir_chamada"
    TOCAR_AUDIO = "tocar_audio"
    AGUARDAR_DTMF = "aguardar_dtmf"
    DETECTAR_VOICEMAIL = "detectar_voicemail"
    FINALIZAR_CHAMADA = "finalizar_chamada"
    ENVIAR_WEBHOOK = "enviar_webhook"

# Modelos SQLAlchemy

class AudioContexto(Base):
    """
    Contexto de audio que define um conjunto de regras e configurações
    para reproducão inteligente de audio em diferentes cenários.
    """
    __tablename__ = "audio_contextos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), unique=True, nullable=False, index=True)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    
    # Configurações gerais
    configuracoes = Column(JSON, default=dict)
    
    # Metadados de auditoria
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    criado_por = Column(String(100))
    
    # Relacionamentos
    regras = relationship("AudioRegra", back_populates="contexto", cascade="all, delete-orphan")
    templates = relationship("AudioTemplate", back_populates="contexto", cascade="all, delete-orphan")
    sessoes = relationship("AudioSessao", back_populates="contexto")

class AudioRegra(Base):
    """
    Regra de negócio para o sistema de audio inteligente.
    Define condições e ações a serem executadas durante a reproducão.
    """
    __tablename__ = "audio_regras"
    
    id = Column(Integer, primary_key=True, index=True)
    contexto_id = Column(Integer, ForeignKey("audio_contextos.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    
    # Ordem de execução (prioridade)
    ordem = Column(Integer, default=0)
    
    # Condições para aplicar a regra
    condicoes = Column(JSON, default=list)  # Lista de condições
    
    # Ações a serem executadas
    acoes = Column(JSON, default=list)  # Lista de ações
    
    # Configurações específicas
    configuracoes = Column(JSON, default=dict)
    
    # Metadados de auditoria
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    contexto = relationship("AudioContexto", back_populates="regras")
    eventos = relationship("AudioEvento", back_populates="regra_aplicada")

class AudioTemplate(Base):
    """
    Template de audio com configurações específicas para reproducão.
    """
    __tablename__ = "audio_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    contexto_id = Column(Integer, ForeignKey("audio_contextos.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    
    # Configurações do template
    arquivo_audio = Column(String(500))  # Caminho do arquivo de audio
    texto_tts = Column(Text)  # Texto para Text-to-Speech
    idioma = Column(String(10), default="pt-BR")
    voz = Column(String(50))
    
    # Configurações de reproducão
    volume = Column(Float, default=1.0)
    velocidade = Column(Float, default=1.0)
    
    # Configurações de comportamento
    repetir = Column(Boolean, default=False)
    max_repeticoes = Column(Integer, default=1)
    aguardar_dtmf = Column(Boolean, default=False)
    timeout_dtmf = Column(Integer, default=10)  # segundos
    
    # Metadados de auditoria
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    contexto = relationship("AudioContexto", back_populates="templates")

class AudioSessao(Base):
    """
    Sessão de audio ativa para uma chamada específica.
    """
    __tablename__ = "audio_sessoes"
    
    id = Column(Integer, primary_key=True, index=True)
    contexto_id = Column(Integer, ForeignKey("audio_contextos.id"), nullable=False)
    llamada_id = Column(Integer, nullable=False)  # ID da chamada
    
    # Estados da sessão
    estado_atual = Column(SQLEnum(EstadoAudio), default=EstadoAudio.INICIANDO)
    estado_anterior = Column(SQLEnum(EstadoAudio))
    
    # Dados do contexto da sessão
    dados_contexto = Column(JSON, default=dict)
    
    # Configurações personalizadas para esta sessão
    configuracoes_personalizadas = Column(JSON, default=dict)
    
    # Timestamps
    iniciado_em = Column(DateTime, default=datetime.utcnow)
    ultima_mudanca_estado = Column(DateTime, default=datetime.utcnow)
    finalizado_em = Column(DateTime)
    
    # Relacionamentos
    contexto = relationship("AudioContexto", back_populates="sessoes")
    eventos = relationship("AudioEvento", back_populates="sessao", cascade="all, delete-orphan")

class AudioEvento(Base):
    """
    Evento registrado durante uma sessão de audio.
    """
    __tablename__ = "audio_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    sessao_id = Column(Integer, ForeignKey("audio_sessoes.id"), nullable=False)
    regra_aplicada_id = Column(Integer, ForeignKey("audio_regras.id"))
    
    # Dados do evento
    tipo_evento = Column(SQLEnum(TipoEvento), nullable=False)
    estado_origem = Column(SQLEnum(EstadoAudio))
    estado_destino = Column(SQLEnum(EstadoAudio))
    
    # Dados específicos do evento
    dados_evento = Column(JSON, default=dict)
    
    # Resultado da execução
    sucesso = Column(Boolean, default=True)
    mensagem_erro = Column(Text)
    
    # Timestamp
    ocorrido_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    sessao = relationship("AudioSessao", back_populates="eventos")
    regra_aplicada = relationship("AudioRegra", back_populates="eventos")

# Exportar classes para uso
__all__ = [
    "TipoEvento", "EstadoAudio", "TipoOperadorRegra", "TipoAcaoRegra",
    "AudioContexto", "AudioRegra", "AudioTemplate", "AudioSessao", "AudioEvento"
] 