from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

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