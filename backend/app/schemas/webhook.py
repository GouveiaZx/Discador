from pydantic import BaseModel, Field
from typing import Literal, Optional

# Estados validos para el webhook
ESTADOS_WEBHOOK_VALIDOS = Literal["en_progreso", "conectada", "finalizada", "fallida", "cancelada"]

class WebhookLlamadaRequest(BaseModel):
    """Esquema de solicitud para actualizar el estado de una llamada via webhook"""
    llamada_id: int = Field(
        ..., 
        description="ID de la llamada a actualizar", 
        example=123,
        gt=0
    )
    nuevo_estado: ESTADOS_WEBHOOK_VALIDOS = Field(
        ..., 
        description="Nuevo estado de la llamada", 
        example="fallida"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "llamada_id": 123,
                "nuevo_estado": "fallida"
            }
        }

class WebhookLlamadaResponse(BaseModel):
    """Esquema de respuesta para webhook de actualizacion de llamada"""
    mensaje: str = Field(
        ..., 
        description="Mensaje informativo sobre el resultado de la operacion",
        example="Estado de llamada actualizado"
    )
    estado_actual: str = Field(
        ..., 
        description="Estado actual de la llamada despues de la actualizacion",
        example="fallida"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "mensaje": "Estado de llamada actualizado",
                "estado_actual": "fallida"
            }
        }

class WebhookErrorResponse(BaseModel):
    """Esquema de respuesta para errores en webhook"""
    error: str = Field(
        ..., 
        description="Descripcion del error ocurrido",
        example="Llamada no encontrada o API Key invalida"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "La llamada con ID 123 no existe"
            }
        } 
