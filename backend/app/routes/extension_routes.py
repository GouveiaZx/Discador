from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..database import get_db
from ..services.extension_service import ExtensionService
from ..models.extension import Extension, ExtensionStats, ExtensionLog, ExtensionConfig
from pydantic import BaseModel, Field

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/extensions", tags=["extensions"])

# Schemas Pydantic
class ExtensionCreate(BaseModel):
    numero: str = Field(..., min_length=3, max_length=10, description="Número da extensão")
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da extensão")
    campanha_id: Optional[int] = Field(None, description="ID da campanha associada")
    ativo: bool = Field(True, description="Status ativo da extensão")
    configuracoes: Optional[dict] = Field(None, description="Configurações técnicas da extensão")
    horario_funcionamento: Optional[dict] = Field(None, description="Horário de funcionamento")

class ExtensionUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome da extensão")
    campanha_id: Optional[int] = Field(None, description="ID da campanha associada")
    ativo: Optional[bool] = Field(None, description="Status ativo da extensão")
    configuracoes: Optional[dict] = Field(None, description="Configurações técnicas da extensão")
    horario_funcionamento: Optional[dict] = Field(None, description="Horário de funcionamento")

class ExtensionConfigCreate(BaseModel):
    sip_username: Optional[str] = Field(None, max_length=50)
    sip_password: Optional[str] = Field(None, max_length=100)
    sip_domain: Optional[str] = Field(None, max_length=100)
    sip_proxy: Optional[str] = Field(None, max_length=100)
    sip_port: Optional[int] = Field(5060, ge=1, le=65535)
    preferred_codec: Optional[str] = Field("ulaw", max_length=20)
    allowed_codecs: Optional[str] = Field("ulaw,alaw,gsm", max_length=200)
    nat_enabled: bool = Field(True)
    stun_server: Optional[str] = Field(None, max_length=100)
    qualify_enabled: bool = Field(True)
    qualify_frequency: Optional[int] = Field(60, ge=10, le=300)
    dtmf_mode: Optional[str] = Field("rfc2833", max_length=20)
    call_limit: Optional[int] = Field(5, ge=1, le=100)
    call_timeout: Optional[int] = Field(30, ge=5, le=300)
    context: Optional[str] = Field("default", max_length=50)

class ExtensionResponse(BaseModel):
    id: int
    numero: str
    nome: str
    campanha_id: Optional[int]
    ativo: bool
    configuracoes: Optional[dict]
    horario_funcionamento: Optional[dict]
    created_at: Optional[str]
    updated_at: Optional[str]
    
    class Config:
        from_attributes = True

class ExtensionStatsResponse(BaseModel):
    id: int
    extension_id: int
    total_calls: int
    successful_calls: int
    failed_calls: int
    active_calls: int
    total_talk_time: int
    avg_talk_time: int
    online: bool
    last_activity: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    date: Optional[str]
    
    class Config:
        from_attributes = True

# Dependência para obter o serviço de extensões
def get_extension_service(db: Session = Depends(get_db)) -> ExtensionService:
    return ExtensionService(db)

