#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schemas Pydantic para o sistema de Campanhas Politicas
Validacao e serializacao de dados eleitorais
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, time
from uuid import UUID
import re

from app.models.campanha_politica import (
    TipoEleicao, StatusCampanhaPolitica, TipoLogEleitoral
)

# ================================================
# SCHEMAS BASE
# ================================================

class ConfiguracaoEleitoralBase(BaseModel):
    """Schema base para configuracao eleitoral"""
    pais_codigo: str = Field(..., min_length=2, max_length=5)
    pais_nome: str = Field(..., min_length=2, max_length=100)
    horario_inicio_permitido: str = Field(..., pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    horario_fim_permitido: str = Field(..., pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    dias_semana_permitidos: List[int] = Field(..., min_items=1, max_items=7)
    mensagem_inicial_obrigatoria: str = Field(..., min_length=10, max_length=1000)
    mensagem_opt_out_obrigatoria: str = Field(..., min_length=10, max_length=500)
    retencao_logs_dias: int = Field(default=2555, ge=365, le=3650)
    hash_algorithm: str = Field(default="SHA256")
    usar_criptografia_exportacao: bool = Field(default=True)
    algoritmo_criptografia: str = Field(default="AES256")
    activo: bool = Field(default=True)

    @validator('dias_semana_permitidos')
    def validar_dias_semana(cls, v):
        """Validar dias da semana (0-6)"""
        if not all(0 <= dia <= 6 for dia in v):
            raise ValueError('Dias da semana devem estar entre 0 (segunda) e 6 (domingo)')
        return sorted(list(set(v)))

    @validator('horario_fim_permitido')
    def validar_horario_fim(cls, v, values):
        """Validar que horario fim e apos horario inicio"""
        if 'horario_inicio_permitido' in values:
            inicio = values['horario_inicio_permitido']
            if inicio >= v:
                raise ValueError('Horario fim deve ser posterior ao horario inicio')
        return v

class ConfiguracaoEleitoralCreate(ConfiguracaoEleitoralBase):
    """Schema para criacao de configuracao eleitoral"""
    pass

class ConfiguracaoEleitoralResponse(ConfiguracaoEleitoralBase):
    """Schema de resposta para configuracao eleitoral"""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

# ================================================
# CALENDARIO ELEITORAL
# ================================================

class CalendarioEleitoralBase(BaseModel):
    """Schema base para calendario eleitoral"""
    pais_codigo: str = Field(..., min_length=2, max_length=5)
    estado_codigo: Optional[str] = Field(None, max_length=10)
    tipo_eleicao: TipoEleicao
    nome_eleicao: str = Field(..., min_length=5, max_length=200)
    data_inicio_campanha: datetime
    data_fim_campanha: datetime
    data_eleicao: datetime
    data_inicio_silencio: Optional[datetime] = None
    data_fim_silencio: Optional[datetime] = None
    orgao_responsavel: str = Field(..., min_length=5, max_length=200)
    numero_resolucao: Optional[str] = Field(None, max_length=100)
    url_oficial: Optional[str] = Field(None, max_length=500)
    activo: bool = Field(default=True)

class CalendarioEleitoralCreate(CalendarioEleitoralBase):
    """Schema para criacao de calendario eleitoral"""
    pass

class CalendarioEleitoralResponse(CalendarioEleitoralBase):
    """Schema de resposta para calendario eleitoral"""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

# ================================================
# CAMPANHA POLITICA
# ================================================

class CampanhaPoliticaBase(BaseModel):
    """Schema base para campanha politica"""
    candidato_nome: str = Field(..., min_length=2, max_length=200)
    candidato_numero: Optional[str] = Field(None, max_length=10)
    partido_sigla: str = Field(..., min_length=1, max_length=10)
    partido_nome: str = Field(..., min_length=2, max_length=200)
    cargo_candidatura: str = Field(..., min_length=2, max_length=100)
    configuracao_eleitoral_id: int = Field(..., gt=0)
    calendario_eleitoral_id: int = Field(..., gt=0)
    permitir_opt_out: bool = Field(default=True)
    limite_diario_ligacoes: Optional[int] = Field(None, gt=0)
    limite_total_ligacoes: Optional[int] = Field(None, gt=0)

class CampanhaPoliticaCreate(CampanhaPoliticaBase):
    """Schema para criacao de campanha politica"""
    campanha_base_id: int = Field(..., gt=0)

class CampanhaPoliticaResponse(CampanhaPoliticaBase):
    """Schema de resposta para campanha politica"""
    id: int
    campanha_base_id: int
    status_politica: StatusCampanhaPolitica
    aprovada_por_autoridade: bool
    data_aprovacao: Optional[datetime]
    autoridade_responsavel: Optional[str]
    contador_opt_outs: int
    contador_ligacoes_realizadas: int
    hash_configuracao: str
    uuid_campanha: UUID
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

# ================================================
# LOG ELEITORAL IMUTAVEL
# ================================================

class LogEleitoralCreate(BaseModel):
    """Schema para criacao de log eleitoral"""
    campanha_politica_id: int = Field(..., gt=0)
    numero_destino: str = Field(..., min_length=8, max_length=20)
    numero_cli_usado: str = Field(..., min_length=8, max_length=20)
    timestamp_local: datetime
    timezone_local: str = Field(..., min_length=3, max_length=50)
    tipo_log: TipoLogEleitoral
    descricao_evento: str = Field(..., min_length=5, max_length=1000)
    dentro_horario_legal: bool
    endereco_ip_servidor: str = Field(..., min_length=7, max_length=45)
    versao_sistema: str = Field(..., min_length=3, max_length=20)

class LogEleitoralResponse(BaseModel):
    """Schema de resposta para log eleitoral (SOMENTE LEITURA)"""
    id: int
    uuid_log: UUID
    hash_proprio: str
    campanha_politica_id: int
    numero_destino: str
    numero_cli_usado: str
    timestamp_utc: datetime
    timestamp_local: datetime
    tipo_log: TipoLogEleitoral
    descricao_evento: str
    dentro_horario_legal: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True

# ================================================
# VALIDACOES
# ================================================

class ValidacaoHorarioRequest(BaseModel):
    """Schema para validacao de horario legal"""
    campanha_politica_id: int = Field(..., gt=0)
    timestamp_ligacao: datetime

class ValidacaoHorarioResponse(BaseModel):
    """Resposta da validacao de horario"""
    dentro_horario_legal: bool
    motivo: str
    horario_inicio_permitido: str
    horario_fim_permitido: str 

class CampanaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activa: Optional[bool] = True
    trunk_id: Optional[int] = None
    cps: Optional[int] = 10
    sleep_time: Optional[int] = 1
    wait_time: Optional[str] = "0.5"
    dnc_list_id: Optional[int] = None
    language: Optional[str] = "pt-BR"
    shuffle_contacts: Optional[bool] = True
    allow_multiple_calls_same_number: Optional[bool] = False
    press_2_audio_id: Optional[int] = None
    max_channels: Optional[int] = 10

class CampanaCreate(CampanaBase):
    pass

class CampanaUpdate(CampanaBase):
    pass

class CampanaOut(CampanaBase):
    id: int
    fecha_creacion: Optional[datetime]
    fecha_actualizacion: Optional[datetime]

    class Config:
        from_attributes = True 
