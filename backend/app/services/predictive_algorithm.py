#!/usr/bin/env python3
"""
Algoritmo Preditivo para Discado Inteligente
Calcula dinamicamente a taxa de discagem ideal
"""

import time
import math
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class CallMetrics:
    """Métricas de chamadas"""
    total_calls: int = 0
    answered_calls: int = 0
    busy_calls: int = 0
    no_answer_calls: int = 0
    failed_calls: int = 0
    average_call_duration: float = 0.0
    connection_rate: float = 0.0
    answer_rate: float = 0.0
    
    def update_rates(self):
        """Atualiza as taxas calculadas"""
        if self.total_calls > 0:
            self.connection_rate = (self.answered_calls + self.busy_calls) / self.total_calls
            self.answer_rate = self.answered_calls / self.total_calls
        else:
            self.connection_rate = 0.0
            self.answer_rate = 0.0

@dataclass
class PredictiveConfig:
    """Configuração do algoritmo preditivo"""
    max_calls_per_second: int = 10
    min_calls_per_second: int = 1
    target_answer_rate: float = 0.30  # 30% de taxa de resposta desejada
    agent_capacity: int = 5  # Número de agentes disponíveis
    average_call_duration: int = 180  # Duração média em segundos
    abandon_rate_threshold: float = 0.05  # 5% máximo de abandono
    adjustment_factor: float = 0.1  # Fator de ajuste (10%)
    
