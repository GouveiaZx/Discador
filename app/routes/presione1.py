"""
Rotas para gerenciar campanhas de discado preditivo con modo "Presione 1".
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import obtener_sesion
from app.services.presione1_service import PresionE1Service
from app.services.asterisk import asterisk_service
from app.schemas.presione1 import (
    CampanaPresione1Create,
    CampanaPresione1Update,
    CampanaPresione1Response,
    IniciarCampanaRequest,
    PausarCampanaRequest,
    EstadisticasCampanaResponse,
    MonitorCampanaResponse,
    LlamadaPresione1Response
)
from app.utils.logger import logger

router = APIRouter(prefix="/presione1", tags=["Discado Preditivo - Presione 1"])

# Instância global do serviço (será inicializada na primeira requisição)
presione1_service_instance = None


def get_presione1_service(db: Session = Depends(obtener_sesion)) -> PresionE1Service:
    """Obtém instância do serviço Presione1."""
    global presione1_service_instance
    
    if presione1_service_instance is None:
        presione1_service_instance = PresionE1Service(db)
        # Registrar callback para eventos do Asterisk
        asterisk_service.registrar_callback_evento(
            "presione1", 
            presione1_service_instance.processar_evento_asterisk
        )
        logger.info("Serviço Presione1 inicializado e integrado com Asterisk")
    
    # Atualizar sessão DB
    presione1_service_instance.db = db
    return presione1_service_instance


@router.post("/campanhas", response_model=CampanaPresione1Response)
def crear_campana_presione1(
    campana_data: CampanaPresione1Create,
    db: Session = Depends(obtener_sesion),
    service: PresionE1Service = Depends(get_presione1_service)
) -> CampanaPresione1Response:
    """
    Cria uma nova campanha de discado preditivo com modo "Presione 1".
    
    **Características da campanha**:
    - **Lista de números**: Números da lista especificada serão discados automaticamente
    - **Áudio personalizado**: Reproduz mensagem específica quando atendida
    - **Detecção DTMF**: Aguarda usuário pressionar tecla 1
    - **Transferência automática**: Se pressionou 1, transfere para agente/fila
    - **Controle de fluxo**: Chamadas simultâneas e tempo entre chamadas configuráveis
    
    **Exemplo de fluxo**:
    1. Sistema liga para número da lista
    2. Quando atendido, reproduz áudio: "Presione 1 para falar com um atendente"
    3. Se pressionar 1: transfere para agente
    4. Se não pressionar ou pressionar outra tecla: encerra
    """
    try:
        campana = service.crear_campana(campana_data)
        return CampanaPresione1Response.from_orm(campana)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar campanha Presione 1: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao criar campanha"
        )


@router.get("/campanhas", response_model=List[CampanaPresione1Response])
def listar_campanhas_presione1(
    skip: int = 0,
    limit: int = 100,
    apenas_ativas: bool = False,
    service: PresionE1Service = Depends(get_presione1_service)
) -> List[CampanaPresione1Response]:
    """
    Lista campanhas de discado preditivo Presione 1.
    
    **Filtros disponíveis**:
    - `apenas_ativas`: Mostra só campanhas atualmente ativas
    - Paginação com `skip` e `limit`
    """
    try:
        campanhas = service.listar_campanas(skip, limit, apenas_ativas)
        return [CampanaPresione1Response.from_orm(c) for c in campanhas]
        
    except Exception as e:
        logger.error(f"Erro ao listar campanhas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao listar campanhas"
        )


@router.get("/campanhas/{campana_id}", response_model=CampanaPresione1Response)
def obter_campana_presione1(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> CampanaPresione1Response:
    """Obtém detalhes de uma campanha específica."""
    try:
        campana = service.obter_campana(campana_id)
        return CampanaPresione1Response.from_orm(campana)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter campanha"
        )


@router.put("/campanhas/{campana_id}", response_model=CampanaPresione1Response)
def atualizar_campana_presione1(
    campana_id: int,
    dados_atualizacao: CampanaPresione1Update,
    service: PresionE1Service = Depends(get_presione1_service)
) -> CampanaPresione1Response:
    """
    Atualiza configurações de uma campanha.
    
    **Nota**: Campanhas ativas não podem ser editadas. 
    Pare a campanha primeiro para fazer alterações.
    """
    try:
        campana = service.atualizar_campana(campana_id, dados_atualizacao)
        return CampanaPresione1Response.from_orm(campana)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao atualizar campanha"
        )


@router.post("/campanhas/{campana_id}/iniciar")
async def iniciar_campana_presione1(
    campana_id: int,
    request: IniciarCampanaRequest,
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    Inicia uma campanha de discado preditivo.
    
    **O que acontece**:
    1. **Validação**: Verifica se há números disponíveis na lista
    2. **Ativação**: Marca campanha como ativa
    3. **Discado automático**: Inicia processo de discado em background
    4. **Chamadas simultâneas**: Respeita limite configurado
    5. **Fluxo contínuo**: Continua até acabar números ou ser parada
    
    **Monitoramento**: Use `/campanhas/{id}/monitor` para acompanhar progresso
    """
    try:
        resultado = await service.iniciar_campana(campana_id, request.usuario_id)
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao iniciar campanha"
        )


