#!/usr/bin/env python3
"""
Worker Principal do Discador Preditivo
Gerencia a fila de chamadas e executa discagem automaticamente
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

from .asterisk_manager import asterisk_ami, CallStatus, CallEvent
from .predictive_algorithm import get_predictive_dialer
from ..database import get_db_connection

logger = logging.getLogger(__name__)

@dataclass
class CampaignConfig:
    """Configuração da campanha"""
    campaign_id: int
    name: str
    status: str
    cli_number: str
    max_attempts: int = 3
    retry_delay: int = 3600  # 1 hora
    active: bool = True

class DialerWorker:
    """
    Worker principal que gerencia todo o processo de discagem
    """
    
    def __init__(self):
        self.running = False
        self.active_campaigns: Dict[int, CampaignConfig] = {}
        self.call_queue: asyncio.Queue = asyncio.Queue()
        self.active_calls: Set[str] = set()
        self.predictive_dialer = get_predictive_dialer()
        
        # Controle de loops
        self.dialer_task = None
        self.queue_processor_task = None
        self.metrics_task = None
        
    async def start(self):
        """Inicia o worker"""
        if self.running:
            logger.warning("⚠️ Worker já está executando")
            return
            
        try:
            # Conectar ao Asterisk
            if not await asterisk_ami.connect():
                logger.error("❌ Falha ao conectar com Asterisk")
                return
            
            self.running = True
            logger.info("🚀 Worker de discagem iniciado")
            
            # Carregar campanhas ativas
            await self._load_active_campaigns()
            
            # Iniciar tasks
            self.dialer_task = asyncio.create_task(self._dialer_loop())
            self.queue_processor_task = asyncio.create_task(self._queue_processor())
            self.metrics_task = asyncio.create_task(self._metrics_loop())
            
            logger.info("✅ Todos os componentes iniciados com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar worker: {str(e)}")
            await self.stop()
    
    async def stop(self):
        """Para o worker"""
        if not self.running:
            return
            
        logger.info("🛑 Parando worker de discagem...")
        self.running = False
        
        # Cancelar tasks
        if self.dialer_task:
            self.dialer_task.cancel()
        if self.queue_processor_task:
            self.queue_processor_task.cancel()
        if self.metrics_task:
            self.metrics_task.cancel()
            
        # Finalizar chamadas ativas
        await self._hangup_all_calls()
        
        # Desconectar do Asterisk
        await asterisk_ami.disconnect()
        
        logger.info("✅ Worker parado com sucesso")
    
    async def add_campaign(self, campaign_id: int, name: str, cli_number: str):
        """Adiciona uma campanha à fila"""
        try:
            config = CampaignConfig(
                campaign_id=campaign_id,
                name=name,
                status="active",
                cli_number=cli_number
            )
            
            self.active_campaigns[campaign_id] = config
            logger.info(f"📝 Campanha adicionada: {name} (ID: {campaign_id})")
            
            # Carregar contatos para a fila
            await self._load_contacts_to_queue(campaign_id)
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar campanha: {str(e)}")
    
    async def pause_campaign(self, campaign_id: int):
        """Pausa uma campanha"""
        if campaign_id in self.active_campaigns:
            self.active_campaigns[campaign_id].active = False
            logger.info(f"⏸️ Campanha pausada: {campaign_id}")
    
    async def resume_campaign(self, campaign_id: int):
        """Retoma uma campanha"""
        if campaign_id in self.active_campaigns:
            self.active_campaigns[campaign_id].active = True
            logger.info(f"▶️ Campanha retomada: {campaign_id}")
    
    async def remove_campaign(self, campaign_id: int):
        """Remove uma campanha"""
        if campaign_id in self.active_campaigns:
            del self.active_campaigns[campaign_id]
            logger.info(f"🗑️ Campanha removida: {campaign_id}")
    
    async def _load_active_campaigns(self):
        """Carrega campanhas ativas do banco"""
        try:
            conn = await get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, cli_number, status
                FROM campaigns 
                WHERE status = 'active'
            """)
            
            campaigns = cursor.fetchall()
            
            for campaign in campaigns:
                config = CampaignConfig(
                    campaign_id=campaign[0],
                    name=campaign[1],
                    cli_number=campaign[2] or "+5511999999999",
                    status=campaign[3]
                )
                
                self.active_campaigns[campaign[0]] = config
                logger.info(f"📋 Campanha carregada: {campaign[1]} (ID: {campaign[0]})")
                
                # Carregar contatos para fila
                await self._load_contacts_to_queue(campaign[0])
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar campanhas: {str(e)}")
    
    async def _load_contacts_to_queue(self, campaign_id: int):
        """Carrega contatos de uma campanha para a fila"""
        try:
            conn = await get_db_connection()
            cursor = conn.cursor()
            
            # Buscar contatos não discados ou com falha
            cursor.execute("""
                SELECT id, phone_number, attempts
                FROM contacts 
                WHERE campaign_id = ? 
                AND (status IS NULL OR status IN ('failed', 'no_answer'))
                AND attempts < 3
                ORDER BY id
                LIMIT 1000
            """, (campaign_id,))
            
            contacts = cursor.fetchall()
            
            # Adicionar à fila
            for contact in contacts:
                await self.call_queue.put({
                    'contact_id': contact[0],
                    'phone_number': contact[1],
                    'campaign_id': campaign_id,
                    'attempts': contact[2] or 0
                })
            
            logger.info(f"📞 {len(contacts)} contatos carregados para campanha {campaign_id}")
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar contatos: {str(e)}")
    
    async def _dialer_loop(self):
        """Loop principal do discador"""
        logger.info("🔄 Iniciando loop de discagem")
        
        while self.running:
            try:
                # Verificar se deve fazer uma chamada
                if self.predictive_dialer.should_make_call():
                    await self._attempt_call()
                
                # Esperar um pouco antes da próxima verificação
                await asyncio.sleep(0.5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop de discagem: {str(e)}")
                await asyncio.sleep(5)
    
    async def _attempt_call(self):
        """Tenta fazer uma chamada se possível"""
        try:
            # Verificar se há campanha ativa
            active_campaigns = [c for c in self.active_campaigns.values() if c.active]
            if not active_campaigns:
                return
            
            # Verificar se há contatos na fila
            if self.call_queue.empty():
                # Tentar recarregar contatos
                for campaign in active_campaigns:
                    await self._load_contacts_to_queue(campaign.campaign_id)
                return
            
            # Pegar próximo contato da fila
            try:
                contact_data = await asyncio.wait_for(self.call_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                return
            
            # Buscar configuração da campanha
            campaign_id = contact_data['campaign_id']
            if campaign_id not in self.active_campaigns:
                return
                
            campaign = self.active_campaigns[campaign_id]
            
            # Fazer a chamada
            call_id = await asterisk_ami.originate_call(
                phone_number=contact_data['phone_number'],
                campaign_id=campaign_id,
                cli_number=campaign.cli_number
            )
            
            if call_id:
                self.active_calls.add(call_id)
                self.predictive_dialer.calls_in_progress += 1
                
                # Registrar no banco
                await self._update_contact_status(
                    contact_data['contact_id'], 
                    'calling', 
                    call_id
                )
                
                logger.info(f"📞 Chamada iniciada: {contact_data['phone_number']} (ID: {call_id})")
                
                # Registrar callback para resultado
                asterisk_ami.register_event_callback(
                    'call_ended',
                    lambda event: self._handle_call_ended(call_id, contact_data, event)
                )
            
        except Exception as e:
            logger.error(f"❌ Erro ao tentar chamada: {str(e)}")
    
    async def _queue_processor(self):
        """Processa eventos da fila"""
        logger.info("🔄 Iniciando processador de fila")
        
        while self.running:
            try:
                # Verificar chamadas ativas
                await self._check_active_calls()
                
                # Limpar chamadas antigas
                await self._cleanup_old_calls()
                
                await asyncio.sleep(10)  # Verificar a cada 10 segundos
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erro no processador de fila: {str(e)}")
                await asyncio.sleep(5)
    
    async def _check_active_calls(self):
        """Verifica status das chamadas ativas"""
        try:
            calls_to_remove = []
            
            for call_id in self.active_calls:
                call_status = await asterisk_ami.get_call_status(call_id)
                
                if not call_status:
                    calls_to_remove.append(call_id)
                    continue
                
                # Verificar se chamada finalizou
                if call_status.status in [CallStatus.HANGUP, CallStatus.FAILED, CallStatus.NO_ANSWER]:
                    calls_to_remove.append(call_id)
                    
                    # Registrar resultado
                    self.predictive_dialer.record_call_result(
                        call_id, 
                        call_status.status.value,
                        int(time.time() - call_status.timestamp)
                    )
                    
                    logger.info(f"📴 Chamada finalizada: {call_id} - {call_status.status.value}")
            
            # Remover chamadas finalizadas
            for call_id in calls_to_remove:
                self.active_calls.discard(call_id)
                self.predictive_dialer.calls_in_progress -= 1
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar chamadas: {str(e)}")
    
    async def _cleanup_old_calls(self):
        """Limpa chamadas antigas (mais de 5 minutos)"""
        try:
            current_time = time.time()
            calls_to_remove = []
            
            for call_id in self.active_calls:
                call_status = await asterisk_ami.get_call_status(call_id)
                
                if call_status and (current_time - call_status.timestamp) > 300:  # 5 minutos
                    calls_to_remove.append(call_id)
                    logger.warning(f"⏰ Chamada antiga removida: {call_id}")
            
            for call_id in calls_to_remove:
                self.active_calls.discard(call_id)
                self.predictive_dialer.calls_in_progress -= 1
                
        except Exception as e:
            logger.error(f"❌ Erro ao limpar chamadas antigas: {str(e)}")
    
    async def _metrics_loop(self):
        """Loop de métricas e estatísticas"""
        logger.info("📊 Iniciando loop de métricas")
        
        while self.running:
            try:
                # Salvar snapshot de métricas
                self.predictive_dialer.save_metrics_snapshot()
                
                # Log de estatísticas
                stats = self.predictive_dialer.get_current_stats()
                logger.info(f"📈 Stats: CPS={stats['current_cps']:.2f}, "
                           f"Ativas={len(self.active_calls)}, "
                           f"Taxa resposta={stats['answer_rate']:.2%}")
                
                # Aguardar 1 minuto
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop de métricas: {str(e)}")
                await asyncio.sleep(60)
    
    async def _update_contact_status(self, contact_id: int, status: str, call_id: str = ""):
        """Atualiza status do contato no banco"""
        try:
            conn = await get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE contacts 
                SET status = ?, 
                    last_call_date = datetime('now'),
                    call_id = ?,
                    attempts = attempts + 1
                WHERE id = ?
            """, (status, call_id, contact_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar contato: {str(e)}")
    
    async def _handle_call_ended(self, call_id: str, contact_data: Dict, event: Dict):
        """Processa fim de chamada"""
        try:
            # Atualizar status no banco
            final_status = event.get('status', 'completed')
            await self._update_contact_status(
                contact_data['contact_id'], 
                final_status
            )
            
            # Se foi transferido (Presione 1), marcar como sucesso
            if event.get('transferred', False):
                await self._update_contact_status(
                    contact_data['contact_id'], 
                    'transferred'
                )
            
            logger.info(f"✅ Chamada processada: {call_id} - {final_status}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar fim de chamada: {str(e)}")
    
    async def _hangup_all_calls(self):
        """Finaliza todas as chamadas ativas"""
        try:
            for call_id in self.active_calls.copy():
                await asterisk_ami.hangup_call(call_id)
            
            self.active_calls.clear()
            self.predictive_dialer.calls_in_progress = 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao finalizar chamadas: {str(e)}")
    
    def get_status(self) -> Dict:
        """Retorna status atual do worker"""
        return {
            "running": self.running,
            "active_campaigns": len(self.active_campaigns),
            "active_calls": len(self.active_calls),
            "queue_size": self.call_queue.qsize(),
            "predictive_stats": self.predictive_dialer.get_current_stats()
        }

# Instância global do worker
dialer_worker = DialerWorker()

def get_dialer_worker() -> DialerWorker:
    """Retorna instância do worker"""
    return dialer_worker 