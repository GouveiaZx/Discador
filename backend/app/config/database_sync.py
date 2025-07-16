"""Configuração de sincronização de banco de dados para o Discador

Este módulo fornece utilitários para melhorar a sincronização entre
o backend e o banco de dados Supabase, incluindo cache, retry e
validação de dados.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from datetime import datetime, timedelta
import json

# Configuração de logging
logger = logging.getLogger(__name__)

class DatabaseSyncConfig:
    """Configurações para sincronização de banco de dados"""
    
    # Timeouts (em segundos)
    DEFAULT_TIMEOUT = 30
    DELETE_TIMEOUT = 45
    BATCH_TIMEOUT = 60
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # segundos
    EXPONENTIAL_BACKOFF = True
    
    # Cache TTL (em segundos)
    CACHE_TTL = 30
    STATS_CACHE_TTL = 10
    
    # Batch sizes
    MAX_BATCH_SIZE = 100
    DELETE_BATCH_SIZE = 50
    
    # Validação
    VALIDATE_RESPONSES = True
    LOG_PERFORMANCE = True

class DatabaseCache:
    """Cache simples para operações de banco de dados"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'clears': 0
        }
    
    def get(self, key: str, ttl: Optional[float] = None) -> Optional[Any]:
        """Obtém um valor do cache"""
        if key not in self._cache:
            self._stats['misses'] += 1
            return None
        
        # Verificar TTL
        if ttl is None:
            ttl = DatabaseSyncConfig.CACHE_TTL
        
        if time.time() - self._timestamps[key] > ttl:
            self.delete(key)
            self._stats['misses'] += 1
            return None
        
        self._stats['hits'] += 1
        return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Define um valor no cache"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
        self._stats['sets'] += 1
    
    def delete(self, key: str) -> None:
        """Remove um valor do cache"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self, pattern: Optional[str] = None) -> None:
        """Limpa o cache"""
        if pattern:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                self.delete(key)
        else:
            self._cache.clear()
            self._timestamps.clear()
        
        self._stats['clears'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            'total_requests': total_requests,
            'hit_rate': f"{hit_rate:.2f}%",
            'cache_size': len(self._cache)
        }

# Instância global do cache
db_cache = DatabaseCache()

def with_retry(max_retries: int = None, delay: float = None, exponential: bool = None):
    """Decorator para retry automático de operações de banco"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            _max_retries = max_retries or DatabaseSyncConfig.MAX_RETRIES
            _delay = delay or DatabaseSyncConfig.RETRY_DELAY
            _exponential = exponential if exponential is not None else DatabaseSyncConfig.EXPONENTIAL_BACKOFF
            
            last_exception = None
            
            for attempt in range(1, _max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == _max_retries:
                        logger.error(f"Operação {func.__name__} falhou após {_max_retries} tentativas: {e}")
                        break
                    
                    wait_time = _delay * (2 ** (attempt - 1)) if _exponential else _delay
                    logger.warning(f"Tentativa {attempt}/{_max_retries} de {func.__name__} falhou: {e}. Tentando novamente em {wait_time}s")
                    
                    await asyncio.sleep(wait_time)
            
            raise last_exception
        
        return wrapper
    return decorator

def with_performance_logging(func: Callable) -> Callable:
    """Decorator para logging de performance"""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not DatabaseSyncConfig.LOG_PERFORMANCE:
            return await func(*args, **kwargs)
        
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"⚡ {func.__name__} executado em {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ {func.__name__} falhou após {duration:.3f}s: {e}")
            raise
    
    return wrapper

