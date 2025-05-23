from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

class Llamada(Base):
    """
    Modelo para la tabla llamadas que almacena la información de las llamadas realizadas.
    """
    __tablename__ = "llamadas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_destino = Column(String(20), nullable=False, index=True)
    numero_normalizado = Column(String(20), nullable=False, index=True)  # Número normalizado para verificación
    cli = Column(String(20), nullable=True)
    id_campana = Column(Integer, ForeignKey("campanas.id"), nullable=True)
    id_lista_llamadas = Column(Integer, ForeignKey("listas_llamadas.id"), nullable=True)  # Nueva referencia a lista
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)  # Usuario asignado a la llamada
    fecha_inicio = Column(DateTime, default=func.now(), nullable=False)
    fecha_asignacion = Column(DateTime, nullable=True)  # Fecha y hora en que se asignó la llamada a un usuario
    fecha_conexion = Column(DateTime, nullable=True)  # Fecha y hora en que el usuario presionó 1
    fecha_fin = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)  # Fecha y hora en que se finalizó la llamada
    duracion = Column(Integer, nullable=True)  # Duración en segundos
    estado = Column(String(20), nullable=False, default="pendiente")  # pendiente, en_progreso, conectada, finalizada
    resultado = Column(String(20), nullable=True)  # contestada, no_contesta, buzon, numero_invalido, otro
    presiono_1 = Column(Boolean, nullable=True)  # Indica si el usuario presionó la tecla 1 (DTMF detectado)
    transcripcion = Column(Text, nullable=True)
    confianza_transcripcion = Column(Float, nullable=True)
    dtmf_detectado = Column(String(20), nullable=True)  # Almacena cualquier dígito DTMF detectado durante la llamada
    bloqueado_blacklist = Column(Boolean, default=False, nullable=False)  # Si fue bloqueado por blacklist
    
    # Relaciones
    campana = relationship("Campana", back_populates="llamadas")
    usuario = relationship("Usuario", back_populates="llamadas")
    lista_llamadas = relationship("ListaLlamadas", back_populates="llamadas")
    
    # Índices adicionales
    __table_args__ = (
        Index('idx_llamadas_numero_destino', numero_destino),
        Index('idx_llamadas_numero_normalizado', numero_normalizado),
        Index('idx_llamadas_fecha_inicio', fecha_inicio),
        Index('idx_llamadas_estado', estado),
        Index('idx_llamadas_usuario_id', usuario_id),
        Index('idx_llamadas_resultado', resultado),
        Index('idx_llamadas_lista', id_lista_llamadas),
        Index('idx_llamadas_bloqueado', bloqueado_blacklist),
    )
    
    def __repr__(self):
        return f"<Llamada(id={self.id}, numero_destino={self.numero_destino}, estado={self.estado})>" 