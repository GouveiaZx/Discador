#!/usr/bin/env python3
"""
Asterisk Manager Interface (AMI) - Sistema de Discado Real
Implementação completa para controle do Asterisk
"""

import asyncio
import socket
import time
import uuid
import json
import logging
import os
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CallStatus(Enum):
    """Status de chamadas"""
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    BUSY = "busy"
    FAILED = "failed"
    HANGUP = "hangup"
    NO_ANSWER = "no_answer"
    CONGESTION = "congestion"

@dataclass
class CallEvent:
    """Evento de chamada"""
    call_id: str
    phone_number: str
    campaign_id: int
    status: CallStatus
    timestamp: float
    duration: int = 0
    hangup_cause: str = ""
    dtmf_pressed: str = ""
    transferred: bool = False

class AsteriskAMI:
    """
    Classe principal para integração com Asterisk Manager Interface
    Permite fazer chamadas, monitorar status e controlar o sistema
    """
    
    def __init__(self, host: str = None, port: int = None, 
                 username: str = None, password: str = None):
        # Usar variáveis de ambiente se disponíveis
        self.host = host or os.getenv('ASTERISK_HOST', 'localhost')
        self.port = port or int(os.getenv('ASTERISK_PORT', '5038'))
        self.username = username or os.getenv('ASTERISK_USERNAME', 'admin')
        self.password = password or os.getenv('ASTERISK_PASSWORD', 'amp111')
        
        # Conexão
        self.socket = None
        self.connected = False
        self.authenticated = False
        
        # Callbacks para eventos
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # Controle de chamadas
        self.active_calls: Dict[str, CallEvent] = {}
        self.call_sequence = 0
        
        # Queue de mensagens
        self.message_queue = asyncio.Queue()
        self.response_handlers: Dict[str, asyncio.Event] = {}
        self.responses: Dict[str, Dict] = {}
        
    async def connect(self) -> bool:
        """Conecta ao Asterisk AMI"""
        try:
            logger.info(f"🔌 Conectando ao Asterisk AMI em {self.host}:{self.port}")
            
            # Criar socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            
            # Conectar
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.connect, (self.host, self.port)
            )
            
            # Ler banner de boas-vindas
            welcome = await self._read_response()
            logger.info(f"📢 Asterisk Banner: {welcome.get('response', 'Unknown')}")
            
            self.connected = True
            
            # Autenticar
            if await self._authenticate():
                logger.info("✅ Conectado e autenticado com sucesso!")
                
                # Iniciar worker de eventos
                asyncio.create_task(self._event_worker())
                
                return True
            else:
                logger.error("❌ Falha na autenticação")
                await self.disconnect()
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao conectar: {str(e)}")
            await self.disconnect()
            return False
    
    async def _authenticate(self) -> bool:
        """Autentica no AMI"""
        try:
            auth_data = {
                "Action": "Login",
                "Username": self.username,
                "Secret": self.password
            }
            
            response = await self._send_action(auth_data)
            
            if response.get("Response") == "Success":
                self.authenticated = True
                logger.info("🔑 Autenticação bem-sucedida")
                return True
            else:
                logger.error(f"🔒 Falha na autenticação: {response.get('Message', 'Unknown')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {str(e)}")
            return False
    
    async def disconnect(self):
        """Desconecta do AMI"""
        try:
            if self.authenticated:
                await self._send_action({"Action": "Logoff"})
            
            if self.socket:
                self.socket.close()
                
            self.connected = False
            self.authenticated = False
            logger.info("🔌 Desconectado do Asterisk AMI")
            
        except Exception as e:
            logger.error(f"❌ Erro ao desconectar: {str(e)}")
    
    async def originate_call(self, phone_number: str, campaign_id: int, 
                           context: str = "discador-outbound", 
                           cli_number: str = "+5511999999999") -> str:
        """
        Origina uma chamada para um número
        Retorna o ID único da chamada
        """
        try:
            # Gerar ID único para a chamada
            call_id = f"call_{campaign_id}_{self.call_sequence}_{int(time.time())}"
            self.call_sequence += 1
            
            # Limpar número (remover caracteres especiais)
            clean_number = ''.join(filter(str.isdigit, phone_number))
            
            logger.info(f"📞 Originando chamada: {phone_number} (ID: {call_id})")
            
            # Dados da ação Originate
            originate_data = {
                "Action": "Originate",
                "Channel": f"Local/{clean_number}@{context}",
                "Context": context,
                "Exten": clean_number,
                "Priority": "1",
                "CallerID": f"Discador <{cli_number}>",
                "Timeout": "30000",  # 30 segundos
                "Variables": f"CALL_ID={call_id},CAMPAIGN_ID={campaign_id},PHONE_NUMBER={phone_number}",
                "ActionID": call_id
            }
            
            # Registrar chamada
            call_event = CallEvent(
                call_id=call_id,
                phone_number=phone_number,
                campaign_id=campaign_id,
                status=CallStatus.INITIATED,
                timestamp=time.time()
            )
            
            self.active_calls[call_id] = call_event
            
            # Enviar comando
            response = await self._send_action(originate_data)
            
            if response.get("Response") == "Success":
                logger.info(f"✅ Chamada originada com sucesso: {call_id}")
                return call_id
            else:
                logger.error(f"❌ Falha ao originar chamada: {response.get('Message', 'Unknown')}")
                # Remover da lista de chamadas ativas
                if call_id in self.active_calls:
                    del self.active_calls[call_id]
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao originar chamada: {str(e)}")
            if call_id in self.active_calls:
                del self.active_calls[call_id]
            return None
    
    async def originar_llamada_presione1(self, numero_destino: str, cli: str, 
                                        audio_url: str = None, timeout_dtmf: int = 15,
                                        llamada_id: int = None, detectar_voicemail: bool = True,
                                        mensaje_voicemail_url: str = None, 
                                        duracion_maxima_voicemail: int = 30) -> Dict[str, any]:
        """Origina uma chamada específica para campanhas Presione 1"""
        try:
            # Gerar ID único para a chamada
            call_id = f"presione1_{llamada_id}_{int(time.time())}"
            
            # Limpar número
            clean_number = ''.join(filter(str.isdigit, numero_destino))
            
            logger.info(f"📞 Originando chamada Presione 1: {numero_destino} (ID: {call_id})")
            
            # Dados da ação Originate para Presione 1
            originate_data = {
                "Action": "Originate",
                "Channel": f"Local/{clean_number}@discador-presione1",
                "Context": "discador-presione1",
                "Exten": clean_number,
                "Priority": "1",
                "CallerID": f"Discador <{cli}>",
                "Timeout": "30000",
                "Variables": f"CALL_ID={call_id},LLAMADA_ID={llamada_id},AUDIO_URL={audio_url or ''},TIMEOUT_DTMF={timeout_dtmf},DETECTAR_VM={detectar_voicemail},VM_URL={mensaje_voicemail_url or ''},VM_MAX_DUR={duracion_maxima_voicemail}",
                "ActionID": call_id
            }
            
            # Registrar chamada
            call_event = CallEvent(
                call_id=call_id,
                phone_number=numero_destino,
                campaign_id=llamada_id or 0,
                status=CallStatus.INITIATED,
                timestamp=time.time()
            )
            
            self.active_calls[call_id] = call_event
            
            # Enviar comando
            response = await self._send_action(originate_data)
            
            if response.get("Response") == "Success":
                logger.info(f"✅ Chamada Presione 1 originada: {call_id}")
                return {
                    "UniqueID": call_id,
                    "Channel": f"Local/{clean_number}@discador-presione1",
                    "success": True
                }
            else:
                logger.error(f"❌ Falha ao originar chamada Presione 1: {response.get('Message')}")
                if call_id in self.active_calls:
                    del self.active_calls[call_id]
                return {
                    "UniqueID": None,
                    "Channel": None,
                    "success": False,
                    "error": response.get('Message', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao originar chamada Presione 1: {str(e)}")
            return {
                "UniqueID": None,
                "Channel": None,
                "success": False,
                "error": str(e)
            }
    
    async def transferir_llamada(self, channel: str, destino: str) -> Dict[str, any]:
        """Transfere uma chamada para uma extensão específica"""
        try:
            logger.info(f"📞 Transferindo chamada {channel} para extensão {destino}")
            
            transfer_data = {
                "Action": "Redirect",
                "Channel": channel,
                "Context": "discador-transfer",
                "Exten": destino,
                "Priority": "1",
                "ActionID": f"transfer_{int(time.time())}"
            }
            
            response = await self._send_action(transfer_data)
            
            if response.get("Response") == "Success":
                logger.info(f"✅ Chamada transferida com sucesso para {destino}")
                return {"success": True, "message": "Transferência realizada"}
            else:
                logger.error(f"❌ Falha na transferência: {response.get('Message')}")
                return {"success": False, "error": response.get('Message', 'Unknown error')}
                
        except Exception as e:
            logger.error(f"❌ Erro ao transferir chamada: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def transferir_a_cola(self, channel: str, cola: str) -> Dict[str, any]:
        """Transfere uma chamada para uma fila de agentes"""
        try:
            logger.info(f"📞 Transferindo chamada {channel} para fila {cola}")
            
            # Transferir para fila usando Queue
            transfer_data = {
                "Action": "Redirect",
                "Channel": channel,
                "Context": "discador-queues",
                "Exten": cola,
                "Priority": "1",
                "ActionID": f"queue_transfer_{int(time.time())}"
            }
            
            response = await self._send_action(transfer_data)
            
            if response.get("Response") == "Success":
                logger.info(f"✅ Chamada transferida com sucesso para fila {cola}")
                return {"success": True, "message": f"Transferido para fila {cola}"}
            else:
                logger.error(f"❌ Falha na transferência para fila: {response.get('Message')}")
                return {"success": False, "error": response.get('Message', 'Unknown error')}
                
        except Exception as e:
            logger.error(f"❌ Erro ao transferir para fila: {str(e)}")
            return {"success": False, "error": str(e)}
                
        except Exception as e:
            logger.error(f"❌ Erro ao originar chamada: {str(e)}")
            return ""
    
    async def hangup_call(self, call_id: str) -> bool:
        """Finaliza uma chamada"""
        try:
            if call_id not in self.active_calls:
                logger.warning(f"⚠️ Chamada {call_id} não encontrada")
                return False
            
            call = self.active_calls[call_id]
            
            hangup_data = {
                "Action": "Hangup",
                "Channel": f"Local/{call.phone_number}@discador-outbound",
                "ActionID": f"hangup_{call_id}"
            }
            
            response = await self._send_action(hangup_data)
            
            if response.get("Response") == "Success":
                logger.info(f"📴 Chamada finalizada: {call_id}")
                
                # Atualizar status
                call.status = CallStatus.HANGUP
                call.timestamp = time.time()
                
                return True
            else:
                logger.error(f"❌ Falha ao finalizar chamada: {response.get('Message', 'Unknown')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao finalizar chamada: {str(e)}")
            return False
    
    async def play_audio(self, call_id: str, audio_file: str) -> bool:
        """Reproduz um áudio em uma chamada"""
        try:
            if call_id not in self.active_calls:
                logger.warning(f"⚠️ Chamada {call_id} não encontrada")
                return False
            
            call = self.active_calls[call_id]
            
            playback_data = {
                "Action": "Command",
                "Command": f"channel originate Local/{call.phone_number}@discador-outbound application Playback {audio_file}",
                "ActionID": f"playback_{call_id}"
            }
            
            response = await self._send_action(playback_data)
            
            if response.get("Response") == "Success":
                logger.info(f"🔊 Áudio reproduzido: {audio_file} na chamada {call_id}")
                return True
            else:
                logger.error(f"❌ Falha ao reproduzir áudio: {response.get('Message', 'Unknown')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao reproduzir áudio: {str(e)}")
            return False
    
    async def get_call_status(self, call_id: str) -> Optional[CallEvent]:
        """Retorna o status atual de uma chamada"""
        return self.active_calls.get(call_id)
    
    async def get_active_calls(self) -> List[CallEvent]:
        """Retorna todas as chamadas ativas"""
        return list(self.active_calls.values())
    
    def register_event_callback(self, event_type: str, callback: Callable):
        """Registra callback para eventos específicos"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    async def _send_action(self, action_data: Dict) -> Dict:
        """Envia uma ação para o AMI e aguarda resposta"""
        try:
            if not self.connected:
                raise Exception("Não conectado ao AMI")
            
            # Gerar ActionID se não existe
            if "ActionID" not in action_data:
                action_data["ActionID"] = str(uuid.uuid4())
            
            action_id = action_data["ActionID"]
            
            # Preparar evento de resposta
            self.response_handlers[action_id] = asyncio.Event()
            
            # Construir mensagem
            message = ""
            for key, value in action_data.items():
                message += f"{key}: {value}\r\n"
            message += "\r\n"
            
            # Enviar
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.send, message.encode()
            )
            
            # Aguardar resposta (timeout 10 segundos)
            try:
                await asyncio.wait_for(self.response_handlers[action_id].wait(), timeout=10.0)
                response = self.responses.get(action_id, {})
                
                # Limpar
                del self.response_handlers[action_id]
                if action_id in self.responses:
                    del self.responses[action_id]
                
                return response
                
            except asyncio.TimeoutError:
                logger.error(f"⏰ Timeout aguardando resposta para ação {action_id}")
                if action_id in self.response_handlers:
                    del self.response_handlers[action_id]
                return {"Response": "Error", "Message": "Timeout"}
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar ação: {str(e)}")
            return {"Response": "Error", "Message": str(e)}
    
    async def _read_response(self) -> Dict:
        """Lê uma resposta do AMI"""
        try:
            data = ""
            while True:
                chunk = await asyncio.get_event_loop().run_in_executor(
                    None, self.socket.recv, 1024
                )
                
                if not chunk:
                    break
                
                data += chunk.decode()
                
                # Verifica fim da mensagem
                if "\r\n\r\n" in data:
                    break
            
            # Parse da resposta
            response = {}
            lines = data.strip().split("\r\n")
            
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    response[key.strip()] = value.strip()
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro ao ler resposta: {str(e)}")
            return {}
    
    async def _event_worker(self):
        """Worker para processar eventos do AMI"""
        logger.info("🔄 Iniciando worker de eventos AMI")
        
        while self.connected:
            try:
                # Ler evento
                event_data = await self._read_response()
                
                if not event_data:
                    continue
                
                # Processar diferentes tipos de evento
                event_type = event_data.get("Event", "")
                action_id = event_data.get("ActionID", "")
                
                # Se é resposta a uma ação
                if "Response" in event_data and action_id:
                    self.responses[action_id] = event_data
                    if action_id in self.response_handlers:
                        self.response_handlers[action_id].set()
                
                # Processar eventos de chamada
                await self._process_call_event(event_type, event_data)
                
                # Chamar callbacks registrados
                if event_type in self.event_callbacks:
                    for callback in self.event_callbacks[event_type]:
                        try:
                            await callback(event_data)
                        except Exception as e:
                            logger.error(f"❌ Erro em callback {event_type}: {str(e)}")
                
            except Exception as e:
                logger.error(f"❌ Erro no worker de eventos: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_call_event(self, event_type: str, event_data: Dict):
        """Processa eventos específicos de chamadas"""
        try:
            call_id = event_data.get("Variables", {}).get("CALL_ID", "")
            if not call_id:
                return
            
            if call_id not in self.active_calls:
                return
            
            call = self.active_calls[call_id]
            
            # Mapear eventos para status
            status_mapping = {
                "Dial": CallStatus.RINGING,
                "DialEnd": self._get_dial_end_status(event_data),
                "Hangup": CallStatus.HANGUP,
                "DTMF": None  # Processado separadamente
            }
            
            if event_type in status_mapping and status_mapping[event_type]:
                call.status = status_mapping[event_type]
                call.timestamp = time.time()
                
                logger.info(f"📱 Chamada {call_id}: {event_type} -> {call.status.value}")
            
            # Processar DTMF
            if event_type == "DTMF":
                digit = event_data.get("Digit", "")
                call.dtmf_pressed += digit
                logger.info(f"🔢 DTMF detectado na chamada {call_id}: {digit}")
                
                # Se pressionou "1", marcar para transferência
                if digit == "1":
                    call.transferred = True
                    logger.info(f"✅ Presione 1 detectado na chamada {call_id}")
                    
                    # Aqui você pode implementar a lógica de transferência
                    await self._transfer_call(call_id)
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar evento de chamada: {str(e)}")
    
    def _get_dial_end_status(self, event_data: Dict) -> CallStatus:
        """Determina o status final baseado no DialEnd"""
        dial_status = event_data.get("DialStatus", "").upper()
        
        status_map = {
            "ANSWER": CallStatus.ANSWERED,
            "BUSY": CallStatus.BUSY,
            "NOANSWER": CallStatus.NO_ANSWER,
            "CONGESTION": CallStatus.CONGESTION,
            "CANCEL": CallStatus.HANGUP,
            "FAILED": CallStatus.FAILED
        }
        
        return status_map.get(dial_status, CallStatus.FAILED)
    
    async def _transfer_call(self, call_id: str):
        """Transfere uma chamada após detecção de Presione 1"""
        try:
            if call_id not in self.active_calls:
                return
            
            call = self.active_calls[call_id]
            
            # Transferir para fila ou extensão
            transfer_data = {
                "Action": "Redirect",
                "Channel": f"Local/{call.phone_number}@discador-outbound",
                "Context": "discador-transfer",
                "Exten": "100",  # Extensão do agente
                "Priority": "1",
                "ActionID": f"transfer_{call_id}"
            }
            
            response = await self._send_action(transfer_data)
            
            if response.get("Response") == "Success":
                logger.info(f"📞 Chamada {call_id} transferida com sucesso")
                call.transferred = True
            else:
                logger.error(f"❌ Falha ao transferir chamada {call_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao transferir chamada: {str(e)}")

# Instância global do AMI
asterisk_ami = AsteriskAMI()

async def init_asterisk():
    """Inicializa conexão com Asterisk"""
    return await asterisk_ami.connect()

async def cleanup_asterisk():
    """Limpa conexão com Asterisk"""
    await asterisk_ami.disconnect()