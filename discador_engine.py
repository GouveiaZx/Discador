#!/usr/bin/env python3
"""
Engine de Discagem Automática para Discador Preditivo
Simula chamadas VoIP até integração real com Asterisk
"""
import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallResult(Enum):
    """Resultado das chamadas"""
    SUCCESS_PRESSED_1 = "success_pressed_1"
    SUCCESS_TRANSFERRED = "success_transferred" 
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    REJECTED = "rejected"
    HANGUP = "hangup"
    ERROR = "error"
    BLACKLISTED = "blacklisted"

class ContactStatus(Enum):
    """Status dos contatos"""
    NOT_STARTED = "not_started"
    CALLING = "calling"
    ANSWERED = "answered"
    PRESSED_1 = "pressed_1"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    REJECTED = "rejected"
    BLACKLISTED = "blacklisted"
    ERROR = "error"

@dataclass
class CallLog:
    """Log de uma chamada"""
    call_id: str
    phone_number: str
    cli_number: str
    initiated_at: datetime
    answered_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    result: Optional[CallResult] = None
    dtmf_pressed: Optional[str] = None
    duration_seconds: int = 0
    error_message: Optional[str] = None

class DiscadorEngine:
    """
    Engine principal do discador preditivo
    """
    
    def __init__(self):
        self.active_calls: Dict[str, CallLog] = {}
        self.campaign_stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'answered_calls': 0,
            'pressed_1_calls': 0,
            'transferred_calls': 0,
            'no_answer_calls': 0,
            'busy_calls': 0,
            'error_calls': 0
        }
        self.is_running = False
        self.max_concurrent_calls = 5
        self.call_interval = 2  # segundos entre chamadas
        
    async def start_campaign(self, campaign_id: int, contacts: List[Dict], cli_number: str):
        """
        Inicia uma campanha de discagem
        """
        logger.info(f"🚀 Iniciando campanha {campaign_id} com {len(contacts)} contatos")
        self.is_running = True
        
        # Filtrar contatos ativos
        active_contacts = [c for c in contacts if c.get('status') != 'blacklisted']
        
        # Processar contatos em batches
        batch_size = self.max_concurrent_calls
        for i in range(0, len(active_contacts), batch_size):
            if not self.is_running:
                break
                
            batch = active_contacts[i:i + batch_size]
            
            # Executar chamadas do batch em paralelo
            tasks = []
            for contact in batch:
                task = asyncio.create_task(
                    self.make_call(contact, cli_number, campaign_id)
                )
                tasks.append(task)
            
            # Aguardar conclusão do batch
            await asyncio.gather(*tasks)
            
            # Intervalo entre batches
            await asyncio.sleep(self.call_interval)
            
        logger.info(f"✅ Campanha {campaign_id} finalizada")
        self.is_running = False
        
    async def make_call(self, contact: Dict, cli_number: str, campaign_id: int) -> CallLog:
        """
        Realiza uma chamada individual (simulada)
        """
        call_id = f"call_{int(time.time())}_{random.randint(1000, 9999)}"
        phone_number = contact['phone_number']
        
        # Criar log da chamada
        call_log = CallLog(
            call_id=call_id,
            phone_number=phone_number,
            cli_number=cli_number,
            initiated_at=datetime.now()
        )
        
        self.active_calls[call_id] = call_log
        
        try:
            logger.info(f"📞 Chamando {phone_number}...")
            
            # Simular tempo de chamada (2-8 segundos)
            call_duration = random.uniform(2, 8)
            await asyncio.sleep(call_duration)
            
            # Simular resultados baseados em probabilidades realistas
            result = self._simulate_call_result()
            
            # Atualizar log da chamada
            call_log.ended_at = datetime.now()
            call_log.result = result
            call_log.duration_seconds = int(call_duration)
            
            # Processar resultado específico
            if result == CallResult.SUCCESS_PRESSED_1:
                call_log.answered_at = call_log.initiated_at + timedelta(seconds=1)
                call_log.dtmf_pressed = "1"
                await self._handle_pressed_1(call_log, contact)
                
            elif result == CallResult.SUCCESS_TRANSFERRED:
                call_log.answered_at = call_log.initiated_at + timedelta(seconds=1)
                call_log.dtmf_pressed = "1"
                await self._handle_transfer(call_log, contact)
            
            # Atualizar estatísticas
            self._update_stats(result)
            
            logger.info(f"📊 Chamada {call_id} finalizada: {result.value}")
            
        except Exception as e:
            call_log.error_message = str(e)
            call_log.result = CallResult.ERROR
            logger.error(f"❌ Erro na chamada {call_id}: {e}")
            
        finally:
            # Remover da lista de chamadas ativas
            if call_id in self.active_calls:
                del self.active_calls[call_id]
                
        return call_log
    
    def _simulate_call_result(self) -> CallResult:
        """
        Simula resultado de chamada com probabilidades realistas
        """
        # Probabilidades baseadas em dados reais de call centers
        probabilities = {
            CallResult.NO_ANSWER: 0.35,        # 35% - não atende
            CallResult.BUSY: 0.15,             # 15% - ocupado
            CallResult.REJECTED: 0.10,         # 10% - rejeitado
            CallResult.HANGUP: 0.20,           # 20% - desliga rápido
            CallResult.SUCCESS_PRESSED_1: 0.12, # 12% - pressiona 1
            CallResult.SUCCESS_TRANSFERRED: 0.06, # 6% - transferido
            CallResult.ERROR: 0.02             # 2% - erro técnico
        }
        
        rand = random.random()
        cumulative = 0
        
        for result, prob in probabilities.items():
            cumulative += prob
            if rand <= cumulative:
                return result
                
        return CallResult.ERROR
    
    async def _handle_pressed_1(self, call_log: CallLog, contact: Dict):
        """
        Processa quando o usuário pressiona 1
        """
        logger.info(f"🎯 SUCESSO! {contact['phone_number']} pressionou 1")
        
        # Simular tempo de processamento
        await asyncio.sleep(0.5)
        
        # Aqui seria a integração com sistema de transferência
        # Por enquanto, apenas loggar
        
    async def _handle_transfer(self, call_log: CallLog, contact: Dict):
        """
        Processa transferência para agente
        """
        logger.info(f"📞 Transferindo {contact['phone_number']} para agente")
        
        # Simular transferência
        await asyncio.sleep(1)
        
        # Aqui seria a integração com sistema de agentes
        
    def _update_stats(self, result: CallResult):
        """
        Atualiza estatísticas da campanha
        """
        self.campaign_stats['total_calls'] += 1
        
        if result in [CallResult.SUCCESS_PRESSED_1, CallResult.SUCCESS_TRANSFERRED]:
            self.campaign_stats['successful_calls'] += 1
            
        if result == CallResult.SUCCESS_PRESSED_1:
            self.campaign_stats['pressed_1_calls'] += 1
            self.campaign_stats['answered_calls'] += 1
            
        elif result == CallResult.SUCCESS_TRANSFERRED:
            self.campaign_stats['transferred_calls'] += 1
            self.campaign_stats['answered_calls'] += 1
            
        elif result == CallResult.NO_ANSWER:
            self.campaign_stats['no_answer_calls'] += 1
            
        elif result == CallResult.BUSY:
            self.campaign_stats['busy_calls'] += 1
            
        elif result == CallResult.ERROR:
            self.campaign_stats['error_calls'] += 1
    
    def get_stats(self) -> Dict:
        """
        Retorna estatísticas atuais
        """
        stats = self.campaign_stats.copy()
        
        # Calcular métricas derivadas
        if stats['total_calls'] > 0:
            stats['success_rate'] = round(
                (stats['successful_calls'] / stats['total_calls']) * 100, 2
            )
            stats['answer_rate'] = round(
                (stats['answered_calls'] / stats['total_calls']) * 100, 2
            )
        else:
            stats['success_rate'] = 0
            stats['answer_rate'] = 0
            
        stats['active_calls'] = len(self.active_calls)
        stats['is_running'] = self.is_running
        
        return stats
    
    def stop_campaign(self):
        """
        Para a campanha atual
        """
        logger.info("🛑 Parando campanha...")
        self.is_running = False
        
    def get_active_calls(self) -> List[Dict]:
        """
        Retorna chamadas ativas
        """
        return [
            {
                'call_id': call.call_id,
                'phone_number': call.phone_number,
                'initiated_at': call.initiated_at.isoformat(),
                'duration': int((datetime.now() - call.initiated_at).total_seconds())
            }
            for call in self.active_calls.values()
        ]

