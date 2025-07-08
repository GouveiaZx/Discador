"""
Serviço avançado de shuffle para randomização inteligente de contatos.
Evita discagem sequencial e implementa múltiplas estratégias de aleatorização.
"""

import random
import math
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ShuffleStrategy(Enum):
    """Estratégias de aleatorização disponíveis"""
    SIMPLE_RANDOM = "simple_random"          # Shuffle simples
    GEOGRAPHIC_DISPERSION = "geo_dispersion"  # Dispersar por região geográfica  
    TIME_BASED = "time_based"                # Baseado em horários ótimos
    PROGRESSIVE_BLOCKS = "progressive_blocks" # Blocos progressivos
    ANTI_PATTERN = "anti_pattern"            # Anti-padrão para evitar detecção
    BALANCED_DISTRIBUTION = "balanced_dist"   # Distribuição balanceada

@dataclass
class ShuffleConfig:
    """Configuração para algoritmos de shuffle"""
    strategy: ShuffleStrategy
    block_size: int = 100
    geographic_zones: int = 5
    time_windows: int = 4
    anti_pattern_factor: float = 0.3
    preserve_contacts: bool = False

@dataclass
class ContactInfo:
    """Informações de um contato"""
    numero_original: str
    numero_normalizado: str
    nome: str = ""
    apellido: str = ""
    empresa: str = ""
    zone_hint: str = ""  # Dica de zona geográfica
    priority: int = 1    # Prioridade (1-5)

