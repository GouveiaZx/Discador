from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class ListaLlamadas(Base):
    __tablename__ = "listas_llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Configurações da lista
    total_contactos = Column(Integer, default=0, nullable=False)
    contactos_procesados = Column(Integer, default=0, nullable=False)
    contactos_pendientes = Column(Integer, default=0, nullable=False)
    
    # Status da lista
    activa = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Configurações de processamento
    prioridad = Column(Integer, default=1, nullable=False)
    limite_intentos = Column(Integer, default=3, nullable=False)
    
    # Metadados
    archivo_origen = Column(String(255), nullable=True)
    usuario_creador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    # Relationships
    numeros = relationship("NumeroLlamada", back_populates="lista", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ListaLlamadas(id={self.id}, nombre={self.nombre}, total={self.total_contactos})>"


class NumeroLlamada(Base):
    __tablename__ = "numeros_llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    lista_id = Column(Integer, ForeignKey("listas_llamadas.id"), nullable=False)
    
    # Dados do número
    numero = Column(String(20), nullable=False)
    numero_normalizado = Column(String(20), nullable=False, index=True)
    
    # Informações adicionais
    nombre = Column(String(100), nullable=True)
    apellido = Column(String(100), nullable=True)
    empresa = Column(String(100), nullable=True)
    
    # Status
    valido = Column(Boolean, default=True, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Histórico de chamadas
    intentos = Column(Integer, default=0, nullable=False)
    ultimo_intento = Column(DateTime, nullable=True)
    ultimo_resultado = Column(String(50), nullable=True)
    
    # Metadados
    notas = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    lista = relationship("ListaLlamadas", back_populates="numeros")
    
    def __repr__(self):
        return f"<NumeroLlamada(id={self.id}, numero={self.numero}, lista_id={self.lista_id})>" 