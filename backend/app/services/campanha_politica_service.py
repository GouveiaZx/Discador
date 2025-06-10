#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço principal para Campanhas Políticas
Garante conformidade com legislação eleitoral
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta, time
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.campanha_politica import (
    CampanhaPolitica, ConfiguracaoEleitoral, CalendarioEleitoral,
    LogEleitoralImutavel, OptOutEleitoral, StatusCampanhaPolitica,
    TipoLogEleitoral
)
from app.schemas.campanha_politica import (
    CampanhaPoliticaCreate, CampanhaPoliticaResponse,
    ValidacaoHorarioRequest, ValidacaoHorarioResponse,
    LogEleitoralCreate
)
from app.utils.logger import logger

class CampanhaPoliticaService:
    """Serviço para gestão de campanhas políticas com compliance eleitoral"""
    
    def __init__(self, db: Session):
        self.db = db
        self.versao_sistema = "1.0.0"
    
    async def validar_horario_legal(
        self, 
        campanha_id: int, 
        timestamp_ligacao: datetime
    ) -> ValidacaoHorarioResponse:
        """Valida se uma ligação pode ser feita no horário especificado"""
        try:
            campanha = self.db.query(CampanhaPolitica).filter(
                CampanhaPolitica.id == campanha_id
            ).first()
            
            if not campanha:
                raise ValueError(f"Campanha {campanha_id} não encontrada")
            
            config = campanha.configuracao_eleitoral
            
            # Verificar dia da semana
            dia_semana = timestamp_ligacao.weekday()
            if dia_semana not in config.dias_semana_permitidos:
                return ValidacaoHorarioResponse(
                    dentro_horario_legal=False,
                    motivo=f"Ligações não permitidas neste dia da semana",
                    horario_inicio_permitido=config.horario_inicio_permitido,
                    horario_fim_permitido=config.horario_fim_permitido
                )
            
            # Verificar horário do dia
            horario_ligacao = timestamp_ligacao.time()
            horario_inicio = time.fromisoformat(config.horario_inicio_permitido)
            horario_fim = time.fromisoformat(config.horario_fim_permitido)
            
            if not (horario_inicio <= horario_ligacao <= horario_fim):
                return ValidacaoHorarioResponse(
                    dentro_horario_legal=False,
                    motivo=f"Fora do horário permitido ({config.horario_inicio_permitido}-{config.horario_fim_permitido})",
                    horario_inicio_permitido=config.horario_inicio_permitido,
                    horario_fim_permitido=config.horario_fim_permitido
                )
            
            return ValidacaoHorarioResponse(
                dentro_horario_legal=True,
                motivo="Horário dentro do período legal",
                horario_inicio_permitido=config.horario_inicio_permitido,
                horario_fim_permitido=config.horario_fim_permitido
            )
            
        except Exception as e:
            logger.error(f"Erro ao validar horário legal: {e}")
            raise
    
    async def registrar_log_eleitoral(
        self, 
        dados_log: LogEleitoralCreate,
        endereco_ip: str
    ) -> LogEleitoralImutavel:
        """Registra log eleitoral imutável"""
        try:
            # Obter hash do último log
            ultimo_log = self.db.query(LogEleitoralImutavel).order_by(
                LogEleitoralImutavel.id.desc()
            ).first()
            
            hash_anterior = ultimo_log.hash_proprio if ultimo_log else None
            
            # Criar log
            log_eleitoral = LogEleitoralImutavel(
                uuid_log=uuid.uuid4(),
                hash_anterior=hash_anterior,
                campanha_politica_id=dados_log.campanha_politica_id,
                campanha_base_id=1,  # TODO: Buscar da campanha
                numero_destino=dados_log.numero_destino,
                numero_cli_usado=dados_log.numero_cli_usado,
                timestamp_utc=datetime.utcnow(),
                timestamp_local=dados_log.timestamp_local,
                timezone_local=dados_log.timezone_local,
                tipo_log=dados_log.tipo_log,
                descricao_evento=dados_log.descricao_evento,
                dentro_horario_legal=dados_log.dentro_horario_legal,
                endereco_ip_servidor=endereco_ip,
                versao_sistema=self.versao_sistema
            )
            
            # Calcular hash próprio
            log_eleitoral.hash_proprio = self._calcular_hash_log(log_eleitoral)
            
            self.db.add(log_eleitoral)
            self.db.commit()
            self.db.refresh(log_eleitoral)
            
            return log_eleitoral
            
        except Exception as e:
            logger.error(f"Erro ao registrar log eleitoral: {e}")
            self.db.rollback()
            raise
    
    def _calcular_hash_log(self, log: LogEleitoralImutavel) -> str:
        """Calcula hash SHA-256 do log"""
        dados_hash = {
            "uuid_log": str(log.uuid_log),
            "hash_anterior": log.hash_anterior,
            "campanha_politica_id": log.campanha_politica_id,
            "numero_destino": log.numero_destino,
            "timestamp_utc": log.timestamp_utc.isoformat(),
            "tipo_log": log.tipo_log,
            "descricao_evento": log.descricao_evento
        }
        
        dados_json = json.dumps(dados_hash, sort_keys=True)
        return hashlib.sha256(dados_json.encode('utf-8')).hexdigest() 