@router.post("/campanhas/{campana_id}/pausar")
async def pausar_campana_presione1(
    campana_id: int,
    request: PausarCampanaRequest,
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    Pausa ou retoma uma campanha ativa.
    
    **Pausar** (`pausar: true`):
    - Pausa discado de novos números
    - Chamadas em andamento continuam normalmente
    - Pode ser retomada a qualquer momento
    
    **Retomar** (`pausar: false`):
    - Retoma discado automático
    - Continua de onde parou
    """
    try:
        resultado = await service.pausar_campana(campana_id, request.pausar, request.motivo)
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao pausar campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao pausar campanha"
        )


@router.post("/campanhas/{campana_id}/parar")
async def parar_campana_presione1(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    Para completamente uma campanha.
    
    **Ação**:
    - Marca campanha como inativa
    - Finaliza todas as chamadas em andamento
    - Para o discado automático
    - Remove da lista de campanhas ativas
    
    **Nota**: Para reiniciar será necessário usar `/iniciar` novamente
    """
    try:
        resultado = await service.parar_campana(campana_id)
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao parar campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao parar campanha"
        )


@router.get("/campanhas/{campana_id}/estadisticas", response_model=EstadisticasCampanaResponse)
def obter_estadisticas_campana(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> EstadisticasCampanaResponse:
    """
    Obtém estatísticas detalhadas de uma campanha.
    
    **Métricas incluídas**:
    - **Contadores**: Total, realizadas, pendentes, atendidas
    - **Resultados**: Quantos pressionaram 1, transferências exitosas
    - **Taxas**: Atendimento, interesse (presione 1), transferência
    - **Tempos**: Resposta média, duração média das chamadas
    - **Estado atual**: Ativa, pausada, chamadas em andamento
    
    **Útil para**: Dashboards de monitoramento e relatórios
    """
    try:
        estadisticas = service.obter_estadisticas_campana(campana_id)
        return estadisticas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas da campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter estatísticas"
        )


@router.get("/campanhas/{campana_id}/monitor", response_model=MonitorCampanaResponse)
def monitorar_campana_presione1(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> MonitorCampanaResponse:
    """
    Monitoramento em tempo real de uma campanha.
    
    **Informações em tempo real**:
    - **Estado da campanha**: Ativa, pausada, parada
    - **Chamadas ativas**: Lista de chamadas em andamento
    - **Últimas chamadas**: Últimas finalizadas com resultados
    - **Estatísticas atuais**: Números atualizados
    
    **Uso**: Para dashboards de monitoramento ao vivo
    """
    try:
        # Obter dados básicos
        estadisticas = service.obter_estadisticas_campana(campana_id)
        campana = service.obter_campana(campana_id)
        
        # Determinar estado da campanha
        if campana.activa:
            if campana.pausada:
                estado_campana = "pausada"
            else:
                estado_campana = "ativa"
        else:
            estado_campana = "parada"
        
        # Obter chamadas ativas (simulação - na implementação real viria do service)
        llamadas_activas = []
        ultimas_llamadas = []
        
        # TODO: Implementar consultas reais quando service tiver os métodos
        
        return MonitorCampanaResponse(
            campana_id=campana_id,
            estado_campana=estado_campana,
            llamadas_activas=llamadas_activas,
            ultimas_llamadas=ultimas_llamadas,
            estadisticas=estadisticas
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no monitoramento da campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno no monitoramento"
        )


@router.get("/campanhas/{campana_id}/llamadas", response_model=List[LlamadaPresione1Response])
def listar_llamadas_campana(
    campana_id: int,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    presiono_1: Optional[bool] = None,
    service: PresionE1Service = Depends(get_presione1_service)
) -> List[LlamadaPresione1Response]:
    """
    Lista chamadas de uma campanha específica.
    
    **Filtros disponíveis**:
    - `estado`: Filtrar por estado específico
    - `presiono_1`: true (pressionaram 1), false (não pressionaram), null (todos)
    - Paginação com `skip` e `limit`
    
    **Estados possíveis**:
    - `pendiente`, `marcando`, `contestada`, `audio_reproducido`
    - `esperando_dtmf`, `presiono_1`, `no_presiono`, `transferida`, `finalizada`, `error`
    """
    try:
        # TODO: Implementar no service
        # Por enquanto retorna lista vazia
        logger.info(f"Listando chamadas da campanha {campana_id}")
        return []
        
    except Exception as e:
        logger.error(f"Erro ao listar chamadas da campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao listar chamadas"
        )


@router.get("/campanhas/{campana_id}/proximo-numero")
def obter_proximo_numero_campana(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    Obtém o próximo número que será discado na campanha.
    
    **Útil para**:
    - Verificar progresso da campanha
    - Debug e monitoramento
    - Validar se há números disponíveis
    
    **Resposta**:
    - Se há próximo número: dados do número
    - Se não há: `null` com mensagem
    """
    try:
        proximo = service.obter_proximo_numero(campana_id)
        
        if proximo:
            return {
                "estado": "disponible",
                "proximo_numero": proximo
            }
        else:
            return {
                "estado": "sin_numeros",
                "mensaje": f"Não há mais números disponíveis na campanha {campana_id}",
                "proximo_numero": None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter próximo número da campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter próximo número"
        ) 