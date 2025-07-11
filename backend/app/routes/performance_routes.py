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
        def __init__(self, db): pass

try:
    from app.services.advanced_dnc_service import AdvancedDNCService
    HAS_ADVANCED_DNC_SERVICE = True
except ImportError:
    HAS_ADVANCED_DNC_SERVICE = False
    class AdvancedDNCService:
        def __init__(self, db): pass

try:
    from app.services.cli_local_randomization_service import CliLocalRandomizationService
    HAS_CLI_LOCAL_RANDOMIZATION_SERVICE = True
except ImportError:
    HAS_CLI_LOCAL_RANDOMIZATION_SERVICE = False
    class CliLocalRandomizationService:
        def __init__(self, db): pass

router = APIRouter(prefix="/performance", tags=["performance"])

# Instância global do dialer (seria melhor usar singleton ou dependency injection)
dialer_instance = None
load_test_service = None
websocket_connections = set()

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
            "period_minutes": minutes
        }
        else:
            return {
                "history": [],
                "message": "Método get_metrics_history não disponível",
                "total_points": 0,
                "period_minutes": minutes
            }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter histórico: {str(e)}")
        return {
            "history": [],
            "message": str(e),
            "total_points": 0,
            "period_minutes": minutes
        }

@router.post("/dialer/start")
async def start_dialer(config: PerformanceConfigRequest, db: Session = Depends(get_db)):
    """Inicia o sistema de discado de alta performance."""
    global dialer_instance
    
    try:
        if not HAS_HIGH_PERFORMANCE_DIALER:
            return {
                "message": "Serviço de discado de alta performance não disponível",
                "status": "service_unavailable",
                "config": config.dict()
            }
        
        if dialer_instance and hasattr(dialer_instance, 'is_running') and dialer_instance.is_running:
            return {"message": "Dialer já está rodando", "status": "already_running"}
        
        # Criar configuração
        performance_config = PerformanceConfig(
            max_cps=config.max_cps,
            initial_cps=config.initial_cps,
            ramp_up_step=config.ramp_up_step,
            ramp_up_interval=config.ramp_up_interval,
            max_concurrent_calls=config.max_concurrent_calls,
            auto_adjust_cps=config.auto_adjust_cps
        )
        
        # Criar e iniciar dialer
        dialer_instance = HighPerformanceDialer(db, performance_config)
        
        # Configurar callbacks para WebSocket
        if hasattr(dialer_instance, 'on_metrics_updated'):
        dialer_instance.on_metrics_updated = broadcast_metrics_update
        
        # Iniciar dialer em background
        if hasattr(dialer_instance, 'start'):
        asyncio.create_task(dialer_instance.start())
        
        logger.info("🚀 Sistema de discado iniciado")
        
        return {
            "message": "Sistema de discado iniciado com sucesso",
            "status": "started",
            "config": config.dict()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar dialer: {str(e)}")
        return {
            "message": f"Erro ao iniciar dialer: {str(e)}",
            "status": "error",
            "config": config.dict()
        }

@router.post("/dialer/stop")
async def stop_dialer():
    """Para o sistema de discado."""
    global dialer_instance
    
    try:
        if not HAS_HIGH_PERFORMANCE_DIALER:
            return {
                "message": "Serviço de discado de alta performance não disponível",
                "status": "service_unavailable"
            }
        
        if not dialer_instance:
            return {"message": "Dialer não está rodando", "status": "not_running"}
        
        if hasattr(dialer_instance, 'stop'):
        await dialer_instance.stop()
        
        dialer_instance = None
        
        logger.info("🛑 Sistema de discado parado")
        
        return {
            "message": "Sistema de discado parado com sucesso",
            "status": "stopped"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao parar dialer: {str(e)}")
        return {
            "message": f"Erro ao parar dialer: {str(e)}",
            "status": "error"
        }

@router.post("/dialer/cps/{new_cps}")
async def set_cps(new_cps: float):
    """Define manualmente o CPS do sistema."""
    try:
        if not HAS_HIGH_PERFORMANCE_DIALER:
            return {
                "message": "Serviço de discado de alta performance não disponível",
                "new_cps": new_cps,
                "status": "service_unavailable"
            }
        
        if not dialer_instance:
            return {
                "message": "Dialer não está rodando",
                "new_cps": new_cps,
                "status": "not_running"
            }
        
        if hasattr(dialer_instance, 'set_cps'):
        dialer_instance.set_cps(new_cps)
        
        return {
            "message": f"CPS definido para {new_cps}",
            "new_cps": new_cps,
            "status": "updated"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao definir CPS: {str(e)}")
        return {
            "message": f"Erro ao definir CPS: {str(e)}",
            "new_cps": new_cps,
            "status": "error"
        }

# ========== ROTAS DE TESTE DE CARGA ==========

@router.post("/load-test/start")
async def start_load_test(config: LoadTestConfigRequest, db: Session = Depends(get_db)):
    """Inicia um teste de carga."""
    global load_test_service
    
    try:
        if not HAS_LOAD_TEST_SERVICE:
            return {
                "message": "Serviço de teste de carga não disponível",
                "status": "service_unavailable",
                "config": config.dict()
            }
        
        if load_test_service and hasattr(load_test_service, 'is_running') and load_test_service.is_running:
            return {"message": "Teste de carga já está rodando", "status": "already_running"}
        
        # Criar configuração do teste
        test_config = LoadTestConfig(
            target_cps=config.target_cps,
            duration_minutes=config.duration_minutes,
            countries_to_test=config.countries_to_test,
            number_of_clis=config.number_of_clis
        )
        
        # Criar e iniciar teste
        load_test_service = LoadTestService(db)
        
        # Executar teste em background
        asyncio.create_task(run_load_test_background(test_config))
        
        logger.info(f"🧪 Teste de carga iniciado: {config.target_cps} CPS")
        
        return {
            "message": "Teste de carga iniciado com sucesso",
            "status": "started",
            "config": config.dict()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar teste: {str(e)}")
        return {
            "message": f"Erro ao iniciar teste: {str(e)}",
            "status": "error",
            "config": config.dict()
        }

@router.post("/load-test/stop")
async def stop_load_test():
    """Para o teste de carga atual."""
    global load_test_service
    
    try:
        if not HAS_LOAD_TEST_SERVICE:
            return {
                "message": "Serviço de teste de carga não disponível",
                "status": "service_unavailable"
            }
        
        if not load_test_service or not hasattr(load_test_service, 'is_running') or not load_test_service.is_running:
            return {"message": "Nenhum teste em execução", "status": "not_running"}
        
        if hasattr(load_test_service, 'is_running'):
        load_test_service.is_running = False
        
        logger.info("🛑 Teste de carga parado")
        
        return {
            "message": "Teste de carga parado com sucesso",
            "status": "stopped"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao parar teste: {str(e)}")
        return {
            "message": f"Erro ao parar teste: {str(e)}",
            "status": "error"
        }

@router.get("/load-test/status")
async def get_load_test_status():
    """Obtém status do teste de carga atual."""
    try:
        if not HAS_LOAD_TEST_SERVICE:
            return {
                "status": "service_unavailable",
                "message": "Serviço de teste de carga não disponível",
                "test_status": "inactive",
                "timestamp": datetime.now().isoformat()
            }
        
        if not load_test_service:
            return {
                "status": "no_test", 
                "message": "Nenhum teste executado",
                "test_status": "inactive",
                "timestamp": datetime.now().isoformat()
            }
        
        status = load_test_service.get_test_status()
        
        return {
            "status": "success",
            "test_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status do teste: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "test_status": "error",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/load-test/results")
async def get_load_test_results(format: str = "json"):
    """Obtém resultados do último teste de carga."""
    try:
        if not HAS_LOAD_TEST_SERVICE:
            return {
                "status": "service_unavailable",
                "message": "Serviço de teste de carga não disponível",
                "results": None,
                "format": format
            }
        
        if not load_test_service:
            return {
                "status": "no_test",
                "message": "Nenhum teste executado",
                "results": None,
                "format": format
            }
        
        if hasattr(load_test_service, 'export_results'):
        results = load_test_service.export_results(format)
        
        if format == "json":
            return {
                "status": "success",
                "format": format,
                "results": json.loads(results)
            }
        else:
            return {
                "status": "success",
                "format": format,
                "results": results
                }
        else:
            return {
                "status": "method_unavailable",
                "message": "Método export_results não disponível",
                "results": None,
                "format": format
            }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter resultados: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "results": None,
            "format": format
        }

# ========== ROTAS DE CLI E PAÍSES ==========

@router.get("/cli/limits")
async def get_cli_limits(db: Session = Depends(get_db)):
    """Obtém limites de CLIs por país."""
    try:
        if not HAS_CLI_LIMITS_SERVICE:
            return {
                "status": "service_unavailable",
                "message": "Serviço de limites CLI não disponível",
                "limits": {
                    "usa": 100,
                    "canada": 100,
                    "mexico": 0,
                    "brasil": 0,
                    "colombia": 0,
                    "argentina": 0,
                    "chile": 0,
                    "peru": 0
                },
                "timestamp": datetime.now().isoformat()
            }
        
        cli_service = CliCountryLimitsService(db)
        
        return {
            "status": "success",
            "limits": cli_service.COUNTRY_DAILY_LIMITS,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter limites: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "limits": {},
            "timestamp": datetime.now().isoformat()
        }

@router.post("/cli/limits/{country}")
async def set_cli_limit(country: str, request: CliLimitRequest, db: Session = Depends(get_db)):
    """Define limite de CLI para um país."""
    try:
        if not HAS_CLI_LIMITS_SERVICE:
            return {
                "status": "service_unavailable",
                "message": "Serviço de limites CLI não disponível",
                "country": country,
                "new_limit": request.daily_limit
            }
        
        cli_service = CliCountryLimitsService(db)
        
        # Atualizar limite
        if hasattr(cli_service, 'COUNTRY_DAILY_LIMITS'):
        cli_service.COUNTRY_DAILY_LIMITS[country.lower()] = request.daily_limit
        
        logger.info(f"📊 Limite de CLI atualizado para {country}: {request.daily_limit}")
        
        return {
            "status": "success",
            "country": country,
            "new_limit": request.daily_limit,
            "message": f"Limite atualizado para {country}"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao definir limite: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "country": country,
            "new_limit": request.daily_limit
        }

@router.get("/cli/usage")
async def get_cli_usage(db: Session = Depends(get_db)):
    """Obtém estatísticas de uso de CLIs."""
    try:
        if not HAS_CLI_LIMITS_SERVICE:
            return {
                "status": "service_unavailable",
                "message": "Serviço de estatísticas CLI não disponível",
                "statistics": {
                    "total_clis": 0,
                    "active_clis": 0,
                    "blocked_clis": 0,
                    "countries": {}
                },
                "timestamp": datetime.now().isoformat()
            }
        
        cli_service = CliCountryLimitsService(db)
        stats = cli_service.get_usage_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "statistics": {},
            "timestamp": datetime.now().isoformat()
        }

@router.post("/cli/reset")
async def reset_cli_usage(db: Session = Depends(get_db)):
    """Reseta uso diário de CLIs."""
    try:
        if not HAS_CLI_LIMITS_SERVICE:
            return {
                "status": "service_unavailable",
                "message": "Serviço de limites CLI não disponível",
                "reset_result": None,
                "timestamp": datetime.now().isoformat()
            }
        
        cli_service = CliCountryLimitsService(db)
        
        if hasattr(cli_service, 'reset_daily_usage'):
        result = cli_service.reset_daily_usage()
        else:
            result = {"message": "Método reset_daily_usage não disponível"}
        
        return {
            "status": "success",
            "reset_result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao resetar uso: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "reset_result": None,
            "timestamp": datetime.now().isoformat()
        }

# ========== WEBSOCKET PARA MÉTRICAS EM TEMPO REAL ==========

@router.websocket("/ws/performance")
async def websocket_performance(websocket: WebSocket):
    """WebSocket para métricas de performance em tempo real."""
    await websocket.accept()
    websocket_connections.add(websocket)
    
    try:
        while True:
            # Manter conexão viva
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        websocket_connections.discard(websocket)
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket: {str(e)}")
        websocket_connections.discard(websocket)

# ========== FUNÇÕES AUXILIARES ==========

async def broadcast_metrics_update(metrics):
    """Envia atualização de métricas para todos os WebSockets conectados."""
    if not websocket_connections:
        return
    
    message = {
        "type": "metrics_update",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "current_cps": metrics.current_cps,
            "concurrent_calls": metrics.concurrent_calls,
            "system_load": metrics.system_load,
            "calls_initiated": metrics.calls_initiated,
            "calls_answered": metrics.calls_answered,
            "calls_failed": metrics.calls_failed
        }
    }
    
    # Enviar para todos os WebSockets conectados
    disconnected = set()
    for websocket in websocket_connections:
        try:
            await websocket.send_text(json.dumps(message))
        except:
            disconnected.add(websocket)
    
    # Remover WebSockets desconectados
    websocket_connections.difference_update(disconnected)

async def run_load_test_background(config: LoadTestConfig):
    """Executa teste de carga em background."""
    try:
        if not HAS_LOAD_TEST_SERVICE or not load_test_service:
            logger.warning("⚠️ Load test service não disponível - simulando resultado")
            # Simular resultado para WebSocket
            message = {
                "type": "load_test_completed",
                "timestamp": datetime.now().isoformat(),
                "result": {
                    "test_id": "simulation",
                    "success_rate": 0.0,
                    "actual_cps": 0.0,
                    "total_calls": 0,
                    "message": "Serviço de teste de carga não disponível"
                }
            }
        else:
        result = await load_test_service.run_load_test(config)
        
        # Enviar resultado via WebSocket
        message = {
            "type": "load_test_completed",
            "timestamp": datetime.now().isoformat(),
            "result": {
                "test_id": result.test_id,
                "success_rate": result.success_rate,
                "actual_cps": result.actual_cps,
                "total_calls": result.total_calls_attempted
            }
        }
        
        for websocket in websocket_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except:
                pass
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de carga: {str(e)}")

# ========== ENDPOINTS DE SAÚDE ==========

@router.get("/health")
async def health_check():
    """Verifica saúde do sistema de performance."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "dialer": "active" if dialer_instance and hasattr(dialer_instance, 'is_running') and dialer_instance.is_running else "inactive",
            "load_test": "active" if load_test_service and hasattr(load_test_service, 'is_running') and load_test_service.is_running else "inactive",
            "websocket_connections": len(websocket_connections),
            "high_performance_dialer": HAS_HIGH_PERFORMANCE_DIALER,
            "load_test_service": HAS_LOAD_TEST_SERVICE,
            "cli_limits_service": HAS_CLI_LIMITS_SERVICE,
            "dtmf_config_service": HAS_DTMF_CONFIG_SERVICE
        }
    }

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste para verificar se as rotas estão funcionando."""
    return {
        "status": "working",
        "message": "Performance routes are working correctly",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/performance/health",
            "/performance/test",
            "/performance/metrics/realtime",
            "/performance/metrics/history",
            "/performance/load-test/status",
            "/performance/load-test/results",
            "/performance/cli/limits",
            "/performance/cli/usage",
            "/performance/dtmf/configs"
        ]
    } 

# ========================= CONFIGURAÇÃO DTMF POR PAÍS =========================

@router.get("/dtmf/configs")
async def get_dtmf_configs(db: Session = Depends(get_db)):
    """Obtém todas as configurações DTMF por país."""
    if not HAS_DTMF_CONFIG_SERVICE:
        return {
            "status": "service_unavailable",
            "message": "Serviço DTMF não disponível",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "configs": {
                    "usa": {"connect_key": "1", "dnc_key": "2", "daily_limit": 100},
                    "canada": {"connect_key": "1", "dnc_key": "2", "daily_limit": 100},
                    "mexico": {"connect_key": "3", "dnc_key": "2", "daily_limit": 0},
                    "brasil": {"connect_key": "1", "dnc_key": "2", "daily_limit": 0},
                    "colombia": {"connect_key": "1", "dnc_key": "2", "daily_limit": 0}
                }
            }
        }
    
    try:
        dtmf_service = DTMFCountryConfigService(db)
        configs = dtmf_service.get_all_country_configs()
        
        return {
            "status": "success",
            "message": "Configurações DTMF obtidas",
            "timestamp": datetime.now().isoformat(),
            "data": {"configs": configs}
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Erro ao obter configurações DTMF: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/dtmf/config/{country}")
async def get_dtmf_config_by_country(country: str, db: Session = Depends(get_db)):
    """Obtém configuração DTMF de um país específico."""
    if not HAS_DTMF_CONFIG_SERVICE:
        # Configurações simuladas baseadas na funcionalidade solicitada
        simulate_configs = {
            "mexico": {"connect_key": "3", "dnc_key": "2", "menu_timeout": 12},
            "usa": {"connect_key": "1", "dnc_key": "2", "menu_timeout": 10},
            "canada": {"connect_key": "1", "dnc_key": "2", "menu_timeout": 10}
        }
        
        config = simulate_configs.get(country.lower(), {"connect_key": "1", "dnc_key": "2", "menu_timeout": 10})
        
        return {
            "status": "service_unavailable",
            "message": f"Configuração DTMF simulada para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": {"config": config, "country": country}
        }
    
    try:
        dtmf_service = DTMFCountryConfigService(db)
        config = dtmf_service.get_country_config(country)
        
        return {
            "status": "success",
            "message": f"Configuração DTMF obtida para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": {"config": config, "country": country}
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao obter configuração DTMF para {country}: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.post("/dtmf/config/{country}")
async def update_dtmf_config(
    country: str,
    config_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Atualiza configuração DTMF de um país."""
    if not HAS_DTMF_CONFIG_SERVICE:
        return {
            "status": "service_unavailable",
            "message": "Serviço DTMF não disponível para atualização",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "country": country,
                "received_config": config_data,
                "message": "Configuração recebida mas não pode ser salva"
            }
        }
    
    try:
        dtmf_service = DTMFCountryConfigService(db)
        
        # Validar configuração
        connect_key = config_data.get("connect_key", "1")
        dnc_key = config_data.get("dnc_key", "2")
        
        validation = dtmf_service.validate_key_assignment(country, connect_key, dnc_key)
        
        if not validation["valid"]:
            return {
                "status": "error",
                "message": f"Configuração inválida: {', '.join(validation['errors'])}",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "validation": validation,
                    "suggestions": validation["suggestions"]
                }
            }
        
        # Atualizar configuração
        success = dtmf_service.update_country_config(country, config_data)
        
        if success:
            updated_config = dtmf_service.get_country_config(country)
            return {
                "status": "success",
                "message": f"Configuração DTMF atualizada para {country}",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "country": country,
                    "updated_config": updated_config
                }
            }
        else:
            return {
                "status": "error",
                "message": f"Falha ao atualizar configuração DTMF para {country}",
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao atualizar configuração DTMF: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/dtmf/dialplan/{country}")
async def generate_asterisk_dialplan(country: str, db: Session = Depends(get_db)):
    """Gera dialplan do Asterisk para configuração DTMF de um país."""
    if not HAS_DTMF_CONFIG_SERVICE:
        # Dialplan simulado baseado no país
        dialplan_templates = {
            "mexico": f"""
; Configuração DTMF para México (CONNECT_KEY=3)
[dtmf-mexico]
exten => s,1,NoOp(DTMF Handler for Mexico)
exten => 3,1,NoOp(Connect key pressed)
exten => 3,n,Set(__CALL_RESULT=CONNECT)
exten => 2,1,NoOp(DNC key pressed)
exten => 2,n,Set(__CALL_RESULT=DNC)
""",
            "usa": f"""
; Configuração DTMF para USA (CONNECT_KEY=1)
[dtmf-usa]
exten => s,1,NoOp(DTMF Handler for USA)
exten => 1,1,NoOp(Connect key pressed)
exten => 1,n,Set(__CALL_RESULT=CONNECT)
exten => 2,1,NoOp(DNC key pressed)
exten => 2,n,Set(__CALL_RESULT=DNC)
"""
        }
        
        dialplan = dialplan_templates.get(country.lower(), dialplan_templates["usa"])
        
        return {
            "status": "service_unavailable",
            "message": f"Dialplan simulado para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "country": country,
                "dialplan": dialplan
            }
        }
    
    try:
        dtmf_service = DTMFCountryConfigService(db)
        dialplan = dtmf_service.generate_asterisk_dialplan(country)
        
        return {
            "status": "success",
            "message": f"Dialplan gerado para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "country": country,
                "dialplan": dialplan
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao gerar dialplan: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

# ========================= CALLER ID DINÂMICO =========================

@router.get("/caller-id/next/{country}")
async def get_next_caller_id(
    country: str,
    campaign_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtém próximo Caller ID disponível para um país."""
    if not HAS_DYNAMIC_CALLER_ID_SERVICE:
        # Caller IDs simulados por país
        fallback_clis = {
            "usa": "+14255551000",
            "canada": "+14165551000", 
            "mexico": "+525555551000",
            "brasil": "+551155551000",
            "colombia": "+5715551000",
            "argentina": "+541155551000",
            "chile": "+5625551000",
            "peru": "+5115551000"
        }
        
        cli = fallback_clis.get(country.lower(), "+18885559999")
        
        return {
            "status": "service_unavailable",
            "message": f"Caller ID simulado para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "cli": cli,
                "country": country,
                "campaign_id": campaign_id,
                "source": "fallback_simulation"
            }
        }
    
    try:
        caller_id_service = DynamicCallerIdService(db)
        cli_info = caller_id_service.get_next_cli(country, campaign_id)
        
        return {
            "status": "success",
            "message": f"Caller ID obtido para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": cli_info
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao obter Caller ID: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/caller-id/stats/{country}")
async def get_caller_id_stats(country: str, db: Session = Depends(get_db)):
    """Obtém estatísticas de Caller ID de um país."""
    if not HAS_DYNAMIC_CALLER_ID_SERVICE:
        return {
            "status": "service_unavailable",
            "message": f"Estatísticas simuladas para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "country": country,
                "total_clis": 1000,
                "daily_limit": 100 if country.lower() in ["usa", "canada"] else 0,
                "used_today": 50,
                "available_today": 950 if country.lower() not in ["usa", "canada"] else 50
            }
        }
    
    try:
        caller_id_service = DynamicCallerIdService(db)
        stats = caller_id_service.get_country_cli_stats(country)
        
        return {
            "status": "success",
            "message": f"Estatísticas de Caller ID para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao obter estatísticas: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/caller-id/stats")
async def get_all_caller_id_stats(db: Session = Depends(get_db)):
    """Obtém estatísticas de Caller ID de todos os países."""
    if not HAS_DYNAMIC_CALLER_ID_SERVICE:
        return {
            "status": "service_unavailable",
            "message": "Estatísticas globais simuladas",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "total_countries": 8,
                "restricted_countries": ["usa", "canada"],
                "unrestricted_countries": ["mexico", "brasil", "colombia", "argentina", "chile", "peru"],
                "total_clis": 8000
            }
        }
    
    try:
        caller_id_service = DynamicCallerIdService(db)
        stats = caller_id_service.get_all_countries_stats()
        
        return {
            "status": "success",
            "message": "Estatísticas globais de Caller ID",
            "timestamp": datetime.now().isoformat(),
            "data": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao obter estatísticas globais: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.post("/caller-id/load/{country}")
async def load_caller_id_list(
    country: str,
    cli_data: Dict[str, List[str]],
    db: Session = Depends(get_db)
):
    """Carrega lista personalizada de Caller IDs para um país."""
    if not HAS_DYNAMIC_CALLER_ID_SERVICE:
        cli_list = cli_data.get("cli_list", [])
        return {
            "status": "service_unavailable",
            "message": f"Lista simulada carregada para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "country": country,
                "received_clis": len(cli_list),
                "message": "Lista recebida mas não pode ser salva"
            }
        }
    
    try:
        caller_id_service = DynamicCallerIdService(db)
        cli_list = cli_data.get("cli_list", [])
        
        result = caller_id_service.load_custom_cli_list(country, cli_list)
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao carregar lista de CLIs: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.post("/caller-id/reset/{country}")
async def reset_caller_id_usage(country: str, db: Session = Depends(get_db)):
    """Reset contadores de uso de Caller ID para um país."""
    if not HAS_DYNAMIC_CALLER_ID_SERVICE:
        return {
            "status": "service_unavailable",
            "message": f"Reset simulado para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "country": country,
                "reset_records": 100,
                "message": "Reset simulado executado"
            }
        }
    
    try:
        caller_id_service = DynamicCallerIdService(db)
        result = caller_id_service.reset_daily_usage(country)
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao resetar uso: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

