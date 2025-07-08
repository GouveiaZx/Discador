from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import re

class ContactBase(BaseModel):
    """Schema base para contatos."""
    nome: Optional[str] = Field(None, max_length=100, description="Nome do contato")
    telefone: str = Field(..., description="Número de telefone")
    email: Optional[str] = Field(None, description="Email do contato")
    empresa: Optional[str] = Field(None, max_length=100, description="Empresa")
    notas: Optional[str] = Field(None, description="Notas adicionais")

class ContactCreate(ContactBase):
    """Schema para criar um contato."""
    pass

class ContactResponse(ContactBase):
    """Schema para resposta de contato."""
    id: int = Field(..., description="ID único do contato")
    telefone_normalizado: str = Field(..., description="Telefone normalizado")
    valido: bool = Field(True, description="Se o telefone é válido")
    pais_detectado: Optional[str] = Field(None, description="País detectado")
    fecha_creacion: datetime = Field(..., description="Data de criação")
    fecha_actualizacion: datetime = Field(..., description="Data de atualização")

    class Config:
        from_attributes = True

class ContactsUploadResponse(BaseModel):
    """Schema para resposta do upload de contatos."""
    mensaje: str = Field(..., description="Mensagem de resultado")
    archivo_original: str = Field(..., description="Nome do arquivo processado")
    total_lineas_archivo: int = Field(..., description="Total de linhas no arquivo")
    contatos_validos: int = Field(..., description="Contatos válidos salvos")
    contatos_invalidos: int = Field(..., description="Contatos inválidos encontrados")
    contatos_duplicados: int = Field(..., description="Contatos duplicados removidos")
    errores: List[str] = Field([], description="Lista de erros encontrados")

class ContactValidation(BaseModel):
    """Schema para validação de contatos."""
    telefone_original: str
    telefone_normalizado: str
    valido: bool
    motivo_invalido: Optional[str] = None
    pais_detectado: Optional[str] = None
    es_toll_free: Optional[bool] = None
    es_wireless: Optional[bool] = None 