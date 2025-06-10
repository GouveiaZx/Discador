from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from app.database import Base

class Campana(Base):
    """
    Modelo para la tabla campanas que almacena la informacion de las campanas de llamadas.
    """
    __tablename__ = "campanas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    activa = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    llamadas = relationship("Llamada", back_populates="campana")
    leads = relationship("Lead", back_populates="campana")
    
    # Indices adicionales
    __table_args__ = (
        Index('idx_campanas_nombre', nombre),
        Index('idx_campanas_activa', activa),
    )
    
    def __repr__(self):
        return f"<Campana(id={self.id}, nombre={self.nombre}, activa={self.activa})>" 