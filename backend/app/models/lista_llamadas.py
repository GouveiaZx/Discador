# Modelo de Lista de Llamadas
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class ListaLlamadas(Base):
    __tablename__ = "listas_llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    activa = Column(Boolean, default=True)
    total_numeros = Column(Integer, default=0)
    numeros_procesados = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    numeros = relationship("NumeroLlamada", back_populates="lista")
    
    def __repr__(self):
        return f"<ListaLlamadas(id={self.id}, nombre={self.nombre})>"

class NumeroLlamada(Base):
    __tablename__ = "numeros_llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, index=True)
    lista_id = Column(Integer, ForeignKey("listas_llamadas.id"))
    procesado = Column(Boolean, default=False)
    resultado = Column(String(50))
    intentos = Column(Integer, default=0)
    datos_adicionales = Column(Text)  # JSON con datos extra
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    lista = relationship("ListaLlamadas", back_populates="numeros")
    
    def __repr__(self):
        return f"<NumeroLlamada(id={self.id}, numero={self.numero})>" 