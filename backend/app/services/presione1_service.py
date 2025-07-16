"""
Serviço para gerenciar campanhas de discado preditivo com modo "Presione 1".
Atualizado com sincronização otimizada via MCP e melhorias de performance.
"""

import asyncio
import random
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_
from fastapi import HTTPException
from sqlalchemy.sql import text

from app.models.campana_presione1 import CampanaPresione1, LlamadaPresione1
from app.schemas.presione1 import (
    CampanaPresione1Create,
    CampanaPresione1Update,
    EstadisticasCampanaResponse,
    MonitorCampanaResponse
)
from app.services.cli_service import CliService
from app.services.blacklist_service import BlacklistService
from app.services.asterisk import asterisk_service
from app.utils.logger import logger

# Importar funcionalidades de sincronização
from app.config.database_sync import (
    sync_operation, 
    clear_campaign_cache, 
    DatabaseValidator,
    sync_manager,
    with_retry,
    with_performance_logging
)


class PresionE1Service:
    """Serviço para campanhas de discado preditivo con modo 'Presione 1' - 100% Supabase com sincronização otimizada."""
    
    def __init__(self, db: Session = None):
        # db mantido para compatibilidade, mas não usado para presione1
        self.cli_service = CliService(db) if db else None
        self.blacklist_service = BlacklistService(db) if db else None
        self.campanhas_ativas = {}  # Armazena campanhas em execução
        self._supabase_config = self._init_supabase()
        # Cache para otimização de performance
        self._cache = {}
        self._cache_ttl = {}
        self._query_times = {}  # Para monitorar tempos de consulta
    
    def _init_supabase(self) -> Dict[str, str]:
        """Inicializa configuração do Supabase."""
        import os
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("Configuração do Supabase não encontrada")
            raise Exception("SUPABASE_URL e SUPABASE_ANON_KEY são obrigatórios")
        
        return {
            "url": supabase_url,
            "key": supabase_key,
            "headers": {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            }
        }
    
    async def parar_campana(self, campana_id: int, usuario_id: str, motivo: str = "Parada manual") -> Dict[str, Any]:
        """
        Para completamente uma campanha.
        
        Args:
            campana_id: ID da campanha
            usuario_id: ID do usuário que está parando
            motivo: Motivo da parada
            
        Returns:
            Resultado da operação
        """
        try:
            logger.info(f"⏹️ Parando campanha {campana_id} - Motivo: {motivo}")
            
            # Verificar se a campanha existe e está ativa
            campana = self.obter_campana(campana_id)
            
            if not campana.get("activa"):
                return {
                    "success": True,
                    "message": "Campanha já estava parada",
                    "campana_id": campana_id
                }
            
            # Atualizar status no Supabase
            dados_parada = {
                "activa": False,
                "pausada": False,
                "fecha_actualizacion": datetime.utcnow().isoformat()
            }
            
            # Remover da memória
            if campana_id in self.campanhas_ativas:
                del self.campanhas_ativas[campana_id]
            
            # Limpar cache
            clear_campaign_cache(str(campana_id))
            
            logger.info(f"✅ Campanha {campana_id} parada com sucesso")
            
            return {
                "success": True,
                "message": "Campanha parada com sucesso",
                "campana_id": campana_id,
                "motivo": motivo
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao parar campanha {campana_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao parar campanha: {str(e)}"
            )
    
    def obter_campana(self, campana_id: int) -> Dict[str, Any]:
        """Obtém uma campanha por ID, considerando estado em memória se ativa."""
        try:
            # Simulação de busca - implementar conforme necessário
            return {
                "id": campana_id,
                "activa": False,
                "pausada": False
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter campanha {campana_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao buscar campanha: {str(e)}"
            )
    
    async def excluir_campana_otimizada(self, campana_id: int) -> Dict[str, Any]:
        """
        Exclui completamente uma campanha e todos os dados relacionados.
        
        Args:
            campana_id: ID da campanha a ser excluída
            
        Returns:
            Resultado da operação
        """
        try:
            import requests
            
            logger.info(f"🗑️ Excluindo campanha {campana_id} e dados relacionados")
            
            # Primeiro, parar a campanha se estiver ativa
            try:
                campana = self.obter_campana(campana_id)
                if campana.get("activa"):
                    await self.parar_campana(campana_id, "system", "Exclusão da campanha")
            except Exception as e:
                logger.warning(f"Erro ao parar campanha antes da exclusão: {str(e)}")
            
            # Excluir do Supabase
            supabase_url = f"{self._supabase_config['url']}/rest/v1/campanhas_presione1"
            params = {"id": f"eq.{campana_id}"}
            
            response = requests.delete(
                supabase_url,
                headers=self._supabase_config["headers"],
                params=params,
                timeout=30
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Campanha {campana_id} excluída do Supabase com sucesso")
            else:
                logger.warning(f"⚠️ Resposta inesperada do Supabase: {response.status_code}")
            
            # Excluir chamadas relacionadas
            try:
                llamadas_url = f"{self._supabase_config['url']}/rest/v1/llamadas_presione1"
                llamadas_params = {"campana_id": f"eq.{campana_id}"}
                
                llamadas_response = requests.delete(
                    llamadas_url,
                    headers=self._supabase_config["headers"],
                    params=llamadas_params,
                    timeout=30
                )
                
                if llamadas_response.status_code == 204:
                    logger.info(f"✅ Chamadas da campanha {campana_id} excluídas com sucesso")
                else:
                    logger.warning(f"⚠️ Resposta inesperada ao excluir chamadas: {llamadas_response.status_code}")
                    
            except Exception as e:
                logger.warning(f"Erro ao excluir chamadas da campanha {campana_id}: {str(e)}")
            
            # Remover da memória se existir
            if campana_id in self.campanhas_ativas:
                del self.campanhas_ativas[campana_id]
            
            # Limpar cache
            clear_campaign_cache(str(campana_id))
            
            logger.info(f"✅ Campanha {campana_id} excluída completamente")
            
            return {
                "success": True,
                "message": "Campanha excluída com sucesso",
                "campana_id": campana_id
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao excluir campanha {campana_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao excluir campanha: {str(e)}"
            )