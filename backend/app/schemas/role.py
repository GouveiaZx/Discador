from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RoleBase(BaseModel):
    """Esquema base para roles"""
    nome: str = Field(..., description="Nome do role")
    descricao: Optional[str] = Field(None, description="Descrição do role")

class RoleCreate(RoleBase):
    """Esquema para criar um role"""
    pass

class Role(RoleBase):
    """Esquema para representar um role nas respostas API"""
    id: int = Field(..., description="ID único do role")
    
    class Config:
        from_attributes = True

class RolePermission(BaseModel):
    """Esquema para representar permissões de role"""
    id: int
    role_id: int
    permission: str
    resource: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserRoleBase(BaseModel):
    user_id: int
    role_id: int

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleOut(UserRoleBase):
    id: int
    assigned_at: Optional[datetime]

    class Config:
        from_attributes = True 