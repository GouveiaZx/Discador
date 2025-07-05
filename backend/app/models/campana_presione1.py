"""
Modelos de dados para campanhas de discado preditivo com modo "Presione 1".
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CampanaPresione1(Base):
    """
    Modelo para campanhas de discado preditivo com modo 'Presione 1'.
    """
    __tablename__ = "campanas_presione1"
    
    # Campos principais
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    descripcion = Column(Text)
    
    # Configurações da campanha
    campaign_id = Column(Integer, nullable=False, index=True)  # Referência para campaigns do Supabase
    mensaje_audio_url = Column(String(500))  # URL do áudio a reproduzir
    timeout_presione1 = Column(Integer, default=10)  # Segundos para esperar tecla 1
    extension_transferencia = Column(String(50))  # Extensão para transferir
    cola_transferencia = Column(String(100))  # Fila para transferir
    
    # Configuração de voicemail - campos que faltavam
    detectar_voicemail = Column(Boolean, default=True)
    mensaje_voicemail_url = Column(String(500))
    duracion_minima_voicemail = Column(Integer, default=3)
    duracion_maxima_voicemail = Column(Integer, default=30)
    
    # Controle de discado
    llamadas_simultaneas = Column(Integer, default=5)  # Máximo de chamadas simultâneas
    tiempo_entre_llamadas = Column(Float, default=1.0)  # Segundos entre chamadas
    
    # Estados
    activa = Column(Boolean, default=False, index=True)
    pausada = Column(Boolean, default=False)
    
    # Metadados
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    fecha_inicio = Column(DateTime)  # Quando foi iniciada
    fecha_finalizacion = Column(DateTime)  # Quando foi finalizada
    
    # Notas/observações
    notas = Column(Text)
    
    # Relacionamentos
    llamadas = relationship("LlamadaPresione1", back_populates="campana", cascade="all, delete-orphan")


class LlamadaPresione1(Base):
    """
    Modelo para chamadas individuais de uma campanha Presione 1.
    """
    __tablename__ = "llamadas_presione1"
    
    # Campos principais
    id = Column(Integer, primary_key=True, index=True)
    campana_id = Column(Integer, ForeignKey("campanas_presione1.id"), nullable=False, index=True)
    
    # Dados da chamada
    numero_destino = Column(String(20), nullable=False)  # Nome correto no serviço
    numero_normalizado = Column(String(20), nullable=False, index=True)
    cli_utilizado = Column(String(20))  # Campo usado no serviço
    
    # Estados da chamada
    estado = Column(String(50), default="pendiente", index=True)
    resultado = Column(String(100))
    
    # Timestamps detalhados - conforme schema
    fecha_inicio = Column(DateTime)
    fecha_contestada = Column(DateTime)
    fecha_audio_inicio = Column(DateTime)
    fecha_dtmf_recibido = Column(DateTime)
    fecha_transferencia = Column(DateTime)
    fecha_fin = Column(DateTime)
    
    # Voicemail - campos que faltavam
    voicemail_detectado = Column(Boolean)
    fecha_voicemail_detectado = Column(DateTime)
    fecha_voicemail_audio_inicio = Column(DateTime)
    fecha_voicemail_audio_fin = Column(DateTime)
    duracion_mensaje_voicemail = Column(Integer)
    
    # Presione 1
    presiono_1 = Column(Boolean, default=False, index=True)
    dtmf_recibido = Column(String(10))
    tiempo_respuesta_dtmf = Column(Float)
    
    # Transferência
    transferencia_exitosa = Column(Boolean)  # Nome correto no serviço
    extension_destino = Column(String(50))
    resultado_transferencia = Column(String(100))
    
    # Durações
    duracion_total = Column(Integer)  # Em segundos
    duracion_conversacion = Column(Float)
    
    # Detalhes técnicos
    canal_asterisk = Column(String(100))
    call_id = Column(String(100), index=True)
    unique_id_asterisk = Column(String(100))  # Campo usado no serviço
    causa_finalizacion = Column(String(100))
    
    # Tentativas
    intento_numero = Column(Integer, default=1)
    
    # Notas
    notas = Column(Text)
    
    # Relacionamentos
    campana = relationship("CampanaPresione1", back_populates="llamadas") 