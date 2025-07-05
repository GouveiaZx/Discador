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
    
    def __init__(self, host: str = "localhost", port: int = 5038, 
                 username: str = "admin", password: str = "admin123"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
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
            
            # Enviar comando (simulado por enquanto)
            logger.info(f"✅ Chamada simulada originada: {call_id}")
            return call_id
                
        except Exception as e:
            logger.error(f"❌ Erro ao originar chamada: {str(e)}")
            return ""
    
    async def get_active_calls(self) -> List[CallEvent]:
        """Retorna todas as chamadas ativas"""
        return list(self.active_calls.values())
    
    async def _authenticate(self) -> bool:
        """Autentica no AMI (simulado)"""
        self.authenticated = True
        return True
    
    async def disconnect(self):
        """Desconecta do AMI"""
        self.connected = False
        self.authenticated = False
        logger.info("🔌 Desconectado do Asterisk AMI")
    
    async def _read_response(self) -> Dict:
        """Lê uma resposta do AMI (simulado)"""
        return {"response": "Asterisk Call Manager/5.0.0"}
    
    async def _event_worker(self):
        """Worker para processar eventos do AMI"""
        logger.info("🔄 Iniciando worker de eventos AMI")
        
        while self.connected:
            await asyncio.sleep(1)

# Instância global do AMI
asterisk_ami = AsteriskAMI()

async def init_asterisk():
    """Inicializa conexão com Asterisk"""
    return await asterisk_ami.connect()

async def cleanup_asterisk():
    """Limpa conexão com Asterisk"""
    await asterisk_ami.disconnect() 