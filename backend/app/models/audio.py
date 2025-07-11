# Modelo de Audio
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from datetime import datetime
from . import Base

class Audio(Base):
    __tablename__ = "audios"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    tipo = Column(String(50), default="presione1")  # presione1, tts, gravacao, etc.
    duracao = Column(Float)  # em segundos
    tamanho = Column(Integer)  # em bytes
    formato = Column(String(10), default="wav")  # wav, mp3, etc.
    activo = Column(Boolean, default=True)
    usuario_id = Column(Integer, nullable=True)
    campana_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Audio(id={self.id}, titulo={self.titulo})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "filename": self.filename,
            "tipo": self.tipo,
            "duracao": self.duracao,
            "formato": self.formato,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 