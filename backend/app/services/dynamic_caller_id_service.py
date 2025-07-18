"""
Serviço de Caller ID dinâmico por país.
Gerencia CLIs por país com fallbacks e rotação inteligente.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import json
from app.utils.logger import logger

class DynamicCallerIdService:
    """
    Serviço para gerenciar Caller IDs dinâmicos por país.
    
    Funcionalidades:
    - CLIs específicos por país
    - Rotação inteligente de CLIs
    - Fallback quando não há listas carregadas
    - Controle de uso diário por CLI
    - Geração automática de CLIs por país
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.country_cli_pools = self._load_default_cli_pools()
        self.usage_tracking = {}
        
    def _load_default_cli_pools(self) -> Dict[str, Dict[str, Any]]:
        """Carrega pools de CLIs padrão por país."""
        return {
            "usa": {
                "country_name": "Estados Unidos",
                "country_code": "+1",
                "daily_limit": 100,
                "rotation_strategy": "round_robin",
                "default_clis": self._generate_usa_clis(),
                "fallback_clis": [
                    "+14255551000", "+14255551001", "+14255551002", "+14255551003", "+14255551004",
                    "+15105551000", "+15105551001", "+15105551002", "+15105551003", "+15105551004",
                    "+12135551000", "+12135551001", "+12135551002", "+12135551003", "+12135551004",
                    "+17145551000", "+17145551001", "+17145551002", "+17145551003", "+17145551004",
                    "+18885551000", "+18885551001", "+18885551002", "+18885551003", "+18885551004"
                ],
                "area_codes": ["425", "510", "213", "714", "888", "855", "844", "833"],
                "restrictions": {
                    "max_daily_usage": 100,
                    "cooldown_hours": 24,
                    "avoid_weekends": True
                }
            },
            "canada": {
                "country_name": "Canadá",
                "country_code": "+1",
                "daily_limit": 100,
                "rotation_strategy": "round_robin",
                "default_clis": self._generate_canada_clis(),
                "fallback_clis": [
                    "+14165551000", "+14165551001", "+14165551002", "+14165551003", "+14165551004",
                    "+16045551000", "+16045551001", "+16045551002", "+16045551003", "+16045551004",
                    "+15145551000", "+15145551001", "+15145551002", "+15145551003", "+15145551004",
                    "+14035551000", "+14035551001", "+14035551002", "+14035551003", "+14035551004",
                    "+18555551000", "+18555551001", "+18555551002", "+18555551003", "+18555551004"
                ],
                "area_codes": ["416", "604", "514", "403", "855", "844", "833", "888"],
                "restrictions": {
                    "max_daily_usage": 100,
                    "cooldown_hours": 24,
                    "avoid_weekends": True
                }
            },
            "mexico": {
                "country_name": "México",
                "country_code": "+52",
                "daily_limit": 0,  # Sem limitação
                "rotation_strategy": "random",
                "default_clis": self._generate_mexico_clis(),
                "fallback_clis": [
                    "+525555551000", "+525555551001", "+525555551002", "+525555551003", "+525555551004",
                    "+528155551000", "+528155551001", "+528155551002", "+528155551003", "+528155551004",
                    "+523355551000", "+523355551001", "+523355551002", "+523355551003", "+523355551004",
                    "+526645551000", "+526645551001", "+526645551002", "+526645551003", "+526645551004",
                    "+528005551000", "+528005551001", "+528005551002", "+528005551003", "+528005551004"
                ],
                "area_codes": ["55", "81", "33", "664", "800"],
                "restrictions": {
                    "max_daily_usage": 0,  # Ilimitado
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "brasil": {
                "country_name": "Brasil",
                "country_code": "+55",
                "daily_limit": 0,  # Sem limitação
                "rotation_strategy": "random",
                "default_clis": self._generate_brasil_clis(),
                "fallback_clis": [
                    "+551155551000", "+551155551001", "+551155551002", "+551155551003", "+551155551004",
                    "+552155551000", "+552155551001", "+552155551002", "+552155551003", "+552155551004",
                    "+551355551000", "+551355551001", "+551355551002", "+551355551003", "+551355551004",
                    "+554755551000", "+554755551001", "+554755551002", "+554755551003", "+554755551004",
                    "+558005551000", "+558005551001", "+558005551002", "+558005551003", "+558005551004"
                ],
                "area_codes": ["11", "21", "13", "47", "800"],
                "restrictions": {
                    "max_daily_usage": 0,  # Ilimitado
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "colombia": {
                "country_name": "Colombia",
                "country_code": "+57",
                "daily_limit": 0,  # Sem limitação
                "rotation_strategy": "random",
                "default_clis": self._generate_colombia_clis(),
                "fallback_clis": [
                    "+5715551000", "+5715551001", "+5715551002", "+5715551003", "+5715551004",
                    "+5745551000", "+5745551001", "+5745551002", "+5745551003", "+5745551004",
                    "+5755551000", "+5755551001", "+5755551002", "+5755551003", "+5755551004",
                    "+5785551000", "+5785551001", "+5785551002", "+5785551003", "+5785551004",
                    "+5715551000", "+5715551001", "+5715551002", "+5715551003", "+5715551004"
                ],
                "area_codes": ["1", "4", "5", "8"],
                "restrictions": {
                    "max_daily_usage": 0,  # Ilimitado
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "argentina": {
                "country_name": "Argentina",
                "country_code": "+54",
                "daily_limit": 0,  # Sem limitação
                "rotation_strategy": "random",
                "default_clis": self._generate_argentina_clis(),
                "fallback_clis": [
                    "+541155551000", "+541155551001", "+541155551002", "+541155551003", "+541155551004",
                    "+543415551000", "+543415551001", "+543415551002", "+543415551003", "+543415551004",
                    "+543515551000", "+543515551001", "+543515551002", "+543515551003", "+543515551004",
                    "+542615551000", "+542615551001", "+542615551002", "+542615551003", "+542615551004",
                    "+548005551000", "+548005551001", "+548005551002", "+548005551003", "+548005551004"
                ],
                "area_codes": ["11", "341", "351", "261", "800"],
                "restrictions": {
                    "max_daily_usage": 0,  # Ilimitado
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "chile": {
                "country_name": "Chile",
                "country_code": "+56",
                "daily_limit": 0,  # Sem limitação
                "rotation_strategy": "random",
                "default_clis": self._generate_chile_clis(),
                "fallback_clis": [
                    "+5625551000", "+5625551001", "+5625551002", "+5625551003", "+5625551004",
                    "+5635551000", "+5635551001", "+5635551002", "+5635551003", "+5635551004",
                    "+5645551000", "+5645551001", "+5645551002", "+5645551003", "+5645551004",
                    "+5665551000", "+5665551001", "+5665551002", "+5665551003", "+5665551004",
                    "+5685551000", "+5685551001", "+5685551002", "+5685551003", "+5685551004"
                ],
                "area_codes": ["2", "3", "4", "6", "8"],
                "restrictions": {
                    "max_daily_usage": 0,  # Ilimitado
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "peru": {
                "country_name": "Peru",
                "country_code": "+51",
                "daily_limit": 0,  # Sem limitação
                "rotation_strategy": "random",
                "default_clis": self._generate_peru_clis(),
                "fallback_clis": [
                    "+5115551000", "+5115551001", "+5115551002", "+5115551003", "+5115551004",
                    "+5145551000", "+5145551001", "+5145551002", "+5145551003", "+5145551004",
                    "+5175551000", "+5175551001", "+5175551002", "+5175551003", "+5175551004",
                    "+5165551000", "+5165551001", "+5165551002", "+5165551003", "+5165551004",
                    "+5185551000", "+5185551001", "+5185551002", "+5185551003", "+5185551004"
                ],
                "area_codes": ["1", "4", "7", "6", "8"],
                "restrictions": {
                    "max_daily_usage": 0,  # Ilimitado
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            # Países Adicionais
            "venezuela": {
                "country_name": "Venezuela",
                "country_code": "+58",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_venezuela_clis(),
                "fallback_clis": [
                    "+582125551000", "+582125551001", "+582125551002", "+582125551003", "+582125551004",
                    "+584145551000", "+584145551001", "+584145551002", "+584145551003", "+584145551004"
                ],
                "area_codes": ["212", "414", "424", "416", "261"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "ecuador": {
                "country_name": "Ecuador",
                "country_code": "+593",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_ecuador_clis(),
                "fallback_clis": [
                    "+59325551000", "+59325551001", "+59325551002", "+59325551003", "+59325551004",
                    "+59345551000", "+59345551001", "+59345551002", "+59345551003", "+59345551004"
                ],
                "area_codes": ["2", "4", "5", "7", "3"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "bolivia": {
                "country_name": "Bolivia",
                "country_code": "+591",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_bolivia_clis(),
                "fallback_clis": [
                    "+59125551000", "+59125551001", "+59125551002", "+59125551003", "+59125551004",
                    "+59135551000", "+59135551001", "+59135551002", "+59135551003", "+59135551004"
                ],
                "area_codes": ["2", "3", "4", "6", "7"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "uruguay": {
                "country_name": "Uruguay",
                "country_code": "+598",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_uruguay_clis(),
                "fallback_clis": [
                    "+59825551000", "+59825551001", "+59825551002", "+59825551003", "+59825551004",
                    "+59847551000", "+59847551001", "+59847551002", "+59847551003", "+59847551004"
                ],
                "area_codes": ["2", "47", "432", "463", "99"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "paraguay": {
                "country_name": "Paraguay",
                "country_code": "+595",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_paraguay_clis(),
                "fallback_clis": [
                    "+59521551000", "+59521551001", "+59521551002", "+59521551003", "+59521551004",
                    "+59561551000", "+59561551001", "+59561551002", "+59561551003", "+59561551004"
                ],
                "area_codes": ["21", "61", "71", "331", "336"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "espanha": {
                "country_name": "España",
                "country_code": "+34",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_espanha_clis(),
                "fallback_clis": [
                    "+34915551000", "+34915551001", "+34915551002", "+34915551003", "+34915551004",
                    "+34935551000", "+34935551001", "+34935551002", "+34935551003", "+34935551004"
                ],
                "area_codes": ["91", "93", "95", "96", "985"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "portugal": {
                "country_name": "Portugal",
                "country_code": "+351",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_portugal_clis(),
                "fallback_clis": [
                    "+351215551000", "+351215551001", "+351215551002", "+351215551003", "+351215551004",
                    "+351225551000", "+351225551001", "+351225551002", "+351225551003", "+351225551004"
                ],
                "area_codes": ["21", "22", "232", "239", "25"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "franca": {
                "country_name": "França",
                "country_code": "+33",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_franca_clis(),
                "fallback_clis": [
                    "+33155551000", "+33155551001", "+33155551002", "+33155551003", "+33155551004",
                    "+33455551000", "+33455551001", "+33455551002", "+33455551003", "+33455551004"
                ],
                "area_codes": ["1", "4", "5", "2", "3"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "alemanha": {
                "country_name": "Alemanha",
                "country_code": "+49",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_alemanha_clis(),
                "fallback_clis": [
                    "+49305551000", "+49305551001", "+49305551002", "+49305551003", "+49305551004",
                    "+49895551000", "+49895551001", "+49895551002", "+49895551003", "+49895551004"
                ],
                "area_codes": ["30", "89", "40", "221", "69"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "italia": {
                "country_name": "Itália",
                "country_code": "+39",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_italia_clis(),
                "fallback_clis": [
                    "+39065551000", "+39065551001", "+39065551002", "+39065551003", "+39065551004",
                    "+39025551000", "+39025551001", "+39025551002", "+39025551003", "+39025551004"
                ],
                "area_codes": ["06", "02", "011", "055", "081"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "reino_unido": {
                "country_name": "Reino Unido",
                "country_code": "+44",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_reino_unido_clis(),
                "fallback_clis": [
                    "+44205551000", "+44205551001", "+44205551002", "+44205551003", "+44205551004",
                    "+441615551000", "+441615551001", "+441615551002", "+441615551003", "+441615551004"
                ],
                "area_codes": ["20", "161", "121", "113", "131"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "australia": {
                "country_name": "Austrália",
                "country_code": "+61",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_australia_clis(),
                "fallback_clis": [
                    "+61255551000", "+61255551001", "+61255551002", "+61255551003", "+61255551004",
                    "+61355551000", "+61355551001", "+61355551002", "+61355551003", "+61355551004"
                ],
                "area_codes": ["2", "3", "7", "8", "4"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "nova_zelandia": {
                "country_name": "Nova Zelândia",
                "country_code": "+64",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_nova_zelandia_clis(),
                "fallback_clis": [
                    "+64955551000", "+64955551001", "+64955551002", "+64955551003", "+64955551004",
                    "+64455551000", "+64455551001", "+64455551002", "+64455551003", "+64455551004"
                ],
                "area_codes": ["9", "4", "3", "6", "7"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "india": {
                "country_name": "Índia",
                "country_code": "+91",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_india_clis(),
                "fallback_clis": [
                    "+91115551000", "+91115551001", "+91115551002", "+91115551003", "+91115551004",
                    "+91225551000", "+91225551001", "+91225551002", "+91225551003", "+91225551004"
                ],
                "area_codes": ["11", "22", "33", "44", "80"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "filipinas": {
                "country_name": "Filipinas",
                "country_code": "+63",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_filipinas_clis(),
                "fallback_clis": [
                    "+63255551000", "+63255551001", "+63255551002", "+63255551003", "+63255551004",
                    "+63325551000", "+63325551001", "+63325551002", "+63325551003", "+63325551004"
                ],
                "area_codes": ["2", "32", "33", "34", "35"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "japao": {
                "country_name": "Japão",
                "country_code": "+81",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_japao_clis(),
                "fallback_clis": [
                    "+81355551000", "+81355551001", "+81355551002", "+81355551003", "+81355551004",
                    "+81655551000", "+81655551001", "+81655551002", "+81655551003", "+81655551004"
                ],
                "area_codes": ["3", "6", "45", "52", "92"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "africa_do_sul": {
                "country_name": "África do Sul",
                "country_code": "+27",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_africa_do_sul_clis(),
                "fallback_clis": [
                    "+27115551000", "+27115551001", "+27115551002", "+27115551003", "+27115551004",
                    "+27215551000", "+27215551001", "+27215551002", "+27215551003", "+27215551004"
                ],
                "area_codes": ["11", "21", "31", "41", "51"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            },
            "israel": {
                "country_name": "Israel",
                "country_code": "+972",
                "daily_limit": 0,
                "rotation_strategy": "random",
                "default_clis": self._generate_israel_clis(),
                "fallback_clis": [
                    "+972355551000", "+972355551001", "+972355551002", "+972355551003", "+972355551004",
                    "+972455551000", "+972455551001", "+972455551002", "+972455551003", "+972455551004"
                ],
                "area_codes": ["3", "4", "8", "9", "2"],
                "restrictions": {
                    "max_daily_usage": 0,
                    "cooldown_hours": 0,
                    "avoid_weekends": False
                }
            }
        }
    
    def _generate_usa_clis(self) -> List[str]:
        """Gera CLIs específicos para USA."""
        clis = []
        area_codes = ["425", "510", "213", "714", "888", "855", "844", "833", "201", "646"]
        
        for area_code in area_codes:
            for i in range(100):  # 100 CLIs por área
                number = f"+1{area_code}555{i:04d}"
                clis.append(number)
        
        return clis
    
    def _generate_canada_clis(self) -> List[str]:
        """Gera CLIs específicos para Canadá."""
        clis = []
        area_codes = ["416", "604", "514", "403", "855", "844", "833", "888", "647", "778"]
        
        for area_code in area_codes:
            for i in range(100):  # 100 CLIs por área
                number = f"+1{area_code}555{i:04d}"
                clis.append(number)
        
        return clis
    
    def _generate_mexico_clis(self) -> List[str]:
        """Gera CLIs específicos para México."""
        clis = []
        area_codes = ["55", "81", "33", "664", "800", "222", "443", "228"]
        
        for area_code in area_codes:
            for i in range(200):  # 200 CLIs por área (México sem limitação)
                number = f"+52{area_code}555{i:04d}"
                clis.append(number)
        
        return clis
    
    def _generate_brasil_clis(self) -> List[str]:
        """Gera CLIs específicos para Brasil com formatação correta."""
        clis = []
        # Códigos de área mais utilizados no Brasil
        area_codes = ["11", "21", "31", "41", "47", "48", "51", "61", "62", "71", "81", "85"]
        
        for area_code in area_codes:
            # Gerar números móveis (9 dígitos) - formato: 55 + área + 9 + 8 dígitos
            for i in range(150):  # 150 CLIs móveis por área
                mobile_number = f"55{area_code}9{random.randint(10000000, 99999999)}"
                clis.append(mobile_number)
            
            # Gerar números fixos (8 dígitos) - formato: 55 + área + 8 dígitos
            for i in range(100):  # 100 CLIs fixos por área
                fixed_number = f"55{area_code}{random.randint(20000000, 99999999)}"
                clis.append(fixed_number)
            
            # Gerar números 0800 para algumas áreas
            if area_code in ["11", "21", "31"]:
                for i in range(50):  # 50 CLIs 0800 por área principal
                    toll_free = f"55{area_code}0800{random.randint(1000, 9999)}"
                    clis.append(toll_free)
        
        return clis
    
    def _generate_colombia_clis(self) -> List[str]:
        """Gera CLIs específicos para Colômbia."""
        clis = []
        area_codes = ["1", "4", "5", "8", "2", "7", "6"]
        
        for area_code in area_codes:
            for i in range(200):  # 200 CLIs por área
                number = f"+57{area_code}555{i:04d}"
                clis.append(number)
        
        return clis
    
    def _generate_argentina_clis(self) -> List[str]:
        """Gera CLIs específicos para Argentina."""
        clis = []
        area_codes = ["11", "341", "351", "261", "800", "221", "223", "379"]
        
        for area_code in area_codes:
            for i in range(200):  # 200 CLIs por área
                number = f"+54{area_code}555{i:04d}"
                clis.append(number)
        
        return clis
    
    def _generate_chile_clis(self) -> List[str]:
        """Gera CLIs específicos para Chile."""
        clis = []
        area_codes = ["2", "3", "4", "6", "8", "5", "7", "9"]
        
        for area_code in area_codes:
            for i in range(200):  # 200 CLIs por área
                number = f"+56{area_code}555{i:04d}"
                clis.append(number)
        
        return clis
    
    def _generate_peru_clis(self) -> List[str]:
        """Gera CLIs específicos para Peru."""
        clis = []
        area_codes = ["1", "4", "7", "6", "8", "3", "5", "9"]
        
        for area_code in area_codes:
            for i in range(200):  # 200 CLIs por área
                number = f"+51{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_venezuela_clis(self) -> List[str]:
        """Gera CLIs específicos para Venezuela."""
        clis = []
        area_codes = ["212", "414", "424", "416", "261", "244", "243", "251"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+58{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_ecuador_clis(self) -> List[str]:
        """Gera CLIs específicos para Ecuador."""
        clis = []
        area_codes = ["2", "4", "5", "7", "3", "6", "8", "9"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+593{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_bolivia_clis(self) -> List[str]:
        """Gera CLIs específicos para Bolivia."""
        clis = []
        area_codes = ["2", "3", "4", "6", "7", "8", "5", "9"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+591{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_uruguay_clis(self) -> List[str]:
        """Gera CLIs específicos para Uruguay."""
        clis = []
        area_codes = ["2", "47", "432", "463", "99", "72", "73", "94"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+598{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_paraguay_clis(self) -> List[str]:
        """Gera CLIs específicos para Paraguay."""
        clis = []
        area_codes = ["21", "61", "71", "331", "336", "343", "381", "528"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+595{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_espanha_clis(self) -> List[str]:
        """Gera CLIs específicos para España."""
        clis = []
        area_codes = ["91", "93", "95", "96", "985", "94", "98", "97"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+34{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_portugal_clis(self) -> List[str]:
        """Gera CLIs específicos para Portugal."""
        clis = []
        area_codes = ["21", "22", "232", "239", "25", "26", "27", "28"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+351{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_franca_clis(self) -> List[str]:
        """Gera CLIs específicos para França."""
        clis = []
        area_codes = ["1", "4", "5", "2", "3", "6", "7", "8"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+33{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_alemanha_clis(self) -> List[str]:
        """Gera CLIs específicos para Alemanha."""
        clis = []
        area_codes = ["30", "89", "40", "221", "69", "211", "531", "351"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+49{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_italia_clis(self) -> List[str]:
        """Gera CLIs específicos para Itália."""
        clis = []
        area_codes = ["06", "02", "011", "055", "081", "041", "051", "085"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+39{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_reino_unido_clis(self) -> List[str]:
        """Gera CLIs específicos para Reino Unido."""
        clis = []
        area_codes = ["20", "161", "121", "113", "131", "141", "151", "117"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+44{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_australia_clis(self) -> List[str]:
        """Gera CLIs específicos para Austrália."""
        clis = []
        area_codes = ["2", "3", "7", "8", "4", "5", "6", "9"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+61{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_nova_zelandia_clis(self) -> List[str]:
        """Gera CLIs específicos para Nova Zelândia."""
        clis = []
        area_codes = ["9", "4", "3", "6", "7", "8", "5", "2"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+64{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_india_clis(self) -> List[str]:
        """Gera CLIs específicos para Índia."""
        clis = []
        area_codes = ["11", "22", "33", "44", "80", "40", "20", "79"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+91{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_filipinas_clis(self) -> List[str]:
        """Gera CLIs específicos para Filipinas."""
        clis = []
        area_codes = ["2", "32", "33", "34", "35", "36", "38", "42"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+63{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_japao_clis(self) -> List[str]:
        """Gera CLIs específicos para Japão."""
        clis = []
        area_codes = ["3", "6", "45", "52", "92", "75", "11", "22"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+81{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_africa_do_sul_clis(self) -> List[str]:
        """Gera CLIs específicos para África do Sul."""
        clis = []
        area_codes = ["11", "21", "31", "41", "51", "12", "13", "14"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+27{area_code}555{i:04d}"
                clis.append(number)
        
        return clis

    def _generate_israel_clis(self) -> List[str]:
        """Gera CLIs específicos para Israel."""
        clis = []
        area_codes = ["3", "4", "8", "9", "2", "6", "7", "5"]
        
        for area_code in area_codes:
            for i in range(200):
                number = f"+972{area_code}555{i:04d}"
                clis.append(number)
        
        return clis
    
    def get_next_cli(self, country: str, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtém próximo CLI disponível para um país."""
        try:
            country_key = country.lower()
            
            if country_key not in self.country_cli_pools:
                logger.warning(f"⚠️ País {country} não configurado, usando fallback")
                return self._get_fallback_cli(country)
            
            country_config = self.country_cli_pools[country_key]
            available_clis = country_config["default_clis"]
            
            # Se não há CLIs carregados, usar fallback
            if not available_clis:
                logger.info(f"📞 Usando CLIs fallback para {country}")
                available_clis = country_config["fallback_clis"]
            
            # Aplicar restrições se necessário
            if country_config["daily_limit"] > 0:
                available_clis = self._filter_by_daily_limit(country_key, available_clis)
            
            if not available_clis:
                logger.warning(f"⚠️ Todos os CLIs de {country} esgotados, usando fallback")
                return self._get_fallback_cli(country)
            
            # Selecionar CLI baseado na estratégia
            selected_cli = self._select_cli_by_strategy(
                country_config["rotation_strategy"], 
                available_clis
            )
            
            # Rastrear uso
            self._track_cli_usage(country_key, selected_cli)
            
            logger.info(f"📞 CLI selecionado para {country}: {selected_cli}")
            
            return {
                "cli": selected_cli,
                "country": country,
                "country_code": country_config["country_code"],
                "strategy": country_config["rotation_strategy"],
                "daily_limit": country_config["daily_limit"],
                "usage_count": self._get_cli_usage_count(country_key, selected_cli),
                "source": "default" if selected_cli in country_config["default_clis"] else "fallback"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter CLI para {country}: {str(e)}")
            return self._get_fallback_cli(country)
    
    def _get_fallback_cli(self, country: str) -> Dict[str, Any]:
        """Retorna CLI fallback básico."""
        fallback_clis = {
            # América
            "usa": "+18885551000",
            "canada": "+18885551001", 
            "mexico": "+528005551000",
            "brasil": "+558005551000",
            "colombia": "+5715551000",
            "argentina": "+548005551000",
            "chile": "+5685551000",
            "peru": "+5185551000",
            "venezuela": "+582125551000",
            "ecuador": "+59325551000",
            "bolivia": "+59125551000",
            "uruguay": "+59825551000",
            "paraguay": "+59521551000",
            
            # Europa
            "espanha": "+34915551000",
            "portugal": "+351215551000",
            "franca": "+33155551000",
            "alemanha": "+49305551000",
            "italia": "+39065551000",
            "reino_unido": "+44205551000",
            "suecia": "+46855551000",
            "noruega": "+47255551000",
            "dinamarca": "+45355551000",
            "finlandia": "+358955551000",
            "polonia": "+48225551000",
            "republica_checa": "+420255551000",
            "hungria": "+36155551000",
            "grecia": "+30215551000",
            "turquia": "+90215551000",
            "russia": "+74955551000",
            "ucrania": "+38445551000",
            "holanda": "+31205551000",
            "belgica": "+32255551000",
            "suica": "+41445551000",
            "austria": "+43155551000",
            
            # Ásia
            "india": "+91115551000",
            "filipinas": "+63255551000",
            "japao": "+81355551000",
            "coreia_do_sul": "+82255551000",
            "china": "+86105551000",
            "hong_kong": "+85255551000",
            "taiwan": "+886255551000",
            "vietna": "+84855551000",
            "paquistao": "+92515551000",
            "bangladesh": "+880255551000",
            "sri_lanka": "+94115551000",
            "malasia": "+60355551000",
            "singapura": "+65655551000",
            "tailandia": "+66255551000",
            "indonesia": "+62215551000",
            
            # Oceania
            "australia": "+61255551000",
            "nova_zelandia": "+64955551000",
            
            # África
            "africa_do_sul": "+27115551000",
            "nigeria": "+234155551000",
            "quenia": "+254255551000",
            "marrocos": "+212525551000",
            "egito": "+20255551000",
            
            # Oriente Médio
            "israel": "+972355551000",
            "emirados_arabes": "+971455551000",
            "arabia_saudita": "+966155551000",
            "qatar": "+974355551000",
            "kuwait": "+965255551000",
            "libano": "+961155551000",
            "jordania": "+962655551000",
            "ira": "+98215551000",
            
            # Caribe
            "jamaica": "+18765551000",
            "cuba": "+53755551000",
            "republica_dominicana": "+18095551000",
            
            # América Central
            "costa_rica": "+506255551000",
            "panama": "+507255551000",
            "guatemala": "+502255551000",
            "honduras": "+504255551000",
            "el_salvador": "+503255551000",
            "nicaragua": "+505255551000"
        }
        
        default_cli = fallback_clis.get(country.lower(), "+18885559999")
        
        # Extrair código do país do CLI fallback
        country_code = "+1"
        if default_cli.startswith("+"):
            if default_cli.startswith("+1"):
                country_code = "+1"
            elif default_cli.startswith("+58"):
                country_code = "+58"
            elif default_cli.startswith("+593"):
                country_code = "+593"
            elif default_cli.startswith("+591"):
                country_code = "+591"
            elif default_cli.startswith("+598"):
                country_code = "+598"
            elif default_cli.startswith("+595"):
                country_code = "+595"
            elif default_cli.startswith("+34"):
                country_code = "+34"
            elif default_cli.startswith("+351"):
                country_code = "+351"
            elif default_cli.startswith("+33"):
                country_code = "+33"
            elif default_cli.startswith("+49"):
                country_code = "+49"
            elif default_cli.startswith("+39"):
                country_code = "+39"
            elif default_cli.startswith("+44"):
                country_code = "+44"
            elif default_cli.startswith("+91"):
                country_code = "+91"
            elif default_cli.startswith("+63"):
                country_code = "+63"
            elif default_cli.startswith("+81"):
                country_code = "+81"
            elif default_cli.startswith("+61"):
                country_code = "+61"
            elif default_cli.startswith("+64"):
                country_code = "+64"
            elif default_cli.startswith("+27"):
                country_code = "+27"
            elif default_cli.startswith("+972"):
                country_code = "+972"
            # Adicionar mais conforme necessário
        
        return {
            "cli": default_cli,
            "country": country,
            "country_code": country_code,
            "strategy": "fallback",
            "daily_limit": 0,
            "usage_count": 0,
            "source": "emergency_fallback"
        }
    
    def _filter_by_daily_limit(self, country: str, clis: List[str]) -> List[str]:
        """Filtra CLIs que ainda não atingiram limite diário."""
        if country not in self.country_cli_pools:
            return clis
        
        daily_limit = self.country_cli_pools[country]["daily_limit"]
        if daily_limit == 0:  # Sem limitação
            return clis
        
        available_clis = []
        for cli in clis:
            usage_count = self._get_cli_usage_count(country, cli)
            if usage_count < daily_limit:
                available_clis.append(cli)
        
        return available_clis
    
    def _select_cli_by_strategy(self, strategy: str, clis: List[str]) -> str:
        """Seleciona CLI baseado na estratégia."""
        if strategy == "random":
            return random.choice(clis)
        elif strategy == "round_robin":
            # Implementar round-robin (simplified)
            return clis[len(self.usage_tracking) % len(clis)]
        else:
            return clis[0]  # Default
    
    def _track_cli_usage(self, country: str, cli: str):
        """Rastreia uso de CLI."""
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"{country}:{cli}:{today}"
        
        if key not in self.usage_tracking:
            self.usage_tracking[key] = 0
        
        self.usage_tracking[key] += 1
    
    def _get_cli_usage_count(self, country: str, cli: str) -> int:
        """Obtém contagem de uso de um CLI hoje."""
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"{country}:{cli}:{today}"
        return self.usage_tracking.get(key, 0)
    
    def get_country_cli_stats(self, country: str) -> Dict[str, Any]:
        """Obtém estatísticas de CLIs de um país."""
        country_key = country.lower()
        
        if country_key not in self.country_cli_pools:
            return {"error": f"País {country} não configurado"}
        
        config = self.country_cli_pools[country_key]
        total_clis = len(config["default_clis"]) + len(config["fallback_clis"])
        
        # Contar CLIs em uso hoje
        today = datetime.now().strftime("%Y-%m-%d")
        used_today = 0
        total_calls_today = 0
        
        for key, count in self.usage_tracking.items():
            if key.startswith(f"{country_key}:") and key.endswith(f":{today}"):
                used_today += 1
                total_calls_today += count
        
        return {
            "country": country,
            "country_name": config["country_name"],
            "total_clis": total_clis,
            "default_clis": len(config["default_clis"]),
            "fallback_clis": len(config["fallback_clis"]),
            "daily_limit": config["daily_limit"],
            "used_today": used_today,
            "total_calls_today": total_calls_today,
            "rotation_strategy": config["rotation_strategy"],
            "restrictions": config["restrictions"]
        }
    
    def get_all_countries_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de todos os países."""
        stats = {}
        
        for country in self.country_cli_pools.keys():
            stats[country] = self.get_country_cli_stats(country)
        
        return {
            "countries": stats,
            "total_countries": len(stats),
            "total_clis": sum(stat["total_clis"] for stat in stats.values()),
            "restricted_countries": [
                country for country, stat in stats.items() 
                if stat["daily_limit"] > 0
            ],
            "unrestricted_countries": [
                country for country, stat in stats.items() 
                if stat["daily_limit"] == 0
            ]
        }
    
    def load_custom_cli_list(self, country: str, cli_list: List[str]) -> Dict[str, Any]:
        """Carrega lista personalizada de CLIs para um país."""
        try:
            country_key = country.lower()
            
            if country_key not in self.country_cli_pools:
                logger.warning(f"⚠️ País {country} não existe, criando configuração")
                # Criar configuração básica para país novo
                self.country_cli_pools[country_key] = {
                    "country_name": country.title(),
                    "country_code": "+1",  # Default
                    "daily_limit": 0,
                    "rotation_strategy": "random",
                    "default_clis": [],
                    "fallback_clis": [],
                    "area_codes": [],
                    "restrictions": {
                        "max_daily_usage": 0,
                        "cooldown_hours": 0,
                        "avoid_weekends": False
                    }
                }
            
            # Validar CLIs
            valid_clis = []
            invalid_clis = []
            
            for cli in cli_list:
                if self._validate_cli_format(cli):
                    valid_clis.append(cli)
                else:
                    invalid_clis.append(cli)
            
            # Atualizar lista
            self.country_cli_pools[country_key]["default_clis"] = valid_clis
            
            logger.info(f"✅ Lista de CLIs atualizada para {country}: {len(valid_clis)} válidos")
            
            return {
                "success": True,
                "country": country,
                "loaded_clis": len(valid_clis),
                "invalid_clis": len(invalid_clis),
                "invalid_examples": invalid_clis[:5] if invalid_clis else [],
                "message": f"Lista de CLIs atualizada com sucesso para {country}"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar lista de CLIs para {country}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "country": country
            }
    
    def _validate_cli_format(self, cli: str) -> bool:
        """Valida formato de CLI."""
        # Remover espaços e caracteres especiais
        clean_cli = cli.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Deve começar com + e ter pelo menos 10 dígitos
        if not clean_cli.startswith("+"):
            return False
        
        numbers_only = clean_cli[1:]  # Remove o +
        if not numbers_only.isdigit():
            return False
        
        if len(numbers_only) < 10 or len(numbers_only) > 15:
            return False
        
        return True
    
    def reset_daily_usage(self, country: Optional[str] = None) -> Dict[str, Any]:
        """Reset contadores diários de uso."""
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            if country:
                # Reset apenas para um país
                country_key = country.lower()
                keys_to_remove = [
                    key for key in self.usage_tracking.keys()
                    if key.startswith(f"{country_key}:") and yesterday in key
                ]
            else:
                # Reset para todos os países
                keys_to_remove = [
                    key for key in self.usage_tracking.keys()
                    if yesterday in key
                ]
            
            for key in keys_to_remove:
                del self.usage_tracking[key]
            
            logger.info(f"✅ Reset de uso diário concluído: {len(keys_to_remove)} registros removidos")
            
            return {
                "success": True,
                "reset_country": country or "all",
                "records_removed": len(keys_to_remove),
                "message": "Reset de uso diário concluído com sucesso"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no reset de uso diário: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }