"""Configurações de performance para o sistema de discador."""

from typing import Dict, Any

class PerformanceConfig:
    """Configurações centralizadas de performance."""
    
    # Cache TTL (Time To Live) em segundos
    CACHE_TTL = {
        "statistics": 30,          # Estatísticas de campanha
        "campaign_data": 300,      # Dados da campanha
        "contact_count": 60,       # Contagem de contatos
        "call_list": 15,           # Lista de chamadas
        "dashboard_metrics": 20,   # Métricas do dashboard
    }
    
    # Configurações de query otimizada
    QUERY_OPTIMIZATION = {
        "use_select_fields": True,     # Usar campos específicos no SELECT
        "use_count_queries": True,     # Usar queries COUNT otimizadas
        "batch_size": 1000,            # Tamanho do lote para queries grandes
        "enable_query_logging": True,  # Log de queries lentas
        "slow_query_threshold": 2.0,   # Threshold para queries lentas (segundos)
    }
    
    # Campos otimizados para diferentes tipos de consulta
    OPTIMIZED_FIELDS = {
        "statistics_query": [
            "estado",
            "fecha_contestada", 
            "presiono_1",
            "transferencia_exitosa",
            "voicemail_detectado",
            "motivo_finalizacion",
            "duracion_mensaje_voicemail",
            "tiempo_respuesta_dtmf",
            "duracion_total"
        ],
        "basic_call_info": [
            "id",
            "numero_telefono",
            "estado",
            "fecha_inicio",
            "fecha_fin"
        ],
        "campaign_summary": [
            "id",
            "nombre",
            "activa",
            "pausada",
            "created_at"
        ]
    }
    
    # Configurações de dashboard
    DASHBOARD_CONFIG = {
        "auto_refresh_interval": 5000,  # ms
        "max_campaigns_display": 10,    # Máximo de campanhas no dashboard
        "enable_real_time_updates": True,
        "cache_dashboard_data": True,
    }
    
    # Configurações de monitoramento
    MONITORING_CONFIG = {
        "enable_performance_metrics": True,
        "log_slow_operations": True,
        "track_cache_hit_rate": True,
        "alert_on_slow_queries": True,
    }
    
    @classmethod
    def get_cache_ttl(cls, cache_type: str) -> int:
        """Obtém TTL para um tipo específico de cache."""
        return cls.CACHE_TTL.get(cache_type, 30)
    
    @classmethod
    def get_optimized_fields(cls, query_type: str) -> str:
        """Obtém campos otimizados para um tipo de query."""
        fields = cls.OPTIMIZED_FIELDS.get(query_type, ["*"])
        return ",".join(fields) if fields != ["*"] else "*"
    
    @classmethod
    def should_use_count_query(cls) -> bool:
        """Verifica se deve usar queries COUNT otimizadas."""
        return cls.QUERY_OPTIMIZATION.get("use_count_queries", True)
    
    @classmethod
    def get_slow_query_threshold(cls) -> float:
        """Obtém threshold para queries lentas."""
        return cls.QUERY_OPTIMIZATION.get("slow_query_threshold", 2.0)
    
    @classmethod
    def should_log_queries(cls) -> bool:
        """Verifica se deve fazer log de queries."""
        return cls.QUERY_OPTIMIZATION.get("enable_query_logging", True)

# Instância global de configuração
performance_config = PerformanceConfig()