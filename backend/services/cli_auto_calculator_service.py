from typing import Dict, List, Optional, Tuple
import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

logger = logging.getLogger(__name__)

class CliAutoCalculatorService:
    """
    Serviço para cálculo automático de CLIs necessários baseado no volume de números
    e geração automática de CLIs para evitar blacklisting.
    """
    
    def __init__(self):
        self.default_daily_limit = 100  # Limite padrão para USA/Canada
        self.default_work_hours = 8     # Horas de trabalho por dia
        self.safety_margin = 1.2        # Margem de segurança de 20%
    
    def calculate_clis_needed(
        self,
        total_numbers: int,
        calls_per_hour: int = 500,
        daily_call_limit: int = 100,
        work_hours: int = 8,
        country: str = 'usa'
    ) -> Dict:
        """
        Calcula o número de CLIs necessários baseado no volume de números.
        
        Fórmula: (Total números × Chamadas por hora) / (Limite diário × Horas de trabalho)
        
        Args:
            total_numbers: Quantidade total de números a serem discados
            calls_per_hour: Velocidade de discagem (chamadas por hora)
            daily_call_limit: Limite de chamadas por CLI por dia
            work_hours: Horas de trabalho por dia
            country: País para aplicar limites específicos
        
        Returns:
            Dict com cálculos detalhados
        """
        try:
            # Limites recomendados por país (sem limite máximo rígido)
            recommended_limits = {
                'usa': 100, 'canada': 100,
                'mexico': 150, 'brazil': 150,
                'colombia': 120, 'argentina': 120,
                'chile': 100, 'peru': 100
            }
            
            # Usar limite fornecido ou recomendado (sem forçar limite máximo)
            if daily_call_limit <= 0:
                daily_call_limit = recommended_limits.get(country.lower(), 100)
            
            # Cálculo básico
            calls_per_day = calls_per_hour * work_hours
            total_calls_needed = total_numbers
            
            # Número mínimo de CLIs necessários
            min_clis_needed = math.ceil(total_calls_needed / daily_call_limit)
            
            # Cálculo baseado na velocidade de discagem
            velocity_based_clis = math.ceil(calls_per_hour / (daily_call_limit / work_hours))
            
            # Usar o maior dos dois cálculos
            base_clis_needed = max(min_clis_needed, velocity_based_clis)
            
            # Aplicar margem de segurança
            recommended_clis = math.ceil(base_clis_needed * self.safety_margin)
            
            # Remover qualquer limite artificial de CLIs - permitir configuração ilimitada
            # O sistema agora calcula baseado puramente no volume e velocidade necessária
            
            # Cálculos adicionais
            calls_per_cli_per_hour = daily_call_limit / work_hours
            estimated_completion_days = math.ceil(total_numbers / (recommended_clis * daily_call_limit))
            
            return {
                'total_numbers': total_numbers,
                'calls_per_hour': calls_per_hour,
                'daily_call_limit': daily_call_limit,
                'work_hours': work_hours,
                'country': country,
                'min_clis_needed': min_clis_needed,
                'velocity_based_clis': velocity_based_clis,
                'base_clis_needed': base_clis_needed,
                'recommended_clis': recommended_clis,
                'safety_margin_percent': int((self.safety_margin - 1) * 100),
                'calls_per_cli_per_hour': round(calls_per_cli_per_hour, 2),
                'estimated_completion_days': estimated_completion_days,
                'total_daily_capacity': recommended_clis * daily_call_limit,
                'efficiency_ratio': round((total_numbers / (recommended_clis * daily_call_limit)) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Erro no cálculo de CLIs: {e}")
            raise
    
    def create_auto_config(
        self,
        campaign_id: Optional[int],
        total_numbers: int,
        calls_per_hour: int = 500,
        daily_call_limit: int = 100,
        work_hours: int = 8,
        country: str = 'usa',
        auto_generate: bool = True
    ) -> Dict:
        """
        Cria uma configuração automática de CLIs.
        
        Args:
            campaign_id: ID da campanha (opcional)
            total_numbers: Quantidade total de números
            calls_per_hour: Velocidade de discagem
            daily_call_limit: Limite diário por CLI
            work_hours: Horas de trabalho
            country: País
            auto_generate: Se deve gerar CLIs automaticamente
        
        Returns:
            Dict com a configuração criada
        """
        try:
            # Calcular CLIs necessários
            calculation = self.calculate_clis_needed(
                total_numbers, calls_per_hour, daily_call_limit, work_hours, country
            )
            
            with next(get_db()) as db:
                # Inserir configuração no banco
                query = text("""
                    INSERT INTO cli_auto_config (
                        campaign_id, total_numbers, daily_call_limit, work_hours,
                        calls_per_hour, calculated_clis_needed, country, auto_generate, status
                    ) VALUES (
                        :campaign_id, :total_numbers, :daily_call_limit, :work_hours,
                        :calls_per_hour, :calculated_clis_needed, :country, :auto_generate, 'created'
                    ) RETURNING id
                """)
                
                result = db.execute(query, {
                    'campaign_id': campaign_id,
                    'total_numbers': total_numbers,
                    'daily_call_limit': daily_call_limit,
                    'work_hours': work_hours,
                    'calls_per_hour': calls_per_hour,
                    'calculated_clis_needed': calculation['recommended_clis'],
                    'country': country,
                    'auto_generate': auto_generate
                })
                
                config_id = result.fetchone()[0]
                db.commit()
                
                # Gerar CLIs automaticamente se solicitado
                if auto_generate:
                    generated_count = self.generate_clis_for_config(
                        config_id, calculation['recommended_clis'], country
                    )
                    calculation['generated_clis'] = generated_count
                
                calculation['config_id'] = config_id
                calculation['status'] = 'created'
                
                return calculation
                
        except Exception as e:
            logger.error(f"Erro ao criar configuração automática: {e}")
            raise
    
    def generate_clis_for_config(
        self,
        config_id: int,
        quantity: int,
        country: str = 'usa'
    ) -> int:
        """
        Gera CLIs automaticamente para uma configuração.
        
        Args:
            config_id: ID da configuração
            quantity: Quantidade de CLIs a gerar
            country: País
        
        Returns:
            Número de CLIs gerados
        """
        try:
            with next(get_db()) as db:
                # Usar função do banco para gerar CLIs
                query = text("""
                    SELECT generate_auto_clis(:config_id, :quantity, :country)
                """)
                
                result = db.execute(query, {
                    'config_id': config_id,
                    'quantity': quantity,
                    'country': country
                })
                
                generated_count = result.fetchone()[0]
                
                # Atualizar status da configuração
                update_query = text("""
                    UPDATE cli_auto_config 
                    SET status = 'generated' 
                    WHERE id = :config_id
                """)
                
                db.execute(update_query, {'config_id': config_id})
                db.commit()
                
                logger.info(f"Gerados {generated_count} CLIs para configuração {config_id}")
                return generated_count
                
        except Exception as e:
            logger.error(f"Erro ao gerar CLIs: {e}")
            raise
    
    def get_config_details(self, config_id: int) -> Dict:
        """
        Obtém detalhes de uma configuração automática.
        
        Args:
            config_id: ID da configuração
        
        Returns:
            Dict com detalhes da configuração
        """
        try:
            with next(get_db()) as db:
                query = text("""
                    SELECT 
                        c.*,
                        COUNT(p.id) as generated_clis_count,
                        COUNT(CASE WHEN p.active = true THEN 1 END) as active_clis_count,
                        SUM(p.daily_usage_count) as total_usage_today
                    FROM cli_auto_config c
                    LEFT JOIN cli_auto_pool p ON c.id = p.auto_config_id
                    WHERE c.id = :config_id
                    GROUP BY c.id
                """)
                
                result = db.execute(query, {'config_id': config_id})
                row = result.fetchone()
                
                if not row:
                    raise ValueError(f"Configuração {config_id} não encontrada")
                
                return {
                    'id': row.id,
                    'campaign_id': row.campaign_id,
                    'total_numbers': row.total_numbers,
                    'daily_call_limit': row.daily_call_limit,
                    'work_hours': row.work_hours,
                    'calls_per_hour': row.calls_per_hour,
                    'calculated_clis_needed': row.calculated_clis_needed,
                    'country': row.country,
                    'auto_generate': row.auto_generate,
                    'status': row.status,
                    'generated_clis_count': row.generated_clis_count or 0,
                    'active_clis_count': row.active_clis_count or 0,
                    'total_usage_today': row.total_usage_today or 0,
                    'created_at': row.created_at,
                    'updated_at': row.updated_at
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter detalhes da configuração: {e}")
            raise
    
    def get_available_area_codes(self, country: str = 'usa') -> List[Dict]:
        """
        Obtém códigos de área disponíveis para um país.
        
        Args:
            country: País
        
        Returns:
            Lista de códigos de área
        """
        try:
            with next(get_db()) as db:
                if country.lower() == 'usa':
                    query = text("""
                        SELECT area_code, state, city, timezone
                        FROM usa_area_codes
                        WHERE active = true
                        ORDER BY state, city
                    """)
                    
                    result = db.execute(query)
                    return [
                        {
                            'area_code': row.area_code,
                            'state': row.state,
                            'city': row.city,
                            'timezone': row.timezone
                        }
                        for row in result.fetchall()
                    ]
                else:
                    # Para outros países, retornar lista vazia por enquanto
                    return []
                    
        except Exception as e:
            logger.error(f"Erro ao obter códigos de área: {e}")
            raise
    
    def get_cli_usage_stats(self, config_id: int) -> Dict:
        """
        Obtém estatísticas de uso dos CLIs de uma configuração.
        
        Args:
            config_id: ID da configuração
        
        Returns:
            Dict com estatísticas
        """
        try:
            with next(get_db()) as db:
                query = text("""
                    SELECT 
                        COUNT(*) as total_clis,
                        COUNT(CASE WHEN active = true THEN 1 END) as active_clis,
                        COUNT(CASE WHEN daily_usage_count > 0 THEN 1 END) as used_today,
                        AVG(daily_usage_count) as avg_usage_per_cli,
                        MAX(daily_usage_count) as max_usage_per_cli,
                        SUM(daily_usage_count) as total_usage_today
                    FROM cli_auto_pool
                    WHERE auto_config_id = :config_id
                """)
                
                result = db.execute(query, {'config_id': config_id})
                row = result.fetchone()
                
                return {
                    'total_clis': row.total_clis or 0,
                    'active_clis': row.active_clis or 0,
                    'used_today': row.used_today or 0,
                    'avg_usage_per_cli': round(row.avg_usage_per_cli or 0, 2),
                    'max_usage_per_cli': row.max_usage_per_cli or 0,
                    'total_usage_today': row.total_usage_today or 0
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de uso: {e}")
            raise
    
    def reset_daily_usage(self, config_id: Optional[int] = None) -> int:
        """
        Reseta o uso diário dos CLIs.
        
        Args:
            config_id: ID da configuração (opcional, se não fornecido reseta todos)
        
        Returns:
            Número de CLIs resetados
        """
        try:
            with next(get_db()) as db:
                if config_id:
                    query = text("""
                        UPDATE cli_auto_pool 
                        SET daily_usage_count = 0, last_used = NULL
                        WHERE auto_config_id = :config_id
                    """)
                    result = db.execute(query, {'config_id': config_id})
                else:
                    query = text("""
                        UPDATE cli_auto_pool 
                        SET daily_usage_count = 0, last_used = NULL
                    """)
                    result = db.execute(query)
                
                db.commit()
                return result.rowcount
                
        except Exception as e:
            logger.error(f"Erro ao resetar uso diário: {e}")
            raise