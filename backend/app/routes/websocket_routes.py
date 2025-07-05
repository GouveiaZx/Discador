#!/usr/bin/env python3
"""
Rotas WebSocket para monitoramento em tempo real
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from ..services.realtime_service import get_realtime_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket para dashboard em tempo real
    """
    realtime_service = get_realtime_service()
    
    try:
        await realtime_service.connect(websocket)
        
        while True:
            # Manter conexão viva
            data = await websocket.receive_text()
            
            # Processar comandos se necessário
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        logger.info("📊 Cliente dashboard desconectado")
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket dashboard: {str(e)}")
    finally:
        realtime_service.disconnect(websocket)

@router.websocket("/ws/monitoring")
async def websocket_monitoring(websocket: WebSocket):
    """
    WebSocket para monitoramento detalhado
    """
    realtime_service = get_realtime_service()
    
    try:
        await realtime_service.connect(websocket)
        
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        logger.info("🔍 Cliente monitoramento desconectado")
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket monitoramento: {str(e)}")
    finally:
        realtime_service.disconnect(websocket)

@router.websocket("/ws/calls")
async def websocket_calls(websocket: WebSocket):
    """
    WebSocket para monitoramento de chamadas
    """
    realtime_service = get_realtime_service()
    
    try:
        await realtime_service.connect(websocket)
        
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        logger.info("📞 Cliente chamadas desconectado")
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket chamadas: {str(e)}")
    finally:
        realtime_service.disconnect(websocket)

@router.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    """
    WebSocket para estatísticas em tempo real
    """
    realtime_service = get_realtime_service()
    
    try:
        await realtime_service.connect(websocket)
        
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        logger.info("📈 Cliente estatísticas desconectado")
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket estatísticas: {str(e)}")
    finally:
        realtime_service.disconnect(websocket) 