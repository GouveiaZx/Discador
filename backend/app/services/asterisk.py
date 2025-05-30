from typing import Dict, Any, Optional
import logging
import asyncio
import uuid
from datetime import datetime

from app.config import configuracion

# Configurar logger
logger = logging.getLogger(__name__)

class AsteriskAMIService:
    """
    Servicio para interactuar con Asterisk Manager Interface (AMI).
    Por ahora, es una implementación simulada.
    """
    def __init__(self):
        self.host = configuracion.ASTERISK_HOST
        self.port = configuracion.ASTERISK_PUERTO
        self.username = configuracion.ASTERISK_USUARIO
        self.password = configuracion.ASTERISK_PASSWORD
        self.conectado = False
        self.event_callbacks = {}  # Callbacks para eventos
        
    async def conectar(self) -> bool:
        """
        Simula una conexión al AMI de Asterisk.
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        # Simulación de conexión
        logger.info(f"Simulando conexión a Asterisk AMI en {self.host}:{self.port}")
        await asyncio.sleep(0.1)  # Pequeña demora para simular latencia
        self.conectado = True
        return True
    
    async def desconectar(self) -> bool:
        """
        Simula una desconexión del AMI de Asterisk.
        
        Returns:
            bool: True si la desconexión fue exitosa
        """
        logger.info("Simulando desconexión de Asterisk AMI")
        await asyncio.sleep(0.05)  # Pequeña demora para simular latencia
        self.conectado = False
        return True
    
    async def originar_llamada(
        self, 
        numero_destino: str, 
        cli: str,
        contexto: str = "salida-campana", 
        extension: str = "s", 
        prioridad: int = 1,
        timeout: int = 30000,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simula la originación de una llamada a través de Asterisk.
        
        Args:
            numero_destino: Número al que se realizará la llamada
            cli: Número que se mostrará como origen de la llamada
            contexto: Contexto del dial plan para la llamada
            extension: Extensión dentro del contexto
            prioridad: Prioridad dentro de la extensión
            timeout: Tiempo máximo de espera en milisegundos
            variables: Variables adicionales para la llamada
            
        Returns:
            Dict: Respuesta simulada de Asterisk
        """
        # Verificar conexión (en una implementación real)
        if not self.conectado:
            await self.conectar()
        
        # Generar un ID único para la llamada
        unique_id = f"SIM-{uuid.uuid4().hex[:12]}"
        
        # Generar un channel simulado
        channel = f"SIP/{numero_destino}-{unique_id[:6]}"
        
        # Logging de la acción
        logger.info(f"Simulando llamada a {numero_destino} con CLI {cli} [ID: {unique_id}]")
        
        # Simular pequeña demora en la respuesta
        await asyncio.sleep(0.2)
        
        # Crear respuesta simulada
        response = {
            "Response": "Success",
            "ActionID": f"action-{uuid.uuid4().hex[:8]}",
            "Message": "Originate successfully queued",
            "Timestamp": datetime.now().isoformat(),
            "UniqueID": unique_id,
            "Channel": channel,
            "Simulation": True
        }
        
        # En una implementación real, aquí se enviaría la acción a Asterisk
        
        return response
    
    async def originar_llamada_presione1(
        self,
        numero_destino: str,
        cli: str,
        audio_url: str,
        timeout_dtmf: int,
        llamada_id: int,
        detectar_voicemail: bool = True,
        mensaje_voicemail_url: Optional[str] = None,
        duracion_maxima_voicemail: int = 30,
        contexto: str = "presione1-campana"
    ) -> Dict[str, Any]:
        """
        Origina una llamada con modo "Presione 1" y detección de voicemail.
        
        Args:
            numero_destino: Número de destino
            cli: CLI a mostrar
            audio_url: URL del arquivo de áudio
            timeout_dtmf: Timeout para aguardar DTMF em segundos
            llamada_id: ID da chamada na base de dados
            detectar_voicemail: Se deve detectar correio de voz
            mensaje_voicemail_url: URL do áudio para voicemail
            duracion_maxima_voicemail: Duração máxima de gravação no voicemail
            contexto: Contexto no dialplan
            
        Returns:
            Dict: Resposta do Asterisk
        """
        if not self.conectado:
            await self.conectar()
        
        # Generar identificadores únicos
        unique_id = f"P1-{uuid.uuid4().hex[:12]}"
        channel = f"SIP/{numero_destino}-{unique_id[:6]}"
        action_id = f"presione1-{uuid.uuid4().hex[:8]}"
        
        # Variables específicas para modo Presione 1 con voicemail
        variables = {
            "LLAMADA_ID": str(llamada_id),
            "AUDIO_URL": audio_url,
            "TIMEOUT_DTMF": str(timeout_dtmf),
            "MODO": "PRESIONE1",
            "DETECTAR_VOICEMAIL": str(detectar_voicemail),
            "VOICEMAIL_AUDIO_URL": mensaje_voicemail_url or "",
            "VOICEMAIL_MAX_DURATION": str(duracion_maxima_voicemail)
        }
        
        logger.info(f"Iniciando chamada Presione 1 com voicemail para {numero_destino} [ID: {llamada_id}]")
        
        # Simular demora da originação
        await asyncio.sleep(0.3)
        
        # Simular fluxo completo em background
        asyncio.create_task(self._simular_flujo_presione1_con_voicemail(
            unique_id, channel, llamada_id, timeout_dtmf, 
            detectar_voicemail, mensaje_voicemail_url, duracion_maxima_voicemail
        ))
        
        response = {
            "Response": "Success",
            "ActionID": action_id,
            "Message": "Presione1 call with voicemail detection originated successfully",
            "Timestamp": datetime.now().isoformat(),
            "UniqueID": unique_id,
            "Channel": channel,
            "LlamadaID": llamada_id,
            "Mode": "PRESIONE1_VOICEMAIL",
            "VoicemailDetection": detectar_voicemail,
            "Simulation": True
        }
        
        return response
    
    async def _simular_flujo_presione1_con_voicemail(
        self,
        unique_id: str,
        channel: str,
        llamada_id: int,
        timeout_dtmf: int,
        detectar_voicemail: bool = True,
        mensaje_voicemail_url: Optional[str] = None,
        duracion_maxima_voicemail: int = 30
    ):
        """
        Simula el flujo completo de una llamada Presione 1 con detección de voicemail.
        """
        try:
            # 1. Simular marcado (3-8 segundos)
            await asyncio.sleep(5)
            
            import random
            
            # 2. Determinar tipo de respuesta
            rand_respuesta = random.random()
            
            if rand_respuesta < 0.15 and detectar_voicemail:
                # 15% chance de caer en voicemail cuando detección está ativa
                await self._simular_voicemail_flow(
                    unique_id, channel, llamada_id, 
                    mensaje_voicemail_url, duracion_maxima_voicemail
                )
                
            elif rand_respuesta < 0.55:  # 40% chance de atender pessoa
                # Atendida por pessoa
                await self._simular_human_answer_flow(
                    unique_id, channel, llamada_id, timeout_dtmf
                )
                
            else:
                # 45% chance de não atender
                await asyncio.sleep(15)  # Simular tentativas
                await self._enviar_evento({
                    "Event": "CallHangup",
                    "UniqueID": unique_id,
                    "Channel": channel,
                    "LlamadaID": llamada_id,
                    "Cause": "19",
                    "CauseTxt": "No Answer",
                    "Timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Erro na simulação Presione 1 com voicemail: {str(e)}")
            # Enviar evento de erro
            await self._enviar_evento({
                "Event": "CallError",
                "UniqueID": unique_id,
                "Channel": channel,
                "LlamadaID": llamada_id,
                "Error": str(e),
                "Timestamp": datetime.now().isoformat()
            })
    
    async def _simular_voicemail_flow(
        self,
        unique_id: str,
        channel: str,
        llamada_id: int,
        mensaje_voicemail_url: Optional[str],
        duracion_maxima_voicemail: int
    ):
        """
        Simula o fluxo quando a chamada cai em correio de voz.
        """
        import random
        
        # Simular tempo até detectar voicemail (baseado em algoritmos reais)
        tempo_detecao = random.uniform(3, 8)
        await asyncio.sleep(tempo_detecao)
        
        # Detectar voicemail
        await self._enviar_evento({
            "Event": "VoicemailDetected",
            "UniqueID": unique_id,
            "Channel": channel,
            "LlamadaID": llamada_id,
            "DetectionMethod": "BeepDetection",  # ou "SilenceDetection", "TonePattern"
            "Timestamp": datetime.now().isoformat()
        })
        
        if mensaje_voicemail_url:
            # Aguardar 1 segundo e começar reprodução da mensagem
            await asyncio.sleep(1)
            
            await self._enviar_evento({
                "Event": "VoicemailAudioStarted",
                "UniqueID": unique_id,
                "Channel": channel,
                "LlamadaID": llamada_id,
                "AudioURL": mensaje_voicemail_url,
                "MaxDuration": duracion_maxima_voicemail,
                "Timestamp": datetime.now().isoformat()
            })
            
            # Simular duração da mensagem (entre 5 segundos e duração máxima)
            duracion_mensagem = random.uniform(5, min(duracion_maxima_voicemail, 25))
            await asyncio.sleep(duracion_mensagem)
            
            await self._enviar_evento({
                "Event": "VoicemailAudioFinished",
                "UniqueID": unique_id,
                "Channel": channel,
                "LlamadaID": llamada_id,
                "AudioDuration": round(duracion_mensagem, 2),
                "Reason": "Completed",  # ou "MaxDurationReached", "Hangup"
                "Timestamp": datetime.now().isoformat()
            })
            
        # Finalizar chamada após deixar mensagem
        await asyncio.sleep(1)
        await self._enviar_evento({
            "Event": "CallHangup",
            "UniqueID": unique_id,
            "Channel": channel,
            "LlamadaID": llamada_id,
            "Cause": "16",
            "CauseTxt": "Normal Clearing - Voicemail message left",
            "Timestamp": datetime.now().isoformat()
        })
    
    async def _simular_human_answer_flow(
        self,
        unique_id: str,
        channel: str,
        llamada_id: int,
        timeout_dtmf: int
    ):
        """
        Simula o fluxo quando uma pessoa atende a chamada.
        """
        import random
        
        # Atendida por pessoa
        await self._enviar_evento({
            "Event": "CallAnswered",
            "UniqueID": unique_id,
            "Channel": channel,
            "LlamadaID": llamada_id,
            "AnswerType": "Human",
            "Timestamp": datetime.now().isoformat()
        })
        
        # Simular início do áudio (1 segundo depois)
        await asyncio.sleep(1)
        await self._enviar_evento({
            "Event": "AudioStarted",
            "UniqueID": unique_id,
            "Channel": channel,
            "LlamadaID": llamada_id,
            "Timestamp": datetime.now().isoformat()
        })
        
        # Simular aguardando DTMF
        await self._enviar_evento({
            "Event": "WaitingDTMF",
            "UniqueID": unique_id,
            "Channel": channel,
            "LlamadaID": llamada_id,
            "Timeout": timeout_dtmf,
            "Timestamp": datetime.now().isoformat()
        })
        
        # Simular resposta DTMF ou timeout
        tempo_resposta = random.uniform(2, timeout_dtmf + 2)
        await asyncio.sleep(tempo_resposta)
        
        if tempo_resposta <= timeout_dtmf:
            # Pressionou alguma tecla (80% chance de ser 1)
            dtmf = "1" if random.random() < 0.8 else random.choice(["2", "3", "0", "*", "#"])
            
            await self._enviar_evento({
                "Event": "DTMFReceived",
                "UniqueID": unique_id,
                "Channel": channel,
                "LlamadaID": llamada_id,
                "DTMF": dtmf,
                "Duration": "100",
                "Timestamp": datetime.now().isoformat()
            })
            
            if dtmf == "1":
                # Simular transferência após 2 segundos
                await asyncio.sleep(2)
                await self._enviar_evento({
                    "Event": "TransferStarted",
                    "UniqueID": unique_id,
                    "Channel": channel,
                    "LlamadaID": llamada_id,
                    "Timestamp": datetime.now().isoformat()
                })
            else:
                # Finalizar chamada - não pressionou 1
                await asyncio.sleep(1)
                await self._enviar_evento({
                    "Event": "CallHangup",
                    "UniqueID": unique_id,
                    "Channel": channel,
                    "LlamadaID": llamada_id,
                    "Cause": "16",
                    "CauseTxt": "Normal Clearing",
                    "Timestamp": datetime.now().isoformat()
                })
        else:
            # Timeout DTMF
            await self._enviar_evento({
                "Event": "DTMFTimeout",
                "UniqueID": unique_id,
                "Channel": channel,
                "LlamadaID": llamada_id,
                "Timestamp": datetime.now().isoformat()
            })
            
            # Finalizar por timeout
            await asyncio.sleep(1)
            await self._enviar_evento({
                "Event": "CallHangup",
                "UniqueID": unique_id,
                "Channel": channel,
                "LlamadaID": llamada_id,
                "Cause": "19",
                "CauseTxt": "No Answer",
                "Timestamp": datetime.now().isoformat()
            })
    
    async def _enviar_evento(self, evento: Dict[str, Any]):
        """
        Simula o envio de eventos do Asterisk.
        Na implementação real, estes eventos viriam via AMI.
        """
        logger.info(f"Evento Asterisk: {evento['Event']} - LlamadaID: {evento.get('LlamadaID')}")
        
        # Chamar callbacks registrados
        for callback in self.event_callbacks.values():
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(evento)
                else:
                    callback(evento)
            except Exception as e:
                logger.error(f"Erro em callback de evento: {str(e)}")
    
    def registrar_callback_evento(self, nome: str, callback):
        """
        Registra callback para processar eventos.
        
        Args:
            nome: Nome identificador do callback
            callback: Função a ser chamada
        """
        self.event_callbacks[nome] = callback
        logger.info(f"Callback '{nome}' registrado para eventos Asterisk")
    
    async def transferir_llamada(self, channel: str, destino: str) -> Dict[str, Any]:
        """
        Transfere uma chamada para destino específico.
        
        Args:
            channel: Channel da chamada
            destino: Extensão ou número de destino
            
        Returns:
            Dict: Resposta da transferência
        """
        logger.info(f"Transferindo {channel} para {destino}")
        
        # Simular demora da transferência
        await asyncio.sleep(0.5)
        
        return {
            "Response": "Success",
            "Message": f"Transfer to {destino} initiated",
            "Channel": channel,
            "Destination": destino,
            "Timestamp": datetime.now().isoformat(),
            "Simulation": True
        }
    
    async def transferir_a_cola(self, channel: str, cola: str) -> Dict[str, Any]:
        """
        Transfere uma chamada para fila de agentes.
        
        Args:
            channel: Channel da chamada
            cola: Nome da fila
            
        Returns:
            Dict: Resposta da transferência
        """
        logger.info(f"Transferindo {channel} para fila {cola}")
        
        # Simular demora da transferência para fila
        await asyncio.sleep(0.8)
        
        return {
            "Response": "Success",
            "Message": f"Transfer to queue {cola} initiated",
            "Channel": channel,
            "Queue": cola,
            "Timestamp": datetime.now().isoformat(),
            "Simulation": True
        }
    
    async def desligar_chamada(self, channel: str, motivo: str = "Normal Clearing") -> Dict[str, Any]:
        """
        Desliga uma chamada específica.
        
        Args:
            channel: Channel da chamada
            motivo: Motivo do desligamento
            
        Returns:
            Dict: Resposta do desligamento
        """
        logger.info(f"Desligando chamada {channel}. Motivo: {motivo}")
        
        await asyncio.sleep(0.2)
        
        return {
            "Response": "Success",
            "Message": "Hangup initiated",
            "Channel": channel,
            "Cause": motivo,
            "Timestamp": datetime.now().isoformat(),
            "Simulation": True
        }

# Crear una instancia del servicio para ser usada por las rutas
asterisk_service = AsteriskAMIService() 