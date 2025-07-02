#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servico Multi-SIP para gerenciamento de multiplos provedores
Sistema de roteamento inteligente de chamadas
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.multi_sip import ProvedorSip, TarifaSip, ConfiguracaoMultiSip
from app.schemas.multi_sip import (
    ProvedorSipCreate, ProvedorSipResponse,
    TarifaSipCreate, TarifaSipResponse,
    ConfiguracaoMultiSipCreate, ConfiguracaoMultiSipResponse,
    EstatisticasProvedor, EstatisticasGerais
)

logger = logging.getLogger(__name__)

class MultiSipService:
    """Servico principal para gerenciamento Multi-SIP"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ================== PROVEDORES SIP ==================
    
    def criar_provedor(self, provedor_data: ProvedorSipCreate) -> ProvedorSipResponse:
        """Cria um novo provedor SIP"""
        try:
            provedor = ProvedorSip(**provedor_data.dict())
            self.db.add(provedor)
            self.db.commit()
            self.db.refresh(provedor)
            
            logger.info(f"Provedor SIP criado: {provedor.nome}")
            return ProvedorSipResponse.from_orm(provedor)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar provedor SIP: {e}")
            raise
    
    def listar_provedores(self, apenas_ativos: bool = True) -> List[ProvedorSipResponse]:
        """Lista todos os provedores SIP"""
        try:
            query = self.db.query(ProvedorSip)
            
            if apenas_ativos:
                query = query.filter(ProvedorSip.status == "ativo")
            
            provedores = query.order_by(ProvedorSip.prioridade).all()
            return [ProvedorSipResponse.from_orm(p) for p in provedores]
        
        except Exception as e:
            logger.error(f"Erro ao listar provedores: {e}")
            raise
    
    def obter_provedor(self, provedor_id: int) -> Optional[ProvedorSipResponse]:
        """Obtem um provedor especifico"""
        try:
            provedor = self.db.query(ProvedorSip).filter(
                ProvedorSip.id == provedor_id
            ).first()
            
            if provedor:
                return ProvedorSipResponse.from_orm(provedor)
            return None
        
        except Exception as e:
            logger.error(f"Erro ao obter provedor {provedor_id}: {e}")
            raise
    
    def atualizar_provedor(self, provedor_id: int, dados_atualizacao: Dict[str, Any]) -> Optional[ProvedorSipResponse]:
        """Atualiza um provedor SIP"""
        try:
            provedor = self.db.query(ProvedorSip).filter(
                ProvedorSip.id == provedor_id
            ).first()
            
            if not provedor:
                return None
            
            for campo, valor in dados_atualizacao.items():
                if hasattr(provedor, campo):
                    setattr(provedor, campo, valor)
            
            provedor.data_atualizacao = datetime.utcnow()
            self.db.commit()
            self.db.refresh(provedor)
            
            logger.info(f"Provedor {provedor_id} atualizado")
            return ProvedorSipResponse.from_orm(provedor)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar provedor {provedor_id}: {e}")
            raise
    
    def deletar_provedor(self, provedor_id: int) -> bool:
        """Deleta um provedor SIP"""
        try:
            provedor = self.db.query(ProvedorSip).filter(
                ProvedorSip.id == provedor_id
            ).first()
            
            if not provedor:
                return False
            
            self.db.delete(provedor)
            self.db.commit()
            
            logger.info(f"Provedor {provedor_id} deletado")
            return True
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar provedor {provedor_id}: {e}")
            raise
    
    # ================== TARIFAS ==================
    
    def criar_tarifa(self, tarifa_data: TarifaSipCreate) -> TarifaSipResponse:
        """Cria uma nova tarifa SIP"""
        try:
            tarifa = TarifaSip(**tarifa_data.dict())
            self.db.add(tarifa)
            self.db.commit()
            self.db.refresh(tarifa)
            
            logger.info(f"Tarifa criada para provedor {tarifa.provedor_id} - {tarifa.nome_destino}")
            return TarifaSipResponse.from_orm(tarifa)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar tarifa: {e}")
            raise
    
    def buscar_melhor_tarifa(self, numero_destino: str) -> Optional[Tuple[ProvedorSipResponse, TarifaSipResponse]]:
        """Busca a melhor tarifa para um numero de destino"""
        try:
            # Extrair prefixos possiveis do numero
            prefixos = self._extrair_prefixos(numero_destino)
            
            # Buscar tarifas ativas para os prefixos
            tarifas = self.db.query(TarifaSip, ProvedorSip).join(
                ProvedorSip, TarifaSip.provedor_id == ProvedorSip.id
            ).filter(
                and_(
                    TarifaSip.prefixo.in_(prefixos),
                    TarifaSip.ativo == True,
                    ProvedorSip.status == "ativo",
                    or_(
                        TarifaSip.data_fim_vigencia.is_(None),
                        TarifaSip.data_fim_vigencia >= datetime.utcnow()
                    )
                )
            ).order_by(
                TarifaSip.custo_por_minuto.asc(),
                ProvedorSip.prioridade.asc()
            ).all()
            
            if tarifas:
                tarifa, provedor = tarifas[0]
                return (
                    ProvedorSipResponse.from_orm(provedor),
                    TarifaSipResponse.from_orm(tarifa)
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Erro ao buscar melhor tarifa para {numero_destino}: {e}")
            raise
    
    def _extrair_prefixos(self, numero: str) -> List[str]:
        """Extrai todos os prefixos possiveis de um numero"""
        numero_limpo = ''.join(filter(str.isdigit, numero))
        prefixos = []
        
        # Gerar prefixos de tamanho decrescente
        for i in range(min(len(numero_limpo), 8), 0, -1):
            prefixos.append(numero_limpo[:i])
        
        return prefixos
    
    # ================== CONFIGURACOES ==================
    
    def criar_configuracao(self, config_data: ConfiguracaoMultiSipCreate) -> ConfiguracaoMultiSipResponse:
        """Cria uma nova configuracao Multi-SIP"""
        try:
            config = ConfiguracaoMultiSip(**config_data.dict())
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
            
            logger.info(f"Configuracao Multi-SIP criada: {config.nome_configuracao}")
            return ConfiguracaoMultiSipResponse.from_orm(config)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar configuracao: {e}")
            raise
    
    def obter_configuracao_ativa(self) -> Optional[ConfiguracaoMultiSipResponse]:
        """Obtem a configuracao ativa do sistema"""
        try:
            config = self.db.query(ConfiguracaoMultiSip).filter(
                ConfiguracaoMultiSip.ativo == True
            ).first()
            
            if config:
                return ConfiguracaoMultiSipResponse.from_orm(config)
            return None
        
        except Exception as e:
            logger.error(f"Erro ao obter configuracao ativa: {e}")
            raise
    
    # ================== ROTEAMENTO INTELIGENTE ==================
    
    def selecionar_provedor_inteligente(self, numero_destino: str) -> Optional[Dict[str, Any]]:
        """Seleciona o melhor provedor usando algoritmo inteligente"""
        try:
            config = self.obter_configuracao_ativa()
            if not config:
                logger.warning("Nenhuma configuracao ativa encontrada")
                return None
            
            # Buscar provedores disponiveis
            resultado_tarifa = self.buscar_melhor_tarifa(numero_destino)
            if not resultado_tarifa:
                logger.warning(f"Nenhuma tarifa encontrada para {numero_destino}")
                return None
            
            provedor, tarifa = resultado_tarifa
            
            # Calcular score baseado na configuracao
            score = self._calcular_score_provedor(provedor, tarifa, config)
            
            return {
                "provedor": provedor,
                "tarifa": tarifa,
                "score": score,
                "algoritmo_usado": config.algoritmo_selecao,
                "timestamp_selecao": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Erro na selecao inteligente para {numero_destino}: {e}")
            raise
    
    def _calcular_score_provedor(self, provedor: ProvedorSipResponse, tarifa: TarifaSipResponse, config: ConfiguracaoMultiSipResponse) -> float:
        """Calcula o score de um provedor baseado nos pesos configurados"""
        try:
            # Score de custo (inverso - menor custo = maior score)
            score_custo = 1.0 / (1.0 + tarifa.custo_por_minuto) if tarifa.custo_por_minuto > 0 else 1.0
            
            # Score de qualidade (baseado na prioridade do provedor)
            score_qualidade = (1000 - provedor.prioridade) / 1000.0
            
            # Score de disponibilidade (baseado no status)
            score_disponibilidade = 1.0 if provedor.status == "ativo" else 0.0
            
            # Calcular score final ponderado
            score_final = (
                config.peso_custo * score_custo +
                config.peso_qualidade * score_qualidade +
                config.peso_disponibilidade * score_disponibilidade
            )
            
            return min(max(score_final, 0.0), 1.0)  # Garantir que esteja entre 0 e 1
        
        except Exception as e:
            logger.error(f"Erro ao calcular score: {e}")
            return 0.0
    
    # ================== ESTATISTICAS ==================
    
    def obter_estatisticas_gerais(self) -> EstatisticasGerais:
        """Obtem estatisticas gerais do sistema"""
        try:
            # Contar provedores
            total_provedores = self.db.query(ProvedorSip).count()
            provedores_ativos = self.db.query(ProvedorSip).filter(
                ProvedorSip.status == "ativo"
            ).count()
            
            # Estatisticas de hoje (simulado - implementar com modelo de chamadas)
            hoje = datetime.utcnow().date()
            
            return EstatisticasGerais(
                total_provedores=total_provedores,
                provedores_ativos=provedores_ativos,
                total_chamadas_hoje=0,  # TODO: Implementar com modelo de chamadas
                taxa_sucesso_geral=0.0,  # TODO: Implementar
                custo_total_hoje=0.0,  # TODO: Implementar
                provedor_mais_usado=None,  # TODO: Implementar
                estatisticas_por_provedor=[]  # TODO: Implementar
            )
        
        except Exception as e:
            logger.error(f"Erro ao obter estatisticas gerais: {e}")
            raise 
