"""
Schemas para trunks SIP avançados.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class CallerIdConfig(BaseModel):
    """Configuração de Caller ID."""
    numero: str = Field(..., description="Número do Caller ID")
    nome: str = Field(..., description="Nome do Caller ID")


class TrunkBase(BaseModel):
    """Schema base para trunks."""
    
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do trunk")
    descripcion: Optional[str] = Field(None, description="Descrição do trunk")
    
    # Configurações de conexão
    host: str = Field(..., description="Host/IP do trunk")
    porta: int = Field(default=5060, ge=1, le=65535, description="Porta SIP")
    usuario: str = Field(..., description="Usuário SIP")
    senha: str = Field(..., description="Senha SIP")
    
    # Configurações avançadas SIP
    protocolo: str = Field(default='UDP', description="Protocolo SIP")
    codec_preferido: str = Field(default='ulaw', description="Codec preferido")
    codecs_permitidos: List[str] = Field(default=['ulaw', 'alaw', 'g729'], description="Codecs permitidos")
    
    # Configurações de roteamento
    prefixo_discagem: str = Field(default='', description="Prefixo para discagem")
    sufixo_discagem: str = Field(default='', description="Sufixo para discagem")
    codigo_pais: str = Field(default='+1', description="Código do país")
    codigo_area_default: str = Field(default='', description="Código de área padrão")
    
    # Configurações de DV (Dígito Verificador)
    usar_dv: bool = Field(default=True, description="Usar formatação DV")
    formato_dv: str = Field(default='10_digit', description="Formato DV")
    remover_codigo_pais: bool = Field(default=False, description="Remover código do país")
    
    # Configurações de Caller ID
    caller_id_nome: str = Field(default='', description="Nome do Caller ID")
    caller_id_numero: str = Field(default='', description="Número do Caller ID")
    randomizar_caller_id: bool = Field(default=False, description="Randomizar Caller ID")
    pool_caller_ids: List[CallerIdConfig] = Field(default=[], description="Pool de Caller IDs")
    
    # Configurações de capacidade
    max_canais_simultaneos: int = Field(default=10, ge=1, le=1000, description="Máximo de canais simultâneos")
    prioridade: int = Field(default=1, ge=1, le=10, description="Prioridade do trunk")
    peso_balanceamento: int = Field(default=100, ge=1, le=1000, description="Peso para balanceamento")
    
    # Configurações de qualidade
    timeout_conexao: int = Field(default=30, ge=5, le=300, description="Timeout de conexão (segundos)")
    timeout_resposta: int = Field(default=60, ge=10, le=600, description="Timeout de resposta (segundos)")
    max_tentativas: int = Field(default=3, ge=1, le=10, description="Máximo de tentativas")
    intervalo_retry: int = Field(default=60, ge=10, le=3600, description="Intervalo entre tentativas")
    
    # Configurações de detecção
    detectar_busy: bool = Field(default=True, description="Detectar ocupado")
    detectar_no_answer: bool = Field(default=True, description="Detectar não atendimento")
    detectar_congestion: bool = Field(default=True, description="Detectar congestionamento")
    detectar_invalid: bool = Field(default=True, description="Detectar número inválido")
    
    # Configurações de horário de funcionamento
    horario_ativo_inicio: Optional[str] = Field(None, pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    horario_ativo_fim: Optional[str] = Field(None, pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    dias_semana_ativo: List[int] = Field(default=[0,1,2,3,4,5,6], description="Dias da semana ativos")
    timezone: str = Field(default='America/New_York', description="Timezone")
    
    # Configurações de custo
    custo_por_minuto: Decimal = Field(default=0.0, ge=0.0, description="Custo por minuto")
    limite_diario_chamadas: int = Field(default=0, ge=0, description="Limite diário de chamadas")
    limite_mensal_custo: Decimal = Field(default=0.0, ge=0.0, description="Limite mensal de custo")
    
    # Configurações de failover
    trunk_backup_id: Optional[int] = Field(None, description="ID do trunk de backup")
    usar_failover: bool = Field(default=False, description="Usar failover")
    
    # Status
    ativo: bool = Field(default=True, description="Trunk ativo")
    
    @validator('protocolo')
    def validate_protocolo(cls, v):
        """Valida o protocolo SIP."""
        protocolos_validos = ['UDP', 'TCP', 'TLS']
        if v.upper() not in protocolos_validos:
            raise ValueError(f"Protocolo deve ser um de: {protocolos_validos}")
        return v.upper()
    
    @validator('formato_dv')
    def validate_formato_dv(cls, v):
        """Valida o formato DV."""
        formatos_validos = ['10_digit', '11_digit', 'e164']
        if v not in formatos_validos:
            raise ValueError(f"Formato DV deve ser um de: {formatos_validos}")
        return v
    
    @validator('horario_ativo_inicio', 'horario_ativo_fim')
    def validate_horario(cls, v):
        """Valida formato de horário."""
        import re
        if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError("Horário deve estar no formato HH:MM")
        return v
    
    @validator('dias_semana_ativo')
    def validate_dias_semana(cls, v):
        """Valida dias da semana."""
        if not v:
            raise ValueError("Deve ter pelo menos um dia ativo")
        
        for dia in v:
            if dia < 0 or dia > 6:
                raise ValueError("Dias da semana devem estar entre 0 (Domingo) e 6 (Sábado)")
        
        return list(set(v))  # Remove duplicatas


class TrunkCreate(TrunkBase):
    """Schema para criação de trunk."""
    pass


class TrunkUpdate(BaseModel):
    """Schema para atualização de trunk."""
    
    # Tornar todos os campos opcionais para update parcial
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    host: Optional[str] = None
    porta: Optional[int] = Field(None, ge=1, le=65535)
    usuario: Optional[str] = None
    senha: Optional[str] = None
    protocolo: Optional[str] = None
    codec_preferido: Optional[str] = None
    codecs_permitidos: Optional[List[str]] = None
    prefixo_discagem: Optional[str] = None
    sufixo_discagem: Optional[str] = None
    codigo_pais: Optional[str] = None
    codigo_area_default: Optional[str] = None
    usar_dv: Optional[bool] = None
    formato_dv: Optional[str] = None
    remover_codigo_pais: Optional[bool] = None
    caller_id_nome: Optional[str] = None
    caller_id_numero: Optional[str] = None
    randomizar_caller_id: Optional[bool] = None
    pool_caller_ids: Optional[List[CallerIdConfig]] = None
    max_canais_simultaneos: Optional[int] = Field(None, ge=1, le=1000)
    prioridade: Optional[int] = Field(None, ge=1, le=10)
    peso_balanceamento: Optional[int] = Field(None, ge=1, le=1000)
    timeout_conexao: Optional[int] = Field(None, ge=5, le=300)
    timeout_resposta: Optional[int] = Field(None, ge=10, le=600)
    max_tentativas: Optional[int] = Field(None, ge=1, le=10)
    intervalo_retry: Optional[int] = Field(None, ge=10, le=3600)
    detectar_busy: Optional[bool] = None
    detectar_no_answer: Optional[bool] = None
    detectar_congestion: Optional[bool] = None
    detectar_invalid: Optional[bool] = None
    horario_ativo_inicio: Optional[str] = Field(None, pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    horario_ativo_fim: Optional[str] = Field(None, pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    dias_semana_ativo: Optional[List[int]] = None
    timezone: Optional[str] = None
    custo_por_minuto: Optional[Decimal] = Field(None, ge=0.0)
    limite_diario_chamadas: Optional[int] = Field(None, ge=0)
    limite_mensal_custo: Optional[Decimal] = Field(None, ge=0.0)
    trunk_backup_id: Optional[int] = None
    usar_failover: Optional[bool] = None
    ativo: Optional[bool] = None


class TrunkResponse(TrunkBase):
    """Schema para resposta de trunk."""
    
    id: int
    canais_em_uso: int = 0
    status_conexao: str = 'desconhecido'
    ultima_verificacao: Optional[datetime] = None
    total_chamadas_hoje: int = 0
    total_chamadas_mes: int = 0
    usuario_criador_id: Optional[int] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True


class TrunkListResponse(BaseModel):
    """Schema para lista de trunks."""
    
    id: int
    nome: str
    host: str
    porta: int
    protocolo: str
    max_canais_simultaneos: int
    canais_em_uso: int
    status_conexao: str
    ativo: bool
    prioridade: int
    
    class Config:
        from_attributes = True


class TrunkEstatisticaResponse(BaseModel):
    """Schema para estatísticas de trunk."""
    
    id: int
    trunk_id: int
    data_inicio: datetime
    data_fim: datetime
    total_chamadas: int
    chamadas_completadas: int
    chamadas_falhadas: int
    duracao_total_minutos: Decimal
    duracao_media_segundos: Decimal
    taxa_sucesso: Decimal
    taxa_abandono: Decimal
    pico_canais_simultaneos: int
    custo_total: Decimal
    
    class Config:
        from_attributes = True


class TrunkTesteConexao(BaseModel):
    """Schema para teste de conexão do trunk."""
    
    trunk_id: int
    resultado: str  # sucesso, falha, timeout
    tempo_resposta: Optional[Decimal] = None
    codigo_resposta: Optional[str] = None
    mensagem: str
    timestamp: datetime


class TrunkBalanceamento(BaseModel):
    """Schema para configuração de balanceamento."""
    
    algoritmo: str = Field(..., description="Algoritmo de balanceamento")  # round_robin, least_used, weighted
    trunks_ids: List[int] = Field(..., description="IDs dos trunks para balanceamento")
    
    @validator('algoritmo')
    def validate_algoritmo(cls, v):
        """Valida algoritmo de balanceamento."""
        algoritmos_validos = ['round_robin', 'least_used', 'weighted', 'priority']
        if v not in algoritmos_validos:
            raise ValueError(f"Algoritmo deve ser um de: {algoritmos_validos}")
        return v


class NumeroFormatado(BaseModel):
    """Schema para resultado de formatação de número."""
    
    numero_original: str
    numero_formatado: str
    trunk_usado: str
    caller_id: Dict[str, str]
    valido: bool
    motivo_invalido: Optional[str] = None 
