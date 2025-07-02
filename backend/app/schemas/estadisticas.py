from pydantic import BaseModel, Field
from typing import Dict, Optional

class EstadisticasLlamadasResponse(BaseModel):
    """Esquema de respuesta para estadisticas de llamadas"""
    total_llamadas: int = Field(
        ..., 
        description="Cantidad total de llamadas en el sistema",
        example=132
    )
    por_estado: Dict[str, int] = Field(
        ..., 
        description="Cantidad de llamadas agrupadas por estado",
        example={
            "pendiente": 12,
            "en_progreso": 15,
            "conectada": 20,
            "finalizada": 85
        }
    )
    por_resultado: Dict[str, int] = Field(
        ..., 
        description="Cantidad de llamadas agrupadas por resultado",
        example={
            "contestada": 40,
            "no_contesta": 30,
            "buzon": 10,
            "numero_invalido": 5,
            "otro": 0
        }
    )
    en_progreso_por_usuario: Dict[str, int] = Field(
        ..., 
        description="Cantidad de llamadas en progreso agrupadas por correo electronico del usuario",
        example={
            "integrador1@example.com": 2,
            "integrador2@example.com": 3
        }
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_llamadas": 132,
                "por_estado": {
                    "pendiente": 12,
                    "en_progreso": 15,
                    "conectada": 20,
                    "finalizada": 85
                },
                "por_resultado": {
                    "contestada": 40,
                    "no_contesta": 30,
                    "buzon": 10,
                    "numero_invalido": 5,
                    "otro": 0
                },
                "en_progreso_por_usuario": {
                    "integrador1@example.com": 2,
                    "integrador2@example.com": 3
                }
            }
        } 
