"""Otimizador de performance para consultas de dados do sistema de discador."""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from functools import wraps
import json

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Classe para otimizar performance das consultas de dados."""
    
    def __init__(self):
        self._cache = {}
        self._cache_ttl = {}
        self.default_cache_time = 30  # 30 segundos
        
    def cache_result(self, key: str, ttl: int = None):
        """Decorator para cache de resultados."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = f"{key}:{hash(str(args) + str(kwargs))}"
                
                # Verificar se está no cache e não expirou
                if cache_key in self._cache:
                    cache_time = self._cache_ttl.get(cache_key, 0)
                    if time.time() - cache_time < (ttl or self.default_cache_time):
                        logger.debug(f"Cache hit para {cache_key}")
                        return self._cache[cache_key]
                
                # Executar função e cachear resultado
                result = await func(*args, **kwargs)
                self._cache[cache_key] = result
                self._cache_ttl[cache_key] = time.time()
                logger.debug(f"Cache miss para {cache_key} - resultado cacheado")
                
                return result
            return wrapper
        return decorator
    
    def clear_cache(self, pattern: str = None):
        """Limpa cache por padrão ou completamente."""
        if pattern:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
                del self._cache_ttl[key]
            logger.info(f"Cache limpo para padrão: {pattern}")
        else:
            self._cache.clear()
            self._cache_ttl.clear()
            logger.info("Cache completamente limpo")
    
    def get_optimized_supabase_query(self, table: str, operation: str, **kwargs) -> Dict[str, Any]:
        """Gera consultas otimizadas para Supabase."""
        
        if table == "llamadas_presione1" and operation == "statistics":
            return self._get_optimized_call_statistics_query(**kwargs)
        elif table == "contacts" and operation == "count":
            return self._get_optimized_contact_count_query(**kwargs)
        elif table == "campanas_presione1" and operation == "list":
            return self._get_optimized_campaign_list_query(**kwargs)
        
        return {}
    
    def _get_optimized_call_statistics_query(self, campana_id: int) -> Dict[str, Any]:
        """Consulta otimizada para estatísticas de chamadas."""
        return {
            "select": "estado,fecha_contestada,presiono_1,transferencia_exitosa,voicemail_detectado,motivo_finalizacion,duracion_mensaje_voicemail,tiempo_respuesta_dtmf,duracion_total",
            "filters": {"campana_id": campana_id},
            "order": "created_at.desc",
            "limit": 10000  # Limitar para evitar consultas muito grandes
        }
    
    def _get_optimized_contact_count_query(self, campaign_id: int) -> Dict[str, Any]:
        """Consulta otimizada para contagem de contatos."""
        return {
            "select": "id",
            "filters": {"campaign_id": campaign_id},
            "count": "exact"  # Usar count do Supabase
        }
    
    def _get_optimized_campaign_list_query(self, apenas_ativas: bool = False) -> Dict[str, Any]:
        """Consulta otimizada para listagem de campanhas."""
        query = {
            "select": "id,nombre,descripcion,campaign_id,activa,pausada,fecha_creacion,llamadas_simultaneas",
            "order": "fecha_creacion.desc",
            "limit": 50
        }
        
        if apenas_ativas:
            query["filters"] = {"activa": "eq.true"}
            
        return query

