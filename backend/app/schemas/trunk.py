from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TrunkBase(BaseModel):
    """Esquema base para trunks"""
    nome: str = Field(..., description="Nome do trunk")
    host: str = Field(..., description="Host do trunk")
    porta: int = Field(..., description="Porta do trunk")
    usuario: str = Field(..., description="Usuario do trunk")
    senha: str = Field(..., description="Senha do trunk")
    ativo: bool = Field(True, description="Indica se o trunk esta ativo")

class TrunkCreate(TrunkBase):
    """Esquema para criar um trunk novo"""
    pass

class TrunkUpdate(BaseModel):
    """Esquema para atualizar um trunk"""
    nome: Optional[str] = None
    host: Optional[str] = None
    porta: Optional[int] = None
    usuario: Optional[str] = None
    senha: Optional[str] = None
    ativo: Optional[bool] = None

class Trunk(TrunkBase):
    """Esquema para representar um trunk nas respostas API"""
    id: int = Field(..., description="ID único do trunk")
    
    class Config:
        from_attributes = True 