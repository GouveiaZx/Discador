from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import shutil
from datetime import datetime
import wave
import asyncio
from pydub import AudioSegment
from pydub.utils import which
import json

from ..database import get_db
from ..services.audio_service import AudioService
from ..models.audio_models import AudioFile, AudioFileCreate, AudioFileUpdate

router = APIRouter()

# Configurações de áudio
AUDIO_UPLOAD_DIR = "uploads/audio"
ALLOWED_FORMATS = ["wav", "mp3", "m4a", "aac", "flac"]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Garantir que o diretório existe
os.makedirs(AUDIO_UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=dict)
async def upload_audio(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    description: Optional[str] = None,
    campaign_id: Optional[int] = None,
    audio_type: str = "greeting",  # greeting, ivr, hold_music, etc.
    db=Depends(get_db)
):
    """
    Upload de arquivo de áudio com conversão automática para WAV
    """
    try:
        # Validar formato do arquivo
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ALLOWED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato não suportado. Use: {', '.join(ALLOWED_FORMATS)}"
            )
        
        # Validar tamanho do arquivo
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande. Máximo: {MAX_FILE_SIZE/1024/1024:.1f}MB"
            )
        
        # Gerar nome único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = name or file.filename.split('.')[0]
        safe_name = "".join(c for c in original_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        # Salvar arquivo temporário
        temp_filename = f"{safe_name}_{timestamp}.{file_extension}"
        temp_path = os.path.join(AUDIO_UPLOAD_DIR, temp_filename)
        
        with open(temp_path, "wb") as temp_file:
            temp_file.write(content)
        
        # Converter para WAV se necessário
        final_filename = f"{safe_name}_{timestamp}.wav"
        final_path = os.path.join(AUDIO_UPLOAD_DIR, final_filename)
        
        if file_extension != "wav":
            # Converter usando pydub
            audio = AudioSegment.from_file(temp_path)
            audio = audio.set_channels(1)  # Mono
            audio = audio.set_frame_rate(8000)  # 8kHz para telefonia
            audio.export(final_path, format="wav")
            
            # Remover arquivo temporário
            os.remove(temp_path)
        else:
            # Apenas mover o arquivo WAV
            shutil.move(temp_path, final_path)
        
        # Analisar propriedades do áudio
        audio_info = await AudioService.analyze_audio(final_path)
        
        # Salvar no banco de dados
        audio_data = AudioFileCreate(
            filename=final_filename,
            original_name=file.filename,
            display_name=safe_name,
            description=description,
            file_path=final_path,
            file_size=os.path.getsize(final_path),
            duration=audio_info.get("duration", 0),
            sample_rate=audio_info.get("sample_rate", 8000),
            channels=audio_info.get("channels", 1),
            format="wav",
            campaign_id=campaign_id,
            audio_type=audio_type
        )
        
        audio_file = await AudioService.create_audio_file(db, audio_data)
        
        return {
            "success": True,
            "message": "Arquivo de áudio enviado com sucesso",
            "audio_file": {
                "id": audio_file.id,
                "filename": audio_file.filename,
                "display_name": audio_file.display_name,
                "duration": audio_file.duration,
                "size": audio_file.file_size,
                "type": audio_file.audio_type
            }
        }
        
    except Exception as e:
        # Limpar arquivo em caso de erro
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        if 'final_path' in locals() and os.path.exists(final_path):
            os.remove(final_path)
        
        raise HTTPException(status_code=500, detail=f"Erro ao processar áudio: {str(e)}")

@router.get("/list", response_model=List[dict])
async def list_audio_files(
    campaign_id: Optional[int] = None,
    audio_type: Optional[str] = None,
    db=Depends(get_db)
):
    """
    Listar arquivos de áudio com filtros
    """
    try:
        audio_files = await AudioService.get_audio_files(db, campaign_id, audio_type)
        
        return [
            {
                "id": audio.id,
                "filename": audio.filename,
                "display_name": audio.display_name,
                "description": audio.description,
                "duration": audio.duration,
                "size": audio.file_size,
                "type": audio.audio_type,
                "campaign_id": audio.campaign_id,
                "created_at": audio.created_at.isoformat(),
                "play_url": f"/api/audio/play/{audio.id}"
            }
            for audio in audio_files
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar áudios: {str(e)}")

@router.get("/play/{audio_id}")
async def play_audio(audio_id: int, db=Depends(get_db)):
    """
    Reproduzir arquivo de áudio
    """
    try:
        audio_file = await AudioService.get_audio_file(db, audio_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Áudio não encontrado")
        
        if not os.path.exists(audio_file.file_path):
            raise HTTPException(status_code=404, detail="Arquivo de áudio não encontrado")
        
        return FileResponse(
            path=audio_file.file_path,
            media_type="audio/wav",
            filename=audio_file.filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reproduzir áudio: {str(e)}")

@router.delete("/delete/{audio_id}")
async def delete_audio(audio_id: int, db=Depends(get_db)):
    """
    Deletar arquivo de áudio
    """
    try:
        audio_file = await AudioService.get_audio_file(db, audio_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Áudio não encontrado")
        
        # Remover arquivo físico
        if os.path.exists(audio_file.file_path):
            os.remove(audio_file.file_path)
        
        # Remover do banco
        await AudioService.delete_audio_file(db, audio_id)
        
        return {"success": True, "message": "Áudio deletado com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar áudio: {str(e)}")

@router.get("/test/{audio_id}")
async def test_audio(audio_id: int, db=Depends(get_db)):
    """
    Testar arquivo de áudio (reprodução via Asterisk)
    """
    try:
        audio_file = await AudioService.get_audio_file(db, audio_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Áudio não encontrado")
        
        # Testar reprodução via AMI
        from ..services.asterisk_manager import AsteriskManager
        ami = AsteriskManager()
        
        test_result = await ami.test_audio_playback(audio_file.file_path)
        
        return {
            "success": True,
            "message": "Teste de áudio executado",
            "result": test_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao testar áudio: {str(e)}")

@router.post("/convert/{audio_id}")
async def convert_audio(
    audio_id: int,
    target_format: str = "wav",
    sample_rate: int = 8000,
    channels: int = 1,
    db=Depends(get_db)
):
    """
    Converter arquivo de áudio para formato específico
    """
    try:
        audio_file = await AudioService.get_audio_file(db, audio_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Áudio não encontrado")
        
        if target_format not in ALLOWED_FORMATS:
            raise HTTPException(status_code=400, detail="Formato não suportado")
        
        # Converter áudio
        converted_path = await AudioService.convert_audio(
            audio_file.file_path,
            target_format,
            sample_rate,
            channels
        )
        
        return {
            "success": True,
            "message": "Áudio convertido com sucesso",
            "converted_path": converted_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao converter áudio: {str(e)}")

@router.get("/stats")
async def get_audio_stats(db=Depends(get_db)):
    """
    Estatísticas dos arquivos de áudio
    """
    try:
        stats = await AudioService.get_audio_stats(db)
        
        return {
            "total_files": stats.get("total_files", 0),
            "total_size": stats.get("total_size", 0),
            "total_duration": stats.get("total_duration", 0),
            "by_type": stats.get("by_type", {}),
            "by_campaign": stats.get("by_campaign", {}),
            "disk_usage": stats.get("disk_usage", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}") 