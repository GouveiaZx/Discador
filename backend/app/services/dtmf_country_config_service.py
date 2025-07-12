"""
Serviço de configuração DTMF por país com opções flexíveis.
Permite configurar diferentes teclas por país para transferência e lista negra.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.utils.logger import logger

class DTMFCountryConfigService:
    """
    Serviço para gerenciar configurações DTMF específicas por país.
    
    Funcionalidades:
    - Configuração de teclas de transferência por país
    - Configuração de teclas para lista negra (DNC)
    - Configuração de timeouts e instruções
    - Fallbacks para países não configurados
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.default_configs = self._load_default_configs()
        
    def _load_default_configs(self) -> Dict[str, Dict[str, Any]]:
        """Carrega configurações padrão por país."""
        return {
            "usa": {
                "country_name": "Estados Unidos",
                "connect_key": "1",
                "disconnect_key": "9", 
                "dnc_key": "2",  # Do Not Call
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up",
                    "spanish": "Presione 1 para conectar, 2 para ser removido de la lista, 9 para colgar"
                },
                "audio_context": {
                    "language": "en-US",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/New_York",
                "calling_restrictions": {
                    "daily_cli_limit": 100,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "canada": {
                "country_name": "Canadá",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up",
                    "french": "Appuyez sur 1 pour vous connecter, 2 pour être supprimé de la liste, 9 pour raccrocher"
                },
                "audio_context": {
                    "language": "en-CA",
                    "voice": "female", 
                    "speed": "normal"
                },
                "timezone": "America/Toronto",
                "calling_restrictions": {
                    "daily_cli_limit": 100,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "mexico": {
                "country_name": "México",
                "connect_key": "3",  # Usar 3 ao invés de 1 por causa das contestadoras
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 12,
                "instructions": {
                    "spanish": "Presione 3 para conectar, 2 para ser removido de la lista, 9 para colgar",
                    "english": "Press 3 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "es-MX",
                    "voice": "female",
                    "speed": "slow"  # Mais devagar para melhor compreensão
                },
                "timezone": "America/Mexico_City",
                "calling_restrictions": {
                    "daily_cli_limit": 0,  # Sem limitação
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "brasil": {
                "country_name": "Brasil",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "portuguese": "Pressione 1 para conectar, 2 para ser removido da lista, 9 para desligar",
                    "spanish": "Presione 1 para conectar, 2 para ser removido de la lista, 9 para colgar"
                },
                "audio_context": {
                    "language": "pt-BR",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Sao_Paulo",
                "calling_restrictions": {
                    "daily_cli_limit": 0,  # Sem limitação
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "colombia": {
                "country_name": "Colombia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "spanish": "Presione 1 para conectar, 2 para ser removido de la lista, 9 para colgar"
                },
                "audio_context": {
                    "language": "es-CO",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Bogota",
                "calling_restrictions": {
                    "daily_cli_limit": 0,  # Sem limitação
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "argentina": {
                "country_name": "Argentina",
                "connect_key": "1",
                "disconnect_key": "9", 
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "spanish": "Presione 1 para conectar, 2 para ser removido de la lista, 9 para colgar"
                },
                "audio_context": {
                    "language": "es-AR",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Argentina/Buenos_Aires",
                "calling_restrictions": {
                    "daily_cli_limit": 0,  # Sem limitação
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "chile": {
                "country_name": "Chile",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2", 
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "spanish": "Presione 1 para conectar, 2 para ser removido de la lista, 9 para colgar"
                },
                "audio_context": {
                    "language": "es-CL",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Santiago",
                "calling_restrictions": {
                    "daily_cli_limit": 0,  # Sem limitação
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "peru": {
                "country_name": "Peru",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0", 
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "spanish": "Presione 1 para conectar, 2 para ser removido de la lista, 9 para colgar"
                },
                "audio_context": {
                    "language": "es-PE",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Lima",
                "calling_restrictions": {
                    "daily_cli_limit": 0,  # Sem limitação
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            }
        }
    
    def get_country_config(self, country: str) -> Dict[str, Any]:
        """Obtém configuração de um país específico."""
        country_key = country.lower()
        
        if country_key in self.default_configs:
            config = self.default_configs[country_key].copy()
            logger.info(f"📞 Configuração DTMF obtida para {country}: connect_key={config['connect_key']}")
            return config
        else:
            # Fallback para países não configurados
            fallback_config = {
                "country_name": country.title(),
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "spanish": "Presione 1 para conectar, 2 para ser removido de la lista, 9 para colgar"
                },
                "audio_context": {
                    "language": "es",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "UTC",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            }
            logger.warning(f"⚠️ País {country} não configurado, usando fallback")
            return fallback_config
    
    def get_all_country_configs(self) -> Dict[str, Dict[str, Any]]:
        """Obtém todas as configurações de países."""
        return self.default_configs.copy()
    
    def update_country_config(self, country: str, new_config: Dict[str, Any]) -> bool:
        """Atualiza configuração de um país."""
        try:
            country_key = country.lower()
            
            if country_key not in self.default_configs:
                # Criar nova configuração para país não existente
                self.default_configs[country_key] = self._get_default_country_template()
            
            # Atualizar configuração
            current_config = self.default_configs[country_key]
            
            # Atualizar campos básicos
            for key in ["connect_key", "disconnect_key", "dnc_key", "repeat_key", "menu_timeout"]:
                if key in new_config:
                    current_config[key] = new_config[key]
            
            # Atualizar instruções
            if "instructions" in new_config:
                current_config["instructions"].update(new_config["instructions"])
            
            # Atualizar contexto de áudio
            if "audio_context" in new_config:
                current_config["audio_context"].update(new_config["audio_context"])
            
            # Atualizar restrições de chamadas
            if "calling_restrictions" in new_config:
                current_config["calling_restrictions"].update(new_config["calling_restrictions"])
            
            logger.info(f"✅ Configuração DTMF atualizada para {country}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar configuração para {country}: {str(e)}")
            return False
    
    def _get_default_country_template(self) -> Dict[str, Any]:
        """Template padrão para novos países."""
        return {
            "country_name": "",
            "connect_key": "1",
            "disconnect_key": "9",
            "dnc_key": "2",
            "repeat_key": "0",
            "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            "menu_timeout": 10,
            "instructions": {
                "spanish": "Presione 1 para conectar, 2 para ser removido de la lista, 9 para colgar"
            },
            "audio_context": {
                "language": "es",
                "voice": "female",
                "speed": "normal"
            },
            "timezone": "UTC",
            "calling_restrictions": {
                "daily_cli_limit": 0,
                "time_restrictions": ["08:00-22:00"],
                "weekend_allowed": True
            }
        }
    
    def get_connect_key(self, country: str) -> str:
        """Obtém tecla de conexão para um país."""
        config = self.get_country_config(country)
        return config["connect_key"]
    
    def get_dnc_key(self, country: str) -> str:
        """Obtém tecla de lista negra (Do Not Call) para um país."""
        config = self.get_country_config(country)
        return config["dnc_key"]
    
    def get_available_keys(self, country: str) -> List[str]:
        """Obtém teclas disponíveis para um país."""
        config = self.get_country_config(country)
        return config["available_options"]
    
    def get_instructions(self, country: str, language: str = "spanish") -> str:
        """Obtém instruções em idioma específico para um país."""
        config = self.get_country_config(country)
        instructions = config["instructions"]
        
        if language in instructions:
            return instructions[language]
        elif "spanish" in instructions:
            return instructions["spanish"]
        else:
            return list(instructions.values())[0]
    
    def validate_key_assignment(self, country: str, connect_key: str, dnc_key: str) -> Dict[str, Any]:
        """Valida se as teclas atribuídas não conflitam."""
        config = self.get_country_config(country)
        available_keys = config["available_options"]
        
        errors = []
        
        if connect_key not in available_keys:
            errors.append(f"Tecla de conexão '{connect_key}' não está disponível")
            
        if dnc_key not in available_keys:
            errors.append(f"Tecla DNC '{dnc_key}' não está disponível")
        
        if connect_key == dnc_key:
            errors.append("Tecla de conexão e DNC não podem ser iguais")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "suggestions": {
                "connect_key": connect_key if connect_key in available_keys else "1",
                "dnc_key": dnc_key if dnc_key in available_keys and dnc_key != connect_key else "2"
            }
        }
    
    def generate_asterisk_dialplan(self, country: str) -> str:
        """Gera dialplan do Asterisk para um país."""
        config = self.get_country_config(country)
        
        dialplan = f"""
; Configuração DTMF para {config['country_name']} ({country.upper()})
[dtmf-{country.lower()}]
exten => s,1,NoOp(DTMF Handler for {config['country_name']})
exten => s,n,Set(TIMEOUT(digit)={config['menu_timeout']})
exten => s,n,Set(TIMEOUT(response)={config['menu_timeout']})
exten => s,n,Read(DTMF_INPUT,,1,,1,{config['menu_timeout']})

; Tecla de conexão ({config['connect_key']})
exten => {config['connect_key']},1,NoOp(Connect key pressed)
exten => {config['connect_key']},n,Set(__CALL_RESULT=CONNECT)
exten => {config['connect_key']},n,Return()

; Tecla de lista negra/DNC ({config['dnc_key']})
exten => {config['dnc_key']},1,NoOp(DNC key pressed)
exten => {config['dnc_key']},n,Set(__CALL_RESULT=DNC)
exten => {config['dnc_key']},n,AGI(add_to_blacklist.py,${{CALLERID(num)}})
exten => {config['dnc_key']},n,Return()

; Tecla de desconexão ({config['disconnect_key']})
exten => {config['disconnect_key']},1,NoOp(Disconnect key pressed)
exten => {config['disconnect_key']},n,Set(__CALL_RESULT=HANGUP)
exten => {config['disconnect_key']},n,Hangup()

; Tecla de repetição ({config['repeat_key']})
exten => {config['repeat_key']},1,NoOp(Repeat key pressed)
exten => {config['repeat_key']},n,Goto(s,1)

; Timeout ou entrada inválida
exten => t,1,NoOp(Timeout)
exten => t,n,Set(__CALL_RESULT=TIMEOUT)
exten => t,n,Return()

exten => i,1,NoOp(Invalid input)
exten => i,n,Goto(s,1)
"""
        return dialplan 