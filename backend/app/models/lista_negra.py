# Modelo de Lista Negra (DNC)
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from . import Base

class ListaNegra(Base):
    __tablename__ = "lista_negra"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, unique=True, index=True)
    motivo = Column(String(100))
    campana_id = Column(Integer, nullable=True)
    usuario_id = Column(Integer, nullable=True)
    observaciones = Column(Text)
    activo = Column(Boolean, default=True)
    fecha_vencimiento = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ListaNegra(id={self.id}, numero={self.numero})>"
    
    def is_expired(self):
        """Verifica se o registro expirou"""
        if self.fecha_vencimiento:
            return datetime.utcnow() > self.fecha_vencimiento
        return False 