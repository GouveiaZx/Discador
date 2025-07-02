from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    # Contraseña hasheada
    password_hash = Column(String(255), nullable=False)
    
    # Estado del usuario
    activo = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_ultimo_acceso = Column(DateTime, nullable=True)
    
    # Roles y permisos
    es_administrador = Column(Boolean, default=False, nullable=False)
    es_integrador = Column(Boolean, default=False, nullable=False)
    
    # Configuraciones específicas
    max_llamadas_simultaneas = Column(Integer, default=1, nullable=False)
    puede_ver_estadisticas = Column(Boolean, default=True, nullable=False)
    puede_exportar_datos = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    # llamadas_asignadas = relationship("Llamada", back_populates="usuario")
    # roles = relationship("UserRole", back_populates="usuario")
    
    @property
    def tiene_permiso_llamadas(self) -> bool:
        """Verifica si el usuario tiene permisos para manejar llamadas"""
        return self.activo and (self.es_administrador or self.es_integrador)
    
    @property
    def tiene_permiso_administracion(self) -> bool:
        """Verifica si el usuario tiene permisos de administración"""
        return self.activo and self.es_administrador
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, username={self.username}, email={self.email})>" 