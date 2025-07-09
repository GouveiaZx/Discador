"""
Serviço para gerenciar limites de uso de DIDs por país.
Implementa restrições específicas como limite de 100 usos/dia para USA/Canadá.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import logging

from app.models.cli import Cli
from app.schemas.lista_llamadas import detectar_pais_numero

logger = logging.getLogger(__name__)

class CliCountryLimitsService:
    """Serviço para gerenciar limites de uso de DIDs por país."""
    
    # Limites por país (usos por dia)
    COUNTRY_DAILY_LIMITS = {
        'usa': 100,      # USA/Canadá - máximo 100 usos por dia
        'canada': 100,   # USA/Canadá - máximo 100 usos por dia
        'mexico': 0,     # México - sem limite
        'brasil': 0,     # Brasil - sem limite
        'colombia': 0,   # Colômbia - sem limite
        'argentina': 0,  # Argentina - sem limite
        'chile': 0,      # Chile - sem limite
        'peru': 0,       # Peru - sem limite
        'venezuela': 0,  # Venezuela - sem limite
        'default': 0     # Padrão - sem limite
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_country_limit(self, country: str) -> int:
        """Obtém o limite diário para um país específico."""
        return self.COUNTRY_DAILY_LIMITS.get(country.lower(), 
                                             self.COUNTRY_DAILY_LIMITS['default'])
    
    def get_cli_usage_today(self, cli_numero: str) -> int:
        """Obtém o uso atual de um CLI hoje."""
        try:
            today = datetime.now().date()
            
            # Buscar CLI
            cli = self.db.query(Cli).filter(
                Cli.numero_normalizado == cli_numero
            ).first()
            
            if not cli:
                return 0
            
            # Contar usos hoje (simulado - em produção consultaria tabela de chamadas)
            # SELECT COUNT(*) FROM llamadas WHERE cli_utilizado = ? AND DATE(fecha_inicio) = ?
            # Por agora, usar o campo veces_usado como base
            
            return cli.veces_usado or 0
            
        except Exception as e:
            logger.error(f"Erro ao obter uso do CLI {cli_numero}: {str(e)}")
            return 0
    
    def can_use_cli(self, cli_numero: str, destination_number: str) -> Tuple[bool, str]:
        """
        Verifica se um CLI pode ser usado para uma chamada específica.
        
        Args:
            cli_numero: Número do CLI
            destination_number: Número de destino
            
        Returns:
            Tuple[bool, str]: (pode_usar, motivo_se_nao_pode)
        """
        try:
            # Detectar país do número de destino
            country = detectar_pais_numero(destination_number)
            
            # Obter limite do país
            daily_limit = self.get_country_limit(country)
            
            # Se não há limite, sempre pode usar
            if daily_limit == 0:
                return True, ""
            
            # Verificar uso atual
            current_usage = self.get_cli_usage_today(cli_numero)
            
            # Verificar se está dentro do limite
            if current_usage >= daily_limit:
                return False, f"CLI {cli_numero} excedeu limite diário de {daily_limit} usos para {country.upper()}"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Erro ao verificar CLI {cli_numero}: {str(e)}")
            return False, f"Erro interno: {str(e)}"
    
    def get_available_clis_for_country(self, destination_number: str, limit: int = 50) -> List[Dict]:
        """
        Obtém lista de CLIs disponíveis para um país específico.
        
        Args:
            destination_number: Número de destino
            limit: Número máximo de CLIs a retornar
            
        Returns:
            List[Dict]: Lista de CLIs disponíveis com informações de uso
        """
        try:
            # Detectar país
            country = detectar_pais_numero(destination_number)
            daily_limit = self.get_country_limit(country)
            
            # Buscar CLIs ativos
            clis = self.db.query(Cli).filter(
                Cli.activo == True
            ).limit(limit).all()
            
            available_clis = []
            
            for cli in clis:
                current_usage = self.get_cli_usage_today(cli.numero_normalizado)
                
                # Se há limite, verificar se está dentro
                if daily_limit > 0:
                    if current_usage >= daily_limit:
                        continue
                
                available_clis.append({
                    'cli': cli.numero_normalizado,
                    'description': cli.descripcion,
                    'current_usage': current_usage,
                    'daily_limit': daily_limit,
                    'remaining_uses': daily_limit - current_usage if daily_limit > 0 else 'unlimited',
                    'country': country,
                    'priority': self._calculate_priority(current_usage, daily_limit)
                })
            
            # Ordenar por prioridade (menos usados primeiro)
            available_clis.sort(key=lambda x: x['priority'], reverse=True)
            
            return available_clis
            
        except Exception as e:
            logger.error(f"Erro ao obter CLIs para {destination_number}: {str(e)}")
            return []
    
    def _calculate_priority(self, current_usage: int, daily_limit: int) -> int:
        """Calcula prioridade do CLI baseado no uso atual."""
        if daily_limit == 0:
            # Sem limite - prioridade baseada apenas no uso atual
            return max(0, 1000 - current_usage)
        
        # Com limite - prioridade baseada na porcentagem restante
        usage_percentage = (current_usage / daily_limit) * 100
        return max(0, 100 - int(usage_percentage))
    
    def increment_cli_usage(self, cli_numero: str) -> bool:
        """
        Incrementa o uso de um CLI.
        
        Args:
            cli_numero: Número do CLI
            
        Returns:
            bool: True se incrementou com sucesso
        """
        try:
            cli = self.db.query(Cli).filter(
                Cli.numero_normalizado == cli_numero
            ).first()
            
            if not cli:
                logger.warning(f"CLI {cli_numero} não encontrado")
                return False
            
            # Incrementar uso
            cli.veces_usado = (cli.veces_usado or 0) + 1
            cli.ultima_vez_usado = datetime.now()
            
            self.db.commit()
            
            logger.info(f"Incrementado uso do CLI {cli_numero}: {cli.veces_usado}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao incrementar uso do CLI {cli_numero}: {str(e)}")
            self.db.rollback()
            return False
    
    def reset_daily_usage(self) -> Dict[str, int]:
        """
        Reset diário dos contadores de uso.
        Deve ser executado diariamente via cron job.
        
        Returns:
            Dict[str, int]: Estatísticas do reset
        """
        try:
            # Em um sistema real, isso resetaria contadores em uma tabela específica
            # Por agora, vamos resetar apenas CLIs que têm limite
            
            # Buscar CLIs que precisam de reset
            clis_to_reset = self.db.query(Cli).filter(
                and_(
                    Cli.activo == True,
                    Cli.veces_usado > 0
                )
            ).all()
            
            reset_count = 0
            
            for cli in clis_to_reset:
                # Resetar contador (em produção, isso seria mais sofisticado)
                cli.veces_usado = 0
                reset_count += 1
            
            self.db.commit()
            
            logger.info(f"Reset diário realizado: {reset_count} CLIs resetados")
            
            return {
                'reset_count': reset_count,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Erro no reset diário: {str(e)}")
            self.db.rollback()
            return {
                'reset_count': 0,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    def get_usage_statistics(self) -> Dict[str, any]:
        """Obtém estatísticas de uso de CLIs por país."""
        try:
            stats = {
                'total_clis': self.db.query(Cli).filter(Cli.activo == True).count(),
                'countries': {},
                'top_used_clis': [],
                'available_clis': {}
            }
            
            # Obter estatísticas por país
            for country, limit in self.COUNTRY_DAILY_LIMITS.items():
                if country == 'default':
                    continue
                    
                stats['countries'][country] = {
                    'daily_limit': limit,
                    'has_limit': limit > 0
                }
            
            # CLIs mais usados
            top_clis = self.db.query(Cli).filter(
                Cli.activo == True
            ).order_by(Cli.veces_usado.desc()).limit(10).all()
            
            for cli in top_clis:
                stats['top_used_clis'].append({
                    'cli': cli.numero_normalizado,
                    'usage': cli.veces_usado,
                    'description': cli.descripcion
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {'error': str(e)} 