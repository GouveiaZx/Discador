from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from services.cli_auto_calculator_service import CliAutoCalculatorService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cli-auto", tags=["CLI Auto Calculator"])

# Schemas
class CliCalculationRequest(BaseModel):
    total_numbers: int = Field(..., gt=0, description="Quantidade total de números")
    calls_per_hour: int = Field(500, gt=0, le=5000, description="Chamadas por hora (sem limite rígido)")
    daily_call_limit: int = Field(100, gt=0, le=10000, description="Limite diário por CLI (configurável)")
    work_hours: int = Field(8, gt=0, le=24, description="Horas de trabalho por dia")
    country: str = Field("usa", description="País")

class CliAutoConfigRequest(BaseModel):
    campaign_id: Optional[int] = Field(None, description="ID da campanha")
    total_numbers: int = Field(..., gt=0, description="Quantidade total de números")
    calls_per_hour: int = Field(500, gt=0, le=2000, description="Chamadas por hora")
    daily_call_limit: int = Field(100, gt=0, le=1000, description="Limite diário por CLI")
    work_hours: int = Field(8, gt=0, le=24, description="Horas de trabalho por dia")
    country: str = Field("usa", description="País")
    auto_generate: bool = Field(True, description="Gerar CLIs automaticamente")

class CliGenerationRequest(BaseModel):
    config_id: int = Field(..., gt=0, description="ID da configuração")
    quantity: int = Field(..., gt=0, le=10000, description="Quantidade de CLIs")
    country: str = Field("usa", description="País")

# Dependency
def get_cli_service() -> CliAutoCalculatorService:
    return CliAutoCalculatorService()

@router.post("/calculate")
async def calculate_clis_needed(
    request: CliCalculationRequest,
    service: CliAutoCalculatorService = Depends(get_cli_service)
) -> Dict:
    """
    Calcula o número de CLIs necessários baseado no volume de números.
    
    Esta endpoint permite calcular quantos CLIs são necessários para uma campanha
    baseado no volume de números, velocidade de discagem e limites diários.
    
    **Fórmula utilizada:**
    - CLIs mínimos = Total números ÷ Limite diário
    - CLIs por velocidade = Chamadas/hora ÷ (Limite diário ÷ Horas trabalho)
    - CLIs recomendados = MAX(mínimos, velocidade) × 1.2 (margem segurança)
    
    **Exemplo de uso:**
    - 10.000 números, 500 chamadas/hora, limite 100/dia, 8h trabalho
    - Resultado: ~63 CLIs recomendados
    """
    try:
        result = service.calculate_clis_needed(
            total_numbers=request.total_numbers,
            calls_per_hour=request.calls_per_hour,
            daily_call_limit=request.daily_call_limit,
            work_hours=request.work_hours,
            country=request.country
        )
        
        logger.info(f"Cálculo realizado: {request.total_numbers} números -> {result['recommended_clis']} CLIs")
        return {
            "success": True,
            "data": result,
            "message": f"Calculados {result['recommended_clis']} CLIs necessários para {request.total_numbers} números"
        }
        
    except Exception as e:
        logger.error(f"Erro no cálculo de CLIs: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no cálculo: {str(e)}")

