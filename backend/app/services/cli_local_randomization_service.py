"""
Serviço de CLI Local Randomization
Gera números de Caller ID que parecem locais para aumentar taxa de resposta.

Estratégias por país:
- USA: Mantém Area Code + prefixo personalizado + aleatorização
- Brasil: DDDs + aleatorização inteligente  
- México: Códigos locais + aleatorização dos últimos dígitos
"""

import random
import re
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.utils.logger import logger

class CliLocalRandomizationService:
    """
    Serviço para gerar CLIs locais baseados no número de destino.
    Cada país tem estratégias específicas para parecer local.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.country_patterns = self._load_country_patterns()
        self.usage_tracking = {}
        
    def _load_country_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Carrega padrões de aleatorização por país."""
        return {
            "usa": {
                "name": "Estados Unidos",
                "country_code": "+1",
                "strategy": "area_code_preservation",
                "area_codes": {
                    # Principais área codes USA com prefixos comuns
                    "205": ["220", "221", "222", "250", "251", "290", "320", "321"],  # Alabama
                    "251": ["220", "221", "222", "250", "251", "290", "320", "321"],  # Alabama Mobile
                    "256": ["220", "221", "222", "250", "251", "290", "320", "321"],  # Alabama North
                    "305": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Miami
                    "321": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Orlando
                    "407": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Orlando
                    "561": ["200", "201", "220", "221", "222", "250", "290", "300"],  # West Palm Beach
                    "786": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Miami
                    "813": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Tampa
                    "727": ["200", "201", "220", "221", "222", "250", "290", "300"],  # St. Petersburg
                    "954": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Fort Lauderdale
                    "239": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Naples
                    "850": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Tallahassee
                    "863": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Lakeland
                    "352": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Gainesville
                    "386": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Daytona Beach
                    "941": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Sarasota
                    "772": ["200", "201", "220", "221", "222", "250", "290", "300"],  # Port St. Lucie
                    
                    # California
                    "213": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Los Angeles
                    "323": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Los Angeles
                    "310": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Beverly Hills
                    "424": ["200", "201", "220", "221", "250", "290", "300", "320"],  # West LA
                    "818": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Fernando Valley
                    "747": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Fernando Valley
                    "626": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Pasadena
                    "661": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Palmdale
                    "714": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Orange County
                    "949": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Orange County
                    "657": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Orange County
                    "415": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Francisco
                    "628": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Francisco
                    "510": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Oakland
                    "925": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Walnut Creek
                    "650": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Palo Alto
                    "408": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Jose
                    "669": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Jose
                    "831": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Monterey
                    "805": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Santa Barbara
                    "559": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Fresno
                    "209": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Stockton
                    "707": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Santa Rosa
                    "760": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Palm Springs
                    "442": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Imperial Valley
                    "858": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Diego
                    "619": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Diego
                    "935": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Diego
                    
                    # Texas
                    "214": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Dallas
                    "469": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Dallas
                    "972": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Dallas
                    "945": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Dallas
                    "713": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Houston
                    "281": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Houston
                    "832": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Houston
                    "346": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Houston
                    "210": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Antonio
                    "726": ["200", "201", "220", "221", "250", "290", "300", "320"],  # San Antonio
                    "512": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Austin
                    "737": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Austin
                    "817": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Fort Worth
                    "682": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Fort Worth
                    
                    # New York
                    "212": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Manhattan
                    "646": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Manhattan
                    "332": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Manhattan
                    "917": ["200", "201", "220", "221", "250", "290", "300", "320"],  # NYC Mobile
                    "718": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Brooklyn/Queens
                    "347": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Brooklyn/Queens
                    "929": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Brooklyn/Queens
                    "516": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Long Island
                    "631": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Long Island
                    "845": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Hudson Valley
                    "914": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Westchester
                },
                "format": "{country_code}{area_code}{prefix}{suffix}",
                "randomization": {
                    "preserve_area_code": True,
                    "custom_prefix_length": 3,
                    "random_suffix_length": 4,
                    "avoid_repeated_digits": True
                }
            },
            
            "canada": {
                "name": "Canadá",
                "country_code": "+1",
                "strategy": "area_code_preservation",
                "area_codes": {
                    # Canada area codes com prefixos comuns
                    "416": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Toronto
                    "647": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Toronto
                    "437": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Toronto
                    "905": ["200", "201", "220", "221", "250", "290", "300", "320"],  # GTA
                    "289": ["200", "201", "220", "221", "250", "290", "300", "320"],  # GTA
                    "365": ["200", "201", "220", "221", "250", "290", "300", "320"],  # GTA
                    "613": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Ottawa
                    "343": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Ottawa
                    "514": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Montreal
                    "438": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Montreal
                    "450": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Montreal suburbs
                    "418": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Quebec City
                    "581": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Quebec City
                    "403": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Calgary
                    "587": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Calgary
                    "825": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Calgary
                    "780": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Edmonton
                    "431": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Manitoba
                    "204": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Manitoba
                    "306": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Saskatchewan
                    "639": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Saskatchewan
                    "604": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Vancouver
                    "778": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Vancouver
                    "236": ["200", "201", "220", "221", "250", "290", "300", "320"],  # Vancouver
                    "250": ["200", "201", "220", "221", "250", "290", "300", "320"],  # BC Interior
                },
                "format": "{country_code}{area_code}{prefix}{suffix}",
                "randomization": {
                    "preserve_area_code": True,
                    "custom_prefix_length": 3,
                    "random_suffix_length": 4,
                    "avoid_repeated_digits": True
                }
            },
            
            "mexico": {
                "name": "México",
                "country_code": "+52",
                "strategy": "local_area_randomization",
                "area_codes": {
                    # México - códigos de área principais
                    "55": ["1000", "1100", "1200", "1300", "1400", "1500", "1600", "1700", "1800", "1900", "2000", "2100", "2200", "2300", "2400", "2500", "2600", "2700", "2800", "2900", "3000", "3100", "3200", "3300", "3400", "3500", "3600", "3700", "3800", "3900", "4000", "4100", "4200", "4300", "4400", "4500", "4600", "4700", "4800", "4900", "5000", "5100", "5200", "5300", "5400", "5500", "5600", "5700", "5800", "5900", "6000", "6100", "6200", "6300", "6400", "6500", "6600", "6700", "6800", "6900", "7000", "7100", "7200", "7300", "7400", "7500", "7600", "7700", "7800", "7900", "8000", "8100", "8200", "8300", "8400", "8500", "8600", "8700", "8800", "8900", "9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # CDMX
                    "81": ["1000", "1100", "1200", "1300", "1400", "1500", "1600", "1700", "1800", "1900", "2000", "2100", "2200", "2300", "2400", "2500", "3000", "3100", "3200", "3300", "3400", "3500", "8000", "8100", "8200", "8300", "8400", "8500"],  # Monterrey
                    "33": ["1000", "1100", "1200", "1300", "1400", "1500", "1600", "1700", "1800", "1900", "2000", "2100", "2200", "2300", "2400", "2500", "3000", "3100", "3200", "3300", "3400", "3500", "3600", "3700", "3800", "3900"],  # Guadalajara
                    "664": ["100", "101", "102", "103", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171", "180", "181", "190", "191", "200", "201", "210", "211", "220", "221", "230", "231"],  # Tijuana
                    "656": ["100", "101", "102", "103", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171", "180", "181", "190", "191", "200", "201", "210", "211", "220", "221", "230", "231"],  # Juárez
                    "222": ["100", "101", "102", "103", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171", "180", "181", "190", "191", "200", "201", "210", "211", "220", "221", "230", "231", "240", "241", "250", "251"],  # Puebla
                    "443": ["100", "101", "102", "103", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171", "180", "181", "190", "191", "200", "201", "210", "211", "220", "221", "230", "231"],  # Morelia
                    "228": ["100", "101", "102", "103", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171", "180", "181", "190", "191", "200", "201", "210", "211", "220", "221", "230", "231"],  # Veracruz
                    "998": ["100", "101", "102", "103", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171", "180", "181", "190", "191", "200", "201", "210", "211", "220", "221", "230", "231"],  # Cancún
                    "999": ["100", "101", "102", "103", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171", "180", "181", "190", "191", "200", "201", "210", "211", "220", "221", "230", "231"],  # Mérida
                    "844": ["100", "101", "102", "103", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171", "180", "181", "190", "191", "200", "201", "210", "211", "220", "221", "230", "231"],  # Saltillo
                    "867": ["100", "101", "102", "103", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171", "180", "181", "190", "191", "200", "201", "210", "211", "220", "221", "230", "231"],  # Nuevo Laredo
                    "686": ["100", "101", "102", "103", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171", "180", "181", "190", "191", "200", "201", "210", "211", "220", "221", "230", "231"],  # Mexicali
                },
                "format": "{country_code}{area_code}{random_number}",
                "randomization": {
                    "preserve_area_code": True,
                    "random_number_length": 7,  # 7 dígitos após o código de área
                    "custom_pattern": True,
                    "avoid_repeated_digits": True
                }
            },
            
            "brasil": {
                "name": "Brasil",
                "country_code": "+55",
                "strategy": "ddd_preservation",
                "area_codes": {
                    # Brasil - DDDs principais
                    "11": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900", "8000", "8100", "8200", "8300", "8400", "8500", "7000", "7100", "7200", "7300", "7400", "7500", "6000", "6100", "6200", "6300", "6400", "6500", "5000", "5100", "5200", "5300", "5400", "5500"],  # São Paulo
                    "21": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900", "8000", "8100", "8200", "8300", "8400", "8500", "7000", "7100", "7200", "7300", "7400", "7500", "6000", "6100", "6200", "6300", "6400", "6500"],  # Rio de Janeiro
                    "31": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900", "8000", "8100", "8200", "8300", "8400", "8500", "7000", "7100", "7200", "7300", "7400", "7500"],  # Belo Horizonte
                    "41": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900", "8000", "8100", "8200", "8300", "8400", "8500"],  # Curitiba
                    "51": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900", "8000", "8100", "8200", "8300", "8400", "8500"],  # Porto Alegre
                    "85": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900", "8000", "8100", "8200", "8300", "8400", "8500"],  # Fortaleza
                    "71": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900", "8000", "8100", "8200", "8300", "8400", "8500"],  # Salvador
                    "81": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900", "8000", "8100", "8200", "8300", "8400", "8500"],  # Recife
                    "62": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900", "8000", "8100", "8200", "8300", "8400", "8500"],  # Goiânia
                    "27": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # Vitória
                    "47": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # Joinville
                    "48": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # Florianópolis
                    "19": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # Campinas
                    "12": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # São José dos Campos
                    "13": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # Santos
                    "14": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # Bauru
                    "15": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # Sorocaba
                    "16": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # Ribeirão Preto
                    "17": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # São José do Rio Preto
                    "18": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],  # Presidente Prudente
                },
                "format": "{country_code}{area_code}{prefix}{suffix}",
                "randomization": {
                    "preserve_area_code": True,
                    "mobile_indicator": "9",  # 9 para celular
                    "custom_prefix_length": 4,
                    "random_suffix_length": 4,
                    "avoid_repeated_digits": True
                }
            },
            
            "colombia": {
                "name": "Colômbia",
                "country_code": "+57",
                "strategy": "area_code_preservation",
                "area_codes": {
                    "1": ["300", "301", "302", "303", "304", "305", "310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323", "324", "325"],  # Bogotá
                    "4": ["300", "301", "302", "303", "304", "305", "310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323", "324", "325"],  # Medellín
                    "5": ["300", "301", "302", "303", "304", "305", "310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323", "324", "325"],  # Barranquilla
                    "2": ["300", "301", "302", "303", "304", "305", "310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323", "324", "325"],  # Cali
                    "7": ["300", "301", "302", "303", "304", "305", "310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323", "324", "325"],  # Bucaramanga
                    "8": ["300", "301", "302", "303", "304", "305", "310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323", "324", "325"],  # Villavicencio
                },
                "format": "{country_code}{area_code}{prefix}{suffix}",
                "randomization": {
                    "preserve_area_code": True,
                    "custom_prefix_length": 3,
                    "random_suffix_length": 4,
                    "avoid_repeated_digits": True
                }
            },
            
            "argentina": {
                "name": "Argentina",
                "country_code": "+54",
                "strategy": "area_code_preservation",
                "area_codes": {
                    "11": ["4000", "4100", "4200", "4300", "4400", "4500", "4600", "4700", "4800", "4900", "5000", "5100", "5200", "5300", "5400", "5500", "6000", "6100", "6200", "6300", "6400", "6500"],  # Buenos Aires
                    "341": ["400", "401", "402", "403", "404", "405", "410", "411", "412", "413", "414", "415", "420", "421", "422", "423", "424", "425", "430", "431", "432", "433", "434", "435"],  # Rosario
                    "351": ["400", "401", "402", "403", "404", "405", "410", "411", "412", "413", "414", "415", "420", "421", "422", "423", "424", "425", "430", "431", "432", "433", "434", "435"],  # Córdoba
                    "261": ["400", "401", "402", "403", "404", "405", "410", "411", "412", "413", "414", "415", "420", "421", "422", "423", "424", "425", "430", "431", "432", "433", "434", "435"],  # Mendoza
                    "221": ["400", "401", "402", "403", "404", "405", "410", "411", "412", "413", "414", "415", "420", "421", "422", "423", "424", "425", "430", "431", "432", "433", "434", "435"],  # La Plata
                    "223": ["400", "401", "402", "403", "404", "405", "410", "411", "412", "413", "414", "415", "420", "421", "422", "423", "424", "425", "430", "431", "432", "433", "434", "435"],  # Mar del Plata
                },
                "format": "{country_code}9{area_code}{prefix}{suffix}",
                "randomization": {
                    "preserve_area_code": True,
                    "mobile_indicator": "9",
                    "custom_prefix_length": 4,
                    "random_suffix_length": 4,
                    "avoid_repeated_digits": True
                }
            },
            
            "chile": {
                "name": "Chile",
                "country_code": "+56",
                "strategy": "area_code_preservation",
                "area_codes": {
                    "2": ["2000", "2100", "2200", "2300", "2400", "2500", "2600", "2700", "2800", "2900", "3000", "3100", "3200", "3300", "3400", "3500", "6000", "6100", "6200", "6300", "6400", "6500", "7000", "7100", "7200", "7300", "7400", "7500", "8000", "8100", "8200", "8300", "8400", "8500", "9000", "9100", "9200", "9300", "9400", "9500"],  # Santiago
                    "33": ["200", "201", "202", "203", "204", "205", "210", "211", "212", "213", "214", "215", "220", "221", "222", "223", "224", "225", "230", "231", "232", "233", "234", "235"],  # Valparaíso
                    "41": ["200", "201", "202", "203", "204", "205", "210", "211", "212", "213", "214", "215", "220", "221", "222", "223", "224", "225", "230", "231", "232", "233", "234", "235"],  # Concepción
                    "55": ["200", "201", "202", "203", "204", "205", "210", "211", "212", "213", "214", "215", "220", "221", "222", "223", "224", "225", "230", "231", "232", "233", "234", "235"],  # Antofagasta
                    "57": ["200", "201", "202", "203", "204", "205", "210", "211", "212", "213", "214", "215", "220", "221", "222", "223", "224", "225", "230", "231", "232", "233", "234", "235"],  # Iquique
                    "51": ["200", "201", "202", "203", "204", "205", "210", "211", "212", "213", "214", "215", "220", "221", "222", "223", "224", "225", "230", "231", "232", "233", "234", "235"],  # La Serena
                },
                "format": "{country_code}{area_code}{prefix}{suffix}",
                "randomization": {
                    "preserve_area_code": True,
                    "custom_prefix_length": 4,
                    "random_suffix_length": 4,
                    "avoid_repeated_digits": True
                }
            },
            
            "peru": {
                "name": "Peru",
                "country_code": "+51",
                "strategy": "area_code_preservation",
                "area_codes": {
                    "1": ["900", "901", "902", "903", "904", "905", "910", "911", "912", "913", "914", "915", "920", "921", "922", "923", "924", "925", "930", "931", "932", "933", "934", "935", "940", "941", "942", "943", "944", "945", "950", "951", "952", "953", "954", "955", "960", "961", "962", "963", "964", "965", "970", "971", "972", "973", "974", "975", "980", "981", "982", "983", "984", "985", "990", "991", "992", "993", "994", "995"],  # Lima
                    "4": ["900", "901", "902", "903", "904", "905", "910", "911", "912", "913", "914", "915", "920", "921", "922", "923", "924", "925", "930", "931", "932", "933", "934", "935"],  # Arequipa
                    "7": ["900", "901", "902", "903", "904", "905", "910", "911", "912", "913", "914", "915", "920", "921", "922", "923", "924", "925", "930", "931", "932", "933", "934", "935"],  # Cusco
                    "6": ["900", "901", "902", "903", "904", "905", "910", "911", "912", "913", "914", "915", "920", "921", "922", "923", "924", "925", "930", "931", "932", "933", "934", "935"],  # Chiclayo
                    "4": ["900", "901", "902", "903", "904", "905", "910", "911", "912", "913", "914", "915", "920", "921", "922", "923", "924", "925", "930", "931", "932", "933", "934", "935"],  # Trujillo
                },
                "format": "{country_code}{area_code}{prefix}{suffix}",
                "randomization": {
                    "preserve_area_code": True,
                    "custom_prefix_length": 3,
                    "random_suffix_length": 6,
                    "avoid_repeated_digits": True
                }
            }
        }
    
    def generate_local_cli(
        self, 
        destination_number: str, 
        custom_pattern: Optional[Dict[str, Any]] = None,
        country_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gera CLI local baseado no número de destino.
        
        Args:
            destination_number: Número de destino para detectar país/área
            custom_pattern: Padrão customizado de aleatorização
            country_override: Forçar país específico
            
        Returns:
            Dict com CLI gerado e metadados
        """
        try:
            # Detectar país do número de destino
            if country_override:
                country = country_override.lower()
            else:
                country = self._detect_country_from_number(destination_number)
            
            if country not in self.country_patterns:
                logger.warning(f"⚠️ País {country} não suportado para CLI local")
                return self._generate_fallback_cli(destination_number, country)
            
            country_config = self.country_patterns[country]
            
            # Extrair área do número de destino
            area_info = self._extract_area_info(destination_number, country_config)
            
            # Gerar CLI local baseado na estratégia do país
            if custom_pattern:
                cli = self._generate_custom_pattern_cli(area_info, custom_pattern, country_config)
            else:
                cli = self._generate_country_strategy_cli(area_info, country_config)
            
            # Validar CLI gerado
            if not self._validate_generated_cli(cli):
                logger.warning(f"⚠️ CLI gerado inválido: {cli}")
                return self._generate_fallback_cli(destination_number, country)
            
            # Rastrear uso
            self._track_cli_generation(cli, country, area_info)
            
            result = {
                "cli": cli,
                "country": country,
                "country_name": country_config["name"],
                "country_code": country_config["country_code"],
                "strategy": country_config["strategy"],
                "destination_number": destination_number,
                "area_detected": area_info.get("area_code", "unknown"),
                "pattern_used": custom_pattern.get("name", "default") if custom_pattern else "default",
                "generation_timestamp": datetime.now().isoformat(),
                "is_local": True
            }
            
            logger.info(f"🎯 CLI local gerado: {cli} para {destination_number} ({country})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar CLI local: {str(e)}")
            return self._generate_fallback_cli(destination_number, country_override or "unknown")
    
    def _detect_country_from_number(self, number: str) -> str:
        """Detecta país baseado no número de telefone."""
        # Limpar número
        clean_number = re.sub(r'[^\d+]', '', number)
        
        if clean_number.startswith('+'):
            clean_number = clean_number[1:]
        
        # Verificar códigos de país
        if clean_number.startswith('1'):
            # Verificar se é USA ou Canada baseado no área code
            if len(clean_number) >= 4:
                area_code = clean_number[1:4]
                # Área codes canadenses específicos
                canada_codes = ['204', '236', '249', '250', '289', '306', '343', '365', '403', '416', '418', '431', '437', '438', '450', '506', '514', '519', '548', '579', '581', '587', '604', '613', '639', '647', '672', '705', '709', '778', '780', '782', '807', '819', '825', '867', '873', '902', '905']
                if area_code in canada_codes:
                    return "canada"
            return "usa"
        elif clean_number.startswith('52'):
            return "mexico"
        elif clean_number.startswith('55'):
            return "brasil"
        elif clean_number.startswith('57'):
            return "colombia"
        elif clean_number.startswith('54'):
            return "argentina"
        elif clean_number.startswith('56'):
            return "chile"
        elif clean_number.startswith('51'):
            return "peru"
        
        # Default para Brasil se não detectar
        return "brasil"
    
    def _extract_area_info(self, number: str, country_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai informações de área do número."""
        clean_number = re.sub(r'[^\d]', '', number)
        
        # Remover código do país
        country_code = country_config["country_code"].replace('+', '')
        if clean_number.startswith(country_code):
            clean_number = clean_number[len(country_code):]
        
        area_codes = country_config.get("area_codes", {})
        
        # Tentar encontrar área code
        for area_code in sorted(area_codes.keys(), key=len, reverse=True):
            if clean_number.startswith(area_code):
                return {
                    "area_code": area_code,
                    "area_prefixes": area_codes[area_code],
                    "remaining_number": clean_number[len(area_code):]
                }
        
        # Se não encontrar, usar primeiro disponível
        if area_codes:
            first_area = list(area_codes.keys())[0]
            return {
                "area_code": first_area,
                "area_prefixes": area_codes[first_area],
                "remaining_number": clean_number
            }
        
        return {
            "area_code": "unknown",
            "area_prefixes": [],
            "remaining_number": clean_number
        }
    
    def _generate_country_strategy_cli(self, area_info: Dict[str, Any], country_config: Dict[str, Any]) -> str:
        """Gera CLI baseado na estratégia específica do país."""
        strategy = country_config["strategy"]
        randomization = country_config["randomization"]
        
        if strategy == "area_code_preservation":
            return self._generate_area_code_preservation_cli(area_info, country_config)
        elif strategy == "local_area_randomization":
            return self._generate_local_area_randomization_cli(area_info, country_config)
        elif strategy == "ddd_preservation":
            return self._generate_ddd_preservation_cli(area_info, country_config)
        else:
            return self._generate_default_cli(area_info, country_config)
    
    def _generate_area_code_preservation_cli(self, area_info: Dict[str, Any], country_config: Dict[str, Any]) -> str:
        """
        Estratégia USA/Canada/Colombia/Argentina/Chile/Peru:
        Mantém área code + prefixo personalizado + aleatorização
        """
        country_code = country_config["country_code"]
        area_code = area_info["area_code"]
        prefixes = area_info.get("area_prefixes", [])
        randomization = country_config["randomization"]
        
        # Selecionar prefixo
        if prefixes:
            prefix = random.choice(prefixes)
        else:
            # Gerar prefixo aleatório
            prefix_length = randomization.get("custom_prefix_length", 3)
            prefix = self._generate_random_digits(prefix_length, avoid_repeated=randomization.get("avoid_repeated_digits", True))
        
        # Gerar sufixo aleatório
        suffix_length = randomization.get("random_suffix_length", 4)
        suffix = self._generate_random_digits(suffix_length, avoid_repeated=randomization.get("avoid_repeated_digits", True))
        
        # Construir CLI
        if country_config.get("format"):
            cli = country_config["format"].format(
                country_code=country_code,
                area_code=area_code,
                prefix=prefix,
                suffix=suffix
            )
        else:
            cli = f"{country_code}{area_code}{prefix}{suffix}"
        
        return cli
    
    def _generate_local_area_randomization_cli(self, area_info: Dict[str, Any], country_config: Dict[str, Any]) -> str:
        """
        Estratégia México:
        Mantém área code + aleatorização completa dos últimos dígitos
        """
        country_code = country_config["country_code"]
        area_code = area_info["area_code"]
        randomization = country_config["randomization"]
        
        # Gerar número aleatório completo
        random_length = randomization.get("random_number_length", 7)
        random_number = self._generate_random_digits(random_length, avoid_repeated=randomization.get("avoid_repeated_digits", True))
        
        # Construir CLI
        cli = f"{country_code}{area_code}{random_number}"
        
        return cli
    
    def _generate_ddd_preservation_cli(self, area_info: Dict[str, Any], country_config: Dict[str, Any]) -> str:
        """
        Estratégia Brasil:
        Mantém DDD + indicador de celular (9) + prefixo + aleatorização
        """
        country_code = country_config["country_code"]
        area_code = area_info["area_code"]
        prefixes = area_info.get("area_prefixes", [])
        randomization = country_config["randomization"]
        
        # Indicador de celular
        mobile_indicator = randomization.get("mobile_indicator", "9")
        
        # Selecionar prefixo
        if prefixes:
            prefix = random.choice(prefixes)
        else:
            # Gerar prefixo aleatório
            prefix_length = randomization.get("custom_prefix_length", 4)
            prefix = self._generate_random_digits(prefix_length, avoid_repeated=randomization.get("avoid_repeated_digits", True))
        
        # Gerar sufixo aleatório
        suffix_length = randomization.get("random_suffix_length", 4)
        suffix = self._generate_random_digits(suffix_length, avoid_repeated=randomization.get("avoid_repeated_digits", True))
        
        # Construir CLI
        cli = f"{country_code}{area_code}{mobile_indicator}{prefix}{suffix}"
        
        return cli
    
    def _generate_custom_pattern_cli(self, area_info: Dict[str, Any], custom_pattern: Dict[str, Any], country_config: Dict[str, Any]) -> str:
        """Gera CLI baseado em padrão customizado."""
        try:
            pattern_type = custom_pattern.get("type", "standard")
            
            if pattern_type == "prefix_mask":
                return self._generate_prefix_mask_cli(area_info, custom_pattern, country_config)
            elif pattern_type == "suffix_randomization":
                return self._generate_suffix_randomization_cli(area_info, custom_pattern, country_config)
            elif pattern_type == "full_custom":
                return self._generate_full_custom_cli(area_info, custom_pattern, country_config)
            else:
                # Fallback para estratégia padrão do país
                return self._generate_country_strategy_cli(area_info, country_config)
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar CLI customizado: {str(e)}")
            return self._generate_country_strategy_cli(area_info, country_config)
    
    def _generate_prefix_mask_cli(self, area_info: Dict[str, Any], custom_pattern: Dict[str, Any], country_config: Dict[str, Any]) -> str:
        """
        Gera CLI com máscara de prefixo:
        Ex: 305 2xx-xxxx (últimos 6 aleatórios)
        """
        country_code = country_config["country_code"]
        area_code = area_info["area_code"]
        
        # Obter padrão da máscara
        mask = custom_pattern.get("mask", "xxxxx")
        fixed_prefix = custom_pattern.get("fixed_prefix", "")
        
        # Substituir 'x' por dígitos aleatórios
        result_number = ""
        for char in mask:
            if char.lower() == 'x':
                result_number += str(random.randint(0, 9))
            else:
                result_number += char
        
        # Construir CLI
        cli = f"{country_code}{area_code}{fixed_prefix}{result_number}"
        
        return cli
    
    def _generate_suffix_randomization_cli(self, area_info: Dict[str, Any], custom_pattern: Dict[str, Any], country_config: Dict[str, Any]) -> str:
        """
        Gera CLI com aleatorização do sufixo:
        Ex: 305 35x-xxxx (últimos 5 aleatórios)
        """
        country_code = country_config["country_code"]
        area_code = area_info["area_code"]
        
        # Obter configurações
        fixed_part = custom_pattern.get("fixed_part", "")
        random_digits = custom_pattern.get("random_digits", 5)
        
        # Gerar dígitos aleatórios
        suffix = self._generate_random_digits(random_digits, avoid_repeated=custom_pattern.get("avoid_repeated", True))
        
        # Construir CLI
        cli = f"{country_code}{area_code}{fixed_part}{suffix}"
        
        return cli
    
    def _generate_full_custom_cli(self, area_info: Dict[str, Any], custom_pattern: Dict[str, Any], country_config: Dict[str, Any]) -> str:
        """Gera CLI completamente customizado baseado em template."""
        template = custom_pattern.get("template", "{country_code}{area_code}{random_7}")
        
        # Variáveis disponíveis para substituição
        variables = {
            "country_code": country_config["country_code"],
            "area_code": area_info["area_code"],
            "random_3": self._generate_random_digits(3),
            "random_4": self._generate_random_digits(4),
            "random_5": self._generate_random_digits(5),
            "random_6": self._generate_random_digits(6),
            "random_7": self._generate_random_digits(7),
            "random_8": self._generate_random_digits(8),
        }
        
        # Adicionar prefixos se disponíveis
        prefixes = area_info.get("area_prefixes", [])
        if prefixes:
            variables["area_prefix"] = random.choice(prefixes)
        else:
            variables["area_prefix"] = self._generate_random_digits(3)
        
        # Substituir variáveis no template
        cli = template.format(**variables)
        
        return cli
    
    def _generate_random_digits(self, length: int, avoid_repeated: bool = True) -> str:
        """Gera string de dígitos aleatórios."""
        if length <= 0:
            return ""
        
        digits = []
        last_digit = None
        
        for _ in range(length):
            if avoid_repeated and last_digit is not None:
                # Evitar dígito repetido consecutivo
                available_digits = [d for d in range(10) if d != last_digit]
                digit = random.choice(available_digits)
            else:
                digit = random.randint(0, 9)
            
            digits.append(str(digit))
            last_digit = digit
        
        return ''.join(digits)
    
    def _generate_default_cli(self, area_info: Dict[str, Any], country_config: Dict[str, Any]) -> str:
        """Gera CLI padrão quando estratégia específica não está disponível."""
        country_code = country_config["country_code"]
        area_code = area_info["area_code"]
        
        # Gerar 7 dígitos aleatórios
        random_part = self._generate_random_digits(7, avoid_repeated=True)
        
        cli = f"{country_code}{area_code}{random_part}"
        
        return cli
    
    def _generate_fallback_cli(self, destination_number: str, country: str) -> Dict[str, Any]:
        """Gera CLI de fallback quando não consegue gerar local."""
        fallback_clis = {
            "usa": "+18885551000",
            "canada": "+18885551001",
            "mexico": "+528885551000",
            "brasil": "+558885551000",
            "colombia": "+578885551000",
            "argentina": "+548885551000",
            "chile": "+568885551000",
            "peru": "+518885551000"
        }
        
        cli = fallback_clis.get(country, "+18885559999")
        
        return {
            "cli": cli,
            "country": country,
            "country_name": f"País {country}",
            "country_code": "+1",
            "strategy": "fallback",
            "destination_number": destination_number,
            "area_detected": "unknown",
            "pattern_used": "fallback",
            "generation_timestamp": datetime.now().isoformat(),
            "is_local": False,
            "warning": "CLI de fallback usado - país não suportado ou erro na geração"
        }
    
    def _validate_generated_cli(self, cli: str) -> bool:
        """Valida se o CLI gerado é válido."""
        if not cli:
            return False
        
        # Deve começar com +
        if not cli.startswith('+'):
            return False
        
        # Remover + e verificar se são apenas dígitos
        numbers_only = cli[1:]
        if not numbers_only.isdigit():
            return False
        
        # Verificar comprimento (mínimo 10, máximo 15)
        if len(numbers_only) < 10 or len(numbers_only) > 15:
            return False
        
        return True
    
    def _track_cli_generation(self, cli: str, country: str, area_info: Dict[str, Any]):
        """Rastreia geração de CLI para estatísticas."""
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"{country}:{area_info.get('area_code', 'unknown')}:{today}"
        
        if key not in self.usage_tracking:
            self.usage_tracking[key] = {
                "count": 0,
                "generated_clis": [],
                "area_code": area_info.get('area_code', 'unknown')
            }
        
        self.usage_tracking[key]["count"] += 1
        self.usage_tracking[key]["generated_clis"].append({
            "cli": cli,
            "timestamp": datetime.now().isoformat()
        })
        
        # Manter apenas os últimos 100 CLIs por área
        if len(self.usage_tracking[key]["generated_clis"]) > 100:
            self.usage_tracking[key]["generated_clis"] = self.usage_tracking[key]["generated_clis"][-100:]
    
    def get_country_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Retorna padrões disponíveis por país."""
        return {
            country: {
                "name": config["name"],
                "country_code": config["country_code"],
                "strategy": config["strategy"],
                "area_codes": list(config["area_codes"].keys()),
                "randomization": config["randomization"]
            }
            for country, config in self.country_patterns.items()
        }
    
    def get_generation_stats(self, country: Optional[str] = None) -> Dict[str, Any]:
        """Obtém estatísticas de geração de CLIs."""
        if country:
            # Estatísticas específicas do país
            country_stats = {}
            today = datetime.now().strftime("%Y-%m-%d")
            
            for key, data in self.usage_tracking.items():
                if key.startswith(f"{country}:"):
                    parts = key.split(":")
                    area_code = parts[1]
                    date = parts[2]
                    
                    if date == today:
                        country_stats[area_code] = data
            
            return {
                "country": country,
                "date": today,
                "areas": country_stats,
                "total_generated": sum(data["count"] for data in country_stats.values())
            }
        else:
            # Estatísticas gerais
            today = datetime.now().strftime("%Y-%m-%d")
            today_stats = {}
            
            for key, data in self.usage_tracking.items():
                if key.endswith(f":{today}"):
                    parts = key.split(":")
                    country_key = parts[0]
                    
                    if country_key not in today_stats:
                        today_stats[country_key] = {"count": 0, "areas": {}}
                    
                    today_stats[country_key]["count"] += data["count"]
                    today_stats[country_key]["areas"][parts[1]] = data["count"]
            
            return {
                "date": today,
                "countries": today_stats,
                "total_generated": sum(data["count"] for data in today_stats.values())
            }
    
    def create_custom_pattern(
        self, 
        name: str, 
        pattern_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cria padrão customizado de aleatorização."""
        try:
            # Validar configuração do padrão
            required_fields = ["type", "countries"]
            for field in required_fields:
                if field not in pattern_config:
                    return {
                        "success": False,
                        "error": f"Campo obrigatório '{field}' não fornecido"
                    }
            
            # Salvar padrão customizado (em produção, salvaria no banco)
            custom_pattern = {
                "name": name,
                "created_at": datetime.now().isoformat(),
                "config": pattern_config,
                "active": True
            }
            
            logger.info(f"📋 Padrão customizado criado: {name}")
            
            return {
                "success": True,
                "pattern": custom_pattern,
                "message": f"Padrão '{name}' criado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar padrão customizado: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def bulk_generate_clis(
        self, 
        destination_numbers: List[str],
        pattern_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gera CLIs em lote para uma lista de números."""
        try:
            results = []
            successful = 0
            failed = 0
            
            for number in destination_numbers:
                try:
                    # Gerar CLI para o número
                    cli_result = self.generate_local_cli(number)
                    
                    if cli_result.get("is_local", False):
                        successful += 1
                    else:
                        failed += 1
                    
                    results.append({
                        "destination_number": number,
                        "generated_cli": cli_result["cli"],
                        "country": cli_result.get("country", "unknown"),
                        "area_detected": cli_result.get("area_detected", "unknown"),
                        "success": cli_result.get("is_local", False)
                    })
                    
                except Exception as e:
                    failed += 1
                    results.append({
                        "destination_number": number,
                        "generated_cli": None,
                        "error": str(e),
                        "success": False
                    })
            
            return {
                "total_processed": len(destination_numbers),
                "successful": successful,
                "failed": failed,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na geração em lote: {str(e)}")
            return {
                "total_processed": 0,
                "successful": 0,
                "failed": len(destination_numbers),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 