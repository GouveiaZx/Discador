from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import obtener_sesion
from app.schemas.trunk import TrunkCreate, TrunkUpdate, TrunkOut
from app.services.trunk_service import TrunkService
from typing import List

router = APIRouter(prefix="/trunks", tags=["Trunks"])

@router.post("/", response_model=TrunkOut)
def create_trunk(trunk_in: TrunkCreate, db: Session = Depends(obtener_sesion)):
    service = TrunkService(db)
    return service.create_trunk(trunk_in)

@router.get("/", response_model=List[TrunkOut])
def list_trunks(db: Session = Depends(obtener_sesion)):
    service = TrunkService(db)
    return service.list_trunks()

@router.get("/{trunk_id}", response_model=TrunkOut)
def get_trunk(trunk_id: int, db: Session = Depends(obtener_sesion)):
    service = TrunkService(db)
    trunk = service.get_trunk(trunk_id)
    if not trunk:
        raise HTTPException(status_code=404, detail="Trunk não encontrado")
    return trunk

@router.put("/{trunk_id}", response_model=TrunkOut)
def update_trunk(trunk_id: int, trunk_in: TrunkUpdate, db: Session = Depends(obtener_sesion)):
    service = TrunkService(db)
    trunk = service.update_trunk(trunk_id, trunk_in)
    if not trunk:
        raise HTTPException(status_code=404, detail="Trunk não encontrado")
    return trunk

@router.delete("/{trunk_id}", response_model=bool)
def delete_trunk(trunk_id: int, db: Session = Depends(obtener_sesion)):
    service = TrunkService(db)
    return service.delete_trunk(trunk_id) 