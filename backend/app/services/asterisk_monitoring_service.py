"""
Serviço de monitoramento no formato Asterisk.
Monitora chamadas em tempo real no formato: SIP/cliente/extensao,prioridade,flags numero duracao
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import re
import random
import asyncio

from app.models.llamada import Llamada, EstadoLlamada
from app.models.trunk import Trunk
from app.utils.logger import logger


class AsteriskMonitoringService:
    """Serviço para monitoramento em formato Asterisk."""
    
    def __init__(self, db: Session):
        self.db = db
        self.llamadas_activas = {}  # Cache de chamadas ativas
        self.formato_asterisk_regex = re.compile(
            r'^SIP/([^/]+)/(\d+),(\d+),([a-zA-Z]*)\s+(\d+)\s+(\d{2}:\d{2}:\d{2})$'
        )
    
    def obter_llamadas_formato_asterisk(
        self,
        incluir_finalizadas: bool = False,
        limite_horas: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Obtém chamadas no formato Asterisk.
        
        Formato: SIP/cliente/extensao,prioridade,flags numero duracao
        Exemplo: SIP/liza/7508,35,tTr 8323870217 00:00:47
        """
        
        # Filtrar chamadas por período
        data_limite = datetime.now() - timedelta(hours=limite_horas)
        
        query = self.db.query(Llamada).filter(
            Llamada.fecha_inicio >= data_limite
        )
        
        if not incluir_finalizadas:
            query = query.filter(
                Llamada.estado.in_([
                    EstadoLlamada.INICIADA,
                    EstadoLlamada.EN_PROGRESO,
                    EstadoLlamada.CONECTADA,
                    EstadoLlamada.TRANSFERIDA
                ])
            )
        
        llamadas = query.order_by(Llamada.fecha_inicio.desc()).all()
        
        resultado = []
        for llamada in llamadas:
            formato_asterisk = self._convertir_a_formato_asterisk(llamada)
            if formato_asterisk:
                resultado.append(formato_asterisk)
        
        return resultado
    
    def _convertir_a_formato_asterisk(self, llamada: Llamada) -> Optional[Dict[str, Any]]:
        """Converte uma chamada para o formato Asterisk."""
        
        try:
            # Obter informações do trunk
            trunk_info = self._obter_info_trunk(llamada.trunk_id) if llamada.trunk_id else None
            
            # Gerar nome do cliente (baseado no trunk ou número)
            cliente = self._gerar_nome_cliente(trunk_info, llamada.numero_destino)
            
            # Gerar extensão (baseado no ID da chamada)
            extensao = self._gerar_extensao(llamada.id)
            
            # Determinar prioridade baseada no estado
            prioridade = self._determinar_prioridade(llamada.estado)
            
            # Gerar flags baseadas no estado e configurações
            flags = self._gerar_flags(llamada)
            
            # Calcular duração
            duracao = self._calcular_duracao(llamada)
            
            # Montar string no formato Asterisk
            canal_sip = f"SIP/{cliente}/{extensao}"
            formato_completo = f"{canal_sip},{prioridade},{flags} {llamada.numero_destino} {duracao}"
            
            return {
                'id': llamada.id,
                'formato_asterisk': formato_completo,
                'canal_sip': canal_sip,
                'cliente': cliente,
                'extensao': extensao,
                'prioridade': prioridade,
                'flags': flags,
                'numero_destino': llamada.numero_destino,
                'duracao': duracao,
                'estado': llamada.estado.value,
                'fecha_inicio': llamada.fecha_inicio.isoformat(),
                'trunk_id': llamada.trunk_id,
                'campanha_id': llamada.campanha_id,
                'detalhes': {
                    'numero_origem': llamada.numero_origem,
                    'resultado': llamada.resultado,
                    'observaciones': llamada.observaciones
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao converter chamada {llamada.id} para formato Asterisk: {str(e)}")
            return None
    
    def _obter_info_trunk(self, trunk_id: int) -> Optional[Dict[str, Any]]:
        """Obtém informações do trunk."""
        
        trunk = self.db.query(Trunk).filter(Trunk.id == trunk_id).first()
        if trunk:
            return {
                'id': trunk.id,
                'nome': trunk.nome,
                'host': trunk.host,
                'porta': trunk.porta,
                'usuario': trunk.usuario
            }
        return None
    
    def _gerar_nome_cliente(
        self, 
        trunk_info: Optional[Dict[str, Any]], 
        numero_destino: str
    ) -> str:
        """Gera nome do cliente para o formato SIP."""
        
        if trunk_info:
            # Usar nome do trunk como base
            nome_base = trunk_info['nome'].lower()
            # Remover caracteres especiais
            nome_limpo = re.sub(r'[^a-z0-9]', '', nome_base)
            return nome_limpo[:10]  # Máximo 10 caracteres
        
        # Fallback: usar parte do número de destino
        apenas_numeros = re.sub(r'\D', '', numero_destino)
        if len(apenas_numeros) >= 4:
            return f"cli{apenas_numeros[-4:]}"
        
        return "default"
    
    def _gerar_extensao(self, llamada_id: int) -> str:
        """Gera extensão baseada no ID da chamada."""
        
        # Usar ID da chamada + offset para simular extensão
        base_extensao = 7000 + (llamada_id % 1000)
        return str(base_extensao)
    
    def _determinar_prioridade(self, estado: EstadoLlamada) -> int:
        """Determina prioridade baseada no estado da chamada."""
        
        prioridades = {
            EstadoLlamada.INICIADA: 1,
            EstadoLlamada.MARCANDO: 5,
            EstadoLlamada.CONECTANDO: 10,
            EstadoLlamada.EN_PROGRESO: 15,
            EstadoLlamada.CONECTADA: 20,
            EstadoLlamada.TRANSFERIDA: 25,
            EstadoLlamada.FINALIZADA: 30,
            EstadoLlamada.FALLIDA: 35,
            EstadoLlamada.OCUPADO: 40,
            EstadoLlamada.NO_CONTESTA: 45,
            EstadoLlamada.CANCELADA: 50
        }
        
        return prioridades.get(estado, 35)
    
    def _gerar_flags(self, llamada: Llamada) -> str:
        """Gera flags baseadas no estado e configurações da chamada."""
        
        flags = []
        
        # Flag 't' - Transferível
        if llamada.estado in [EstadoLlamada.CONECTADA, EstadoLlamada.EN_PROGRESO]:
            flags.append('t')
        
        # Flag 'T' - Permite transfer pelo chamado
        if llamada.estado == EstadoLlamada.CONECTADA:
            flags.append('T')
        
        # Flag 'r' - Ring back tone
        if llamada.estado in [EstadoLlamada.MARCANDO, EstadoLlamada.CONECTANDO]:
            flags.append('r')
        
        # Flag 'g' - Continue no dialplan em caso de busy/congestion
        if llamada.estado in [EstadoLlamada.OCUPADO, EstadoLlamada.FALLIDA]:
            flags.append('g')
        
        # Flag 'h' - Hang up após bridge
        if llamada.estado == EstadoLlamada.FINALIZADA:
            flags.append('h')
        
        # Flag 'c' - Caller ID
        if llamada.numero_origem:
            flags.append('c')
        
        # Flag 'n' - No answer
        if llamada.estado == EstadoLlamada.NO_CONTESTA:
            flags.append('n')
        
        return ''.join(sorted(set(flags)))
    
    def _calcular_duracao(self, llamada: Llamada) -> str:
        """Calcula duração da chamada no formato HH:MM:SS."""
        
        if llamada.fecha_fin:
            # Chamada finalizada
            duracao_segundos = int((llamada.fecha_fin - llamada.fecha_inicio).total_seconds())
        else:
            # Chamada em progresso
            duracao_segundos = int((datetime.now() - llamada.fecha_inicio).total_seconds())
        
        # Converter para formato HH:MM:SS
        horas = duracao_segundos // 3600
        minutos = (duracao_segundos % 3600) // 60
        segundos = duracao_segundos % 60
        
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    
    def obter_estatisticas_tempo_real(self) -> Dict[str, Any]:
        """Obtém estatísticas em tempo real no formato Asterisk."""
        
        agora = datetime.now()
        inicio_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Chamadas ativas
        llamadas_activas = self.db.query(Llamada).filter(
            Llamada.estado.in_([
                EstadoLlamada.INICIADA,
                EstadoLlamada.MARCANDO,
                EstadoLlamada.CONECTANDO,
                EstadoLlamada.EN_PROGRESO,
                EstadoLlamada.CONECTADA
            ])
        ).count()
        
        # Chamadas do dia
        llamadas_hoje = self.db.query(Llamada).filter(
            Llamada.fecha_inicio >= inicio_dia
        ).count()
        
        # Chamadas completadas hoje
        llamadas_completadas = self.db.query(Llamada).filter(
            Llamada.fecha_inicio >= inicio_dia,
            Llamada.estado == EstadoLlamada.FINALIZADA
        ).count()
        
        # Trunks ativos
        trunks_ativos = self.db.query(Trunk).filter(
            Trunk.ativo == True,
            Trunk.status_conexao == 'online'
        ).count()
        
        # Canais em uso
        canais_em_uso = self.db.query(func.sum(Trunk.canais_em_uso)).filter(
            Trunk.ativo == True
        ).scalar() or 0
        
        # Taxa de sucesso do dia
        taxa_sucesso = 0.0
        if llamadas_hoje > 0:
            taxa_sucesso = (llamadas_completadas / llamadas_hoje) * 100
        
        return {
            'timestamp': agora.isoformat(),
            'llamadas_activas': llamadas_activas,
            'llamadas_hoje': llamadas_hoje,
            'llamadas_completadas': llamadas_completadas,
            'trunks_ativos': trunks_ativos,
            'canais_em_uso': int(canais_em_uso),
            'taxa_sucesso': round(taxa_sucesso, 2),
            'formato_asterisk_ativo': True,
            'versao_asterisk_simulada': '18.0.0'
        }
    
    def parsear_formato_asterisk(self, linha_asterisk: str) -> Optional[Dict[str, Any]]:
        """
        Parseia uma linha no formato Asterisk.
        
        Formato esperado: SIP/cliente/extensao,prioridade,flags numero duracao
        """
        
        match = self.formato_asterisk_regex.match(linha_asterisk.strip())
        if not match:
            return None
        
        cliente, extensao, prioridade, flags, numero, duracao = match.groups()
        
        return {
            'canal_sip': f"SIP/{cliente}/{extensao}",
            'cliente': cliente,
            'extensao': int(extensao),
            'prioridade': int(prioridade),
            'flags': flags,
            'numero_destino': numero,
            'duracao': duracao,
            'linha_original': linha_asterisk
        }
    
    def simular_evento_asterisk(
        self, 
        tipo_evento: str, 
        llamada_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Simula eventos do Asterisk para teste."""
        
        eventos_asterisk = {
            'NewChannel': {
                'Event': 'Newchannel',
                'Privilege': 'call,all',
                'Channel': 'SIP/trunk-00000001',
                'ChannelState': '0',
                'ChannelStateDesc': 'Down',
                'CallerIDNum': '',
                'CallerIDName': '',
                'ConnectedLineNum': '',
                'ConnectedLineName': '',
                'Language': 'en',
                'Context': 'outbound',
                'Exten': '',
                'Priority': '1',
                'Uniqueid': f'{datetime.now().timestamp():.0f}.1',
                'Linkedid': f'{datetime.now().timestamp():.0f}.1'
            },
            'Dial': {
                'Event': 'Dial',
                'Privilege': 'call,all',
                'SubEvent': 'Begin',
                'Channel': 'SIP/trunk-00000001',
                'Destination': 'SIP/provider-00000002',
                'CallerIDNum': '1234567890',
                'CallerIDName': 'Discador',
                'ConnectedLineNum': '',
                'ConnectedLineName': '',
                'UniqueID': f'{datetime.now().timestamp():.0f}.1',
                'DestUniqueID': f'{datetime.now().timestamp():.0f}.2',
                'Dialstring': '8323870217'
            },
            'DialEnd': {
                'Event': 'DialEnd',
                'Privilege': 'call,all',
                'Channel': 'SIP/trunk-00000001',
                'UniqueID': f'{datetime.now().timestamp():.0f}.1',
                'CallerIDNum': '1234567890',
                'CallerIDName': 'Discador',
                'ConnectedLineNum': '8323870217',
                'ConnectedLineName': '',
                'DialStatus': 'ANSWER'
            },
            'Hangup': {
                'Event': 'Hangup',
                'Privilege': 'call,all',
                'Channel': 'SIP/trunk-00000001',
                'UniqueID': f'{datetime.now().timestamp():.0f}.1',
                'CallerIDNum': '1234567890',
                'CallerIDName': 'Discador',
                'ConnectedLineNum': '8323870217',
                'ConnectedLineName': '',
                'Cause': '16',
                'Cause-txt': 'Normal Clearing'
            }
        }
        
        evento = eventos_asterisk.get(tipo_evento, eventos_asterisk['NewChannel'])
        evento['Timestamp'] = datetime.now().isoformat()
        
        if llamada_id:
            evento['CustomField_LlamadaID'] = llamada_id
        
        return evento
    
    def obter_canais_sip_ativos(self) -> List[Dict[str, Any]]:
        """Obtém lista de canais SIP ativos no formato Asterisk."""
        
        llamadas_activas = self.db.query(Llamada).filter(
            Llamada.estado.in_([
                EstadoLlamada.INICIADA,
                EstadoLlamada.MARCANDO,
                EstadoLlamada.CONECTANDO,
                EstadoLlamada.EN_PROGRESO,
                EstadoLlamada.CONECTADA
            ])
        ).all()
        
        canais = []
        for llamada in llamadas_activas:
            canal_info = self._convertir_a_formato_asterisk(llamada)
            if canal_info:
                canais.append({
                    'canal': canal_info['canal_sip'],
                    'estado': self._mapear_estado_asterisk(llamada.estado),
                    'numero_destino': llamada.numero_destino,
                    'duracao': canal_info['duracao'],
                    'caller_id': llamada.numero_origem or 'Unknown',
                    'contexto': 'outbound',
                    'aplicacao': 'Dial',
                    'dados': f"SIP/provider/{llamada.numero_destino}",
                    'uniqueid': f"{int(llamada.fecha_inicio.timestamp())}.{llamada.id}"
                })
        
        return canais
    
    def _mapear_estado_asterisk(self, estado: EstadoLlamada) -> str:
        """Mapeia estados internos para estados do Asterisk."""
        
        mapeamento = {
            EstadoLlamada.INICIADA: 'Down',
            EstadoLlamada.MARCANDO: 'Dialing',
            EstadoLlamada.CONECTANDO: 'Ring',
            EstadoLlamada.EN_PROGRESO: 'Ringing',
            EstadoLlamada.CONECTADA: 'Up',
            EstadoLlamada.TRANSFERIDA: 'Up',
            EstadoLlamada.FINALIZADA: 'Down',
            EstadoLlamada.FALLIDA: 'Down',
            EstadoLlamada.OCUPADO: 'Busy',
            EstadoLlamada.NO_CONTESTA: 'Down',
            EstadoLlamada.CANCELADA: 'Down'
        }
        
        return mapeamento.get(estado, 'Unknown')
    
    async def monitoramento_continuo(self, callback_func=None):
        """Executa monitoramento contínuo das chamadas."""
        
        logger.info("Iniciando monitoramento contínuo no formato Asterisk")
        
        while True:
            try:
                # Obter chamadas no formato Asterisk
                llamadas_formato = self.obter_llamadas_formato_asterisk()
                
                # Obter estatísticas
                stats = self.obter_estatisticas_tempo_real()
                
                # Dados de monitoramento
                dados_monitoring = {
                    'timestamp': datetime.now().isoformat(),
                    'llamadas_activas': llamadas_formato,
                    'estadisticas': stats,
                    'canais_sip': self.obter_canais_sip_ativos(),
                    'formato': 'asterisk_compatible'
                }
                
                # Executar callback se fornecido
                if callback_func:
                    await callback_func(dados_monitoring)
                
                # Log das estatísticas principais
                logger.debug(f"Monitoramento: {stats['llamadas_activas']} chamadas ativas, "
                           f"{stats['canais_em_uso']} canais em uso")
                
                # Aguardar antes da próxima verificação
                await asyncio.sleep(5)  # Atualizar a cada 5 segundos
                
            except Exception as e:
                logger.error(f"Erro no monitoramento contínuo: {str(e)}")
                await asyncio.sleep(10)  # Aguardar mais tempo em caso de erro 