from sqlalchemy import Column, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base

class Usuario(Base):
    """
    Modelo para la tabla usuarios que almacena la informacion de los usuarios del sistema.
    """
    __tablename__ = "usuarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(100), nullable=False)
    rol = Column(String(20), nullable=False, default="cliente")  # cliente, integrador, administrador
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relaciones
    llamadas = relationship("Llamada", back_populates="usuario")
    
    # Indices adicionales
    __table_args__ = (
        Index('idx_usuarios_email', email),
        Index('idx_usuarios_rol', rol),
    )
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, rol={self.rol})>"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.nombre} {self.apellido}"
    
    @property
    def es_administrador(self):
        """Verifica si el usuario es administrador"""
        return self.rol == "administrador"
    
    @property
    def es_integrador(self):
        """Verifica si el usuario es integrador"""
        return self.rol == "integrador"
    
    @property
    def tiene_permiso_llamadas(self):
        """Verifica si el usuario tiene permiso para gestionar llamadas"""
        return self.rol in ["administrador", "integrador"] 