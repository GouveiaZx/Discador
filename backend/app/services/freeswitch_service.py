"""
Serviço FreeSWITCH para Discado Preditivo
Implementação específica para integração com FreeSWITCH
"""

import asyncio
import logging
import socket
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import uuid
import json
import time

# Configurar logging
logger = logging.getLogger(__name__)

class EstadoLlamada(Enum):
    """Estados das chamadas no FreeSWITCH"""
    INICIANDO = "iniciando"
    MARCANDO = "marcando"
    CONECTANDO = "conectando"
    CONECTADA = "conectada"
    TRANSFERINDO = "transferindo"
    FINALIZADA = "finalizada"
    ERROR = "error"
    OCUPADO = "ocupado"
    NO_RESPONDE = "no_responde"
    CANCELADA = "cancelada"

class TipoEvento(Enum):
    """Tipos de eventos FreeSWITCH"""
    CHANNEL_CREATE = "CHANNEL_CREATE"
    CHANNEL_ANSWER = "CHANNEL_ANSWER"
    CHANNEL_HANGUP = "CHANNEL_HANGUP"
    CHANNEL_BRIDGE = "CHANNEL_BRIDGE"
    DTMF = "DTMF"
    PLAYBACK_START = "PLAYBACK_START"
    PLAYBACK_STOP = "PLAYBACK_STOP"
    RECORD_START = "RECORD_START"
    RECORD_STOP = "RECORD_STOP"

@dataclass
class ConfiguracionFreeSWITCH:
    """Configuração do FreeSWITCH"""
    host: str = "localhost"
    puerto_esl: int = 8021
    password_esl: str = "ClueCon"
    puerto_api: int = 8080
    contexto_discado: str = "discador"
    perfil_sip: str = "external"
    prefijo_cli: str = "discador_"
    directorio_audios: str = "/usr/local/freeswitch/sounds/discador"
    directorio_grabaciones: str = "/usr/local/freeswitch/recordings"
    timeout_conexion: int = 30
    max_canales_simultaneos: int = 100
    calidad_audio: str = "PCMU"  # PCMU, PCMA, G729
    habilitar_ssl: bool = False

@dataclass
class LlamadaFreeSWITCH:
    """Representação de uma chamada FreeSWITCH"""
    uuid: str
    numero_destino: str
    cli: str
    estado: EstadoLlamada
    canal: str
    fecha_inicio: datetime
    fecha_respuesta: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    duracion: float = 0.0
    causa_hangup: Optional[str] = None
    variables: Dict[str, Any] = None
    eventos: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}
        if self.eventos is None:
            self.eventos = []

