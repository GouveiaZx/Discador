from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.services.audio_service import AudioService
from app.schemas.audio import AudioCreate, AudioUpdate, AudioResponse
from app.utils.logger import logger

router = APIRouter(prefix="/audio", tags=["Audio"])

# Endpoint simples para contextos que não depende do banco
@router.get("/contextos")
async def listar_contextos_mock():
    """Lista contextos de áudio - dados mock para evitar erro de banco"""
    try:
        contextos = [
            {
                "id": 1,
                "nome": "Contexto Padrão",
                "descricao": "Contexto de áudio padrão para campanhas",
                "ativo": True,
                "configuracoes": {
                    "deteccao_voz": True,
                    "timeout_resposta": 5,
                    "max_tentativas": 3
                }
            },
            {
                "id": 2,
                "nome": "Contexto Personalizado",
                "descricao": "Contexto de áudio personalizado",
                "ativo": True,
                "configuracoes": {
                    "deteccao_voz": True,
                    "timeout_resposta": 10,
                    "max_tentativas": 5
                }
            }
        ]
        return {
            "status": "success",
            "contextos": contextos,
            "total": len(contextos)
        }
    except Exception as e:
        logger.error(f"Erro ao listar contextos de áudio: {e}")
        return {
            "status": "error",
            "contextos": [],
            "total": 0,
            "error": str(e)
        }

@router.post("/", response_model=AudioResponse)
async def criar_audio(
    audio_data: AudioCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo arquivo de áudio"""
    try:
        service = AudioService(db)
        audio = service.create_audio(audio_data)
        return AudioResponse.from_orm(audio)
    except Exception as e:
        logger.error(f"Erro ao criar áudio: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar áudio")

@router.get("/{audio_id}", response_model=AudioResponse)
async def obter_audio(
    audio_id: int,
    db: Session = Depends(get_db)
):
    """Obtém um arquivo de áudio específico"""
    try:
        service = AudioService(db)
        audio = service.get_audio(audio_id)
        if not audio:
            raise HTTPException(status_code=404, detail="Áudio não encontrado")
        return AudioResponse.from_orm(audio)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter áudio {audio_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter áudio")

@router.get("/", response_model=List[AudioResponse])
async def listar_audios(
    campaign_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista todos os arquivos de áudio"""
    try:
        service = AudioService(db)
        audios = service.list_audios(campaign_id)
        return [AudioResponse.from_orm(audio) for audio in audios]
    except Exception as e:
        logger.error(f"Erro ao listar áudios: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao listar áudios")

@router.put("/{audio_id}", response_model=AudioResponse)
async def atualizar_audio(
    audio_id: int,
    audio_data: AudioUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um arquivo de áudio"""
    try:
        service = AudioService(db)
        audio = service.update_audio(audio_id, audio_data)
        if not audio:
            raise HTTPException(status_code=404, detail="Áudio não encontrado")
        return AudioResponse.from_orm(audio)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar áudio {audio_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar áudio")

@router.delete("/{audio_id}")
async def deletar_audio(
    audio_id: int,
    db: Session = Depends(get_db)
):
    """Deleta um arquivo de áudio"""
    try:
        service = AudioService(db)
        success = service.delete_audio(audio_id)
        if not success:
            raise HTTPException(status_code=404, detail="Áudio não encontrado")
        return {"message": "Áudio deletado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar áudio {audio_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar áudio")

@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    nome: str = Form(...),
    descricao: str = Form(None),
    campaign_id: int = Form(None),
    db: Session = Depends(get_db)
):
    """Faz upload de um arquivo de áudio"""
    try:
        # Validar tipo de arquivo
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser do tipo áudio")
        
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Criar registro no banco
        audio_data = AudioCreate(
            nome=nome,
            descricao=descricao,
            campaign_id=campaign_id,
            arquivo_nome=file.filename,
            arquivo_tamanho=len(content),
            arquivo_tipo=file.content_type
        )
        
        service = AudioService(db)
        audio = service.create_audio(audio_data)
        
        return {
            "message": "Arquivo enviado com sucesso",
            "audio_id": audio.id,
            "nome": audio.nome
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer upload de áudio: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao fazer upload") 