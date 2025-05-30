from fastapi import APIRouter, Query, HTTPException
import random

router = APIRouter(tags=["CLI"])

@router.get("/generar", summary="Generar identificador de llamada (CLI) aleatorio")
async def generar_cli(
    numero_destino: str = Query(..., description="Número de teléfono destino")
):
    """
    Genera un identificador de llamada (CLI) aleatorio basado en el prefijo del número destino.
    
    Parámetros:
        numero_destino: Número de teléfono destino
        
    Retorna:
        dict: CLI generado
    """
    try:
        # Validar número
        if not numero_destino or len(numero_destino) < 6:
            raise HTTPException(status_code=400, detail="Número de teléfono inválido")
        
        # Extraer prefijo (primeros 5 dígitos)
        prefijo = numero_destino[:5]
        
        # Generar 5 dígitos aleatorios para el sufijo
        sufijo = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        
        # Crear CLI completo
        cli_generado = f"{prefijo}{sufijo}"
        
        return {
            "numero_destino": numero_destino,
            "cli_generado": cli_generado,
            "prefijo": prefijo,
            "sufijo": sufijo
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al generar CLI: {str(e)}") 