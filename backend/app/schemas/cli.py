"""
Schemas para manejo de CLIs (Caller Line Identification).
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.schemas.lista_llamadas import validar_numero_telefono


class CliBase(BaseModel):
    """Schema base para CLI."""
    numero: str = Field(..., description="Número de teléfono CLI")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción del CLI")
    notas: Optional[str] = Field(None, description="Notas adicionales sobre el CLI")


class CliCreate(CliBase):
    """Schema para crear CLI."""
    
    @validator('numero')
    def validar_numero_telefono_field(cls, v):
        """Valida que el número sea válido."""
        validacion = validar_numero_telefono(v)
        if not validacion.valido:
            raise ValueError(f"Número CLI inválido: {validacion.motivo_invalido}")
        return validacion.numero_normalizado


class CliUpdate(BaseModel):
    """Schema para actualizar CLI."""
    descripcion: Optional[str] = Field(None, max_length=255)
    notas: Optional[str] = Field(None)
    activo: Optional[bool] = Field(None, description="Si el CLI está activo")


class CliResponse(CliBase):
    """Schema para respuesta de CLI."""
    id: int = Field(..., description="ID único del CLI")
    numero_normalizado: str = Field(..., description="Número normalizado")
    activo: bool = Field(..., description="Si el CLI está activo")
    veces_usado: int = Field(..., description="Veces que se ha usado este CLI")
    ultima_vez_usado: Optional[datetime] = Field(None, description="Última vez que se usó")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")
    
    class Config:
        from_attributes = True


class CliBulkAddRequest(BaseModel):
    """Schema para agregar múltiples CLIs."""
    numeros: List[str] = Field(..., description="Lista de números CLI a agregar")
    descripcion: Optional[str] = Field(None, description="Descripción común para todos los CLIs")


class CliBulkAddResponse(BaseModel):
    """Schema para respuesta de agregado masivo de CLIs."""
    mensaje: str = Field(..., description="Mensaje de resultado")
    clis_agregados: int = Field(..., description="Cantidad de CLIs agregados exitosamente")
    clis_duplicados: int = Field(..., description="CLIs que ya existían")
    clis_invalidos: int = Field(..., description="CLIs inválidos encontrados")
    errores: List[str] = Field([], description="Lista de errores encontrados")


class CliStatsResponse(BaseModel):
    """Schema para estadísticas de CLIs."""
    total_clis: int = Field(..., description="Total de CLIs registrados")
    clis_activos: int = Field(..., description="CLIs activos")
    clis_inactivos: int = Field(..., description="CLIs inactivos")
    cli_mas_usado: Optional[str] = Field(None, description="CLI más usado")
    total_usos_hoy: int = Field(..., description="Total de usos hoy")
    total_usos_mes: int = Field(..., description="Total de usos este mes")


class CliRandomRequest(BaseModel):
    """Schema para solicitar CLI aleatorio."""
    excluir_cli: Optional[str] = Field(None, description="CLI a excluir de la selección")
    solo_poco_usados: Optional[bool] = Field(False, description="Preferir CLIs menos usados")


class CliRandomResponse(BaseModel):
    """Schema para respuesta de CLI aleatorio."""
    cli_seleccionado: str = Field(..., description="CLI seleccionado")
    cli_id: int = Field(..., description="ID del CLI seleccionado")
    veces_usado: int = Field(..., description="Veces que se ha usado este CLI")
    mensaje: str = Field(..., description="Mensaje informativo") 