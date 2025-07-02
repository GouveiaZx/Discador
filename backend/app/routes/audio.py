from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import obtener_sesion
from app.schemas.audio import AudioCreate, AudioUpdate, AudioOut
from app.services.audio_service import AudioService
from typing import List, Optional

router = APIRouter(prefix="/audios", tags=["Audios"])

@router.post("/", response_model=AudioOut)
def create_audio(audio_in: AudioCreate, db: Session = Depends(obtener_sesion)):
    service = AudioService(db)
    return service.create_audio(audio_in)

@router.get("/", response_model=List[AudioOut])
def list_audios(campaign_id: Optional[int] = None, db: Session = Depends(obtener_sesion)):
    service = AudioService(db)
    return service.list_audios(campaign_id)

@router.get("/{audio_id}", response_model=AudioOut)
def get_audio(audio_id: int, db: Session = Depends(obtener_sesion)):
    service = AudioService(db)
    audio = service.get_audio(audio_id)
    if not audio:
        raise HTTPException(status_code=404, detail="Áudio não encontrado")
    return audio

@router.put("/{audio_id}", response_model=AudioOut)
def update_audio(audio_id: int, audio_in: AudioUpdate, db: Session = Depends(obtener_sesion)):
    service = AudioService(db)
    audio = service.update_audio(audio_id, audio_in)
    if not audio:
        raise HTTPException(status_code=404, detail="Áudio não encontrado")
    return audio

@router.delete("/{audio_id}", response_model=bool)
def delete_audio(audio_id: int, db: Session = Depends(obtener_sesion)):
    service = AudioService(db)
    return service.delete_audio(audio_id) 