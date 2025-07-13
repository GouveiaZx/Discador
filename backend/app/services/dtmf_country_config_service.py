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
            # América do Norte
            "usa": {
                "country_name": "Estados Unidos",
                "connect_key": "1",
                "disconnect_key": "9", 
                "dnc_key": "2",
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
            
            # América Latina
            "mexico": {
                "country_name": "México",
                "connect_key": "3",
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
                    "speed": "slow"
                },
                "timezone": "America/Mexico_City",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
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
                    "daily_cli_limit": 0,
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
                    "daily_cli_limit": 0,
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
                    "daily_cli_limit": 0,
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
                    "daily_cli_limit": 0,
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
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "venezuela": {
                "country_name": "Venezuela",
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
                    "language": "es-VE",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Caracas",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "ecuador": {
                "country_name": "Ecuador",
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
                    "language": "es-EC",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Guayaquil",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "uruguay": {
                "country_name": "Uruguay",
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
                    "language": "es-UY",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Montevideo",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "bolivia": {
                "country_name": "Bolivia",
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
                    "language": "es-BO",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/La_Paz",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "paraguay": {
                "country_name": "Paraguay",
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
                    "language": "es-PY",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Asuncion",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            
            # Europa
            "espanha": {
                "country_name": "España",
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
                    "language": "es-ES",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Madrid",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "portugal": {
                "country_name": "Portugal",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "portuguese": "Pressione 1 para conectar, 2 para ser removido da lista, 9 para desligar"
                },
                "audio_context": {
                    "language": "pt-PT",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Lisbon",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "italia": {
                "country_name": "Italia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "italian": "Premi 1 per connettere, 2 per essere rimosso dall'elenco, 9 per riagganciare"
                },
                "audio_context": {
                    "language": "it-IT",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Rome",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "franca": {
                "country_name": "França",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "french": "Appuyez sur 1 pour vous connecter, 2 pour être supprimé de la liste, 9 pour raccrocher"
                },
                "audio_context": {
                    "language": "fr-FR",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Paris",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "alemanha": {
                "country_name": "Alemanha",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "german": "Drücken Sie 1 um zu verbinden, 2 um aus der Liste entfernt zu werden, 9 um aufzulegen"
                },
                "audio_context": {
                    "language": "de-DE",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Berlin",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "reino_unido": {
                "country_name": "Reino Unido",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-GB",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/London",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "holanda": {
                "country_name": "Holanda",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "dutch": "Druk op 1 om te verbinden, 2 om uit de lijst te worden verwijderd, 9 om op te hangen"
                },
                "audio_context": {
                    "language": "nl-NL",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Amsterdam",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "belgica": {
                "country_name": "Bélgica",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "french": "Appuyez sur 1 pour vous connecter, 2 pour être supprimé de la liste, 9 pour raccrocher",
                    "dutch": "Druk op 1 om te verbinden, 2 om uit de lijst te worden verwijderd, 9 om op te hangen"
                },
                "audio_context": {
                    "language": "fr-BE",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Brussels",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "suica": {
                "country_name": "Suíça",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "german": "Drücken Sie 1 um zu verbinden, 2 um aus der Liste entfernt zu werden, 9 um aufzulegen",
                    "french": "Appuyez sur 1 pour vous connecter, 2 pour être supprimé de la liste, 9 pour raccrocher"
                },
                "audio_context": {
                    "language": "de-CH",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Zurich",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "austria": {
                "country_name": "Áustria",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "german": "Drücken Sie 1 um zu verbinden, 2 um aus der Liste entfernt zu werden, 9 um aufzulegen"
                },
                "audio_context": {
                    "language": "de-AT",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Vienna",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            
            # Ásia
            "india": {
                "country_name": "Índia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up",
                    "hindi": "जुड़ने के लिए 1 दबाएं, सूची से हटाने के लिए 2 दबाएं, फोन काटने के लिए 9 दबाएं"
                },
                "audio_context": {
                    "language": "en-IN",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Kolkata",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "filipinas": {
                "country_name": "Filipinas",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-PH",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Manila",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "malasia": {
                "country_name": "Malásia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-MY",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Kuala_Lumpur",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "singapura": {
                "country_name": "Singapura",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-SG",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Singapore",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "tailandia": {
                "country_name": "Tailândia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-TH",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Bangkok",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "indonesia": {
                "country_name": "Indonésia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-ID",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Jakarta",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            
            # Oceania
            "australia": {
                "country_name": "Austrália",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-AU",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Australia/Sydney",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "nova_zelandia": {
                "country_name": "Nova Zelândia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-NZ",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Pacific/Auckland",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            
            # África
            "africa_do_sul": {
                "country_name": "África do Sul",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-ZA",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Africa/Johannesburg",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            
            # Oriente Médio
            "israel": {
                "country_name": "Israel",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-IL",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Jerusalem",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            
            # Caribe
            "republica_dominicana": {
                "country_name": "República Dominicana",
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
                    "language": "es-DO",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Santo_Domingo",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "porto_rico": {
                "country_name": "Porto Rico",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "spanish": "Presione 1 para conectar, 2 para ser removido de la lista, 9 para colgar",
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "es-PR",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Puerto_Rico",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            
            # Costa Rica
            "costa_rica": {
                "country_name": "Costa Rica",
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
                    "language": "es-CR",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Costa_Rica",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            
            # Panamá
            "panama": {
                "country_name": "Panamá",
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
                    "language": "es-PA",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Panama",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            
            # Guatemala
            "guatemala": {
                "country_name": "Guatemala",
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
                    "language": "es-GT",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Guatemala",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            
            # Honduras
            "honduras": {
                "country_name": "Honduras",
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
                    "language": "es-HN",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Tegucigalpa",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            
            # El Salvador
            "el_salvador": {
                "country_name": "El Salvador",
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
                    "language": "es-SV",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/El_Salvador",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            
            # Nicaragua
            "nicaragua": {
                "country_name": "Nicaragua",
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
                    "language": "es-NI",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Managua",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            
            # Resto da América do Norte
            "jamaica": {
                "country_name": "Jamaica",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-JM",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Jamaica",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            "cuba": {
                "country_name": "Cuba",
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
                    "language": "es-CU",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "America/Havana",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["08:00-22:00"],
                    "weekend_allowed": True
                }
            },
            
            # Resto da Europa
            "suecia": {
                "country_name": "Suecia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "swedish": "Tryck 1 för att ansluta, 2 för att tas bort från listan, 9 för att lägga på"
                },
                "audio_context": {
                    "language": "sv-SE",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Stockholm",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "noruega": {
                "country_name": "Noruega",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "norwegian": "Trykk 1 for å koble til, 2 for å fjernes fra listen, 9 for å legge på"
                },
                "audio_context": {
                    "language": "no-NO",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Oslo",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "dinamarca": {
                "country_name": "Dinamarca",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "danish": "Tryk 1 for at oprette forbindelse, 2 for at blive fjernet fra listen, 9 for at lægge på"
                },
                "audio_context": {
                    "language": "da-DK",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Copenhagen",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "finlandia": {
                "country_name": "Finlândia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "finnish": "Paina 1 yhdistääksesi, 2 poistuaksesi listalta, 9 lopettaaksesi"
                },
                "audio_context": {
                    "language": "fi-FI",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Helsinki",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "polonia": {
                "country_name": "Polonia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "polish": "Naciśnij 1, aby się połączyć, 2, aby zostać usuniętym z listy, 9, aby się rozłączyć"
                },
                "audio_context": {
                    "language": "pl-PL",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Warsaw",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "republica_checa": {
                "country_name": "República Checa",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "czech": "Stiskněte 1 pro připojení, 2 pro odstranění ze seznamu, 9 pro zavěšení"
                },
                "audio_context": {
                    "language": "cs-CZ",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Prague",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "hungria": {
                "country_name": "Hungria",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "hungarian": "Nyomja meg az 1-et a csatlakozáshoz, a 2-t a listáról való eltávolításhoz, a 9-et a lerakáshoz"
                },
                "audio_context": {
                    "language": "hu-HU",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Budapest",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "grecia": {
                "country_name": "Grécia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "greek": "Πιέστε 1 για σύνδεση, 2 για αφαίρεση από τη λίστα, 9 για κατέβασμα"
                },
                "audio_context": {
                    "language": "el-GR",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Athens",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "turquia": {
                "country_name": "Turquia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "turkish": "Bağlanmak için 1'e, listeden çıkarılmak için 2'ye, kapatmak için 9'a basın"
                },
                "audio_context": {
                    "language": "tr-TR",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Istanbul",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "russia": {
                "country_name": "Rússia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "russian": "Нажмите 1 для подключения, 2 для удаления из списка, 9 для завершения"
                },
                "audio_context": {
                    "language": "ru-RU",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Moscow",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "ucrania": {
                "country_name": "Ucrânia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "ukrainian": "Натисніть 1 для з'єднання, 2 для видалення зі списку, 9 для завершення"
                },
                "audio_context": {
                    "language": "uk-UA",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Europe/Kiev",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            
            # Resto da Ásia
            "japao": {
                "country_name": "Japão",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "japanese": "接続するには1を、リストから削除するには2を、電話を切るには9を押してください"
                },
                "audio_context": {
                    "language": "ja-JP",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Tokyo",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "coreia_do_sul": {
                "country_name": "Coreia do Sul",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "korean": "연결하려면 1번, 목록에서 제거하려면 2번, 전화를 끊으려면 9번을 누르세요"
                },
                "audio_context": {
                    "language": "ko-KR",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Seoul",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "china": {
                "country_name": "China",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "chinese": "请按1连接，按2从列表中移除，按9挂断"
                },
                "audio_context": {
                    "language": "zh-CN",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Shanghai",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "hong_kong": {
                "country_name": "Hong Kong",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "chinese": "請按1連接，按2從列表中移除，按9掛斷",
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "zh-HK",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Hong_Kong",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "taiwan": {
                "country_name": "Taiwan",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "chinese": "請按1連接，按2從列表中移除，按9掛斷"
                },
                "audio_context": {
                    "language": "zh-TW",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Taipei",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": False
                }
            },
            "vietna": {
                "country_name": "Vietnã",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "vietnamese": "Nhấn 1 để kết nối, 2 để bị loại khỏi danh sách, 9 để cúp máy"
                },
                "audio_context": {
                    "language": "vi-VN",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Ho_Chi_Minh",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "paquistao": {
                "country_name": "Paquistão",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "urdu": "کنکشن کے لیے 1 دبائیں، فہرست سے ہٹانے کے لیے 2 دبائیں، فون بند کرنے کے لیے 9 دبائیں"
                },
                "audio_context": {
                    "language": "ur-PK",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Karachi",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "bangladesh": {
                "country_name": "Bangladesh",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "bengali": "সংযোগের জন্য ১ চাপুন, তালিকা থেকে সরানোর জন্য ২ চাপুন, ফোন বন্ধ করার জন্য ৯ চাপুন"
                },
                "audio_context": {
                    "language": "bn-BD",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Dhaka",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "sri_lanka": {
                "country_name": "Sri Lanka",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "sinhala": "සම්බන්ධ වීමට 1 අඟුල්ල, ලැයිස්තුවෙන් ඉවත් කිරීමට 2 අඟුල්ල, දුරකථනය තැබීමට 9 අඟුල්ල"
                },
                "audio_context": {
                    "language": "si-LK",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Colombo",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            
            # Resto da África
            "nigeria": {
                "country_name": "Nigéria",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-NG",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Africa/Lagos",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "quenia": {
                "country_name": "Quênia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "english": "Press 1 to connect, 2 to be removed from list, 9 to hang up"
                },
                "audio_context": {
                    "language": "en-KE",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Africa/Nairobi",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "marrocos": {
                "country_name": "Marrocos",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "arabic": "اضغط 1 للاتصال، 2 لإزالة من القائمة، 9 لإنهاء المكالمة"
                },
                "audio_context": {
                    "language": "ar-MA",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Africa/Casablanca",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "egito": {
                "country_name": "Egito",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "arabic": "اضغط 1 للاتصال، 2 لإزالة من القائمة، 9 لإنهاء المكالمة"
                },
                "audio_context": {
                    "language": "ar-EG",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Africa/Cairo",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            
            # Oriente Médio
            "emirados_arabes": {
                "country_name": "Emirados Árabes Unidos",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "arabic": "اضغط 1 للاتصال، 2 لإزالة من القائمة، 9 لإنهاء المكالمة"
                },
                "audio_context": {
                    "language": "ar-AE",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Dubai",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "arabia_saudita": {
                "country_name": "Arábia Saudita",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "arabic": "اضغط 1 للاتصال، 2 لإزالة من القائمة، 9 لإنهاء المكالمة"
                },
                "audio_context": {
                    "language": "ar-SA",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Riyadh",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "qatar": {
                "country_name": "Qatar",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "arabic": "اضغط 1 للاتصال، 2 لإزالة من القائمة، 9 لإنهاء المكالمة"
                },
                "audio_context": {
                    "language": "ar-QA",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Qatar",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "kuwait": {
                "country_name": "Kuwait",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "arabic": "اضغط 1 للاتصال، 2 لإزالة من القائمة، 9 لإنهاء المكالمة"
                },
                "audio_context": {
                    "language": "ar-KW",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Kuwait",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "libano": {
                "country_name": "Líbano",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "arabic": "اضغط 1 للاتصال، 2 لإزالة من القائمة، 9 لإنهاء المكالمة"
                },
                "audio_context": {
                    "language": "ar-LB",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Beirut",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "jordania": {
                "country_name": "Jordânia",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "arabic": "اضغط 1 للاتصال، 2 لإزالة من القائمة، 9 لإنهاء المكالمة"
                },
                "audio_context": {
                    "language": "ar-JO",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Amman",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
                    "weekend_allowed": True
                }
            },
            "ira": {
                "country_name": "Irã",
                "connect_key": "1",
                "disconnect_key": "9",
                "dnc_key": "2",
                "repeat_key": "0",
                "available_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                "menu_timeout": 10,
                "instructions": {
                    "persian": "برای اتصال ۱ را فشار دهید، برای حذف از لیست ۲ را فشار دهید، برای قطع تماس ۹ را فشار دهید"
                },
                "audio_context": {
                    "language": "fa-IR",
                    "voice": "female",
                    "speed": "normal"
                },
                "timezone": "Asia/Tehran",
                "calling_restrictions": {
                    "daily_cli_limit": 0,
                    "time_restrictions": ["09:00-21:00"],
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