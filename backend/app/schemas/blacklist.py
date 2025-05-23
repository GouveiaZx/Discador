"""
Schemas para manejo de blacklist/lista negra.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.schemas.lista_llamadas import validar_numero_telefono


class BlacklistBase(BaseModel):
    """Schema base para blacklist."""
    numero: str = Field(..., description="Número de teléfono a bloquear")
    motivo: Optional[str] = Field(None, max_length=255, description="Motivo del bloqueo")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    creado_por: Optional[str] = Field(None, max_length=100, description="Usuario que creó el registro")


class BlacklistCreate(BlacklistBase):
    """Schema para crear entrada en blacklist."""
    
    @validator('numero')
    def validar_numero_telefono_field(cls, v):
        """Valida que el número sea válido."""
        validacion = validar_numero_telefono(v)
        if not validacion.valido:
            raise ValueError(f"Número inválido: {validacion.motivo_invalido}")
        return validacion.numero_normalizado


class BlacklistUpdate(BaseModel):
    """Schema para actualizar entrada en blacklist."""
    motivo: Optional[str] = Field(None, max_length=255)
    observaciones: Optional[str] = Field(None)
    activo: Optional[bool] = Field(None, description="Si el bloqueo está activo")


class BlacklistResponse(BlacklistBase):
    """Schema para respuesta de blacklist."""
    id: int = Field(..., description="ID único del registro")
    numero_normalizado: str = Field(..., description="Número normalizado")
    activo: bool = Field(..., description="Si el bloqueo está activo")
    veces_bloqueado: int = Field(..., description="Veces que se ha bloqueado este número")
    ultima_vez_bloqueado: Optional[datetime] = Field(None, description="Última vez que se intentó llamar")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")
    
    class Config:
        from_attributes = True


class BlacklistVerificationRequest(BaseModel):
    """Schema para verificar si un número está en blacklist."""
    numero: str = Field(..., description="Número a verificar")


class BlacklistVerificationResponse(BaseModel):
    """Schema para respuesta de verificación de blacklist."""
    numero_original: str = Field(..., description="Número original consultado")
    numero_normalizado: str = Field(..., description="Número normalizado")
    en_blacklist: bool = Field(..., description="Si el número está en blacklist")
    motivo: Optional[str] = Field(None, description="Motivo del bloqueo si aplica")
    fecha_bloqueo: Optional[datetime] = Field(None, description="Fecha del bloqueo si aplica")


class BlacklistBulkAddRequest(BaseModel):
    """Schema para agregar múltiples números a blacklist."""
    numeros: List[str] = Field(..., description="Lista de números a bloquear")
    motivo: Optional[str] = Field(None, description="Motivo común para todos los números")
    creado_por: Optional[str] = Field(None, description="Usuario que agrega los números")


class BlacklistBulkAddResponse(BaseModel):
    """Schema para respuesta de agregado masivo a blacklist."""
    mensaje: str = Field(..., description="Mensaje de resultado")
    numeros_agregados: int = Field(..., description="Cantidad de números agregados exitosamente")
    numeros_duplicados: int = Field(..., description="Números que ya estaban en blacklist")
    numeros_invalidos: int = Field(..., description="Números inválidos encontrados")
    errores: List[str] = Field([], description="Lista de errores encontrados")


class BlacklistStatsResponse(BaseModel):
    """Schema para estadísticas de blacklist."""
    total_numeros: int = Field(..., description="Total de números en blacklist")
    numeros_activos: int = Field(..., description="Números activos en blacklist")
    numeros_inactivos: int = Field(..., description="Números inactivos en blacklist")
    total_bloqueos_hoy: int = Field(..., description="Total de bloqueos realizados hoy")
    total_bloqueos_mes: int = Field(..., description="Total de bloqueos realizados este mes")
    numero_mas_bloqueado: Optional[str] = Field(None, description="Número más veces bloqueado")


class BlacklistSearchRequest(BaseModel):
    """Schema para búsqueda en blacklist."""
    numero: Optional[str] = Field(None, description="Buscar por número")
    motivo: Optional[str] = Field(None, description="Buscar por motivo")
    creado_por: Optional[str] = Field(None, description="Buscar por creador")
    activo: Optional[bool] = Field(None, description="Filtrar por estado activo")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha de creación desde")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha de creación hasta") 