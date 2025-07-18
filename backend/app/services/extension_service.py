from typing import List, Dict, Optional, Any
from datetime import datetime, time
import asyncio
import json
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from ..database import get_db
from ..models.extension import Extension, ExtensionStats
from ..utils.logger import logger
from ..utils.asterisk_ami import AsteriskAMI
import re

class ExtensionService:
    def __init__(self):
        self.ami = AsteriskAMI()
        self._stats_cache = {}
        self._last_stats_update = None
    
    async def create_extension(self, extension_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Cria uma nova extensão
        """
        try:
            # Validar dados
            self._validate_extension_data(extension_data)
            
            # Verificar se o número já existe
            existing = db.query(Extension).filter(
                Extension.numero == extension_data['numero']
            ).first()
            
            if existing:
                raise ValueError(f"Extensão {extension_data['numero']} já existe")
            
            # Criar extensão
            extension = Extension(
                numero=extension_data['numero'],
                nome=extension_data['nome'],
                campanha_id=extension_data.get('campanha_id'),
                ativo=extension_data.get('ativo', True),
                configuracoes=extension_data.get('configuracoes', {}),
                horario_funcionamento=extension_data.get('horario_funcionamento', {}),
                created_at=datetime.utcnow()
            )
            
            db.add(extension)
            db.commit()
            db.refresh(extension)
            
            # Gerar configuração do Asterisk
            await self._generate_asterisk_config(extension)
            
            # Recarregar configuração do Asterisk
            await self._reload_asterisk_config()
            
            logger.info(f"Extensão {extension.numero} criada com sucesso")
            
            return {
                'id': extension.id,
                'numero': extension.numero,
                'nome': extension.nome,
                'campanha_id': extension.campanha_id,
                'ativo': extension.ativo,
                'configuracoes': extension.configuracoes,
                'horario_funcionamento': extension.horario_funcionamento,
                'created_at': extension.created_at.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao criar extensão: {str(e)}")
            raise
    
    async def get_extensions(self, db: Session, campanha_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista todas as extensões
        """
        try:
            query = db.query(Extension)
            
            if campanha_id:
                query = query.filter(Extension.campanha_id == campanha_id)
            
            extensions = query.order_by(Extension.numero).all()
            
            result = []
            for ext in extensions:
                result.append({
                    'id': ext.id,
                    'numero': ext.numero,
                    'nome': ext.nome,
                    'campanha_id': ext.campanha_id,
                    'ativo': ext.ativo,
                    'configuracoes': ext.configuracoes,
                    'horario_funcionamento': ext.horario_funcionamento,
                    'created_at': ext.created_at.isoformat() if ext.created_at else None,
                    'updated_at': ext.updated_at.isoformat() if ext.updated_at else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao listar extensões: {str(e)}")
            raise
    
    async def get_extension(self, extension_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """
        Obtém uma extensão específica
        """
        try:
            extension = db.query(Extension).filter(Extension.id == extension_id).first()
            
            if not extension:
                return None
            
            return {
                'id': extension.id,
                'numero': extension.numero,
                'nome': extension.nome,
                'campanha_id': extension.campanha_id,
                'ativo': extension.ativo,
                'configuracoes': extension.configuracoes,
                'horario_funcionamento': extension.horario_funcionamento,
                'created_at': extension.created_at.isoformat() if extension.created_at else None,
                'updated_at': extension.updated_at.isoformat() if extension.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter extensão {extension_id}: {str(e)}")
            raise
    
    async def update_extension(self, extension_id: int, extension_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Atualiza uma extensão
        """
        try:
            extension = db.query(Extension).filter(Extension.id == extension_id).first()
            
            if not extension:
                raise ValueError("Extensão não encontrada")
            
            # Validar dados
            self._validate_extension_data(extension_data)
            
            # Verificar se o número já existe (exceto para a própria extensão)
            if extension_data.get('numero') != extension.numero:
                existing = db.query(Extension).filter(
                    and_(
                        Extension.numero == extension_data['numero'],
                        Extension.id != extension_id
                    )
                ).first()
                
                if existing:
                    raise ValueError(f"Extensão {extension_data['numero']} já existe")
            
            # Atualizar campos
            extension.numero = extension_data.get('numero', extension.numero)
            extension.nome = extension_data.get('nome', extension.nome)
            extension.campanha_id = extension_data.get('campanha_id', extension.campanha_id)
            extension.ativo = extension_data.get('ativo', extension.ativo)
            extension.configuracoes = extension_data.get('configuracoes', extension.configuracoes)
            extension.horario_funcionamento = extension_data.get('horario_funcionamento', extension.horario_funcionamento)
            extension.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(extension)
            
            # Regenerar configuração do Asterisk
            await self._generate_asterisk_config(extension)
            await self._reload_asterisk_config()
            
            logger.info(f"Extensão {extension.numero} atualizada com sucesso")
            
            return {
                'id': extension.id,
                'numero': extension.numero,
                'nome': extension.nome,
                'campanha_id': extension.campanha_id,
                'ativo': extension.ativo,
                'configuracoes': extension.configuracoes,
                'horario_funcionamento': extension.horario_funcionamento,
                'updated_at': extension.updated_at.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao atualizar extensão {extension_id}: {str(e)}")
            raise
    
    async def delete_extension(self, extension_id: int, db: Session) -> bool:
        """
        Deleta uma extensão
        """
        try:
            extension = db.query(Extension).filter(Extension.id == extension_id).first()
            
            if not extension:
                raise ValueError("Extensão não encontrada")
            
            # Verificar se há chamadas ativas
            stats = await self.get_extension_stats(extension.numero)
            if stats and stats.get('active_calls', 0) > 0:
                raise ValueError("Não é possível deletar extensão com chamadas ativas")
            
            numero = extension.numero
            
            # Deletar estatísticas relacionadas
            db.query(ExtensionStats).filter(ExtensionStats.extension_id == extension_id).delete()
            
            # Deletar extensão
            db.delete(extension)
            db.commit()
            
            # Remover configuração do Asterisk
            await self._remove_asterisk_config(numero)
            await self._reload_asterisk_config()
            
            logger.info(f"Extensão {numero} deletada com sucesso")
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao deletar extensão {extension_id}: {str(e)}")
            raise
    
    async def toggle_extension_status(self, extension_id: int, db: Session) -> Dict[str, Any]:
        """
        Alterna o status ativo/inativo de uma extensão
        """
        try:
            extension = db.query(Extension).filter(Extension.id == extension_id).first()
            
            if not extension:
                raise ValueError("Extensão não encontrada")
            
            extension.ativo = not extension.ativo
            extension.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(extension)
            
            # Atualizar configuração do Asterisk
            await self._generate_asterisk_config(extension)
            await self._reload_asterisk_config()
            
            logger.info(f"Extensão {extension.numero} {'ativada' if extension.ativo else 'desativada'}")
            
            return {
                'id': extension.id,
                'numero': extension.numero,
                'ativo': extension.ativo
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao alterar status da extensão {extension_id}: {str(e)}")
            raise
    
    async def test_extension(self, extension_id: int, db: Session) -> Dict[str, Any]:
        """
        Testa a conectividade de uma extensão
        """
        try:
            extension = db.query(Extension).filter(Extension.id == extension_id).first()
            
            if not extension:
                raise ValueError("Extensão não encontrada")
            
            if not extension.ativo:
                return {
                    'success': False,
                    'message': 'Extensão está inativa'
                }
            
            # Verificar status no Asterisk
            status = await self._check_extension_status(extension.numero)
            
            if status['registered']:
                return {
                    'success': True,
                    'message': 'Extensão online e funcionando',
                    'details': status
                }
            else:
                return {
                    'success': False,
                    'message': 'Extensão offline ou não registrada',
                    'details': status
                }
            
        except Exception as e:
            logger.error(f"Erro ao testar extensão {extension_id}: {str(e)}")
            return {
                'success': False,
                'message': f'Erro no teste: {str(e)}'
            }
    
    async def get_extension_stats(self, numero: str) -> Optional[Dict[str, Any]]:
        """
        Obtém estatísticas de uma extensão específica
        """
        try:
            # Verificar cache
            if (self._last_stats_update and 
                (datetime.utcnow() - self._last_stats_update).seconds < 30 and
                numero in self._stats_cache):
                return self._stats_cache[numero]
            
            # Obter status do Asterisk
            status = await self._check_extension_status(numero)
            
            stats = {
                'online': status.get('registered', False),
                'active_calls': status.get('active_calls', 0),
                'total_calls': status.get('total_calls', 0),
                'last_activity': status.get('last_activity'),
                'ip_address': status.get('ip_address'),
                'user_agent': status.get('user_agent')
            }
            
            # Atualizar cache
            self._stats_cache[numero] = stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas da extensão {numero}: {str(e)}")
            return None
    
    async def get_all_extension_stats(self, db: Session) -> Dict[int, Dict[str, Any]]:
        """
        Obtém estatísticas de todas as extensões
        """
        try:
            # Verificar cache
            if (self._last_stats_update and 
                (datetime.utcnow() - self._last_stats_update).seconds < 30):
                return self._stats_cache
            
            extensions = db.query(Extension).filter(Extension.ativo == True).all()
            stats = {}
            
            for extension in extensions:
                ext_stats = await self.get_extension_stats(extension.numero)
                if ext_stats:
                    stats[extension.id] = ext_stats
            
            self._last_stats_update = datetime.utcnow()
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas das extensões: {str(e)}")
            return {}
    
    def _validate_extension_data(self, data: Dict[str, Any]) -> None:
        """
        Valida os dados da extensão
        """
        if not data.get('numero'):
            raise ValueError("Número da extensão é obrigatório")
        
        if not data.get('nome'):
            raise ValueError("Nome da extensão é obrigatório")
        
        # Validar formato do número
        numero = str(data['numero'])
        if not re.match(r'^\d{3,6}$', numero):
            raise ValueError("Número da extensão deve ter entre 3 e 6 dígitos")
        
        # Validar configurações
        config = data.get('configuracoes', {})
        if config.get('max_chamadas_simultaneas', 1) < 1:
            raise ValueError("Máximo de chamadas simultâneas deve ser pelo menos 1")
        
        if config.get('timeout_chamada', 30) < 10:
            raise ValueError("Timeout de chamada deve ser pelo menos 10 segundos")
    
    async def _generate_asterisk_config(self, extension: Extension) -> None:
        """
        Gera configuração do Asterisk para a extensão
        """
        try:
            config = extension.configuracoes or {}
            
            # Template de configuração SIP
            sip_config = f"""
[{extension.numero}]
type={config.get('type', 'friend')}
host={config.get('host', 'dynamic')}
context={config.get('context', 'default')}
secret={extension.numero}123
nat={config.get('nat', 'yes')}
qualify={config.get('qualify', 'yes')}
canreinvite={config.get('canreinvite', 'no')}
dtmfmode={config.get('dtmf_mode', 'rfc2833')}
disallow={config.get('disallow', 'all')}
allow={config.get('allow', 'ulaw,alaw,gsm')}
call-limit={config.get('max_chamadas_simultaneas', 5)}
"""
            
            # Salvar configuração (implementar conforme necessário)
            # Aqui você salvaria a configuração no arquivo sip.conf ou banco
            
            logger.info(f"Configuração gerada para extensão {extension.numero}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar configuração para extensão {extension.numero}: {str(e)}")
            raise
    
    async def _remove_asterisk_config(self, numero: str) -> None:
        """
        Remove configuração do Asterisk para a extensão
        """
        try:
            # Implementar remoção da configuração
            logger.info(f"Configuração removida para extensão {numero}")
            
        except Exception as e:
            logger.error(f"Erro ao remover configuração da extensão {numero}: {str(e)}")
            raise
    
    async def _reload_asterisk_config(self) -> None:
        """
        Recarrega configuração do Asterisk
        """
        try:
            if self.ami.connected:
                await self.ami.send_command('sip reload')
                logger.info("Configuração do Asterisk recarregada")
            
        except Exception as e:
            logger.error(f"Erro ao recarregar configuração do Asterisk: {str(e)}")
    
    async def _check_extension_status(self, numero: str) -> Dict[str, Any]:
        """
        Verifica status da extensão no Asterisk
        """
        try:
            if not self.ami.connected:
                await self.ami.connect()
            
            # Comando para verificar status SIP
            response = await self.ami.send_command(f'sip show peer {numero}')
            
            status = {
                'registered': False,
                'active_calls': 0,
                'total_calls': 0,
                'last_activity': None,
                'ip_address': None,
                'user_agent': None
            }
            
            if response and 'Status' in response:
                # Parsear resposta do Asterisk
                lines = response.split('\n')
                for line in lines:
                    if 'Status' in line and 'OK' in line:
                        status['registered'] = True
                    elif 'Addr->IP' in line:
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            status['ip_address'] = ip_match.group(1)
                    elif 'Useragent' in line:
                        ua_match = re.search(r'Useragent\s*:\s*(.+)', line)
                        if ua_match:
                            status['user_agent'] = ua_match.group(1).strip()
            
            # Verificar chamadas ativas
            channels_response = await self.ami.send_command('core show channels')
            if channels_response:
                active_calls = channels_response.count(f'SIP/{numero}-')
                status['active_calls'] = active_calls
            
            return status
            
        except Exception as e:
            logger.error(f"Erro ao verificar status da extensão {numero}: {str(e)}")
            return {
                'registered': False,
                'active_calls': 0,
                'total_calls': 0,
                'last_activity': None,
                'ip_address': None,
                'user_agent': None
            }
    
    def is_extension_available(self, numero: str, horario_funcionamento: Dict[str, Any]) -> bool:
        """
        Verifica se a extensão está disponível no horário atual
        """
        try:
            now = datetime.now()
            weekday = now.weekday()  # 0 = segunda, 6 = domingo
            
            dias = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
            dia_atual = dias[weekday]
            
            config_dia = horario_funcionamento.get(dia_atual, {})
            
            if not config_dia.get('ativo', False):
                return False
            
            inicio_str = config_dia.get('inicio', '08:00')
            fim_str = config_dia.get('fim', '18:00')
            
            inicio = datetime.strptime(inicio_str, '%H:%M').time()
            fim = datetime.strptime(fim_str, '%H:%M').time()
            
            hora_atual = now.time()
            
            return inicio <= hora_atual <= fim
            
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade da extensão {numero}: {str(e)}")
            return True  # Em caso de erro, assumir disponível
    
    async def get_available_extensions(self, db: Session, campanha_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtém extensões disponíveis para discagem
        """
        try:
            query = db.query(Extension).filter(Extension.ativo == True)
            
            if campanha_id:
                query = query.filter(
                    or_(
                        Extension.campanha_id == campanha_id,
                        Extension.campanha_id.is_(None)
                    )
                )
            
            extensions = query.all()
            available = []
            
            for ext in extensions:
                # Verificar horário de funcionamento
                if not self.is_extension_available(ext.numero, ext.horario_funcionamento or {}):
                    continue
                
                # Verificar se está online
                stats = await self.get_extension_stats(ext.numero)
                if not stats or not stats.get('online', False):
                    continue
                
                # Verificar limite de chamadas
                max_calls = ext.configuracoes.get('max_chamadas_simultaneas', 5)
                active_calls = stats.get('active_calls', 0)
                
                if active_calls >= max_calls:
                    continue
                
                available.append({
                    'id': ext.id,
                    'numero': ext.numero,
                    'nome': ext.nome,
                    'active_calls': active_calls,
                    'max_calls': max_calls,
                    'available_slots': max_calls - active_calls
                })
            
            # Ordenar por menor número de chamadas ativas
            available.sort(key=lambda x: x['active_calls'])
            
            return available
            
        except Exception as e:
            logger.error(f"Erro ao obter extensões disponíveis: {str(e)}")
            return []

# Instância global do serviço
extension_service = ExtensionService()