# Instância global do engine
discador_engine = DiscadorEngine()

# API para integração com FastAPI
class DiscadorAPI:
    """
    API para integração com o backend FastAPI
    """
    
    @staticmethod
    async def start_campaign_async(campaign_data: Dict):
        """
        Inicia campanha de forma assíncrona
        """
        campaign_id = campaign_data['id']
        contacts = campaign_data['contacts']
        cli_number = campaign_data.get('cli_number', '+5511999999999')
        
        # Executar em background
        asyncio.create_task(
            discador_engine.start_campaign(campaign_id, contacts, cli_number)
        )
        
        return {"status": "started", "campaign_id": campaign_id}
    
    @staticmethod
    def get_campaign_stats():
        """
        Retorna estatísticas da campanha
        """
        return discador_engine.get_stats()
    
    @staticmethod
    def get_active_calls():
        """
        Retorna chamadas ativas
        """
        return discador_engine.get_active_calls()
    
    @staticmethod
    def stop_campaign():
        """
        Para campanha ativa
        """
        discador_engine.stop_campaign()
        return {"status": "stopped"}

if __name__ == "__main__":
    # Teste do engine
    async def test_discador():
        # Contatos de teste
        test_contacts = [
            {"phone_number": "+5511999999991", "name": "Teste 1"},
            {"phone_number": "+5511999999992", "name": "Teste 2"},
            {"phone_number": "+5511999999993", "name": "Teste 3"},
        ]
        
        # Iniciar campanha de teste
        await discador_engine.start_campaign(1, test_contacts, "+5511123456789")
        
        # Mostrar estatísticas
        stats = discador_engine.get_stats()
        print("📊 Estatísticas finais:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    # Executar teste
    print("🧪 Testando Discador Engine...")
    asyncio.run(test_discador()) 