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
    class CliPatternGeneratorService:
        def __init__(self, db): 
            pass

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

# ========== ROTAS CLI PATTERN GENERATOR ==========

@router.get("/cli-pattern/countries")
async def get_supported_countries(db: Session = Depends(get_db)):
    """Obtém países suportados pelo gerador de padrões CLI."""
    try:
        if not HAS_CLI_PATTERN_GENERATOR_SERVICE:
            return {
                "countries": [],
                "message": "Serviço de padrões CLI não disponível"
            }
        
        cli_service = CliPatternGeneratorService(db)
        
        if hasattr(cli_service, 'get_supported_countries'):
            countries = cli_service.get_supported_countries()
            return {
                "countries": countries,
                "total": len(countries),
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "countries": [],
            "message": "Método não disponível"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter países: {str(e)}")
        return {
            "countries": [],
            "message": f"Erro: {str(e)}"
        }

@router.get("/cli-pattern/patterns/{country}")
async def get_country_patterns(country: str, db: Session = Depends(get_db)):
    """Obtém padrões disponíveis para um país."""
    try:
        if not HAS_CLI_PATTERN_GENERATOR_SERVICE:
            return {
                "patterns": [],
                "message": "Serviço de padrões CLI não disponível"
            }
        
        cli_service = CliPatternGeneratorService(db)
        
        if hasattr(cli_service, 'get_country_patterns'):
            patterns = cli_service.get_country_patterns(country)
            return {
                "country": country,
                "patterns": patterns,
                "total": len(patterns),
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "patterns": [],
            "message": "Método não disponível"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter padrões: {str(e)}")
        return {
            "patterns": [],
            "message": f"Erro: {str(e)}"
        }

@router.post("/cli-pattern/generate")
async def generate_cli_pattern(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Gera CLI baseado em padrão."""
    try:
        if not HAS_CLI_PATTERN_GENERATOR_SERVICE:
            raise HTTPException(
                status_code=503,
                detail="Serviço de padrões CLI não disponível"
            )
        
        cli_service = CliPatternGeneratorService(db)
        
        # Parâmetros obrigatórios
        destination_number = request.get("destination_number")
        if not destination_number:
            raise HTTPException(
                status_code=400,
                detail="destination_number é obrigatório"
            )
        
        # Parâmetros opcionais
        pattern = request.get("pattern")
        country = request.get("country")
        
        if hasattr(cli_service, 'generate_cli_pattern'):
            result = cli_service.generate_cli_pattern(
                destination_number=destination_number,
                pattern=pattern,
                country=country
            )
            
            return {
                "status": "success",
                "destination_number": destination_number,
                "generated_cli": result.get("cli"),
                "pattern_used": result.get("pattern"),
                "country": result.get("country"),
                "area_code": result.get("area_code"),
                "timestamp": datetime.now().isoformat()
            }
        
        raise HTTPException(
            status_code=503,
            detail="Método de geração não disponível"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar padrão: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar padrão: {str(e)}"
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