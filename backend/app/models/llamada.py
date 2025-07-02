from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Llamada(Base):
    __tablename__ = "llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_destino = Column(String(20), nullable=False)
    campana_id = Column(Integer, ForeignKey("campanas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    # Estados: pendiente, en_progreso, conectada, finalizada, fallida
    estado = Column(String(20), default="pendiente", nullable=False)
    
    # CLI utilizado para la llamada
    cli = Column(String(20), nullable=True)
    
    # Timestamps
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_conexion = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)
    fecha_asignacion = Column(DateTime, nullable=True)
    
    # Resultado de la llamada
    resultado = Column(String(50), nullable=True)
    
    # Notas y observaciones
    notas = Column(Text, nullable=True)
    
    # Variables adicionales (JSON)
    variables_adicionales = Column(Text, nullable=True)
    
    # ID único de Asterisk
    asterisk_unique_id = Column(String(100), nullable=True)
    
    # Duración de la llamada en segundos
    duracion_segundos = Column(Integer, nullable=True)
    
    # DTMF presionado por el usuario
    dtmf_presionado = Column(String(10), nullable=True)
    
    # Relationships
    # campana = relationship("Campana", back_populates="llamadas")
    # usuario = relationship("Usuario", back_populates="llamadas_asignadas")
    
    def __repr__(self):
        return f"<Llamada(id={self.id}, numero={self.numero_destino}, estado={self.estado})>" 