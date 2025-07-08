"""
Schemas para manejo de blacklist/lista negra.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.schemas.lista_llamadas import validar_numero_telefone


class BlacklistBase(BaseModel):
    """Schema base para blacklist."""
    numero: str = Field(..., description="Numero de telefono a bloquear")
    motivo: Optional[str] = Field(None, max_length=255, description="Motivo del bloqueo")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    creado_por: Optional[str] = Field(None, max_length=100, description="Usuario que creo el registro")


class BlacklistCreate(BlacklistBase):
    """Schema para crear entrada en blacklist."""
    
    @validator('numero')
    def validar_numero_telefono_field(cls, v):
        """Valida que el numero sea valido."""
        validacion = validar_numero_telefone(v)
        if not validacion.valido:
            raise ValueError(f"Numero invalido: {validacion.motivo_invalido}")
        return validacion.numero_normalizado


class BlacklistUpdate(BaseModel):
    """Schema para actualizar entrada en blacklist."""
    motivo: Optional[str] = Field(None, max_length=255)
    observaciones: Optional[str] = Field(None)
    activo: Optional[bool] = Field(None, description="Si el bloqueo esta activo")


class BlacklistResponse(BlacklistBase):
    """Schema para respuesta de blacklist."""
    id: int = Field(..., description="ID unico del registro")
    numero_normalizado: str = Field(..., description="Numero normalizado")
    activo: bool = Field(..., description="Si el bloqueo esta activo")
    veces_bloqueado: int = Field(..., description="Veces que se ha bloqueado este numero")
    ultima_vez_bloqueado: Optional[datetime] = Field(None, description="Ultima vez que se intento llamar")
    fecha_creacion: datetime = Field(..., description="Fecha de creacion")
    fecha_actualizacion: datetime = Field(..., description="Fecha de ultima actualizacion")
    
    class Config:
        from_attributes = True


class BlacklistVerificationRequest(BaseModel):
    """Schema para verificar si un numero esta en blacklist."""
    numero: str = Field(..., description="Numero a verificar")


class BlacklistVerificationResponse(BaseModel):
    """Schema para respuesta de verificacion de blacklist."""
    numero_original: str = Field(..., description="Numero original consultado")
    numero_normalizado: str = Field(..., description="Numero normalizado")
    en_blacklist: bool = Field(..., description="Si el numero esta en blacklist")
    motivo: Optional[str] = Field(None, description="Motivo del bloqueo si aplica")
    fecha_bloqueo: Optional[datetime] = Field(None, description="Fecha del bloqueo si aplica")


class BlacklistBulkAddRequest(BaseModel):
    """Schema para agregar multiples numeros a blacklist."""
    numeros: List[str] = Field(..., description="Lista de numeros a bloquear")
    motivo: Optional[str] = Field(None, description="Motivo comun para todos los numeros")
    creado_por: Optional[str] = Field(None, description="Usuario que agrega los numeros")


class BlacklistBulkAddResponse(BaseModel):
    """Schema para respuesta de agregado masivo a blacklist."""
    mensaje: str = Field(..., description="Mensaje de resultado")
    numeros_agregados: int = Field(..., description="Cantidad de numeros agregados exitosamente")
    numeros_duplicados: int = Field(..., description="Numeros que ya estaban en blacklist")
    numeros_invalidos: int = Field(..., description="Numeros invalidos encontrados")
    errores: List[str] = Field([], description="Lista de errores encontrados")


class BlacklistStatsResponse(BaseModel):
    """Schema para estadisticas de blacklist."""
    total_numeros: int = Field(..., description="Total de numeros en blacklist")
    numeros_activos: int = Field(..., description="Numeros activos en blacklist")
    numeros_inactivos: int = Field(..., description="Numeros inactivos en blacklist")
    total_bloqueos_hoy: int = Field(..., description="Total de bloqueos realizados hoy")
    total_bloqueos_mes: int = Field(..., description="Total de bloqueos realizados este mes")
    numero_mas_bloqueado: Optional[str] = Field(None, description="Numero mas veces bloqueado")


class BlacklistSearchRequest(BaseModel):
    """Schema para busqueda en blacklist."""
    numero: Optional[str] = Field(None, description="Buscar por numero")
    motivo: Optional[str] = Field(None, description="Buscar por motivo")
    creado_por: Optional[str] = Field(None, description="Buscar por creador")
    activo: Optional[bool] = Field(None, description="Filtrar por estado activo")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha de creacion desde")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha de creacion hasta") 