class FreeSWITCHService:
    """Serviço principal FreeSWITCH"""
    
    def __init__(self, configuracion: Optional[ConfiguracionFreeSWITCH] = None):
        self.configuracion = configuracion or ConfiguracionFreeSWITCH()
        self.conexion_esl = None
        self.llamadas_activas: Dict[str, LlamadaFreeSWITCH] = {}
        self.callbacks_eventos: Dict[TipoEvento, List[Callable]] = {}
        self.canal_activo = True
        self.estadisticas = {
            "llamadas_iniciadas": 0,
            "llamadas_conectadas": 0,
            "llamadas_finalizadas": 0,
            "eventos_procesados": 0,
            "errors": 0
        }
        
        self._inicializar_callbacks()
    
    def _inicializar_callbacks(self):
        """Inicializa callbacks padrão para eventos"""
        for tipo_evento in TipoEvento:
            self.callbacks_eventos[tipo_evento] = []
    
    async def conectar(self) -> bool:
        """Conecta ao FreeSWITCH via ESL"""
        try:
            import socket
            
            logger.info(f"🔌 Conectando ao FreeSWITCH ESL: {self.configuracion.host}:{self.configuracion.puerto_esl}")
            
            # Criar conexão socket
            self.conexion_esl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conexion_esl.settimeout(self.configuracion.timeout_conexion)
            
            # Conectar
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self.conexion_esl.connect, 
                (self.configuracion.host, self.configuracion.puerto_esl)
            )
            
            # Autenticar
            await self._autenticar_esl()
            
            # Subscrever a eventos
            await self._subscrever_eventos()
            
            # Iniciar listener de eventos
            asyncio.create_task(self._listener_eventos())
            
            logger.info("✅ Conectado ao FreeSWITCH ESL com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar FreeSWITCH: {e}")
            return False
    
    async def _autenticar_esl(self):
        """Autentica na conexão ESL"""
        try:
            # Ler mensagem de boas-vindas
            resposta = await self._ler_resposta_esl()
            
            # Enviar comando de autenticação
            comando_auth = f"auth {self.configuracion.password_esl}\n\n"
            await self._enviar_comando_esl(comando_auth)
            
            # Verificar resposta
            resposta_auth = await self._ler_resposta_esl()
            if "Command/Reply-Text: +OK accepted" not in resposta_auth:
                raise Exception(f"Falha na autenticação: {resposta_auth}")
            
            logger.info("✅ Autenticação ESL bem-sucedida")
            
        except Exception as e:
            logger.error(f"❌ Erro na autenticação ESL: {e}")
            raise
    
    async def _subscrever_eventos(self):
        """Subscreve aos eventos necessários"""
        try:
            eventos = [
                "CHANNEL_CREATE",
                "CHANNEL_ANSWER", 
                "CHANNEL_HANGUP",
                "CHANNEL_BRIDGE",
                "DTMF",
                "PLAYBACK_START",
                "PLAYBACK_STOP",
                "RECORD_START",
                "RECORD_STOP"
            ]
            
            for evento in eventos:
                comando = f"event plain {evento}\n\n"
                await self._enviar_comando_esl(comando)
                resposta = await self._ler_resposta_esl()
                
                if "+OK" not in resposta:
                    logger.warning(f"⚠️ Falha ao subscrever evento {evento}: {resposta}")
            
            logger.info(f"✅ Subscrito a {len(eventos)} eventos FreeSWITCH")
            
        except Exception as e:
            logger.error(f"❌ Erro ao subscrever eventos: {e}")
            raise
    
    async def _enviar_comando_esl(self, comando: str) -> bool:
        """Envia comando via ESL"""
        try:
            if self.conexion_esl:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.conexion_esl.send,
                    comando.encode('utf-8')
                )
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar comando ESL: {e}")
            return False
    
    async def _ler_resposta_esl(self) -> str:
        """Lê resposta via ESL"""
        try:
            if self.conexion_esl:
                resposta = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.conexion_esl.recv,
                    4096
                )
                return resposta.decode('utf-8')
            return ""
        except Exception as e:
            logger.error(f"❌ Erro ao ler resposta ESL: {e}")
            return ""
    
    async def _listener_eventos(self):
        """Loop principal para escutar eventos"""
        logger.info("🎧 Iniciando listener de eventos FreeSWITCH")
        
        while self.canal_activo:
            try:
                # Ler evento
                evento_raw = await self._ler_resposta_esl()
                
                if evento_raw:
                    await self._processar_evento(evento_raw)
                    self.estadisticas["eventos_procesados"] += 1
                
                # Pequena pausa para evitar sobrecarga
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"❌ Erro no listener de eventos: {e}")
                self.estadisticas["errors"] += 1
                await asyncio.sleep(1)  # Pausa maior em caso de erro
    
    async def _processar_evento(self, evento_raw: str):
        """Processa evento recebido do FreeSWITCH"""
        try:
            # Parse do evento
            evento = self._parsear_evento(evento_raw)
            
            if not evento:
                return
            
            tipo_evento = evento.get("Event-Name")
            uuid_llamada = evento.get("Unique-ID")
            
            # Processar por tipo de evento
            if tipo_evento == "CHANNEL_CREATE":
                await self._processar_channel_create(evento)
            elif tipo_evento == "CHANNEL_ANSWER":
                await self._processar_channel_answer(evento)
            elif tipo_evento == "CHANNEL_HANGUP":
                await self._processar_channel_hangup(evento)
            elif tipo_evento == "CHANNEL_BRIDGE":
                await self._processar_channel_bridge(evento)
            elif tipo_evento == "DTMF":
                await self._processar_dtmf(evento)
            elif tipo_evento in ["PLAYBACK_START", "PLAYBACK_STOP"]:
                await self._processar_playback(evento)
            elif tipo_evento in ["RECORD_START", "RECORD_STOP"]:
                await self._processar_record(evento)
            
            # Executar callbacks registrados
            if TipoEvento(tipo_evento) in self.callbacks_eventos:
                for callback in self.callbacks_eventos[TipoEvento(tipo_evento)]:
                    try:
                        await callback(evento)
                    except Exception as e:
                        logger.error(f"❌ Erro em callback de evento: {e}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar evento: {e}")
    
    def _parsear_evento(self, evento_raw: str) -> Optional[Dict[str, str]]:
        """Converte evento raw em dicionário"""
        try:
            evento = {}
            linhas = evento_raw.strip().split('\n')
            
            for linha in linhas:
                if ': ' in linha:
                    chave, valor = linha.split(': ', 1)
                    evento[chave] = valor
            
            return evento if evento else None
            
        except Exception as e:
            logger.error(f"❌ Erro ao parsear evento: {e}")
            return None
    
    async def _processar_channel_create(self, evento: Dict[str, str]):
        """Processa criação de canal"""
        try:
            uuid_llamada = evento.get("Unique-ID")
            numero_destino = evento.get("Caller-Destination-Number", "")
            cli = evento.get("Caller-Caller-ID-Number", "")
            canal = evento.get("Channel-Name", "")
            
            # Verificar se é chamada nossa
            if not canal.startswith(self.configuracion.prefijo_cli):
                return
            
            # Criar objeto llamada
            llamada = LlamadaFreeSWITCH(
                uuid=uuid_llamada,
                numero_destino=numero_destino,
                cli=cli,
                estado=EstadoLlamada.INICIANDO,
                canal=canal,
                fecha_inicio=datetime.now()
            )
            
            llamada.eventos.append({
                "tipo": "CHANNEL_CREATE",
                "timestamp": datetime.now().isoformat(),
                "datos": evento
            })
            
            self.llamadas_activas[uuid_llamada] = llamada
            self.estadisticas["llamadas_iniciadas"] += 1
            
            logger.info(f"📞 Chamada criada: {numero_destino} via {canal}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar CHANNEL_CREATE: {e}")
    
    async def _processar_channel_answer(self, evento: Dict[str, str]):
        """Processa resposta de canal"""
        try:
            uuid_llamada = evento.get("Unique-ID")
            
            if uuid_llamada in self.llamadas_activas:
                llamada = self.llamadas_activas[uuid_llamada]
                llamada.estado = EstadoLlamada.CONECTADA
                llamada.fecha_respuesta = datetime.now()
                
                llamada.eventos.append({
                    "tipo": "CHANNEL_ANSWER",
                    "timestamp": datetime.now().isoformat(),
                    "datos": evento
                })
                
                self.estadisticas["llamadas_conectadas"] += 1
                
                logger.info(f"✅ Chamada respondida: {llamada.numero_destino}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar CHANNEL_ANSWER: {e}")
    
    async def _processar_channel_hangup(self, evento: Dict[str, str]):
        """Processa finalização de canal"""
        try:
            uuid_llamada = evento.get("Unique-ID")
            causa_hangup = evento.get("Hangup-Cause", "UNKNOWN")
            
            if uuid_llamada in self.llamadas_activas:
                llamada = self.llamadas_activas[uuid_llamada]
                llamada.estado = EstadoLlamada.FINALIZADA
                llamada.fecha_fin = datetime.now()
                llamada.causa_hangup = causa_hangup
                
                # Calcular duração
                if llamada.fecha_respuesta:
                    duracao = (llamada.fecha_fin - llamada.fecha_respuesta).total_seconds()
                    llamada.duracion = duracao
                
                llamada.eventos.append({
                    "tipo": "CHANNEL_HANGUP",
                    "timestamp": datetime.now().isoformat(),
                    "datos": evento
                })
                
                self.estadisticas["llamadas_finalizadas"] += 1
                
                logger.info(f"📴 Chamada finalizada: {llamada.numero_destino} - Causa: {causa_hangup}")
                
                # Remover das chamadas ativas após um tempo
                asyncio.create_task(self._limpar_llamada_finalizada(uuid_llamada))
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar CHANNEL_HANGUP: {e}")
    
    async def _processar_channel_bridge(self, evento: Dict[str, str]):
        """Processa bridge entre canais"""
        try:
            uuid_llamada = evento.get("Unique-ID")
            bridge_uuid = evento.get("Bridge-B-Unique-ID")
            
            if uuid_llamada in self.llamadas_activas:
                llamada = self.llamadas_activas[uuid_llamada]
                llamada.estado = EstadoLlamada.TRANSFERINDO
                llamada.variables["bridge_uuid"] = bridge_uuid
                
                llamada.eventos.append({
                    "tipo": "CHANNEL_BRIDGE",
                    "timestamp": datetime.now().isoformat(),
                    "datos": evento
                })
                
                logger.info(f"🔗 Chamada em bridge: {llamada.numero_destino}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar CHANNEL_BRIDGE: {e}")
    
    async def _processar_dtmf(self, evento: Dict[str, str]):
        """Processa evento DTMF"""
        try:
            uuid_llamada = evento.get("Unique-ID")
            dtmf_digit = evento.get("DTMF-Digit")
            
            if uuid_llamada in self.llamadas_activas:
                llamada = self.llamadas_activas[uuid_llamada]
                
                if "dtmf_digits" not in llamada.variables:
                    llamada.variables["dtmf_digits"] = ""
                
                llamada.variables["dtmf_digits"] += dtmf_digit
                
                llamada.eventos.append({
                    "tipo": "DTMF",
                    "timestamp": datetime.now().isoformat(),
                    "digit": dtmf_digit,
                    "datos": evento
                })
                
                logger.info(f"🔢 DTMF detectado: {dtmf_digit} em {llamada.numero_destino}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar DTMF: {e}")
    
    async def _processar_playback(self, evento: Dict[str, str]):
        """Processa eventos de reprodução de áudio"""
        try:
            uuid_llamada = evento.get("Unique-ID")
            playback_file = evento.get("Playback-File-Path", "")
            
            if uuid_llamada in self.llamadas_activas:
                llamada = self.llamadas_activas[uuid_llamada]
                
                llamada.eventos.append({
                    "tipo": evento.get("Event-Name"),
                    "timestamp": datetime.now().isoformat(),
                    "archivo": playback_file,
                    "datos": evento
                })
                
                logger.info(f"🎵 Playback {evento.get('Event-Name')}: {playback_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar PLAYBACK: {e}")
    
    async def _processar_record(self, evento: Dict[str, str]):
        """Processa eventos de gravação"""
        try:
            uuid_llamada = evento.get("Unique-ID")
            record_file = evento.get("Record-File-Path", "")
            
            if uuid_llamada in self.llamadas_activas:
                llamada = self.llamadas_activas[uuid_llamada]
                
                llamada.eventos.append({
                    "tipo": evento.get("Event-Name"),
                    "timestamp": datetime.now().isoformat(),
                    "archivo": record_file,
                    "datos": evento
                })
                
                logger.info(f"🎙️ Record {evento.get('Event-Name')}: {record_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar RECORD: {e}")
    
    async def _limpar_llamada_finalizada(self, uuid_llamada: str):
        """Remove chamada finalizada após delay"""
        await asyncio.sleep(300)  # 5 minutos
        if uuid_llamada in self.llamadas_activas:
            del self.llamadas_activas[uuid_llamada]
    
    async def iniciar_llamada(self, numero_destino: str, cli: str, contexto: Optional[str] = None) -> Optional[str]:
        """Inicia nova chamada"""
        try:
            contexto = contexto or self.configuracion.contexto_discado
            uuid_llamada = str(uuid.uuid4())
            
            # Normalizar número de destino
            numero_destino = self._normalizar_numero(numero_destino)
            
            # Construir comando de originate
            comando = (
                f"bgapi originate "
                f"{{origination_uuid={uuid_llamada},"
                f"origination_caller_id_number={cli},"
                f"origination_caller_id_name=Discador}} "
                f"sofia/{self.configuracion.perfil_sip}/{numero_destino} "
                f"&park\n\n"
            )
            
            # Enviar comando
            if await self._enviar_comando_esl(comando):
                logger.info(f"📞 Chamada iniciada: {numero_destino} com CLI {cli}")
                return uuid_llamada
            else:
                logger.error(f"❌ Falha ao iniciar chamada: {numero_destino}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar chamada: {e}")
            return None
    
    async def finalizar_llamada(self, uuid_llamada: str, causa: str = "MANAGER_REQUEST") -> bool:
        """Finaliza chamada específica"""
        try:
            comando = f"bgapi uuid_kill {uuid_llamada} {causa}\n\n"
            
            if await self._enviar_comando_esl(comando):
                logger.info(f"📴 Chamada finalizada: {uuid_llamada}")
                return True
            else:
                logger.error(f"❌ Falha ao finalizar chamada: {uuid_llamada}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao finalizar chamada: {e}")
            return False
    
    async def transferir_llamada(self, uuid_llamada: str, destino: str) -> bool:
        """Transfere chamada para destino"""
        try:
            comando = f"bgapi uuid_transfer {uuid_llamada} {destino}\n\n"
            
            if await self._enviar_comando_esl(comando):
                logger.info(f"🔄 Chamada transferida: {uuid_llamada} -> {destino}")
                return True
            else:
                logger.error(f"❌ Falha ao transferir chamada: {uuid_llamada}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao transferir chamada: {e}")
            return False
    
    async def reproduzir_audio(self, uuid_llamada: str, arquivo_audio: str) -> bool:
        """Reproduz áudio em chamada"""
        try:
            comando = f"bgapi uuid_broadcast {uuid_llamada} {arquivo_audio}\n\n"
            
            if await self._enviar_comando_esl(comando):
                logger.info(f"🎵 Áudio reproduzido: {arquivo_audio} em {uuid_llamada}")
                return True
            else:
                logger.error(f"❌ Falha ao reproduzir áudio: {arquivo_audio}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao reproduzir áudio: {e}")
            return False
    
    async def iniciar_gravacao(self, uuid_llamada: str, arquivo_gravacao: str) -> bool:
        """Inicia gravação de chamada"""
        try:
            comando = f"bgapi uuid_record {uuid_llamada} start {arquivo_gravacao}\n\n"
            
            if await self._enviar_comando_esl(comando):
                logger.info(f"🎙️ Gravação iniciada: {arquivo_gravacao}")
                return True
            else:
                logger.error(f"❌ Falha ao iniciar gravação: {arquivo_gravacao}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar gravação: {e}")
            return False
    
    async def parar_gravacao(self, uuid_llamada: str) -> bool:
        """Para gravação de chamada"""
        try:
            comando = f"bgapi uuid_record {uuid_llamada} stop\n\n"
            
            if await self._enviar_comando_esl(comando):
                logger.info(f"⏹️ Gravação parada: {uuid_llamada}")
                return True
            else:
                logger.error(f"❌ Falha ao parar gravação: {uuid_llamada}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao parar gravação: {e}")
            return False
    
    def _normalizar_numero(self, numero: str) -> str:
        """Normaliza número para formato FreeSWITCH"""
        # Remover caracteres não numéricos exceto +
        numero_limpo = ''.join(c for c in numero if c.isdigit() or c == '+')
        
        # Adicionar prefixos se necessário
        if numero_limpo.startswith('+'):
            numero_limpo = numero_limpo[1:]
        
        return numero_limpo
    
    def obter_llamadas_activas(self) -> List[Dict[str, Any]]:
        """Obtém lista de chamadas ativas"""
        llamadas = []
        
        for uuid_llamada, llamada in self.llamadas_activas.items():
            llamadas.append({
                "uuid": llamada.uuid,
                "numero_destino": llamada.numero_destino,
                "cli": llamada.cli,
                "estado": llamada.estado.value,
                "canal": llamada.canal,
                "fecha_inicio": llamada.fecha_inicio.isoformat(),
                "fecha_respuesta": llamada.fecha_respuesta.isoformat() if llamada.fecha_respuesta else None,
                "duracion": llamada.duracion,
                "variables": llamada.variables,
                "total_eventos": len(llamada.eventos)
            })
        
        return llamadas
    
    def obter_estadisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do serviço"""
        return {
            **self.estadisticas,
            "llamadas_activas": len(self.llamadas_activas),
            "timestamp": datetime.now().isoformat(),
            "configuracion": {
                "host": self.configuracion.host,
                "puerto_esl": self.configuracion.puerto_esl,
                "contexto": self.configuracion.contexto_discado,
                "max_canales": self.configuracion.max_canales_simultaneos
            }
        }
    
    def registrar_callback_evento(self, tipo_evento: TipoEvento, callback: Callable):
        """Registra callback para tipo de evento"""
        if tipo_evento in self.callbacks_eventos:
            self.callbacks_eventos[tipo_evento].append(callback)
    
    async def desconectar(self):
        """Desconecta do FreeSWITCH"""
        try:
            self.canal_activo = False
            
            if self.conexion_esl:
                await self._enviar_comando_esl("exit\n\n")
                self.conexion_esl.close()
                self.conexion_esl = None
            
            logger.info("✅ Desconectado do FreeSWITCH")
            
        except Exception as e:
            logger.error(f"❌ Erro ao desconectar FreeSWITCH: {e}")

# Instância global do serviço
freeswitch_service = FreeSWITCHService() 