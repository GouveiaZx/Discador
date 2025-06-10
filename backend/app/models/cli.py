from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, Text
from sqlalchemy.schema import Index

from app.database import Base

class Cli(Base):
    """
    Modelo para la tabla cli que almacena los identificadores de llamada permitidos.
    """
    __tablename__ = "cli"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, unique=True, index=True)
    numero_normalizado = Column(String(20), nullable=False, unique=True, index=True)
    descripcion = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    veces_usado = Column(Integer, default=0, nullable=False)
    ultima_vez_usado = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    notas = Column(Text, nullable=True)
    
    # Indices adicionales
    __table_args__ = (
        Index('idx_cli_numero', numero),
        Index('idx_cli_normalizado', numero_normalizado),
        Index('idx_cli_activo', activo),
        Index('idx_cli_fecha', fecha_creacion),
        Index('idx_cli_veces_usado', veces_usado),
    )
    
    def __repr__(self):
        return f"<Cli(id={self.id}, numero={self.numero_normalizado}, activo={self.activo})>" 