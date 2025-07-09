"""
Serviço para configurações de DTMF específicas por país.
Permite configurar diferentes teclas DTMF por país (ex: "oprimir 3" para México).
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import logging

from app.models.audio_sistema import AudioContexto, AudioRegra, TipoEvento, EstadoAudio
from app.schemas.lista_llamadas import detectar_pais_numero

logger = logging.getLogger(__name__)

class DTMFCountryConfigService:
    """Serviço para configurações de DTMF por país."""
    
    # Configurações DTMF por país
    COUNTRY_DTMF_CONFIG = {
        'usa': {
            'connect_key': '1',
            'disconnect_key': '9',
            'repeat_key': '0',
            'menu_timeout': 10,
            'instructions': 'Press 1 to connect, 9 to be removed from list',
            'instructions_audio': 'press_1_connect_en.wav',
            'context_suffix': '_usa'
        },
        'canada': {
            'connect_key': '1',
            'disconnect_key': '9', 
            'repeat_key': '0',
            'menu_timeout': 10,
            'instructions': 'Press 1 to connect, 9 to be removed from list',
            'instructions_audio': 'press_1_connect_en.wav',
            'context_suffix': '_canada'
        },
        'mexico': {
            'connect_key': '3',  # México usa tecla 3 ao invés de 1
            'disconnect_key': '9',
            'repeat_key': '0',
            'menu_timeout': 15,
            'instructions': 'Presione 3 para conectar, 9 para salir de la lista',
            'instructions_audio': 'presione_3_conectar_mx.wav',
            'context_suffix': '_mexico'
        },
        'brasil': {
            'connect_key': '1',
            'disconnect_key': '9',
            'repeat_key': '0',
            'menu_timeout': 10,
            'instructions': 'Pressione 1 para conectar, 9 para sair da lista',
            'instructions_audio': 'pressione_1_conectar_br.wav',
            'context_suffix': '_brasil'
        },
        'colombia': {
            'connect_key': '1',
            'disconnect_key': '9',
            'repeat_key': '0',
            'menu_timeout': 12,
            'instructions': 'Presione 1 para conectar, 9 para salir de la lista',
            'instructions_audio': 'presione_1_conectar_co.wav',
            'context_suffix': '_colombia'
        },
        'argentina': {
            'connect_key': '1',
            'disconnect_key': '9',
            'repeat_key': '0',
            'menu_timeout': 10,
            'instructions': 'Presione 1 para conectar, 9 para salir de la lista',
            'instructions_audio': 'presione_1_conectar_ar.wav',
            'context_suffix': '_argentina'
        },
        'chile': {
            'connect_key': '1',
            'disconnect_key': '9',
            'repeat_key': '0',
            'menu_timeout': 10,
            'instructions': 'Presione 1 para conectar, 9 para salir de la lista',
            'instructions_audio': 'presione_1_conectar_cl.wav',
            'context_suffix': '_chile'
        },
        'peru': {
            'connect_key': '1',
            'disconnect_key': '9',
            'repeat_key': '0',
            'menu_timeout': 12,
            'instructions': 'Presione 1 para conectar, 9 para salir de la lista',
            'instructions_audio': 'presione_1_conectar_pe.wav',
            'context_suffix': '_peru'
        },
        'venezuela': {
            'connect_key': '1',
            'disconnect_key': '9',
            'repeat_key': '0',
            'menu_timeout': 12,
            'instructions': 'Presione 1 para conectar, 9 para salir de la lista',
            'instructions_audio': 'presione_1_conectar_ve.wav',
            'context_suffix': '_venezuela'
        },
        'default': {
            'connect_key': '1',
            'disconnect_key': '9',
            'repeat_key': '0',
            'menu_timeout': 10,
            'instructions': 'Press 1 to connect, 9 to be removed from list',
            'instructions_audio': 'press_1_connect_default.wav',
            'context_suffix': '_default'
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_country_config(self, country: str) -> Dict[str, Any]:
        """Obtém configuração DTMF para um país específico."""
        return self.COUNTRY_DTMF_CONFIG.get(country.lower(), 
                                           self.COUNTRY_DTMF_CONFIG['default'])
    
    def get_dtmf_config_for_number(self, destination_number: str) -> Dict[str, Any]:
        """
        Obtém configuração DTMF baseada no número de destino.
        
        Args:
            destination_number: Número de destino
            
        Returns:
            Dict com configurações DTMF específicas do país
        """
        try:
            # Detectar país do número
            country = detectar_pais_numero(destination_number)
            
            # Obter configuração do país
            config = self.get_country_config(country)
            
            # Adicionar informações do país
            config['detected_country'] = country
            config['destination_number'] = destination_number
            
            return config
            
        except Exception as e:
            logger.error(f"Erro ao obter configuração DTMF para {destination_number}: {str(e)}")
            return self.COUNTRY_DTMF_CONFIG['default']
    
    def create_country_specific_context(self, 
                                      base_context_name: str,
                                      destination_number: str,
                                      audio_base_url: str = "https://example.com/audios/") -> Optional[AudioContexto]:
        """
        Cria contexto de áudio específico para um país.
        
        Args:
            base_context_name: Nome base do contexto
            destination_number: Número de destino
            audio_base_url: URL base para áudios
            
        Returns:
            AudioContexto criado ou None se erro
        """
        try:
            # Obter configuração do país
            config = self.get_dtmf_config_for_number(destination_number)
            country = config['detected_country']
            
            # Nome do contexto específico do país
            context_name = f"{base_context_name}{config['context_suffix']}"
            
            # Verificar se já existe
            existing_context = self.db.query(AudioContexto).filter(
                AudioContexto.nome == context_name
            ).first()
            
            if existing_context:
                return existing_context
            
            # Criar novo contexto
            new_context = AudioContexto(
                nome=context_name,
                descricao=f"Contexto para {country.upper()} - {config['instructions']}",
                timeout_dtmf_padrao=config['menu_timeout'],
                detectar_voicemail=True,
                audio_principal_url=f"{audio_base_url}{config['instructions_audio']}",
                audio_voicemail_url=f"{audio_base_url}voicemail_{country}.wav",
                configuracoes_avancadas={
                    'country': country,
                    'connect_key': config['connect_key'],
                    'disconnect_key': config['disconnect_key'],
                    'repeat_key': config['repeat_key'],
                    'instructions': config['instructions']
                }
            )
            
            self.db.add(new_context)
            self.db.commit()
            self.db.refresh(new_context)
            
            # Criar regras específicas para este contexto
            self._create_country_specific_rules(new_context, config)
            
            logger.info(f"Contexto criado para {country}: {context_name}")
            return new_context
            
        except Exception as e:
            logger.error(f"Erro ao criar contexto para {destination_number}: {str(e)}")
            self.db.rollback()
            return None
    
    def _create_country_specific_rules(self, context: AudioContexto, config: Dict[str, Any]):
        """Cria regras específicas para um contexto de país."""
        try:
            # Regra para tecla de conexão (1 para maioria, 3 para México)
            connect_rule = AudioRegra(
                contexto_id=context.id,
                nome=f"Conectar - Tecla {config['connect_key']}",
                descricao=f"Cliente pressionou tecla {config['connect_key']} para conectar",
                prioridade=95,
                estado_origem=EstadoAudio.AGUARDANDO_DTMF,
                evento_disparador=TipoEvento.DTMF_DETECTADO,
                estado_destino=EstadoAudio.CONECTADO,
                condicoes=[
                    {
                        "campo": "dtmf_tecla",
                        "operador": "igual",
                        "valor": config['connect_key']
                    }
                ],
                audio_url=f"https://example.com/audios/connecting_{config['detected_country']}.wav"
            )
            
            # Regra para tecla de desconexão (9)
            disconnect_rule = AudioRegra(
                contexto_id=context.id,
                nome=f"Desconectar - Tecla {config['disconnect_key']}",
                descricao=f"Cliente pressionou tecla {config['disconnect_key']} para sair da lista",
                prioridade=90,
                estado_origem=EstadoAudio.AGUARDANDO_DTMF,
                evento_disparador=TipoEvento.DTMF_DETECTADO,
                estado_destino=EstadoAudio.FINALIZADO,
                condicoes=[
                    {
                        "campo": "dtmf_tecla",
                        "operador": "igual",
                        "valor": config['disconnect_key']
                    }
                ],
                audio_url=f"https://example.com/audios/removed_{config['detected_country']}.wav"
            )
            
            # Regra para repetir (0)
            repeat_rule = AudioRegra(
                contexto_id=context.id,
                nome=f"Repetir - Tecla {config['repeat_key']}",
                descricao=f"Cliente pressionou tecla {config['repeat_key']} para repetir",
                prioridade=85,
                estado_origem=EstadoAudio.AGUARDANDO_DTMF,
                evento_disparador=TipoEvento.DTMF_DETECTADO,
                estado_destino=EstadoAudio.AGUARDANDO_DTMF,
                condicoes=[
                    {
                        "campo": "dtmf_tecla",
                        "operador": "igual",
                        "valor": config['repeat_key']
                    }
                ],
                audio_url=context.audio_principal_url  # Repetir áudio principal
            )
            
            # Regra para teclas inválidas
            invalid_key_rule = AudioRegra(
                contexto_id=context.id,
                nome="Tecla Inválida",
                descricao="Cliente pressionou tecla inválida",
                prioridade=50,
                estado_origem=EstadoAudio.AGUARDANDO_DTMF,
                evento_disparador=TipoEvento.DTMF_DETECTADO,
                estado_destino=EstadoAudio.AGUARDANDO_DTMF,
                condicoes=[
                    {
                        "campo": "dtmf_tecla",
                        "operador": "nao_contem",
                        "valor": f"{config['connect_key']}{config['disconnect_key']}{config['repeat_key']}"
                    }
                ],
                audio_url=f"https://example.com/audios/invalid_key_{config['detected_country']}.wav"
            )
            
            # Adicionar regras ao banco
            rules = [connect_rule, disconnect_rule, repeat_rule, invalid_key_rule]
            for rule in rules:
                self.db.add(rule)
            
            self.db.commit()
            
            logger.info(f"Criadas {len(rules)} regras para contexto {context.nome}")
            
        except Exception as e:
            logger.error(f"Erro ao criar regras para contexto {context.nome}: {str(e)}")
            self.db.rollback()
    
    def get_context_for_number(self, destination_number: str, 
                             base_context_name: str = "Presione") -> Optional[AudioContexto]:
        """
        Obtém ou cria contexto específico para um número.
        
        Args:
            destination_number: Número de destino
            base_context_name: Nome base do contexto
            
        Returns:
            AudioContexto específico do país ou None
        """
        try:
            # Obter configuração do país
            config = self.get_dtmf_config_for_number(destination_number)
            context_name = f"{base_context_name}{config['context_suffix']}"
            
            # Buscar contexto existente
            context = self.db.query(AudioContexto).filter(
                AudioContexto.nome == context_name
            ).first()
            
            if context:
                return context
            
            # Criar contexto se não existir
            return self.create_country_specific_context(
                base_context_name, 
                destination_number
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter contexto para {destination_number}: {str(e)}")
            return None
    
    def update_country_config(self, country: str, new_config: Dict[str, Any]) -> bool:
        """
        Atualiza configuração DTMF para um país (em runtime).
        
        Args:
            country: País a atualizar
            new_config: Nova configuração
            
        Returns:
            bool: True se atualizou com sucesso
        """
        try:
            if country.lower() not in self.COUNTRY_DTMF_CONFIG:
                logger.warning(f"País {country} não encontrado na configuração")
                return False
            
            # Atualizar configuração em runtime
            self.COUNTRY_DTMF_CONFIG[country.lower()].update(new_config)
            
            logger.info(f"Configuração DTMF atualizada para {country}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração para {country}: {str(e)}")
            return False
    
    def get_all_country_configs(self) -> Dict[str, Dict[str, Any]]:
        """Obtém todas as configurações DTMF por país."""
        return self.COUNTRY_DTMF_CONFIG.copy()
    
    def validate_dtmf_key(self, dtmf_key: str, destination_number: str) -> Dict[str, Any]:
        """
        Valida se uma tecla DTMF é válida para um país.
        
        Args:
            dtmf_key: Tecla DTMF pressionada
            destination_number: Número de destino
            
        Returns:
            Dict com resultado da validação
        """
        try:
            config = self.get_dtmf_config_for_number(destination_number)
            
            if dtmf_key == config['connect_key']:
                return {
                    'valid': True,
                    'action': 'connect',
                    'message': 'Conectando chamada',
                    'country': config['detected_country']
                }
            elif dtmf_key == config['disconnect_key']:
                return {
                    'valid': True,
                    'action': 'disconnect',
                    'message': 'Removendo da lista',
                    'country': config['detected_country']
                }
            elif dtmf_key == config['repeat_key']:
                return {
                    'valid': True,
                    'action': 'repeat',
                    'message': 'Repetindo mensagem',
                    'country': config['detected_country']
                }
            else:
                return {
                    'valid': False,
                    'action': 'invalid',
                    'message': f'Tecla inválida. {config["instructions"]}',
                    'country': config['detected_country']
                }
                
        except Exception as e:
            logger.error(f"Erro ao validar tecla DTMF {dtmf_key}: {str(e)}")
            return {
                'valid': False,
                'action': 'error',
                'message': 'Erro interno',
                'country': 'unknown'
            } 