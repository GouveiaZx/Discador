"""
Modelo para manejo de blacklist/lista negra.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.database import Base


class ListaNegra(Base):
    """Modelo para lista negra/blacklist."""
    
    __tablename__ = "lista_negra"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, index=True, comment="Numero de telefone original")
    numero_normalizado = Column(String(20), nullable=False, unique=True, index=True, comment="Numero normalizado")
    motivo = Column(String(255), nullable=True, comment="Motivo del bloqueo")
    observaciones = Column(Text, nullable=True, comment="Observaciones adicionales")
    creado_por = Column(String(100), nullable=True, comment="Usuario que creo el registro")
    activo = Column(Boolean, default=True, nullable=False, comment="Si el bloqueo esta activo")
    veces_bloqueado = Column(Integer, default=0, nullable=False, comment="Veces que se ha bloqueado este numero")
    ultima_vez_bloqueado = Column(DateTime, nullable=True, comment="Ultima vez que se intento llamar")
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False, comment="Fecha de creacion")
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="Fecha de ultima actualizacion")
    
    def __repr__(self):
        return f"<ListaNegra(id={self.id}, numero='{self.numero_normalizado}', activo={self.activo})>" 