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

logger = logging.getLogger(__name__)

class RealtimeService:
    """
    Serviço de tempo real para broadcasting de dados via WebSocket
    """
    
    def __init__(self):
        # Conexões ativas
        self.connections: Set[WebSocket] = set()
        
        # Estado dos dados
        self.last_data = {}
        
        # Task de broadcasting
        self.broadcast_task = None
        self.running = False
    
    def start(self):
        """Inicia o serviço"""
        if not self.running:
            self.running = True
            self.broadcast_task = asyncio.create_task(self._broadcast_loop())
            logger.info("📡 Serviço WebSocket iniciado")
    
    def stop(self):
        """Para o serviço"""
        self.running = False
        if self.broadcast_task:
            self.broadcast_task.cancel()
        logger.info("📡 Serviço WebSocket parado")
    
    async def connect(self, websocket: WebSocket):
        """Conecta um cliente"""
        await websocket.accept()
        self.connections.add(websocket)
        logger.info(f"📡 Cliente conectado. Total: {len(self.connections)}")
        
        # Enviar dados iniciais
        await self._send_initial_data(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Desconecta um cliente"""
        self.connections.discard(websocket)
        logger.info(f"📡 Cliente desconectado. Total: {len(self.connections)}")
    
    async def _send_initial_data(self, websocket: WebSocket):
        """Envia dados iniciais"""
        try:
            data = await self._get_current_data()
            await websocket.send_text(json.dumps({
                "type": "initial_data",
                "data": data,
                "timestamp": time.time()
            }))
        except Exception as e:
            logger.error(f"❌ Erro ao enviar dados iniciais: {str(e)}")
    
    async def _broadcast_loop(self):
        """Loop principal de broadcasting"""
        logger.info("🔄 Iniciando loop de broadcasting")
        
        while self.running:
            try:
                # Coletar dados atuais
                data = await self._get_current_data()
                
                # Broadcast para todas as conexões
                await self._broadcast_data(data)
                
                # Aguardar antes do próximo broadcast
                await asyncio.sleep(2)  # 2 segundos
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop de broadcasting: {str(e)}")
                await asyncio.sleep(5)
    
    async def _broadcast_data(self, data: dict):
        """Transmite dados para todas as conexões"""
        if not self.connections:
            return
        
        message = json.dumps({
            "type": "data_update",
            "data": data,
            "timestamp": time.time()
        })
        
        # Lista de conexões para remover
        to_remove = []
        
        for websocket in self.connections.copy():
            try:
                await websocket.send_text(message)
            except WebSocketDisconnect:
                to_remove.append(websocket)
            except Exception as e:
                logger.error(f"❌ Erro ao enviar WebSocket: {str(e)}")
                to_remove.append(websocket)
        
        # Remover conexões mortas
        for websocket in to_remove:
            self.connections.discard(websocket)
    
    async def _get_current_data(self) -> dict:
        """Coleta dados atuais do sistema"""
        try:
            # Dados simulados por enquanto
            return {
                "system_status": {
                    "dialer_running": True,
                    "asterisk_connected": True,
                    "total_connections": len(self.connections)
                },
                "call_metrics": {
                    "active_calls": 0,
                    "calls_in_queue": 0,
                    "active_campaigns": 0,
                    "current_cps": 1.0,
                    "available_agents": 5
                },
                "performance": {
                    "total_calls": 0,
                    "answered_calls": 0,
                    "answer_rate": 0.0,
                    "connection_rate": 0.0,
                    "average_call_duration": 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados: {str(e)}")
            return {"error": str(e)}
    
    async def broadcast_event(self, event_type: str, data: dict):
        """Transmite um evento específico"""
        try:
            message = json.dumps({
                "type": "event",
                "event_type": event_type,
                "data": data,
                "timestamp": time.time()
            })
            
            to_remove = []
            for websocket in self.connections.copy():
                try:
                    await websocket.send_text(message)
                except:
                    to_remove.append(websocket)
            
            # Limpar conexões mortas
            for websocket in to_remove:
                self.connections.discard(websocket)
                
        except Exception as e:
            logger.error(f"❌ Erro ao transmitir evento: {str(e)}")

# Instância global
realtime_service = RealtimeService()

def get_realtime_service() -> RealtimeService:
    """Retorna instância do serviço"""
    return realtime_service 