class PredictiveDialer:
    """
    Algoritmo principal do discador preditivo
    Calcula dinamicamente a taxa de discagem ideal
    """
    
    def __init__(self, config: PredictiveConfig = None):
        self.config = config or PredictiveConfig()
        
        # Histórico de métricas
        self.metrics_history: List[CallMetrics] = []
        self.current_metrics = CallMetrics()
        
        # Estado atual
        self.current_cps = 1.0  # Calls per second
        self.available_agents = self.config.agent_capacity
        self.calls_in_progress = 0
        self.calls_waiting = 0
        
        # Controle de ajustes
        self.last_adjustment = time.time()
        self.adjustment_interval = 30  # Ajustar a cada 30 segundos
        
        # Estatísticas por período
        self.hourly_stats = defaultdict(lambda: CallMetrics())
        self.daily_stats = defaultdict(lambda: CallMetrics())
        
    def calculate_optimal_cps(self) -> float:
        """
        Calcula a taxa ideal de chamadas por segundo
        Baseado em algoritmos de discado preditivo
        """
        try:
            # Se não há histórico, começar conservador
            if len(self.metrics_history) == 0:
                return self.config.min_calls_per_second
            
            # Métricas atuais
            recent_metrics = self._get_recent_metrics()
            
            # Calcular taxa de conexão
            connection_rate = recent_metrics.connection_rate
            answer_rate = recent_metrics.answer_rate
            
            # Se taxa de resposta muito baixa, aumentar CPS
            if answer_rate < self.config.target_answer_rate * 0.8:
                adjustment = 1.0 + self.config.adjustment_factor
            # Se taxa de resposta muito alta, diminuir CPS
            elif answer_rate > self.config.target_answer_rate * 1.2:
                adjustment = 1.0 - self.config.adjustment_factor
            else:
                adjustment = 1.0
            
            # Calcular CPS baseado na capacidade dos agentes
            agent_based_cps = self._calculate_agent_based_cps(recent_metrics)
            
            # Aplicar ajuste
            optimal_cps = agent_based_cps * adjustment
            
            # Limitar aos valores min/max
            optimal_cps = max(self.config.min_calls_per_second, 
                            min(optimal_cps, self.config.max_calls_per_second))
            
            logger.info(f"📊 CPS Calculado: {optimal_cps:.2f} "
                       f"(Taxa resposta: {answer_rate:.2%}, "
                       f"Ajuste: {adjustment:.2%})")
            
            return optimal_cps
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular CPS: {str(e)}")
            return self.config.min_calls_per_second
    
    def _calculate_agent_based_cps(self, metrics: CallMetrics) -> float:
        """
        Calcula CPS baseado na capacidade dos agentes
        Usa fórmula: CPS = (Agentes Disponíveis / Duração Média Chamada) / Taxa de Resposta
        """
        try:
            if metrics.answer_rate <= 0:
                return self.config.min_calls_per_second
            
            # Duração média da chamada em segundos
            avg_duration = metrics.average_call_duration or self.config.average_call_duration
            
            # Capacidade teórica dos agentes (chamadas por segundo)
            agent_capacity = self.available_agents / avg_duration
            
            # Ajustar pela taxa de resposta
            theoretical_cps = agent_capacity / metrics.answer_rate
            
            # Aplicar fator de segurança para evitar abandono
            safety_factor = 1.0 - self.config.abandon_rate_threshold
            
            return theoretical_cps * safety_factor
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo baseado em agentes: {str(e)}")
            return self.config.min_calls_per_second
    
    def _get_recent_metrics(self) -> CallMetrics:
        """Obtém métricas dos últimos 5 minutos"""
        if not self.metrics_history:
            return CallMetrics()
        
        # Últimas 5 entradas (assumindo 1 por minuto)
        recent = self.metrics_history[-5:]
        
        # Agregar métricas
        total_calls = sum(m.total_calls for m in recent)
        answered_calls = sum(m.answered_calls for m in recent)
        busy_calls = sum(m.busy_calls for m in recent)
        no_answer_calls = sum(m.no_answer_calls for m in recent)
        failed_calls = sum(m.failed_calls for m in recent)
        
        # Duração média ponderada
        total_duration = sum(m.average_call_duration * m.answered_calls for m in recent)
        avg_duration = total_duration / answered_calls if answered_calls > 0 else 0
        
        metrics = CallMetrics(
            total_calls=total_calls,
            answered_calls=answered_calls,
            busy_calls=busy_calls,
            no_answer_calls=no_answer_calls,
            failed_calls=failed_calls,
            average_call_duration=avg_duration
        )
        
        metrics.update_rates()
        return metrics
    
    def should_make_call(self) -> bool:
        """
        Determina se deve fazer uma nova chamada
        Baseado no estado atual e algoritmo preditivo
        """
        try:
            # Verificar se há agentes disponíveis
            if self.available_agents <= 0:
                return False
            
            # Calcular CPS ideal
            optimal_cps = self.calculate_optimal_cps()
            
            # Verificar se pode fazer mais chamadas
            max_concurrent = math.ceil(optimal_cps * self.config.average_call_duration)
            
            # Não exceder capacidade
            if self.calls_in_progress >= max_concurrent:
                return False
            
            # Verificar intervalo entre chamadas
            interval = 1.0 / optimal_cps
            time_since_last = time.time() - self.last_adjustment
            
            return time_since_last >= interval
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar se deve fazer chamada: {str(e)}")
            return False
    
    def record_call_result(self, call_id: str, status: str, duration: int = 0):
        """
        Registra resultado de uma chamada para aprendizado
        """
        try:
            # Atualizar métricas atuais
            self.current_metrics.total_calls += 1
            
            if status == "answered":
                self.current_metrics.answered_calls += 1
                if duration > 0:
                    # Calcular nova duração média
                    total_duration = (self.current_metrics.average_call_duration * 
                                    (self.current_metrics.answered_calls - 1) + duration)
                    self.current_metrics.average_call_duration = total_duration / self.current_metrics.answered_calls
            elif status == "busy":
                self.current_metrics.busy_calls += 1
            elif status == "no_answer":
                self.current_metrics.no_answer_calls += 1
            elif status == "failed":
                self.current_metrics.failed_calls += 1
            
            # Atualizar taxas
            self.current_metrics.update_rates()
            
            # Registrar estatísticas por período
            self._record_period_stats(status, duration)
            
            logger.info(f"📈 Chamada registrada: {status} "
                       f"(Total: {self.current_metrics.total_calls}, "
                       f"Taxa resposta: {self.current_metrics.answer_rate:.2%})")
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar resultado: {str(e)}")
    
    def _record_period_stats(self, status: str, duration: int):
        """Registra estatísticas por período (hora/dia)"""
        now = datetime.now()
        hour_key = now.strftime("%Y-%m-%d %H:00")
        day_key = now.strftime("%Y-%m-%d")
        
        # Estatísticas horárias
        hour_stats = self.hourly_stats[hour_key]
        hour_stats.total_calls += 1
        
        # Estatísticas diárias
        day_stats = self.daily_stats[day_key]
        day_stats.total_calls += 1
        
        # Atualizar por status
        if status == "answered":
            hour_stats.answered_calls += 1
            day_stats.answered_calls += 1
        elif status == "busy":
            hour_stats.busy_calls += 1
            day_stats.busy_calls += 1
        elif status == "no_answer":
            hour_stats.no_answer_calls += 1
            day_stats.no_answer_calls += 1
        elif status == "failed":
            hour_stats.failed_calls += 1
            day_stats.failed_calls += 1
        
        # Atualizar taxas
        hour_stats.update_rates()
        day_stats.update_rates()
    
    def update_agent_status(self, available_agents: int):
        """Atualiza número de agentes disponíveis"""
        self.available_agents = available_agents
        logger.info(f"👥 Agentes disponíveis atualizados: {available_agents}")
    
    def get_current_stats(self) -> Dict:
        """Retorna estatísticas atuais"""
        return {
            "current_cps": self.current_cps,
            "available_agents": self.available_agents,
            "calls_in_progress": self.calls_in_progress,
            "calls_waiting": self.calls_waiting,
            "total_calls": self.current_metrics.total_calls,
            "answered_calls": self.current_metrics.answered_calls,
            "answer_rate": self.current_metrics.answer_rate,
            "connection_rate": self.current_metrics.connection_rate,
            "average_call_duration": self.current_metrics.average_call_duration
        }
    
    def get_hourly_stats(self) -> Dict:
        """Retorna estatísticas por hora"""
        stats = {}
        for hour, metrics in self.hourly_stats.items():
            stats[hour] = {
                "total_calls": metrics.total_calls,
                "answered_calls": metrics.answered_calls,
                "answer_rate": metrics.answer_rate,
                "connection_rate": metrics.connection_rate
            }
        return stats
    
    def optimize_for_time_period(self, hour: int) -> float:
        """
        Otimiza CPS para um período específico do dia
        Baseado em histórico de performance
        """
        try:
            # Buscar dados históricos para esta hora
            hour_key = f"{datetime.now().strftime('%Y-%m-%d')} {hour:02d}:00"
            
            if hour_key in self.hourly_stats:
                hour_metrics = self.hourly_stats[hour_key]
                
                # Ajustar CPS baseado na performance histórica
                if hour_metrics.answer_rate > self.config.target_answer_rate:
                    # Boa performance, pode aumentar CPS
                    return min(self.config.max_calls_per_second, 
                             self.current_cps * 1.2)
                elif hour_metrics.answer_rate < self.config.target_answer_rate * 0.8:
                    # Performance baixa, diminuir CPS
                    return max(self.config.min_calls_per_second, 
                             self.current_cps * 0.8)
            
            # Padrões gerais por hora do dia
            peak_hours = [9, 10, 11, 14, 15, 16, 17, 18, 19, 20]  # Horários de pico
            
            if hour in peak_hours:
                return min(self.config.max_calls_per_second, 
                         self.current_cps * 1.1)
            else:
                return max(self.config.min_calls_per_second, 
                         self.current_cps * 0.9)
                
        except Exception as e:
            logger.error(f"❌ Erro ao otimizar por período: {str(e)}")
            return self.current_cps
    
    def save_metrics_snapshot(self):
        """Salva snapshot das métricas atuais"""
        try:
            # Adicionar ao histórico
            self.metrics_history.append(self.current_metrics)
            
            # Manter apenas últimas 100 entradas
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            # Resetar métricas atuais
            self.current_metrics = CallMetrics()
            
            logger.info("📊 Snapshot de métricas salvo")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar snapshot: {str(e)}")

# Instância global do algoritmo preditivo
predictive_dialer = PredictiveDialer()

def get_predictive_dialer() -> PredictiveDialer:
    """Retorna instância do algoritmo preditivo"""
    return predictive_dialer 