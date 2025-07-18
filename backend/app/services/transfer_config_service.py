"""Serviço para configurações flexíveis de transferência."""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

logger = logging.getLogger(__name__)

class TransferConfigService:
    """Serviço para gerenciar configurações de transferência flexíveis."""
    
    def __init__(self, db: Session):
        self.db = db
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Garante que as tabelas de configuração de transferência existam."""
        try:
            # Criar tabela de configurações de transferência
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS transfer_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campanha_id INTEGER,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                numeros_transferencia TEXT NOT NULL, -- JSON array de números
                estrategia_selecao VARCHAR(50) DEFAULT 'round_robin', -- round_robin, random, priority
                horario_funcionamento TEXT, -- JSON com horários
                ativo BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            self.db.execute(text(create_table_sql))
            
            # Criar tabela de histórico de transferências
            create_history_sql = """
            CREATE TABLE IF NOT EXISTS transfer_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_id INTEGER,
                llamada_id INTEGER,
                numero_origem VARCHAR(20),
                numero_transferencia VARCHAR(20),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sucesso BOOLEAN DEFAULT FALSE,
                motivo_falha TEXT,
                duracao_transferencia INTEGER -- em segundos
            )
            """
            
            self.db.execute(text(create_history_sql))
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao criar tabelas de transferência: {e}")
            self.db.rollback()
    
    def criar_configuracao_transferencia(
        self, 
        campanha_id: Optional[int],
        nome: str,
        numeros_transferencia: List[str],
        estrategia_selecao: str = "round_robin",
        descricao: str = None,
        horario_funcionamento: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Cria uma nova configuração de transferência."""
        try:
            import json
            
            # Validar números de transferência
            if not numeros_transferencia or len(numeros_transferencia) == 0:
                raise ValueError("Pelo menos um número de transferência deve ser fornecido")
            
            # Validar estratégia
            estrategias_validas = ["round_robin", "random", "priority"]
            if estrategia_selecao not in estrategias_validas:
                raise ValueError(f"Estratégia deve ser uma de: {estrategias_validas}")
            
            # Horário padrão (24/7)
            if not horario_funcionamento:
                horario_funcionamento = {
                    "segunda": {"inicio": "00:00", "fim": "23:59"},
                    "terca": {"inicio": "00:00", "fim": "23:59"},
                    "quarta": {"inicio": "00:00", "fim": "23:59"},
                    "quinta": {"inicio": "00:00", "fim": "23:59"},
                    "sexta": {"inicio": "00:00", "fim": "23:59"},
                    "sabado": {"inicio": "00:00", "fim": "23:59"},
                    "domingo": {"inicio": "00:00", "fim": "23:59"}
                }
            
            insert_sql = """
            INSERT INTO transfer_configurations 
            (campanha_id, nome, descricao, numeros_transferencia, estrategia_selecao, horario_funcionamento)
            VALUES (:campanha_id, :nome, :descricao, :numeros_transferencia, :estrategia_selecao, :horario_funcionamento)
            """
            
            result = self.db.execute(text(insert_sql), {
                "campanha_id": campanha_id,
                "nome": nome,
                "descricao": descricao,
                "numeros_transferencia": json.dumps(numeros_transferencia),
                "estrategia_selecao": estrategia_selecao,
                "horario_funcionamento": json.dumps(horario_funcionamento)
            })
            
            self.db.commit()
            config_id = result.lastrowid
            
            logger.info(f"✅ Configuração de transferência criada: {config_id}")
            
            return {
                "success": True,
                "config_id": config_id,
                "message": f"Configuração '{nome}' criada com sucesso",
                "numeros_configurados": len(numeros_transferencia)
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar configuração de transferência: {e}")
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def obter_numero_transferencia(
        self, 
        campanha_id: Optional[int] = None,
        config_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obtém o próximo número de transferência baseado na estratégia configurada."""
        try:
            import json
            
            # Buscar configuração
            if config_id:
                query = "SELECT * FROM transfer_configurations WHERE id = :config_id AND ativo = TRUE"
                params = {"config_id": config_id}
            elif campanha_id:
                query = "SELECT * FROM transfer_configurations WHERE campanha_id = :campanha_id AND ativo = TRUE LIMIT 1"
                params = {"campanha_id": campanha_id}
            else:
                query = "SELECT * FROM transfer_configurations WHERE campanha_id IS NULL AND ativo = TRUE LIMIT 1"
                params = {}
            
            result = self.db.execute(text(query), params).fetchone()
            
            if not result:
                # Retornar configuração padrão
                return {
                    "numero": "100",  # Extensão padrão
                    "estrategia": "default",
                    "config_id": None
                }
            
            config = dict(result._mapping)
            numeros = json.loads(config["numeros_transferencia"])
            estrategia = config["estrategia_selecao"]
            
            # Verificar horário de funcionamento
            if not self._is_horario_funcionamento(config["horario_funcionamento"]):
                return {
                    "numero": numeros[0] if numeros else "100",
                    "estrategia": "fora_horario",
                    "config_id": config["id"]
                }
            
            # Selecionar número baseado na estratégia
            if estrategia == "random":
                import random
                numero_selecionado = random.choice(numeros)
            elif estrategia == "priority":
                numero_selecionado = numeros[0]  # Primeiro da lista tem prioridade
            else:  # round_robin
                numero_selecionado = self._get_round_robin_number(config["id"], numeros)
            
            return {
                "numero": numero_selecionado,
                "estrategia": estrategia,
                "config_id": config["id"],
                "total_numeros": len(numeros)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter número de transferência: {e}")
            return {
                "numero": "100",  # Fallback
                "estrategia": "error",
                "config_id": None,
                "error": str(e)
            }
    
    def _is_horario_funcionamento(self, horario_json: str) -> bool:
        """Verifica se está dentro do horário de funcionamento."""
        try:
            import json
            from datetime import datetime, time
            
            horarios = json.loads(horario_json)
            agora = datetime.now()
            dia_semana = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"][agora.weekday()]
            
            if dia_semana not in horarios:
                return True  # Se não configurado, assume 24/7
            
            horario_dia = horarios[dia_semana]
            hora_atual = agora.time()
            
            inicio = time.fromisoformat(horario_dia["inicio"])
            fim = time.fromisoformat(horario_dia["fim"])
            
            return inicio <= hora_atual <= fim
            
        except Exception as e:
            logger.error(f"Erro ao verificar horário: {e}")
            return True  # Em caso de erro, assume que está no horário
    
    def _get_round_robin_number(self, config_id: int, numeros: List[str]) -> str:
        """Implementa round-robin para seleção de números."""
        try:
            # Buscar último número usado
            query = """
            SELECT numero_transferencia 
            FROM transfer_history 
            WHERE config_id = :config_id 
            ORDER BY timestamp DESC 
            LIMIT 1
            """
            
            result = self.db.execute(text(query), {"config_id": config_id}).fetchone()
            
            if not result:
                return numeros[0]  # Primeiro uso
            
            ultimo_numero = result[0]
            
            try:
                indice_atual = numeros.index(ultimo_numero)
                proximo_indice = (indice_atual + 1) % len(numeros)
                return numeros[proximo_indice]
            except ValueError:
                return numeros[0]  # Se número não encontrado, volta ao primeiro
            
        except Exception as e:
            logger.error(f"Erro no round-robin: {e}")
            return numeros[0] if numeros else "100"
    
    def registrar_transferencia(
        self,
        config_id: Optional[int],
        llamada_id: int,
        numero_origem: str,
        numero_transferencia: str,
        sucesso: bool,
        motivo_falha: str = None,
        duracao_transferencia: int = None
    ) -> bool:
        """Registra uma transferência no histórico."""
        try:
            insert_sql = """
            INSERT INTO transfer_history 
            (config_id, llamada_id, numero_origem, numero_transferencia, sucesso, motivo_falha, duracao_transferencia)
            VALUES (:config_id, :llamada_id, :numero_origem, :numero_transferencia, :sucesso, :motivo_falha, :duracao_transferencia)
            """
            
            self.db.execute(text(insert_sql), {
                "config_id": config_id,
                "llamada_id": llamada_id,
                "numero_origem": numero_origem,
                "numero_transferencia": numero_transferencia,
                "sucesso": sucesso,
                "motivo_falha": motivo_falha,
                "duracao_transferencia": duracao_transferencia
            })
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar transferência: {e}")
            self.db.rollback()
            return False
    
    def listar_configuracoes(self, campanha_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lista todas as configurações de transferência."""
        try:
            import json
            
            if campanha_id:
                query = "SELECT * FROM transfer_configurations WHERE campanha_id = :campanha_id ORDER BY nome"
                params = {"campanha_id": campanha_id}
            else:
                query = "SELECT * FROM transfer_configurations ORDER BY nome"
                params = {}
            
            results = self.db.execute(text(query), params).fetchall()
            
            configuracoes = []
            for row in results:
                config = dict(row._mapping)
                config["numeros_transferencia"] = json.loads(config["numeros_transferencia"])
                config["horario_funcionamento"] = json.loads(config["horario_funcionamento"])
                configuracoes.append(config)
            
            return configuracoes
            
        except Exception as e:
            logger.error(f"Erro ao listar configurações: {e}")
            return []
    
    def obter_estatisticas_transferencia(self, config_id: int, dias: int = 7) -> Dict[str, Any]:
        """Obtém estatísticas de transferência para uma configuração."""
        try:
            query = """
            SELECT 
                COUNT(*) as total_transferencias,
                SUM(CASE WHEN sucesso = TRUE THEN 1 ELSE 0 END) as transferencias_sucesso,
                AVG(duracao_transferencia) as duracao_media,
                numero_transferencia,
                COUNT(*) as uso_por_numero
            FROM transfer_history 
            WHERE config_id = :config_id 
            AND timestamp >= datetime('now', '-{} days')
            GROUP BY numero_transferencia
            """.format(dias)
            
            results = self.db.execute(text(query), {"config_id": config_id}).fetchall()
            
            estatisticas = {
                "total_transferencias": 0,
                "transferencias_sucesso": 0,
                "taxa_sucesso": 0.0,
                "duracao_media": 0.0,
                "uso_por_numero": {}
            }
            
            for row in results:
                row_dict = dict(row._mapping)
                estatisticas["total_transferencias"] += row_dict["total_transferencias"]
                estatisticas["transferencias_sucesso"] += row_dict["transferencias_sucesso"]
                estatisticas["uso_por_numero"][row_dict["numero_transferencia"]] = row_dict["uso_por_numero"]
                
                if row_dict["duracao_media"]:
                    estatisticas["duracao_media"] = row_dict["duracao_media"]
            
            if estatisticas["total_transferencias"] > 0:
                estatisticas["taxa_sucesso"] = (estatisticas["transferencias_sucesso"] / estatisticas["total_transferencias"]) * 100
            
            return estatisticas
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}