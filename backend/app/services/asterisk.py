from typing import Dict, Any, Optional
import logging
import asyncio
import uuid
from datetime import datetime
import os

# Configurar logger
logger = logging.getLogger(__name__)

class AsteriskAMIService:
    """
    Serviço simplificado para Asterisk Manager Interface (AMI).
    Versão mock para produção sem dependências externas.
    """
    def __init__(self):
        # Usar variáveis de ambiente se disponíveis
        self.host = os.getenv('ASTERISK_HOST', 'localhost')
        self.port = int(os.getenv('ASTERISK_PUERTO', '5038'))
        self.username = os.getenv('ASTERISK_USUARIO', 'admin')
        self.password = os.getenv('ASTERISK_PASSWORD', 'password')
        self.conectado = False
        self.event_callbacks = {}
        
    async def conectar(self) -> bool:
        """
        Simula conexão ao AMI de Asterisk.
        """
        logger.info(f"Mock: Conectando a Asterisk AMI em {self.host}:{self.port}")
        await asyncio.sleep(0.1)
        self.conectado = True
        return True
    
    async def desconectar(self) -> bool:
        """
        Simula desconexão do AMI de Asterisk.
        """
        logger.info("Mock: Desconectando de Asterisk AMI")
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
        Simula originação de chamada.
        """
        if not self.conectado:
            await self.conectar()
        
        unique_id = f"SIM-{uuid.uuid4().hex[:12]}"
        channel = f"SIP/{numero_destino}-{unique_id[:6]}"
        
        logger.info(f"Mock: Originando chamada para {numero_destino} com CLI {cli}")
        
        await asyncio.sleep(0.2)
        
        return {
            "Response": "Success",
            "ActionID": f"action-{uuid.uuid4().hex[:8]}",
            "Message": "Originate successfully queued",
            "Timestamp": datetime.now().isoformat(),
            "UniqueID": unique_id,
            "Channel": channel,
            "Simulation": True
        }
    
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
        Simula chamada com modo "Presione 1".
        """
        if not self.conectado:
            await self.conectar()
        
        unique_id = f"P1-{uuid.uuid4().hex[:12]}"
        
        logger.info(f"Mock: Iniciando chamada Presione 1 para {numero_destino}")
        
        await asyncio.sleep(0.3)
        
        return {
            "Response": "Success",
            "ActionID": f"presione1-{uuid.uuid4().hex[:8]}",
            "Message": "Presione1 call originated successfully",
            "Timestamp": datetime.now().isoformat(),
            "UniqueID": unique_id,
            "LlamadaID": llamada_id,
            "Mode": "PRESIONE1_MOCK",
            "Simulation": True
        }
    
    async def transferir_llamada(self, channel: str, destino: str) -> Dict[str, Any]:
        """
        Simula transferência de chamada.
        """
        logger.info(f"Mock: Transferindo {channel} para {destino}")
        
        return {
            "Response": "Success",
            "Message": "Transfer completed",
            "Channel": channel,
            "Destination": destino,
            "Simulation": True
        }
    
    async def desligar_chamada(self, channel: str, motivo: str = "Normal Clearing") -> Dict[str, Any]:
        """
        Simula desligamento de chamada.
        """
        logger.info(f"Mock: Desligando chamada {channel} - {motivo}")
        
        return {
            "Response": "Success",
            "Message": "Hangup completed",
            "Channel": channel,
            "Cause": motivo,
            "Simulation": True
        }

# Instância global do serviço
asterisk_service = AsteriskAMIService() 