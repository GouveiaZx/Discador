"""
Rotas para monitoramento no formato Asterisk.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import asyncio
import json

from app.database import obtener_sesion
from app.services.asterisk_monitoring_service import AsteriskMonitoringService
from app.utils.logger import logger

router = APIRouter(prefix="/asterisk-monitoring", tags=["Monitoramento Asterisk"])


@router.get("/llamadas")
def obter_llamadas_formato_asterisk(
    incluir_finalizadas: bool = Query(False, description="Incluir chamadas finalizadas"),
    limite_horas: int = Query(24, ge=1, le=168, description="Limite de horas para buscar"),
    db: Session = Depends(obtener_sesion)
):
    """
    Obtém chamadas no formato Asterisk.
    
    **Formato de saída:** SIP/cliente/extensao,prioridade,flags numero duracao
    
    **Exemplo:** SIP/liza/7508,35,tTr 8323870217 00:00:47
    
    **Flags disponíveis:**
    - **t**: Transferível
    - **T**: Permite transfer pelo chamado
    - **r**: Ring back tone
    - **g**: Continue no dialplan em caso de busy/congestion
    - **h**: Hang up após bridge
    - **c**: Caller ID presente
    - **n**: No answer
    
    **Prioridades:**
    - 1-10: Chamadas sendo iniciadas
    - 11-20: Chamadas conectando/em progresso
    - 21-30: Chamadas conectadas
    - 31+: Chamadas finalizadas/com erro
    """
    try:
        service = AsteriskMonitoringService(db)
        llamadas = service.obter_llamadas_formato_asterisk(
            incluir_finalizadas=incluir_finalizadas,
            limite_horas=limite_horas
        )
        
        return {
            "status": "success",
            "formato": "asterisk_compatible",
            "total_llamadas": len(llamadas),
            "llamadas": llamadas,
            "timestamp": service.obter_estatisticas_tempo_real()['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter chamadas formato Asterisk: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter chamadas"
        )


@router.get("/stats")
def obter_estatisticas_tempo_real(db: Session = Depends(obtener_sesion)):
    """
    Obtém estatísticas em tempo real no formato compatível com Asterisk.
    
    **Inclui:**
    - Chamadas ativas por estado
    - Trunks online/offline
    - Canais SIP em uso
    - Taxa de sucesso do dia
    - Versão simulada do Asterisk
    
    **Atualização:** Dados atualizados em tempo real
    """
    try:
        service = AsteriskMonitoringService(db)
        stats = service.obter_estatisticas_tempo_real()
        
        return {
            "status": "success",
            "estadisticas": stats,
            "formato": "asterisk_monitoring"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas tempo real: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter estatísticas"
        )


@router.get("/canais-sip")
def obter_canais_sip_ativos(db: Session = Depends(obtener_sesion)):
    """
    Lista canais SIP ativos no formato Asterisk.
    
    **Formato similar ao comando:** `asterisk -rx "sip show channels"`
    
    **Inclui para cada canal:**
    - Nome do canal (SIP/cliente/extensao)
    - Estado atual (Up, Down, Ring, etc.)
    - Número de destino
    - Duração da chamada
    - Caller ID
    - Contexto e aplicação
    - Unique ID único
    """
    try:
        service = AsteriskMonitoringService(db)
        canais = service.obter_canais_sip_ativos()
        
        return {
            "status": "success",
            "total_canais": len(canais),
            "canais_ativos": canais,
            "formato": "sip_show_channels",
            "timestamp": service.obter_estatisticas_tempo_real()['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter canais SIP: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter canais SIP"
        )


@router.post("/parsear-linha")
def parsear_linha_asterisk(
    linha_asterisk: str = Query(..., description="Linha no formato Asterisk para parsear"),
    db: Session = Depends(obtener_sesion)
):
    """
    Parseia uma linha no formato Asterisk.
    
    **Formato esperado:** SIP/cliente/extensao,prioridade,flags numero duracao
    
    **Exemplo de entrada:** SIP/liza/7508,35,tTr 8323870217 00:00:47
    
    **Retorna:** Dados estruturados extraídos da linha
    """
    try:
        service = AsteriskMonitoringService(db)
        resultado = service.parsear_formato_asterisk(linha_asterisk)
        
        if not resultado:
            raise HTTPException(
                status_code=400,
                detail="Formato de linha inválido. Use: SIP/cliente/extensao,prioridade,flags numero duracao"
            )
        
        return {
            "status": "success",
            "dados_parseados": resultado,
            "valido": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao parsear linha Asterisk: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao parsear linha"
        )


@router.get("/simular-evento/{tipo_evento}")
def simular_evento_asterisk(
    tipo_evento: str,
    llamada_id: Optional[int] = Query(None, description="ID da chamada para simular evento"),
    db: Session = Depends(obtener_sesion)
):
    """
    Simula eventos do Asterisk para teste.
    
    **Tipos de evento disponíveis:**
    - **NewChannel**: Novo canal criado
    - **Dial**: Início de discagem
    - **DialEnd**: Fim da discagem
    - **Hangup**: Desligamento da chamada
    
    **Uso:** Para testes de integração com sistemas que esperam eventos do Asterisk
    """
    try:
        service = AsteriskMonitoringService(db)
        evento = service.simular_evento_asterisk(tipo_evento, llamada_id)
        
        return {
            "status": "success",
            "evento_simulado": evento,
            "tipo": tipo_evento,
            "formato": "asterisk_manager_interface"
        }
        
    except Exception as e:
        logger.error(f"Erro ao simular evento Asterisk: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao simular evento"
        )


# WebSocket para monitoramento em tempo real
class ConnectionManager:
    """Gerenciador de conexões WebSocket."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Remover conexões mortas
                self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws/monitoring")
