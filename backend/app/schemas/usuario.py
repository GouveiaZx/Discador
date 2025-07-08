from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional, List, Dict, Any

class UsuarioBase(BaseModel):
    """Esquema base para usuarios"""
    email: str = Field(..., description="Correo electronico del usuario")
    nombre: str = Field(..., description="Nombre del usuario")
    apellido: str = Field(..., description="Apellido del usuario")
    
class UsuarioCreate(UsuarioBase):
    """Esquema para crear un usuario nuevo"""
    password: str = Field(..., description="Contrasena del usuario (sin encriptar)")
    rol: str = Field("cliente", description="Rol del usuario: cliente, integrador, administrador")

class UsuarioInDB(UsuarioBase):
    """Esquema para representar un usuario en la base de datos"""
    id: UUID4 = Field(..., description="ID unico del usuario")
    hashed_password: str = Field(..., description="Contrasena encriptada del usuario")
    rol: str = Field(..., description="Rol del usuario: cliente, integrador, administrador")
    activo: bool = Field(..., description="Indica si el usuario esta activo")
    fecha_creacion: datetime = Field(..., description="Fecha de creacion del usuario")
    fecha_actualizacion: datetime = Field(..., description="Fecha de ultima actualizacion del usuario")
    
    class Config:
        from_attributes = True

class Usuario(UsuarioBase):
    """Esquema para representar un usuario en las respuestas API"""
    id: UUID4 = Field(..., description="ID unico del usuario")
    rol: str = Field(..., description="Rol del usuario: cliente, integrador, administrador")
    activo: bool = Field(..., description="Indica si el usuario esta activo")
    
    class Config:
        from_attributes = True 