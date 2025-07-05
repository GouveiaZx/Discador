#!/usr/bin/env python3
"""
Sistema WebSocket para Monitoramento em Tempo Real
Transmite métricas e eventos do discador em tempo real
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import asdict

from .dialer_worker import get_dialer_worker
from .predictive_algorithm import get_predictive_dialer
from .asterisk_manager import asterisk_ami

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Gerenciador de conexões WebSocket para monitoramento em tempo real
    """
    
    def __init__(self):
        # Conexões ativas por tipo
        self.dashboard_connections: Set[WebSocket] = set()
        self.monitoring_connections: Set[WebSocket] = set()
        self.calls_connections: Set[WebSocket] = set()
        self.stats_connections: Set[WebSocket] = set()
        
        # Estado dos dados
        self.last_metrics = {}
        self.last_call_stats = {}
        self.last_system_status = {}
        
        # Task de broadcasting
        self.broadcast_task = None
        self.running = False
    
    def start(self):
        """Inicia o sistema de broadcasting"""
        if not self.running:
            self.running = True
            self.broadcast_task = asyncio.create_task(self._broadcast_loop())
            logger.info("📡 Sistema WebSocket iniciado")
    
    def stop(self):
        """Para o sistema de broadcasting"""
        self.running = False
        if self.broadcast_task:
            self.broadcast_task.cancel()
        logger.info("📡 Sistema WebSocket parado")
    
    async def connect_dashboard(self, websocket: WebSocket):
        """Conecta um cliente ao dashboard"""
        await websocket.accept()
        self.dashboard_connections.add(websocket)
        logger.info(f"📊 Dashboard conectado. Total: {len(self.dashboard_connections)}")
        
        # Enviar dados iniciais
        await self._send_initial_data(websocket, "dashboard")
    
    async def connect_monitoring(self, websocket: WebSocket):
        """Conecta um cliente ao monitoramento"""
        await websocket.accept()
        self.monitoring_connections.add(websocket)
        logger.info(f"🔍 Monitoramento conectado. Total: {len(self.monitoring_connections)}")
        
        # Enviar dados iniciais
        await self._send_initial_data(websocket, "monitoring")
    
    async def connect_calls(self, websocket: WebSocket):
        """Conecta um cliente ao monitoramento de chamadas"""
        await websocket.accept()
        self.calls_connections.add(websocket)
        logger.info(f"📞 Monitoramento de chamadas conectado. Total: {len(self.calls_connections)}")
        
        # Enviar dados iniciais
        await self._send_initial_data(websocket, "calls")
    
    async def connect_stats(self, websocket: WebSocket):
        """Conecta um cliente às estatísticas"""
        await websocket.accept()
        self.stats_connections.add(websocket)
        logger.info(f"📈 Estatísticas conectadas. Total: {len(self.stats_connections)}")
        
        # Enviar dados iniciais
        await self._send_initial_data(websocket, "stats")
    
    def disconnect_dashboard(self, websocket: WebSocket):
        """Desconecta um cliente do dashboard"""
        self.dashboard_connections.discard(websocket)
        logger.info(f"📊 Dashboard desconectado. Total: {len(self.dashboard_connections)}")
    
    def disconnect_monitoring(self, websocket: WebSocket):
        """Desconecta um cliente do monitoramento"""
        self.monitoring_connections.discard(websocket)
        logger.info(f"🔍 Monitoramento desconectado. Total: {len(self.monitoring_connections)}")
    
    def disconnect_calls(self, websocket: WebSocket):
        """Desconecta um cliente do monitoramento de chamadas"""
        self.calls_connections.discard(websocket)
        logger.info(f"📞 Monitoramento de chamadas desconectado. Total: {len(self.calls_connections)}")
    
    def disconnect_stats(self, websocket: WebSocket):
        """Desconecta um cliente das estatísticas"""
        self.stats_connections.discard(websocket)
        logger.info(f"📈 Estatísticas desconectadas. Total: {len(self.stats_connections)}")
    
    async def _send_initial_data(self, websocket: WebSocket, connection_type: str):
        """Envia dados iniciais para uma nova conexão"""
        try:
            if connection_type == "dashboard":
                data = await self._get_dashboard_data()
                await websocket.send_text(json.dumps({
                    "type": "dashboard_update",
                    "data": data,
                    "timestamp": time.time()
                }))
            
            elif connection_type == "monitoring":
                data = await self._get_monitoring_data()
                await websocket.send_text(json.dumps({
                    "type": "monitoring_update",
                    "data": data,
                    "timestamp": time.time()
                }))
            
            elif connection_type == "calls":
                data = await self._get_calls_data()
                await websocket.send_text(json.dumps({
                    "type": "calls_update",
                    "data": data,
                    "timestamp": time.time()
                }))
            
            elif connection_type == "stats":
                data = await self._get_stats_data()
                await websocket.send_text(json.dumps({
                    "type": "stats_update",
                    "data": data,
                    "timestamp": time.time()
                }))
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar dados iniciais: {str(e)}")
    
    async def _broadcast_loop(self):
        """Loop principal de broadcasting"""
        logger.info("🔄 Iniciando loop de broadcasting WebSocket")
        
        while self.running:
            try:
                # Coletar dados atuais
                dashboard_data = await self._get_dashboard_data()
                monitoring_data = await self._get_monitoring_data()
                calls_data = await self._get_calls_data()
                stats_data = await self._get_stats_data()
                
                # Broadcast para cada tipo de conexão
                await self._broadcast_to_connections(
                    self.dashboard_connections,
                    "dashboard_update",
                    dashboard_data
                )
                
                await self._broadcast_to_connections(
                    self.monitoring_connections,
                    "monitoring_update",
                    monitoring_data
                )
                
                await self._broadcast_to_connections(
                    self.calls_connections,
                    "calls_update",
                    calls_data
                )
                
                await self._broadcast_to_connections(
                    self.stats_connections,
                    "stats_update",
                    stats_data
                )
                
                # Aguardar antes do próximo broadcast
                await asyncio.sleep(2)  # 2 segundos
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop de broadcasting: {str(e)}")
                await asyncio.sleep(5)
    
    async def _broadcast_to_connections(self, connections: Set[WebSocket], message_type: str, data: dict):
        """Envia dados para um conjunto de conexões"""
        if not connections:
            return
        
        message = json.dumps({
            "type": message_type,
            "data": data,
            "timestamp": time.time()
        })
        
        # Lista de conexões para remover (desconectadas)
        to_remove = []
        
        for websocket in connections.copy():
            try:
                await websocket.send_text(message)
            except WebSocketDisconnect:
                to_remove.append(websocket)
            except Exception as e:
                logger.error(f"❌ Erro ao enviar para WebSocket: {str(e)}")
                to_remove.append(websocket)
        
        # Remover conexões mortas
        for websocket in to_remove:
            connections.discard(websocket)
    
    async def _get_dashboard_data(self) -> dict:
        """Coleta dados para o dashboard"""
        try:
            worker = get_dialer_worker()
            predictive = get_predictive_dialer()
            
            # Status do worker
            worker_status = worker.get_status()
            
            # Estatísticas do algoritmo preditivo
            predictive_stats = predictive.get_current_stats()
            
            # Chamadas ativas do Asterisk
            active_calls = await asterisk_ami.get_active_calls()
            
            # Preparar dados do dashboard
            dashboard_data = {
                "system_status": {
                    "dialer_running": worker.running,
                    "asterisk_connected": asterisk_ami.connected,
                    "total_connections": (
                        len(self.dashboard_connections) + 
                        len(self.monitoring_connections) + 
                        len(self.calls_connections) + 
                        len(self.stats_connections)
                    )
                },
                "call_metrics": {
                    "active_calls": len(active_calls),
                    "calls_in_queue": worker_status["queue_size"],
                    "active_campaigns": worker_status["active_campaigns"],
                    "current_cps": predictive_stats["current_cps"],
                    "available_agents": predictive_stats["available_agents"]
                },
                "performance": {
                    "total_calls": predictive_stats["total_calls"],
                    "answered_calls": predictive_stats["answered_calls"],
                    "answer_rate": predictive_stats["answer_rate"],
                    "connection_rate": predictive_stats["connection_rate"],
                    "average_call_duration": predictive_stats["average_call_duration"]
                },
                "campaigns": []
            }
            
            # Adicionar informações das campanhas ativas
            for campaign_id, config in worker.active_campaigns.items():
                dashboard_data["campaigns"].append({
                    "id": campaign_id,
                    "name": config.name,
                    "status": "active" if config.active else "paused",
                    "cli_number": config.cli_number
                })
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados do dashboard: {str(e)}")
            return {"error": str(e)}
    
    async def _get_monitoring_data(self) -> dict:
        """Coleta dados para monitoramento detalhado"""
        try:
            worker = get_dialer_worker()
            predictive = get_predictive_dialer()
            
            return {
                "worker_status": worker.get_status(),
                "predictive_stats": predictive.get_current_stats(),
                "hourly_stats": predictive.get_hourly_stats(),
                "asterisk_status": {
                    "connected": asterisk_ami.connected,
                    "authenticated": asterisk_ami.authenticated,
                    "host": asterisk_ami.host,
                    "port": asterisk_ami.port
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados de monitoramento: {str(e)}")
            return {"error": str(e)}
    
    async def _get_calls_data(self) -> dict:
        """Coleta dados das chamadas ativas"""
        try:
            active_calls = await asterisk_ami.get_active_calls()
            
            calls_data = []
            for call in active_calls:
                calls_data.append({
                    "call_id": call.call_id,
                    "phone_number": call.phone_number,
                    "campaign_id": call.campaign_id,
                    "status": call.status.value,
                    "duration": int(time.time() - call.timestamp),
                    "dtmf_pressed": call.dtmf_pressed,
                    "transferred": call.transferred
                })
            
            return {
                "active_calls": calls_data,
                "total_active": len(calls_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados de chamadas: {str(e)}")
            return {"error": str(e)}
    
    async def _get_stats_data(self) -> dict:
        """Coleta estatísticas detalhadas"""
        try:
            predictive = get_predictive_dialer()
            
            current_stats = predictive.get_current_stats()
            hourly_stats = predictive.get_hourly_stats()
            
            # Calcular estatísticas dos últimos 30 minutos
            recent_metrics = predictive._get_recent_metrics()
            
            return {
                "current": current_stats,
                "hourly": hourly_stats,
                "recent": {
                    "total_calls": recent_metrics.total_calls,
                    "answered_calls": recent_metrics.answered_calls,
                    "busy_calls": recent_metrics.busy_calls,
                    "no_answer_calls": recent_metrics.no_answer_calls,
                    "failed_calls": recent_metrics.failed_calls,
                    "answer_rate": recent_metrics.answer_rate,
                    "connection_rate": recent_metrics.connection_rate,
                    "average_call_duration": recent_metrics.average_call_duration
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar estatísticas: {str(e)}")
            return {"error": str(e)}
    
    async def broadcast_event(self, event_type: str, data: dict):
        """Transmite um evento específico para todas as conexões relevantes"""
        try:
            message = json.dumps({
                "type": "event",
                "event_type": event_type,
                "data": data,
                "timestamp": time.time()
            })
            
            # Enviar para todas as conexões
            all_connections = (
                self.dashboard_connections |
                self.monitoring_connections |
                self.calls_connections |
                self.stats_connections
            )
            
            to_remove = []
            for websocket in all_connections:
                try:
                    await websocket.send_text(message)
                except:
                    to_remove.append(websocket)
            
            # Limpar conexões mortas
            for websocket in to_remove:
                self.dashboard_connections.discard(websocket)
                self.monitoring_connections.discard(websocket)
                self.calls_connections.discard(websocket)
                self.stats_connections.discard(websocket)
                
        except Exception as e:
            logger.error(f"❌ Erro ao transmitir evento: {str(e)}")

# Instância global do gerenciador WebSocket
websocket_manager = WebSocketManager()

def get_websocket_manager() -> WebSocketManager:
    """Retorna instância do gerenciador WebSocket"""
    return websocket_manager 