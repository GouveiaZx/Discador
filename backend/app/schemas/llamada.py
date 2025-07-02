from pydantic import BaseModel, Field, UUID4, validator
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal

class LlamadaBase(BaseModel):
    """Esquema base para llamadas"""
    numero_destino: str = Field(..., description="Numero de telefono al que se realizara la llamada")
    
class LlamadaProximaResponse(BaseModel):
    """Esquema de respuesta para la ruta de proxima llamada"""
    mensaje: str = Field(..., description="Mensaje informativo sobre el resultado de la operacion")
    llamada_id: int = Field(..., description="ID de la llamada asignada")
    numero_destino: str = Field(..., description="Numero de telefono de la llamada asignada")
    estado: str = Field(..., description="Estado de la llamada")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mensaje": "Llamada asignada correctamente",
                "llamada_id": 123,
                "numero_destino": "+5491112345678",
                "estado": "en_progreso"
            }
        }

class LlamadaNoDisponibleResponse(BaseModel):
    """Esquema de respuesta cuando no hay llamadas disponibles"""
    mensaje: str = Field(..., description="Mensaje informativo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mensaje": "No hay llamadas pendientes para asignar"
            }
        }

class ErrorResponse(BaseModel):
    """Esquema para respuestas de error"""
    error: str = Field(..., description="Mensaje de error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "No tienes permisos para acceder a este recurso"
            }
        }

class FinalizarLlamadaRequest(BaseModel):
    """Esquema para finalizar una llamada"""
    llamada_id: int = Field(..., description="ID de la llamada a finalizar")
    resultado: Literal["contestada", "no_contesta", "buzon", "numero_invalido", "otro"] = Field(
        ..., 
        description="Resultado de la llamada"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "llamada_id": 123,
                "resultado": "contestada"
            }
        }

class FinalizarLlamadaResponse(BaseModel):
    """Esquema de respuesta para la finalizacion de una llamada"""
    mensaje: str = Field(..., description="Mensaje informativo sobre el resultado de la operacion")
    llamada_id: int = Field(..., description="ID de la llamada finalizada")
    estado: str = Field(..., description="Estado de la llamada")
    resultado: str = Field(..., description="Resultado de la llamada")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mensaje": "Llamada finalizada correctamente",
                "llamada_id": 123,
                "estado": "finalizada",
                "resultado": "contestada"
            }
        } 
