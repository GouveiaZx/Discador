"""
Serviço DNC (Do Not Call) avançado com funcionalidades específicas para mercado americano.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_, text
from fastapi import HTTPException
import re
import requests
import asyncio
from enum import Enum

from app.models.lista_negra import ListaNegra
from app.schemas.lista_llamadas import validar_numero_telefone
from app.utils.logger import logger


class TipoDNC(str, Enum):
    """Tipos de DNC."""
    FEDERAL = "federal"           # National DNC Registry
    ESTADUAL = "estadual"         # State-specific DNC
    INTERNO = "interno"           # Internal company DNC
    WIRELESS = "wireless"         # Wireless DNC
    TCPA = "tcpa"                # TCPA violations
    MANUAL = "manual"            # Manually added


class MotivoOptOut(str, Enum):
    """Motivos de opt-out."""
    SOLICITACAO_CLIENTE = "solicitacao_cliente"
    RECLAMACAO = "reclamacao"
    NUMERO_INVALIDO = "numero_invalido"
    FAX_DETECTADO = "fax_detectado"
    EMPRESA_FECHADA = "empresa_fechada"
    NUMERO_INCORRETO = "numero_incorreto"
    NAO_INTERESSADO = "nao_interessado"
    JA_CLIENTE = "ja_cliente"
    HORARIO_INADEQUADO = "horario_inadequado"
    TCPA_VIOLATION = "tcpa_violation"


class DNCAvarancadoService:
    """Serviço DNC avançado."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_dnc_federal = {}  # Cache para consultas DNC federal
        self.cache_expires = {}      # Controle de expiração do cache
        self.timezone_map = {
            # Mapeamento de códigos de área para timezones dos EUA
            '212': 'America/New_York',    # NY
            '213': 'America/Los_Angeles', # CA
            '214': 'America/Chicago',     # TX
            '215': 'America/New_York',    # PA
            '216': 'America/New_York',    # OH
            '217': 'America/Chicago',     # IL
            '218': 'America/Chicago',     # MN
            '219': 'America/Chicago',     # IN
            # Adicionar mais conforme necessário
        }
    
    def verificar_dnc_completo(
        self, 
        numero: str,
        campanha_id: Optional[int] = None,
        verificar_horario: bool = True
    ) -> Dict[str, Any]:
        """
        Verificação completa de DNC incluindo múltiplas listas e horários.
        """
        
        # Validar número
        validacao = validar_numero_telefone(numero)
        if not validacao.valido:
            return {
                'numero_original': numero,
                'valido': False,
                'pode_ligar': False,
                'motivo': 'Número inválido',
                'detalhes': validacao.motivo_invalido
            }
        
        numero_normalizado = validacao.numero_normalizado
        resultado = {
            'numero_original': numero,
            'numero_normalizado': numero_normalizado,
            'valido': True,
            'pode_ligar': True,
            'motivo': None,
            'verificacoes': {},
            'horario_permitido': True,
            'timezone': None
        }
        
        # 1. Verificar DNC interno
        dnc_interno = self._verificar_dnc_interno(numero_normalizado)
        resultado['verificacoes']['dnc_interno'] = dnc_interno
        
        if dnc_interno['bloqueado']:
            resultado['pode_ligar'] = False
            resultado['motivo'] = f"DNC Interno: {dnc_interno['motivo']}"
        
        # 2. Verificar DNC federal (simulado)
        dnc_federal = self._verificar_dnc_federal(numero_normalizado)
        resultado['verificacoes']['dnc_federal'] = dnc_federal
        
        if dnc_federal['bloqueado']:
            resultado['pode_ligar'] = False
            resultado['motivo'] = f"DNC Federal: {dnc_federal['motivo']}"
        
        # 3. Verificar números wireless
        wireless_check = self._verificar_wireless(numero_normalizado)
        resultado['verificacoes']['wireless'] = wireless_check
        
        if wireless_check['is_wireless'] and wireless_check['requer_consentimento']:
            resultado['pode_ligar'] = False
            resultado['motivo'] = "Número wireless requer consentimento específico"
        
        # 4. Verificar horários permitidos
        if verificar_horario:
            horario_check = self._verificar_horario_permitido(numero_normalizado)
            resultado['verificacoes']['horario'] = horario_check
            resultado['horario_permitido'] = horario_check['permitido']
            resultado['timezone'] = horario_check['timezone']
            
            if not horario_check['permitido']:
                resultado['pode_ligar'] = False
                resultado['motivo'] = f"Horário não permitido: {horario_check['motivo']}"
        
        # 5. Verificar TCPA compliance
        tcpa_check = self._verificar_tcpa_compliance(numero_normalizado, campanha_id)
        resultado['verificacoes']['tcpa'] = tcpa_check
        
        if not tcpa_check['compliant']:
            resultado['pode_ligar'] = False
            resultado['motivo'] = f"TCPA: {tcpa_check['motivo']}"
        
        # 6. Verificar frequência de chamadas
        frequencia_check = self._verificar_frequencia_chamadas(numero_normalizado)
        resultado['verificacoes']['frequencia'] = frequencia_check
        
        if not frequencia_check['permitido']:
            resultado['pode_ligar'] = False
            resultado['motivo'] = f"Frequência: {frequencia_check['motivo']}"
        
        return resultado
    
    def _verificar_dnc_interno(self, numero_normalizado: str) -> Dict[str, Any]:
        """Verifica DNC interno da empresa."""
        
        entrada = self.db.query(ListaNegra).filter(
            and_(
                ListaNegra.numero_normalizado == numero_normalizado,
                ListaNegra.activo == True
            )
        ).first()
        
        if entrada:
            return {
                'bloqueado': True,
                'motivo': entrada.motivo or 'Lista interna',
                'data_inclusao': entrada.fecha_creacion.isoformat(),
                'tipo': TipoDNC.INTERNO.value,
                'observacoes': entrada.observaciones
            }
        
        return {
            'bloqueado': False,
            'motivo': None,
            'tipo': TipoDNC.INTERNO.value
        }
    
    def _verificar_dnc_federal(self, numero_normalizado: str) -> Dict[str, Any]:
        """
        Verifica DNC federal (simulado - em produção seria integração real).
        """
        
        # Cache check
        if numero_normalizado in self.cache_dnc_federal:
            cache_time = self.cache_expires.get(numero_normalizado)
            if cache_time and datetime.now() < cache_time:
                return self.cache_dnc_federal[numero_normalizado]
        
        # Simular verificação DNC federal
        # Em produção, seria uma chamada para a API do National DNC Registry
        
        # Para simulação, marcar alguns números como DNC federal
        codigo_area = numero_normalizado[:3] if len(numero_normalizado) >= 10 else ""
        
        # Simular que números com código de área específico estão no DNC federal
        codigos_dnc_simulados = ['555', '800', '888', '877', '866']
        
        resultado = {
            'bloqueado': codigo_area in codigos_dnc_simulados,
            'motivo': 'National Do Not Call Registry' if codigo_area in codigos_dnc_simulados else None,
            'tipo': TipoDNC.FEDERAL.value,
            'verificado_em': datetime.now().isoformat(),
            'fonte': 'National DNC Registry (simulado)'
        }
        
        # Cache por 24 horas
        self.cache_dnc_federal[numero_normalizado] = resultado
        self.cache_expires[numero_normalizado] = datetime.now() + timedelta(hours=24)
        
        return resultado
    
    def _verificar_wireless(self, numero_normalizado: str) -> Dict[str, Any]:
        """Verifica se é número wireless e regras específicas."""
        
        if len(numero_normalizado) < 10:
            return {
                'is_wireless': False,
                'requer_consentimento': False,
                'motivo': 'Número muito curto para verificação'
            }
        
        # Extrair código de área
        codigo_area = numero_normalizado[:3]
        
        # Códigos de área tipicamente wireless (simulado)
        codigos_wireless = [
            '310', '323', '424', '661', '747', '818', '858', '909', '949',  # CA
            '917', '347', '646', '929',  # NY
            '202', '240', '301', '410', '443', '667'  # DC/MD área
        ]
        
        is_wireless = codigo_area in codigos_wireless
        
        return {
            'is_wireless': is_wireless,
            'requer_consentimento': is_wireless,
            'codigo_area': codigo_area,
            'motivo': 'Número wireless detectado - requer consentimento específico' if is_wireless else None,
            'tipo': 'wireless' if is_wireless else 'landline'
        }
    
    def _verificar_horario_permitido(self, numero_normalizado: str) -> Dict[str, Any]:
        """Verifica se horário atual é permitido para o número."""
        
        # Determinar timezone baseado no código de área
        codigo_area = numero_normalizado[:3] if len(numero_normalizado) >= 10 else ""
        timezone = self.timezone_map.get(codigo_area, 'America/New_York')  # Default EST
        
        # Para simplicidade, usar horário local do servidor
        # Em produção, converter para timezone correto
        agora = datetime.now()
        hora_atual = agora.time()
        
        # Horários permitidos: 8:00 - 21:00 (TCPA compliance)
        inicio_permitido = time(8, 0)   # 8:00 AM
        fim_permitido = time(21, 0)     # 9:00 PM
        
        # Verificar se é domingo (dia 6)
        if agora.weekday() == 6:  # Domingo
            inicio_permitido = time(13, 0)  # 1:00 PM aos domingos
        
        permitido = inicio_permitido <= hora_atual <= fim_permitido
        
        return {
            'permitido': permitido,
            'timezone': timezone,
            'hora_local': hora_atual.strftime('%H:%M:%S'),
            'janela_permitida': f"{inicio_permitido.strftime('%H:%M')} - {fim_permitido.strftime('%H:%M')}",
            'motivo': None if permitido else f"Fora do horário permitido ({inicio_permitido.strftime('%H:%M')}-{fim_permitido.strftime('%H:%M')})"
        }
    
    def _verificar_tcpa_compliance(
        self, 
        numero_normalizado: str, 
        campanha_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Verifica compliance com TCPA (Telephone Consumer Protection Act)."""
        
        violacoes = []
        
        # 1. Verificar se há consentimento registrado
        consentimento = self._verificar_consentimento(numero_normalizado, campanha_id)
        if not consentimento['tem_consentimento']:
            violacoes.append("Sem consentimento registrado")
        
        # 2. Verificar limite de tentativas por dia
        tentativas_hoje = self._contar_tentativas_hoje(numero_normalizado)
        if tentativas_hoje > 3:  # Máximo 3 tentativas por dia
            violacoes.append(f"Limite de tentativas excedido ({tentativas_hoje}/3)")
        
        # 3. Verificar intervalo mínimo entre chamadas
        ultima_chamada = self._obter_ultima_chamada(numero_normalizado)
        if ultima_chamada:
            tempo_desde_ultima = datetime.now() - ultima_chamada
            if tempo_desde_ultima < timedelta(hours=4):  # Mínimo 4 horas
                violacoes.append(f"Intervalo mínimo não respeitado ({tempo_desde_ultima})")
        
        return {
            'compliant': len(violacoes) == 0,
            'violacoes': violacoes,
            'motivo': '; '.join(violacoes) if violacoes else None,
            'consentimento': consentimento,
            'tentativas_hoje': tentativas_hoje
        }
    
    def _verificar_consentimento(
        self, 
        numero_normalizado: str, 
        campanha_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Verifica se há consentimento registrado para o número."""
        
        # Em um sistema real, isso consultaria uma tabela de consentimentos
        # Por agora, simulando baseado em critérios
        
        # Simular que números que terminam em dígitos pares têm consentimento
        ultimo_digito = int(numero_normalizado[-1]) if numero_normalizado else 0
        tem_consentimento = ultimo_digito % 2 == 0
        
        return {
            'tem_consentimento': tem_consentimento,
            'data_consentimento': datetime.now() - timedelta(days=30) if tem_consentimento else None,
            'tipo_consentimento': 'opt-in' if tem_consentimento else None,
            'campanha_id': campanha_id,
            'metodo_consentimento': 'website' if tem_consentimento else None
        }
    
    def _contar_tentativas_hoje(self, numero_normalizado: str) -> int:
        """Conta tentativas de chamada hoje para o número."""
        
        # Simular contagem baseada no banco
        # Em produção, consultaria tabela de chamadas
        
        inicio_dia = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Query simulada - em produção seria:
        # return self.db.query(Llamada).filter(
        #     and_(
        #         Llamada.numero_destino == numero_normalizado,
        #         Llamada.fecha_inicio >= inicio_dia
        #     )
        # ).count()
        
        # Para simulação, retornar valor baseado no hash do número
        return hash(numero_normalizado) % 4  # 0-3 tentativas
    
    def _obter_ultima_chamada(self, numero_normalizado: str) -> Optional[datetime]:
        """Obtém timestamp da última chamada para o número."""
        
        # Simular última chamada
        # Em produção seria query real no banco
        
        # Para simulação, retornar horário baseado no hash
        if hash(numero_normalizado) % 3 == 0:
            return datetime.now() - timedelta(hours=2)  # 2 horas atrás
        elif hash(numero_normalizado) % 3 == 1:
            return datetime.now() - timedelta(hours=6)  # 6 horas atrás
        else:
            return None  # Nunca ligou
    
    def _verificar_frequencia_chamadas(self, numero_normalizado: str) -> Dict[str, Any]:
        """Verifica se a frequência de chamadas está dentro dos limites."""
        
        # Verificar chamadas na última semana
        inicio_semana = datetime.now() - timedelta(days=7)
        
        # Simular contagem
        chamadas_semana = hash(numero_normalizado) % 8  # 0-7 chamadas
        
        # Limite: máximo 5 chamadas por semana
        limite_semanal = 5
        permitido = chamadas_semana <= limite_semanal
        
        return {
            'permitido': permitido,
            'chamadas_semana': chamadas_semana,
            'limite_semanal': limite_semanal,
            'motivo': None if permitido else f"Limite semanal excedido ({chamadas_semana}/{limite_semanal})"
        }
    
    def adicionar_opt_out(
        self,
        numero: str,
        motivo: MotivoOptOut,
        observacoes: Optional[str] = None,
        campanha_id: Optional[int] = None,
        usuario: Optional[str] = None
    ) -> Dict[str, Any]:
        """Adiciona número à lista de opt-out."""
        
        validacao = validar_numero_telefone(numero)
        if not validacao.valido:
            raise HTTPException(
                status_code=400,
                detail=f"Número inválido: {validacao.motivo_invalido}"
            )
        
        # Verificar se já existe
        existente = self.db.query(ListaNegra).filter(
            ListaNegra.numero_normalizado == validacao.numero_normalizado
        ).first()
        
        if existente and existente.activo:
            # Atualizar motivo se for mais específico
            existente.motivo = f"{motivo.value}: {observacoes}" if observacoes else motivo.value
            existente.observaciones = observacoes
            existente.fecha_actualizacion = func.now()
            self.db.commit()
            
            return {
                'numero': validacao.numero_normalizado,
                'acao': 'atualizado',
                'motivo': motivo.value,
                'id': existente.id
            }
        
        # Criar nova entrada
        nova_entrada = ListaNegra(
            numero=numero,
            numero_normalizado=validacao.numero_normalizado,
            motivo=f"{motivo.value}: {observacoes}" if observacoes else motivo.value,
            observaciones=observacoes,
            creado_por=usuario,
            activo=True
        )
        
        try:
            self.db.add(nova_entrada)
            self.db.commit()
            self.db.refresh(nova_entrada)
            
            logger.info(f"Opt-out adicionado: {validacao.numero_normalizado} - {motivo.value}")
            
            return {
                'numero': validacao.numero_normalizado,
                'acao': 'adicionado',
                'motivo': motivo.value,
                'id': nova_entrada.id
            }
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Erro ao adicionar opt-out"
            )
    
    def processar_opt_outs_bulk(
        self,
        numeros: List[str],
        motivo: MotivoOptOut,
        observacoes: Optional[str] = None,
        usuario: Optional[str] = None
    ) -> Dict[str, Any]:
        """Processa múltiplos opt-outs."""
        
        resultados = {
            'processados': 0,
            'adicionados': 0,
            'atualizados': 0,
            'erros': 0,
            'detalhes': []
        }
        
        for numero in numeros:
            try:
                resultado = self.adicionar_opt_out(
                    numero=numero,
                    motivo=motivo,
                    observacoes=observacoes,
                    usuario=usuario
                )
                
                resultados['processados'] += 1
                if resultado['acao'] == 'adicionado':
                    resultados['adicionados'] += 1
                else:
                    resultados['atualizados'] += 1
                
                resultados['detalhes'].append(resultado)
                
            except Exception as e:
                resultados['erros'] += 1
                resultados['detalhes'].append({
                    'numero': numero,
                    'erro': str(e)
                })
        
        return resultados
    
    def obter_relatorio_dnc(
        self,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Gera relatório completo de DNC."""
        
        if not data_inicio:
            data_inicio = datetime.now() - timedelta(days=30)
        if not data_fim:
            data_fim = datetime.now()
        
        # Estatísticas da blacklist
        total_dnc = self.db.query(ListaNegra).filter(ListaNegra.activo == True).count()
        
        dnc_por_motivo = self.db.query(
            ListaNegra.motivo,
            func.count(ListaNegra.id)
        ).filter(
            and_(
                ListaNegra.activo == True,
                ListaNegra.fecha_creacion >= data_inicio,
                ListaNegra.fecha_creacion <= data_fim
            )
        ).group_by(ListaNegra.motivo).all()
        
        return {
            'periodo': {
                'inicio': data_inicio.isoformat(),
                'fim': data_fim.isoformat()
            },
            'estatisticas': {
                'total_dnc_ativo': total_dnc,
                'adicionados_periodo': sum(count for _, count in dnc_por_motivo),
                'por_motivo': dict(dnc_por_motivo)
            },
            'compliance': {
                'verificacoes_ativas': [
                    'DNC Interno',
                    'DNC Federal (simulado)',
                    'Wireless Detection',
                    'TCPA Compliance',
                    'Horários Permitidos',
                    'Frequência de Chamadas'
                ],
                'cache_federal_entries': len(self.cache_dnc_federal)
            }
        } 