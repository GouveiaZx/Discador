"""
Serviço para gerenciar configurações avançadas de discagem.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

try:
    from app.models.configuracao_discagem import (
        ConfiguracaoDiscagem, 
        HistoricoConfiguracaoDiscagem,
        CampanhaConfiguracaoDiscagem
    )
    from app.schemas.configuracao_discagem import (
        ConfiguracaoDiscagemCreate,
        ConfiguracaoDiscagemUpdate,
        CampanhaConfiguracaoOverride
    )
    CONFIGURACAO_DISCAGEM_DISPONIVEL = True
except ImportError:
    # Fallback caso os módulos não estejam disponíveis
    ConfiguracaoDiscagem = None
    HistoricoConfiguracaoDiscagem = None
    CampanhaConfiguracaoDiscagem = None
    ConfiguracaoDiscagemCreate = None
    ConfiguracaoDiscagemUpdate = None
    CampanhaConfiguracaoOverride = None
    CONFIGURACAO_DISCAGEM_DISPONIVEL = False

from app.utils.logger import logger


class ConfiguracaoDiscagemService:
    """Serviço para configurações de discagem."""
    
    def __init__(self, db: Session):
        if not CONFIGURACAO_DISCAGEM_DISPONIVEL:
            raise HTTPException(
                status_code=503,
                detail="Funcionalidade de configuração avançada não disponível nesta versão"
            )
        self.db = db
    
    def criar_configuracao(
        self, 
        configuracao_data: ConfiguracaoDiscagemCreate,
        usuario_id: Optional[int] = None
    ) -> ConfiguracaoDiscagem:
        """Cria uma nova configuração de discagem."""
        
        # Verificar se nome já existe
        existente = self.db.query(ConfiguracaoDiscagem).filter(
            ConfiguracaoDiscagem.nome == configuracao_data.nome
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe uma configuração com o nome '{configuracao_data.nome}'"
            )
        
        # Se é marcada como default, remover default das outras
        if configuracao_data.es_default:
            self._remover_defaults()
        
        try:
            configuracao = ConfiguracaoDiscagem(
                **configuracao_data.dict(),
                usuario_creador_id=usuario_id
            )
            
            self.db.add(configuracao)
            self.db.commit()
            self.db.refresh(configuracao)
            
            logger.info(f"Configuração criada: {configuracao.nome} (ID: {configuracao.id})")
            return configuracao
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Erro de integridade ao criar configuração: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Erro de integridade nos dados da configuração"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro inesperado ao criar configuração: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao criar configuração"
            )
    
    def listar_configuracoes(
        self, 
        ativas_apenas: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ConfiguracaoDiscagem]:
        """Lista configurações de discagem."""
        
        query = self.db.query(ConfiguracaoDiscagem)
        
        if ativas_apenas:
            query = query.filter(ConfiguracaoDiscagem.activa == True)
        
        return query.order_by(
            ConfiguracaoDiscagem.es_default.desc(),
            ConfiguracaoDiscagem.fecha_creacion.desc()
        ).offset(skip).limit(limit).all()
    
    def obter_configuracao(self, configuracao_id: int) -> ConfiguracaoDiscagem:
        """Obtém uma configuração por ID."""
        
        configuracao = self.db.query(ConfiguracaoDiscagem).filter(
            ConfiguracaoDiscagem.id == configuracao_id
        ).first()
        
        if not configuracao:
            raise HTTPException(
                status_code=404,
                detail=f"Configuração com ID {configuracao_id} não encontrada"
            )
        
        return configuracao
    
    def obter_configuracao_default(self) -> Optional[ConfiguracaoDiscagem]:
        """Obtém a configuração padrão."""
        
        return self.db.query(ConfiguracaoDiscagem).filter(
            ConfiguracaoDiscagem.es_default == True,
            ConfiguracaoDiscagem.activa == True
        ).first()
    
    def atualizar_configuracao(
        self,
        configuracao_id: int,
        configuracao_data: ConfiguracaoDiscagemUpdate,
        usuario_id: Optional[int] = None,
        motivo: Optional[str] = None
    ) -> ConfiguracaoDiscagem:
        """Atualiza uma configuração existente."""
        
        configuracao = self.obter_configuracao(configuracao_id)
        
        # Se está marcando como default, remover default das outras
        if configuracao_data.es_default:
            self._remover_defaults()
        
        # Salvar snapshot antes da mudança
        if motivo:
            self._salvar_historico(configuracao, usuario_id, motivo)
        
        try:
            # Atualizar apenas campos fornecidos
            update_data = configuracao_data.dict(exclude_unset=True)
            
            for campo, valor in update_data.items():
                setattr(configuracao, campo, valor)
            
            self.db.commit()
            self.db.refresh(configuracao)
            
            logger.info(f"Configuração atualizada: {configuracao.nome} (ID: {configuracao_id})")
            return configuracao
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar configuração {configuracao_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao atualizar configuração"
            )
    
    def excluir_configuracao(self, configuracao_id: int) -> bool:
        """Exclui uma configuração (soft delete)."""
        
        configuracao = self.obter_configuracao(configuracao_id)
        
        # Verificar se está sendo usada em campanhas ativas
        campanhas_ativas = self.db.query(CampanhaConfiguracaoDiscagem).filter(
            CampanhaConfiguracaoDiscagem.configuracao_discagem_id == configuracao_id,
            CampanhaConfiguracaoDiscagem.activa == True
        ).count()
        
        if campanhas_ativas > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir: configuração está sendo usada em {campanhas_ativas} campanhas ativas"
            )
        
        try:
            configuracao.activa = False
            self.db.commit()
            
            logger.info(f"Configuração desativada: {configuracao.nome} (ID: {configuracao_id})")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao desativar configuração {configuracao_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao desativar configuração"
            )
    
    def associar_campanha(
        self,
        campanha_id: int,
        configuracao_data: CampanhaConfiguracaoOverride
    ) -> CampanhaConfiguracaoDiscagem:
        """Associa uma configuração a uma campanha com possíveis overrides."""
        
        # Verificar se configuração existe
        configuracao = self.obter_configuracao(configuracao_data.configuracao_discagem_id)
        
        # Desativar associação anterior se existir
        self.db.query(CampanhaConfiguracaoDiscagem).filter(
            CampanhaConfiguracaoDiscagem.campanha_id == campanha_id,
            CampanhaConfiguracaoDiscagem.activa == True
        ).update({"activa": False})
        
        try:
            associacao = CampanhaConfiguracaoDiscagem(
                campanha_id=campanha_id,
                **configuracao_data.dict()
            )
            
            self.db.add(associacao)
            self.db.commit()
            self.db.refresh(associacao)
            
            logger.info(f"Configuração {configuracao.nome} associada à campanha {campanha_id}")
            return associacao
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao associar configuração à campanha: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao associar configuração"
            )
    
    def obter_configuracao_campanha(self, campanha_id: int) -> Optional[CampanhaConfiguracaoDiscagem]:
        """Obtém a configuração ativa de uma campanha."""
        
        return self.db.query(CampanhaConfiguracaoDiscagem).filter(
            CampanhaConfiguracaoDiscagem.campanha_id == campanha_id,
            CampanhaConfiguracaoDiscagem.activa == True
        ).first()
    
    def obter_configuracao_efetiva_campanha(self, campanha_id: int) -> Dict[str, Any]:
        """Obtém a configuração efetiva (com overrides) para uma campanha."""
        
        associacao = self.obter_configuracao_campanha(campanha_id)
        
        if associacao:
            return associacao.get_configuracao_efetiva()
        
        # Se não tem configuração específica, usar a default
        config_default = self.obter_configuracao_default()
        if config_default:
            return config_default.to_dict()
        
        raise HTTPException(
            status_code=404,
            detail="Nenhuma configuração encontrada para a campanha"
        )
    
    def obter_historico(
        self,
        configuracao_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[HistoricoConfiguracaoDiscagem]:
        """Obtém o histórico de uma configuração."""
        
        return self.db.query(HistoricoConfiguracaoDiscagem).filter(
            HistoricoConfiguracaoDiscagem.configuracao_id == configuracao_id
        ).order_by(
            HistoricoConfiguracaoDiscagem.fecha_inicio.desc()
        ).offset(skip).limit(limit).all()
    
    def clonar_configuracao(
        self,
        configuracao_id: int,
        novo_nome: str,
        usuario_id: Optional[int] = None
    ) -> ConfiguracaoDiscagem:
        """Clona uma configuração existente."""
        
        configuracao_original = self.obter_configuracao(configuracao_id)
        
        # Criar dados para nova configuração
        dados_clone = configuracao_original.to_dict()
        dados_clone.pop('id')
        dados_clone.pop('fecha_creacion')
        dados_clone.pop('fecha_actualizacion')
        dados_clone['nome'] = novo_nome
        dados_clone['es_default'] = False  # Clone nunca é default
        
        configuracao_create = ConfiguracaoDiscagemCreate(**dados_clone)
        
        return self.criar_configuracao(configuracao_create, usuario_id)
    
    def _remover_defaults(self):
        """Remove a marcação de default de todas as configurações."""
        
        self.db.query(ConfiguracaoDiscagem).filter(
            ConfiguracaoDiscagem.es_default == True
        ).update({"es_default": False})
    
    def _salvar_historico(
        self,
        configuracao: ConfiguracaoDiscagem,
        usuario_id: Optional[int],
        motivo: str
    ):
        """Salva um snapshot da configuração no histórico."""
        
        try:
            historico = HistoricoConfiguracaoDiscagem(
                configuracao_id=configuracao.id,
                configuracao_snapshot=configuracao.to_dict(),
                usuario_modificador_id=usuario_id,
                motivo_cambio=motivo,
                fecha_inicio=configuracao.fecha_actualizacion
            )
            
            self.db.add(historico)
            # Não fazer commit aqui, será feito junto com a atualização
            
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {str(e)}")
            # Não falhar a operação principal por erro no histórico
    
    def obter_estatisticas_configuracao(
        self,
        configuracao_id: int,
        periodo_dias: int = 30
    ) -> Dict[str, Any]:
        """Obtém estatísticas de uso de uma configuração."""
        
        configuracao = self.obter_configuracao(configuracao_id)
        
        # Aqui você implementaria as consultas para estatísticas
        # Por agora, retornando estrutura básica
        
        return {
            'configuracao_id': configuracao_id,
            'nome': configuracao.nome,
            'campanhas_ativas': 0,  # Implementar consulta
            'total_llamadas': 0,    # Implementar consulta
            'tasa_contacto': 0.0,   # Implementar consulta
            'periodo_dias': periodo_dias
        } 