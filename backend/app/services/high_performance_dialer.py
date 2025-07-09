"""
Sistema de Discado de Alta Performance
Suporta 20-30 CPS (Calls Per Second) com controle otimizado e monitoramento em tempo real.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
import threading
from collections import deque
import statistics

from app.services.cli_country_limits_service import CliCountryLimitsService
from app.services.dtmf_country_config_service import DTMFCountryConfigService
from app.services.asterisk_manager import AsteriskManager
from app.utils.logger import logger

@dataclass
class CallMetrics:
    """Métricas de chamadas para monitoramento de performance."""
    timestamp: datetime
    calls_initiated: int
    calls_answered: int
    calls_failed: int
    current_cps: float
    average_setup_time: float
    concurrent_calls: int
    system_load: float

@dataclass
class PerformanceConfig:
    """Configuração de performance do discador."""
    max_cps: float = 30.0
    initial_cps: float = 5.0
    ramp_up_step: float = 2.0
    ramp_up_interval: int = 10  # segundos
    max_concurrent_calls: int = 500
    thread_pool_size: int = 50
    monitoring_interval: int = 1  # segundos
    auto_adjust_cps: bool = True
    emergency_brake_threshold: float = 0.1  # 10% success rate
    quality_threshold: float = 0.8  # 80% success rate

class HighPerformanceDialer:
    """Sistema de discado de alta performance."""
    
    def __init__(self, db: Session, config: PerformanceConfig = None):
        self.db = db
        self.config = config or PerformanceConfig()
        
        # Serviços auxiliares
        self.cli_limits_service = CliCountryLimitsService(db)
        self.dtmf_config_service = DTMFCountryConfigService(db)
        self.asterisk_manager = AsteriskManager()
        
        # Estado do discador
        self.current_cps = self.config.initial_cps
        self.is_running = False
        self.concurrent_calls = 0
        self.call_queue = asyncio.Queue(maxsize=10000)
        self.metrics_history = deque(maxlen=1000)
        
        # Controle de threading
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.thread_pool_size)
        self.metrics_lock = threading.Lock()
        self.performance_lock = threading.Lock()
        
        # Estatísticas em tempo real
        self.stats = {
            'total_calls_initiated': 0,
            'total_calls_answered': 0,
            'total_calls_failed': 0,
            'session_start_time': datetime.now(),
            'last_cps_adjustment': datetime.now(),
            'emergency_brake_active': False
        }
        
        # Timers para controle de CPS
        self.last_call_time = 0
        self.call_interval = 1.0 / self.current_cps
        
        # Callbacks para eventos
        self.on_call_initiated: Optional[Callable] = None
        self.on_call_answered: Optional[Callable] = None
        self.on_call_failed: Optional[Callable] = None
        self.on_metrics_updated: Optional[Callable] = None
    
    async def start(self):
        """Inicia o sistema de discado de alta performance."""
        logger.info("🚀 Iniciando sistema de discado de alta performance")
        
        try:
            self.is_running = True
            
            # Iniciar tasks assíncronas
            tasks = [
                asyncio.create_task(self._call_processor()),
                asyncio.create_task(self._metrics_collector()),
                asyncio.create_task(self._performance_monitor()),
                asyncio.create_task(self._cps_auto_adjuster())
            ]
            
            # Aguardar tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar discador: {str(e)}")
            await self.stop()
    
    async def stop(self):
        """Para o sistema de discado."""
        logger.info("🛑 Parando sistema de discado")
        
        self.is_running = False
        
        # Aguardar finalização das chamadas ativas
        while self.concurrent_calls > 0:
            await asyncio.sleep(0.1)
        
        # Fechar thread pool
        self.thread_pool.shutdown(wait=True)
        
        logger.info("✅ Sistema de discado parado")
    
    async def add_call_to_queue(self, call_data: Dict[str, Any]) -> bool:
        """
        Adiciona uma chamada à fila de discagem.
        
        Args:
            call_data: Dados da chamada
            
        Returns:
            bool: True se adicionou com sucesso
        """
        try:
            # Validar dados da chamada
            required_fields = ['numero_destino', 'campana_id']
            for field in required_fields:
                if field not in call_data:
                    logger.error(f"Campo obrigatório faltando: {field}")
                    return False
            
            # Verificar limites do CLI
            if 'cli_numero' in call_data:
                can_use, reason = self.cli_limits_service.can_use_cli(
                    call_data['cli_numero'],
                    call_data['numero_destino']
                )
                if not can_use:
                    logger.warning(f"CLI não pode ser usado: {reason}")
                    return False
            
            # Adicionar à fila
            await self.call_queue.put(call_data)
            logger.debug(f"Chamada adicionada à fila: {call_data['numero_destino']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar chamada à fila: {str(e)}")
            return False
    
    async def _call_processor(self):
        """Processa chamadas da fila respeitando CPS configurado."""
        logger.info("📞 Iniciando processador de chamadas")
        
        while self.is_running:
            try:
                # Verificar se pode fazer nova chamada
                if not self._can_make_call():
                    await asyncio.sleep(0.01)  # 10ms
                    continue
                
                # Buscar próxima chamada da fila
                try:
                    call_data = await asyncio.wait_for(
                        self.call_queue.get(), 
                        timeout=0.1
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Processar chamada em thread separada
                future = self.thread_pool.submit(
                    self._process_single_call, 
                    call_data
                )
                
                # Não aguardar resultado (processamento assíncrono)
                asyncio.create_task(self._handle_call_result(future, call_data))
                
                # Atualizar timestamp da última chamada
                self.last_call_time = time.time()
                
            except Exception as e:
                logger.error(f"❌ Erro no processador de chamadas: {str(e)}")
                await asyncio.sleep(0.1)
    
    def _can_make_call(self) -> bool:
        """Verifica se pode fazer uma nova chamada baseado em CPS e limites."""
        try:
            # Verificar se sistema está ativo
            if not self.is_running:
                return False
            
            # Verificar emergency brake
            if self.stats['emergency_brake_active']:
                return False
            
            # Verificar limite de chamadas concorrentes
            if self.concurrent_calls >= self.config.max_concurrent_calls:
                return False
            
            # Verificar intervalo de CPS
            current_time = time.time()
            time_since_last_call = current_time - self.last_call_time
            
            if time_since_last_call < self.call_interval:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar se pode fazer chamada: {str(e)}")
            return False
    
    def _process_single_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa uma chamada individual."""
        call_start_time = time.time()
        
        try:
            # Incrementar contador de chamadas concorrentes
            with self.performance_lock:
                self.concurrent_calls += 1
            
            # Selecionar CLI se não fornecido
            if 'cli_numero' not in call_data:
                available_clis = self.cli_limits_service.get_available_clis_for_country(
                    call_data['numero_destino'], 
                    limit=10
                )
                
                if not available_clis:
                    raise Exception("Nenhum CLI disponível")
                
                call_data['cli_numero'] = available_clis[0]['cli']
            
            # Obter configuração DTMF para o país
            dtmf_config = self.dtmf_config_service.get_dtmf_config_for_number(
                call_data['numero_destino']
            )
            
            # Iniciar chamada via Asterisk
            asterisk_response = self.asterisk_manager.originate_call(
                destination=call_data['numero_destino'],
                cli=call_data['cli_numero'],
                context=dtmf_config.get('context_suffix', '_default'),
                timeout=30,
                variables={
                    'CAMPANA_ID': call_data['campana_id'],
                    'DTMF_CONNECT_KEY': dtmf_config['connect_key'],
                    'DTMF_DISCONNECT_KEY': dtmf_config['disconnect_key'],
                    'COUNTRY': dtmf_config['detected_country']
                }
            )
            
            # Incrementar uso do CLI
            self.cli_limits_service.increment_cli_usage(call_data['cli_numero'])
            
            # Atualizar estatísticas
            with self.metrics_lock:
                self.stats['total_calls_initiated'] += 1
            
            # Simular resposta do Asterisk
            call_result = {
                'success': True,
                'call_id': asterisk_response.get('ActionID', 'unknown'),
                'setup_time': time.time() - call_start_time,
                'cli_used': call_data['cli_numero'],
                'country': dtmf_config['detected_country'],
                'asterisk_response': asterisk_response
            }
            
            # Callback de chamada iniciada
            if self.on_call_initiated:
                self.on_call_initiated(call_data, call_result)
            
            return call_result
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar chamada {call_data['numero_destino']}: {str(e)}")
            
            # Atualizar estatísticas de erro
            with self.metrics_lock:
                self.stats['total_calls_failed'] += 1
            
            call_result = {
                'success': False,
                'error': str(e),
                'setup_time': time.time() - call_start_time,
                'cli_used': call_data.get('cli_numero', 'unknown')
            }
            
            # Callback de chamada falhada
            if self.on_call_failed:
                self.on_call_failed(call_data, call_result)
            
            return call_result
            
        finally:
            # Decrementar contador de chamadas concorrentes
            with self.performance_lock:
                self.concurrent_calls -= 1
    
    async def _handle_call_result(self, future, call_data: Dict[str, Any]):
        """Manipula resultado de uma chamada processada."""
        try:
            result = future.result()
            
            if result['success']:
                logger.debug(f"✅ Chamada iniciada: {call_data['numero_destino']}")
            else:
                logger.warning(f"❌ Chamada falhou: {call_data['numero_destino']} - {result['error']}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar resultado da chamada: {str(e)}")
    
    async def _metrics_collector(self):
        """Coleta métricas de performance em tempo real."""
        logger.info("📊 Iniciando coletor de métricas")
        
        while self.is_running:
            try:
                # Calcular métricas atuais
                current_time = datetime.now()
                
                # Calcular CPS atual baseado no histórico recente
                recent_metrics = [m for m in self.metrics_history 
                                if (current_time - m.timestamp).seconds <= 10]
                
                if recent_metrics:
                    recent_calls = sum(m.calls_initiated for m in recent_metrics)
                    actual_cps = recent_calls / min(10, len(recent_metrics))
                else:
                    actual_cps = 0
                
                # Calcular tempo médio de setup
                recent_setup_times = [m.average_setup_time for m in recent_metrics if m.average_setup_time > 0]
                avg_setup_time = statistics.mean(recent_setup_times) if recent_setup_times else 0
                
                # Calcular carga do sistema
                system_load = (self.concurrent_calls / self.config.max_concurrent_calls) * 100
                
                # Criar métrica atual
                current_metric = CallMetrics(
                    timestamp=current_time,
                    calls_initiated=self.stats['total_calls_initiated'],
                    calls_answered=self.stats['total_calls_answered'],
                    calls_failed=self.stats['total_calls_failed'],
                    current_cps=actual_cps,
                    average_setup_time=avg_setup_time,
                    concurrent_calls=self.concurrent_calls,
                    system_load=system_load
                )
                
                # Adicionar ao histórico
                self.metrics_history.append(current_metric)
                
                # Callback de métricas atualizadas
                if self.on_metrics_updated:
                    self.on_metrics_updated(current_metric)
                
                await asyncio.sleep(self.config.monitoring_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no coletor de métricas: {str(e)}")
                await asyncio.sleep(1)
    
    async def _performance_monitor(self):
        """Monitora performance e ativa emergency brake se necessário."""
        logger.info("🔍 Iniciando monitor de performance")
        
        while self.is_running:
            try:
                # Verificar se há métricas suficientes
                if len(self.metrics_history) < 10:
                    await asyncio.sleep(5)
                    continue
                
                # Calcular taxa de sucesso dos últimos 10 minutos
                recent_metrics = [m for m in self.metrics_history 
                                if (datetime.now() - m.timestamp).seconds <= 600]
                
                if recent_metrics:
                    total_initiated = sum(m.calls_initiated for m in recent_metrics)
                    total_failed = sum(m.calls_failed for m in recent_metrics)
                    
                    if total_initiated > 0:
                        success_rate = 1 - (total_failed / total_initiated)
                        
                        # Verificar emergency brake
                        if success_rate < self.config.emergency_brake_threshold:
                            self.stats['emergency_brake_active'] = True
                            logger.warning(f"🚨 EMERGENCY BRAKE ATIVO - Taxa de sucesso: {success_rate:.2%}")
                        elif success_rate > self.config.quality_threshold:
                            self.stats['emergency_brake_active'] = False
                
                await asyncio.sleep(30)  # Verificar a cada 30 segundos
                
            except Exception as e:
                logger.error(f"❌ Erro no monitor de performance: {str(e)}")
                await asyncio.sleep(30)
    
    async def _cps_auto_adjuster(self):
        """Ajusta CPS automaticamente baseado na performance."""
        logger.info("⚡ Iniciando ajustador automático de CPS")
        
        while self.is_running:
            try:
                if not self.config.auto_adjust_cps:
                    await asyncio.sleep(self.config.ramp_up_interval)
                    continue
                
                # Verificar se deve ajustar CPS
                if len(self.metrics_history) >= 5:
                    recent_metrics = list(self.metrics_history)[-5:]
                    
                    # Calcular taxa de sucesso recente
                    total_initiated = sum(m.calls_initiated for m in recent_metrics)
                    total_failed = sum(m.calls_failed for m in recent_metrics)
                    
                    if total_initiated > 0:
                        success_rate = 1 - (total_failed / total_initiated)
                        avg_system_load = statistics.mean(m.system_load for m in recent_metrics)
                        
                        # Lógica de ajuste
                        if (success_rate > self.config.quality_threshold and 
                            avg_system_load < 80 and 
                            self.current_cps < self.config.max_cps):
                            
                            # Aumentar CPS
                            old_cps = self.current_cps
                            self.current_cps = min(
                                self.current_cps + self.config.ramp_up_step,
                                self.config.max_cps
                            )
                            self.call_interval = 1.0 / self.current_cps
                            
                            logger.info(f"📈 CPS aumentado: {old_cps:.1f} → {self.current_cps:.1f}")
                            
                        elif (success_rate < self.config.quality_threshold or 
                              avg_system_load > 90):
                            
                            # Diminuir CPS
                            old_cps = self.current_cps
                            self.current_cps = max(
                                self.current_cps - self.config.ramp_up_step,
                                1.0
                            )
                            self.call_interval = 1.0 / self.current_cps
                            
                            logger.warning(f"📉 CPS reduzido: {old_cps:.1f} → {self.current_cps:.1f}")
                
                await asyncio.sleep(self.config.ramp_up_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no ajustador de CPS: {str(e)}")
                await asyncio.sleep(self.config.ramp_up_interval)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Obtém métricas atuais do sistema."""
        if not self.metrics_history:
            return {
                'current_cps': 0,
                'concurrent_calls': 0,
                'total_calls': 0,
                'success_rate': 0,
                'system_load': 0
            }
        
        latest_metric = self.metrics_history[-1]
        
        # Calcular taxa de sucesso
        total_calls = self.stats['total_calls_initiated']
        failed_calls = self.stats['total_calls_failed']
        success_rate = 1 - (failed_calls / total_calls) if total_calls > 0 else 0
        
        return {
            'current_cps': latest_metric.current_cps,
            'target_cps': self.current_cps,
            'concurrent_calls': self.concurrent_calls,
            'max_concurrent_calls': self.config.max_concurrent_calls,
            'total_calls_initiated': total_calls,
            'total_calls_failed': failed_calls,
            'success_rate': success_rate,
            'system_load': latest_metric.system_load,
            'emergency_brake_active': self.stats['emergency_brake_active'],
            'queue_size': self.call_queue.qsize(),
            'uptime': (datetime.now() - self.stats['session_start_time']).total_seconds()
        }
    
    def set_cps(self, new_cps: float):
        """Define manualmente o CPS target."""
        if 0.1 <= new_cps <= self.config.max_cps:
            self.current_cps = new_cps
            self.call_interval = 1.0 / new_cps
            logger.info(f"🎯 CPS definido manualmente: {new_cps}")
        else:
            logger.warning(f"❌ CPS inválido: {new_cps} (deve estar entre 0.1 e {self.config.max_cps})")
    
    def get_metrics_history(self, minutes: int = 10) -> List[CallMetrics]:
        """Obtém histórico de métricas dos últimos X minutos."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time] 