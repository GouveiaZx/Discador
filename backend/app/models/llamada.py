from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from app.database import Base

class EstadoLlamada(PyEnum):
    """Estados possíveis de uma chamada."""
    PENDIENTE = "pendiente"
    INICIADA = "iniciada"
    MARCANDO = "marcando"
    CONECTANDO = "conectando"
    EN_PROGRESO = "en_progreso"
    CONECTADA = "conectada"
    TRANSFERIDA = "transferida"
    FINALIZADA = "finalizada"
    FALLIDA = "fallida"
    OCUPADO = "ocupado"
    NO_CONTESTA = "no_contesta"
    CANCELADA = "cancelada"

class Llamada(Base):
    __tablename__ = "llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_destino = Column(String(20), nullable=False)
    numero_origem = Column(String(20), nullable=True)  # Adicionado para compatibilidade
    campana_id = Column(Integer, ForeignKey("campanas.id"), nullable=False)
    campanha_id = Column(Integer, ForeignKey("campanas.id"), nullable=True)  # Alias para compatibilidade
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    trunk_id = Column(Integer, ForeignKey("trunk.id"), nullable=True)  # Adicionado para trunks
    
    # Estados usando enum
    estado = Column(Enum(EstadoLlamada), default=EstadoLlamada.PENDIENTE, nullable=False)
    
    # CLI utilizado para la llamada
    cli = Column(String(20), nullable=True)
    
    # Timestamps
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_conexion = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)
    fecha_asignacion = Column(DateTime, nullable=True)
    
    # Resultado de la llamada
    resultado = Column(String(50), nullable=True)
    
    # Notas y observaciones
    notas = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)  # Alias para compatibilidade
    
    # Variables adicionales (JSON)
    variables_adicionales = Column(Text, nullable=True)
    
    # ID único de Asterisk
    asterisk_unique_id = Column(String(100), nullable=True)
    
    # Duración de la llamada en segundos
    duracion_segundos = Column(Integer, nullable=True)
    
    # DTMF presionado por el usuario
    dtmf_presionado = Column(String(10), nullable=True)
    
    # Relationships
    # campana = relationship("Campana", back_populates="llamadas")
    # usuario = relationship("Usuario", back_populates="llamadas_asignadas")
    # trunk = relationship("Trunk", back_populates="llamadas")
    
    def __repr__(self):
        return f"<Llamada(id={self.id}, numero={self.numero_destino}, estado={self.estado.value})>" 