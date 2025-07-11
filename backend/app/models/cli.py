# Modelo de CLI (Caller ID)
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from . import Base

class Cli(Base):
    __tablename__ = "clis"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, index=True)
    pais = Column(String(10), default="usa")
    activo = Column(Boolean, default=True)
    usos_diarios = Column(Integer, default=0)
    limite_diario = Column(Integer, default=100)
    ultimo_uso = Column(DateTime)
    campana_id = Column(Integer, nullable=True)
    proveedor = Column(String(50))
    observaciones = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Cli(id={self.id}, numero={self.numero}, pais={self.pais})>"
    
    def can_use(self):
        """Verifica se o CLI pode ser usado (limite diário)"""
        return self.activo and self.usos_diarios < self.limite_diario 