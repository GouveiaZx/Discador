import os
from fastapi import Header, HTTPException, status
import logging

# Configurar logger
logger = logging.getLogger(__name__)

async def verificar_api_key(x_api_key: str = Header(..., description="API Key para autenticacion del webhook")):
    """
    Dependencia para verificar la API Key proporcionada en el encabezado X-API-Key.
    
    Esta funcion:
    1. Obtiene la API Key valida desde variable de entorno
    2. Compara con la API Key proporcionada en la solicitud
    3. Autoriza o rechaza la solicitud segun corresponda
    
    Args:
        x_api_key: API Key proporcionada en el encabezado de la solicitud
        
    Returns:
        None: Si la autenticacion es exitosa, la solicitud continua procesandose
        
    Raises:
        HTTPException: Si la API Key es invalida o no se proporciona
    """
    # Obtener API Key desde variable de entorno
    # Si no existe, se usa un valor predeterminado para desarrollo (NO RECOMENDADO EN PRODUCCION)
    api_key_esperada = os.environ.get("WEBHOOK_API_KEY", "api_key_development_only")
    
    # Verificar si la API Key proporcionada coincide con la esperada
    if x_api_key != api_key_esperada:
        logger.warning(f"Intento de acceso al webhook con API Key invalida")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key invalida o no proporcionada"
        )
    
    # Si llegamos aqui, la API Key es valida
    return None 