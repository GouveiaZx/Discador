from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class Campana(Base):
    __tablename__ = "campanas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Tipo de campanha
    tipo_campana = Column(String(50), default="general", nullable=False)  # general, politica, comercial
    
    # Status e configurações
    activa = Column(Boolean, default=True, nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=True)
    
    # Configurações de discagem
    max_intentos = Column(Integer, default=3, nullable=False)
    intervalo_reintento = Column(Integer, default=300, nullable=False)  # segundos
    
    # Horários de funcionamento
    hora_inicio = Column(String(5), default="08:00", nullable=False)  # HH:MM
    hora_fin = Column(String(5), default="18:00", nullable=False)  # HH:MM
    
    # Configurações de áudio
    audio_principal_id = Column(Integer, ForeignKey("audios.id"), nullable=True)
    detectar_caixa_postal = Column(Boolean, default=True, nullable=False)
    
    # Metadados
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Estatísticas básicas
    total_contactos = Column(Integer, default=0, nullable=False)
    contactos_procesados = Column(Integer, default=0, nullable=False)
    contactos_pendientes = Column(Integer, default=0, nullable=False)
    
    # Relationships
    # creado_por = relationship("Usuario")
    # audio_principal = relationship("Audio")
    # llamadas = relationship("Llamada", back_populates="campana")
    
    def __repr__(self):
        return f"<Campana(id={self.id}, nombre={self.nombre}, tipo={self.tipo_campana})>" 