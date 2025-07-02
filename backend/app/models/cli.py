"""
Modelo para manejo de CLIs (Caller Line Identification).
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.database import Base


class Cli(Base):
    """Modelo para CLIs."""
    
    __tablename__ = "cli"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, index=True, comment="Numero de telefone CLI original")
    numero_normalizado = Column(String(20), nullable=False, unique=True, index=True, comment="Numero normalizado")
    descripcion = Column(String(255), nullable=True, comment="Descripcion del CLI")
    notas = Column(Text, nullable=True, comment="Notas adicionales sobre el CLI")
    activo = Column(Boolean, default=True, nullable=False, comment="Si el CLI esta activo")
    veces_usado = Column(Integer, default=0, nullable=False, comment="Veces que se ha usado este CLI")
    ultima_vez_usado = Column(DateTime, nullable=True, comment="Ultima vez que se uso")
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False, comment="Fecha de creacion")
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="Fecha de ultima actualizacion")
    
    def __repr__(self):
        return f"<Cli(id={self.id}, numero='{self.numero_normalizado}', activo={self.activo})>" 