"""
Rotas para gerenciar configurações avançadas de discagem.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import obtener_sesion
try:
    from app.services.configuracao_discagem_service import ConfiguracaoDiscagemService
    from app.schemas.configuracao_discagem import (
        ConfiguracaoDiscagemCreate,
        ConfiguracaoDiscagemUpdate,
        ConfiguracaoDiscagemResponse,
        ConfiguracaoDiscagemListResponse,
        CampanhaConfiguracaoOverride,
        CampanhaConfiguracaoResponse,
        HistoricoConfiguracaoResponse
    )
    CONFIGURACAO_DISCAGEM_DISPONIVEL = True
except ImportError:
    # Fallback caso os módulos não estejam disponíveis
    ConfiguracaoDiscagemService = None
    CONFIGURACAO_DISCAGEM_DISPONIVEL = False
    
from app.utils.logger import logger

router = APIRouter(prefix="/configuracao-discagem", tags=["Configuração de Discagem"])


def verificar_disponibilidade():
    """Verifica se a funcionalidade está disponível."""
    if not CONFIGURACAO_DISCAGEM_DISPONIVEL:
        raise HTTPException(
            status_code=503,
            detail="Funcionalidade de configuração avançada não disponível nesta versão"
        )


@router.post("/", response_model=ConfiguracaoDiscagemResponse if CONFIGURACAO_DISCAGEM_DISPONIVEL else dict)
def criar_configuracao(
    configuracao: ConfiguracaoDiscagemCreate if CONFIGURACAO_DISCAGEM_DISPONIVEL else dict,
    db: Session = Depends(obtener_sesion)
):
    """
    Cria uma nova configuração de discagem avançada.
    
    **Parâmetros principais:**
    - **CPS (Calls Per Second)**: Controla velocidade de discagem
    - **Sleep Time**: Tempo entre chamadas para evitar sobrecarga
    - **Wait Time**: Tempo de espera por resposta
    - **AMD**: Detecção automática de secretária eletrônica
    - **Predictive Ratio**: Quantas chamadas iniciar por agente disponível
    
    **Configurações de compliance:**
    - Respeitar DNC (Do Not Call)
    - Horários permitidos
    - Detecção de fax/ocupado
    """
    verificar_disponibilidade()
    
    try:
        service = ConfiguracaoDiscagemService(db)
        nova_configuracao = service.criar_configuracao(configuracao)
        
        logger.info(f"Nova configuração criada: {nova_configuracao.nome}")
        return nova_configuracao
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao criar configuração: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@router.get("/", response_model=List[ConfiguracaoDiscagemListResponse])
def listar_configuracoes(
    ativas_apenas: bool = Query(True, description="Listar apenas configurações ativas"),
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros"),
    db: Session = Depends(obtener_sesion)
):
    """
    Lista todas as configurações de discagem disponíveis.
    
    **Filtros:**
    - **ativas_apenas**: Mostrar apenas configurações ativas
    - **skip/limit**: Paginação
    
    **Ordenação:** Configuração padrão primeiro, depois por data de criação
    """
    try:
        service = ConfiguracaoDiscagemService(db)
        configuracoes = service.listar_configuracoes(
            ativas_apenas=ativas_apenas,
            skip=skip,
            limit=limit
        )
        
        return configuracoes
        
    except Exception as e:
        logger.error(f"Erro ao listar configurações: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao listar configurações"
        )


@router.get("/default", response_model=Optional[ConfiguracaoDiscagemResponse])
def obter_configuracao_default(db: Session = Depends(obtener_sesion)):
    """
    Obtém a configuração padrão do sistema.
    
    Esta configuração será usada quando uma campanha não tiver
    configuração específica definida.
    """
    try:
        service = ConfiguracaoDiscagemService(db)
        config_default = service.obter_configuracao_default()
        
        return config_default
        
    except Exception as e:
        logger.error(f"Erro ao obter configuração default: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter configuração padrão"
        )


@router.get("/{configuracao_id}", response_model=ConfiguracaoDiscagemResponse)
def obter_configuracao(
    configuracao_id: int,
    db: Session = Depends(obtener_sesion)
):
    """
    Obtém uma configuração específica por ID.
    
    **Retorna:** Todos os detalhes da configuração incluindo:
    - Parâmetros de velocidade (CPS)
    - Configurações de timing
    - Configurações de detecção
    - Configurações de compliance
    - Histórico de modificações
    """
    try:
        service = ConfiguracaoDiscagemService(db)
        configuracao = service.obter_configuracao(configuracao_id)
        
        return configuracao
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração {configuracao_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter configuração"
        )


@router.put("/{configuracao_id}", response_model=ConfiguracaoDiscagemResponse)
def atualizar_configuracao(
    configuracao_id: int,
    configuracao: ConfiguracaoDiscagemUpdate,
    motivo: Optional[str] = Query(None, description="Motivo da alteração"),
    db: Session = Depends(obtener_sesion)
):
    """
    Atualiza uma configuração existente.
    
    **Importante:** 
    - Mudanças são salvas no histórico para auditoria
    - Se a configuração estiver em uso, as mudanças afetarão campanhas ativas
    - Forneça um motivo para facilitar auditoria
    
    **Validações automáticas:**
    - CPS inicial ≤ CPS máximo
    - Horário fim > Horário início
    - Dias da semana válidos (0-6)
    - Valores dentro dos limites permitidos
    """
    try:
        service = ConfiguracaoDiscagemService(db)
        configuracao_atualizada = service.atualizar_configuracao(
            configuracao_id=configuracao_id,
            configuracao_data=configuracao,
            motivo=motivo
        )
        
        return configuracao_atualizada
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar configuração {configuracao_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao atualizar configuração"
        )


@router.delete("/{configuracao_id}")
def excluir_configuracao(
    configuracao_id: int,
    db: Session = Depends(obtener_sesion)
):
    """
    Exclui (desativa) uma configuração.
    
    **Nota:** Exclusão é lógica (soft delete) para preservar histórico.
    
    **Validações:**
    - Não permite excluir se estiver sendo usada em campanhas ativas
    - Configuração padrão só pode ser excluída se houver outra para substituir
    """
    try:
        service = ConfiguracaoDiscagemService(db)
        sucesso = service.excluir_configuracao(configuracao_id)
        
        if sucesso:
            return {"message": f"Configuração {configuracao_id} desativada com sucesso"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Falha ao desativar configuração"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir configuração {configuracao_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao excluir configuração"
        )


@router.post("/{configuracao_id}/clonar", response_model=ConfiguracaoDiscagemResponse)
def clonar_configuracao(
    configuracao_id: int,
    novo_nome: str = Query(..., description="Nome para a nova configuração"),
    db: Session = Depends(obtener_sesion)
):
    """
    Clona uma configuração existente.
    
    **Útil para:**
    - Criar variações de uma configuração que funciona bem
    - Fazer testes com parâmetros similares
    - Backup antes de modificações importantes
    
    **Nota:** O clone nunca será marcado como configuração padrão.
    """
    try:
        service = ConfiguracaoDiscagemService(db)
        configuracao_clonada = service.clonar_configuracao(
            configuracao_id=configuracao_id,
            novo_nome=novo_nome
        )
        
        return configuracao_clonada
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao clonar configuração {configuracao_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao clonar configuração"
        )


@router.get("/{configuracao_id}/historico", response_model=List[HistoricoConfiguracaoResponse])
def obter_historico_configuracao(
    configuracao_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(obtener_sesion)
):
    """
    Obtém o histórico de modificações de uma configuração.
    
    **Inclui:**
    - Snapshots de todas as versões
    - Usuário que fez a modificação
    - Motivo da mudança
    - Métricas de performance do período
    
    **Ordenação:** Mais recente primeiro
    """
    try:
        service = ConfiguracaoDiscagemService(db)
        historico = service.obter_historico(
            configuracao_id=configuracao_id,
            skip=skip,
            limit=limit
        )
        
        return historico
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter histórico da configuração {configuracao_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter histórico"
        )


@router.post("/campanha/{campanha_id}/associar", response_model=CampanhaConfiguracaoResponse)
def associar_configuracao_campanha(
    campanha_id: int,
    configuracao: CampanhaConfiguracaoOverride,
    db: Session = Depends(obtener_sesion)
):
    """
    Associa uma configuração a uma campanha específica.
    
    **Overrides possíveis:**
    - **CPS**: Ajustar velocidade específica para esta campanha
    - **Horários**: Horários diferentes da configuração base
    - **Canais**: Número máximo de canais para esta campanha
    
    **Comportamento:**
    - Desativa associação anterior se existir
    - Overrides são opcionais (usa configuração base se não especificado)
    - Mudanças entram em vigor imediatamente
    """
    try:
        service = ConfiguracaoDiscagemService(db)
        associacao = service.associar_campanha(campanha_id, configuracao)
        
        # Adicionar configuração efetiva na resposta
        configuracao_efetiva = associacao.get_configuracao_efetiva()
        
        response_data = {
            **associacao.__dict__,
            'configuracao_efetiva': configuracao_efetiva
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao associar configuração à campanha {campanha_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao associar configuração"
        )


@router.get("/campanha/{campanha_id}/configuracao")
def obter_configuracao_campanha(
    campanha_id: int,
    db: Session = Depends(obtener_sesion)
):
    """
    Obtém a configuração efetiva de uma campanha.
    
    **Retorna:**
    - Configuração base + overrides aplicados
    - Se não há configuração específica, retorna a configuração padrão
    - Todos os parâmetros prontos para uso pelo discador
    
    **Use este endpoint** para obter os parâmetros que o sistema
    de discagem deve usar para uma campanha específica.
    """
    try:
        service = ConfiguracaoDiscagemService(db)
        configuracao_efetiva = service.obter_configuracao_efetiva_campanha(campanha_id)
        
        return {
            "campanha_id": campanha_id,
            "configuracao": configuracao_efetiva,
            "fonte": "campanha_especifica" if service.obter_configuracao_campanha(campanha_id) else "default"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração da campanha {campanha_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter configuração da campanha"
        )


@router.get("/{configuracao_id}/estatisticas")
def obter_estatisticas_configuracao(
    configuracao_id: int,
    periodo_dias: int = Query(30, ge=1, le=365, description="Período em dias para estatísticas"),
    db: Session = Depends(obtener_sesion)
):
    """
    Obtém estatísticas de uso e performance de uma configuração.
    
    **Métricas incluídas:**
    - Número de campanhas que usam esta configuração
    - Total de chamadas realizadas
    - Taxa de contato e abandono
    - Performance média (CPS, tempo de resposta)
    - Violações de compliance
    
    **Período:** Últimos N dias (padrão: 30 dias)
    """
    try:
        service = ConfiguracaoDiscagemService(db)
        estatisticas = service.obter_estatisticas_configuracao(
            configuracao_id=configuracao_id,
            periodo_dias=periodo_dias
        )
        
        return estatisticas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas da configuração {configuracao_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter estatísticas"
        ) 