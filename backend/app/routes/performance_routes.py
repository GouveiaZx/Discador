"""
Rotas API para gerenciamento de performance, testes de carga e limites de CLI.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import json

from app.database import get_db
from app.utils.logger import logger

# Imports opcionais para evitar erros
try:
    from app.services.high_performance_dialer import HighPerformanceDialer, PerformanceConfig
    HAS_HIGH_PERFORMANCE_DIALER = True
except ImportError:
    HAS_HIGH_PERFORMANCE_DIALER = False
    print("⚠️ Warning: high_performance_dialer not available")
    # Classe fallback
    class PerformanceConfig:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

try:
    from app.services.load_test_service import LoadTestService, LoadTestConfig
    HAS_LOAD_TEST_SERVICE = True
except ImportError:
    HAS_LOAD_TEST_SERVICE = False
    print("⚠️ Warning: load_test_service not available")
    # Classes fallback
    class LoadTestConfig:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class LoadTestService:
        def __init__(self, *args, **kwargs):
            pass

try:
    from app.services.cli_country_limits_service import CliCountryLimitsService
    HAS_CLI_LIMITS_SERVICE = True
except ImportError:
    HAS_CLI_LIMITS_SERVICE = False
    print("⚠️ Warning: cli_country_limits_service not available")
    # Classe fallback
    class CliCountryLimitsService:
        def __init__(self, *args, **kwargs):
            pass

try:
    from app.services.dtmf_country_config_service import DTMFCountryConfigService
    HAS_DTMF_CONFIG_SERVICE = True
except ImportError:
    HAS_DTMF_CONFIG_SERVICE = False
    print("⚠️ Warning: dtmf_country_config_service not available")
    # Classe fallback
    class DTMFCountryConfigService:
        def __init__(self, *args, **kwargs):
            pass

try:
    from app.services.dynamic_caller_id_service import DynamicCallerIdService
    HAS_DYNAMIC_CALLER_ID_SERVICE = True
except ImportError:
    HAS_DYNAMIC_CALLER_ID_SERVICE = False
    class DynamicCallerIdService:
        def __init__(self, db): 
            pass

try:
    from app.services.advanced_dnc_service import AdvancedDNCService
    HAS_ADVANCED_DNC_SERVICE = True
except ImportError:
    HAS_ADVANCED_DNC_SERVICE = False
    class AdvancedDNCService:
        def __init__(self, db): 
            pass

try:
    from app.services.cli_local_randomization_service import CliLocalRandomizationService
    HAS_CLI_LOCAL_RANDOMIZATION_SERVICE = True
except ImportError:
    HAS_CLI_LOCAL_RANDOMIZATION_SERVICE = False
    class CliLocalRandomizationService:
        def __init__(self, db): 
            pass

try:
    from app.services.cli_pattern_generator_service import CliPatternGeneratorService
    HAS_CLI_PATTERN_GENERATOR_SERVICE = True
except ImportError:
    HAS_CLI_PATTERN_GENERATOR_SERVICE = False
    print("⚠️ Warning: cli_pattern_generator_service not available")
    
    # Classe fallback com métodos básicos
    class CliPatternGeneratorService:
        def __init__(self, db): 
            self.db = db
            
        def get_supported_countries(self):
            """Fallback: retorna países básicos se o serviço não estiver disponível."""
            return [
                {'country_code': 'usa', 'country_name': 'Estados Unidos', 'phone_code': '+1', 'strategy': 'basic', 'area_codes': ['305', '425']},
                {'country_code': 'canada', 'country_name': 'Canadá', 'phone_code': '+1', 'strategy': 'basic', 'area_codes': ['416', '514']},
                {'country_code': 'mexico', 'country_name': 'México', 'phone_code': '+52', 'strategy': 'basic', 'area_codes': ['55', '81']},
                {'country_code': 'brasil', 'country_name': 'Brasil', 'phone_code': '+55', 'strategy': 'basic', 'area_codes': ['11', '21']},
                {'country_code': 'colombia', 'country_name': 'Colombia', 'phone_code': '+57', 'strategy': 'basic', 'area_codes': ['1', '4']},
                {'country_code': 'argentina', 'country_name': 'Argentina', 'phone_code': '+54', 'strategy': 'basic', 'area_codes': ['11', '351']},
                {'country_code': 'chile', 'country_name': 'Chile', 'phone_code': '+56', 'strategy': 'basic', 'area_codes': ['2', '32']},
                {'country_code': 'peru', 'country_name': 'Perú', 'phone_code': '+51', 'strategy': 'basic', 'area_codes': ['1', '44']}
            ]
            
        def get_country_patterns(self, country):
            """Fallback: retorna padrões básicos."""
            return {
                'country_code': country,
                'country_name': country.title(),
                'phone_code': '+1',
                'strategy': 'basic_fallback',
                'area_codes': {'default': {'name': 'Default', 'patterns': [{'mask': 'xxxx-xxxx', 'weight': 1.0}]}}
            }
            
        def generate_cli_with_pattern(self, **kwargs):
            """Fallback: retorna erro."""
            return {
                'success': False,
                'error': 'CLI Pattern Generator service not available. Using fallback.',
                'generated_clis': []
            }
            
        def get_generation_stats(self):
            """Fallback: retorna stats vazias."""
            return {
                'total_generated': 0,
                'countries_supported': 8,
                'message': 'Service not available'
            }

# Modelos Pydantic para requests/responses
from pydantic import BaseModel

class PerformanceConfigRequest(BaseModel):
    max_cps: float = 30.0
    initial_cps: float = 5.0
    ramp_up_step: float = 2.0
    ramp_up_interval: int = 10
    max_concurrent_calls: int = 500
    auto_adjust_cps: bool = True

class LoadTestConfigRequest(BaseModel):
    target_cps: float = 25.0
    duration_minutes: int = 10
    countries_to_test: List[str] = ["usa", "mexico", "brasil", "colombia"]
    number_of_clis: int = 1000

class CountryConfigRequest(BaseModel):
    country: str
    connect_key: str = "1"
    disconnect_key: str = "9"
    repeat_key: str = "0"
    menu_timeout: int = 10
    instructions: str = "Press 1 to connect"

class CliLimitRequest(BaseModel):
    country: str
    daily_limit: int = 100

# Instâncias globais
router = APIRouter(prefix="/performance", tags=["performance"])
dialer_instance = None
load_test_service = None
websocket_connections = set()

# ========== ROTAS DE PERFORMANCE EM TEMPO REAL ==========

@router.get("/metrics/realtime")
async def get_realtime_metrics(db: Session = Depends(get_db)):
    """Obtém métricas em tempo real do sistema."""
    try:
        if not HAS_HIGH_PERFORMANCE_DIALER or not dialer_instance:
            return {
                "status": "inactive",
                "current_cps": 0,
                "concurrent_calls": 0,
                "success_rate": 0,
                "system_load": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        if hasattr(dialer_instance, 'get_current_metrics'):
            metrics = dialer_instance.get_current_metrics()
        else:
            metrics = {}
        
        # Adicionar informações extras
        cli_stats = {}
        if HAS_CLI_LIMITS_SERVICE:
            try:
                cli_service = CliCountryLimitsService(db)
                if hasattr(cli_service, 'get_usage_statistics'):
                    cli_stats = cli_service.get_usage_statistics()
            except Exception:
                pass
        
        return {
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "dialer_metrics": metrics,
            "cli_stats": cli_stats,
            "uptime": metrics.get("uptime", 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter métricas: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "current_cps": 0,
            "concurrent_calls": 0,
            "success_rate": 0,
            "system_load": 0,
            "timestamp": datetime.now().isoformat()
        }

@router.get("/metrics/history")
async def get_metrics_history(minutes: int = 60, db: Session = Depends(get_db)):
    """Obtém histórico de métricas."""
    try:
        if not HAS_HIGH_PERFORMANCE_DIALER or not dialer_instance:
            return {
                "history": [],
                "message": "Dialer não ativo",
                "total_points": 0,
                "period_minutes": minutes
            }
        
        if hasattr(dialer_instance, 'get_metrics_history'):
            history = dialer_instance.get_metrics_history(minutes)
        
            return {
                "history": [
                    {
                        "timestamp": metric.timestamp.isoformat() if hasattr(metric, 'timestamp') else datetime.now().isoformat(),
                        "current_cps": getattr(metric, 'current_cps', 0),
                        "concurrent_calls": getattr(metric, 'concurrent_calls', 0),
                        "success_rate": getattr(metric, 'calls_answered', 0) / getattr(metric, 'calls_initiated', 1) if getattr(metric, 'calls_initiated', 0) > 0 else 0,
                        "system_load": getattr(metric, 'system_load', 0)
                    }
                    for metric in history
                ],
                "total_points": len(history),
                "period_minutes": minutes,
                "status": "success"
            }
        else:
            return {
                "history": [],
                "message": "Histórico não disponível",
                "total_points": 0,
                "period_minutes": minutes
            }
            
    except Exception as e:
        logger.error(f"❌ Erro ao obter histórico: {str(e)}")
        return {
            "history": [],
            "message": f"Erro: {str(e)}",
            "total_points": 0,
            "period_minutes": minutes
        }

@router.post("/dialer/start")
async def start_dialer(config: PerformanceConfigRequest, db: Session = Depends(get_db)):
    """Inicia o dialer de alta performance."""
    global dialer_instance
    
    try:
        if not HAS_HIGH_PERFORMANCE_DIALER:
            raise HTTPException(
                status_code=503,
                detail="Serviço de dialer não disponível"
            )
        
        if dialer_instance and hasattr(dialer_instance, 'is_active') and dialer_instance.is_active():
            return {
                "status": "already_running",
                "message": "Dialer já está ativo",
                "current_cps": getattr(dialer_instance, 'current_cps', 0)
            }
        
        # Criar configuração
        performance_config = PerformanceConfig(
            max_cps=config.max_cps,
            initial_cps=config.initial_cps,
            ramp_up_step=config.ramp_up_step,
            ramp_up_interval=config.ramp_up_interval,
            max_concurrent_calls=config.max_concurrent_calls,
            auto_adjust_cps=config.auto_adjust_cps
        )
        
        # Inicializar dialer
        dialer_instance = HighPerformanceDialer(performance_config, db)
        
        # Iniciar em background
        asyncio.create_task(dialer_instance.start())
        
        return {
            "status": "started",
            "message": "Dialer iniciado com sucesso",
            "config": config.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar dialer: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao iniciar dialer: {str(e)}"
        )

@router.post("/dialer/stop")
async def stop_dialer():
    """Para o dialer de alta performance."""
    global dialer_instance
    
    try:
        if not dialer_instance:
            return {
                "status": "not_running",
                "message": "Dialer não está ativo"
            }
        
        if hasattr(dialer_instance, 'stop'):
            await dialer_instance.stop()
        
        dialer_instance = None
        
        return {
            "status": "stopped",
            "message": "Dialer parado com sucesso",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao parar dialer: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao parar dialer: {str(e)}"
        )

@router.post("/dialer/cps/{new_cps}")
async def set_cps(new_cps: float):
    """Ajusta o CPS do dialer."""
    try:
        if not dialer_instance:
            raise HTTPException(
                status_code=400,
                detail="Dialer não está ativo"
            )
        
        if hasattr(dialer_instance, 'set_cps'):
            dialer_instance.set_cps(new_cps)
        
        return {
            "status": "updated",
            "message": f"CPS ajustado para {new_cps}",
            "new_cps": new_cps,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao ajustar CPS: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ajustar CPS: {str(e)}"
        )

# ========== ROTAS DE TESTE DE CARGA ==========

@router.post("/load-test/start")
async def start_load_test(config: LoadTestConfigRequest, db: Session = Depends(get_db)):
    """Inicia teste de carga."""
    global load_test_service
    
    try:
        if not HAS_LOAD_TEST_SERVICE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de teste de carga não disponível"
            )
        
        if load_test_service and hasattr(load_test_service, 'is_running') and load_test_service.is_running():
            return {
                "status": "already_running",
                "message": "Teste de carga já está em execução"
            }
        
        # Criar configuração
        load_config = LoadTestConfig(
            target_cps=config.target_cps,
            duration_minutes=config.duration_minutes,
            countries_to_test=config.countries_to_test,
            number_of_clis=config.number_of_clis
        )
        
        # Inicializar serviço
        load_test_service = LoadTestService(load_config, db)
        
        # Iniciar em background
        asyncio.create_task(run_load_test_background(load_config))
        
        return {
            "status": "started",
            "message": "Teste de carga iniciado",
            "config": config.dict(),
            "estimated_duration": config.duration_minutes,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar teste de carga: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao iniciar teste: {str(e)}"
        )

@router.post("/load-test/stop")
async def stop_load_test():
    """Para o teste de carga."""
    global load_test_service
    
    try:
        if not load_test_service:
            return {
                "status": "not_running",
                "message": "Teste de carga não está em execução"
            }
        
        if hasattr(load_test_service, 'stop'):
            await load_test_service.stop()
        
        load_test_service = None
        
        return {
            "status": "stopped",
            "message": "Teste de carga parado",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao parar teste: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao parar teste: {str(e)}"
        )

@router.get("/load-test/status")
async def get_load_test_status():
    """Obtém status do teste de carga."""
    try:
        if not load_test_service:
            return {
                "status": "inactive",
                "message": "Nenhum teste em execução"
            }
        
        if hasattr(load_test_service, 'get_status'):
            status = load_test_service.get_status()
            return {
                "status": "active",
                "details": status,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "status": "unknown",
            "message": "Status não disponível"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/load-test/results")
async def get_load_test_results(format: str = "json"):
    """Obtém resultados do teste de carga."""
    try:
        if not load_test_service:
            return {
                "results": [],
                "message": "Nenhum teste executado"
            }
        
        if hasattr(load_test_service, 'get_results'):
            results = load_test_service.get_results()
            
            if format == "csv":
                # Converter para CSV
                import csv
                import io
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Cabeçalho
                writer.writerow(["timestamp", "cps", "concurrent_calls", "success_rate", "response_time"])
                
                # Dados
                for result in results:
                    writer.writerow([
                        result.get("timestamp", ""),
                        result.get("cps", 0),
                        result.get("concurrent_calls", 0),
                        result.get("success_rate", 0),
                        result.get("response_time", 0)
                    ])
                
                return {
                    "format": "csv",
                    "data": output.getvalue(),
                    "total_records": len(results)
                }
            
            return {
                "format": "json",
                "results": results,
                "total_records": len(results),
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "results": [],
            "message": "Resultados não disponíveis"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter resultados: {str(e)}")
        return {
            "results": [],
            "message": f"Erro: {str(e)}"
        }

# ========== ROTAS DE LIMITES CLI ==========

@router.get("/cli/limits")
async def get_cli_limits(db: Session = Depends(get_db)):
    """Obtém limites de CLI por país."""
    try:
        if not HAS_CLI_LIMITS_SERVICE:
            return {
                "limits": {},
                "message": "Serviço de limites CLI não disponível"
            }
        
        cli_service = CliCountryLimitsService(db)
        
        if hasattr(cli_service, 'get_all_limits'):
            limits = cli_service.get_all_limits()
            return {
                "limits": limits,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "limits": {},
            "message": "Método não disponível"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter limites: {str(e)}")
        return {
            "limits": {},
            "message": f"Erro: {str(e)}"
        }

@router.post("/cli/limits/{country}")
async def set_cli_limit(country: str, request: CliLimitRequest, db: Session = Depends(get_db)):
    """Define limite de CLI para país."""
    try:
        if not HAS_CLI_LIMITS_SERVICE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de limites CLI não disponível"
            )
        
        cli_service = CliCountryLimitsService(db)
        
        if hasattr(cli_service, 'set_limit'):
            cli_service.set_limit(country, request.daily_limit)
        
        return {
            "status": "updated",
            "country": country,
            "daily_limit": request.daily_limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao definir limite: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao definir limite: {str(e)}"
        )

@router.get("/cli/usage")
async def get_cli_usage(db: Session = Depends(get_db)):
    """Obtém uso atual de CLI por país."""
    try:
        if not HAS_CLI_LIMITS_SERVICE:
            return {
                "usage": {},
                "message": "Serviço de limites CLI não disponível"
            }
        
        cli_service = CliCountryLimitsService(db)
        
        if hasattr(cli_service, 'get_usage_statistics'):
            usage = cli_service.get_usage_statistics()
            return {
                "usage": usage,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "usage": {},
            "message": "Estatísticas não disponíveis"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter uso: {str(e)}")
        return {
            "usage": {},
            "message": f"Erro: {str(e)}"
        }

@router.post("/cli/reset")
async def reset_cli_usage(db: Session = Depends(get_db)):
    """Reseta contadores de uso de CLI."""
    try:
        if not HAS_CLI_LIMITS_SERVICE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de limites CLI não disponível"
            )
        
        cli_service = CliCountryLimitsService(db)
        
        if hasattr(cli_service, 'reset_usage'):
            cli_service.reset_usage()
        
        return {
            "status": "reset",
            "message": "Contadores de uso resetados",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao resetar uso: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao resetar uso: {str(e)}"
        )

# ========== WEBSOCKET ==========

@router.websocket("/ws/performance")
async def websocket_performance(websocket: WebSocket):
    """WebSocket para métricas em tempo real."""
    await websocket.accept()
    websocket_connections.add(websocket)
    
    try:
        while True:
            await asyncio.sleep(1)
            
            # Enviar métricas atuais
            if dialer_instance and hasattr(dialer_instance, 'get_current_metrics'):
                metrics = dialer_instance.get_current_metrics()
                await websocket.send_json({
                    "type": "metrics",
                    "data": metrics,
                    "timestamp": datetime.now().isoformat()
                })
            
    except WebSocketDisconnect:
        websocket_connections.discard(websocket)
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket: {str(e)}")
        websocket_connections.discard(websocket)

async def broadcast_metrics_update(metrics):
    """Broadcast métricas para todos os websockets conectados."""
    if not websocket_connections:
        return
    
    message = {
        "type": "metrics_update",
        "data": metrics,
        "timestamp": datetime.now().isoformat()
    }
    
    disconnected = set()
    for websocket in websocket_connections:
        try:
            await websocket.send_json(message)
        except:
            disconnected.add(websocket)
    
    # Remover conexões mortas
    websocket_connections -= disconnected

# ========== FUNÇÕES AUXILIARES ==========

async def run_load_test_background(config: LoadTestConfig):
    """Executa teste de carga em background."""
    global load_test_service
    
    try:
        if load_test_service and hasattr(load_test_service, 'run'):
            await load_test_service.run()
        
        logger.info("🎯 Teste de carga finalizado")
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de carga: {str(e)}")
    
    finally:
        load_test_service = None

# ========== ROTAS DE SAÚDE ==========

@router.get("/health")
async def health_check():
    """Verifica saúde dos serviços."""
    return {
        "status": "healthy",
        "services": {
            "high_performance_dialer": HAS_HIGH_PERFORMANCE_DIALER,
            "load_test_service": HAS_LOAD_TEST_SERVICE,
            "cli_limits_service": HAS_CLI_LIMITS_SERVICE,
            "dtmf_config_service": HAS_DTMF_CONFIG_SERVICE,
            "dynamic_caller_id_service": HAS_DYNAMIC_CALLER_ID_SERVICE,
            "advanced_dnc_service": HAS_ADVANCED_DNC_SERVICE,
            "cli_local_randomization_service": HAS_CLI_LOCAL_RANDOMIZATION_SERVICE,
            "cli_pattern_generator_service": HAS_CLI_PATTERN_GENERATOR_SERVICE
        },
        "dialer_active": dialer_instance is not None,
        "load_test_active": load_test_service is not None,
        "websocket_connections": len(websocket_connections),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste simples."""
    return {
        "status": "ok",
        "message": "Performance routes funcionando",
        "timestamp": datetime.now().isoformat()
    }

