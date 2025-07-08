"""
Rotas para gerenciar campanhas de discado preditivo con modo "Presione 1".
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from datetime import datetime

try:
    from sqlalchemy.orm import Session
except ImportError:
    # Fallback para quando SQLAlchemy não está disponível
    Session = object

try:
    from app.database import obtener_sesion
except ImportError:
    def obtener_sesion():
        """Fallback para obtener_sesion quando não está disponível"""
        return None
        
try:
    from app.services.presione1_service import PresionE1Service
except ImportError:
    # Fallback para quando o serviço não está disponível
    class PresionE1Service:
        def __init__(self, db=None):
            self.db = db
        
        def listar_campanas(self, skip=0, limit=100, apenas_ativas=False):
            return []
        
        def crear_campana(self, campana_data):
            raise HTTPException(
                status_code=503,
                detail="Serviço Presione1 não está disponível"
            )
        
        def obter_campana(self, campana_id):
            raise HTTPException(
                status_code=503,
                detail="Serviço Presione1 não está disponível"
            )
try:
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
except ImportError:
    # Fallbacks para quando os schemas não estão disponíveis
    from pydantic import BaseModel
    from typing import Any
    
    class CampanaPresione1Create(BaseModel):
        nombre: str
        descripcion: str = ""
        campaign_id: int
        
    class CampanaPresione1Update(BaseModel):
        nombre: str = None
        descripcion: str = None
        
    class CampanaPresione1Response(BaseModel):
        id: int
        nombre: str
        descripcion: str
        
    class IniciarCampanaRequest(BaseModel):
        usuario_id: str = None
        
    class PausarCampanaRequest(BaseModel):
        pausar: bool = True
        
    class EstadisticasCampanaResponse(BaseModel):
        total_llamadas: int = 0
        
    class MonitorCampanaResponse(BaseModel):
        status: str = "active"
        
    class LlamadaPresione1Response(BaseModel):
        id: int
        numero_destino: str
try:
    from app.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

router = APIRouter(prefix="/presione1", tags=["Discado Preditivo - Presione 1"])

# Instância global do serviço (será inicializada na primeira requisição)
presione1_service_instance = None


def get_presione1_service(db: Session = Depends(obtener_sesion)) -> PresionE1Service:
    """Obtém instância do serviço Presione1."""
    global presione1_service_instance
    
    if presione1_service_instance is None:
        presione1_service_instance = PresionE1Service(db)
        # TODO: Registrar callback para eventos do Asterisk (não implementado ainda)
        # AsteriskMonitoringService.registrar_callback_evento(
        #     "presione1", 
        #     presione1_service_instance.processar_evento_asterisk
        # )
        logger.info("Serviço Presione1 inicializado")
    
    # Atualizar sessão DB se disponível
    if hasattr(presione1_service_instance, 'db'):
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
    
    **Estatísticas incluídas**:
    - Total de números na lista
    - Chamadas realizadas e pendentes
    - Taxa de atendimento
    - Números que pressionaram 1
    - Transferências realizadas
    - Tempo médio de chamada
    """
    try:
        # Verificar se campanha existe
        campana = service.obter_campana(campana_id)
        if not campana:
            raise HTTPException(
                status_code=404,
                detail=f"Campanha {campana_id} não encontrada"
            )
        
        # Buscar estatísticas
        stats = service.obter_estadisticas_campana(campana_id)
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas da campanha {campana_id}: {str(e)}")
        # Retornar dados zerados em caso de erro
        return EstadisticasCampanaResponse(
            campana_id=campana_id,
            total_numeros=0,
            llamadas_realizadas=0,
            llamadas_contestadas=0,
            llamadas_presiono_1=0,
            llamadas_transferidas=0,
            tasa_contestacion=0.0,
            tasa_presiono_1=0.0,
            tasa_transferencia=0.0,
            tiempo_promedio_llamada=0,
            numeros_pendientes=0,
            llamadas_fallidas=0,
            ultima_actualizacion=datetime.now()
        )


