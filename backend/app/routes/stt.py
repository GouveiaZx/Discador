from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import tempfile

from app.database import obtener_sesion

router = APIRouter(tags=["STT"])

@router.post("/reconocer", summary="Reconocer voz en archivo de audio")
async def reconocer_voz(
    archivo: UploadFile = File(...),
    db: Session = Depends(obtener_sesion)
):
    """
    Endpoint mock para reconhecimento de voz.
    Em produção, pode ser integrado com serviços como Google Speech-to-Text,
    Azure Speech Services ou AWS Transcribe.
    
    Parametros:
        archivo: Arquivo de áudio em formato .wav
        
    Retorna:
        dict: Transcrição simulada do áudio
    """
    try:
        # Verificar extensão do arquivo
        nome_arquivo = archivo.filename
        if not nome_arquivo.endswith(('.wav', '.mp3', '.m4a')):
            raise HTTPException(
                status_code=400, 
                detail="Formato de arquivo não suportado. Use WAV, MP3 ou M4A"
            )
        
        # Verificar tamanho do arquivo (máximo 10MB)
        arquivo_bytes = await archivo.read()
        if len(arquivo_bytes) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="Arquivo muito grande. Máximo 10MB"
            )
        
        # Simulação de processamento
        transcricoes_exemplo = [
            "Olá, estou interessado no produto que vocês anunciaram.",
            "Gostaria de saber mais informações sobre o serviço.",
            "Podem me ligar mais tarde, por favor?",
            "Não tenho interesse no momento, obrigado.",
            "Deixa eu ver... sim, quero saber mais detalhes."
        ]
        
        import random
        transcricao = random.choice(transcricoes_exemplo)
        confianca = round(random.uniform(0.7, 0.95), 2)
        
        return {
            "status": "success",
            "mensaje": "Áudio processado com sucesso",
            "transcripcion": transcricao,
            "confianza": confianca,
            "duracion_segundos": round(len(arquivo_bytes) / 16000, 1),  # Estimativa
            "formato": nome_arquivo.split('.')[-1].upper(),
            "tamanho_kb": round(len(arquivo_bytes) / 1024, 1),
            "mock": True
        }
                
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao processar áudio: {str(e)}"
        ) 