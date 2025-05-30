import os
from fastapi import Header, HTTPException, status
import logging

# Configurar logger
logger = logging.getLogger(__name__)

async def verificar_api_key(x_api_key: str = Header(..., description="API Key para autenticación del webhook")):
    """
    Dependencia para verificar la API Key proporcionada en el encabezado X-API-Key.
    
    Esta función:
    1. Obtiene la API Key válida desde variable de entorno
    2. Compara con la API Key proporcionada en la solicitud
    3. Autoriza o rechaza la solicitud según corresponda
    
    Args:
        x_api_key: API Key proporcionada en el encabezado de la solicitud
        
    Returns:
        None: Si la autenticación es exitosa, la solicitud continúa procesándose
        
    Raises:
        HTTPException: Si la API Key es inválida o no se proporciona
    """
    # Obtener API Key desde variable de entorno
    # Si no existe, se usa un valor predeterminado para desarrollo (NO RECOMENDADO EN PRODUCCIÓN)
    api_key_esperada = os.environ.get("WEBHOOK_API_KEY", "api_key_development_only")
    
    # Verificar si la API Key proporcionada coincide con la esperada
    if x_api_key != api_key_esperada:
        logger.warning(f"Intento de acceso al webhook con API Key inválida")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key inválida o no proporcionada"
        )
    
    # Si llegamos aquí, la API Key es válida
    return None 