def with_cache(cache_key_func: Callable = None, ttl: float = None):
    """Decorator para cache automático"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave do cache
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # Chave padrão baseada no nome da função e argumentos
                cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Tentar obter do cache
            cached_result = db_cache.get(cache_key, ttl)
            if cached_result is not None:
                logger.debug(f"📋 Cache hit para {func.__name__}: {cache_key}")
                return cached_result
            
            # Executar função e cachear resultado
            result = await func(*args, **kwargs)
            db_cache.set(cache_key, result)
            logger.debug(f"💾 Resultado cacheado para {func.__name__}: {cache_key}")
            
            return result
        
        return wrapper
    return decorator

class DatabaseValidator:
    """Validador para operações de banco de dados"""
    
    @staticmethod
    def validate_campaign_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados de campanha"""
        required_fields = ['nombre', 'descripcion']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        # Normalizar dados
        normalized = {
            'nombre': str(data['nombre']).strip(),
            'descripcion': str(data['descripcion']).strip(),
            'activa': bool(data.get('activa', False)),
            'pausada': bool(data.get('pausada', False)),
            'fecha_actualizacion': datetime.utcnow().isoformat()
        }
        
        # Adicionar campos opcionais
        optional_fields = ['mensaje', 'lista_telefonos', 'configuracion']
        for field in optional_fields:
            if field in data:
                normalized[field] = data[field]
        
        return normalized
    
    @staticmethod
    def validate_response(response: Any, operation: str) -> bool:
        """Valida resposta do banco de dados"""
        if not DatabaseSyncConfig.VALIDATE_RESPONSES:
            return True
        
        if response is None:
            logger.warning(f"Resposta nula para operação: {operation}")
            return False
        
        # Validações específicas por tipo de operação
        if operation in ['insert', 'update']:
            if isinstance(response, dict) and 'id' in response:
                return True
            if isinstance(response, list) and len(response) > 0 and 'id' in response[0]:
                return True
            logger.warning(f"Resposta inválida para {operation}: {response}")
            return False
        
        if operation == 'delete':
            # Para delete, qualquer resposta não-nula é válida
            return True
        
        if operation == 'select':
            if isinstance(response, (list, dict)):
                return True
            logger.warning(f"Resposta inválida para {operation}: {response}")
            return False
        
        return True

class DatabaseSyncManager:
    """Gerenciador principal de sincronização de banco de dados"""
    
    def __init__(self):
        self.cache = db_cache
        self.validator = DatabaseValidator()
        self._stats = {
            'operations': 0,
            'errors': 0,
            'cache_hits': 0,
            'retries': 0
        }
    
    def clear_cache(self, pattern: Optional[str] = None) -> None:
        """Limpa o cache"""
        self.cache.clear(pattern)
        logger.info(f"🧹 Cache limpo{f' (padrão: {pattern})' if pattern else ''}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de sincronização"""
        cache_stats = self.cache.get_stats()
        
        return {
            'sync_stats': self._stats,
            'cache_stats': cache_stats,
            'config': {
                'max_retries': DatabaseSyncConfig.MAX_RETRIES,
                'cache_ttl': DatabaseSyncConfig.CACHE_TTL,
                'timeout': DatabaseSyncConfig.DEFAULT_TIMEOUT
            }
        }
    
    def increment_stat(self, stat_name: str) -> None:
        """Incrementa uma estatística"""
        if stat_name in self._stats:
            self._stats[stat_name] += 1

# Instância global do gerenciador
sync_manager = DatabaseSyncManager()

# Utilitários para uso direto
def clear_campaign_cache(campaign_id: Optional[str] = None) -> None:
    """Limpa cache relacionado a campanhas"""
    if campaign_id:
        sync_manager.clear_cache(f"campaign_{campaign_id}")
    else:
        sync_manager.clear_cache("campaign")

def get_sync_stats() -> Dict[str, Any]:
    """Retorna estatísticas de sincronização"""
    return sync_manager.get_stats()

# Decorators prontos para uso
retry_db_operation = with_retry()
log_performance = with_performance_logging
cache_result = with_cache()

# Exemplo de uso combinado
def sync_operation(cache_key_func: Callable = None, ttl: float = None):
    """Decorator que combina retry, cache e logging de performance"""
    def decorator(func: Callable) -> Callable:
        # Aplicar decorators em ordem
        func = with_retry()(func)
        func = with_performance_logging(func)
        func = with_cache(cache_key_func, ttl)(func)
        return func
    return decorator

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger.info("🔄 Módulo de sincronização de banco de dados carregado")