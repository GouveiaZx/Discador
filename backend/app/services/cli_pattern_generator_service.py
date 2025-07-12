"""
Servicio Avanzado de Generación de Patrones CLI Personalizados
Sistema completo para generar CLIs locales con patrones personalizados por país.

Funcionalidades:
- Patrones personalizados por país/área (ej: 305 2xx-xxxx, 305 35x-xxxx)
- Soporte completo para todos los países
- Configuraciones flexibles de aleatorización
- Validación y control de calidad
- Integración con Performance Avanzado
"""

import random
import re
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.utils.logger import logger

class CliPatternGeneratorService:
    """
    Servicio para generar CLIs con patrones personalizados por país.
    Permite configuraciones específicas como "305 2xx-xxxx" o "55 xxxx-xxxx".
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.pattern_configs = self._load_pattern_configs()
        self.generation_cache = {}
        
    def _load_pattern_configs(self) -> Dict[str, Any]:
        """Carga configuraciones de patrones por país."""
        return {
            'usa': {
                'country_code': '+1',
                'strategy': 'area_code_preservation',
                'area_codes': {
                    '305': {
                        'name': 'Miami, FL',
                        'patterns': [
                            {'mask': '2xx-xxxx', 'weight': 0.4, 'description': 'Prefijo 2 + 5 aleatorios'},
                            {'mask': '25x-xxxx', 'weight': 0.3, 'description': 'Prefijo 25 + 4 aleatorios'},
                            {'mask': '3xx-xxxx', 'weight': 0.3, 'description': 'Prefijo 3 + 5 aleatorios'}
                        ]
                    },
                    '425': {
                        'name': 'Seattle, WA',
                        'patterns': [
                            {'mask': '2xx-xxxx', 'weight': 0.5, 'description': 'Prefijo 2 + 5 aleatorios'},
                            {'mask': '4xx-xxxx', 'weight': 0.5, 'description': 'Prefijo 4 + 5 aleatorios'}
                        ]
                    },
                    '213': {
                        'name': 'Los Angeles, CA',
                        'patterns': [
                            {'mask': '2xx-xxxx', 'weight': 0.4, 'description': 'Prefijo 2 + 5 aleatorios'},
                            {'mask': '3xx-xxxx', 'weight': 0.6, 'description': 'Prefijo 3 + 5 aleatorios'}
                        ]
                    }
                }
            },
            'canada': {
                'country_code': '+1',
                'strategy': 'area_code_preservation',
                'area_codes': {
                    '416': {
                        'name': 'Toronto, ON',
                        'patterns': [
                            {'mask': '2xx-xxxx', 'weight': 0.5, 'description': 'Prefijo 2 + 5 aleatorios'},
                            {'mask': '4xx-xxxx', 'weight': 0.5, 'description': 'Prefijo 4 + 5 aleatorios'}
                        ]
                    },
                    '514': {
                        'name': 'Montreal, QC',
                        'patterns': [
                            {'mask': '2xx-xxxx', 'weight': 0.5, 'description': 'Prefijo 2 + 5 aleatorios'},
                            {'mask': '5xx-xxxx', 'weight': 0.5, 'description': 'Prefijo 5 + 5 aleatorios'}
                        ]
                    }
                }
            },
            'mexico': {
                'country_code': '+52',
                'strategy': 'local_area_randomization',
                'area_codes': {
                    '55': {
                        'name': 'Ciudad de México (CDMX)',
                        'patterns': [
                            {'mask': 'xxxx-xxxx', 'weight': 1.0, 'description': '8 dígitos aleatorios completos'}
                        ]
                    },
                    '81': {
                        'name': 'Monterrey, NL',
                        'patterns': [
                            {'mask': 'xxxx-xxxx', 'weight': 1.0, 'description': '8 dígitos aleatorios completos'}
                        ]
                    },
                    '33': {
                        'name': 'Guadalajara, JAL',
                        'patterns': [
                            {'mask': 'xxxx-xxxx', 'weight': 1.0, 'description': '8 dígitos aleatorios completos'}
                        ]
                    },
                    '222': {
                        'name': 'Puebla, PUE',
                        'patterns': [
                            {'mask': 'xxx-xxxx', 'weight': 1.0, 'description': '7 dígitos aleatorios'}
                        ]
                    }
                }
            },
            'brasil': {
                'country_code': '+55',
                'strategy': 'ddd_preservation',
                'area_codes': {
                    '11': {
                        'name': 'São Paulo, SP',
                        'patterns': [
                            {'mask': '9xxxx-xxxx', 'weight': 0.8, 'description': 'Celular 9 + 8 aleatorios'},
                            {'mask': '8xxxx-xxxx', 'weight': 0.2, 'description': 'Celular 8 + 8 aleatorios'}
                        ]
                    },
                    '21': {
                        'name': 'Rio de Janeiro, RJ',
                        'patterns': [
                            {'mask': '9xxxx-xxxx', 'weight': 0.8, 'description': 'Celular 9 + 8 aleatorios'},
                            {'mask': '8xxxx-xxxx', 'weight': 0.2, 'description': 'Celular 8 + 8 aleatorios'}
                        ]
                    },
                    '31': {
                        'name': 'Belo Horizonte, MG',
                        'patterns': [
                            {'mask': '9xxxx-xxxx', 'weight': 0.8, 'description': 'Celular 9 + 8 aleatorios'},
                            {'mask': '8xxxx-xxxx', 'weight': 0.2, 'description': 'Celular 8 + 8 aleatorios'}
                        ]
                    }
                }
            },
            'colombia': {
                'country_code': '+57',
                'strategy': 'area_code_full',
                'area_codes': {
                    '1': {
                        'name': 'Bogotá, DC',
                        'patterns': [
                            {'mask': 'xxx-xxxx', 'weight': 1.0, 'description': '7 dígitos aleatorios'}
                        ]
                    },
                    '4': {
                        'name': 'Medellín, ANT',
                        'patterns': [
                            {'mask': '3xx-xxxx', 'weight': 0.6, 'description': 'Celular 3 + 6 aleatorios'},
                            {'mask': 'xxx-xxxx', 'weight': 0.4, 'description': '7 dígitos aleatorios'}
                        ]
                    },
                    '5': {
                        'name': 'Barranquilla, ATL',
                        'patterns': [
                            {'mask': 'xxx-xxxx', 'weight': 1.0, 'description': '7 dígitos aleatorios'}
                        ]
                    }
                }
            },
            'argentina': {
                'country_code': '+54',
                'strategy': 'area_code_full',
                'area_codes': {
                    '11': {
                        'name': 'Buenos Aires, CABA',
                        'patterns': [
                            {'mask': 'xxxx-xxxx', 'weight': 0.6, 'description': '8 dígitos aleatorios'},
                            {'mask': '15xx-xxxx', 'weight': 0.4, 'description': 'Celular 15 + 6 aleatorios'}
                        ]
                    },
                    '341': {
                        'name': 'Rosario, SF',
                        'patterns': [
                            {'mask': 'xxx-xxxx', 'weight': 0.6, 'description': '7 dígitos aleatorios'},
                            {'mask': '15x-xxxx', 'weight': 0.4, 'description': 'Celular 15 + 5 aleatorios'}
                        ]
                    },
                    '351': {
                        'name': 'Córdoba, COR',
                        'patterns': [
                            {'mask': 'xxx-xxxx', 'weight': 0.6, 'description': '7 dígitos aleatorios'},
                            {'mask': '15x-xxxx', 'weight': 0.4, 'description': 'Celular 15 + 5 aleatorios'}
                        ]
                    }
                }
            },
            'chile': {
                'country_code': '+56',
                'strategy': 'area_code_full',
                'area_codes': {
                    '2': {
                        'name': 'Santiago, RM',
                        'patterns': [
                            {'mask': 'xxxx-xxxx', 'weight': 0.6, 'description': '8 dígitos aleatorios'},
                            {'mask': '9xxx-xxxx', 'weight': 0.4, 'description': 'Celular 9 + 7 aleatorios'}
                        ]
                    },
                    '32': {
                        'name': 'Valparaíso, VAL',
                        'patterns': [
                            {'mask': 'xxx-xxxx', 'weight': 0.6, 'description': '7 dígitos aleatorios'},
                            {'mask': '9xx-xxxx', 'weight': 0.4, 'description': 'Celular 9 + 6 aleatorios'}
                        ]
                    },
                    '41': {
                        'name': 'Concepción, BIO',
                        'patterns': [
                            {'mask': 'xxx-xxxx', 'weight': 0.6, 'description': '7 dígitos aleatorios'},
                            {'mask': '9xx-xxxx', 'weight': 0.4, 'description': 'Celular 9 + 6 aleatorios'}
                        ]
                    }
                }
            },
            'peru': {
                'country_code': '+51',
                'strategy': 'area_code_full',
                'area_codes': {
                    '1': {
                        'name': 'Lima, LIM',
                        'patterns': [
                            {'mask': 'xxxx-xxxx', 'weight': 0.6, 'description': '8 dígitos aleatorios'},
                            {'mask': '9xx-xxxx', 'weight': 0.4, 'description': 'Celular 9 + 6 aleatorios'}
                        ]
                    },
                    '44': {
                        'name': 'Trujillo, LAL',
                        'patterns': [
                            {'mask': 'xxx-xxxx', 'weight': 0.6, 'description': '7 dígitos aleatorios'},
                            {'mask': '9xx-xxxx', 'weight': 0.4, 'description': 'Celular 9 + 6 aleatorios'}
                        ]
                    },
                    '51': {
                        'name': 'Arequipa, ARE',
                        'patterns': [
                            {'mask': 'xxx-xxxx', 'weight': 0.6, 'description': '7 dígitos aleatorios'},
                            {'mask': '9xx-xxxx', 'weight': 0.4, 'description': 'Celular 9 + 6 aleatorios'}
                        ]
                    }
                }
            }
        }
    
    def get_supported_countries(self) -> List[Dict[str, Any]]:
        """Obtiene lista de países soportados."""
        countries = []
        for country_code, config in self.pattern_configs.items():
            countries.append({
                'country_code': country_code,
                'country_name': self._get_country_name(country_code),
                'phone_code': config['country_code'],
                'strategy': config['strategy'],
                'area_codes': list(config['area_codes'].keys())
            })
        return countries
    
    def _get_country_name(self, country_code: str) -> str:
        """Obtiene nombre del país en español."""
        names = {
            'usa': 'Estados Unidos',
            'canada': 'Canadá',
            'mexico': 'México',
            'brasil': 'Brasil',
            'colombia': 'Colombia',
            'argentina': 'Argentina',
            'chile': 'Chile',
            'peru': 'Perú'
        }
        return names.get(country_code, country_code.upper())
    
    def get_country_patterns(self, country: str) -> Dict[str, Any]:
        """Obtiene patrones disponibles para un país."""
        if country not in self.pattern_configs:
            return {}
        
        config = self.pattern_configs[country]
        return {
            'country_code': country,
            'country_name': self._get_country_name(country),
            'phone_code': config['country_code'],
            'strategy': config['strategy'],
            'area_codes': config['area_codes']
        }
    
    def generate_cli_with_pattern(
        self,
        destination_number: str,
        custom_pattern: Optional[str] = None,
        custom_area_code: Optional[str] = None,
        quantity: int = 1,
        country_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera CLIs con patrones personalizados.
        
        Args:
            destination_number: Número de destino
            custom_pattern: Patrón personalizado (ej: "2xx-xxxx", "35x-xxxx")
            custom_area_code: Código de área específico para forzar
            quantity: Cantidad de CLIs a generar
            country_override: Forzar país específico
            
        Returns:
            Dict con CLIs generados y metadatos
        """
        try:
            # Detectar país
            country = country_override or self._detect_country(destination_number)
            
            if country not in self.pattern_configs:
                return self._generate_fallback_response(destination_number, country)
            
            country_config = self.pattern_configs[country]
            
            # Extraer información del número
            area_info = self._extract_area_info(destination_number, country_config)
            
            # Determinar código de área a usar
            target_area_code = custom_area_code or area_info.get("area_code")
            
            if not target_area_code:
                return self._generate_fallback_response(destination_number, country)
            
            # Generar CLIs
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
            
            # Registrar generación
            self._track_generation(country, target_area_code, quantity)
            
            return {
                'success': True,
                'country': country,
                'country_name': self._get_country_name(country),
                'area_code': target_area_code,
                'area_name': area_info.get('area_name', ''),
                'pattern_used': custom_pattern or 'default',
                'quantity': len(generated_clis),
                'generated_clis': generated_clis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error al generar CLIs: {str(e)}")
            return {
                'success': False,
                'error': f'Error al generar CLIs: {str(e)}',
                'country': country_override or 'unknown',
                'generated_clis': []
            }
    
    def generate_bulk_patterns(
        self,
        destination_numbers: List[str],
        custom_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """Genera patrones para múltiples números."""
        try:
            results = []
            
            for number in destination_numbers:
                result = self.generate_cli_with_pattern(
                    destination_number=number,
                    custom_pattern=custom_pattern,
                    quantity=1
                )
                results.append(result)
            
            return {
                'success': True,
                'total_numbers': len(destination_numbers),
                'successful_generations': len([r for r in results if r.get('success')]),
                'generated_clis': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error en generación masiva: {str(e)}")
            return {
                'success': False,
                'error': f'Error en generación masiva: {str(e)}',
                'generated_clis': []
            }
    
    def _generate_cli_with_custom_pattern(
        self,
        country_config: Dict[str, Any],
        area_code: str,
        custom_pattern: str
    ) -> str:
        """Genera CLI con patrón personalizado."""
        try:
            country_code = country_config["country_code"]
            
            # Procesar patrón personalizado
            processed_pattern = self._process_pattern(custom_pattern)
            
            # Construir CLI
            cli = f"{country_code}{area_code}{processed_pattern}"
            
            return cli
            
        except Exception as e:
            logger.error(f"❌ Error al generar CLI con patrón personalizado: {str(e)}")
            return None
    
    def _generate_cli_with_default_pattern(
        self,
        country_config: Dict[str, Any],
        area_code: str
    ) -> str:
        """Genera CLI con patrón por defecto del área."""
        try:
            country_code = country_config["country_code"]
            area_config = country_config["area_codes"].get(area_code)
            
            if not area_config:
                # Usar patrón genérico
                return f"{country_code}{area_code}{''.join([str(random.randint(0, 9)) for _ in range(7)])}"
            
            # Seleccionar patrón basado en el peso
            patterns = area_config["patterns"]
            weights = [p["weight"] for p in patterns]
            selected_pattern = random.choices(patterns, weights=weights)[0]
            
            # Procesar patrón
            processed_pattern = self._process_pattern(selected_pattern["mask"])
            
            # Construir CLI
            cli = f"{country_code}{area_code}{processed_pattern}"
            
            return cli
            
        except Exception as e:
            logger.error(f"❌ Error al generar CLI con patrón por defecto: {str(e)}")
            return None
    
    def _process_pattern(self, pattern: str) -> str:
        """Procesa patrón de máscara convirtiendo 'x' en dígitos aleatorios."""
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
        """Detecta país basado en el número."""
        clean_number = re.sub(r'[^\d+]', '', number)
        
        if clean_number.startswith('+'):
            clean_number = clean_number[1:]
        
        # Códigos de país
        if clean_number.startswith('1'):
            # Verificar si es USA o Canada
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
        """Extrae información del código de área del número."""
        clean_number = re.sub(r'[^\d+]', '', number)
        
        if clean_number.startswith('+'):
            clean_number = clean_number[1:]
        
        # Remover código de país
        country_code = country_config["country_code"].replace('+', '')
        if clean_number.startswith(country_code):
            clean_number = clean_number[len(country_code):]
        
        # Detectar código de área
        area_codes = country_config["area_codes"].keys()
        
        for area_code in sorted(area_codes, key=len, reverse=True):
            if clean_number.startswith(area_code):
                area_config = country_config["area_codes"][area_code]
                return {
                    "area_code": area_code,
                    "area_name": area_config["name"],
                    "patterns": area_config["patterns"]
                }
        
        # Si no encuentra, usar el primer disponible
        first_area = list(area_codes)[0]
        return {
            "area_code": first_area,
            "area_name": country_config["area_codes"][first_area]["name"],
            "patterns": country_config["area_codes"][first_area]["patterns"]
        }
    
    def _generate_fallback_response(self, destination_number: str, country: str) -> Dict[str, Any]:
        """Genera respuesta de fallback cuando no se puede procesar."""
        return {
            'success': False,
            'error': f'País {country} no soportado o número inválido',
            'country': country,
            'destination_number': destination_number,
            'generated_clis': []
        }
    
    def _track_generation(self, country: str, area_code: str, quantity: int):
        """Registra la generación para estadísticas."""
        # Implementar tracking si es necesario
        pass
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de generación."""
        return {
            'total_countries': len(self.pattern_configs),
            'total_area_codes': sum(len(config['area_codes']) for config in self.pattern_configs.values()),
            'supported_countries': list(self.pattern_configs.keys()),
            'generation_timestamp': datetime.now().isoformat()
        } 