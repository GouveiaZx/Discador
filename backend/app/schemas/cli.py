"""
Schemas para manejo de CLIs (Caller Line Identification).
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.schemas.lista_llamadas import validar_numero_telefone


class CliBase(BaseModel):
    """Schema base para CLI."""
    numero: str = Field(..., description="Numero de telefono CLI")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripcion del CLI")
    notas: Optional[str] = Field(None, description="Notas adicionales sobre el CLI")


class CliCreate(CliBase):
    """Schema para crear CLI."""
    
    @validator('numero')
    def validar_numero_telefone_field(cls, v):
        """Valida que el numero sea valido."""
        validacion = validar_numero_telefone(v)
        if not validacion.valido:
            raise ValueError(f"Numero CLI invalido: {validacion.motivo_invalido}")
        return validacion.numero_normalizado


class CliUpdate(BaseModel):
    """Schema para actualizar CLI."""
    descripcion: Optional[str] = Field(None, max_length=255)
    notas: Optional[str] = Field(None)
    activo: Optional[bool] = Field(None, description="Si el CLI esta activo")


class CliResponse(CliBase):
    """Schema para respuesta de CLI."""
    id: int = Field(..., description="ID unico del CLI")
    numero_normalizado: str = Field(..., description="Numero normalizado")
    activo: bool = Field(..., description="Si el CLI esta activo")
    veces_usado: int = Field(..., description="Veces que se ha usado este CLI")
    ultima_vez_usado: Optional[datetime] = Field(None, description="Ultima vez que se uso")
    fecha_creacion: datetime = Field(..., description="Fecha de creacion")
    fecha_actualizacion: datetime = Field(..., description="Fecha de ultima actualizacion")
    
    class Config:
        from_attributes = True


class CliBulkAddRequest(BaseModel):
    """Schema para agregar multiples CLIs."""
    numeros: List[str] = Field(..., description="Lista de numeros CLI a agregar")
    descripcion: Optional[str] = Field(None, description="Descripcion comun para todos los CLIs")


class CliBulkAddResponse(BaseModel):
    """Schema para respuesta de agregado masivo de CLIs."""
    mensaje: str = Field(..., description="Mensaje de resultado")
    clis_agregados: int = Field(..., description="Cantidad de CLIs agregados exitosamente")
    clis_duplicados: int = Field(..., description="CLIs que ya existian")
    clis_invalidos: int = Field(..., description="CLIs invalidos encontrados")
    errores: List[str] = Field([], description="Lista de errores encontrados")


class CliStatsResponse(BaseModel):
    """Schema para estadisticas de CLIs."""
    total_clis: int = Field(..., description="Total de CLIs registrados")
    clis_activos: int = Field(..., description="CLIs activos")
    clis_inactivos: int = Field(..., description="CLIs inactivos")
    cli_mas_usado: Optional[str] = Field(None, description="CLI mas usado")
    total_usos_hoy: int = Field(..., description="Total de usos hoy")
    total_usos_mes: int = Field(..., description="Total de usos este mes")


class CliRandomRequest(BaseModel):
    """Schema para solicitar CLI aleatorio."""
    excluir_cli: Optional[str] = Field(None, description="CLI a excluir de la seleccion")
    solo_poco_usados: Optional[bool] = Field(False, description="Preferir CLIs menos usados")


class CliRandomResponse(BaseModel):
    """Schema para respuesta de CLI aleatorio."""
    cli_seleccionado: str = Field(..., description="CLI seleccionado")
    cli_id: int = Field(..., description="ID del CLI seleccionado")
    veces_usado: int = Field(..., description="Veces que se ha usado este CLI")
    mensaje: str = Field(..., description="Mensaje informativo") 
