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
    # usuario_creador = relationship("Usuario")
    # contactos = relationship("ContactoLista", back_populates="lista", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ListaLlamadas(id={self.id}, nombre={self.nombre}, total={self.total_contactos})>" 