from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, func, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, date, time
import enum

from app.database import Base

# Enums para tipos de log eleitoral
class TipoLogEleitoral(enum.Enum):
    CONFIGURACAO_CRIADA = "configuracao_criada"
    CONFIGURACAO_ALTERADA = "configuracao_alterada"
    CALENDARIO_CRIADO = "calendario_criado"
    CAMPANHA_INICIADA = "campanha_iniciada"
    CAMPANHA_PAUSADA = "campanha_pausada"
    CAMPANHA_FINALIZADA = "campanha_finalizada"
    VIOLACAO_HORARIO = "violacao_horario"
    OPT_OUT_REGISTRADO = "opt_out_registrado"

# Enum para tipos de eleição
class TipoEleicao(enum.Enum):
    MUNICIPAL = "municipal"
    ESTADUAL = "estadual"
    FEDERAL = "federal"
    ESPECIAL = "especial"

# Enum para status da campanha política
class StatusCampanhaPolitica(enum.Enum):
    CRIADA = "criada"
    AGUARDANDO_APROVACAO = "aguardando_aprovacao"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    ATIVA = "ativa"
    PAUSADA = "pausada"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"

class CampanhaPolitica(Base):
    __tablename__ = "campanha_politica"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    candidato = Column(String(100), nullable=False)
    partido = Column(String(50), nullable=True)
    cargo = Column(String(50), nullable=False)
    
    # Configurações da campanha
    descricao = Column(Text, nullable=True)
    numero_candidato = Column(String(10), nullable=True)
    
    # Status e datas
    ativa = Column(Boolean, default=True, nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    
    # Metadados
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Configurações específicas
    permite_sms = Column(Boolean, default=False, nullable=False)
    permite_whatsapp = Column(Boolean, default=False, nullable=False)
    limite_chamadas_dia = Column(Integer, default=1000, nullable=False)
    
    # Relationships
    # criado_por = relationship("Usuario")
    # audios = relationship("AudioCampanha", back_populates="campanha", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CampanhaPolitica(id={self.id}, nome={self.nome}, candidato={self.candidato})>"

class ConfiguracaoEleitoral(Base):
    __tablename__ = "configuracao_eleitoral"
    
    id = Column(Integer, primary_key=True, index=True)
    pais_codigo = Column(String(3), nullable=False, unique=True)
    nome_pais = Column(String(100), nullable=False)
    
    # Horários permitidos
    horario_inicio_segunda = Column(Time, nullable=False)
    horario_fim_segunda = Column(Time, nullable=False)
    horario_inicio_sabado = Column(Time, nullable=False)
    horario_fim_sabado = Column(Time, nullable=False)
    permite_domingo = Column(Boolean, default=False, nullable=False)
    
    # Configurações específicas
    maximo_chamadas_por_numero = Column(Integer, default=1, nullable=False)
    intervalo_minimo_chamadas_horas = Column(Integer, default=24, nullable=False)
    
    # Status
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConfiguracaoEleitoral(id={self.id}, pais={self.pais_codigo})>"

class CalendarioEleitoral(Base):
    __tablename__ = "calendario_eleitoral"
    
    id = Column(Integer, primary_key=True, index=True)
    pais_codigo = Column(String(3), nullable=False)
    nome_eleicao = Column(String(100), nullable=False)
    
    # Datas da eleição
    data_eleicao = Column(Date, nullable=False)
    data_inicio_campanha = Column(Date, nullable=False)
    data_fim_campanha = Column(Date, nullable=False)
    
    # Períodos de silêncio
    data_inicio_silencio = Column(Date, nullable=True)
    data_fim_silencio = Column(Date, nullable=True)
    
    # Configurações
    tipo_eleicao = Column(String(50), nullable=False)  # municipal, estadual, federal
    permite_pesquisa = Column(Boolean, default=True, nullable=False)
    
    # Status
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<CalendarioEleitoral(id={self.id}, eleicao={self.nome_eleicao})>"

class LogEleitoralImutavel(Base):
    __tablename__ = "log_eleitoral_imutavel"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações do log
    tipo_log = Column(String(50), nullable=False)  # Usar enum TipoLogEleitoral
    descricao = Column(Text, nullable=False)
    dados_antes = Column(Text, nullable=True)  # JSON dos dados antes da mudança
    dados_depois = Column(Text, nullable=True)  # JSON dos dados depois da mudança
    
    # Metadados imutáveis
    usuario_id = Column(Integer, nullable=True)
    usuario_nome = Column(String(100), nullable=True)
    ip_origem = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamp imutável
    timestamp_utc = Column(DateTime, default=func.now(), nullable=False)
    
    # Hash de integridade
    hash_integridade = Column(String(64), nullable=False)
    
    def __repr__(self):
        return f"<LogEleitoralImutavel(id={self.id}, tipo={self.tipo_log}, timestamp={self.timestamp_utc})>"

class OptOutEleitoral(Base):
    __tablename__ = "opt_out_eleitoral"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações do número
    numero = Column(String(20), nullable=False)
    numero_normalizado = Column(String(20), nullable=False, unique=True, index=True)
    
    # Informações do opt-out
    motivo = Column(String(255), nullable=True)
    canal_origem = Column(String(50), nullable=False)  # telefone, sms, whatsapp, web
    
    # Metadados
    ip_origem = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Status
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<OptOutEleitoral(id={self.id}, numero={self.numero})>"

class AudioCampanha(Base):
    __tablename__ = "audio_campanha"
    
    id = Column(Integer, primary_key=True, index=True)
    campanha_id = Column(Integer, ForeignKey("campanha_politica.id"), nullable=False)
    
    # Informações do áudio
    nome = Column(String(100), nullable=False)
    tipo_audio = Column(String(50), nullable=False)  # principal, press_1, press_2, etc.
    arquivo_path = Column(String(255), nullable=False)
    duracao_segundos = Column(Integer, nullable=True)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relationships
    # campanha = relationship("CampanhaPolitica", back_populates="audios")
    
    def __repr__(self):
        return f"<AudioCampanha(id={self.id}, nome={self.nome}, tipo={self.tipo_audio})>"

class EstatisticaCampanha(Base):
    __tablename__ = "estatistica_campanha"
    
    id = Column(Integer, primary_key=True, index=True)
    campanha_id = Column(Integer, ForeignKey("campanha_politica.id"), nullable=False)
    
    # Métricas do dia
    data_estatistica = Column(DateTime, nullable=False)
    total_chamadas = Column(Integer, default=0, nullable=False)
    chamadas_atendidas = Column(Integer, default=0, nullable=False)
    chamadas_nao_atendidas = Column(Integer, default=0, nullable=False)
    chamadas_ocupado = Column(Integer, default=0, nullable=False)
    
    # Interações
    press_1 = Column(Integer, default=0, nullable=False)
    press_2 = Column(Integer, default=0, nullable=False)
    press_3 = Column(Integer, default=0, nullable=False)
    
    # Custos
    custo_total = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    tempo_total_minutos = Column(Integer, default=0, nullable=False)
    
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relationships
    # campanha = relationship("CampanhaPolitica")
    
    def __repr__(self):
        return f"<EstatisticaCampanha(id={self.id}, campanha_id={self.campanha_id}, data={self.data_estatistica})>" 