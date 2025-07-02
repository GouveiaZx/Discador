from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

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