async def websocket_monitoring(websocket: WebSocket, db: Session = Depends(obtener_sesion)):
    """
    WebSocket para monitoramento em tempo real no formato Asterisk.
    
    **Envia a cada 5 segundos:**
    - Lista de chamadas ativas no formato Asterisk
    - Estatísticas em tempo real
    - Canais SIP ativos
    - Eventos de mudança de estado
    
    **Formato de mensagem:**
    ```json
    {
        "tipo": "monitoring_update",
        "timestamp": "2024-01-01T12:00:00",
        "llamadas_activas": [...],
        "estadisticas": {...},
        "canais_sip": [...]
    }
    ```
    """
    await manager.connect(websocket)
    
    try:
        service = AsteriskMonitoringService(db)
        
        # Função callback para enviar dados via WebSocket
        async def enviar_dados_monitoring(dados):
            message = json.dumps({
                "tipo": "monitoring_update",
                **dados
            })
            await manager.send_personal_message(message, websocket)
        
        # Iniciar monitoramento contínuo
        await service.monitoramento_continuo(enviar_dados_monitoring)
        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Cliente WebSocket desconectado do monitoramento")
    except Exception as e:
        logger.error(f"Erro no WebSocket de monitoramento: {str(e)}")
        manager.disconnect(websocket)


@router.get("/dashboard")
def obter_dashboard_asterisk(db: Session = Depends(obtener_sesion)):
    """
    Dashboard completo no formato Asterisk.
    
    **Inclui tudo em uma única requisição:**
    - Chamadas ativas no formato Asterisk
    - Estatísticas em tempo real
    - Canais SIP ativos
    - Status dos trunks
    - Eventos recentes
    
    **Ideal para:** Dashboards que precisam de visão completa do sistema
    """
    try:
        service = AsteriskMonitoringService(db)
        
        # Obter todos os dados
        llamadas_formato = service.obter_llamadas_formato_asterisk()
        stats = service.obter_estatisticas_tempo_real()
        canais_sip = service.obter_canais_sip_ativos()
        
        # Simular alguns eventos recentes
        eventos_recentes = [
            service.simular_evento_asterisk('NewChannel'),
            service.simular_evento_asterisk('Dial'),
            service.simular_evento_asterisk('DialEnd')
        ]
        
        return {
            "status": "success",
            "dashboard": {
                "llamadas_activas": llamadas_formato,
                "estadisticas": stats,
                "canais_sip": canais_sip,
                "eventos_recientes": eventos_recentes,
                "formato": "asterisk_dashboard",
                "ultima_atualizacao": stats['timestamp']
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter dashboard Asterisk: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter dashboard"
        )


@router.get("/export/asterisk-format")
def exportar_formato_asterisk(
    incluir_finalizadas: bool = Query(False),
    limite_horas: int = Query(24, ge=1, le=168),
    formato_saida: str = Query("json", pattern="^(json|text|csv)$"),
    db: Session = Depends(obtener_sesion)
):
    """
    Exporta dados no formato Asterisk.
    
    **Formatos de saída:**
    - **json**: Dados estruturados JSON
    - **text**: Formato texto puro (como saída do Asterisk CLI)
    - **csv**: Arquivo CSV para análise
    
    **Uso:** Para integração com sistemas externos ou análise de dados
    """
    try:
        service = AsteriskMonitoringService(db)
        llamadas = service.obter_llamadas_formato_asterisk(
            incluir_finalizadas=incluir_finalizadas,
            limite_horas=limite_horas
        )
        
        if formato_saida == "text":
            # Formato texto puro
            linhas = []
            linhas.append("=== CHAMADAS ATIVAS - FORMATO ASTERISK ===")
            linhas.append(f"Total: {len(llamadas)} chamadas")
            linhas.append("")
            
            for llamada in llamadas:
                linhas.append(llamada['formato_asterisk'])
            
            return {
                "status": "success",
                "formato": "text",
                "conteudo": "\n".join(linhas)
            }
        
        elif formato_saida == "csv":
            # Formato CSV
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Cabeçalho
            writer.writerow([
                'Canal_SIP', 'Cliente', 'Extensao', 'Prioridade', 'Flags',
                'Numero_Destino', 'Duracao', 'Estado', 'Trunk_ID'
            ])
            
            # Dados
            for llamada in llamadas:
                writer.writerow([
                    llamada['canal_sip'],
                    llamada['cliente'],
                    llamada['extensao'],
                    llamada['prioridade'],
                    llamada['flags'],
                    llamada['numero_destino'],
                    llamada['duracao'],
                    llamada['estado'],
                    llamada['trunk_id']
                ])
            
            return {
                "status": "success",
                "formato": "csv",
                "conteudo": output.getvalue()
            }
        
        # Formato JSON (padrão)
        return {
            "status": "success",
            "formato": "json",
            "total_llamadas": len(llamadas),
            "llamadas": llamadas,
            "metadata": {
                "incluir_finalizadas": incluir_finalizadas,
                "limite_horas": limite_horas,
                "timestamp_export": service.obter_estatisticas_tempo_real()['timestamp']
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao exportar formato Asterisk: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao exportar dados"
        ) 