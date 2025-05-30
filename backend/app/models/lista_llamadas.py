from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from app.database import Base

class ListaLlamadas(Base):
    """
    Modelo para la tabla listas_llamadas que almacena las listas de números para llamar.
    """
    __tablename__ = "listas_llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(255), nullable=True)
    archivo_original = Column(String(255), nullable=False)
    total_numeros = Column(Integer, default=0, nullable=False)
    numeros_validos = Column(Integer, default=0, nullable=False)
    numeros_duplicados = Column(Integer, default=0, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    activa = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    numeros = relationship("NumeroLlamada", back_populates="lista", cascade="all, delete-orphan")
    llamadas = relationship("Llamada", back_populates="lista_llamadas")
    
    # Índices adicionales
    __table_args__ = (
        Index('idx_listas_nombre', nombre),
        Index('idx_listas_activa', activa),
        Index('idx_listas_fecha', fecha_creacion),
    )
    
    def __repr__(self):
        return f"<ListaLlamadas(id={self.id}, nombre={self.nombre}, total={self.numeros_validos})>"


class NumeroLlamada(Base):
    """
    Modelo para almacenar los números individuales de cada lista.
    """
    __tablename__ = "numeros_llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False)
    numero_normalizado = Column(String(20), nullable=False, index=True)
    id_lista = Column(Integer, ForeignKey("listas_llamadas.id"), nullable=False, index=True)
    valido = Column(Boolean, default=True, nullable=False)
    notas = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    
    # Relaciones - Usando string para evitar import circular
    lista = relationship("ListaLlamadas", back_populates="numeros")
    
    # Índices adicionales
    __table_args__ = (
        Index('idx_numeros_numero', numero),
        Index('idx_numeros_normalizado', numero_normalizado),
        Index('idx_numeros_lista', id_lista),
        Index('idx_numeros_valido', valido),
        # Índice único para evitar duplicados por lista
        Index('idx_unique_numero_lista', numero_normalizado, id_lista, unique=True),
    )
    
    def __repr__(self):
        return f"<NumeroLlamada(id={self.id}, numero={self.numero}, valido={self.valido})>" 