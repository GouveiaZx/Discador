from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, func
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from app.database import Base


class CampanaPresione1(Base):
    """
    Modelo para campanhas de discado preditivo con modo "Presione 1".
    """
    __tablename__ = "campanas_presione1"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    
    # Configuração da campanha
    lista_llamadas_id = Column(Integer, ForeignKey("listas_llamadas.id"), nullable=False)
    mensaje_audio_url = Column(String(500), nullable=False)  # URL del audio a reproducir
    timeout_presione1 = Column(Integer, default=10, nullable=False)  # Segundos para esperar DTMF
    
    # Configuração de voicemail
    detectar_voicemail = Column(Boolean, default=True, nullable=False)  # Se deve detectar voicemail
    mensaje_voicemail_url = Column(String(500), nullable=True)  # URL del audio para voicemail
    duracion_minima_voicemail = Column(Integer, default=3, nullable=False)  # Segundos mínimos para considerar voicemail
    duracion_maxima_voicemail = Column(Integer, default=30, nullable=False)  # Segundos máximos de gravação no voicemail
    
    # Configuração de transferência
    extension_transferencia = Column(String(20), nullable=True)  # Extensión para transferir
    cola_transferencia = Column(String(50), nullable=True)  # Cola de agentes
    
    # Estados da campanha
    activa = Column(Boolean, default=False, nullable=False)
    pausada = Column(Boolean, default=False, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Configuração de discado
    llamadas_simultaneas = Column(Integer, default=1, nullable=False)  # Canales simultáneos
    tiempo_entre_llamadas = Column(Integer, default=5, nullable=False)  # Segundos entre llamadas
    
    # Notas adicionales
    notas = Column(Text, nullable=True)
    
    # Relações
    lista_llamadas = relationship("ListaLlamadas", foreign_keys=[lista_llamadas_id])
    llamadas_presione1 = relationship("LlamadaPresione1", back_populates="campana")
    
    # Índices
    __table_args__ = (
        Index('idx_campanas_presione1_nombre', nombre),
        Index('idx_campanas_presione1_activa', activa),
        Index('idx_campanas_presione1_lista', lista_llamadas_id),
    )
    
    def __repr__(self):
        return f"<CampanaPresione1(id={self.id}, nombre={self.nombre}, activa={self.activa})>"


class LlamadaPresione1(Base):
    """
    Modelo para registrar llamadas específicas del modo "Presione 1".
    """
    __tablename__ = "llamadas_presione1"
    
    id = Column(Integer, primary_key=True, index=True)
    campana_id = Column(Integer, ForeignKey("campanas_presione1.id"), nullable=False)
    numero_destino = Column(String(20), nullable=False, index=True)
    numero_normalizado = Column(String(20), nullable=False, index=True)
    cli_utilizado = Column(String(20), nullable=True)
    
    # Estados específicos do fluxo
    estado = Column(String(30), default="pendiente", nullable=False)
    # Estados: pendiente, marcando, contestada, audio_reproducido, esperando_dtmf, 
    #          presiono_1, no_presiono, transferida, finalizada, error
    #          voicemail_detectado, voicemail_audio_reproducido, voicemail_finalizado
    
    # Dados da chamada
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_contestada = Column(DateTime, nullable=True)
    fecha_audio_inicio = Column(DateTime, nullable=True)
    fecha_dtmf_recibido = Column(DateTime, nullable=True)
    fecha_transferencia = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    
    # Dados específicos de voicemail
    voicemail_detectado = Column(Boolean, nullable=True)
    fecha_voicemail_detectado = Column(DateTime, nullable=True)
    fecha_voicemail_audio_inicio = Column(DateTime, nullable=True)
    fecha_voicemail_audio_fin = Column(DateTime, nullable=True)
    duracion_mensaje_voicemail = Column(Integer, nullable=True)  # Segundos de gravação no voicemail
    
    # Resultados
    presiono_1 = Column(Boolean, nullable=True)
    dtmf_recibido = Column(String(10), nullable=True)  # Tecla pressionada
    tiempo_respuesta_dtmf = Column(Float, nullable=True)  # Segundos hasta presionar tecla
    transferencia_exitosa = Column(Boolean, nullable=True)
    
    # Dados técnicos
    unique_id_asterisk = Column(String(50), nullable=True)
    channel = Column(String(100), nullable=True)
    duracion_total = Column(Integer, nullable=True)  # Segundos totales
    duracion_audio = Column(Integer, nullable=True)  # Segundos de audio
    
    # Motivo de finalização
    motivo_finalizacion = Column(String(100), nullable=True)
    # ex: "presiono_1_transferido", "timeout_dtmf", "colgado_durante_audio", "voicemail_mensaje_dejado", etc.
    
    # Relações
    campana = relationship("CampanaPresione1", back_populates="llamadas_presione1")
    
    # Índices
    __table_args__ = (
        Index('idx_llamadas_presione1_campana', campana_id),
        Index('idx_llamadas_presione1_numero', numero_destino),
        Index('idx_llamadas_presione1_estado', estado),
        Index('idx_llamadas_presione1_fecha', fecha_inicio),
        Index('idx_llamadas_presione1_presiono1', presiono_1),
        Index('idx_llamadas_presione1_voicemail', voicemail_detectado),
    )
    
    def __repr__(self):
        return f"<LlamadaPresione1(id={self.id}, numero={self.numero_destino}, estado={self.estado}, presiono_1={self.presiono_1}, voicemail={self.voicemail_detectado})>" 