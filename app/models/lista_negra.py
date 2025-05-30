from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.schema import Index

from app.database import Base

class ListaNegra(Base):
    """
    Modelo para la tabla lista_negra que almacena los números de teléfono bloqueados.
    """
    __tablename__ = "lista_negra"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)
    motivo = Column(String(255), nullable=True)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Índices adicionales
    __table_args__ = (
        Index('idx_lista_negra_numero', numero),
    )
    
    def __repr__(self):
        return f"<ListaNegra(id={self.id}, numero={self.numero})>" 