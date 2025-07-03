"""
Schemas para configurações avançadas de discagem.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class ConfiguracaoDiscagemBase(BaseModel):
    """Schema base para configuração de discagem."""
    
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da configuração")
    descripcion: Optional[str] = Field(None, description="Descrição da configuração")
    
    # Configurações de velocidade
    cps_maximo: Decimal = Field(default=1.0, ge=0.1, le=10.0, description="Máximo de chamadas por segundo")
    cps_inicial: Decimal = Field(default=0.5, ge=0.1, le=5.0, description="CPS inicial")
    auto_ajuste_cps: bool = Field(default=True, description="Auto ajustar CPS baseado na performance")
    
    # Configurações de timing
    sleep_time_entre_llamadas: Decimal = Field(default=1.0, ge=0.1, le=10.0, description="Tempo entre chamadas (segundos)")
    wait_time_respuesta: Decimal = Field(default=30.0, ge=5.0, le=120.0, description="Tempo de espera por resposta")
    timeout_marcacion: Decimal = Field(default=60.0, ge=15.0, le=300.0, description="Timeout para marcação")
    
    # Configurações de retry
    max_intentos_por_numero: int = Field(default=3, ge=1, le=10, description="Máximo de tentativas por número")
    intervalo_retry_minutos: int = Field(default=60, ge=15, le=1440, description="Intervalo entre tentativas (minutos)")
    
    # Configurações de detecção
    detectar_contestador: bool = Field(default=True, description="Detectar secretária eletrônica")
    detectar_fax: bool = Field(default=True, description="Detectar fax")
    detectar_tono_ocupado: bool = Field(default=True, description="Detectar tom de ocupado")
    
    # Configurações de horário
    horario_inicio: str = Field(default="08:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Horário de início")
    horario_fin: str = Field(default="20:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Horário de fim")
    dias_semana_activos: List[int] = Field(default=[1,2,3,4,5], description="Dias da semana ativos (0=Domingo)")
    
    # Configurações de trunk/carrier
    balanceamento_trunks: bool = Field(default=True, description="Balancear entre trunks")
    rotacao_cli: bool = Field(default=True, description="Rotacionar CLI")
    
    # Configurações de qualidade
    amd_habilitado: bool = Field(default=True, description="Habilitar detecção de secretária")
    amd_timeout: Decimal = Field(default=3.0, ge=1.0, le=10.0, description="Timeout AMD")
    amd_silence_threshold: int = Field(default=1000, ge=100, le=5000, description="Threshold de silêncio AMD")
    
    # Configurações de compliance
    respetar_dnc: bool = Field(default=True, description="Respeitar DNC")
    respetar_horarios_locales: bool = Field(default=True, description="Respeitar horários locais")
    permitir_manual_override: bool = Field(default=False, description="Permitir override manual")
    
    # Configurações de performance
    max_canales_simultaneos: int = Field(default=10, ge=1, le=100, description="Máximo de canais simultâneos")
    buffer_numeros: int = Field(default=50, ge=10, le=500, description="Buffer de números")
    predictive_ratio: Decimal = Field(default=1.2, ge=1.0, le=3.0, description="Ratio preditivo")
    
    # Status
    activa: bool = Field(default=True, description="Configuração ativa")
    es_default: bool = Field(default=False, description="É configuração padrão")
    
    @validator('dias_semana_activos')
    def validate_dias_semana(cls, v):
        """Valida os dias da semana."""
        if not v:
            raise ValueError("Deve ter pelo menos um dia ativo")
        
        for dia in v:
            if dia < 0 or dia > 6:
                raise ValueError("Dias da semana devem estar entre 0 (Domingo) e 6 (Sábado)")
        
        return list(set(v))  # Remove duplicatas
    
    @validator('horario_fin')
    def validate_horario_fim(cls, v, values):
        """Valida que horário fim seja maior que início."""
        if 'horario_inicio' in values:
            inicio = values['horario_inicio']
            if v <= inicio:
                raise ValueError("Horário de fim deve ser maior que horário de início")
        return v
    
    @validator('cps_inicial')
    def validate_cps_inicial(cls, v, values):
        """Valida que CPS inicial seja menor ou igual ao máximo."""
        if 'cps_maximo' in values:
            if v > values['cps_maximo']:
                raise ValueError("CPS inicial deve ser menor ou igual ao CPS máximo")
        return v


class ConfiguracaoDiscagemCreate(ConfiguracaoDiscagemBase):
    """Schema para criação de configuração."""
    pass


class ConfiguracaoDiscagemUpdate(ConfiguracaoDiscagemBase):
    """Schema para atualização de configuração."""
    
    # Tornar todos os campos opcionais para update parcial
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    cps_maximo: Optional[Decimal] = Field(None, ge=0.1, le=10.0)
    cps_inicial: Optional[Decimal] = Field(None, ge=0.1, le=5.0)
    auto_ajuste_cps: Optional[bool] = None
    sleep_time_entre_llamadas: Optional[Decimal] = Field(None, ge=0.1, le=10.0)
    wait_time_respuesta: Optional[Decimal] = Field(None, ge=5.0, le=120.0)
    timeout_marcacion: Optional[Decimal] = Field(None, ge=15.0, le=300.0)
    max_intentos_por_numero: Optional[int] = Field(None, ge=1, le=10)
    intervalo_retry_minutos: Optional[int] = Field(None, ge=15, le=1440)
    detectar_contestador: Optional[bool] = None
    detectar_fax: Optional[bool] = None
    detectar_tono_ocupado: Optional[bool] = None
    horario_inicio: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    horario_fin: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    dias_semana_activos: Optional[List[int]] = None
    balanceamento_trunks: Optional[bool] = None
    rotacao_cli: Optional[bool] = None
    amd_habilitado: Optional[bool] = None
    amd_timeout: Optional[Decimal] = Field(None, ge=1.0, le=10.0)
    amd_silence_threshold: Optional[int] = Field(None, ge=100, le=5000)
    respetar_dnc: Optional[bool] = None
    respetar_horarios_locales: Optional[bool] = None
    permitir_manual_override: Optional[bool] = None
    max_canales_simultaneos: Optional[int] = Field(None, ge=1, le=100)
    buffer_numeros: Optional[int] = Field(None, ge=10, le=500)
    predictive_ratio: Optional[Decimal] = Field(None, ge=1.0, le=3.0)
    activa: Optional[bool] = None
    es_default: Optional[bool] = None


class ConfiguracaoDiscagemResponse(ConfiguracaoDiscagemBase):
    """Schema para resposta de configuração."""
    
    id: int
    usuario_creador_id: Optional[int] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True


class ConfiguracaoDiscagemListResponse(BaseModel):
    """Schema para lista de configurações."""
    
    id: int
    nome: str
    descripcion: Optional[str] = None
    cps_maximo: Decimal
    max_canales_simultaneos: int
    activa: bool
    es_default: bool
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class CampanhaConfiguracaoOverride(BaseModel):
    """Schema para overrides específicos de campanha."""
    
    campanha_id: int
    configuracao_discagem_id: int
    override_cps: Optional[Decimal] = Field(None, ge=0.1, le=10.0)
    override_horario_inicio: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    override_horario_fin: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    override_max_canales: Optional[int] = Field(None, ge=1, le=100)


class CampanhaConfiguracaoResponse(BaseModel):
    """Schema para resposta de associação campanha-configuração."""
    
    id: int
    campanha_id: int
    configuracao_discagem_id: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    override_cps: Optional[Decimal] = None
    override_horario_inicio: Optional[str] = None
    override_horario_fin: Optional[str] = None
    override_max_canales: Optional[int] = None
    activa: bool
    configuracao_efetiva: Dict[str, Any]
    
    class Config:
        from_attributes = True


class HistoricoConfiguracaoResponse(BaseModel):
    """Schema para resposta de histórico."""
    
    id: int
    configuracao_id: int
    configuracao_snapshot: Dict[str, Any]
    usuario_modificador_id: Optional[int] = None
    motivo_cambio: Optional[str] = None
    llamadas_realizadas: int
    tasa_contacto: Optional[Decimal] = None
    tasa_abandono: Optional[Decimal] = None
    duracion_promedio: Optional[Decimal] = None
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConfiguracaoDiscagemStats(BaseModel):
    """Schema para estatísticas de configuração."""
    
    configuracao_id: int
    nome: str
    periodo_inicio: datetime
    periodo_fim: Optional[datetime] = None
    
    # Estatísticas de uso
    campanhas_ativas: int
    total_llamadas: int
    llamadas_exitosas: int
    tasa_contacto: Decimal
    tasa_abandono: Decimal
    duracion_promedio: Decimal
    
    # Performance
    cps_promedio: Decimal
    canales_promedio: Decimal
    tiempo_respuesta_promedio: Decimal
    
    # Compliance
    violaciones_horario: int
    numeros_dnc_bloqueados: int
    opt_outs_generados: int 
