"""
Modelo para gerenciamento avançado de trunks SIP.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, func, DECIMAL, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Dict, Any

from app.database import Base


class Trunk(Base):
    """Modelo para trunks SIP avançados."""
    
    __tablename__ = "trunks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação básica
    nome = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)
    
    # Configurações de conexão
    host = Column(String(255), nullable=False)
    porta = Column(Integer, default=5060, nullable=False)
    usuario = Column(String(100), nullable=False)
    senha = Column(String(255), nullable=False)
    
    # Configurações avançadas SIP
    protocolo = Column(String(10), default='UDP', nullable=False)  # UDP, TCP, TLS
    codec_preferido = Column(String(50), default='ulaw', nullable=False)
    codecs_permitidos = Column(JSON, default=['ulaw', 'alaw', 'g729'])
    
    # Configurações de roteamento
    prefixo_discagem = Column(String(20), default='')
    sufixo_discagem = Column(String(20), default='')
    codigo_pais = Column(String(5), default='+1')  # Para EUA
    codigo_area_default = Column(String(10), default='')
    
    # Configurações de DV (Dígito Verificador) para EUA
    usar_dv = Column(Boolean, default=True)
    formato_dv = Column(String(50), default='10_digit')  # 10_digit, 11_digit, e164
    remover_codigo_pais = Column(Boolean, default=False)
    
    # Configurações de Caller ID
    caller_id_nome = Column(String(100), default='')
    caller_id_numero = Column(String(20), default='')
    randomizar_caller_id = Column(Boolean, default=False)
    pool_caller_ids = Column(JSON, default=[])  # Lista de CLIs disponíveis
    
    # Configurações de capacidade
    max_canais_simultaneos = Column(Integer, default=10)
    canais_em_uso = Column(Integer, default=0)
    prioridade = Column(Integer, default=1)  # 1=alta, 5=baixa
    peso_balanceamento = Column(Integer, default=100)  # Para load balancing
    
    # Configurações de qualidade
    timeout_conexao = Column(Integer, default=30)  # segundos
    timeout_resposta = Column(Integer, default=60)  # segundos
    max_tentativas = Column(Integer, default=3)
    intervalo_retry = Column(Integer, default=60)  # segundos
    
    # Configurações de detecção
    detectar_busy = Column(Boolean, default=True)
    detectar_no_answer = Column(Boolean, default=True)
    detectar_congestion = Column(Boolean, default=True)
    detectar_invalid = Column(Boolean, default=True)
    
    # Configurações de horário
    horario_ativo_inicio = Column(String(5), default='00:00')
    horario_ativo_fim = Column(String(5), default='23:59')
    dias_semana_ativo = Column(JSON, default=[0,1,2,3,4,5,6])  # 0=Domingo
    timezone = Column(String(50), default='America/New_York')
    
    # Configurações de custo e limites
    custo_por_minuto = Column(DECIMAL(10,4), default=0.0)
    limite_diario_chamadas = Column(Integer, default=0)  # 0=ilimitado
    limite_mensal_custo = Column(DECIMAL(10,2), default=0.0)  # 0=ilimitado
    
    # Status e monitoramento
    ativo = Column(Boolean, default=True)
    status_conexao = Column(String(20), default='desconhecido')  # online, offline, erro
    ultima_verificacao = Column(DateTime)
    total_chamadas_hoje = Column(Integer, default=0)
    total_chamadas_mes = Column(Integer, default=0)
    
    # Configurações de failover
    trunk_backup_id = Column(Integer, ForeignKey("trunks.id"), nullable=True)
    usar_failover = Column(Boolean, default=False)
    
    # Auditoria
    usuario_criador_id = Column(Integer, nullable=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    trunk_backup = relationship("Trunk", remote_side=[id])
    estatisticas = relationship("TrunkEstatistica", back_populates="trunk")
    
    def __repr__(self):
        return f"<Trunk(id={self.id}, nome={self.nome}, host={self.host})>"
    
    def esta_ativo(self) -> bool:
        """Verifica se o trunk está ativo e dentro do horário."""
        if not self.ativo:
            return False
        
        # Aqui você implementaria verificação de horário
        # Por simplicidade, retornando apenas o status ativo
        return True
    
    def pode_aceitar_chamada(self) -> bool:
        """Verifica se o trunk pode aceitar uma nova chamada."""
        if not self.esta_ativo():
            return False
        
        if self.max_canais_simultaneos > 0:
            return self.canais_em_uso < self.max_canais_simultaneos
        
        return True
    
    def formatar_numero(self, numero: str) -> str:
        """Formata um número de acordo com as configurações do trunk."""
        numero_formatado = numero.strip()
        
        # Remover caracteres não numéricos
        numero_limpo = ''.join(filter(str.isdigit, numero_formatado))
        
        if self.usar_dv and self.codigo_pais == '+1':  # EUA
            # Lógica específica para números dos EUA
            if len(numero_limpo) == 11 and numero_limpo.startswith('1'):
                numero_limpo = numero_limpo[1:]  # Remover o 1 inicial
            
            if len(numero_limpo) == 10:
                if self.formato_dv == '11_digit':
                    numero_limpo = '1' + numero_limpo
                elif self.formato_dv == 'e164':
                    numero_limpo = '+1' + numero_limpo
        
        # Adicionar prefixo e sufixo
        numero_final = self.prefixo_discagem + numero_limpo + self.sufixo_discagem
        
        return numero_final
    
    def obter_caller_id(self) -> Dict[str, str]:
        """Obtém o Caller ID a ser usado."""
        if self.randomizar_caller_id and self.pool_caller_ids:
            import random
            cli_escolhido = random.choice(self.pool_caller_ids)
            return {
                'numero': cli_escolhido.get('numero', self.caller_id_numero),
                'nome': cli_escolhido.get('nome', self.caller_id_nome)
            }
        
        return {
            'numero': self.caller_id_numero,
            'nome': self.caller_id_nome
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'descripcion': self.descripcion,
            'host': self.host,
            'porta': self.porta,
            'usuario': self.usuario,
            'protocolo': self.protocolo,
            'codec_preferido': self.codec_preferido,
            'codecs_permitidos': self.codecs_permitidos,
            'prefixo_discagem': self.prefixo_discagem,
            'sufixo_discagem': self.sufixo_discagem,
            'codigo_pais': self.codigo_pais,
            'codigo_area_default': self.codigo_area_default,
            'usar_dv': self.usar_dv,
            'formato_dv': self.formato_dv,
            'caller_id_nome': self.caller_id_nome,
            'caller_id_numero': self.caller_id_numero,
            'randomizar_caller_id': self.randomizar_caller_id,
            'pool_caller_ids': self.pool_caller_ids,
            'max_canais_simultaneos': self.max_canais_simultaneos,
            'canais_em_uso': self.canais_em_uso,
            'prioridade': self.prioridade,
            'peso_balanceamento': self.peso_balanceamento,
            'timeout_conexao': self.timeout_conexao,
            'timeout_resposta': self.timeout_resposta,
            'ativo': self.ativo,
            'status_conexao': self.status_conexao,
            'ultima_verificacao': self.ultima_verificacao.isoformat() if self.ultima_verificacao else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class TrunkEstatistica(Base):
    """Estatísticas de uso do trunk."""
    
    __tablename__ = "trunk_estatisticas"
    
    id = Column(Integer, primary_key=True, index=True)
    trunk_id = Column(Integer, ForeignKey("trunks.id"), nullable=False)
    
    # Período das estatísticas
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    
    # Estatísticas de chamadas
    total_chamadas = Column(Integer, default=0)
    chamadas_completadas = Column(Integer, default=0)
    chamadas_falhadas = Column(Integer, default=0)
    chamadas_ocupado = Column(Integer, default=0)
    chamadas_nao_atendidas = Column(Integer, default=0)
    
    # Estatísticas de tempo
    duracao_total_minutos = Column(DECIMAL(10,2), default=0.0)
    duracao_media_segundos = Column(DECIMAL(6,2), default=0.0)
    tempo_resposta_medio = Column(DECIMAL(6,2), default=0.0)
    
    # Estatísticas de qualidade
    taxa_sucesso = Column(DECIMAL(5,2), default=0.0)  # Percentual
    taxa_abandono = Column(DECIMAL(5,2), default=0.0)  # Percentual
    
    # Estatísticas de uso
    pico_canais_simultaneos = Column(Integer, default=0)
    media_canais_em_uso = Column(DECIMAL(5,2), default=0.0)
    
    # Custos
    custo_total = Column(DECIMAL(10,2), default=0.0)
    
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relationships
    trunk = relationship("Trunk", back_populates="estatisticas")
    
    def __repr__(self):
        return f"<TrunkEstatistica(trunk_id={self.trunk_id}, total_chamadas={self.total_chamadas})>"


class TrunkLog(Base):
    """Log de eventos do trunk."""
    
    __tablename__ = "trunk_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    trunk_id = Column(Integer, ForeignKey("trunks.id"), nullable=False)
    
    # Evento
    tipo_evento = Column(String(50), nullable=False)  # conexao, chamada, erro, etc.
    descricao = Column(Text, nullable=False)
    nivel = Column(String(10), default='info')  # debug, info, warning, error
    
    # Contexto
    numero_destino = Column(String(20))
    codigo_resposta = Column(String(10))
    tempo_resposta = Column(DECIMAL(6,3))  # em segundos
    
    # Metadados
    dados_extras = Column(JSON)
    
    timestamp = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<TrunkLog(trunk_id={self.trunk_id}, tipo={self.tipo_evento})>" 