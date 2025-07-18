from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime
import random
import re
from app.models.cli import Cli
from app.models.trunk import Trunk
from app.database import get_db
import logging

logger = logging.getLogger(__name__)

class DynamicCliService:
    """
    Serviço para geração de CLI dinâmico conforme regras específicas por país.
    
    Regras implementadas:
    - MXN (México): Detecta código de área e gera últimos 4 dígitos aleatórios
    - ALEATORIO (USA/Canadá): Código de área aleatório para estados com código único
    - ALEATORIO1 (USA/Canadá): Adiciona "1" no início quando exigido pelo provedor
    - DID (USA/Canadá): Usa mesmo prefixo do DID quando disponível
    - DID1 (USA/Canadá): DID com "1" no início
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cli_usage_cache = {}  # Cache para controle de uso diário
        self.area_codes_usa_canada = self._load_usa_canada_area_codes()
        self.florida_codes = ['239', '305', '321', '352', '386', '407', '561', '727', '754', '772', '786', '813', '850', '863', '904', '941', '954']
        
    def _load_usa_canada_area_codes(self) -> Dict[str, List[str]]:
        """
        Carrega códigos de área dos EUA e Canadá por estado/província.
        """
        # Códigos de área por estado (exemplo da Flórida mencionado pelo cliente)
        return {
            'florida': ['239', '305', '321', '352', '386', '407', '561', '727', '754', '772', '786', '813', '850', '863', '904', '941', '954'],
            'california': ['209', '213', '279', '310', '323', '341', '408', '415', '424', '442', '510', '530', '559', '562', '619', '626', '628', '650', '657', '661', '669', '707', '714', '747', '760', '805', '818', '831', '858', '909', '916', '925', '949', '951'],
            'texas': ['214', '254', '281', '409', '430', '432', '469', '512', '713', '737', '806', '817', '832', '903', '915', '936', '940', '956', '972', '979'],
            'new_york': ['212', '315', '347', '516', '518', '585', '607', '631', '646', '680', '716', '718', '845', '914', '917', '929', '934'],
            'delaware': ['302'],  # Estado com código único
            'wyoming': ['307'],   # Estado com código único
            'alaska': ['907'],    # Estado com código único
            'hawaii': ['808'],    # Estado com código único
            # Canadá
            'ontario': ['416', '437', '519', '613', '647', '705', '807', '905'],
            'quebec': ['418', '438', '450', '514', '579', '581', '819', '873'],
            'british_columbia': ['236', '250', '604', '672', '778'],
            'alberta': ['403', '587', '780', '825']
        }
    
    def generate_dynamic_cli(self, destination_number: str, cli_type: str, trunk_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera CLI dinâmico baseado no tipo e número de destino.
        
        Args:
            destination_number: Número que será discado
            cli_type: Tipo de CLI (MXN, ALEATORIO, ALEATORIO1, DID, DID1)
            trunk_id: ID do trunk para obter configurações específicas
            
        Returns:
            Dict com CLI gerado e informações adicionais
        """
        try:
            # Limpar número de destino
            clean_destination = re.sub(r'[^0-9]', '', destination_number)
            
            if cli_type == 'MXN':
                return self._generate_mexico_cli(clean_destination)
            elif cli_type == 'ALEATORIO':
                return self._generate_random_usa_canada_cli(clean_destination, add_prefix=False)
            elif cli_type == 'ALEATORIO1':
                return self._generate_random_usa_canada_cli(clean_destination, add_prefix=True)
            elif cli_type == 'DID':
                return self._generate_did_cli(clean_destination, trunk_id, add_prefix=False)
            elif cli_type == 'DID1':
                return self._generate_did_cli(clean_destination, trunk_id, add_prefix=True)
            else:
                return {
                    'cli': None,
                    'error': f'Tipo de CLI não suportado: {cli_type}',
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"Erro ao gerar CLI dinâmico: {str(e)}")
            return {
                'cli': None,
                'error': str(e),
                'success': False
            }
    
    def _generate_mexico_cli(self, destination_number: str) -> Dict[str, Any]:
        """
        Gera CLI para México baseado no número de destino.
        
        Regras:
        - Se número tem 8 dígitos (ex: 55 2222 2222): mostra 55 2222-xxxx
        - Se número tem 10 dígitos (ex: 998 222 2222): mostra 998 222-xxxx
        - Gera últimos 4 dígitos aleatoriamente
        """
        try:
            # Remover código do país se presente (52)
            if destination_number.startswith('52'):
                destination_number = destination_number[2:]
            
            if len(destination_number) == 8:
                # Cidade do México, Jalisco, Nuevo León (8 dígitos)
                area_code = destination_number[:2]
                prefix = destination_number[2:6]
                random_suffix = f"{random.randint(0, 9999):04d}"
                cli = f"{area_code}{prefix}{random_suffix}"
                display_cli = f"{area_code} {prefix}-{random_suffix}"
                
            elif len(destination_number) == 10:
                # Cancún e outras cidades (10 dígitos)
                area_code = destination_number[:3]
                prefix = destination_number[3:6]
                random_suffix = f"{random.randint(0, 9999):04d}"
                cli = f"{area_code}{prefix}{random_suffix}"
                display_cli = f"{area_code} {prefix}-{random_suffix}"
                
            else:
                return {
                    'cli': None,
                    'error': f'Formato de número mexicano inválido: {destination_number}',
                    'success': False
                }
            
            return {
                'cli': cli,
                'display_cli': display_cli,
                'country': 'Mexico',
                'type': 'MXN',
                'success': True
            }
            
        except Exception as e:
            return {
                'cli': None,
                'error': f'Erro ao gerar CLI mexicano: {str(e)}',
                'success': False
            }
    
    def _generate_random_usa_canada_cli(self, destination_number: str, add_prefix: bool = False) -> Dict[str, Any]:
        """
        Gera CLI aleatório para USA/Canadá evitando mesmo código de área do destino.
        
        Regras:
        - Se estado tem múltiplos códigos: escolhe aleatório diferente do destino
        - Se estado tem código único: escolhe qualquer código aleatório
        """
        try:
            # Remover código do país se presente (1)
            if destination_number.startswith('1'):
                destination_number = destination_number[1:]
            
            if len(destination_number) < 10:
                return {
                    'cli': None,
                    'error': f'Número USA/Canadá deve ter 10 dígitos: {destination_number}',
                    'success': False
                }
            
            dest_area_code = destination_number[:3]
            
            # Encontrar estado do código de área de destino
            dest_state = self._find_state_by_area_code(dest_area_code)
            
            if dest_state and len(self.area_codes_usa_canada[dest_state]) > 1:
                # Estado com múltiplos códigos - escolher diferente do destino
                available_codes = [code for code in self.area_codes_usa_canada[dest_state] if code != dest_area_code]
                if available_codes:
                    selected_area_code = random.choice(available_codes)
                else:
                    # Fallback para qualquer código
                    selected_area_code = self._get_random_area_code(exclude=dest_area_code)
            else:
                # Estado com código único ou não encontrado - usar qualquer código aleatório
                selected_area_code = self._get_random_area_code(exclude=dest_area_code)
            
            # Gerar número aleatório
            random_number = f"{random.randint(200, 999)}{random.randint(0, 9999):04d}"
            
            cli = f"{selected_area_code}{random_number}"
            if add_prefix:
                cli = f"1{cli}"
                display_cli = f"1 {selected_area_code} {random_number[:3]}-{random_number[3:]}"
            else:
                display_cli = f"{selected_area_code} {random_number[:3]}-{random_number[3:]}"
            
            return {
                'cli': cli,
                'display_cli': display_cli,
                'country': 'USA/Canada',
                'type': 'ALEATORIO1' if add_prefix else 'ALEATORIO',
                'selected_area_code': selected_area_code,
                'dest_area_code': dest_area_code,
                'success': True
            }
            
        except Exception as e:
            return {
                'cli': None,
                'error': f'Erro ao gerar CLI aleatório: {str(e)}',
                'success': False
            }
    
    def _generate_did_cli(self, destination_number: str, trunk_id: Optional[int], add_prefix: bool = False) -> Dict[str, Any]:
        """
        Gera CLI baseado em DIDs disponíveis.
        
        Regras:
        - Usa mesmo prefixo do DID se disponível
        - Controla limite de 100 usos por dia
        - Se não encontra DID do mesmo código, usa outro do mesmo estado
        """
        try:
            # Remover código do país se presente (1)
            if destination_number.startswith('1'):
                destination_number = destination_number[1:]
            
            dest_area_code = destination_number[:3]
            
            # Buscar DIDs disponíveis do mesmo código de área
            available_dids = self._get_available_dids(dest_area_code, trunk_id)
            
            if not available_dids:
                # Buscar DIDs do mesmo estado
                dest_state = self._find_state_by_area_code(dest_area_code)
                if dest_state:
                    state_area_codes = self.area_codes_usa_canada[dest_state]
                    for area_code in state_area_codes:
                        if area_code != dest_area_code:
                            available_dids = self._get_available_dids(area_code, trunk_id)
                            if available_dids:
                                break
            
            if not available_dids:
                return {
                    'cli': None,
                    'error': f'Nenhum DID disponível para área {dest_area_code}',
                    'success': False
                }
            
            # Selecionar DID com menor uso hoje
            selected_did = self._select_least_used_did(available_dids)
            
            # Verificar limite diário
            usage_today = self._get_did_usage_today(selected_did['numero'])
            if usage_today >= 100:
                return {
                    'cli': None,
                    'error': f'DID {selected_did["numero"]} atingiu limite diário (100 usos)',
                    'success': False,
                    'limit_reached': True
                }
            
            # Gerar CLI baseado no DID
            did_number = re.sub(r'[^0-9]', '', selected_did['numero'])
            if len(did_number) >= 10:
                area_code = did_number[:3]
                prefix = did_number[3:6]
                random_suffix = f"{random.randint(0, 9999):04d}"
                
                cli = f"{area_code}{prefix}{random_suffix}"
                if add_prefix:
                    cli = f"1{cli}"
                    display_cli = f"1 {area_code} {prefix}-{random_suffix}"
                else:
                    display_cli = f"{area_code} {prefix}-{random_suffix}"
                
                # Registrar uso
                self._register_did_usage(selected_did['numero'])
                
                return {
                    'cli': cli,
                    'display_cli': display_cli,
                    'country': 'USA/Canada',
                    'type': 'DID1' if add_prefix else 'DID',
                    'did_used': selected_did['numero'],
                    'usage_today': usage_today + 1,
                    'success': True
                }
            
            return {
                'cli': None,
                'error': f'Formato de DID inválido: {selected_did["numero"]}',
                'success': False
            }
            
        except Exception as e:
            return {
                'cli': None,
                'error': f'Erro ao gerar CLI DID: {str(e)}',
                'success': False
            }
    
    def _find_state_by_area_code(self, area_code: str) -> Optional[str]:
        """Encontra o estado/província pelo código de área."""
        for state, codes in self.area_codes_usa_canada.items():
            if area_code in codes:
                return state
        return None
    
    def _get_random_area_code(self, exclude: str = None) -> str:
        """Obtém código de área aleatório."""
        all_codes = []
        for codes in self.area_codes_usa_canada.values():
            all_codes.extend(codes)
        
        if exclude:
            all_codes = [code for code in all_codes if code != exclude]
        
        return random.choice(all_codes) if all_codes else '555'
    
    def _get_available_dids(self, area_code: str, trunk_id: Optional[int]) -> List[Dict]:
        """Busca DIDs disponíveis para um código de área."""
        query = self.db.query(Cli).filter(
            Cli.activo == True,
            Cli.numero.like(f'%{area_code}%')
        )
        
        if trunk_id:
            query = query.filter(Cli.proveedor_id == trunk_id)
        
        dids = query.all()
        return [{'numero': did.numero, 'id': did.id} for did in dids]
    
    def _select_least_used_did(self, available_dids: List[Dict]) -> Dict:
        """Seleciona o DID com menor uso hoje."""
        # Por simplicidade, retorna o primeiro. Em produção, implementar lógica de menor uso
        return available_dids[0]
    
    def _get_did_usage_today(self, did_number: str) -> int:
        """Obtém quantidade de usos do DID hoje."""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.cli_usage_cache.get(f"{did_number}_{today}", 0)
    
    def _register_did_usage(self, did_number: str):
        """Registra uso do DID."""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"{did_number}_{today}"
        self.cli_usage_cache[key] = self.cli_usage_cache.get(key, 0) + 1
    
    def get_cli_usage_stats(self, did_number: Optional[str] = None) -> Dict[str, Any]:
        """Obtém estatísticas de uso de CLIs."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if did_number:
            usage_today = self._get_did_usage_today(did_number)
            return {
                'did_number': did_number,
                'usage_today': usage_today,
                'limit': 100,
                'remaining': max(0, 100 - usage_today),
                'percentage_used': (usage_today / 100) * 100
            }
        
        # Estatísticas gerais
        total_usage = sum(count for key, count in self.cli_usage_cache.items() if today in key)
        return {
            'total_usage_today': total_usage,
            'active_dids': len([key for key in self.cli_usage_cache.keys() if today in key]),
            'date': today
        }
    
    def reset_daily_usage(self):
        """Reseta contadores diários (executar via cron à meia-noite)."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        keys_to_remove = [key for key in self.cli_usage_cache.keys() if yesterday in key]
        for key in keys_to_remove:
            del self.cli_usage_cache[key]
        
        logger.info(f"Reset de uso diário executado. Removidas {len(keys_to_remove)} entradas.")