@router.post("/config")
async def create_auto_config(
    request: CliAutoConfigRequest,
    service: CliAutoCalculatorService = Depends(get_cli_service)
) -> Dict:
    """
    Cria uma configuração automática de CLIs.
    
    Esta endpoint cria uma configuração completa incluindo:
    - Cálculo automático de CLIs necessários
    - Geração automática de CLIs (se solicitado)
    - Armazenamento da configuração no banco
    
    **Benefícios:**
    - Remove limite de 20 CLIs
    - Cálculo baseado em volume real
    - Geração automática com códigos de área reais
    - Prevenção de blacklisting
    """
    try:
        result = service.create_auto_config(
            campaign_id=request.campaign_id,
            total_numbers=request.total_numbers,
            calls_per_hour=request.calls_per_hour,
            daily_call_limit=request.daily_call_limit,
            work_hours=request.work_hours,
            country=request.country,
            auto_generate=request.auto_generate
        )
        
        logger.info(f"Configuração criada: ID {result['config_id']} com {result['recommended_clis']} CLIs")
        return {
            "success": True,
            "data": result,
            "message": f"Configuração criada com sucesso. {result.get('generated_clis', 0)} CLIs gerados."
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar configuração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar configuração: {str(e)}")

@router.post("/generate")
async def generate_clis(
    request: CliGenerationRequest,
    service: CliAutoCalculatorService = Depends(get_cli_service)
) -> Dict:
    """
    Gera CLIs adicionais para uma configuração existente.
    
    Permite gerar mais CLIs para uma configuração já criada,
    útil quando o volume de números aumenta ou quando é necessário
    expandir o pool de CLIs disponíveis.
    """
    try:
        generated_count = service.generate_clis_for_config(
            config_id=request.config_id,
            quantity=request.quantity,
            country=request.country
        )
        
        logger.info(f"Gerados {generated_count} CLIs para configuração {request.config_id}")
        return {
            "success": True,
            "data": {
                "config_id": request.config_id,
                "generated_count": generated_count,
                "requested_quantity": request.quantity
            },
            "message": f"Gerados {generated_count} CLIs com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar CLIs: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar CLIs: {str(e)}")

@router.get("/config/{config_id}")
async def get_config_details(
    config_id: int,
    service: CliAutoCalculatorService = Depends(get_cli_service)
) -> Dict:
    """
    Obtém detalhes completos de uma configuração automática.
    
    Retorna informações detalhadas incluindo:
    - Parâmetros da configuração
    - Quantidade de CLIs gerados
    - Estatísticas de uso
    - Status atual
    """
    try:
        result = service.get_config_details(config_id)
        
        return {
            "success": True,
            "data": result,
            "message": "Detalhes da configuração obtidos com sucesso"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao obter detalhes da configuração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter detalhes: {str(e)}")

@router.get("/area-codes")
async def get_area_codes(
    country: str = Query("usa", description="País"),
    service: CliAutoCalculatorService = Depends(get_cli_service)
) -> Dict:
    """
    Obtém códigos de área disponíveis para um país.
    
    Retorna lista completa de códigos de área com informações de:
    - Estado/Província
    - Cidade principal
    - Fuso horário
    
    **Suporte atual:**
    - USA: 300+ códigos de área
    - Outros países: Em desenvolvimento
    """
    try:
        area_codes = service.get_available_area_codes(country)
        
        return {
            "success": True,
            "data": {
                "country": country,
                "area_codes": area_codes,
                "total_count": len(area_codes)
            },
            "message": f"Encontrados {len(area_codes)} códigos de área para {country.upper()}"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter códigos de área: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter códigos de área: {str(e)}")

@router.get("/config/{config_id}/stats")
async def get_cli_usage_stats(
    config_id: int,
    service: CliAutoCalculatorService = Depends(get_cli_service)
) -> Dict:
    """
    Obtém estatísticas de uso dos CLIs de uma configuração.
    
    Fornece métricas importantes para monitoramento:
    - Total de CLIs ativos
    - CLIs utilizados hoje
    - Uso médio por CLI
    - Uso máximo por CLI
    - Capacidade total utilizada
    """
    try:
        stats = service.get_cli_usage_stats(config_id)
        
        return {
            "success": True,
            "data": {
                "config_id": config_id,
                "stats": stats
            },
            "message": "Estatísticas obtidas com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@router.post("/reset-usage")
async def reset_daily_usage(
    config_id: Optional[int] = Query(None, description="ID da configuração (opcional)"),
    service: CliAutoCalculatorService = Depends(get_cli_service)
) -> Dict:
    """
    Reseta o uso diário dos CLIs.
    
    Permite resetar contadores diários de uso:
    - Se config_id fornecido: reseta apenas essa configuração
    - Se config_id não fornecido: reseta todos os CLIs
    
    **Uso recomendado:**
    - Executar automaticamente à meia-noite
    - Executar manualmente quando necessário
    """
    try:
        reset_count = service.reset_daily_usage(config_id)
        
        message = f"Resetados {reset_count} CLIs"
        if config_id:
            message += f" da configuração {config_id}"
        else:
            message += " de todas as configurações"
        
        logger.info(message)
        return {
            "success": True,
            "data": {
                "reset_count": reset_count,
                "config_id": config_id
            },
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Erro ao resetar uso diário: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao resetar uso: {str(e)}")

@router.get("/examples")
async def get_calculation_examples() -> Dict:
    """
    Fornece exemplos práticos de cálculos de CLIs.
    
    Demonstra diferentes cenários de uso com cálculos reais
    para ajudar na compreensão do sistema.
    """
    examples = [
        {
            "scenario": "Campanha Pequena",
            "description": "Campanha local com volume baixo",
            "parameters": {
                "total_numbers": 1000,
                "calls_per_hour": 200,
                "daily_call_limit": 100,
                "work_hours": 8
            },
            "result": "~3 CLIs necessários",
            "explanation": "Volume baixo permite poucos CLIs com margem de segurança"
        },
        {
            "scenario": "Campanha Média",
            "description": "Campanha regional com volume moderado",
            "parameters": {
                "total_numbers": 10000,
                "calls_per_hour": 500,
                "daily_call_limit": 100,
                "work_hours": 8
            },
            "result": "~63 CLIs necessários",
            "explanation": "Velocidade de discagem determina necessidade de mais CLIs"
        },
        {
            "scenario": "Campanha Grande",
            "description": "Campanha nacional com alto volume",
            "parameters": {
                "total_numbers": 100000,
                "calls_per_hour": 1000,
                "daily_call_limit": 100,
                "work_hours": 8
            },
            "result": "~1500 CLIs necessários",
            "explanation": "Alto volume requer pool grande de CLIs para evitar blacklisting"
        },
        {
            "scenario": "Campanha Intensiva",
            "description": "Campanha com discagem muito agressiva",
            "parameters": {
                "total_numbers": 50000,
                "calls_per_hour": 2000,
                "daily_call_limit": 100,
                "work_hours": 8
            },
            "result": "~3000 CLIs necessários",
            "explanation": "Velocidade extrema requer pool muito grande para distribuir carga"
        }
    ]
    
    return {
        "success": True,
        "data": {
            "examples": examples,
            "formula_explanation": {
                "basic_formula": "CLIs = (Total números × Chamadas/hora) ÷ (Limite diário × Horas trabalho)",
                "safety_margin": "Resultado × 1.2 (20% margem de segurança)",
                "minimum_rule": "Nunca menos que Total números ÷ Limite diário",
                "velocity_rule": "Considerar velocidade de discagem para distribuição de carga"
            },
            "best_practices": [
                "Sempre usar margem de segurança de pelo menos 20%",
                "Considerar fuso horário do público-alvo",
                "Monitorar uso diário para ajustar limites",
                "Resetar contadores diariamente",
                "Usar códigos de área locais quando possível"
            ]
        },
        "message": "Exemplos e melhores práticas fornecidos"
    }