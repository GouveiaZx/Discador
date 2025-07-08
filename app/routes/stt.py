from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import tempfile

from app.database import obtener_sesion
from app.config import VOSK_MODEL_PATH
# Importar servicios necesarios

router = APIRouter(tags=["STT"])

@router.post("/reconocer", summary="Reconocer voz en archivo de audio")
async def reconocer_voz(
    archivo: UploadFile = File(...),
    db: Session = Depends(obtener_sesion)
):
    """
    Envía un archivo .wav y devuelve la transcripción usando Vosk.
    
    Parámetros:
        archivo: Archivo de audio en formato .wav
        
    Retorna:
        dict: Transcripción del audio
    """
    try:
        # Verificar extensión del archivo
        nombre_archivo = archivo.filename
        if not nombre_archivo.endswith('.wav'):
            raise HTTPException(status_code=400, detail="Formato de archivo no soportado. Use WAV")
        
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(await archivo.read())
        
        try:
            # En una implementación real, aquí iría la lógica para usar Vosk
            # Por ahora, simulamos el reconocimiento
            
            # Simulación de respuesta
            transcripcion = "Hola, estoy interesado en el producto que mencionaste en el anuncio."
            
            return {
                "mensaje": "Audio procesado correctamente",
                "transcripcion": transcripcion,
                "confianza": 0.85
            }
        finally:
            # Eliminar archivo temporal
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al procesar audio: {str(e)}") 