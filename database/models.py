"""
Models do banco de dados para o Sistema de Discador Preditivo
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum

# Enums para status
class CampaignStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ContactStatus(enum.Enum):
    NOT_STARTED = "not_started"
    CALLING = "calling"
    ANSWERED = "answered"
    PRESSED_1 = "pressed_1"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    REJECTED = "rejected"
    BLACKLISTED = "blacklisted"
    ERROR = "error"

class CallResult(enum.Enum):
    SUCCESS_PRESSED_1 = "success_pressed_1"
    SUCCESS_TRANSFERRED = "success_transferred"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    REJECTED = "rejected"
    HANGUP = "hangup"
    ERROR = "error"
    BLACKLISTED = "blacklisted"

# Models
class User(Base):
    """
    Usuários do sistema (opcional - preparado para autenticação futura)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Opcional por enquanto
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    campaigns = relationship("Campaign", back_populates="owner")

class Campaign(Base):
    """
    Campanhas de discagem
    """
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Configurações da campanha
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    cli_number = Column(String(20), nullable=False)  # Número origem (CLI)
    audio_url = Column(String(255), nullable=True)  # URL do áudio "Pressione 1"
    audio_file_path = Column(String(255), nullable=True)  # Caminho local do áudio
    
    # Horários
    start_time = Column(String(5), default="09:00")  # HH:MM
    end_time = Column(String(5), default="18:00")    # HH:MM
    timezone = Column(String(50), default="America/Argentina/Buenos_Aires")
    
    # Configurações avançadas
    max_attempts = Column(Integer, default=3)
    retry_interval = Column(Integer, default=30)  # minutos
    max_concurrent_calls = Column(Integer, default=5)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relacionamentos
    owner = relationship("User", back_populates="campaigns")
    contacts = relationship("Contact", back_populates="campaign", cascade="all, delete-orphan")
    call_logs = relationship("CallLog", back_populates="campaign")

class Contact(Base):
    """
    Contatos das campanhas (lista de números para discar)
    """
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    
    # Status e tentativas
    status = Column(Enum(ContactStatus), default=ContactStatus.NOT_STARTED)
    attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    
    # Dados adicionais do CSV
    extra_data = Column(Text, nullable=True)  # JSON com campos extras do CSV
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    
    # Relacionamentos
    campaign = relationship("Campaign", back_populates="contacts")
    call_logs = relationship("CallLog", back_populates="contact")

class Blacklist(Base):
    """
    Lista negra de números bloqueados
    """
    __tablename__ = "blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, unique=True, index=True)
    reason = Column(String(255), nullable=True)
    added_by = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CallLog(Base):
    """
    Logs detalhados de todas as chamadas realizadas
    """
    __tablename__ = "call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(50), unique=True, index=True)  # ID único da chamada no Asterisk
    
    # Dados básicos da chamada
    phone_number = Column(String(20), nullable=False, index=True)
    cli_number = Column(String(20), nullable=False)
    
    # Timestamps
    initiated_at = Column(DateTime(timezone=True), nullable=False)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Resultado da chamada
    result = Column(Enum(CallResult), nullable=True)
    dtmf_pressed = Column(String(10), nullable=True)  # Tecla pressionada
    duration_seconds = Column(Integer, default=0)
    
    # Detalhes técnicos
    asterisk_channel = Column(String(100), nullable=True)
    transfer_number = Column(String(20), nullable=True)  # Número para onde transferiu
    error_message = Column(Text, nullable=True)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    
    # Relacionamentos
    campaign = relationship("Campaign", back_populates="call_logs")
    contact = relationship("Contact", back_populates="call_logs") 