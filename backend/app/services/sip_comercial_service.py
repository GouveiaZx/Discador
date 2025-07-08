"""
Serviço SIP Comercial para Discado Preditivo
Suporte a múltiplos provedores SIP comerciais
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid
import hashlib
import time
import socket
import ssl

# Configurar logging
logger = logging.getLogger(__name__)

class TipoProveedorSIP(Enum):
    """Tipos de provedores SIP suportados"""
    GENERIC = "generic"
    TWILIO = "twilio"
    VONAGE = "vonage"
    BANDWIDTH = "bandwidth"
    TELNYX = "telnyx"
    PLIVO = "plivo"
    SIGNALWIRE = "signalwire"
    ASTERISK_SIP = "asterisk_sip"
    FREESWITCH_SIP = "freeswitch_sip"

class ProtocoloSIP(Enum):
    """Protocolos SIP suportados"""
    SIP_UDP = "sip_udp"
    SIP_TCP = "sip_tcp"
    SIP_TLS = "sip_tls"
    SIP_WSS = "sip_wss"
    WEBRTC = "webrtc"

class EstadoRegistro(Enum):
    """Estados de registro SIP"""
    REGISTRANDO = "registrando"
    REGISTRADO = "registrado"
    FALLO_REGISTRO = "fallo_registro"
    DESREGISTRADO = "desregistrado"
    EXPIRADO = "expirado"

class CalidadLlamada(Enum):
    """Níveis de qualidade de chamada"""
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    CRITICA = "critica"

@dataclass
class ConfiguracionProveedorSIP:
    """Configuração de um provedor SIP"""
    nombre: str
    tipo: TipoProveedorSIP
    protocolo: ProtocoloSIP
    servidor_sip: str
    puerto: int
    usuario: str
    password: str
    dominio: str
    proxy_outbound: Optional[str] = None
    registrar: Optional[str] = None
    auth_username: Optional[str] = None
    display_name: Optional[str] = None
    contact_uri: Optional[str] = None
    expires: int = 3600
    keep_alive: bool = True
    habilitar_stun: bool = False
    servidor_stun: Optional[str] = None
    codecs_audio: List[str] = field(default_factory=lambda: ["PCMU", "PCMA", "G729"])
    max_llamadas_simultaneas: int = 50
    timeout_invitacion: int = 30
    timeout_registro: int = 60
    calidad_minima: CalidadLlamada = CalidadLlamada.MEDIA
    costo_por_minuto: float = 0.0
    moneda: str = "USD"
    zona_horaria: str = "UTC"
    activo: bool = True

@dataclass
class LlamadaSIP:
    """Representación de una llamada SIP"""
    call_id: str
    numero_origen: str
    numero_destino: str
    provedor: str
    estado: str
    fecha_inicio: datetime
    fecha_respuesta: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    duracion: float = 0.0
    costo: float = 0.0
    calidad: Optional[CalidadLlamada] = None
    codec_usado: Optional[str] = None
    ip_remota: Optional[str] = None
    causa_finalizacion: Optional[str] = None
    logs_sip: List[Dict[str, Any]] = field(default_factory=list)
    metricas: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricasProvedor:
    """Métricas de un provedor SIP"""
    nombre_provedor: str
    llamadas_exitosas: int = 0
    llamadas_fallidas: int = 0
    tiempo_respuesta_promedio: float = 0.0
    calidad_promedio: float = 0.0
    costo_total: float = 0.0
    uptime: float = 100.0
    ultima_actualizacion: datetime = field(default_factory=datetime.now)

class SIPComercialService:
    """Serviço principal para SIP comercial"""
    
    def __init__(self):
        self.provedores: Dict[str, ConfiguracionProveedorSIP] = {}
        self.llamadas_activas: Dict[str, LlamadaSIP] = {}
        self.registros_sip: Dict[str, EstadoRegistro] = {}
        self.metricas_provedores: Dict[str, MetricasProvedor] = {}
        self.algoritmo_enrutamiento = "round_robin"  # round_robin, least_cost, best_quality
        self.failover_habilitado = True
        self.conexiones_activas: Dict[str, Any] = {}
        
        self._inicializar_provedores_ejemplo()
    
    def _inicializar_provedores_ejemplo(self):
        """Inicializa provedores de exemplo para desenvolvimento"""
        provedores_ejemplo = [
            ConfiguracionProveedorSIP(
                nombre="Twilio-Primary",
                tipo=TipoProveedorSIP.TWILIO,
                protocolo=ProtocoloSIP.SIP_TLS,
                servidor_sip="sip.twilio.com",
                puerto=5061,
                usuario="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                password="auth_token_here",
                dominio="sip.twilio.com",
                max_llamadas_simultaneas=100,
                costo_por_minuto=0.013,
                calidad_minima=CalidadLlamada.ALTA
            ),
            ConfiguracionProveedorSIP(
                nombre="Vonage-Secondary",
                tipo=TipoProveedorSIP.VONAGE,
                protocolo=ProtocoloSIP.SIP_UDP,
                servidor_sip="sip.nexmo.com",
                puerto=5060,
                usuario="vonage_user",
                password="vonage_pass",
                dominio="sip.nexmo.com",
                max_llamadas_simultaneas=50,
                costo_por_minuto=0.015,
                calidad_minima=CalidadLlamada.MEDIA
            ),
            ConfiguracionProveedorSIP(
                nombre="Telnyx-Backup",
                tipo=TipoProveedorSIP.TELNYX,
                protocolo=ProtocoloSIP.SIP_TCP,
                servidor_sip="sip.telnyx.com",
                puerto=5060,
                usuario="telnyx_user",
                password="telnyx_pass",
                dominio="sip.telnyx.com",
                max_llamadas_simultaneas=75,
                costo_por_minuto=0.012,
                calidad_minima=CalidadLlamada.ALTA
            )
        ]
        
        for provedor in provedores_ejemplo:
            self.agregar_provedor(provedor)
    
    def agregar_provedor(self, configuracion: ConfiguracionProveedorSIP) -> bool:
        """Adiciona novo provedor SIP"""
        try:
            self.provedores[configuracion.nombre] = configuracion
            self.registros_sip[configuracion.nombre] = EstadoRegistro.DESREGISTRADO
            self.metricas_provedores[configuracion.nombre] = MetricasProvedor(
                nombre_provedor=configuracion.nombre
            )
            
            logger.info(f"✅ Provedor SIP adicionado: {configuracion.nombre}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar provedor: {e}")
            return False
    
    async def registrar_provedor(self, nombre_provedor: str) -> bool:
        """Registra provedor SIP"""
        try:
            if nombre_provedor not in self.provedores:
                logger.error(f"❌ Provedor não encontrado: {nombre_provedor}")
                return False
            
            provedor = self.provedores[nombre_provedor]
            
            # Atualizar estado
            self.registros_sip[nombre_provedor] = EstadoRegistro.REGISTRANDO
            
            # Simular processo de registro
            logger.info(f"📝 Registrando provedor: {nombre_provedor}")
            
            # Para Twilio, usar API específica
            if provedor.tipo == TipoProveedorSIP.TWILIO:
                resultado = await self._registrar_twilio(provedor)
            # Para Vonage, usar API específica
            elif provedor.tipo == TipoProveedorSIP.VONAGE:
                resultado = await self._registrar_vonage(provedor)
            # Para Telnyx, usar API específica
            elif provedor.tipo == TipoProveedorSIP.TELNYX:
                resultado = await self._registrar_telnyx(provedor)
            # Para provedores genéricos, usar SIP padrão
            else:
                resultado = await self._registrar_sip_generico(provedor)
            
            # Atualizar estado baseado no resultado
            if resultado:
                self.registros_sip[nombre_provedor] = EstadoRegistro.REGISTRADO
                logger.info(f"✅ Provedor registrado: {nombre_provedor}")
            else:
                self.registros_sip[nombre_provedor] = EstadoRegistro.FALLO_REGISTRO
                logger.error(f"❌ Falha no registro: {nombre_provedor}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar provedor: {e}")
            self.registros_sip[nombre_provedor] = EstadoRegistro.FALLO_REGISTRO
            return False
    
    async def _registrar_twilio(self, provedor: ConfiguracionProveedorSIP) -> bool:
        """Registro específico para Twilio"""
        try:
            # Implementação específica para Twilio
            # Aqui você conectaria com a API do Twilio
            logger.info(f"🔧 Registrando Twilio: {provedor.servidor_sip}")
            
            # Simular autenticação Twilio
            await asyncio.sleep(1)
            
            # Validar credenciais (simulado)
            if provedor.usuario.startswith("AC") and len(provedor.password) > 10:
                return True
            else:
                logger.error("❌ Credenciais Twilio inválidas")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro no registro Twilio: {e}")
            return False
    
    async def _registrar_vonage(self, provedor: ConfiguracionProveedorSIP) -> bool:
        """Registro específico para Vonage"""
        try:
            logger.info(f"🔧 Registrando Vonage: {provedor.servidor_sip}")
            
            # Simular autenticação Vonage
            await asyncio.sleep(1)
            
            # Validar configuração
            if provedor.servidor_sip == "sip.nexmo.com":
                return True
            else:
                logger.error("❌ Configuração Vonage inválida")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro no registro Vonage: {e}")
            return False
    
    async def _registrar_telnyx(self, provedor: ConfiguracionProveedorSIP) -> bool:
        """Registro específico para Telnyx"""
        try:
            logger.info(f"🔧 Registrando Telnyx: {provedor.servidor_sip}")
            
            # Simular autenticação Telnyx
            await asyncio.sleep(1)
            
            # Validar configuração
            if provedor.servidor_sip == "sip.telnyx.com":
                return True
            else:
                logger.error("❌ Configuração Telnyx inválida")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro no registro Telnyx: {e}")
            return False
    
    async def _registrar_sip_generico(self, provedor: ConfiguracionProveedorSIP) -> bool:
        """Registro SIP genérico"""
        try:
            logger.info(f"🔧 Registrando SIP genérico: {provedor.servidor_sip}")
            
            # Simular conexão SIP
            await asyncio.sleep(2)
            
            # Testar conectividade
            resultado_teste = await self._testar_conectividade_sip(provedor)
            
            return resultado_teste
            
        except Exception as e:
            logger.error(f"❌ Erro no registro SIP genérico: {e}")
            return False
    
    async def _testar_conectividade_sip(self, provedor: ConfiguracionProveedorSIP) -> bool:
        """Testa conectividade com servidor SIP"""
        try:
            # Testar conexão socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # Para UDP, testar com envio de dados
            if provedor.protocolo == ProtocoloSIP.SIP_UDP:
                sock.sendto(b"OPTIONS sip:test SIP/2.0\r\n", (provedor.servidor_sip, provedor.puerto))
                sock.close()
                return True
            
            # Para TCP/TLS, testar conexão
            elif provedor.protocolo in [ProtocoloSIP.SIP_TCP, ProtocoloSIP.SIP_TLS]:
                if provedor.protocolo == ProtocoloSIP.SIP_TLS:
                    context = ssl.create_default_context()
                    sock = context.wrap_socket(sock, server_hostname=provedor.servidor_sip)
                
                sock.connect((provedor.servidor_sip, provedor.puerto))
                sock.close()
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de conectividade: {e}")
            return False
    
    async def iniciar_llamada(self, numero_destino: str, numero_origen: str = None, 
                            provedor_preferido: str = None) -> Optional[str]:
        """Inicia nova chamada SIP"""
        try:
            # Selecionar provedor
            provedor_seleccionado = await self._seleccionar_provedor(
                numero_destino, provedor_preferido
            )
            
            if not provedor_seleccionado:
                logger.error("❌ Nenhum provedor disponível")
                return None
            
            # Gerar Call-ID único
            call_id = str(uuid.uuid4())
            
            # Normalizar números
            numero_destino = self._normalizar_numero(numero_destino)
            numero_origen = numero_origen or self._obter_cli_aleatorio(provedor_seleccionado)
            
            # Criar objeto llamada
            llamada = LlamadaSIP(
                call_id=call_id,
                numero_origen=numero_origen,
                numero_destino=numero_destino,
                provedor=provedor_seleccionado,
                estado="iniciando",
                fecha_inicio=datetime.now()
            )
            
            # Adicionar à lista de chamadas ativas
            self.llamadas_activas[call_id] = llamada
            
            # Executar chamada baseado no tipo de provedor
            provedor_config = self.provedores[provedor_seleccionado]
            
            if provedor_config.tipo == TipoProveedorSIP.TWILIO:
                resultado = await self._llamada_twilio(llamada, provedor_config)
            elif provedor_config.tipo == TipoProveedorSIP.VONAGE:
                resultado = await self._llamada_vonage(llamada, provedor_config)
            elif provedor_config.tipo == TipoProveedorSIP.TELNYX:
                resultado = await self._llamada_telnyx(llamada, provedor_config)
            else:
                resultado = await self._llamada_sip_generica(llamada, provedor_config)
            
            if resultado:
                logger.info(f"📞 Chamada iniciada: {numero_destino} via {provedor_seleccionado}")
                return call_id
            else:
                # Remover chamada se falhou
                del self.llamadas_activas[call_id]
                return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar chamada: {e}")
            return None
    
    async def _seleccionar_provedor(self, numero_destino: str, 
                                   provedor_preferido: str = None) -> Optional[str]:
        """Seleciona melhor provedor para a chamada"""
        try:
            # Se provedor preferido especificado e disponível
            if (provedor_preferido and 
                provedor_preferido in self.provedores and
                self.registros_sip[provedor_preferido] == EstadoRegistro.REGISTRADO):
                return provedor_preferido
            
            # Filtrar provedores disponíveis
            provedores_disponibles = [
                nombre for nombre, estado in self.registros_sip.items()
                if estado == EstadoRegistro.REGISTRADO
            ]
            
            if not provedores_disponibles:
                return None
            
            # Aplicar algoritmo de seleção
            if self.algoritmo_enrutamiento == "round_robin":
                return await self._seleccionar_round_robin(provedores_disponibles)
            elif self.algoritmo_enrutamiento == "least_cost":
                return await self._seleccionar_menor_costo(provedores_disponibles)
            elif self.algoritmo_enrutamiento == "best_quality":
                return await self._seleccionar_mejor_calidad(provedores_disponibles)
            else:
                # Padrão: primeiro disponível
                return provedores_disponibles[0]
            
        except Exception as e:
            logger.error(f"❌ Erro ao selecionar provedor: {e}")
            return None
    
    async def _seleccionar_round_robin(self, provedores: List[str]) -> str:
        """Seleção round robin"""
        # Implementação simples - pode ser melhorada com estado persistente
        timestamp = int(time.time())
        index = timestamp % len(provedores)
        return provedores[index]
    
    async def _seleccionar_menor_costo(self, provedores: List[str]) -> str:
        """Seleção por menor custo"""
        menor_costo = float('inf')
        provedor_seleccionado = provedores[0]
        
        for nombre_provedor in provedores:
            provedor = self.provedores[nombre_provedor]
            if provedor.costo_por_minuto < menor_costo:
                menor_costo = provedor.costo_por_minuto
                provedor_seleccionado = nombre_provedor
        
        return provedor_seleccionado
    
    async def _seleccionar_mejor_calidad(self, provedores: List[str]) -> str:
        """Seleção por melhor qualidade"""
        mejor_calidad = 0
        provedor_seleccionado = provedores[0]
        
        for nombre_provedor in provedores:
            metricas = self.metricas_provedores[nombre_provedor]
            if metricas.calidad_promedio > mejor_calidad:
                mejor_calidad = metricas.calidad_promedio
                provedor_seleccionado = nombre_provedor
        
        return provedor_seleccionado
    
    async def _llamada_twilio(self, llamada: LlamadaSIP, provedor: ConfiguracionProveedorSIP) -> bool:
        """Executa chamada via Twilio"""
        try:
            logger.info(f"📞 Executando chamada Twilio: {llamada.numero_destino}")
            
            # Simular chamada Twilio
            await asyncio.sleep(1)
            
            # Atualizar estado
            llamada.estado = "conectando"
            llamada.logs_sip.append({
                "timestamp": datetime.now().isoformat(),
                "evento": "INVITE_SENT",
                "provedor": "twilio"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na chamada Twilio: {e}")
            return False
    
    async def _llamada_vonage(self, llamada: LlamadaSIP, provedor: ConfiguracionProveedorSIP) -> bool:
        """Executa chamada via Vonage"""
        try:
            logger.info(f"📞 Executando chamada Vonage: {llamada.numero_destino}")
            
            # Simular chamada Vonage
            await asyncio.sleep(1)
            
            # Atualizar estado
            llamada.estado = "conectando"
            llamada.logs_sip.append({
                "timestamp": datetime.now().isoformat(),
                "evento": "INVITE_SENT",
                "provedor": "vonage"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na chamada Vonage: {e}")
            return False
    
    async def _llamada_telnyx(self, llamada: LlamadaSIP, provedor: ConfiguracionProveedorSIP) -> bool:
        """Executa chamada via Telnyx"""
        try:
            logger.info(f"📞 Executando chamada Telnyx: {llamada.numero_destino}")
            
            # Simular chamada Telnyx
            await asyncio.sleep(1)
            
            # Atualizar estado
            llamada.estado = "conectando"
            llamada.logs_sip.append({
                "timestamp": datetime.now().isoformat(),
                "evento": "INVITE_SENT",
                "provedor": "telnyx"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na chamada Telnyx: {e}")
            return False
    
    async def _llamada_sip_generica(self, llamada: LlamadaSIP, provedor: ConfiguracionProveedorSIP) -> bool:
        """Executa chamada SIP genérica"""
        try:
            logger.info(f"📞 Executando chamada SIP genérica: {llamada.numero_destino}")
            
            # Simular chamada SIP
            await asyncio.sleep(1)
            
            # Atualizar estado
            llamada.estado = "conectando"
            llamada.logs_sip.append({
                "timestamp": datetime.now().isoformat(),
                "evento": "INVITE_SENT",
                "provedor": "generic_sip"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na chamada SIP genérica: {e}")
            return False
    
    def _normalizar_numero(self, numero: str) -> str:
        """Normaliza número para formato E.164"""
        # Remover caracteres não numéricos exceto +
        numero_limpo = ''.join(c for c in numero if c.isdigit() or c == '+')
        
        # Adicionar + se não tiver
        if not numero_limpo.startswith('+'):
            numero_limpo = '+' + numero_limpo
        
        return numero_limpo
    
    def _obter_cli_aleatorio(self, nombre_provedor: str) -> str:
        """Obtém CLI aleatório para o provedor"""
        # Implementação simples - pode ser melhorada
        import random
        
        base_cli = "+1800555"
        sufijo = str(random.randint(1000, 9999))
        
        return base_cli + sufijo
    
    async def finalizar_llamada(self, call_id: str, causa: str = "NORMAL_CLEARING") -> bool:
        """Finaliza chamada específica"""
        try:
            if call_id not in self.llamadas_activas:
                logger.error(f"❌ Chamada não encontrada: {call_id}")
                return False
            
            llamada = self.llamadas_activas[call_id]
            llamada.estado = "finalizada"
            llamada.fecha_fin = datetime.now()
            llamada.causa_finalizacion = causa
            
            # Calcular duração e costo
            if llamada.fecha_respuesta:
                duracao_segundos = (llamada.fecha_fin - llamada.fecha_respuesta).total_seconds()
                llamada.duracion = duracao_segundos
                
                # Calcular costo
                provedor = self.provedores[llamada.provedor]
                minutos = duracao_segundos / 60
                llamada.costo = minutos * provedor.costo_por_minuto
            
            # Adicionar log
            llamada.logs_sip.append({
                "timestamp": datetime.now().isoformat(),
                "evento": "CALL_HANGUP",
                "causa": causa
            })
            
            # Atualizar métricas
            await self._actualizar_metricas_provedor(llamada)
            
            logger.info(f"📴 Chamada finalizada: {call_id} - Duração: {llamada.duracion}s")
            
            # Remover das chamadas ativas após delay
            asyncio.create_task(self._limpiar_llamada_finalizada(call_id))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao finalizar chamada: {e}")
            return False
    
    async def _actualizar_metricas_provedor(self, llamada: LlamadaSIP):
        """Atualiza métricas do provedor"""
        try:
            metricas = self.metricas_provedores[llamada.provedor]
            
            if llamada.estado == "finalizada" and llamada.duracion > 0:
                metricas.llamadas_exitosas += 1
            else:
                metricas.llamadas_fallidas += 1
            
            metricas.costo_total += llamada.costo
            metricas.ultima_actualizacion = datetime.now()
            
            # Calcular qualidade baseada na duração
            if llamada.duracion > 30:  # Chamadas longas = boa qualidade
                calidad_llamada = 5
            elif llamada.duracion > 10:
                calidad_llamada = 4
            elif llamada.duracion > 5:
                calidad_llamada = 3
            else:
                calidad_llamada = 2
            
            # Atualizar qualidade promedio
            total_llamadas = metricas.llamadas_exitosas + metricas.llamadas_fallidas
            metricas.calidad_promedio = (
                (metricas.calidad_promedio * (total_llamadas - 1) + calidad_llamada) / total_llamadas
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar métricas: {e}")
    
    async def _limpiar_llamada_finalizada(self, call_id: str):
        """Remove chamada finalizada após delay"""
        await asyncio.sleep(300)  # 5 minutos
        if call_id in self.llamadas_activas:
            del self.llamadas_activas[call_id]
    
    def obter_llamadas_activas(self) -> List[Dict[str, Any]]:
        """Obtém lista de chamadas ativas"""
        llamadas = []
        
        for call_id, llamada in self.llamadas_activas.items():
            llamadas.append({
                "call_id": llamada.call_id,
                "numero_origen": llamada.numero_origen,
                "numero_destino": llamada.numero_destino,
                "provedor": llamada.provedor,
                "estado": llamada.estado,
                "fecha_inicio": llamada.fecha_inicio.isoformat(),
                "duracion": llamada.duracion,
                "costo": llamada.costo,
                "calidad": llamada.calidad.value if llamada.calidad else None,
                "codec": llamada.codec_usado
            })
        
        return llamadas
    
    def obter_metricas_provedores(self) -> Dict[str, Any]:
        """Obtém métricas de todos os provedores"""
        metricas = {}
        
        for nombre, metricas_provedor in self.metricas_provedores.items():
            metricas[nombre] = {
                "nombre": metricas_provedor.nombre_provedor,
                "llamadas_exitosas": metricas_provedor.llamadas_exitosas,
                "llamadas_fallidas": metricas_provedor.llamadas_fallidas,
                "tiempo_respuesta_promedio": metricas_provedor.tiempo_respuesta_promedio,
                "calidad_promedio": metricas_provedor.calidad_promedio,
                "costo_total": metricas_provedor.costo_total,
                "uptime": metricas_provedor.uptime,
                "estado_registro": self.registros_sip.get(nombre, EstadoRegistro.DESREGISTRADO).value,
                "llamadas_activas": len([l for l in self.llamadas_activas.values() if l.provedor == nombre])
            }
        
        return metricas
    
    def configurar_algoritmo_enrutamiento(self, algoritmo: str) -> bool:
        """Configura algoritmo de enrutamiento"""
        algoritmos_validos = ["round_robin", "least_cost", "best_quality"]
        
        if algoritmo in algoritmos_validos:
            self.algoritmo_enrutamiento = algoritmo
            logger.info(f"✅ Algoritmo configurado: {algoritmo}")
            return True
        else:
            logger.error(f"❌ Algoritmo inválido: {algoritmo}")
            return False
    
    def habilitar_failover(self, habilitado: bool):
        """Habilita/desabilita failover automático"""
        self.failover_habilitado = habilitado
        logger.info(f"🔄 Failover {'habilitado' if habilitado else 'desabilitado'}")
    
    async def registrar_todos_provedores(self) -> Dict[str, bool]:
        """Registra todos os provedores"""
        resultados = {}
        
        for nombre_provedor in self.provedores.keys():
            resultado = await self.registrar_provedor(nombre_provedor)
            resultados[nombre_provedor] = resultado
        
        return resultados
    
    def obter_status_sistema(self) -> Dict[str, Any]:
        """Obtém status completo do sistema"""
        return {
            "provedores_configurados": len(self.provedores),
            "provedores_registrados": len([
                p for p in self.registros_sip.values() 
                if p == EstadoRegistro.REGISTRADO
            ]),
            "llamadas_activas": len(self.llamadas_activas),
            "algoritmo_enrutamiento": self.algoritmo_enrutamiento,
            "failover_habilitado": self.failover_habilitado,
            "timestamp": datetime.now().isoformat()
        }

# Instância global do serviço
sip_comercial_service = SIPComercialService() 