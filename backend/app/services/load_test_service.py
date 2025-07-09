"""
Serviço de Testes de Carga para Sistema de Discado
Valida performance com 20-30 CPS e monitora comportamento do sistema.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import statistics
import json
import uuid

from app.services.high_performance_dialer import HighPerformanceDialer, PerformanceConfig
from app.services.cli_country_limits_service import CliCountryLimitsService
from app.utils.logger import logger

@dataclass
class LoadTestConfig:
    """Configuração do teste de carga."""
    target_cps: float = 25.0
    duration_minutes: int = 10
    ramp_up_time: int = 60  # segundos
    countries_to_test: List[str] = None
    number_of_clis: int = 1000
    concurrent_campaigns: int = 5
    test_numbers_per_country: int = 100
    
    def __post_init__(self):
        if self.countries_to_test is None:
            self.countries_to_test = ['usa', 'mexico', 'brasil', 'colombia', 'argentina']

@dataclass
class LoadTestResult:
    """Resultado do teste de carga."""
    test_id: str
    start_time: datetime
    end_time: datetime
    config: LoadTestConfig
    
    # Métricas gerais
    total_calls_attempted: int
    total_calls_successful: int
    total_calls_failed: int
    success_rate: float
    
    # Métricas de performance
    actual_cps: float
    max_cps_achieved: float
    average_setup_time: float
    max_concurrent_calls: int
    
    # Métricas por país
    country_stats: Dict[str, Dict[str, Any]]
    
    # Métricas de CLI
    cli_usage_stats: Dict[str, Any]
    
    # Métricas de sistema
    system_load_avg: float
    memory_usage_avg: float
    error_details: List[Dict[str, Any]]
    
    # Status do teste
    test_completed: bool
    test_interrupted: bool
    interruption_reason: Optional[str]

class LoadTestService:
    """Serviço para executar testes de carga no sistema de discado."""
    
    def __init__(self, db_session):
        self.db = db_session
        self.cli_limits_service = CliCountryLimitsService(db_session)
        
        # Estado do teste
        self.current_test: Optional[LoadTestResult] = None
        self.is_running = False
        self.dialer: Optional[HighPerformanceDialer] = None
        
        # Dados de teste
        self.test_numbers = self._generate_test_numbers()
        self.test_clis = self._generate_test_clis()
        
        # Estatísticas em tempo real
        self.test_stats = {
            'calls_per_country': defaultdict(int),
            'errors_per_country': defaultdict(int),
            'response_times': defaultdict(list),
            'cli_usage': defaultdict(int),
            'system_metrics': []
        }
    
    def _generate_test_numbers(self) -> Dict[str, List[str]]:
        """Gera números de teste para diferentes países."""
        test_numbers = {
            'usa': [f"1555{i:07d}" for i in range(1, 101)],
            'mexico': [f"52555{i:06d}" for i in range(1, 101)],
            'brasil': [f"5511{i:08d}" for i in range(1, 101)],
            'colombia': [f"571{i:08d}" for i in range(1, 101)],
            'argentina': [f"5411{i:08d}" for i in range(1, 101)]
        }
        return test_numbers
    
    def _generate_test_clis(self) -> List[str]:
        """Gera CLIs de teste."""
        clis = []
        
        # CLIs para USA/Canadá
        for i in range(1, 501):
            clis.append(f"1555{i:07d}")
        
        # CLIs para América Latina
        for i in range(1, 501):
            clis.append(f"5511{i:08d}")
        
        return clis
    
    async def run_load_test(self, config: LoadTestConfig) -> LoadTestResult:
        """
        Executa teste de carga completo.
        
        Args:
            config: Configuração do teste
            
        Returns:
            LoadTestResult com resultados completos
        """
        test_id = str(uuid.uuid4())
        logger.info(f"🧪 Iniciando teste de carga: {test_id}")
        
        try:
            # Criar resultado inicial
            self.current_test = LoadTestResult(
                test_id=test_id,
                start_time=datetime.now(),
                end_time=None,
                config=config,
                total_calls_attempted=0,
                total_calls_successful=0,
                total_calls_failed=0,
                success_rate=0.0,
                actual_cps=0.0,
                max_cps_achieved=0.0,
                average_setup_time=0.0,
                max_concurrent_calls=0,
                country_stats={},
                cli_usage_stats={},
                system_load_avg=0.0,
                memory_usage_avg=0.0,
                error_details=[],
                test_completed=False,
                test_interrupted=False,
                interruption_reason=None
            )
            
            self.is_running = True
            
            # Configurar dialer para teste
            performance_config = PerformanceConfig(
                max_cps=config.target_cps,
                initial_cps=1.0,
                ramp_up_step=2.0,
                ramp_up_interval=5,
                max_concurrent_calls=int(config.target_cps * 30),  # 30 segundos de buffer
                thread_pool_size=100,
                auto_adjust_cps=True
            )
            
            self.dialer = HighPerformanceDialer(self.db, performance_config)
            
            # Configurar callbacks
            self.dialer.on_call_initiated = self._on_call_initiated
            self.dialer.on_call_answered = self._on_call_answered
            self.dialer.on_call_failed = self._on_call_failed
            self.dialer.on_metrics_updated = self._on_metrics_updated
            
            # Executar teste
            await self._execute_test(config)
            
            # Finalizar teste
            self.current_test.end_time = datetime.now()
            self.current_test.test_completed = True
            
            # Calcular estatísticas finais
            self._calculate_final_statistics()
            
            logger.info(f"✅ Teste de carga concluído: {test_id}")
            return self.current_test
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de carga: {str(e)}")
            
            if self.current_test:
                self.current_test.test_interrupted = True
                self.current_test.interruption_reason = str(e)
                self.current_test.end_time = datetime.now()
            
            raise
        
        finally:
            self.is_running = False
            if self.dialer:
                await self.dialer.stop()
    
    async def _execute_test(self, config: LoadTestConfig):
        """Executa o teste de carga principal."""
        logger.info(f"🚀 Iniciando teste: {config.target_cps} CPS por {config.duration_minutes} minutos")
        
        # Iniciar dialer
        dialer_task = asyncio.create_task(self.dialer.start())
        
        # Iniciar gerador de chamadas
        generator_task = asyncio.create_task(self._call_generator(config))
        
        # Iniciar monitor de sistema
        monitor_task = asyncio.create_task(self._system_monitor(config))
        
        # Aguardar conclusão
        try:
            await asyncio.wait_for(
                asyncio.gather(generator_task, monitor_task),
                timeout=config.duration_minutes * 60 + 120  # 2 minutos extra
            )
        except asyncio.TimeoutError:
            logger.warning("⏰ Teste interrompido por timeout")
        finally:
            # Parar dialer
            dialer_task.cancel()
    
    async def _call_generator(self, config: LoadTestConfig):
        """Gera chamadas para o teste."""
        logger.info("📞 Iniciando gerador de chamadas")
        
        test_start = time.time()
        test_duration = config.duration_minutes * 60
        
        calls_generated = 0
        
        while self.is_running and (time.time() - test_start) < test_duration:
            try:
                # Selecionar país aleatório
                country = config.countries_to_test[calls_generated % len(config.countries_to_test)]
                
                # Selecionar número de teste
                numbers = self.test_numbers.get(country, [])
                if not numbers:
                    continue
                
                number = numbers[calls_generated % len(numbers)]
                
                # Selecionar CLI de teste
                cli = self.test_clis[calls_generated % len(self.test_clis)]
                
                # Criar dados da chamada
                call_data = {
                    'numero_destino': number,
                    'campana_id': 999,  # Campanha de teste
                    'cli_numero': cli,
                    'test_id': self.current_test.test_id,
                    'country': country,
                    'call_index': calls_generated
                }
                
                # Adicionar à fila do dialer
                await self.dialer.add_call_to_queue(call_data)
                
                calls_generated += 1
                
                # Controlar rate de geração
                if calls_generated % 100 == 0:
                    logger.info(f"📊 Geradas {calls_generated} chamadas")
                
                # Pausa para não sobrecarregar
                await asyncio.sleep(0.001)  # 1ms
                
            except Exception as e:
                logger.error(f"❌ Erro ao gerar chamada: {str(e)}")
                await asyncio.sleep(0.1)
        
        logger.info(f"🏁 Gerador finalizado: {calls_generated} chamadas geradas")
    
    async def _system_monitor(self, config: LoadTestConfig):
        """Monitora métricas do sistema durante o teste."""
        logger.info("🔍 Iniciando monitor de sistema")
        
        while self.is_running:
            try:
                # Coletar métricas do dialer
                if self.dialer:
                    dialer_metrics = self.dialer.get_current_metrics()
                    
                    # Adicionar às estatísticas
                    self.test_stats['system_metrics'].append({
                        'timestamp': datetime.now().isoformat(),
                        'current_cps': dialer_metrics['current_cps'],
                        'concurrent_calls': dialer_metrics['concurrent_calls'],
                        'success_rate': dialer_metrics['success_rate'],
                        'system_load': dialer_metrics['system_load'],
                        'queue_size': dialer_metrics['queue_size']
                    })
                
                await asyncio.sleep(1)  # Coletar a cada segundo
                
            except Exception as e:
                logger.error(f"❌ Erro no monitor de sistema: {str(e)}")
                await asyncio.sleep(1)
    
    def _on_call_initiated(self, call_data: Dict[str, Any], result: Dict[str, Any]):
        """Callback quando uma chamada é iniciada."""
        if self.current_test:
            self.current_test.total_calls_attempted += 1
            
            # Estatísticas por país
            country = call_data.get('country', 'unknown')
            self.test_stats['calls_per_country'][country] += 1
            
            # Estatísticas de CLI
            cli = call_data.get('cli_numero', 'unknown')
            self.test_stats['cli_usage'][cli] += 1
            
            # Tempos de resposta
            if 'setup_time' in result:
                self.test_stats['response_times'][country].append(result['setup_time'])
    
    def _on_call_answered(self, call_data: Dict[str, Any], result: Dict[str, Any]):
        """Callback quando uma chamada é atendida."""
        if self.current_test:
            self.current_test.total_calls_successful += 1
    
    def _on_call_failed(self, call_data: Dict[str, Any], result: Dict[str, Any]):
        """Callback quando uma chamada falha."""
        if self.current_test:
            self.current_test.total_calls_failed += 1
            
            # Estatísticas de erro por país
            country = call_data.get('country', 'unknown')
            self.test_stats['errors_per_country'][country] += 1
            
            # Detalhes do erro
            self.current_test.error_details.append({
                'timestamp': datetime.now().isoformat(),
                'country': country,
                'number': call_data.get('numero_destino', 'unknown'),
                'cli': call_data.get('cli_numero', 'unknown'),
                'error': result.get('error', 'unknown')
            })
    
    def _on_metrics_updated(self, metrics):
        """Callback quando métricas são atualizadas."""
        if self.current_test:
            # Atualizar CPS máximo
            if metrics.current_cps > self.current_test.max_cps_achieved:
                self.current_test.max_cps_achieved = metrics.current_cps
            
            # Atualizar chamadas concorrentes máximas
            if metrics.concurrent_calls > self.current_test.max_concurrent_calls:
                self.current_test.max_concurrent_calls = metrics.concurrent_calls
    
    def _calculate_final_statistics(self):
        """Calcula estatísticas finais do teste."""
        if not self.current_test:
            return
        
        # Taxa de sucesso
        if self.current_test.total_calls_attempted > 0:
            self.current_test.success_rate = (
                self.current_test.total_calls_successful / 
                self.current_test.total_calls_attempted
            )
        
        # CPS médio
        if self.test_stats['system_metrics']:
            cps_values = [m['current_cps'] for m in self.test_stats['system_metrics']]
            self.current_test.actual_cps = statistics.mean(cps_values)
        
        # Tempo médio de setup
        all_response_times = []
        for country_times in self.test_stats['response_times'].values():
            all_response_times.extend(country_times)
        
        if all_response_times:
            self.current_test.average_setup_time = statistics.mean(all_response_times)
        
        # Estatísticas por país
        for country in self.test_stats['calls_per_country'].keys():
            calls_attempted = self.test_stats['calls_per_country'][country]
            calls_failed = self.test_stats['errors_per_country'][country]
            calls_successful = calls_attempted - calls_failed
            
            country_success_rate = calls_successful / calls_attempted if calls_attempted > 0 else 0
            
            country_response_times = self.test_stats['response_times'][country]
            avg_response_time = statistics.mean(country_response_times) if country_response_times else 0
            
            self.current_test.country_stats[country] = {
                'calls_attempted': calls_attempted,
                'calls_successful': calls_successful,
                'calls_failed': calls_failed,
                'success_rate': country_success_rate,
                'average_response_time': avg_response_time
            }
        
        # Estatísticas de CLI
        self.current_test.cli_usage_stats = {
            'total_clis_used': len(self.test_stats['cli_usage']),
            'most_used_cli': max(self.test_stats['cli_usage'].items(), key=lambda x: x[1]) if self.test_stats['cli_usage'] else None,
            'average_uses_per_cli': statistics.mean(self.test_stats['cli_usage'].values()) if self.test_stats['cli_usage'] else 0,
            'usage_distribution': dict(self.test_stats['cli_usage'])
        }
        
        # Métricas de sistema
        if self.test_stats['system_metrics']:
            system_loads = [m['system_load'] for m in self.test_stats['system_metrics']]
            self.current_test.system_load_avg = statistics.mean(system_loads)
    
    def get_test_status(self) -> Dict[str, Any]:
        """Obtém status atual do teste."""
        if not self.current_test:
            return {'status': 'no_test_running'}
        
        duration = (datetime.now() - self.current_test.start_time).total_seconds()
        
        return {
            'status': 'running' if self.is_running else 'completed',
            'test_id': self.current_test.test_id,
            'duration_seconds': duration,
            'calls_attempted': self.current_test.total_calls_attempted,
            'calls_successful': self.current_test.total_calls_successful,
            'calls_failed': self.current_test.total_calls_failed,
            'current_success_rate': self.current_test.success_rate,
            'max_cps_achieved': self.current_test.max_cps_achieved,
            'concurrent_calls': self.current_test.max_concurrent_calls,
            'dialer_metrics': self.dialer.get_current_metrics() if self.dialer else {}
        }
    
    def export_results(self, format: str = 'json') -> str:
        """Exporta resultados do teste."""
        if not self.current_test:
            return "No test results available"
        
        if format == 'json':
            return json.dumps(asdict(self.current_test), indent=2, default=str)
        
        # Formato de relatório
        report = f"""
