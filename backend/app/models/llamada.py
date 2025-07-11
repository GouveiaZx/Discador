# Modelo de Llamada
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
import enum

class EstadoLlamada(enum.Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"  
    CONECTADA = "conectada"
    FINALIZADA = "finalizada"
    ERROR = "error"
    TRANSFERIDA = "transferida"

class Llamada(Base):
    __tablename__ = "llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_destino = Column(String(20), nullable=False)
    numero_origen = Column(String(20))
    estado = Column(Enum(EstadoLlamada), default=EstadoLlamada.PENDIENTE)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime)
    duracion = Column(Float)  # en segundos
    resultado = Column(String(50))
    campana_id = Column(Integer, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    lista_id = Column(Integer, nullable=True)
    presiono_1 = Column(Boolean, default=False)
    transferido = Column(Boolean, default=False)
    notas = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="llamadas")
    
    def __repr__(self):
        return f"<Llamada(id={self.id}, numero={self.numero_destino}, estado={self.estado})>" 