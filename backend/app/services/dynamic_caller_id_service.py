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
        """Gera CLIs específicos para Brasil."""
        clis = []
        area_codes = ["11", "21", "13", "47", "800", "85", "31", "51"]
        
        for area_code in area_codes:
            for i in range(200):  # 200 CLIs por área
                number = f"+55{area_code}555{i:04d}"
                clis.append(number)
        
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
            "usa": "+18885551000",
            "canada": "+18885551001", 
            "mexico": "+528005551000",
            "brasil": "+558005551000",
            "colombia": "+5715551000",
            "argentina": "+548005551000",
            "chile": "+5685551000",
            "peru": "+5185551000"
        }
        
        default_cli = fallback_clis.get(country.lower(), "+18885559999")
        
        return {
            "cli": default_cli,
            "country": country,
            "country_code": "+1",
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