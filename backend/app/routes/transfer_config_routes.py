"""Rotas para configuração flexível de transferências."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, time
import logging

from ..database import get_db
from ..services.transfer_config_service import TransferConfigService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transfer-config", tags=["Configuração de Transferência"])

# Schemas
class HorarioFuncionamento(BaseModel):
    """Schema para horário de funcionamento."""
    inicio: str = Field(..., description="Horário de início (HH:MM)")
    fim: str = Field(..., description="Horário de fim (HH:MM)")
    dias_semana: List[int] = Field(..., description="Dias da semana (0=Segunda, 6=Domingo)")
    fuso_horario: str = Field(default="America/Sao_Paulo", description="Fuso horário")

class TransferConfigCreate(BaseModel):
    """Schema para criação de configuração de transferência."""
    campanha_id: int = Field(..., description="ID da campanha")
    nome: str = Field(..., max_length=100, description="Nome da configuração")
    numeros_transferencia: List[str] = Field(..., description="Lista de números para transferência")
    estrategia_selecao: str = Field(
        default="round-robin", 
        description="Estratégia de seleção: round-robin, aleatoria, prioridade"
    )
    horario_funcionamento: Optional[HorarioFuncionamento] = Field(
        None, description="Horário de funcionamento (opcional)"
    )
    ativo: bool = Field(default=True, description="Se a configuração está ativa")
    prioridades: Optional[Dict[str, int]] = Field(
        None, description="Prioridades dos números (para estratégia prioridade)"
    )

class TransferConfigUpdate(BaseModel):
    """Schema para atualização de configuração de transferência."""
    nome: Optional[str] = Field(None, max_length=100)
    numeros_transferencia: Optional[List[str]] = None
    estrategia_selecao: Optional[str] = None
    horario_funcionamento: Optional[HorarioFuncionamento] = None
    ativo: Optional[bool] = None
    prioridades: Optional[Dict[str, int]] = None

class TransferConfigResponse(BaseModel):
    """Schema para resposta de configuração de transferência."""
    id: int
    campanha_id: int
    nome: str
    numeros_transferencia: List[str]
    estrategia_selecao: str
    horario_funcionamento: Optional[Dict[str, Any]]
    ativo: bool
    prioridades: Optional[Dict[str, int]]
    created_at: datetime
    updated_at: Optional[datetime]

class TransferStatsResponse(BaseModel):
    """Schema para estatísticas de transferência."""
    config_id: int
    total_transferencias: int
    transferencias_sucesso: int
    transferencias_falha: int
    taxa_sucesso: float
    numero_mais_usado: Optional[str]
    ultimo_uso: Optional[datetime]

@router.post("/", response_model=TransferConfigResponse)
async def create_transfer_config(
    config: TransferConfigCreate,
    db: Session = Depends(get_db)
):
    """Criar nova configuração de transferência."""
    try:
        service = TransferConfigService(db)
        result = service.create_config(
            campanha_id=config.campanha_id,
            nome=config.nome,
            numeros_transferencia=config.numeros_transferencia,
            estrategia_selecao=config.estrategia_selecao,
            horario_funcionamento=config.horario_funcionamento.dict() if config.horario_funcionamento else None,
            ativo=config.ativo,
            prioridades=config.prioridades
        )
        
        if result["success"]:
            return TransferConfigResponse(**result["data"])
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Erro ao criar configuração de transferência: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/", response_model=List[TransferConfigResponse])
async def list_transfer_configs(
    campanha_id: Optional[int] = Query(None, description="Filtrar por campanha"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db)
):
    """Listar configurações de transferência."""
    try:
        service = TransferConfigService(db)
        result = service.list_configs(
            campanha_id=campanha_id,
            ativo=ativo,
            skip=skip,
            limit=limit
        )
        
        if result["success"]:
            return [TransferConfigResponse(**config) for config in result["data"]]
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Erro ao listar configurações: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/{config_id}", response_model=TransferConfigResponse)
async def get_transfer_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Obter configuração específica de transferência."""
    try:
        service = TransferConfigService(db)
        result = service.get_config(config_id)
        
        if result["success"]:
            return TransferConfigResponse(**result["data"])
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Erro ao obter configuração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.put("/{config_id}", response_model=TransferConfigResponse)
async def update_transfer_config(
    config_id: int,
    config: TransferConfigUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar configuração de transferência."""
    try:
        service = TransferConfigService(db)
        
        # Preparar dados para atualização
        update_data = {}
        if config.nome is not None:
            update_data["nome"] = config.nome
        if config.numeros_transferencia is not None:
            update_data["numeros_transferencia"] = config.numeros_transferencia
        if config.estrategia_selecao is not None:
            update_data["estrategia_selecao"] = config.estrategia_selecao
        if config.horario_funcionamento is not None:
            update_data["horario_funcionamento"] = config.horario_funcionamento.dict()
        if config.ativo is not None:
            update_data["ativo"] = config.ativo
        if config.prioridades is not None:
            update_data["prioridades"] = config.prioridades
        
        result = service.update_config(config_id, update_data)
        
        if result["success"]:
            return TransferConfigResponse(**result["data"])
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Erro ao atualizar configuração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.delete("/{config_id}")
async def delete_transfer_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Deletar configuração de transferência."""
    try:
        service = TransferConfigService(db)
        result = service.delete_config(config_id)
        
        if result["success"]:
            return {"message": "Configuração deletada com sucesso"}
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Erro ao deletar configuração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/{config_id}/next-number")
async def get_next_transfer_number(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Obter próximo número para transferência baseado na estratégia."""
    try:
        service = TransferConfigService(db)
        result = service.get_next_number(config_id)
        
        if result["success"]:
            return {
                "numero": result["numero"],
                "estrategia_usada": result["estrategia"],
                "config_id": config_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Erro ao obter próximo número: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/{config_id}/register-transfer")
async def register_transfer(
    config_id: int,
    numero_usado: str,
    sucesso: bool,
    detalhes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Registrar uma transferência realizada."""
    try:
        service = TransferConfigService(db)
        result = service.register_transfer(
            config_id=config_id,
            numero_usado=numero_usado,
            sucesso=sucesso,
            detalhes=detalhes
        )
        
        if result["success"]:
            return {
                "message": "Transferência registrada com sucesso",
                "transfer_id": result["transfer_id"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Erro ao registrar transferência: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/{config_id}/stats", response_model=TransferStatsResponse)
async def get_transfer_stats(
    config_id: int,
    dias: int = Query(30, ge=1, le=365, description="Período em dias para estatísticas"),
    db: Session = Depends(get_db)
):
    """Obter estatísticas de uso da configuração de transferência."""
    try:
        service = TransferConfigService(db)
        result = service.get_transfer_stats(config_id, dias)
        
        if result["success"]:
            return TransferStatsResponse(**result["data"])
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/campanha/{campanha_id}/active")
async def get_active_config_for_campaign(
    campanha_id: int,
    db: Session = Depends(get_db)
):
    """Obter configuração ativa para uma campanha específica."""
    try:
        service = TransferConfigService(db)
        result = service.get_active_config_for_campaign(campanha_id)
        
        if result["success"]:
            if result["data"]:
                return TransferConfigResponse(**result["data"])
            else:
                raise HTTPException(
                    status_code=404, 
                    detail="Nenhuma configuração ativa encontrada para esta campanha"
                )
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Erro ao obter configuração ativa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/test-strategy")
async def test_transfer_strategy(
    numeros: List[str],
    estrategia: str,
    prioridades: Optional[Dict[str, int]] = None,
    quantidade_testes: int = Query(10, ge=1, le=100)
):
    """Testar estratégia de seleção de números."""
    try:
        service = TransferConfigService(None)  # Não precisa de DB para teste
        
        resultados = []
        for i in range(quantidade_testes):
            numero = service._select_number_by_strategy(
                numeros, estrategia, prioridades
            )
            resultados.append(numero)
        
        # Calcular distribuição
        distribuicao = {}
        for numero in resultados:
            distribuicao[numero] = distribuicao.get(numero, 0) + 1
        
        return {
            "estrategia": estrategia,
            "numeros_testados": numeros,
            "quantidade_testes": quantidade_testes,
            "resultados": resultados,
            "distribuicao": distribuicao,
            "distribuicao_percentual": {
                numero: round((count / quantidade_testes) * 100, 2)
                for numero, count in distribuicao.items()
            }
        }
        
    except Exception as e:
        logger.error(f"Erro no teste de estratégia: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/validate-numbers")
async def validate_transfer_numbers(
    numeros: List[str] = Query(..., description="Lista de números para validar")
):
    """Validar formato de números de transferência."""
    try:
        service = TransferConfigService(None)
        
        resultados = []
        for numero in numeros:
            is_valid, error = service._validate_phone_number(numero)
            resultados.append({
                "numero": numero,
                "valido": is_valid,
                "erro": error if not is_valid else None
            })
        
        total_validos = sum(1 for r in resultados if r["valido"])
        
        return {
            "total_numeros": len(numeros),
            "total_validos": total_validos,
            "total_invalidos": len(numeros) - total_validos,
            "taxa_validacao": round((total_validos / len(numeros)) * 100, 2) if numeros else 0,
            "resultados": resultados
        }
        
    except Exception as e:
        logger.error(f"Erro na validação de números: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")