# ========== ROTAS DTMF ==========

def get_dtmf_fallback_configs():
    """Configurações DTMF fallback para garantir funcionamento com 60+ países."""
    return {
        # América do Norte
        "usa": {
            "country_name": "Estados Unidos",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "canada": {
            "country_name": "Canadá",
            "connect_key": "1", 
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "dominican_republic": {
            "country_name": "República Dominicana",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "puerto_rico": {
            "country_name": "Porto Rico",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "jamaica": {
            "country_name": "Jamaica",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        
        # América Latina
        "mexico": {
            "country_name": "México",
            "connect_key": "3",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 15,
            "instructions": "Presione 3 para conectar, 9 para desconectar, 0 para repetir"
        },
        "brasil": {
            "country_name": "Brasil",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Pressione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "argentina": {
            "country_name": "Argentina",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "colombia": {
            "country_name": "Colombia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "chile": {
            "country_name": "Chile",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "peru": {
            "country_name": "Peru",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "venezuela": {
            "country_name": "Venezuela",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "ecuador": {
            "country_name": "Ecuador",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "bolivia": {
            "country_name": "Bolivia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "uruguay": {
            "country_name": "Uruguay",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "paraguay": {
            "country_name": "Paraguay",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "costa_rica": {
            "country_name": "Costa Rica",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "panama": {
            "country_name": "Panamá",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "guatemala": {
            "country_name": "Guatemala",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "honduras": {
            "country_name": "Honduras",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "el_salvador": {
            "country_name": "El Salvador",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "nicaragua": {
            "country_name": "Nicaragua",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "cuba": {
            "country_name": "Cuba",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        
        # Europa
        "spain": {
            "country_name": "España",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Pulse 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "portugal": {
            "country_name": "Portugal",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Prima 1 para conectar, 9 para desconectar, 0 para repetir"
        },
        "france": {
            "country_name": "França",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Appuyez sur 1 pour connecter, 9 pour déconnecter, 0 pour répéter"
        },
        "germany": {
            "country_name": "Alemanha",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Drücken Sie 1 zum Verbinden, 9 zum Trennen, 0 zum Wiederholen"
        },
        "italy": {
            "country_name": "Itália",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Premi 1 per connettere, 9 per disconnettere, 0 per ripetere"
        },
        "uk": {
            "country_name": "Reino Unido",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "netherlands": {
            "country_name": "Holanda",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Druk op 1 om te verbinden, 9 om te verbreken, 0 om te herhalen"
        },
        "belgium": {
            "country_name": "Bélgica",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Appuyez sur 1 pour connecter, 9 pour déconnecter, 0 pour répéter"
        },
        "switzerland": {
            "country_name": "Suíça",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Drücken Sie 1 zum Verbinden, 9 zum Trennen, 0 zum Wiederholen"
        },
        "austria": {
            "country_name": "Áustria",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Drücken Sie 1 zum Verbinden, 9 zum Trennen, 0 zum Wiederholen"
        },
        "sweden": {
            "country_name": "Suécia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Tryck 1 för att ansluta, 9 för att koppla från, 0 för att upprepa"
        },
        "norway": {
            "country_name": "Noruega",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Trykk 1 for å koble til, 9 for å koble fra, 0 for å gjenta"
        },
        "denmark": {
            "country_name": "Dinamarca",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Tryk på 1 for at forbinde, 9 for at afbryde, 0 for at gentage"
        },
        "finland": {
            "country_name": "Finlândia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Paina 1 yhdistääksesi, 9 katkaistaksesi, 0 toistaaksesi"
        },
        "poland": {
            "country_name": "Polônia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Naciśnij 1, aby połączyć, 9, aby rozłączyć, 0, aby powtórzyć"
        },
        "czech_republic": {
            "country_name": "República Checa",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Stiskněte 1 pro připojení, 9 pro odpojení, 0 pro opakování"
        },
        "hungary": {
            "country_name": "Hungria",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Nyomja meg az 1-et a csatlakozáshoz, a 9-et a bontáshoz, a 0-t az ismétléshez"
        },
        "greece": {
            "country_name": "Grécia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Πατήστε 1 για σύνδεση, 9 για αποσύνδεση, 0 για επανάληψη"
        },
        "turkey": {
            "country_name": "Turquia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Bağlanmak için 1'e, bağlantıyı kesmek için 9'a, tekrarlamak için 0'a basın"
        },
        "russia": {
            "country_name": "Rússia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Нажмите 1 для соединения, 9 для отключения, 0 для повтора"
        },
        "ukraine": {
            "country_name": "Ucrânia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Натисніть 1 для з'єднання, 9 для відключення, 0 для повтору"
        },
        
        # Ásia
        "india": {
            "country_name": "Índia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "philippines": {
            "country_name": "Filipinas",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "malaysia": {
            "country_name": "Malásia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "singapore": {
            "country_name": "Singapura",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "thailand": {
            "country_name": "Tailândia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "indonesia": {
            "country_name": "Indonésia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "japan": {
            "country_name": "Japão",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "接続する場合は1を、切断する場合は9を、繰り返す場合は0を押してください"
        },
        "south_korea": {
            "country_name": "Coreia do Sul",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "연결하려면 1번을, 끊으려면 9번을, 반복하려면 0번을 누르세요"
        },
        "china": {
            "country_name": "China",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "按1连接，按9断开，按0重复"
        },
        "hong_kong": {
            "country_name": "Hong Kong",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "taiwan": {
            "country_name": "Taiwan",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "按1連接，按9斷開，按0重複"
        },
        "vietnam": {
            "country_name": "Vietnã",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Nhấn 1 để kết nối, 9 để ngắt kết nối, 0 để lặp lại"
        },
        "pakistan": {
            "country_name": "Paquistão",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "bangladesh": {
            "country_name": "Bangladesh",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "sri_lanka": {
            "country_name": "Sri Lanka",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        
        # Oceania
        "australia": {
            "country_name": "Austrália",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "new_zealand": {
            "country_name": "Nova Zelândia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        
        # África
        "south_africa": {
            "country_name": "África do Sul",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "nigeria": {
            "country_name": "Nigéria",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "kenya": {
            "country_name": "Quênia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Press 1 to connect, 9 to disconnect, 0 to repeat"
        },
        "morocco": {
            "country_name": "Marrocos",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "Appuyez sur 1 pour connecter, 9 pour déconnecter, 0 pour répéter"
        },
        "egypt": {
            "country_name": "Egito",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "اضغط 1 للاتصال، 9 لقطع الاتصال، 0 للتكرار"
        },
        
        # Oriente Médio
        "israel": {
            "country_name": "Israel",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "לחץ 1 להתחבר, 9 להתנתק, 0 לחזור"
        },
        "uae": {
            "country_name": "Emirados Árabes Unidos",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "اضغط 1 للاتصال، 9 لقطع الاتصال، 0 للتكرار"
        },
        "saudi_arabia": {
            "country_name": "Arábia Saudita",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "اضغط 1 للاتصال، 9 لقطع الاتصال، 0 للتكرار"
        },
        "qatar": {
            "country_name": "Qatar",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "اضغط 1 للاتصال، 9 لقطع الاتصال، 0 للتكرار"
        },
        "kuwait": {
            "country_name": "Kuwait",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "اضغط 1 للاتصال، 9 لقطع الاتصال، 0 للتكرار"
        },
        "lebanon": {
            "country_name": "Líbano",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "اضغط 1 للاتصال، 9 لقطع الاتصال، 0 للتكرار"
        },
        "jordan": {
            "country_name": "Jordânia",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "اضغط 1 للاتصال، 9 لقطع الاتصال، 0 للتكرار"
        },
        "iran": {
            "country_name": "Irã",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "menu_timeout": 10,
            "instructions": "برای اتصال 1 را فشار دهید، برای قطع اتصال 9 را، برای تکرار 0 را"
        }
    }

@router.get("/dtmf/configs")
async def get_dtmf_configs(db: Session = Depends(get_db)):
    """Obtém todas as configurações DTMF dos países."""
    try:
        if not HAS_DTMF_CONFIG_SERVICE:
            # Fallback com configurações diretas
            return {
                "status": "success",
                "configs": get_dtmf_fallback_configs(),
                "timestamp": datetime.now().isoformat(),
                "message": "Usando configurações fallback"
            }
        
        dtmf_service = DTMFCountryConfigService(db)
        
        if hasattr(dtmf_service, 'get_all_country_configs'):
            configs = dtmf_service.get_all_country_configs()
            return {
                "status": "success",
                "configs": configs,
                "timestamp": datetime.now().isoformat()
            }
        
        # Fallback se método não existe
        return {
            "status": "success",
            "configs": get_dtmf_fallback_configs(),
            "timestamp": datetime.now().isoformat(),
            "message": "Usando configurações fallback"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter configurações DTMF: {str(e)}")
        # Ainda assim retorna fallback para não quebrar o frontend
        return {
            "status": "success",
            "configs": get_dtmf_fallback_configs(),
            "timestamp": datetime.now().isoformat(),
            "message": f"Usando fallback devido a erro: {str(e)}"
        }

@router.get("/dtmf/configs/{country}")
async def get_dtmf_config_by_country(country: str, db: Session = Depends(get_db)):
    """Obtém configuração DTMF específica de um país."""
    try:
        if not HAS_DTMF_CONFIG_SERVICE:
            raise HTTPException(
                status_code=503,
                detail="Serviço DTMF não disponível"
            )
        
        dtmf_service = DTMFCountryConfigService(db)
        
        if hasattr(dtmf_service, 'get_country_config'):
            config = dtmf_service.get_country_config(country)
            if not config:
                raise HTTPException(
                    status_code=404,
                    detail=f"Configuração DTMF não encontrada para país: {country}"
                )
            
            return {
                "status": "success",
                "country": country,
                "config": config,
                "timestamp": datetime.now().isoformat()
            }
        
        raise HTTPException(
            status_code=503,
            detail="Método não disponível"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao obter configuração DTMF para {country}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter configuração: {str(e)}"
        )

@router.post("/dtmf/configs/{country}")
async def update_dtmf_config(
    country: str,
    config: CountryConfigRequest,
    db: Session = Depends(get_db)
):
    """Atualiza configuração DTMF de um país."""
    try:
        if not HAS_DTMF_CONFIG_SERVICE:
            raise HTTPException(
                status_code=503,
                detail="Serviço DTMF não disponível"
            )
        
        dtmf_service = DTMFCountryConfigService(db)
        
        if hasattr(dtmf_service, 'update_country_config'):
            result = dtmf_service.update_country_config(country, config.dict())
            return {
                "status": "success",
                "country": country,
                "config": result,
                "message": f"Configuração DTMF atualizada para {country}",
                "timestamp": datetime.now().isoformat()
            }
        
        raise HTTPException(
            status_code=503,
            detail="Método não disponível"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar configuração DTMF para {country}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar configuração: {str(e)}"
        )

# ========== ROTAS CLI PATTERN GENERATOR ==========

@router.get("/cli-pattern/countries")
async def get_supported_countries(db: Session = Depends(get_db)):
    """Obtiene lista de países soportados para generación CLI."""
    try:
        logger.info("🌍 Solicitando lista de países soportados...")
        
        # Verificar se o serviço está disponível
        if not HAS_CLI_PATTERN_GENERATOR_SERVICE:
            logger.warning("⚠️ Usando serviço CLI Pattern Generator em modo fallback")
        
        cli_service = CliPatternGeneratorService(db)
        countries = cli_service.get_supported_countries()
        
        logger.info(f"✅ Retornando {len(countries)} países soportados")
        
        return {
            "success": True,
            "data": countries,
            "total_countries": len(countries),
            "service_available": HAS_CLI_PATTERN_GENERATOR_SERVICE,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error al obtener países soportados: {str(e)}")
        
        # Fallback manual se todo falhar
        fallback_countries = [
            {'country_code': 'usa', 'country_name': 'Estados Unidos', 'phone_code': '+1'},
            {'country_code': 'mexico', 'country_name': 'México', 'phone_code': '+52'},
            {'country_code': 'brasil', 'country_name': 'Brasil', 'phone_code': '+55'},
            {'country_code': 'colombia', 'country_name': 'Colombia', 'phone_code': '+57'},
            {'country_code': 'argentina', 'country_name': 'Argentina', 'phone_code': '+54'}
        ]
        
        logger.warning(f"🔄 Usando fallback manual con {len(fallback_countries)} países")
        
        return {
            "success": True,
            "data": fallback_countries,
            "total_countries": len(fallback_countries),
            "service_available": False,
            "fallback": True,
            "timestamp": datetime.now().isoformat()
        }

@router.get("/cli-pattern/patterns/{country}")
async def get_country_patterns(
    country: str,
    db: Session = Depends(get_db)
):
    """Obtiene patrones disponibles para un país."""
    try:
        cli_service = CliPatternGeneratorService(db)
        patterns = cli_service.get_country_patterns(country)
        
        if not patterns:
            raise HTTPException(
                status_code=404,
                detail=f"País {country} no soportado"
            )
        
        return {
            "success": True,
            "data": patterns,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al obtener patrones del país: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patrones del país: {str(e)}"
        )

@router.post("/cli-pattern/generate")
async def generate_cli_pattern(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Genera CLIs con patrones personalizados."""
    try:
        cli_service = CliPatternGeneratorService(db)
        
        # Parámetros obligatorios
        destination_number = request.get("destination_number")
        if not destination_number:
            raise HTTPException(
                status_code=400,
                detail="destination_number es obligatorio"
            )
        
        # Parámetros opcionales
        custom_pattern = request.get("custom_pattern")
        custom_area_code = request.get("custom_area_code")
        quantity = request.get("quantity", 1)
        country_override = request.get("country_override")
        
        result = cli_service.generate_cli_with_pattern(
            destination_number=destination_number,
            custom_pattern=custom_pattern,
            custom_area_code=custom_area_code,
            quantity=quantity,
            country_override=country_override
        )
        
        return {
            "success": result.get("success", False),
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al generar patrones CLI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar patrones CLI: {str(e)}"
        )

@router.post("/cli-pattern/bulk-generate")
async def generate_bulk_cli_patterns(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Genera CLIs para múltiples números."""
    try:
        cli_service = CliPatternGeneratorService(db)
        
        # Parámetros obligatorios
        destination_numbers = request.get("destination_numbers")
        if not destination_numbers or not isinstance(destination_numbers, list):
            raise HTTPException(
                status_code=400,
                detail="destination_numbers es obligatorio y debe ser una lista"
            )
        
        # Parámetros opcionales
        custom_pattern = request.get("custom_pattern")
        
        result = cli_service.generate_bulk_patterns(
            destination_numbers=destination_numbers,
            custom_pattern=custom_pattern
        )
        
        return {
            "success": result.get("success", False),
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en generación masiva: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en generación masiva: {str(e)}"
        )

@router.get("/cli-pattern/stats")
async def get_cli_pattern_stats(db: Session = Depends(get_db)):
    """Obtiene estadísticas de generación de patrones CLI."""
    try:
        cli_service = CliPatternGeneratorService(db)
        stats = cli_service.get_generation_stats()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error al obtener estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

@router.post("/cli-pattern/bulk-generate")
async def bulk_generate_cli_patterns(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Gera múltiplos CLIs baseados em padrões."""
    try:
        if not HAS_CLI_PATTERN_GENERATOR_SERVICE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de padrões CLI não disponível"
            )
        
        cli_service = CliPatternGeneratorService(db)
        
        # Parâmetros obrigatórios
        destination_numbers = request.get("destination_numbers", [])
        if not destination_numbers:
            raise HTTPException(
                status_code=400,
                detail="destination_numbers é obrigatório"
            )
        
        # Parâmetros opcionais
        pattern = request.get("pattern")
        country = request.get("country")
        
        if hasattr(cli_service, 'bulk_generate_cli_patterns'):
            results = cli_service.bulk_generate_cli_patterns(
                destination_numbers=destination_numbers,
                pattern=pattern,
                country=country
            )
            
            return {
                "status": "success",
                "total_generated": len(results),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
        
        # Fallback para geração individual
        results = []
        for destination_number in destination_numbers:
            try:
                if hasattr(cli_service, 'generate_cli_pattern'):
                    result = cli_service.generate_cli_pattern(
                        destination_number=destination_number,
                        pattern=pattern,
                        country=country
                    )
                    results.append({
                        "destination_number": destination_number,
                        "generated_cli": result.get("cli"),
                        "pattern_used": result.get("pattern"),
                        "country": result.get("country"),
                        "status": "success"
                    })
                else:
                    results.append({
                        "destination_number": destination_number,
                        "status": "error",
                        "error": "Método não disponível"
                    })
            except Exception as e:
                results.append({
                    "destination_number": destination_number,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "total_generated": len([r for r in results if r.get("status") == "success"]),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar padrões em lote: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar padrões em lote: {str(e)}"
        )

@router.get("/cli-pattern/stats")
async def get_cli_pattern_stats(
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de geração de padrões CLI."""
    try:
        if not HAS_CLI_PATTERN_GENERATOR_SERVICE:
            return {
                "stats": {},
                "message": "Serviço de padrões CLI não disponível"
            }
        
        cli_service = CliPatternGeneratorService(db)
        
        if hasattr(cli_service, 'get_generation_stats'):
            stats = cli_service.get_generation_stats(country)
            return {
                "stats": stats,
                "country": country,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "stats": {},
            "message": "Estatísticas não disponíveis"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
        return {
            "stats": {},
            "message": f"Erro: {str(e)}"
        }

@router.get("/cli-pattern/examples/{country}")
async def get_pattern_examples(country: str, db: Session = Depends(get_db)):
    """Obtém exemplos de padrões para um país."""
    try:
        if not HAS_CLI_PATTERN_GENERATOR_SERVICE:
            return {
                "examples": [],
                "message": "Serviço de padrões CLI não disponível"
            }
        
        cli_service = CliPatternGeneratorService(db)
        
        if hasattr(cli_service, 'get_pattern_examples'):
            examples = cli_service.get_pattern_examples(country)
            return {
                "country": country,
                "examples": examples,
                "total": len(examples),
                "timestamp": datetime.now().isoformat()
            }
        
        # Fallback com exemplos padrão
        examples = []
        if country.lower() == "usa":
            examples = [
                {"pattern": "2xx-xxxx", "example": "+1 305 221-4567", "description": "Padrão Miami local"},
                {"pattern": "35x-xxxx", "example": "+1 305 350-1234", "description": "Padrão Miami específico"}
            ]
        elif country.lower() == "mexico":
            examples = [
                {"pattern": "xxxx-xxxx", "example": "+52 55 1234-5678", "description": "Padrão CDMX geral"}
            ]
        elif country.lower() == "brasil":
            examples = [
                {"pattern": "9xxxx-xxxx", "example": "+55 11 99123-4567", "description": "Padrão São Paulo celular"}
            ]
        
        return {
            "country": country,
            "examples": examples,
            "total": len(examples),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter exemplos: {str(e)}")
        return {
            "examples": [],
            "message": f"Erro: {str(e)}"
        }

@router.post("/cli-pattern/validate")
async def validate_cli_pattern(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Valida um padrão CLI."""
    try:
        if not HAS_CLI_PATTERN_GENERATOR_SERVICE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de padrões CLI não disponível"
            )
        
        cli_service = CliPatternGeneratorService(db)
        
        # Parâmetros obrigatórios
        pattern = request.get("pattern")
        country = request.get("country")
        
        if not pattern or not country:
            raise HTTPException(
                status_code=400,
                detail="pattern e country são obrigatórios"
            )
        
        if hasattr(cli_service, 'validate_pattern'):
            validation = cli_service.validate_pattern(pattern, country)
            return {
                "pattern": pattern,
                "country": country,
                "is_valid": validation.get("valid", False),
                "message": validation.get("message", ""),
                "suggestions": validation.get("suggestions", []),
                "timestamp": datetime.now().isoformat()
            }
        
        # Validação básica
        is_valid = True
        message = "Padrão válido"
        suggestions = []
        
        if "x" not in pattern:
            is_valid = False
            message = "Padrão deve conter pelo menos um 'x'"
            suggestions.append("Use 'x' para dígitos variáveis")
        
        return {
            "pattern": pattern,
            "country": country,
            "is_valid": is_valid,
            "message": message,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao validar padrão: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao validar padrão: {str(e)}"
        )