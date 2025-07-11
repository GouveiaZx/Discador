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

@router.get("/dtmf/configs")
async def get_dtmf_configs(db: Session = Depends(get_db)):
    """Obtém configurações DTMF por país."""
    try:
        if not HAS_DTMF_CONFIG_SERVICE:
            return {
                "status": "service_unavailable",
                "message": "Serviço de configurações DTMF não disponível",
                "configurations": {
                    "usa": {
                        "connect_key": "1",
                        "disconnect_key": "9",
                        "repeat_key": "0",
                        "menu_timeout": 10,
                        "instructions": "Press 1 to connect"
                    },
                    "canada": {
                        "connect_key": "1",
                        "disconnect_key": "9",
                        "repeat_key": "0",
                        "menu_timeout": 10,
                        "instructions": "Press 1 to connect"
                    },
                    "mexico": {
                        "connect_key": "3",
                        "disconnect_key": "9",
                        "repeat_key": "0",
                        "menu_timeout": 10,
                        "instructions": "Presione 3 para conectar"
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
        
        dtmf_service = DTMFCountryConfigService(db)
        configs = dtmf_service.get_all_country_configs()
        
        return {
            "status": "success",
            "configurations": configs,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter configurações: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "configurations": {},
            "timestamp": datetime.now().isoformat()
        }

@router.post("/dtmf/config/{country}")
async def update_dtmf_config(country: str, request: CountryConfigRequest, db: Session = Depends(get_db)):
    """Atualiza configuração DTMF para um país."""
    try:
        if not HAS_DTMF_CONFIG_SERVICE:
            return {
                "status": "service_unavailable",
                "message": "Serviço de configurações DTMF não disponível",
                "country": country,
                "new_config": None
            }
        
        dtmf_service = DTMFCountryConfigService(db)
        
        new_config = {
            "connect_key": request.connect_key,
            "disconnect_key": request.disconnect_key,
            "repeat_key": request.repeat_key,
            "menu_timeout": request.menu_timeout,
            "instructions": request.instructions
        }
        
        if hasattr(dtmf_service, 'update_country_config'):
            success = dtmf_service.update_country_config(country, new_config)
            
            if success:
                return {
                    "status": "success",
                    "country": country,
                    "new_config": new_config,
                    "message": f"Configuração DTMF atualizada para {country}"
                }
            else:
                return {
                    "status": "not_found",
                    "country": country,
                    "new_config": new_config,
                    "message": f"País {country} não encontrado"
                }
        else:
            return {
                "status": "method_unavailable",
                "country": country,
                "new_config": new_config,
                "message": "Método update_country_config não disponível"
            }
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar configuração: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "country": country,
            "new_config": None
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