class OptimizedPresione1Service:
    """Versão otimizada do serviço Presione1 com melhor performance."""
    
    def __init__(self, base_service):
        self.base_service = base_service
        self.optimizer = PerformanceOptimizer()
        
    @property
    def _supabase_config(self):
        return self.base_service._supabase_config
    
    def _supabase_request(self, method: str, table: str, data=None, filters=None, select=None, use_count=False) -> Dict[str, Any]:
        """Versão otimizada do _supabase_request com suporte a count."""
        import requests
        
        url = f"{self._supabase_config['url']}/rest/v1/{table}"
        headers = self._supabase_config['headers'].copy()
        
        # Adicionar filtros na URL
        if filters:
            filter_params = []
            for key, value in filters.items():
                if "=" in str(key):
                    filter_params.append(f"{key}")
                else:
                    filter_params.append(f"{key}=eq.{value}")
            if filter_params:
                url += "?" + "&".join(filter_params)
        
        # Adicionar select ou count
        separator = "?" if "?" not in url else "&"
        if use_count:
            url += f"{separator}select=count"
            headers["Prefer"] = "count=exact"
        elif select:
            url += f"{separator}select={select}"
        
        # Configurar headers específicos por método
        if method.upper() in ["PATCH", "PUT", "POST"]:
            headers["Prefer"] = "return=representation"
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            query_time = time.time() - start_time
            if query_time > 1.0:  # Log consultas lentas
                logger.warning(f"Consulta lenta detectada: {method} {table} - {query_time:.2f}s")
            
            if response.status_code not in [200, 201, 204, 206]:
                logger.error(f"Erro Supabase {method} {table}: {response.status_code} - {response.text}")
                return None
            
            if response.status_code == 204:
                return {"success": True}
            
            # Para count, retornar o número do header
            if use_count and "content-range" in response.headers:
                count_info = response.headers["content-range"]
                if "/" in count_info:
                    total = count_info.split("/")[1]
                    return {"count": int(total) if total != "*" else 0}
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Erro de conexão Supabase: {str(e)}")
            return None
    
    async def obter_estadisticas_campana_otimizada(self, campana_id: int) -> Dict[str, Any]:
        """Versão otimizada para obter estatísticas de campanha."""
        try:
            # Cache por 30 segundos
            cache_key = f"stats_campana_{campana_id}"
            
            # Verificar cache
            if cache_key in self.optimizer._cache:
                cache_time = self.optimizer._cache_ttl.get(cache_key, 0)
                if time.time() - cache_time < 30:
                    logger.debug(f"Retornando estatísticas do cache para campanha {campana_id}")
                    return self.optimizer._cache[cache_key]
            
            # Buscar dados da campanha (cache por 5 minutos)
            campana = await self._get_campana_cached(campana_id)
            campaign_id = campana.get("campaign_id")
            
            # Buscar contatos totais usando count otimizado
            total_numeros = 0
            if campaign_id:
                count_result = self._supabase_request(
                    "GET",
                    "contacts",
                    filters={"campaign_id": campaign_id},
                    use_count=True
                )
                total_numeros = count_result.get("count", 0) if count_result else 0
            
            # Buscar llamadas com select otimizado
            llamadas = self._supabase_request(
                "GET",
                "llamadas_presione1",
                filters={"campana_id": campana_id},
                select="estado,fecha_contestada,presiono_1,transferencia_exitosa,voicemail_detectado,motivo_finalizacion,duracion_mensaje_voicemail,tiempo_respuesta_dtmf,duracion_total"
            )
            
            if not llamadas:
                llamadas = []
            
            # Calcular estatísticas de forma otimizada
            stats = self._calculate_statistics_optimized(llamadas)
            
            # Chamadas ativas
            llamadas_activas = 0
            if campana_id in self.base_service.campanhas_ativas:
                llamadas_activas = len(self.base_service.campanhas_ativas[campana_id].get("llamadas_activas", []))
            
            result = {
                "campana_id": campana_id,
                "nombre_campana": campana.get("nombre", "Campanha"),
                "total_numeros": total_numeros,
                "llamadas_pendientes": total_numeros - stats["llamadas_realizadas"],
                "llamadas_activas": llamadas_activas,
                "activa": campana.get("activa", False),
                "pausada": campana.get("pausada", False),
                **stats
            }
            
            # Cachear resultado
            self.optimizer._cache[cache_key] = result
            self.optimizer._cache_ttl[cache_key] = time.time()
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas otimizadas da campanha {campana_id}: {str(e)}")
            return self._get_default_stats(campana_id)
    
    async def _get_campana_cached(self, campana_id: int) -> Dict[str, Any]:
        """Busca campanha com cache de 5 minutos."""
        cache_key = f"campana_{campana_id}"
        
        if cache_key in self.optimizer._cache:
            cache_time = self.optimizer._cache_ttl.get(cache_key, 0)
            if time.time() - cache_time < 300:  # 5 minutos
                return self.optimizer._cache[cache_key]
        
        campana = self.base_service.obter_campana(campana_id)
        
        self.optimizer._cache[cache_key] = campana
        self.optimizer._cache_ttl[cache_key] = time.time()
        
        return campana
    
    def _calculate_statistics_optimized(self, llamadas: List[Dict]) -> Dict[str, Any]:
        """Calcula estatísticas de forma otimizada usando uma única passada."""
        stats = {
            "llamadas_realizadas": len(llamadas),
            "llamadas_contestadas": 0,
            "llamadas_presiono_1": 0,
            "llamadas_no_presiono": 0,
            "llamadas_transferidas": 0,
            "llamadas_error": 0,
            "llamadas_voicemail": 0,
            "llamadas_voicemail_mensaje_dejado": 0,
            "tasa_contestacion": 0.0,
            "tasa_presiono_1": 0.0,
            "tasa_transferencia": 0.0,
            "tasa_voicemail": 0.0,
            "tasa_mensaje_voicemail": 0.0,
            "tiempo_medio_respuesta": None,
            "duracion_media_llamada": None,
            "duracion_media_mensaje_voicemail": None
        }
        
        if not llamadas:
            return stats
        
        # Listas para cálculos de média
        tiempos_respuesta = []
        duraciones_llamada = []
        duraciones_voicemail = []
        
        # Uma única passada pelos dados
        for llamada in llamadas:
            # Contestadas
            if llamada.get("fecha_contestada"):
                stats["llamadas_contestadas"] += 1
                
                # Presiono 1
                if llamada.get("presiono_1") is True:
                    stats["llamadas_presiono_1"] += 1
                elif llamada.get("presiono_1") is False:
                    stats["llamadas_no_presiono"] += 1
            
            # Transferidas
            if llamada.get("transferencia_exitosa") is True:
                stats["llamadas_transferidas"] += 1
            
            # Erro
            if llamada.get("estado") == "error":
                stats["llamadas_error"] += 1
            
            # Voicemail
            if llamada.get("voicemail_detectado") is True:
                stats["llamadas_voicemail"] += 1
                
                if llamada.get("motivo_finalizacion") == "voicemail_mensaje_dejado":
                    stats["llamadas_voicemail_mensaje_dejado"] += 1
                
                # Duração voicemail
                duracion_vm = llamada.get("duracion_mensaje_voicemail")
                if duracion_vm:
                    duraciones_voicemail.append(duracion_vm)
            
            # Tempos de resposta
            tiempo_resp = llamada.get("tiempo_respuesta_dtmf")
            if tiempo_resp:
                tiempos_respuesta.append(tiempo_resp)
            
            # Duração da chamada
            duracion = llamada.get("duracion_total")
            if duracion:
                duraciones_llamada.append(duracion)
        
        # Calcular percentuais
        if stats["llamadas_realizadas"] > 0:
            stats["tasa_contestacion"] = round((stats["llamadas_contestadas"] / stats["llamadas_realizadas"]) * 100, 2)
            stats["tasa_voicemail"] = round((stats["llamadas_voicemail"] / stats["llamadas_realizadas"]) * 100, 2)
        
        if stats["llamadas_contestadas"] > 0:
            stats["tasa_presiono_1"] = round((stats["llamadas_presiono_1"] / stats["llamadas_contestadas"]) * 100, 2)
        
        if stats["llamadas_presiono_1"] > 0:
            stats["tasa_transferencia"] = round((stats["llamadas_transferidas"] / stats["llamadas_presiono_1"]) * 100, 2)
        
        if stats["llamadas_voicemail"] > 0:
            stats["tasa_mensaje_voicemail"] = round((stats["llamadas_voicemail_mensaje_dejado"] / stats["llamadas_voicemail"]) * 100, 2)
        
        # Calcular médias
        if tiempos_respuesta:
            stats["tiempo_medio_respuesta"] = round(sum(tiempos_respuesta) / len(tiempos_respuesta), 2)
        
        if duraciones_llamada:
            stats["duracion_media_llamada"] = round(sum(duraciones_llamada) / len(duraciones_llamada), 2)
        
        if duraciones_voicemail:
            stats["duracion_media_mensaje_voicemail"] = round(sum(duraciones_voicemail) / len(duraciones_voicemail), 2)
        
        return stats
    
    def _get_default_stats(self, campana_id: int) -> Dict[str, Any]:
        """Retorna estatísticas padrão em caso de erro."""
        return {
            "campana_id": campana_id,
            "nombre_campana": "Campanha",
            "total_numeros": 0,
            "llamadas_realizadas": 0,
            "llamadas_pendientes": 0,
            "llamadas_contestadas": 0,
            "llamadas_presiono_1": 0,
            "llamadas_no_presiono": 0,
            "llamadas_transferidas": 0,
            "llamadas_error": 0,
            "llamadas_voicemail": 0,
            "llamadas_voicemail_mensaje_dejado": 0,
            "tasa_voicemail": 0.0,
            "tasa_mensaje_voicemail": 0.0,
            "duracion_media_mensaje_voicemail": None,
            "tasa_contestacion": 0.0,
            "tasa_presiono_1": 0.0,
            "tasa_transferencia": 0.0,
            "tiempo_medio_respuesta": None,
            "duracion_media_llamada": None,
            "activa": False,
            "pausada": False,
            "llamadas_activas": 0
        }
    
    def clear_campaign_cache(self, campana_id: int = None):
        """Limpa cache de uma campanha específica ou todas."""
        if campana_id:
            self.optimizer.clear_cache(f"campana_{campana_id}")
            self.optimizer.clear_cache(f"stats_campana_{campana_id}")
        else:
            self.optimizer.clear_cache("campana_")
            self.optimizer.clear_cache("stats_campana_")
        
        logger.info(f"Cache limpo para campanha {campana_id if campana_id else 'todas'}")

# Instância global do otimizador
performance_optimizer = PerformanceOptimizer()