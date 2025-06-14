#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schemas Pydantic para sistema Multi-SIP
Validacao de dados para multiplos provedores VoIP
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ================== ENUMS ==================

class StatusProvedor(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    MANUTENCAO = "manutencao"

class TipoAutenticacao(str, Enum):
    USUARIO_SENHA = "usuario_senha"
    IP_WHITELIST = "ip_whitelist"
    CERTIFICADO = "certificado"

# ================== SCHEMAS BASE ==================

class ProvedorSIPBase(BaseModel):
    """Schema base para provedor SIP"""
    nome: str = Field(..., min_length=1, max_length=100)
    servidor_sip: str = Field(..., min_length=5, max_length=255)
    porta: int = Field(default=5060, ge=1, le=65535)
    tipo_autenticacao: TipoAutenticacao = TipoAutenticacao.USUARIO_SENHA
    usuario_sip: Optional[str] = Field(None, max_length=100)
    senha_sip: Optional[str] = Field(None, max_length=100)
    ips_permitidos: Optional[List[str]] = Field(default_factory=list)
    certificado_path: Optional[str] = Field(None, max_length=500)
    timeout_conexao: int = Field(default=30, ge=1, le=300)
    max_chamadas_simultaneas: int = Field(default=50, ge=1, le=1000)
    prioridade: int = Field(default=100, ge=1, le=1000)
    codec_preferido: str = Field(default="G711", max_length=20)
    codecs_suportados: List[str] = Field(default_factory=lambda: ["G711", "G729"])
    status: StatusProvedor = StatusProvedor.ATIVO
    observacoes: Optional[str] = Field(None, max_length=1000)

    @validator('ips_permitidos')
    def validar_ips(cls, v):
        """Validar formato dos IPs"""
        if v:
            import ipaddress
            for ip in v:
                try:
                    ipaddress.ip_address(ip)
                except ValueError:
                    raise ValueError(f'IP invalido: {ip}')
        return v

class ProvedorSIPCreate(ProvedorSIPBase):
    """Schema para criacao de provedor SIP"""
    pass

class ProvedorSIPResponse(ProvedorSIPBase):
    """Schema de resposta do provedor SIP"""
    id: int
    data_criacao: datetime
    data_atualizacao: datetime
    ultimo_teste: Optional[datetime]
    status_conexao: Optional[str]
    chamadas_ativas: int = 0

    class Config:
        orm_mode = True

# ================== TARIFAS SIP ==================

class TarifaSIPBase(BaseModel):
    """Schema base para tarifa SIP"""
    provedor_id: int = Field(..., gt=0)
    pais_codigo: str = Field(..., min_length=2, max_length=5)
    prefixo: str = Field(..., min_length=1, max_length=10)
    nome_destino: str = Field(..., min_length=1, max_length=100)
    custo_por_minuto: float = Field(..., ge=0.0)
    custo_conexao: float = Field(default=0.0, ge=0.0)
    incremento_faturamento: int = Field(default=60, ge=1, le=3600)
    minutos_minimos: int = Field(default=0, ge=0)
    moeda: str = Field(default="USD", min_length=3, max_length=3)
    data_inicio_vigencia: datetime
    data_fim_vigencia: Optional[datetime] = None
    ativo: bool = Field(default=True)

class TarifaSIPCreate(TarifaSIPBase):
    """Schema para criacao de tarifa SIP"""
    pass

class TarifaSIPResponse(TarifaSIPBase):
    """Schema de resposta da tarifa SIP"""
    id: int
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        orm_mode = True

# ================== CONFIGURACAO MULTI-SIP ==================

class ConfiguracaoMultiSIPBase(BaseModel):
    """Schema base para configuracao Multi-SIP"""
    nome_configuracao: str = Field(..., min_length=1, max_length=100)
    algoritmo_selecao: str = Field(default="menor_custo")
    failover_ativo: bool = Field(default=True)
    balanceamento_carga: bool = Field(default=True)
    peso_custo: float = Field(default=0.6, ge=0.0, le=1.0)
    peso_qualidade: float = Field(default=0.3, ge=0.0, le=1.0)
    peso_disponibilidade: float = Field(default=0.1, ge=0.0, le=1.0)
    timeout_selecao: int = Field(default=5, ge=1, le=60)
    tentativas_maximas: int = Field(default=3, ge=1, le=10)
    blacklist_ativo: bool = Field(default=True)
    ativo: bool = Field(default=True)

    @validator('peso_custo', 'peso_qualidade', 'peso_disponibilidade')
    def validar_soma_pesos(cls, v, values):
        """Validar que a soma dos pesos nao exceda 1.0"""
        pesos = [
            values.get('peso_custo', 0),
            values.get('peso_qualidade', 0),
            v
        ]
        if sum(pesos) > 1.0:
            raise ValueError('Soma dos pesos nao pode exceder 1.0')
        return v

class ConfiguracaoMultiSIPCreate(ConfiguracaoMultiSIPBase):
    """Schema para criacao de configuracao Multi-SIP"""
    pass

class ConfiguracaoMultiSIPResponse(ConfiguracaoMultiSIPBase):
    """Schema de resposta da configuracao Multi-SIP"""
    id: int
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        orm_mode = True

# ================== ESTATISTICAS ==================

class EstatisticasProvedor(BaseModel):
    """Estatisticas de um provedor SIP"""
    provedor_id: int
    nome_provedor: str
    total_chamadas: int = 0
    chamadas_completadas: int = 0
    taxa_sucesso: float = 0.0
    tempo_medio_conexao: float = 0.0
    custo_total: float = 0.0
    ultima_chamada: Optional[datetime] = None
    status_atual: StatusProvedor

class EstatisticasGerais(BaseModel):
    """Estatisticas gerais do sistema Multi-SIP"""
    total_provedores: int
    provedores_ativos: int
    total_chamadas_hoje: int
    taxa_sucesso_geral: float
    custo_total_hoje: float
    provedor_mais_usado: Optional[str]
    estatisticas_por_provedor: List[EstatisticasProvedor] 