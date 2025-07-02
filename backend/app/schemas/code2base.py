"""
Esquemas Pydantic para o Sistema CODE2BASE Avancado
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums para os schemas
class TipoNumeroEnum(str, Enum):
    MOVIL = "movil"
    FIJO = "fijo"
    ESPECIAL = "especial"

class TipoOperadoraEnum(str, Enum):
    DESCONOCIDA = "desconocida"
    CLARO = "claro"
    MOVISTAR = "movistar"
    PERSONAL = "personal"
    OTROS = "otros"

class TipoReglaEnum(str, Enum):
    GEOGRAFIA = "geografia"
    OPERADORA = "operadora"
    CALIDAD = "calidad"
    TIEMPO = "tiempo"


# ================== ESQUEMAS BASE ==================

class PaisBase(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=5, description="Codigo do pais (ES, FR, etc.)")
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do pais")
    codigo_telefone: str = Field(..., description="Codigo telefonico (+34, +33, etc.)")
    activo: bool = True


class PaisCreate(PaisBase):
    pass


class PaisUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    codigo_telefone: Optional[str] = None
    activo: Optional[bool] = None


class PaisResponse(PaisBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True


# ================== ESTADO ==================

class EstadoBase(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=10, description="Codigo do estado")
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do estado")
    pais_id: int = Field(..., description="ID do pais")
    activo: bool = True


class EstadoCreate(EstadoBase):
    pass


class EstadoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, min_length=1, max_length=10)
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    activo: Optional[bool] = None


class EstadoResponse(EstadoBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    pais: Optional[PaisResponse] = None
    
    class Config:
        from_attributes = True


# ================== CIDADE ==================

class CidadeBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da cidade")
    codigo_postal: Optional[str] = Field(None, max_length=10, description="Codigo postal")
    estado_id: int = Field(..., description="ID do estado")
    activo: bool = True


class CidadeCreate(CidadeBase):
    pass


class CidadeUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    codigo_postal: Optional[str] = Field(None, max_length=10)
    activo: Optional[bool] = None


class CidadeResponse(CidadeBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacao: datetime
    estado: Optional[EstadoResponse] = None
    
    class Config:
        from_attributes = True


# ================== PREFIJO ==================

class PrefijoBase(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=10, description="Codigo do prefixo")
    tipo_numero: TipoNumeroEnum = TipoNumeroEnum.MOVIL
    operadora: Optional[TipoOperadoraEnum] = TipoOperadoraEnum.DESCONOCIDA
    pais_id: int = Field(..., description="ID do pais")
    estado_id: Optional[int] = None
    cidade_id: Optional[int] = None
    descripcion: Optional[str] = None
    activo: bool = True
    prioridad: int = Field(1, ge=1, le=10, description="Prioridade (1=alta, 10=baixa)")

    @validator('codigo')
    def validate_codigo(cls, v):
        if not v.isdigit():
            raise ValueError('O codigo deve conter apenas digitos')
        return v


class PrefijoCreate(PrefijoBase):
    pass


class PrefijoUpdate(BaseModel):
    tipo_numero: Optional[TipoNumeroEnum] = None
    operadora: Optional[TipoOperadoraEnum] = None
    estado_id: Optional[int] = None
    cidade_id: Optional[int] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    prioridad: Optional[int] = Field(None, ge=1, le=10)


class PrefijoResponse(PrefijoBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacao: datetime
    pais: Optional[PaisResponse] = None
    estado: Optional[EstadoResponse] = None
    cidade: Optional[CidadeResponse] = None
    
    class Config:
        from_attributes = True


# ================== CLI GEO ==================

class CliGeoBase(BaseModel):
    numero: str = Field(..., description="Numero CLI")
    cli_id: int = Field(..., description="ID do CLI original")
    prefijo_id: int = Field(..., description="ID do prefixo")
    tipo_numero: TipoNumeroEnum = TipoNumeroEnum.MOVIL
    operadora: Optional[TipoOperadoraEnum] = TipoOperadoraEnum.DESCONOCIDA
    calidad: float = Field(1.0, ge=0.0, le=1.0, description="Qualidade do CLI (0.0 a 1.0)")
    activo: bool = True


class CliGeoCreate(CliGeoBase):
    pass


class CliGeoUpdate(BaseModel):
    prefijo_id: Optional[int] = None
    tipo_numero: Optional[TipoNumeroEnum] = None
    operadora: Optional[TipoOperadoraEnum] = None
    calidad: Optional[float] = Field(None, ge=0.0, le=1.0)
    activo: Optional[bool] = None


class CliGeoResponse(CliGeoBase):
    id: int
    numero_normalizado: str
    veces_usado: int
    ultima_vez_usado: Optional[datetime]
    tasa_exito: float
    fecha_creacion: datetime
    fecha_actualizacao: datetime
    prefijo: Optional[PrefijoResponse] = None
    
    class Config:
        from_attributes = True


# ================== REGLA CLI ==================

class ReglaCliBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da regra")
    descripcion: Optional[str] = None
    tipo_regra: TipoReglaEnum
    condiciones: Dict[str, Any] = Field(..., description="Condicoes da regra em JSON")
    prioridad: int = Field(1, ge=1, le=10, description="Prioridade (1=alta, 10=baixa)")
    peso: float = Field(1.0, ge=0.0, le=10.0, description="Peso na selecao")
    activo: bool = True
    aplica_a_campana: bool = False
    campana_ids: Optional[List[int]] = None


class ReglaCliCreate(ReglaCliBase):
    pass


class ReglaCliUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    condiciones: Optional[Dict[str, Any]] = None
    prioridad: Optional[int] = Field(None, ge=1, le=10)
    peso: Optional[float] = Field(None, ge=0.0, le=10.0)
    activo: Optional[bool] = None
    aplica_a_campana: Optional[bool] = None
    campana_ids: Optional[List[int]] = None


class ReglaCliResponse(ReglaCliBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacao: datetime
    
    class Config:
        from_attributes = True


# ================== ESQUEMAS DE SELECAO ==================

class SeleccionCliRequest(BaseModel):
    numero_destino: str = Field(..., description="Numero de destino")
    campana_id: Optional[int] = None
    tipo_numero_preferido: Optional[TipoNumeroEnum] = None
    operadora_preferida: Optional[TipoOperadoraEnum] = None
    excluir_clis: Optional[List[str]] = Field(None, description="CLIs a excluir da selecao")
    contexto_adicional: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional para selecao")


class CliSeleccionado(BaseModel):
    id: int
    numero: str
    numero_normalizado: str
    prefijo_codigo: str
    tipo_numero: TipoNumeroEnum
    operadora: Optional[TipoOperadoraEnum]
    calidad: float
    tasa_exito: float
    score_seleccion: float
    reglas_aplicadas: List[str]


class SeleccionCliResponse(BaseModel):
    cli_seleccionado: CliSeleccionado
    numero_destino: str
    numero_destino_normalizado: str
    prefijo_destino: Optional[str]
    total_clis_disponibles: int
    tiempo_seleccion_ms: float
    mensaje: str


# ================== ESQUEMAS DE ANALISE ==================

class AnalisisDestinoRequest(BaseModel):
    numero_destino: str = Field(..., description="Numero a analisar")


class AnalisisDestinoResponse(BaseModel):
    numero_normalizado: str
    pais_detectado: Optional[str]
    estado_detectado: Optional[str]
    cidade_detectada: Optional[str]
    prefijo_detectado: Optional[str]
    tipo_numero: Optional[TipoNumeroEnum]
    operadora_detectada: Optional[TipoOperadoraEnum]
    clis_compatibles: List[CliGeoResponse]
    total_clis_compatibles: int


# ================== ESQUEMAS DE ESTATISTICAS ==================

class EstadisticasCli(BaseModel):
    total_clis: int
    clis_ativos: int
    clis_por_tipo: Dict[str, int]
    clis_por_operadora: Dict[str, int]
    clis_por_pais: Dict[str, int]
    tasa_exito_promedio: float


class EstadisticasSeleccion(BaseModel):
    total_selecciones: int
    selecciones_exitosas: int
    tasa_exito_global: float
    prefijos_mas_usados: List[Dict[str, Any]]
    operadoras_mas_exitosas: List[Dict[str, Any]]


class ReporteSistemaResponse(BaseModel):
    estadisticas_cli: EstadisticasCli
    estadisticas_seleccion: EstadisticasSeleccion
    fecha_reporte: datetime


# ================== ESQUEMAS DE IMPORTACAO ==================

class ImportarPrefijosRequest(BaseModel):
    arquivo_csv: str = Field(..., description="Dados CSV em base64 ou conteudo direto")
    formato: str = Field("csv", description="Formato do arquivo")
    sobrescribir: bool = Field(False, description="Sobrescrever dados existentes")


class ImportarPrefijosResponse(BaseModel):
    prefijos_importados: int
    prefijos_actualizados: int
    prefijos_errores: int
    errores: List[str]
    mensaje: str


# ================== CONFIGURACAO DO SISTEMA ==================

class ConfiguracionSistema(BaseModel):
    algoritmo_seleccion: str = Field("weighted_score", description="Algoritmo de selecao")
    peso_geografia: float = Field(0.4, ge=0.0, le=1.0, description="Peso da geografia na selecao")
    peso_calidad: float = Field(0.3, ge=0.0, le=1.0, description="Peso da qualidade na selecao")
    peso_tasa_exito: float = Field(0.2, ge=0.0, le=1.0, description="Peso da taxa de sucesso na selecao")
    peso_uso_reciente: float = Field(0.1, ge=0.0, le=1.0, description="Peso do uso recente na selecao")
    limite_selecciones_por_cli: int = Field(100, ge=1, description="Limite de selecoes por CLI por dia")
    habilitar_fallback: bool = Field(True, description="Habilitar selecao de fallback")
    tiempo_cache_segundos: int = Field(300, ge=0, description="Tempo de cache em segundos")


class ConfiguracionSistemaResponse(ConfiguracionSistema):
    fecha_actualizacion: datetime
    usuario_actualizacion: Optional[str] = None
    
    class Config:
        from_attributes = True


# ================== TESTE DO SISTEMA ==================

class TesteSistemaRequest(BaseModel):
    numero_destino: str
    campana_id: Optional[int] = None
    simulaciones: int = Field(10, ge=1, le=100, description="Numero de simulacoes")


class TesteSistemaResponse(BaseModel):
    numero_destino: str
    total_simulaciones: int
    clis_seleccionados: List[Dict[str, Any]]
    distribucion_por_prefijo: Dict[str, int]
    distribucion_por_operadora: Dict[str, int]
    score_promedio: float
    tiempo_promedio_ms: float
    recomendaciones: List[str] 