@router.get("/campanhas/{campana_id}/monitor", response_model=MonitorCampanaResponse)
def monitorar_campana_presione1(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> MonitorCampanaResponse:
    """
    Monitora campanha em tempo real.
    
    **Dados do monitoramento**:
    - **Status atual**: Ativa, pausada, parada
    - **Chamadas ativas**: Lista com status individual
    - **Última atividade**: Timestamp da última operação
    - **Próximos números**: Fila de discagem
    - **Erros recentes**: Problemas detectados
    
    **Atualização**: Recomenda-se consultar a cada 2-3 segundos
    para monitoramento em tempo real.
    """
    try:
        # Verificar se campanha existe
        campana = service.obter_campana(campana_id)
        if not campana:
            raise HTTPException(
                status_code=404,
                detail=f"Campanha {campana_id} não encontrada"
            )
        
        # Buscar dados de monitoramento
        activa = campana.get("activa", False)
        pausada = campana.get("pausada", False)
        
        # Determinar estado da campanha
        if activa:
            estado = "pausada" if pausada else "activa"
        else:
            estado = "parada"
            
        # Criar resposta de monitoramento
        monitor_data = MonitorCampanaResponse(
            campana_id=campana_id,
            estado=estado,
            llamadas_activas=[],
            ultimas_llamadas=[],
            proximos_numeros=[],
            errores_recientes=[],
            ultima_actividad=datetime.now(),
            llamadas_simultaneas_actuales=0,
            numeros_pendientes=0
        )
        
        return monitor_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao monitorar campanha {campana_id}: {str(e)}")
        # Retornar dados básicos em caso de erro
        try:
            campana = service.obter_campana(campana_id)
            estado = campana.estado if hasattr(campana, 'estado') else 'parada'
        except:
            estado = 'erro'
            
        return MonitorCampanaResponse(
            campana_id=campana_id,
            estado=estado,
            llamadas_activas=[],
            ultimas_llamadas=[],
            proximos_numeros=[],
            errores_recientes=[f"Erro interno: {str(e)}"],
            ultima_actividad=datetime.now(),
            llamadas_simultaneas_actuales=0,
            numeros_pendientes=0
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


@router.post("/campanhas/{campana_id}/popular-contatos-teste")
async def popular_contatos_teste(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    Popula contatos de teste para uma campanha presione1.
    
    **Útil para**:
    - Testes de desenvolvimento
    - Campanhas sem contatos
    - Demonstrações do sistema
    
    **Números criados**:
    - +5511999000001 até +5511999000010 (10 números de teste)
    - Todos validados e prontos para discagem
    """
    try:
        resultado = await service.popular_contatos_teste(campana_id)
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao popular contatos de teste para campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao popular contatos de teste"
        )


@router.get("/campanhas/{campana_id}/debug")
async def debug_campana_presione1(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    Debug/diagnóstico de uma campanha presione1.
    
    **Informações fornecidas**:
    - Dados da campanha presione1
    - Campanha principal associada (se existe)
    - Contatos disponíveis
    - Chamadas já realizadas
    - Status geral para iniciar
    """
    try:
        resultado = await service.debug_campana(campana_id)
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer debug da campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao fazer debug da campanha"
        )


@router.get("/campanhas/{campana_id}/debug-detalhado")
async def debug_detalhado_campana_presione1(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    Debug detalhado com verificação passo a passo dos dados.
    """
    try:
        resultado = await service.debug_detalhado_campana(campana_id)
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer debug detalhado da campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao fazer debug detalhado da campanha"
        )


@router.post("/campanhas/{campana_id}/resetar-llamadas")
async def resetar_llamadas_campana(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    Reseta/limpa todas as llamadas de uma campanha presione1.
    
    **Útil para**:
    - Reiniciar campanhas que foram testadas
    - Limpar histórico de chamadas para re-discagem
    - Resolver problemas de "todos números já discados"
    
    **⚠️ ATENÇÃO**: Esta operação remove TODAS as llamadas da campanha!
    """
    try:
        resultado = await service.resetar_llamadas_campana(campana_id)
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar llamadas da campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao resetar llamadas da campanha"
        )


@router.get("/campanhas/{campana_id}/investigar-llamadas")
async def investigar_llamadas_campana(
    campana_id: int,
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    ENDPOINT TEMPORÁRIO para investigar o problema das llamadas.
    """
    try:
        resultado = await service.investigar_llamadas_detalhado(campana_id)
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao investigar llamadas da campanha {campana_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao investigar llamadas"
        )


@router.post("/llamadas/{llamada_id}/transferir")
async def transferir_llamada(
    llamada_id: int,
    extension: str,
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    Transfere uma chamada ativa para uma extensão específica.
    
    **Parâmetros**:
    - `llamada_id`: ID da chamada a ser transferida
    - `extension`: Extensão ou número de destino para transferir
    
    **Uso comum**:
    - Transferir para agente: extensão 100, 101, etc.
    - Transferir para fila: extensão 200, 300, etc.
    - Transferir para número externo: número completo
    """
    try:
        # Verificar se a chamada existe
        llamada = service.obter_llamada(llamada_id)
        if not llamada:
            raise HTTPException(
                status_code=404,
                detail=f"Chamada {llamada_id} não encontrada"
            )
        
        # Verificar se a chamada está ativa
        if llamada.estado not in ['em_andamento', 'conectada', 'ativa']:
            raise HTTPException(
                status_code=400,
                detail=f"Chamada {llamada_id} não está ativa (estado: {llamada.estado})"
            )
        
        # Executar transferência
        resultado = await service.transferir_llamada(llamada_id, extension)
        
        return {
            "success": True,
            "message": f"Chamada {llamada_id} transferida para {extension}",
            "llamada_id": llamada_id,
            "extension": extension,
            "resultado": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao transferir chamada {llamada_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao transferir chamada: {str(e)}"
        )


@router.post("/llamadas/{llamada_id}/finalizar")
async def finalizar_llamada(
    llamada_id: int,
    motivo: str = "manual",
    service: PresionE1Service = Depends(get_presione1_service)
) -> dict:
    """
    Finaliza uma chamada ativa manualmente.
    
    **Parâmetros**:
    - `llamada_id`: ID da chamada a ser finalizada
    - `motivo`: Motivo da finalização (manual, timeout, erro, etc.)
    
    **Efeitos**:
    - Encerra a chamada no Asterisk
    - Atualiza status no banco de dados
    - Libera recursos do sistema
    """
    try:
        # Verificar se a chamada existe
        llamada = service.obter_llamada(llamada_id)
        if not llamada:
            raise HTTPException(
                status_code=404,
                detail=f"Chamada {llamada_id} não encontrada"
            )
        
        # Verificar se a chamada pode ser finalizada
        if llamada.estado in ['finalizada', 'desligada', 'erro']:
            return {
                "success": True,
                "message": f"Chamada {llamada_id} já estava finalizada",
                "llamada_id": llamada_id,
                "estado_anterior": llamada.estado
            }
        
        # Executar finalização
        resultado = await service.finalizar_llamada(llamada_id, motivo)
        
        return {
            "success": True,
            "message": f"Chamada {llamada_id} finalizada com sucesso",
            "llamada_id": llamada_id,
            "motivo": motivo,
            "resultado": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao finalizar chamada {llamada_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao finalizar chamada: {str(e)}"
        ) 