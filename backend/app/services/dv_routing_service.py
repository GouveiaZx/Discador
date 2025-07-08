"""
Serviço para gerenciar códigos DV (Dial Via) e roteamento inteligente por país.
Permite usar diferentes códigos antes do código do país para otimizar rotas.
"""

import random
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from app.database import get_db_connection

logger = logging.getLogger(__name__)

@dataclass
class DVRoute:
    """Representa uma rota DV disponível"""
    dv_code: str
    country_code: str
    country_name: str
    cost_per_minute: float
    quality_score: int  # 1-10
    success_rate: float  # 0.0-1.0
    max_concurrent: int
    current_usage: int = 0
    is_active: bool = True

@dataclass
class CallRouting:
    """Resultado do roteamento de uma chamada"""
    dv_code: str
    full_number: str
    trunk_name: str
    estimated_cost: float
    quality_score: int

class DVRoutingService:
    """Serviço principal para roteamento DV"""
    
    def __init__(self):
        self.routes: Dict[str, List[DVRoute]] = {}
        self.load_routes()
    
    def load_routes(self):
        """Carrega rotas DV do banco de dados"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Carregar trunks com códigos DV
                cursor.execute("""
                    SELECT name, country_code, dv_codes, is_active,
                           trunk_type, sip_config
                    FROM trunks 
                    WHERE dv_codes IS NOT NULL AND is_active = true
                """)
                
                trunks = cursor.fetchall()
                
                for trunk in trunks:
                    name, country_code, dv_codes, is_active, trunk_type, sip_config = trunk
                    
                    if not dv_codes or not country_code:
                        continue
                        
                    # Parse dos códigos DV (JSON array)
                    import json
                    if isinstance(dv_codes, str):
                        dv_codes = json.loads(dv_codes)
                    
                    # Criar rotas para cada código DV
                    if country_code not in self.routes:
                        self.routes[country_code] = []
                    
                    for dv_code in dv_codes:
                        route = DVRoute(
                            dv_code=dv_code,
                            country_code=country_code,
                            country_name=self._get_country_name(country_code),
                            cost_per_minute=self._calculate_cost(country_code, dv_code),
                            quality_score=self._get_quality_score(dv_code),
                            success_rate=self._get_success_rate(dv_code),
                            max_concurrent=self._get_max_concurrent(trunk_type),
                            is_active=is_active
                        )
                        self.routes[country_code].append(route)
                
                logger.info(f"Carregadas {len(self.routes)} rotas DV para {sum(len(routes) for routes in self.routes.values())} códigos")
                
        except Exception as e:
            logger.error(f"Erro ao carregar rotas DV: {e}")
            self._load_default_routes()
    
    def _load_default_routes(self):
        """Carrega rotas padrão em caso de erro"""
        default_routes = {
            '1': [  # USA/Canadá
                DVRoute('01', '1', 'USA/Canadá', 0.02, 9, 0.95, 100),
                DVRoute('02', '1', 'USA/Canadá', 0.025, 8, 0.92, 80),
                DVRoute('03', '1', 'USA/Canadá', 0.03, 7, 0.88, 60)
            ],
            '52': [  # México
                DVRoute('04', '52', 'México', 0.05, 8, 0.90, 50),
                DVRoute('05', '52', 'México', 0.055, 7, 0.87, 40)
            ],
            '57': [  # Colômbia
                DVRoute('06', '57', 'Colômbia', 0.08, 7, 0.85, 30),
                DVRoute('07', '57', 'Colômbia', 0.09, 6, 0.82, 25)
            ],
            '51': [  # Peru
                DVRoute('08', '51', 'Peru', 0.10, 6, 0.80, 20),
                DVRoute('09', '51', 'Peru', 0.12, 5, 0.75, 15)
            ],
            '55': [  # Brasil
                DVRoute('10', '55', 'Brasil', 0.06, 8, 0.88, 40)
            ]
        }
        self.routes = default_routes
        logger.info("Carregadas rotas DV padrão")
    
    def get_best_route(self, phone_number: str, priority: str = 'balanced') -> Optional[CallRouting]:
        """
        Encontra a melhor rota DV para um número
        
        Args:
            phone_number: Número completo com código do país
            priority: 'cost' (menor custo), 'quality' (melhor qualidade), 'balanced' (equilibrado)
        """
        try:
            # Detectar código do país
            country_code = self._detect_country_code(phone_number)
            if not country_code:
                logger.warning(f"Código do país não detectado para: {phone_number}")
                return None
            
            # Buscar rotas disponíveis
            available_routes = self.routes.get(country_code, [])
            if not available_routes:
                logger.warning(f"Nenhuma rota DV disponível para país: {country_code}")
                return None
            
            # Filtrar rotas ativas e com capacidade
            active_routes = [
                route for route in available_routes 
                if route.is_active and route.current_usage < route.max_concurrent
            ]
            
            if not active_routes:
                logger.warning(f"Nenhuma rota DV ativa disponível para país: {country_code}")
                return None
            
            # Selecionar melhor rota baseada na prioridade
            best_route = self._select_route_by_priority(active_routes, priority)
            
            # Construir número completo com DV
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            if clean_number.startswith(country_code):
                national_number = clean_number[len(country_code):]
            else:
                national_number = clean_number
            
            full_number_with_dv = f"{best_route.dv_code}{country_code}{national_number}"
            
            # Estimar custo da chamada (assumindo 3 minutos médio)
            estimated_cost = best_route.cost_per_minute * 3.0
            
            # Incrementar uso da rota
            best_route.current_usage += 1
            
            routing = CallRouting(
                dv_code=best_route.dv_code,
                full_number=full_number_with_dv,
                trunk_name=f"trunk_{best_route.country_name.lower().replace('/', '_')}",
                estimated_cost=estimated_cost,
                quality_score=best_route.quality_score
            )
            
            logger.info(f"Rota selecionada: DV {best_route.dv_code} para {country_code} - Custo: ${estimated_cost:.3f}")
            return routing
            
        except Exception as e:
            logger.error(f"Erro ao encontrar rota DV: {e}")
            return None
    
    def _select_route_by_priority(self, routes: List[DVRoute], priority: str) -> DVRoute:
        """Seleciona a melhor rota baseada na prioridade"""
        if priority == 'cost':
            # Menor custo primeiro
            return min(routes, key=lambda r: r.cost_per_minute)
        elif priority == 'quality':
            # Melhor qualidade primeiro
            return max(routes, key=lambda r: r.quality_score * r.success_rate)
        else:  # balanced
            # Score balanceado: qualidade vs custo
            def balanced_score(route):
                # Score = qualidade * taxa_sucesso / custo
                return (route.quality_score * route.success_rate) / (route.cost_per_minute * 100)
            
            return max(routes, key=balanced_score)
    
    def _detect_country_code(self, phone_number: str) -> Optional[str]:
        """Detecta o código do país de um número de telefone"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Lista de códigos de país por ordem de tamanho (maiores primeiro)
        country_codes = ['1', '52', '55', '57', '51', '56', '54', '58']
        
        for code in country_codes:
            if clean_number.startswith(code):
                return code
        
        return None
    
    def _get_country_name(self, country_code: str) -> str:
        """Retorna o nome do país pelo código"""
        country_map = {
            '1': 'USA/Canadá',
            '52': 'México',
            '55': 'Brasil',
            '57': 'Colômbia',
            '51': 'Peru',
            '56': 'Chile',
            '54': 'Argentina',
            '58': 'Venezuela'
        }
        return country_map.get(country_code, f'País {country_code}')
    
    def _calculate_cost(self, country_code: str, dv_code: str) -> float:
        """Calcula o custo por minuto baseado no país e código DV"""
        base_costs = {
            '1': 0.02,    # USA/Canadá
            '52': 0.05,   # México
            '55': 0.06,   # Brasil
            '57': 0.08,   # Colômbia
            '51': 0.10,   # Peru
            '56': 0.07,   # Chile
            '54': 0.09,   # Argentina
            '58': 0.12    # Venezuela
        }
        
        base_cost = base_costs.get(country_code, 0.15)
        
        # Códigos DV menores = rotas premium (mais caras)
        dv_multiplier = 1.0 + (int(dv_code) - 1) * 0.1
        
        return base_cost * dv_multiplier
    
    def _get_quality_score(self, dv_code: str) -> int:
        """Retorna score de qualidade baseado no código DV"""
        # Códigos menores = melhor qualidade
        return max(1, 11 - int(dv_code))
    
    def _get_success_rate(self, dv_code: str) -> float:
        """Retorna taxa de sucesso baseada no código DV"""
        # Códigos menores = maior taxa de sucesso
        base_rate = 0.95
        return max(0.70, base_rate - (int(dv_code) - 1) * 0.02)
    
    def _get_max_concurrent(self, trunk_type: str) -> int:
        """Retorna limite de chamadas simultâneas por tipo de trunk"""
        limits = {
            'dv_voip': 100,
            'standard': 50,
            'residential': 10,
            'business': 30
        }
        return limits.get(trunk_type, 50)
    
    def release_route(self, dv_code: str, country_code: str):
        """Libera uma rota após o término da chamada"""
        routes = self.routes.get(country_code, [])
        for route in routes:
            if route.dv_code == dv_code and route.current_usage > 0:
                route.current_usage -= 1
                break
    
    def get_route_statistics(self) -> Dict:
        """Retorna estatísticas das rotas DV"""
        stats = {
            'total_countries': len(self.routes),
            'total_routes': sum(len(routes) for routes in self.routes.values()),
            'routes_by_country': {},
            'total_active_calls': 0
        }
        
        for country_code, routes in self.routes.items():
            active_routes = [r for r in routes if r.is_active]
            current_calls = sum(r.current_usage for r in routes)
            
            stats['routes_by_country'][country_code] = {
                'country_name': self._get_country_name(country_code),
                'total_routes': len(routes),
                'active_routes': len(active_routes),
                'current_calls': current_calls,
                'avg_cost': sum(r.cost_per_minute for r in routes) / len(routes) if routes else 0,
                'avg_quality': sum(r.quality_score for r in routes) / len(routes) if routes else 0
            }
            
            stats['total_active_calls'] += current_calls
        
        return stats
    
    def optimize_routes(self) -> Dict:
        """Otimiza a distribuição de rotas baseada no uso"""
        optimizations = []
        
        for country_code, routes in self.routes.items():
            # Identificar rotas sobrecarregadas
            overloaded = [r for r in routes if r.current_usage >= r.max_concurrent * 0.9]
            underused = [r for r in routes if r.current_usage <= r.max_concurrent * 0.3]
            
            if overloaded and underused:
                for route in overloaded:
                    optimizations.append({
                        'type': 'redistribute',
                        'country': self._get_country_name(country_code),
                        'from_dv': route.dv_code,
                        'to_dv': underused[0].dv_code,
                        'reason': 'Balanceamento de carga'
                    })
        
        return {
            'optimizations': optimizations,
            'timestamp': datetime.now().isoformat()
        }

# Instância global do serviço
dv_routing_service = DVRoutingService()

def get_best_dv_route(phone_number: str, priority: str = 'balanced') -> Optional[CallRouting]:
    """Função de conveniência para obter a melhor rota DV"""
    return dv_routing_service.get_best_route(phone_number, priority)

def release_dv_route(dv_code: str, country_code: str):
    """Função de conveniência para liberar uma rota DV"""
    return dv_routing_service.release_route(dv_code, country_code)

def get_dv_statistics() -> Dict:
    """Função de conveniência para obter estatísticas DV"""
    return dv_routing_service.get_route_statistics() 