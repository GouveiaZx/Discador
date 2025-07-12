"""
Serviço Avançado de Geração de Padrões CLI Customizados
Sistema completo para gerar CLIs locais com padrões personalizados por país.

Funcionalidades:
- Padrões customizados por país/área (ex: 305 2xx-xxxx, 305 35x-xxxx)
- Suporte completo para todos os países
- Configurações flexíveis de aleatorização
- Validação e controle de qualidade
- Integração com Performance Avançado
"""

import random
import re
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.utils.logger import logger

class CliPatternGeneratorService:
    """
    Serviço para gerar CLIs com padrões customizados por país.
    Permite configurações específicas como "305 2xx-xxxx" ou "55 xxxx-xxxx".
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.pattern_configs = self._load_pattern_configs()
        self.generation_cache = {}
        
    def _load_pattern_configs(self) -> Dict[str, Dict[str, Any]]:
        """Carrega configurações de padrões por país."""
        return {
            "usa": {
                "country_name": "Estados Unidos",
                "country_code": "+1",
                "pattern_type": "area_code_prefix",
                "area_codes": {
                    # Florida
                    "305": {
                        "name": "Miami",
                        "state": "FL",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 30},
                            {"mask": "22x-xxxx", "description": "Padrão 22x", "weight": 25},
                            {"mask": "25x-xxxx", "description": "Padrão 25x", "weight": 20},
                            {"mask": "29x-xxxx", "description": "Padrão 29x", "weight": 15},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 10}
                        ]
                    },
                    "321": {
                        "name": "Orlando",
                        "state": "FL",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 35},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 30},
                            {"mask": "5xx-xxxx", "description": "Padrão 5xx", "weight": 20},
                            {"mask": "6xx-xxxx", "description": "Padrão 6xx", "weight": 15}
                        ]
                    },
                    "407": {
                        "name": "Orlando Central",
                        "state": "FL",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 40},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 35},
                            {"mask": "8xx-xxxx", "description": "Padrão 8xx", "weight": 25}
                        ]
                    },
                    "786": {
                        "name": "Miami Beach",
                        "state": "FL",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 30},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 25},
                            {"mask": "5xx-xxxx", "description": "Padrão 5xx", "weight": 20},
                            {"mask": "7xx-xxxx", "description": "Padrão 7xx", "weight": 15},
                            {"mask": "9xx-xxxx", "description": "Padrão 9xx", "weight": 10}
                        ]
                    },
                    # Texas
                    "214": {
                        "name": "Dallas",
                        "state": "TX",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 30},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 25},
                            {"mask": "4xx-xxxx", "description": "Padrão 4xx", "weight": 20},
                            {"mask": "8xx-xxxx", "description": "Padrão 8xx", "weight": 15},
                            {"mask": "9xx-xxxx", "description": "Padrão 9xx", "weight": 10}
                        ]
                    },
                    "713": {
                        "name": "Houston",
                        "state": "TX",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 35},
                            {"mask": "5xx-xxxx", "description": "Padrão 5xx", "weight": 30},
                            {"mask": "7xx-xxxx", "description": "Padrão 7xx", "weight": 20},
                            {"mask": "9xx-xxxx", "description": "Padrão 9xx", "weight": 15}
                        ]
                    },
                    # California
                    "213": {
                        "name": "Los Angeles",
                        "state": "CA",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 30},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 25},
                            {"mask": "6xx-xxxx", "description": "Padrão 6xx", "weight": 20},
                            {"mask": "8xx-xxxx", "description": "Padrão 8xx", "weight": 15},
                            {"mask": "9xx-xxxx", "description": "Padrão 9xx", "weight": 10}
                        ]
                    },
                    "310": {
                        "name": "Beverly Hills",
                        "state": "CA",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 35},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 30},
                            {"mask": "5xx-xxxx", "description": "Padrão 5xx", "weight": 20},
                            {"mask": "8xx-xxxx", "description": "Padrão 8xx", "weight": 15}
                        ]
                    },
                    # New York
                    "212": {
                        "name": "Manhattan",
                        "state": "NY",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 30},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 25},
                            {"mask": "4xx-xxxx", "description": "Padrão 4xx", "weight": 20},
                            {"mask": "7xx-xxxx", "description": "Padrão 7xx", "weight": 15},
                            {"mask": "9xx-xxxx", "description": "Padrão 9xx", "weight": 10}
                        ]
                    },
                    "646": {
                        "name": "Manhattan Cell",
                        "state": "NY",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 35},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 30},
                            {"mask": "5xx-xxxx", "description": "Padrão 5xx", "weight": 20},
                            {"mask": "8xx-xxxx", "description": "Padrão 8xx", "weight": 15}
                        ]
                    }
                }
            },
            "canada": {
                "country_name": "Canadá",
                "country_code": "+1",
                "pattern_type": "area_code_prefix",
                "area_codes": {
                    "416": {
                        "name": "Toronto",
                        "province": "ON",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 30},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 25},
                            {"mask": "5xx-xxxx", "description": "Padrão 5xx", "weight": 20},
                            {"mask": "8xx-xxxx", "description": "Padrão 8xx", "weight": 15},
                            {"mask": "9xx-xxxx", "description": "Padrão 9xx", "weight": 10}
                        ]
                    },
                    "514": {
                        "name": "Montreal",
                        "province": "QC",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 35},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 30},
                            {"mask": "8xx-xxxx", "description": "Padrão 8xx", "weight": 20},
                            {"mask": "9xx-xxxx", "description": "Padrão 9xx", "weight": 15}
                        ]
                    },
                    "604": {
                        "name": "Vancouver",
                        "province": "BC",
                        "patterns": [
                            {"mask": "2xx-xxxx", "description": "Padrão 2xx", "weight": 30},
                            {"mask": "3xx-xxxx", "description": "Padrão 3xx", "weight": 25},
                            {"mask": "7xx-xxxx", "description": "Padrão 7xx", "weight": 20},
                            {"mask": "9xx-xxxx", "description": "Padrão 9xx", "weight": 15},
                            {"mask": "4xx-xxxx", "description": "Padrão 4xx", "weight": 10}
                        ]
                    }
                }
            },
            "mexico": {
                "country_name": "México",
                "country_code": "+52",
                "pattern_type": "area_code_full",
                "area_codes": {
                    "55": {
                        "name": "Ciudad de México (CDMX)",
                        "state": "CDMX",
                        "patterns": [
                            {"mask": "xxxx-xxxx", "description": "8 dígitos completos", "weight": 100}
                        ]
                    },
                    "81": {
                        "name": "Monterrey",
                        "state": "NL",
                        "patterns": [
                            {"mask": "xxxx-xxxx", "description": "8 dígitos completos", "weight": 100}
                        ]
                    },
                    "33": {
                        "name": "Guadalajara",
                        "state": "JA",
                        "patterns": [
                            {"mask": "xxxx-xxxx", "description": "8 dígitos completos", "weight": 100}
                        ]
                    },
                    "222": {
                        "name": "Puebla",
                        "state": "PU",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    },
                    "998": {
                        "name": "Cancún",
                        "state": "QR",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    }
                }
            },
            "brasil": {
                "country_name": "Brasil",
                "country_code": "+55",
                "pattern_type": "ddd_celular",
                "area_codes": {
                    "11": {
                        "name": "São Paulo",
                        "state": "SP",
                        "patterns": [
                            {"mask": "9xxxx-xxxx", "description": "Celular 9 dígitos", "weight": 80},
                            {"mask": "8xxxx-xxxx", "description": "Celular 8 dígitos", "weight": 20}
                        ]
                    },
                    "21": {
                        "name": "Rio de Janeiro",
                        "state": "RJ",
                        "patterns": [
                            {"mask": "9xxxx-xxxx", "description": "Celular 9 dígitos", "weight": 80},
                            {"mask": "8xxxx-xxxx", "description": "Celular 8 dígitos", "weight": 20}
                        ]
                    },
                    "31": {
                        "name": "Belo Horizonte",
                        "state": "MG",
                        "patterns": [
                            {"mask": "9xxxx-xxxx", "description": "Celular 9 dígitos", "weight": 80},
                            {"mask": "8xxxx-xxxx", "description": "Celular 8 dígitos", "weight": 20}
                        ]
                    },
                    "47": {
                        "name": "Joinville",
                        "state": "SC",
                        "patterns": [
                            {"mask": "9xxxx-xxxx", "description": "Celular 9 dígitos", "weight": 80},
                            {"mask": "8xxxx-xxxx", "description": "Celular 8 dígitos", "weight": 20}
                        ]
                    },
                    "85": {
                        "name": "Fortaleza",
                        "state": "CE",
                        "patterns": [
                            {"mask": "9xxxx-xxxx", "description": "Celular 9 dígitos", "weight": 80},
                            {"mask": "8xxxx-xxxx", "description": "Celular 8 dígitos", "weight": 20}
                        ]
                    }
                }
            },
            "colombia": {
                "country_name": "Colombia",
                "country_code": "+57",
                "pattern_type": "area_code_full",
                "area_codes": {
                    "1": {
                        "name": "Bogotá",
                        "department": "DC",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    },
                    "4": {
                        "name": "Medellín",
                        "department": "AN",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    },
                    "5": {
                        "name": "Barranquilla",
                        "department": "AT",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    },
                    "2": {
                        "name": "Cali",
                        "department": "VC",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    }
                }
            },
            "argentina": {
                "country_name": "Argentina",
                "country_code": "+54",
                "pattern_type": "area_code_celular",
                "area_codes": {
                    "11": {
                        "name": "Buenos Aires",
                        "province": "BA",
                        "patterns": [
                            {"mask": "xxxx-xxxx", "description": "8 dígitos completos", "weight": 100}
                        ]
                    },
                    "341": {
                        "name": "Rosario",
                        "province": "SF",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    },
                    "351": {
                        "name": "Córdoba",
                        "province": "CB",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    },
                    "261": {
                        "name": "Mendoza",
                        "province": "MZ",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    }
                }
            },
            "chile": {
                "country_name": "Chile",
                "country_code": "+56",
                "pattern_type": "area_code_full",
                "area_codes": {
                    "2": {
                        "name": "Santiago",
                        "region": "RM",
                        "patterns": [
                            {"mask": "xxxx-xxxx", "description": "8 dígitos completos", "weight": 100}
                        ]
                    },
                    "32": {
                        "name": "Valparaíso",
                        "region": "VS",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    },
                    "41": {
                        "name": "Concepción",
                        "region": "BB",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    }
                }
            },
            "peru": {
                "country_name": "Perú",
                "country_code": "+51",
                "pattern_type": "area_code_full",
                "area_codes": {
                    "1": {
                        "name": "Lima",
                        "department": "LM",
                        "patterns": [
                            {"mask": "xxxx-xxxx", "description": "8 dígitos completos", "weight": 100}
                        ]
                    },
                    "44": {
                        "name": "Trujillo",
                        "department": "LL",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    },
                    "54": {
                        "name": "Arequipa",
                        "department": "AR",
                        "patterns": [
                            {"mask": "xxx-xxxx", "description": "7 dígitos completos", "weight": 100}
                        ]
                    }
                }
            }
        }
    
    def generate_cli_with_pattern(
        self,
        destination_number: str,
        custom_pattern: Optional[str] = None,
        custom_area_code: Optional[str] = None,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Gera CLIs com padrões customizados.
        
        Args:
            destination_number: Número de destino
            custom_pattern: Padrão customizado (ex: "2xx-xxxx", "35x-xxxx")
            custom_area_code: Área code específico para forçar
            quantity: Quantidade de CLIs a gerar
            
        Returns:
            Dict com CLIs gerados e metadados
        """
        try:
            # Detectar país
            country = self._detect_country(destination_number)
            
            if country not in self.pattern_configs:
                return self._generate_fallback_response(destination_number, country)
            
            country_config = self.pattern_configs[country]
            
            # Extrair informações do número
            area_info = self._extract_area_info(destination_number, country_config)
            
            # Determinar área code a usar
            target_area_code = custom_area_code or area_info.get("area_code")
            
            if not target_area_code:
                return self._generate_fallback_response(destination_number, country)
            
            # Gerar CLIs
            generated_clis = []
            
            for i in range(quantity):
                if custom_pattern:
                    cli = self._generate_cli_with_custom_pattern(
                        country_config, target_area_code, custom_pattern
                    )
                else:
                    cli = self._generate_cli_with_default_pattern(
                        country_config, target_area_code
                    )
                
                if cli:
                    generated_clis.append(cli)
            
            # Remover duplicatas
            unique_clis = list(set(generated_clis))
            
            return {
                "success": True,
                "country": country,
                "country_name": country_config["country_name"],
                "country_code": country_config["country_code"],
                "destination_number": destination_number,
                "area_code": target_area_code,
                "area_name": area_info.get("area_name", "Desconhecida"),
                "pattern_used": custom_pattern or "default",
                "generated_clis": unique_clis,
                "quantity_requested": quantity,
                "quantity_generated": len(unique_clis),
                "generation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar CLI com padrão: {str(e)}")
            return self._generate_fallback_response(destination_number, country)
    
    def _generate_cli_with_custom_pattern(
        self,
        country_config: Dict[str, Any],
        area_code: str,
        pattern: str
    ) -> str:
        """
        Gera CLI com padrão customizado.
        
        Args:
            country_config: Configuração do país
            area_code: Código de área
            pattern: Padrão customizado (ex: "2xx-xxxx", "35x-xxxx")
            
        Returns:
            CLI gerado
        """
        try:
            country_code = country_config["country_code"]
            
            # Processar padrão
            processed_pattern = self._process_pattern(pattern)
            
            # Construir CLI
            cli = f"{country_code}{area_code}{processed_pattern}"
            
            return cli
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar CLI com padrão customizado: {str(e)}")
            return None
    
    def _generate_cli_with_default_pattern(
        self,
        country_config: Dict[str, Any],
        area_code: str
    ) -> str:
        """
        Gera CLI com padrão padrão da área.
        
        Args:
            country_config: Configuração do país
            area_code: Código de área
            
        Returns:
            CLI gerado
        """
        try:
            country_code = country_config["country_code"]
            area_config = country_config["area_codes"].get(area_code)
            
            if not area_config:
                # Usar padrão genérico
                return f"{country_code}{area_code}{''.join([str(random.randint(0, 9)) for _ in range(7)])}"
            
            # Selecionar padrão baseado no peso
            patterns = area_config["patterns"]
            weights = [p["weight"] for p in patterns]
            selected_pattern = random.choices(patterns, weights=weights)[0]
            
            # Processar padrão
            processed_pattern = self._process_pattern(selected_pattern["mask"])
            
            # Construir CLI
            cli = f"{country_code}{area_code}{processed_pattern}"
            
            return cli
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar CLI com padrão padrão: {str(e)}")
            return None
    
    def _process_pattern(self, pattern: str) -> str:
        """
        Processa padrão de máscara convertendo 'x' em dígitos aleatórios.
        
        Args:
            pattern: Padrão (ex: "2xx-xxxx", "35x-xxxx", "xxxx-xxxx")
            
        Returns:
            Padrão processado com números
        """
        result = ""
        
        for char in pattern:
            if char == 'x':
                result += str(random.randint(0, 9))
            elif char == 'X':
                result += str(random.randint(0, 9))
            else:
                result += char
        
        return result
    
    def _detect_country(self, number: str) -> str:
        """Detecta país baseado no número."""
        clean_number = re.sub(r'[^\d+]', '', number)
        
        if clean_number.startswith('+'):
            clean_number = clean_number[1:]
        
        # Códigos de país
        if clean_number.startswith('1'):
            # Verificar se é USA ou Canada
            if len(clean_number) >= 4:
                area_code = clean_number[1:4]
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
        
        return "usa"  # Default
    
    def _extract_area_info(self, number: str, country_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai informações da área do número."""
        clean_number = re.sub(r'[^\d+]', '', number)
        
        if clean_number.startswith('+'):
            clean_number = clean_number[1:]
        
        # Remover código do país
        country_code = country_config["country_code"].replace('+', '')
        if clean_number.startswith(country_code):
            clean_number = clean_number[len(country_code):]
        
        # Extrair área code baseado no tipo
        pattern_type = country_config["pattern_type"]
        
        if pattern_type == "area_code_prefix":
            # USA/Canada: 3 dígitos
            area_code = clean_number[:3]
        elif pattern_type == "area_code_full":
            # México/Colombia: 1-3 dígitos
            if len(clean_number) >= 10:
                area_code = clean_number[:2]
            else:
                area_code = clean_number[:1]
        elif pattern_type == "ddd_celular":
            # Brasil: 2 dígitos
            area_code = clean_number[:2]
        elif pattern_type == "area_code_celular":
            # Argentina: 2-3 dígitos
            if clean_number.startswith('11'):
                area_code = clean_number[:2]
            else:
                area_code = clean_number[:3]
        else:
            area_code = clean_number[:3]
        
        # Buscar informações da área
        area_info = country_config["area_codes"].get(area_code, {})
        
        return {
            "area_code": area_code,
            "area_name": area_info.get("name", "Desconhecida"),
            "patterns": area_info.get("patterns", []),
            "area_info": area_info
        }
    
    def _generate_fallback_response(self, destination_number: str, country: str) -> Dict[str, Any]:
        """Gera resposta de fallback."""
        fallback_clis = {
            "usa": ["+18885551000", "+18885551001"],
            "canada": ["+18885551002", "+18885551003"],
            "mexico": ["+528885551000", "+528885551001"],
            "brasil": ["+558885551000", "+558885551001"],
            "colombia": ["+578885551000", "+578885551001"],
            "argentina": ["+548885551000", "+548885551001"],
            "chile": ["+568885551000", "+568885551001"],
            "peru": ["+518885551000", "+518885551001"]
        }
        
        return {
            "success": False,
            "country": country,
            "destination_number": destination_number,
            "error": "País não suportado ou erro na geração",
            "fallback_clis": fallback_clis.get(country, ["+18885559999"]),
            "generation_timestamp": datetime.now().isoformat()
        }
    
    def get_available_patterns_for_country(self, country: str) -> Dict[str, Any]:
        """Obtém padrões disponíveis para um país."""
        if country not in self.pattern_configs:
            return {"error": "País não suportado"}
        
        country_config = self.pattern_configs[country]
        
        return {
            "country": country,
            "country_name": country_config["country_name"],
            "country_code": country_config["country_code"],
            "pattern_type": country_config["pattern_type"],
            "area_codes": country_config["area_codes"]
        }
    
    def get_all_supported_countries(self) -> List[Dict[str, Any]]:
        """Obtém lista de todos os países suportados."""
        countries = []
        
        for country_key, config in self.pattern_configs.items():
            countries.append({
                "country_code": country_key,
                "country_name": config["country_name"],
                "country_calling_code": config["country_code"],
                "pattern_type": config["pattern_type"],
                "area_codes_count": len(config["area_codes"])
            })
        
        return countries 