RELATÓRIO DE TESTE DE CARGA
===========================

Teste ID: {self.current_test.test_id}
Data/Hora: {self.current_test.start_time} - {self.current_test.end_time}
Duração: {self.current_test.config.duration_minutes} minutos

CONFIGURAÇÃO
------------
CPS Alvo: {self.current_test.config.target_cps}
Países: {', '.join(self.current_test.config.countries_to_test)}
CLIs: {self.current_test.config.number_of_clis}

RESULTADOS GERAIS
-----------------
Chamadas Tentadas: {self.current_test.total_calls_attempted}
Chamadas Bem-sucedidas: {self.current_test.total_calls_successful}
Chamadas Falhadas: {self.current_test.total_calls_failed}
Taxa de Sucesso: {self.current_test.success_rate:.2%}

PERFORMANCE
-----------
CPS Médio: {self.current_test.actual_cps:.2f}
CPS Máximo: {self.current_test.max_cps_achieved:.2f}
Tempo Médio Setup: {self.current_test.average_setup_time:.3f}s
Chamadas Concorrentes Máx: {self.current_test.max_concurrent_calls}

ESTATÍSTICAS POR PAÍS
--------------------
"""
        
        for country, stats in self.current_test.country_stats.items():
            report += f"{country.upper()}: {stats['calls_attempted']} chamadas, {stats['success_rate']:.2%} sucesso\n"
        
        return report 