class AdvancedShuffleService:
    """Serviço principal para shuffle avançado de contatos"""
    
    def __init__(self):
        self.zone_prefixes = self._load_zone_prefixes()
    
    def shuffle_contacts(
        self, 
        contacts: List[Dict[str, Any]], 
        config: ShuffleConfig
    ) -> List[ContactInfo]:
        """
        Aplica algoritmo de shuffle baseado na configuração
        
        Args:
            contacts: Lista de contatos para aleatorizar
            config: Configuração do algoritmo de shuffle
            
        Returns:
            Lista de contatos aleatorizada com ContactInfo
        """
        # Converter para ContactInfo
        contact_objects = self._convert_to_contact_info(contacts)
        
        if not contact_objects:
            return contact_objects
        
        logger.info(f"Iniciando shuffle de {len(contact_objects)} contatos com estratégia: {config.strategy.value}")
        
        # Aplicar estratégia específica
        if config.strategy == ShuffleStrategy.SIMPLE_RANDOM:
            shuffled = self._simple_random_shuffle(contact_objects)
        elif config.strategy == ShuffleStrategy.GEOGRAPHIC_DISPERSION:
            shuffled = self._geographic_dispersion_shuffle(contact_objects, config)
        elif config.strategy == ShuffleStrategy.TIME_BASED:
            shuffled = self._time_based_shuffle(contact_objects, config)
        elif config.strategy == ShuffleStrategy.PROGRESSIVE_BLOCKS:
            shuffled = self._progressive_blocks_shuffle(contact_objects, config)
        elif config.strategy == ShuffleStrategy.ANTI_PATTERN:
            shuffled = self._anti_pattern_shuffle(contact_objects, config)
        elif config.strategy == ShuffleStrategy.BALANCED_DISTRIBUTION:
            shuffled = self._balanced_distribution_shuffle(contact_objects, config)
        else:
            # Fallback para shuffle simples
            shuffled = self._simple_random_shuffle(contact_objects)
        
        logger.info(f"Shuffle concluído: {len(shuffled)} contatos reorganizados")
        return shuffled
    
    def _convert_to_contact_info(self, contacts: List[Dict[str, Any]]) -> List[ContactInfo]:
        """Converte lista de dicionários para ContactInfo"""
        contact_objects = []
        
        for contact in contacts:
            # Detectar zona geográfica pelo prefixo
            zone_hint = self._detect_geographic_zone(contact.get('numero_normalizado', ''))
            
            contact_obj = ContactInfo(
                numero_original=contact.get('numero_original', ''),
                numero_normalizado=contact.get('numero_normalizado', ''),
                nome=contact.get('nome', ''),
                apellido=contact.get('apellido', ''),
                empresa=contact.get('empresa', ''),
                zone_hint=zone_hint,
                priority=contact.get('priority', 1)
            )
            contact_objects.append(contact_obj)
        
        return contact_objects
    
    def _simple_random_shuffle(self, contacts: List[ContactInfo]) -> List[ContactInfo]:
        """Shuffle simples padrão do Python"""
        shuffled = contacts.copy()
        random.shuffle(shuffled)
        return shuffled
    
    def _geographic_dispersion_shuffle(
        self, 
        contacts: List[ContactInfo], 
        config: ShuffleConfig
    ) -> List[ContactInfo]:
        """
        Aleatoriza garantindo dispersão geográfica.
        Evita ligar para a mesma região sequencialmente.
        """
        # Agrupar por zona geográfica
        zones: Dict[str, List[ContactInfo]] = {}
        for contact in contacts:
            zone = contact.zone_hint or 'unknown'
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(contact)
        
        # Shuffle dentro de cada zona
        for zone_contacts in zones.values():
            random.shuffle(zone_contacts)
        
        # Distribuir alternando zonas
        shuffled = []
        zone_keys = list(zones.keys())
        random.shuffle(zone_keys)  # Randomizar ordem das zonas
        
        max_zone_size = max(len(zone_contacts) for zone_contacts in zones.values())
        
        for i in range(max_zone_size):
            for zone in zone_keys:
                if i < len(zones[zone]):
                    shuffled.append(zones[zone][i])
        
        logger.info(f"Dispersão geográfica aplicada: {len(zones)} zonas identificadas")
        return shuffled
    
    def _time_based_shuffle(
        self, 
        contacts: List[ContactInfo], 
        config: ShuffleConfig
    ) -> List[ContactInfo]:
        """
        Aleatoriza baseado em janelas de tempo ótimas.
        Prioriza horários com maior taxa de resposta.
        """
        # Dividir em janelas de tempo (simulado)
        window_size = len(contacts) // config.time_windows
        windows = []
        
        for i in range(config.time_windows):
            start_idx = i * window_size
            end_idx = start_idx + window_size if i < config.time_windows - 1 else len(contacts)
            window_contacts = contacts[start_idx:end_idx]
            random.shuffle(window_contacts)
            windows.append(window_contacts)
        
        # Intercalar janelas baseado em prioridades (horários ótimos)
        shuffled = []
        max_window_size = max(len(window) for window in windows)
        
        # Ordem de prioridade das janelas (simulando horários ótimos)
        window_priority = [0, 2, 1, 3]  # Manhã, tarde, meio-dia, noite
        
        for i in range(max_window_size):
            for priority_idx in window_priority:
                if priority_idx < len(windows) and i < len(windows[priority_idx]):
                    shuffled.append(windows[priority_idx][i])
        
        logger.info(f"Shuffle temporal aplicado: {config.time_windows} janelas de tempo")
        return shuffled
    
    def _progressive_blocks_shuffle(
        self, 
        contacts: List[ContactInfo], 
        config: ShuffleConfig
    ) -> List[ContactInfo]:
        """
        Aleatoriza em blocos progressivos para distribuir a carga.
        Útil para campanhas longas.
        """
        # Dividir em blocos
        blocks = []
        block_size = config.block_size
        
        for i in range(0, len(contacts), block_size):
            block = contacts[i:i + block_size]
            random.shuffle(block)
            blocks.append(block)
        
        # Randomizar ordem dos blocos
        random.shuffle(blocks)
        
        # Intercalar contatos dos blocos
        shuffled = []
        max_block_size = max(len(block) for block in blocks) if blocks else 0
        
        for i in range(max_block_size):
            for block in blocks:
                if i < len(block):
                    shuffled.append(block[i])
        
        logger.info(f"Shuffle em blocos aplicado: {len(blocks)} blocos de {block_size} contatos")
        return shuffled
    
    def _anti_pattern_shuffle(
        self, 
        contacts: List[ContactInfo], 
        config: ShuffleConfig
    ) -> List[ContactInfo]:
        """
        Shuffle anti-padrão para evitar detecção de robôs.
        Introduz variações propositais.
        """
        shuffled = contacts.copy()
        
        # Shuffle inicial
        random.shuffle(shuffled)
        
        # Aplicar anti-padrão: trocar posições aleatoriamente
        num_swaps = int(len(shuffled) * config.anti_pattern_factor)
        
        for _ in range(num_swaps):
            # Escolher duas posições aleatórias distantes
            pos1 = random.randint(0, len(shuffled) - 1)
            pos2 = random.randint(0, len(shuffled) - 1)
            
            # Garantir que estão suficientemente distantes
            if abs(pos1 - pos2) > 10:
                shuffled[pos1], shuffled[pos2] = shuffled[pos2], shuffled[pos1]
        
        # Pequenas rotações em segmentos
        segment_size = 20
        for i in range(0, len(shuffled) - segment_size, segment_size * 2):
            segment = shuffled[i:i + segment_size]
            rotation = random.randint(1, segment_size - 1)
            rotated = segment[rotation:] + segment[:rotation]
            shuffled[i:i + segment_size] = rotated
        
        logger.info(f"Anti-padrão aplicado: {num_swaps} trocas, rotações em segmentos")
        return shuffled
    
    def _balanced_distribution_shuffle(
        self, 
        contacts: List[ContactInfo], 
        config: ShuffleConfig
    ) -> List[ContactInfo]:
        """
        Distribuição balanceada considerando múltiplos fatores.
        Combina zona geográfica, prioridade e aleatoriedade.
        """
        # Agrupar por zona e prioridade
        groups: Dict[str, List[ContactInfo]] = {}
        
        for contact in contacts:
            key = f"{contact.zone_hint}_{contact.priority}"
            if key not in groups:
                groups[key] = []
            groups[key].append(contact)
        
        # Shuffle dentro de cada grupo
        for group_contacts in groups.values():
            random.shuffle(group_contacts)
        
        # Distribuir balanceadamente
        shuffled = []
        group_keys = list(groups.keys())
        random.shuffle(group_keys)
        
        # Calcular pesos baseados na prioridade
        weighted_distribution = []
        for key in group_keys:
            priority = int(key.split('_')[-1])
            weight = priority * len(groups[key])
            weighted_distribution.extend([key] * weight)
        
        random.shuffle(weighted_distribution)
        
        # Distribuir contatos baseado nos pesos
        group_indices = {key: 0 for key in group_keys}
        
        for key in weighted_distribution:
            if group_indices[key] < len(groups[key]):
                shuffled.append(groups[key][group_indices[key]])
                group_indices[key] += 1
        
        # Adicionar contatos restantes
        for key in group_keys:
            for i in range(group_indices[key], len(groups[key])):
                shuffled.append(groups[key][i])
        
        logger.info(f"Distribuição balanceada aplicada: {len(groups)} grupos")
        return shuffled
    
    def _detect_geographic_zone(self, phone_number: str) -> str:
        """Detecta zona geográfica baseada no prefixo do número"""
        if not phone_number:
            return 'unknown'
        
        # Remover códigos de país comuns
        clean_number = phone_number
        for country_code in ['55', '1', '52', '57', '51']:
            if clean_number.startswith(country_code):
                clean_number = clean_number[len(country_code):]
                break
        
        # Extrair prefixo (primeiros 2-3 dígitos)
        prefix = clean_number[:3] if len(clean_number) >= 3 else clean_number
        
        # Mapear para zonas (exemplo para Brasil)
        if prefix.startswith('11'):
            return 'sao_paulo'
        elif prefix.startswith('21'):
            return 'rio_janeiro'
        elif prefix.startswith('31'):
            return 'minas_gerais'
        elif prefix.startswith('41'):
            return 'parana'
        elif prefix.startswith('51'):
            return 'rio_grande_sul'
        elif prefix.startswith('61'):
            return 'distrito_federal'
        elif prefix.startswith('71'):
            return 'bahia'
        elif prefix.startswith('81'):
            return 'pernambuco'
        elif prefix.startswith('85'):
            return 'ceara'
        else:
            return f'zone_{prefix[0] if prefix else "0"}'
    
    def _load_zone_prefixes(self) -> Dict[str, List[str]]:
        """Carrega mapeamento de prefixos por zona geográfica"""
        return {
            'sao_paulo': ['11', '12', '13', '14', '15', '16', '17', '18', '19'],
            'rio_janeiro': ['21', '22', '24'],
            'minas_gerais': ['31', '32', '33', '34', '35', '37', '38'],
            'parana': ['41', '42', '43', '44', '45', '46'],
            'rio_grande_sul': ['51', '53', '54', '55'],
            'distrito_federal': ['61'],
            'bahia': ['71', '73', '74', '75', '77'],
            'pernambuco': ['81', '87'],
            'ceara': ['85', '88']
        }
    
    def analyze_distribution(self, contacts: List[ContactInfo]) -> Dict[str, Any]:
        """Analisa a distribuição dos contatos após shuffle"""
        if not contacts:
            return {'error': 'Nenhum contato para analisar'}
        
        # Análise por zona geográfica
        zone_distribution = {}
        for contact in contacts:
            zone = contact.zone_hint
            zone_distribution[zone] = zone_distribution.get(zone, 0) + 1
        
        # Análise de dispersão (distância entre contatos da mesma zona)
        zone_positions = {}
        for i, contact in enumerate(contacts):
            zone = contact.zone_hint
            if zone not in zone_positions:
                zone_positions[zone] = []
            zone_positions[zone].append(i)
        
        # Calcular dispersão média
        avg_dispersion = 0
        total_zones = 0
        
        for zone, positions in zone_positions.items():
            if len(positions) > 1:
                distances = []
                for i in range(len(positions) - 1):
                    distances.append(positions[i + 1] - positions[i])
                avg_dispersion += sum(distances) / len(distances)
                total_zones += 1
        
        if total_zones > 0:
            avg_dispersion /= total_zones
        
        return {
            'total_contacts': len(contacts),
            'zone_distribution': zone_distribution,
            'unique_zones': len(zone_distribution),
            'average_dispersion': round(avg_dispersion, 2),
            'dispersion_quality': 'Excelente' if avg_dispersion > 50 
                                else 'Boa' if avg_dispersion > 20 
                                else 'Regular' if avg_dispersion > 10 
                                else 'Baixa'
        }

# Instância global do serviço
advanced_shuffle_service = AdvancedShuffleService()

def shuffle_contacts_advanced(
    contacts: List[Dict[str, Any]], 
    strategy: str = 'balanced_dist',
    **kwargs
) -> List[ContactInfo]:
    """
    Função de conveniência para shuffle avançado de contatos
    
    Args:
        contacts: Lista de contatos
        strategy: Estratégia de shuffle
        **kwargs: Parâmetros adicionais para configuração
    """
    try:
        strategy_enum = ShuffleStrategy(strategy)
    except ValueError:
        strategy_enum = ShuffleStrategy.BALANCED_DISTRIBUTION
    
    config = ShuffleConfig(
        strategy=strategy_enum,
        block_size=kwargs.get('block_size', 100),
        geographic_zones=kwargs.get('geographic_zones', 5),
        time_windows=kwargs.get('time_windows', 4),
        anti_pattern_factor=kwargs.get('anti_pattern_factor', 0.3)
    )
    
    return advanced_shuffle_service.shuffle_contacts(contacts, config) 