from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, Text
from sqlalchemy.schema import Index

from app.database import Base

class ListaNegra(Base):
    """
    Modelo para la tabla lista_negra que almacena los numeros de telefono bloqueados.
    """
    __tablename__ = "lista_negra"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, index=True)
    numero_normalizado = Column(String(20), unique=True, nullable=False, index=True)
    motivo = Column(String(255), nullable=True)
    observaciones = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    creado_por = Column(String(100), nullable=True)  # Usuario que agrego el numero
    veces_bloqueado = Column(Integer, default=0, nullable=False)  # Contador de veces que se bloqueo
    ultima_vez_bloqueado = Column(DateTime, nullable=True)  # Ultima vez que se intento llamar
    
    # Indices adicionales
    __table_args__ = (
        Index('idx_lista_negra_numero', numero),
        Index('idx_lista_negra_normalizado', numero_normalizado),
        Index('idx_lista_negra_activo', activo),
        Index('idx_lista_negra_fecha', fecha_creacion),
    )
    
    def __repr__(self):
        return f"<ListaNegra(id={self.id}, numero={self.numero_normalizado}, activo={self.activo})>" 