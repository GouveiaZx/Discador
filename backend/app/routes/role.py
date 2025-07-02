from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import obtener_sesion
from app.schemas.role import RoleCreate, RoleOut, UserRoleCreate, UserRoleOut
from app.services.role_service import RoleService
from typing import List, Optional

router = APIRouter(prefix="/roles", tags=["Roles"])

# Role
@router.post("/", response_model=RoleOut)
def create_role(role_in: RoleCreate, db: Session = Depends(obtener_sesion)):
    service = RoleService(db)
    return service.create_role(role_in)

@router.get("/", response_model=List[RoleOut])
def list_roles(db: Session = Depends(obtener_sesion)):
    service = RoleService(db)
    return service.list_roles()

@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: int, db: Session = Depends(obtener_sesion)):
    service = RoleService(db)
    role = service.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role não encontrado")
    return role

@router.delete("/{role_id}", response_model=bool)
def delete_role(role_id: int, db: Session = Depends(obtener_sesion)):
    service = RoleService(db)
    return service.delete_role(role_id)

# UserRole
@router.post("/assign/", response_model=UserRoleOut)
def assign_role(user_role_in: UserRoleCreate, db: Session = Depends(obtener_sesion)):
    service = RoleService(db)
    return service.assign_role(user_role_in)

@router.get("/user_roles/", response_model=List[UserRoleOut])
def list_user_roles(user_id: Optional[int] = None, db: Session = Depends(obtener_sesion)):
    service = RoleService(db)
    return service.list_user_roles(user_id)

@router.delete("/user_roles/{user_role_id}", response_model=bool)
def delete_user_role(user_role_id: int, db: Session = Depends(obtener_sesion)):
    service = RoleService(db)
    return service.delete_user_role(user_role_id) 