# ========================= LISTA NEGRA/DNC AVANÇADA =========================

@router.post("/dnc/add")
async def add_to_dnc(
    dnc_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Adiciona número à lista DNC."""
    if not HAS_ADVANCED_DNC_SERVICE:
        phone_number = dnc_data.get("phone_number")
        country = dnc_data.get("country")
        return {
            "status": "service_unavailable",
            "message": f"Adição simulada à DNC: {phone_number} ({country})",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "phone_number": phone_number,
                "country": country,
                "action": "simulated_add"
            }
        }
    
    try:
        dnc_service = AdvancedDNCService(db)
        
        phone_number = dnc_data.get("phone_number")
        country = dnc_data.get("country")
        campaign_id = dnc_data.get("campaign_id")
        reason = dnc_data.get("reason", "customer_request")
        
        if not phone_number or not country:
            return {
                "status": "error",
                "message": "phone_number e country são obrigatórios",
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
        
        result = dnc_service.add_to_dnc(phone_number, country, campaign_id, reason)
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao adicionar à DNC: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/dnc/check/{phone_number}/{country}")
async def check_dnc_status(
    phone_number: str,
    country: str,
    campaign_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Verifica se número está na lista DNC."""
    if not HAS_ADVANCED_DNC_SERVICE:
        return {
            "status": "service_unavailable",
            "message": f"Verificação simulada para {phone_number}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "is_dnc": False,
                "phone_number": phone_number,
                "country": country,
                "reason": "Simulation - not in DNC"
            }
        }
    
    try:
        dnc_service = AdvancedDNCService(db)
        result = dnc_service.check_dnc_status(phone_number, country, campaign_id)
        
        return {
            "status": "success",
            "message": f"Status DNC verificado para {phone_number}",
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao verificar DNC: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.delete("/dnc/remove")
async def remove_from_dnc(
    dnc_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Remove número da lista DNC."""
    if not HAS_ADVANCED_DNC_SERVICE:
        phone_number = dnc_data.get("phone_number")
        country = dnc_data.get("country")
        return {
            "status": "service_unavailable",
            "message": f"Remoção simulada da DNC: {phone_number} ({country})",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "phone_number": phone_number,
                "country": country,
                "action": "simulated_remove"
            }
        }
    
    try:
        dnc_service = AdvancedDNCService(db)
        
        phone_number = dnc_data.get("phone_number")
        country = dnc_data.get("country")
        campaign_id = dnc_data.get("campaign_id")
        reason = dnc_data.get("reason", "manual_removal")
        
        if not phone_number or not country:
            return {
                "status": "error",
                "message": "phone_number e country são obrigatórios",
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
        
        result = dnc_service.remove_from_dnc(phone_number, country, campaign_id, reason)
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao remover da DNC: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/dnc/stats")
async def get_dnc_stats(
    country: Optional[str] = None,
    campaign_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtém estatísticas da lista DNC."""
    if not HAS_ADVANCED_DNC_SERVICE:
        return {
            "status": "service_unavailable",
            "message": "Estatísticas DNC simuladas",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "total_entries": 1500,
                "active_entries": 1200,
                "expired_entries": 300,
                "filter_country": country,
                "filter_campaign": campaign_id
            }
        }
    
    try:
        dnc_service = AdvancedDNCService(db)
        stats = dnc_service.get_dnc_stats(country, campaign_id)
        
        return {
            "status": "success",
            "message": "Estatísticas DNC obtidas",
            "timestamp": datetime.now().isoformat(),
            "data": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao obter estatísticas DNC: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.post("/dnc/cleanup")
async def cleanup_expired_dnc(
    cleanup_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Remove entradas DNC expiradas."""
    if not HAS_ADVANCED_DNC_SERVICE:
        country = cleanup_data.get("country")
        return {
            "status": "service_unavailable",
            "message": f"Limpeza simulada para {country or 'todos os países'}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "removed_count": 150,
                "filter_country": country
            }
        }
    
    try:
        dnc_service = AdvancedDNCService(db)
        country = cleanup_data.get("country")
        
        result = dnc_service.cleanup_expired_dnc(country)
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na limpeza DNC: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/dnc/export")
async def export_dnc_list(
    country: Optional[str] = None,
    campaign_id: Optional[str] = None,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """Exporta lista DNC."""
    if not HAS_ADVANCED_DNC_SERVICE:
        return {
            "status": "service_unavailable",
            "message": f"Exportação simulada ({format})",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "format": format,
                "total_entries": 100,
                "filter_country": country,
                "filter_campaign": campaign_id,
                "download_url": f"/simulated-export.{format}"
            }
        }
    
    try:
        dnc_service = AdvancedDNCService(db)
        result = dnc_service.export_dnc_list(country, campaign_id, format)
        
        return {
            "status": "success" if result["success"] else "error",
            "message": f"Exportação DNC concluída ({format})",
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na exportação DNC: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.post("/dnc/import")
async def import_dnc_list(
    import_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Importa lista DNC."""
    if not HAS_ADVANCED_DNC_SERVICE:
        data = import_data.get("data", [])
        country = import_data.get("country")
        return {
            "status": "service_unavailable",
            "message": f"Importação simulada para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "country": country,
                "received_entries": len(data),
                "simulated_imported": len(data),
                "message": "Dados recebidos mas não podem ser salvos"
            }
        }
    
    try:
        dnc_service = AdvancedDNCService(db)
        
        data = import_data.get("data", [])
        country = import_data.get("country")
        campaign_id = import_data.get("campaign_id")
        
        if not data or not country:
            return {
                "status": "error",
                "message": "data e country são obrigatórios",
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
        
        result = dnc_service.import_dnc_list(data, country, campaign_id)
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na importação DNC: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/dnc/audit")
async def get_dnc_audit_log(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtém log de auditoria DNC."""
    if not HAS_ADVANCED_DNC_SERVICE:
        # Log simulado
        simulated_log = [
            {
                "action": "ADD",
                "phone_number": "+5525555551234",
                "country": "mexico",
                "campaign_id": "camp_001",
                "reason": "customer_request",
                "timestamp": datetime.now().isoformat(),
                "user": "system"
            }
        ]
        
        return {
            "status": "service_unavailable",
            "message": "Log de auditoria simulado",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "audit_log": simulated_log,
                "total_entries": len(simulated_log),
                "limit": limit
            }
        }
    
    try:
        dnc_service = AdvancedDNCService(db)
        audit_log = dnc_service.get_audit_log(limit)
        
        return {
            "status": "success",
            "message": "Log de auditoria DNC obtido",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "audit_log": audit_log,
                "total_entries": len(audit_log),
                "limit": limit
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao obter log de auditoria: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

# ========================= CONFIGURAÇÃO INTEGRADA POR PAÍS =========================

@router.get("/country-config/{country}")
async def get_complete_country_config(country: str, db: Session = Depends(get_db)):
    """Obtém configuração completa de um país (DTMF + CLI + DNC)."""
    try:
        config_result = {
            "country": country,
            "timestamp": datetime.now().isoformat()
        }
        
        # Configuração DTMF
        if HAS_DTMF_CONFIG_SERVICE:
            dtmf_service = DTMFCountryConfigService(db)
            config_result["dtmf"] = dtmf_service.get_country_config(country)
        else:
            config_result["dtmf"] = {
                "connect_key": "3" if country.lower() == "mexico" else "1",
                "dnc_key": "2",
                "status": "simulated"
            }
        
        # Estatísticas de CLI
        if HAS_DYNAMIC_CALLER_ID_SERVICE:
            caller_id_service = DynamicCallerIdService(db)
            config_result["caller_id"] = caller_id_service.get_country_cli_stats(country)
        else:
            config_result["caller_id"] = {
                "daily_limit": 100 if country.lower() in ["usa", "canada"] else 0,
                "total_clis": 1000,
                "status": "simulated"
            }
        
        # Estatísticas DNC
        if HAS_ADVANCED_DNC_SERVICE:
            dnc_service = AdvancedDNCService(db)
            config_result["dnc"] = dnc_service.get_dnc_stats(country)
        else:
            config_result["dnc"] = {
                "total_entries": 100,
                "active_entries": 80,
                "status": "simulated"
            }
        
        return {
            "status": "success",
            "message": f"Configuração completa obtida para {country}",
            "timestamp": datetime.now().isoformat(),
            "data": config_result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao obter configuração completa: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        } 

# ========================= CLI LOCAL RANDOMIZATION =========================

@router.post("/cli-local/generate")
async def generate_local_cli(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Gera CLI local baseado no número de destino.
    
    Body:
        destination_number: Número de destino
        custom_pattern: Padrão customizado (opcional)
        country_override: Forçar país específico (opcional)
    """
    try:
        destination_number = request.get("destination_number")
        if not destination_number:
            return {
                "status": "error",
                "message": "destination_number é obrigatório",
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
        
        service = CliLocalRandomizationService(db)
        result = service.generate_local_cli(
            destination_number=destination_number,
            custom_pattern=request.get("custom_pattern"),
            country_override=request.get("country_override")
        )
        
        return {
            "status": "success",
            "message": f"CLI local gerado para {destination_number}",
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar CLI local: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao gerar CLI local: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/cli-local/patterns")
async def get_country_patterns(db: Session = Depends(get_db)):
    """Obtém padrões disponíveis por país para CLI local."""
    try:
        service = CliLocalRandomizationService(db)
        patterns = service.get_country_patterns()
        
        return {
            "status": "success",
            "message": "Padrões de países obtidos",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "countries": patterns,
                "total_countries": len(patterns)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter padrões: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao obter padrões: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/cli-local/stats")
async def get_generation_stats(
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de geração de CLIs locais."""
    try:
        service = CliLocalRandomizationService(db)
        stats = service.get_generation_stats(country)
        
        return {
            "status": "success",
            "message": f"Estatísticas obtidas" + (f" para {country}" if country else ""),
            "timestamp": datetime.now().isoformat(),
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao obter estatísticas: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.post("/cli-local/patterns/create")
async def create_custom_pattern(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Cria padrão customizado de aleatorização CLI.
    
    Body:
        name: Nome do padrão
        pattern_config: Configuração do padrão
    """
    try:
        name = request.get("name")
        pattern_config = request.get("pattern_config")
        
        if not name or not pattern_config:
            return {
                "status": "error",
                "message": "name e pattern_config são obrigatórios",
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
        
        service = CliLocalRandomizationService(db)
        result = service.create_custom_pattern(name, pattern_config)
        
        if result["success"]:
            return {
                "status": "success",
                "message": result["message"],
                "timestamp": datetime.now().isoformat(),
                "data": result["pattern"]
            }
        else:
            return {
                "status": "error",
                "message": result["error"],
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar padrão customizado: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao criar padrão: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.post("/cli-local/bulk-generate")
async def bulk_generate_clis(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Gera CLIs locais em lote para uma lista de números.
    
    Body:
        destination_numbers: Lista de números de destino
        pattern_name: Nome do padrão a usar (opcional)
    """
    try:
        destination_numbers = request.get("destination_numbers", [])
        pattern_name = request.get("pattern_name")
        
        if not destination_numbers:
            return {
                "status": "error",
                "message": "destination_numbers é obrigatório",
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
        
        service = CliLocalRandomizationService(db)
        result = service.bulk_generate_clis(destination_numbers, pattern_name)
        
        return {
            "status": "success",
            "message": f"Processados {result['total_processed']} números",
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na geração em lote: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro na geração em lote: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

@router.get("/cli-local/test/{destination_number}")
async def test_cli_generation(
    destination_number: str,
    country_override: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Testa geração de CLI local para um número específico."""
    try:
        service = CliLocalRandomizationService(db)
        
        # Gerar 5 CLIs diferentes para mostrar variações
        results = []
        for i in range(5):
            result = service.generate_local_cli(
                destination_number=destination_number,
                country_override=country_override
            )
            results.append(result)
        
        return {
            "status": "success",
            "message": f"5 CLIs gerados para teste: {destination_number}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "destination_number": destination_number,
                "country_override": country_override,
                "generated_clis": results,
                "total_generated": len(results)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de geração: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro no teste: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": {}
    } 