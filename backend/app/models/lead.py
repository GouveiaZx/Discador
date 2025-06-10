from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from app.database import Base

class Lead(Base):
    """
    Modelo para la tabla leads que almacena los numeros a llamar.
    """
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, index=True)
    nombre = Column(String(100), nullable=True)
    correo = Column(String(100), nullable=True)
    notas = Column(String(255), nullable=True)
    id_campana = Column(Integer, ForeignKey("campanas.id"), nullable=False)
    procesado = Column(Boolean, default=False, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_procesado = Column(DateTime, nullable=True)
    
    # Relaciones
    campana = relationship("Campana", back_populates="leads")
    
    # Indices adicionales
    __table_args__ = (
        Index('idx_leads_numero', numero),
        Index('idx_leads_procesado', procesado),
        Index('idx_leads_campana_procesado', id_campana, procesado),
    )
    
    def __repr__(self):
        return f"<Lead(id={self.id}, numero={self.numero}, procesado={self.procesado})>" 