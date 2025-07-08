"""
Schemas para campanhas de discado preditivo con modo "Presione 1".
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class CampanaPresione1Base(BaseModel):
    """Schema base para campanhas Presione 1."""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nome da campanha")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descrição da campanha")
    campaign_id: int = Field(..., description="ID da campanha principal no sistema")
    mensaje_audio_url: str = Field(..., description="URL do arquivo de áudio a reproduzir")
    timeout_presione1: int = Field(10, ge=3, le=60, description="Segundos para aguardar DTMF")
    
    # Configuração de voicemail
    detectar_voicemail: bool = Field(True, description="Se deve detectar correio de voz")
    mensaje_voicemail_url: Optional[str] = Field(None, description="URL do áudio para correio de voz")
    duracion_minima_voicemail: int = Field(3, ge=1, le=10, description="Duração mínima para considerar voicemail (segundos)")
    duracion_maxima_voicemail: int = Field(30, ge=10, le=180, description="Duração máxima de gravação no voicemail (segundos)")
    
    extension_transferencia: Optional[str] = Field(None, description="Extensão para transferir chamadas")
    cola_transferencia: Optional[str] = Field(None, description="Fila de agentes para transferir")
    llamadas_simultaneas: int = Field(1, ge=1, le=10, description="Chamadas simultâneas máximas")
    tiempo_entre_llamadas: int = Field(5, ge=1, le=60, description="Segundos entre chamadas")
    notas: Optional[str] = Field(None, description="Notas adicionais")


class CampanaPresione1Create(CampanaPresione1Base):
    """Schema para criar campanha Presione 1."""
    
    @validator('mensaje_audio_url')
    def validar_audio_url(cls, v):
        """Valida URL do áudio."""
        if not v.strip():
            raise ValueError("URL do áudio é obrigatória")
        
        # Verificar extensões válidas
        extensoes_validas = ['.wav', '.gsm', '.ulaw', '.alaw', '.mp3']
        if not any(v.lower().endswith(ext) for ext in extensoes_validas):
            raise ValueError(f"Formato de áudio inválido. Use: {', '.join(extensoes_validas)}")
        
        return v.strip()
    
    @validator('mensaje_voicemail_url')
    def validar_voicemail_url(cls, v, values):
        """Valida URL do áudio de voicemail se detecção estiver ativa."""
        if values.get('detectar_voicemail', True) and v:
            if not v.strip():
                raise ValueError("URL do áudio de voicemail não pode estar vazia")
            
            # Verificar extensões válidas
            extensoes_validas = ['.wav', '.gsm', '.ulaw', '.alaw', '.mp3']
            if not any(v.lower().endswith(ext) for ext in extensoes_validas):
                raise ValueError(f"Formato de áudio de voicemail inválido. Use: {', '.join(extensoes_validas)}")
            
            return v.strip()
        return v
    
    @validator('timeout_presione1')
    def validar_timeout(cls, v):
        """Valida timeout razoável."""
        if v < 3:
            raise ValueError("Timeout deve ser de pelo menos 3 segundos")
        if v > 60:
            raise ValueError("Timeout não pode exceder 60 segundos")
        return v
    
    @validator('duracion_maxima_voicemail')
    def validar_duracao_voicemail(cls, v, values):
        """Valida que duração máxima seja maior que mínima."""
        duracao_minima = values.get('duracion_minima_voicemail', 3)
        if v <= duracao_minima:
            raise ValueError("Duração máxima deve ser maior que duração mínima")
        return v


class CampanaPresione1Update(BaseModel):
    """Schema para atualizar campanha Presione 1."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    mensaje_audio_url: Optional[str] = Field(None)
    timeout_presione1: Optional[int] = Field(None, ge=3, le=60)
    
    # Configuração de voicemail
    detectar_voicemail: Optional[bool] = Field(None)
    mensaje_voicemail_url: Optional[str] = Field(None)
    duracion_minima_voicemail: Optional[int] = Field(None, ge=1, le=10)
    duracion_maxima_voicemail: Optional[int] = Field(None, ge=10, le=180)
    
    extension_transferencia: Optional[str] = Field(None)
    cola_transferencia: Optional[str] = Field(None)
    llamadas_simultaneas: Optional[int] = Field(None, ge=1, le=10)
    tiempo_entre_llamadas: Optional[int] = Field(None, ge=1, le=60)
    activa: Optional[bool] = Field(None)
    pausada: Optional[bool] = Field(None)
    notas: Optional[str] = Field(None)


class CampanaPresione1Response(CampanaPresione1Base):
    """Schema para resposta de campanha Presione 1."""
    id: int = Field(..., description="ID da campanha")
    activa: bool = Field(..., description="Se a campanha está ativa")
    pausada: bool = Field(..., description="Se a campanha está pausada")
    fecha_creacion: datetime = Field(..., description="Data de criação")
    fecha_actualizacion: datetime = Field(..., description="Data de última atualização")
    
    class Config:
        from_attributes = True


class LlamadaPresione1Base(BaseModel):
    """Schema base para chamadas Presione 1."""
    numero_destino: str = Field(..., description="Número de destino")
    numero_normalizado: str = Field(..., description="Número normalizado")
    cli_utilizado: Optional[str] = Field(None, description="CLI utilizado")