@router.post("/", response_model=ExtensionResponse, status_code=status.HTTP_201_CREATED)
async def create_extension(
    extension_data: ExtensionCreate,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Criar uma nova extensão
    """
    try:
        extension = await service.create_extension(
            numero=extension_data.numero,
            nome=extension_data.nome,
            campanha_id=extension_data.campanha_id,
            ativo=extension_data.ativo,
            configuracoes=extension_data.configuracoes,
            horario_funcionamento=extension_data.horario_funcionamento
        )
        return ExtensionResponse.from_orm(extension)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar extensão: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.get("/", response_model=List[ExtensionResponse])
async def list_extensions(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    campanha_id: Optional[int] = None,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Listar extensões com filtros opcionais
    """
    try:
        extensions = await service.list_extensions(
            skip=skip,
            limit=limit,
            ativo=ativo,
            campanha_id=campanha_id
        )
        return [ExtensionResponse.from_orm(ext) for ext in extensions]
    except Exception as e:
        logger.error(f"Erro ao listar extensões: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.get("/{extension_id}", response_model=ExtensionResponse)
async def get_extension(
    extension_id: int,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Obter uma extensão específica
    """
    try:
        extension = await service.get_extension(extension_id)
        if not extension:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extensão não encontrada")
        return ExtensionResponse.from_orm(extension)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.put("/{extension_id}", response_model=ExtensionResponse)
async def update_extension(
    extension_id: int,
    extension_data: ExtensionUpdate,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Atualizar uma extensão
    """
    try:
        extension = await service.update_extension(
            extension_id=extension_id,
            **extension_data.dict(exclude_unset=True)
        )
        if not extension:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extensão não encontrada")
        return ExtensionResponse.from_orm(extension)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao atualizar extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.delete("/{extension_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_extension(
    extension_id: int,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Deletar uma extensão
    """
    try:
        success = await service.delete_extension(extension_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extensão não encontrada")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.post("/{extension_id}/toggle-status", response_model=ExtensionResponse)
async def toggle_extension_status(
    extension_id: int,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Alternar status ativo/inativo da extensão
    """
    try:
        extension = await service.toggle_status(extension_id)
        if not extension:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extensão não encontrada")
        return ExtensionResponse.from_orm(extension)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alternar status da extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.get("/{extension_id}/stats", response_model=ExtensionStatsResponse)
async def get_extension_stats(
    extension_id: int,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Obter estatísticas de uma extensão
    """
    try:
        stats = await service.get_extension_stats(extension_id)
        if not stats:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estatísticas não encontradas")
        return ExtensionStatsResponse.from_orm(stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas da extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.post("/{extension_id}/test-connectivity")
async def test_extension_connectivity(
    extension_id: int,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Testar conectividade da extensão
    """
    try:
        result = await service.test_connectivity(extension_id)
        return result
    except Exception as e:
        logger.error(f"Erro ao testar conectividade da extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.get("/available/for-dialing")
async def get_available_extensions(
    campanha_id: Optional[int] = None,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Obter extensões disponíveis para discagem
    """
    try:
        extensions = await service.get_available_extensions(campanha_id)
        return [ExtensionResponse.from_orm(ext) for ext in extensions]
    except Exception as e:
        logger.error(f"Erro ao obter extensões disponíveis: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.get("/stats/summary")
async def get_extensions_summary(
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Obter resumo das estatísticas de todas as extensões
    """
    try:
        summary = await service.get_extensions_summary()
        return summary
    except Exception as e:
        logger.error(f"Erro ao obter resumo das extensões: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.post("/{extension_id}/config", status_code=status.HTTP_201_CREATED)
async def create_extension_config(
    extension_id: int,
    config_data: ExtensionConfigCreate,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Criar configuração avançada para uma extensão
    """
    try:
        config = await service.create_extension_config(
            extension_id=extension_id,
            **config_data.dict(exclude_unset=True)
        )
        return config.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar configuração da extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.get("/{extension_id}/config")
async def get_extension_config(
    extension_id: int,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Obter configuração avançada de uma extensão
    """
    try:
        config = await service.get_extension_config(extension_id)
        if not config:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuração não encontrada")
        return config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração da extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.post("/{extension_id}/asterisk/generate-config")
async def generate_asterisk_config(
    extension_id: int,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Gerar configuração do Asterisk para a extensão
    """
    try:
        config = await service.generate_asterisk_config(extension_id)
        return {"config": config, "message": "Configuração gerada com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao gerar configuração Asterisk para extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.post("/{extension_id}/asterisk/reload")
async def reload_asterisk_config(
    extension_id: int,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Recarregar configuração do Asterisk para a extensão
    """
    try:
        result = await service.reload_asterisk_config(extension_id)
        return result
    except Exception as e:
        logger.error(f"Erro ao recarregar configuração Asterisk para extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.get("/{extension_id}/logs")
async def get_extension_logs(
    extension_id: int,
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Obter logs de atividades de uma extensão
    """
    try:
        logs = await service.get_extension_logs(
            extension_id=extension_id,
            skip=skip,
            limit=limit,
            event_type=event_type
        )
        return [log.to_dict() for log in logs]
    except Exception as e:
        logger.error(f"Erro ao obter logs da extensão {extension_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.post("/bulk-import")
async def bulk_import_extensions(
    extensions_data: List[ExtensionCreate],
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Importar múltiplas extensões em lote
    """
    try:
        results = await service.bulk_import_extensions(extensions_data)
        return results
    except Exception as e:
        logger.error(f"Erro ao importar extensões em lote: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.post("/bulk-update-status")
async def bulk_update_status(
    extension_ids: List[int],
    ativo: bool,
    service: ExtensionService = Depends(get_extension_service)
):
    """
    Atualizar status de múltiplas extensões
    """
    try:
        results = await service.bulk_update_status(extension_ids, ativo)
        return results
    except Exception as e:
        logger.error(f"Erro ao atualizar status em lote: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")