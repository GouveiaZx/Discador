from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from app.database import Base

class Llamada(Base):
    """
    Modelo para la tabla llamadas que almacena la información de las llamadas realizadas.
    """
    __tablename__ = "llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_destino = Column(String(20), nullable=False, index=True)
    cli = Column(String(20), nullable=True)
    id_campana = Column(Integer, ForeignKey("campanas.id"), nullable=True)
    fecha_inicio = Column(DateTime, default=func.now(), nullable=False)
    fecha_fin = Column(DateTime, nullable=True)
    duracion = Column(Integer, nullable=True)  # Duración en segundos
    estado = Column(String(20), nullable=False, default="pendiente")  # pendiente, iniciada, completada, fallida
    presiono_1 = Column(Boolean, nullable=True)
    transcripcion = Column(Text, nullable=True)
    confianza_transcripcion = Column(Float, nullable=True)
    
    # Relaciones
    campana = relationship("Campana", back_populates="llamadas")
    
    # Índices adicionales
    __table_args__ = (
        Index('idx_llamadas_numero_destino', numero_destino),
        Index('idx_llamadas_fecha_inicio', fecha_inicio),
        Index('idx_llamadas_estado', estado),
    )
    
    def __repr__(self):
        return f"<Llamada(id={self.id}, numero_destino={self.numero_destino}, estado={self.estado})>" 