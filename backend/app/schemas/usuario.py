from pydantic import BaseModel, Field, UUID4, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any

class UsuarioBase(BaseModel):
    """Esquema base para usuarios"""
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    nombre: str = Field(..., description="Nombre del usuario")
    apellido: str = Field(..., description="Apellido del usuario")
    
class UsuarioCreate(UsuarioBase):
    """Esquema para crear un usuario nuevo"""
    password: str = Field(..., description="Contraseña del usuario (sin encriptar)")
    rol: str = Field("cliente", description="Rol del usuario: cliente, integrador, administrador")

class UsuarioInDB(UsuarioBase):
    """Esquema para representar un usuario en la base de datos"""
    id: UUID4 = Field(..., description="ID único del usuario")
    hashed_password: str = Field(..., description="Contraseña encriptada del usuario")
    rol: str = Field(..., description="Rol del usuario: cliente, integrador, administrador")
    activo: bool = Field(..., description="Indica si el usuario está activo")
    fecha_creacion: datetime = Field(..., description="Fecha de creación del usuario")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización del usuario")
    
    class Config:
        orm_mode = True

class Usuario(UsuarioBase):
    """Esquema para representar un usuario en las respuestas API"""
    id: UUID4 = Field(..., description="ID único del usuario")
    rol: str = Field(..., description="Rol del usuario: cliente, integrador, administrador")
    activo: bool = Field(..., description="Indica si el usuario está activo")
    
    class Config:
        orm_mode = True 