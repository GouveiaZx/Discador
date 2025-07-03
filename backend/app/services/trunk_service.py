"""
Serviço para gerenciamento avançado de trunks SIP.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_
from fastapi import HTTPException
from datetime import datetime, timedelta
import random
import re

from app.models.trunk import Trunk, TrunkEstatistica, TrunkLog
from app.schemas.trunk import (
    TrunkCreate, TrunkUpdate, TrunkBalanceamento,
    NumeroFormatado, TrunkTesteConexao
)
from app.utils.logger import logger


class TrunkService:
    """Serviço para gerenciamento de trunks SIP."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def criar_trunk(
        self, 
        trunk_data: TrunkCreate,
        usuario_id: Optional[int] = None
    ) -> Trunk:
        """Cria um novo trunk."""
        
        # Verificar se nome já existe
        existente = self.db.query(Trunk).filter(
            Trunk.nome == trunk_data.nome
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe um trunk com o nome '{trunk_data.nome}'"
            )
        
        try:
            trunk = Trunk(
                **trunk_data.dict(),
                usuario_criador_id=usuario_id
            )
            
            self.db.add(trunk)
            self.db.commit()
            self.db.refresh(trunk)
            
            # Log da criação
            self._criar_log(
                trunk.id, 
                'criacao', 
                f'Trunk {trunk.nome} criado com sucesso',
                'info'
            )
            
            logger.info(f"Trunk criado: {trunk.nome} (ID: {trunk.id})")
            return trunk
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Erro de integridade ao criar trunk: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Erro de integridade nos dados do trunk"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro inesperado ao criar trunk: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao criar trunk"
            )
    
    def listar_trunks(
        self, 
        ativos_apenas: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Trunk]:
        """Lista trunks."""
        
        query = self.db.query(Trunk)
        
        if ativos_apenas:
            query = query.filter(Trunk.ativo == True)
        
        return query.order_by(
            Trunk.prioridade.asc(),
            Trunk.nome.asc()
        ).offset(skip).limit(limit).all()
    
    def obter_trunk(self, trunk_id: int) -> Trunk:
        """Obtém um trunk por ID."""
        
        trunk = self.db.query(Trunk).filter(Trunk.id == trunk_id).first()
        
        if not trunk:
            raise HTTPException(
                status_code=404,
                detail=f"Trunk com ID {trunk_id} não encontrado"
            )
        
        return trunk
    
    def atualizar_trunk(
        self,
        trunk_id: int,
        trunk_data: TrunkUpdate,
        usuario_id: Optional[int] = None
    ) -> Trunk:
        """Atualiza um trunk existente."""
        
        trunk = self.obter_trunk(trunk_id)
        
        try:
            # Salvar dados antigos para log
            dados_antigos = trunk.to_dict()
            
            # Atualizar apenas campos fornecidos
            update_data = trunk_data.dict(exclude_unset=True)
            
            for campo, valor in update_data.items():
                setattr(trunk, campo, valor)
            
            self.db.commit()
            self.db.refresh(trunk)
            
            # Log da atualização
            self._criar_log(
                trunk.id,
                'atualizacao',
                f'Trunk {trunk.nome} atualizado',
                'info',
                dados_extras={'campos_alterados': list(update_data.keys())}
            )
            
            logger.info(f"Trunk atualizado: {trunk.nome} (ID: {trunk_id})")
            return trunk
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar trunk {trunk_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao atualizar trunk"
            )
    
    def excluir_trunk(self, trunk_id: int) -> bool:
        """Exclui um trunk (soft delete)."""
        
        trunk = self.obter_trunk(trunk_id)
        
        # Verificar se está sendo usado
        if trunk.canais_em_uso > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir: trunk tem {trunk.canais_em_uso} canais em uso"
            )
        
        try:
            trunk.ativo = False
            self.db.commit()
            
            # Log da exclusão
            self._criar_log(
                trunk.id,
                'exclusao',
                f'Trunk {trunk.nome} desativado',
                'info'
            )
            
            logger.info(f"Trunk desativado: {trunk.nome} (ID: {trunk_id})")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao desativar trunk {trunk_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao desativar trunk"
            )
    
    def testar_conexao(self, trunk_id: int) -> TrunkTesteConexao:
        """Testa a conexão com um trunk."""
        
        trunk = self.obter_trunk(trunk_id)
        
        inicio = datetime.now()
        
        try:
            # Aqui você implementaria o teste real de conexão SIP
            # Por agora, simulando o teste
            
            import time
            time.sleep(0.1)  # Simular latência
            
            tempo_resposta = (datetime.now() - inicio).total_seconds()
            
            # Simular resultado baseado no status do trunk
            if trunk.ativo and trunk.host:
                resultado = 'sucesso'
                codigo_resposta = '200'
                mensagem = 'Conexão estabelecida com sucesso'
                
                # Atualizar status do trunk
                trunk.status_conexao = 'online'
                trunk.ultima_verificacao = datetime.now()
                
            else:
                resultado = 'falha'
                codigo_resposta = '503'
                mensagem = 'Falha na conexão'
                trunk.status_conexao = 'offline'
                trunk.ultima_verificacao = datetime.now()
            
            self.db.commit()
            
            # Log do teste
            self._criar_log(
                trunk.id,
                'teste_conexao',
                f'Teste de conexão: {resultado}',
                'info' if resultado == 'sucesso' else 'warning',
                dados_extras={'tempo_resposta': tempo_resposta}
            )
            
            return TrunkTesteConexao(
                trunk_id=trunk_id,
                resultado=resultado,
                tempo_resposta=tempo_resposta,
                codigo_resposta=codigo_resposta,
                mensagem=mensagem,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro ao testar conexão do trunk {trunk_id}: {str(e)}")
            return TrunkTesteConexao(
                trunk_id=trunk_id,
                resultado='erro',
                codigo_resposta='500',
                mensagem=f'Erro interno: {str(e)}',
                timestamp=datetime.now()
            )
    
    def formatar_numero(
        self, 
        numero: str, 
        trunk_id: Optional[int] = None
    ) -> NumeroFormatado:
        """Formata um número usando as regras de um trunk específico."""
        
        if trunk_id:
            trunk = self.obter_trunk(trunk_id)
        else:
            # Usar trunk padrão (menor prioridade ativo)
            trunk = self.db.query(Trunk).filter(
                Trunk.ativo == True
            ).order_by(Trunk.prioridade.asc()).first()
            
            if not trunk:
                raise HTTPException(
                    status_code=404,
                    detail="Nenhum trunk ativo encontrado"
                )
        
        try:
            numero_formatado = trunk.formatar_numero(numero)
            caller_id = trunk.obter_caller_id()
            
            # Validar número formatado
            valido = self._validar_numero_formatado(numero_formatado, trunk)
            motivo_invalido = None if valido else "Formato inválido"
            
            return NumeroFormatado(
                numero_original=numero,
                numero_formatado=numero_formatado,
                trunk_usado=trunk.nome,
                caller_id=caller_id,
                valido=valido,
                motivo_invalido=motivo_invalido
            )
            
        except Exception as e:
            logger.error(f"Erro ao formatar número {numero}: {str(e)}")
            return NumeroFormatado(
                numero_original=numero,
                numero_formatado=numero,
                trunk_usado=trunk.nome if trunk_id else 'desconhecido',
                caller_id={},
                valido=False,
                motivo_invalido=str(e)
            )
    
    def selecionar_trunk_para_chamada(
        self,
        algoritmo: str = 'priority',
        excluir_trunk_ids: List[int] = None
    ) -> Optional[Trunk]:
        """Seleciona o melhor trunk para uma chamada."""
        
        if excluir_trunk_ids is None:
            excluir_trunk_ids = []
        
        # Filtrar trunks disponíveis
        query = self.db.query(Trunk).filter(
            Trunk.ativo == True,
            ~Trunk.id.in_(excluir_trunk_ids)
        )
        
        # Verificar capacidade
        trunks_disponiveis = [
            trunk for trunk in query.all()
            if trunk.pode_aceitar_chamada()
        ]
        
        if not trunks_disponiveis:
            return None
        
        # Aplicar algoritmo de seleção
        if algoritmo == 'priority':
            return min(trunks_disponiveis, key=lambda t: t.prioridade)
        
        elif algoritmo == 'least_used':
            return min(trunks_disponiveis, key=lambda t: t.canais_em_uso)
        
        elif algoritmo == 'weighted':
            # Seleção baseada em peso
            total_peso = sum(t.peso_balanceamento for t in trunks_disponiveis)
            if total_peso == 0:
                return random.choice(trunks_disponiveis)
            
            escolha = random.randint(1, total_peso)
            peso_acumulado = 0
            
            for trunk in trunks_disponiveis:
                peso_acumulado += trunk.peso_balanceamento
                if escolha <= peso_acumulado:
                    return trunk
        
        elif algoritmo == 'round_robin':
            # Implementação simples de round robin
            # Em produção, você manteria um contador persistente
            return random.choice(trunks_disponiveis)
        
        # Fallback para prioridade
        return min(trunks_disponiveis, key=lambda t: t.prioridade)
    
    def incrementar_uso_canal(self, trunk_id: int) -> bool:
        """Incrementa o uso de canal de um trunk."""
        
        trunk = self.obter_trunk(trunk_id)
        
        if not trunk.pode_aceitar_chamada():
            return False
        
        try:
            trunk.canais_em_uso += 1
            self.db.commit()
            
            logger.debug(f"Canal incrementado para trunk {trunk.nome}: {trunk.canais_em_uso}/{trunk.max_canais_simultaneos}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao incrementar canal do trunk {trunk_id}: {str(e)}")
            return False
    
    def decrementar_uso_canal(self, trunk_id: int) -> bool:
        """Decrementa o uso de canal de um trunk."""
        
        trunk = self.obter_trunk(trunk_id)
        
        try:
            if trunk.canais_em_uso > 0:
                trunk.canais_em_uso -= 1
                self.db.commit()
                
                logger.debug(f"Canal decrementado para trunk {trunk.nome}: {trunk.canais_em_uso}/{trunk.max_canais_simultaneos}")
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao decrementar canal do trunk {trunk_id}: {str(e)}")
            return False
    
    def obter_estatisticas(
        self,
        trunk_id: int,
        periodo_dias: int = 30
    ) -> Dict[str, Any]:
        """Obtém estatísticas de um trunk."""
        
        trunk = self.obter_trunk(trunk_id)
        data_inicio = datetime.now() - timedelta(days=periodo_dias)
        
        # Buscar estatísticas do período
        estatisticas = self.db.query(TrunkEstatistica).filter(
            TrunkEstatistica.trunk_id == trunk_id,
            TrunkEstatistica.data_inicio >= data_inicio
        ).all()
        
        if not estatisticas:
            return {
                'trunk_id': trunk_id,
                'nome': trunk.nome,
                'periodo_dias': periodo_dias,
                'total_chamadas': 0,
                'taxa_sucesso': 0.0,
                'custo_total': 0.0
            }
        
        # Agregar estatísticas
        total_chamadas = sum(e.total_chamadas for e in estatisticas)
        chamadas_completadas = sum(e.chamadas_completadas for e in estatisticas)
        custo_total = sum(e.custo_total for e in estatisticas)
        
        taxa_sucesso = (chamadas_completadas / total_chamadas * 100) if total_chamadas > 0 else 0.0
        
        return {
            'trunk_id': trunk_id,
            'nome': trunk.nome,
            'periodo_dias': periodo_dias,
            'total_chamadas': total_chamadas,
            'chamadas_completadas': chamadas_completadas,
            'taxa_sucesso': round(taxa_sucesso, 2),
            'custo_total': float(custo_total),
            'status_atual': trunk.status_conexao,
            'canais_em_uso': trunk.canais_em_uso,
            'max_canais': trunk.max_canais_simultaneos
        }
    
    def _validar_numero_formatado(self, numero: str, trunk: Trunk) -> bool:
        """Valida se um número formatado está correto."""
        
        # Validações básicas
        if not numero or not numero.strip():
            return False
        
        # Para números dos EUA (código +1)
        if trunk.codigo_pais == '+1':
            # Remover caracteres não numéricos
            apenas_numeros = re.sub(r'\D', '', numero)
            
            # Verificar formato 10 ou 11 dígitos
            if len(apenas_numeros) == 10:
                # Formato: NXXNXXXXXX (N = 2-9, X = 0-9)
                return re.match(r'^[2-9]\d{2}[2-9]\d{6}$', apenas_numeros) is not None
            elif len(apenas_numeros) == 11 and apenas_numeros.startswith('1'):
                # Formato: 1NXXNXXXXXX
                return re.match(r'^1[2-9]\d{2}[2-9]\d{6}$', apenas_numeros) is not None
        
        # Para outros países, validação básica
        apenas_numeros = re.sub(r'\D', '', numero)
        return len(apenas_numeros) >= 7  # Mínimo 7 dígitos
    
    def _criar_log(
        self,
        trunk_id: int,
        tipo_evento: str,
        descricao: str,
        nivel: str = 'info',
        dados_extras: Dict[str, Any] = None
    ):
        """Cria um log de evento do trunk."""
        
        try:
            log = TrunkLog(
                trunk_id=trunk_id,
                tipo_evento=tipo_evento,
                descricao=descricao,
                nivel=nivel,
                dados_extras=dados_extras or {}
            )
            
            self.db.add(log)
            # Não fazer commit aqui, será feito junto com a operação principal
            
        except Exception as e:
            logger.error(f"Erro ao criar log do trunk: {str(e)}")
            # Não falhar a operação principal por erro no log 