class LlamadaPresione1Response(LlamadaPresione1Base):
    """Schema para resposta de chamada Presione 1."""
    id: int = Field(..., description="ID da chamada")
    campana_id: int = Field(..., description="ID da campanha")
    estado: str = Field(..., description="Estado atual da chamada")
    
    # Timestamps
    fecha_inicio: Optional[datetime] = Field(None, description="Data de início")
    fecha_contestada: Optional[datetime] = Field(None, description="Data de atendimento")
    fecha_audio_inicio: Optional[datetime] = Field(None, description="Data de início do áudio")
    fecha_dtmf_recibido: Optional[datetime] = Field(None, description="Data de recebimento do DTMF")
    fecha_transferencia: Optional[datetime] = Field(None, description="Data de transferência")
    fecha_fin: Optional[datetime] = Field(None, description="Data de finalização")
    
    # Dados de voicemail
    voicemail_detectado: Optional[bool] = Field(None, description="Se foi detectado correio de voz")
    fecha_voicemail_detectado: Optional[datetime] = Field(None, description="Data de detecção do voicemail")
    fecha_voicemail_audio_inicio: Optional[datetime] = Field(None, description="Data de início do áudio no voicemail")
    fecha_voicemail_audio_fin: Optional[datetime] = Field(None, description="Data de fim do áudio no voicemail")
    duracion_mensaje_voicemail: Optional[int] = Field(None, description="Duração da mensagem no voicemail (segundos)")
    
    # Resultados
    presiono_1: Optional[bool] = Field(None, description="Se pressionou a tecla 1")
    dtmf_recibido: Optional[str] = Field(None, description="Tecla pressionada")
    tiempo_respuesta_dtmf: Optional[float] = Field(None, description="Tempo de resposta em segundos")
    transferencia_exitosa: Optional[bool] = Field(None, description="Se a transferência foi exitosa")
    
    # Dados técnicos
    duracion_total: Optional[int] = Field(None, description="Duração total em segundos")
    duracion_audio: Optional[int] = Field(None, description="Duração do áudio em segundos")
    motivo_finalizacion: Optional[str] = Field(None, description="Motivo da finalização")
    
    class Config:
        from_attributes = True


class IniciarCampanaRequest(BaseModel):
    """Schema para iniciar campanha preditiva."""
    usuario_id: Optional[str] = Field(None, description="ID do usuário que inicia")


class PausarCampanaRequest(BaseModel):
    """Schema para pausar/retomar campanha."""
    pausar: bool = Field(..., description="True para pausar, False para retomar")
    motivo: Optional[str] = Field(None, description="Motivo da pausa")


class EstadisticasCampanaResponse(BaseModel):
    """Schema para estatísticas de campanha."""
    campana_id: int = Field(..., description="ID da campanha")
    nombre_campana: str = Field(..., description="Nome da campanha")
    
    # Contadores gerais
    total_numeros: int = Field(..., description="Total de números na lista")
    llamadas_realizadas: int = Field(..., description="Chamadas realizadas")
    llamadas_pendientes: int = Field(..., description="Chamadas pendentes")
    
    # Estados das chamadas
    llamadas_contestadas: int = Field(..., description="Chamadas atendidas")
    llamadas_presiono_1: int = Field(..., description="Chamadas que pressionaram 1")
    llamadas_no_presiono: int = Field(..., description="Chamadas que não pressionaram")
    llamadas_transferidas: int = Field(..., description="Chamadas transferidas")
    llamadas_error: int = Field(..., description="Chamadas com erro")
    
    # Estatísticas de voicemail
    llamadas_voicemail: int = Field(0, description="Chamadas que caíram em voicemail")
    llamadas_voicemail_mensaje_dejado: int = Field(0, description="Chamadas com mensagem deixada no voicemail")
    tasa_voicemail: float = Field(0.0, description="Taxa de detecção de voicemail (%)")
    tasa_mensaje_voicemail: float = Field(0.0, description="Taxa de mensagem deixada no voicemail (%)")
    duracion_media_mensaje_voicemail: Optional[float] = Field(None, description="Duração média das mensagens no voicemail")
    
    # Percentuais
    tasa_contestacion: float = Field(..., description="Taxa de atendimento (%)")
    tasa_presiono_1: float = Field(..., description="Taxa de interesse (%)")
    tasa_transferencia: float = Field(..., description="Taxa de transferência (%)")
    
    # Tempos médios
    tiempo_medio_respuesta: Optional[float] = Field(None, description="Tempo médio de resposta DTMF")
    duracion_media_llamada: Optional[float] = Field(None, description="Duração média das chamadas")
    
    # Estado atual
    activa: bool = Field(..., description="Se a campanha está ativa")
    pausada: bool = Field(..., description="Se a campanha está pausada")
    llamadas_activas: int = Field(..., description="Chamadas ativas no momento")


class MonitorCampanaResponse(BaseModel):
    """Schema para monitoramento em tempo real."""
    campana_id: int = Field(..., description="ID da campanha")
    estado: str = Field(..., description="Estado da campanha")
    llamadas_activas: List[dict] = Field([], description="Chamadas ativas")
    ultimas_llamadas: List[dict] = Field([], description="Últimas chamadas finalizadas")
    proximos_numeros: List[dict] = Field([], description="Próximos números")
    errores_recientes: List[str] = Field([], description="Erros recentes")
    ultima_actividad: datetime = Field(..., description="Última atividade")
    llamadas_simultaneas_actuales: int = Field(0, description="Chamadas simultâneas atuais")
    numeros_pendientes: int = Field(0, description="Números pendentes") 