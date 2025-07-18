from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.database import get_db
from app.services.dynamic_cli_service import DynamicCliService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dynamic-cli", tags=["Dynamic CLI"])

class CliGenerationRequest(BaseModel):
    destination_number: str
    cli_type: str  # MXN, ALEATORIO, ALEATORIO1, DID, DID1
    trunk_id: Optional[int] = None
    campaign_id: Optional[str] = None

class BulkCliGenerationRequest(BaseModel):
    destination_numbers: list[str]
    cli_type: str
    trunk_id: Optional[int] = None
    campaign_id: Optional[str] = None

@router.post("/generate")
async def generate_dynamic_cli(
    request: CliGenerationRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Gera CLI dinâmico para um número específico.
    
    Tipos suportados:
    - MXN: México (detecta código de área e gera últimos 4 dígitos aleatórios)
    - ALEATORIO: USA/Canadá código aleatório
    - ALEATORIO1: USA/Canadá código aleatório com prefixo "1"
    - DID: USA/Canadá baseado em DIDs disponíveis
    - DID1: USA/Canadá DIDs com prefixo "1"
    """
    try:
        cli_service = DynamicCliService(db)
        result = cli_service.generate_dynamic_cli(
            destination_number=request.destination_number,
            cli_type=request.cli_type,
            trunk_id=request.trunk_id
        )
        
        if result['success']:
            return {
                "status": "success",
                "data": result,
                "message": f"CLI gerado com sucesso para {request.destination_number}"
            }
        else:
            return {
                "status": "error",
                "error": result['error'],
                "message": "Falha ao gerar CLI"
            }
            
    except Exception as e:
        logger.error(f"Erro ao gerar CLI dinâmico: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/bulk")
async def generate_bulk_dynamic_cli(
    request: BulkCliGenerationRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Gera CLIs dinâmicos para múltiplos números.
    Útil para pré-processamento de listas grandes.
    """
    try:
        cli_service = DynamicCliService(db)
        results = []
        errors = []
        
        for destination_number in request.destination_numbers:
            result = cli_service.generate_dynamic_cli(
                destination_number=destination_number,
                cli_type=request.cli_type,
                trunk_id=request.trunk_id
            )
            
            if result['success']:
                results.append({
                    "destination": destination_number,
                    "cli": result['cli'],
                    "display_cli": result['display_cli'],
                    "type": result['type']
                })
            else:
                errors.append({
                    "destination": destination_number,
                    "error": result['error']
                })
        
        return {
            "status": "completed",
            "total_processed": len(request.destination_numbers),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar CLIs em lote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/stats")
async def get_cli_usage_stats(
    did_number: Optional[str] = Query(None, description="Número DID específico para estatísticas"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtém estatísticas de uso de CLIs.
    
    Se did_number for fornecido, retorna estatísticas específicas do DID.
    Caso contrário, retorna estatísticas gerais.
    """
    try:
        cli_service = DynamicCliService(db)
        stats = cli_service.get_cli_usage_stats(did_number)
        
        return {
            "status": "success",
            "data": stats,
            "message": "Estatísticas obtidas com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de CLI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/usage/reset")
async def reset_daily_usage(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reseta contadores de uso diário.
    Normalmente executado automaticamente à meia-noite.
    """
    try:
        cli_service = DynamicCliService(db)
        cli_service.reset_daily_usage()
        
        return {
            "status": "success",
            "message": "Contadores de uso diário resetados com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao resetar uso diário: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types")
async def get_cli_types() -> Dict[str, Any]:
    """
    Retorna tipos de CLI disponíveis e suas descrições.
    """
    return {
        "status": "success",
        "data": {
            "MXN": {
                "description": "México - Detecta código de área e gera últimos 4 dígitos aleatórios",
                "example": "55 2222-xxxx (Cidade do México) ou 998 222-xxxx (Cancún)",
                "countries": ["Mexico"]
            },
            "ALEATORIO": {
                "description": "USA/Canadá - Código de área aleatório evitando mesmo do destino",
                "example": "813 2xx-xxxx (se chamando para 727)",
                "countries": ["USA", "Canada"]
            },
            "ALEATORIO1": {
                "description": "USA/Canadá - Código aleatório com prefixo '1'",
                "example": "1 813 2xx-xxxx",
                "countries": ["USA", "Canada"]
            },
            "DID": {
                "description": "USA/Canadá - Baseado em DIDs disponíveis (limite 100/dia)",
                "example": "212 xxx-xxxx (usando DID de Nova York)",
                "countries": ["USA", "Canada"]
            },
            "DID1": {
                "description": "USA/Canadá - DIDs com prefixo '1'",
                "example": "1 212 xxx-xxxx",
                "countries": ["USA", "Canada"]
            }
        },
        "message": "Tipos de CLI disponíveis"
    }

@router.get("/area-codes/{country}")
async def get_area_codes_by_country(
    country: str,
    state: Optional[str] = Query(None, description="Estado/província específico"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retorna códigos de área por país/estado.
    """
    try:
        cli_service = DynamicCliService(db)
        
        if country.lower() in ['usa', 'canada', 'us', 'ca']:
            area_codes = cli_service.area_codes_usa_canada
            
            if state:
                state_codes = area_codes.get(state.lower(), [])
                return {
                    "status": "success",
                    "data": {
                        "country": country,
                        "state": state,
                        "area_codes": state_codes,
                        "total": len(state_codes)
                    }
                }
            else:
                return {
                    "status": "success",
                    "data": {
                        "country": country,
                        "states": area_codes,
                        "total_states": len(area_codes)
                    }
                }
        else:
            return {
                "status": "error",
                "message": f"País {country} não suportado. Disponíveis: USA, Canada"
            }
            
    except Exception as e:
        logger.error(f"Erro ao obter códigos de área: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/{cli_type}")
async def test_cli_generation(
    cli_type: str,
    destination: str = Query(..., description="Número de destino para teste"),
    trunk_id: Optional[int] = Query(None, description="ID do trunk"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Endpoint para testar geração de CLI com diferentes tipos.
    """
    try:
        cli_service = DynamicCliService(db)
        result = cli_service.generate_dynamic_cli(
            destination_number=destination,
            cli_type=cli_type,
            trunk_id=trunk_id
        )
        
        return {
            "status": "test_completed",
            "input": {
                "destination": destination,
                "cli_type": cli_type,
                "trunk_id": trunk_id
            },
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Erro no teste de CLI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))