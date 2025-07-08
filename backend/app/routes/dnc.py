from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import obtener_sesion
from app.schemas.dnc import DNCListCreate, DNCListOut, DNCNumberCreate, DNCNumberOut
from app.services.dnc_service import DNCService
from typing import List

router = APIRouter(prefix="/dnc", tags=["DNC"])

# DNCList
@router.post("/lists/", response_model=DNCListOut)
def create_dnc_list(dnc_list_in: DNCListCreate, db: Session = Depends(obtener_sesion)):
    service = DNCService(db)
    return service.create_dnc_list(dnc_list_in)

@router.get("/lists/", response_model=List[DNCListOut])
def list_dnc_lists(db: Session = Depends(obtener_sesion)):
    service = DNCService(db)
    return service.list_dnc_lists()

@router.get("/lists/{dnc_list_id}", response_model=DNCListOut)
def get_dnc_list(dnc_list_id: int, db: Session = Depends(obtener_sesion)):
    service = DNCService(db)
    dnc_list = service.get_dnc_list(dnc_list_id)
    if not dnc_list:
        raise HTTPException(status_code=404, detail="Lista DNC não encontrada")
    return dnc_list

@router.delete("/lists/{dnc_list_id}", response_model=bool)
def delete_dnc_list(dnc_list_id: int, db: Session = Depends(obtener_sesion)):
    service = DNCService(db)
    return service.delete_dnc_list(dnc_list_id)

# DNCNumber
@router.post("/lists/{dnc_list_id}/numbers/", response_model=DNCNumberOut)
def add_dnc_number(dnc_list_id: int, dnc_number_in: DNCNumberCreate, db: Session = Depends(obtener_sesion)):
    service = DNCService(db)
    return service.add_dnc_number(dnc_list_id, dnc_number_in)

@router.get("/lists/{dnc_list_id}/numbers/", response_model=List[DNCNumberOut])
def list_dnc_numbers(dnc_list_id: int, db: Session = Depends(obtener_sesion)):
    service = DNCService(db)
    return service.list_dnc_numbers(dnc_list_id)

@router.delete("/numbers/{dnc_number_id}", response_model=bool)
def delete_dnc_number(dnc_number_id: int, db: Session = Depends(obtener_sesion)):
    service = DNCService(db)
    return service.delete_dnc_number(dnc_number_id) 