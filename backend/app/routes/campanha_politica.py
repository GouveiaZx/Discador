#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas API para o sistema de Campanhas Políticas
Endpoints para conformidade com legislação eleitoral
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import tempfile
import json

from app.database import get_db
from app.models.campanha_politica import (
    CampanhaPolitica, ConfiguracaoEleitoral, CalendarioEleitoral,
    LogEleitoralImutavel, OptOutEleitoral, TipoLogEleitoral
)
from app.schemas.campanha_politica import (
    ConfiguracaoEleitoralCreate, ConfiguracaoEleitoralResponse,
    CalendarioEleitoralCreate, CalendarioEleitoralResponse,
    CampanhaPoliticaCreate, CampanhaPoliticaResponse,
    LogEleitoralCreate, LogEleitoralResponse,
    ValidacaoHorarioRequest, ValidacaoHorarioResponse
)
from app.services.campanha_politica_service import CampanhaPoliticaService
from app.utils.logger import logger

router = APIRouter(tags=["Campanhas Políticas"])

# ================================================
# CONFIGURAÇÃO ELEITORAL
# ================================================

@router.post("/configuracao-eleitoral", response_model=ConfiguracaoEleitoralResponse)
async def criar_configuracao_eleitoral(
    configuracao: ConfiguracaoEleitoralCreate,
    db: Session = Depends(get_db)
):
    """Cria nova configuração eleitoral para um país"""
    try:
        # Verificar se já existe configuração para o país
        config_existente = db.query(ConfiguracaoEleitoral).filter(
            ConfiguracaoEleitoral.pais_codigo == configuracao.pais_codigo
        ).first()
        
        if config_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Configuração eleitoral já existe para o país {configuracao.pais_codigo}"
            )
        
        # Criar configuração
        nova_config = ConfiguracaoEleitoral(**configuracao.dict())
        db.add(nova_config)
        db.commit()
        db.refresh(nova_config)
        
        logger.info(f"Configuração eleitoral criada para país: {configuracao.pais_codigo}")
        
        return nova_config
        
    except Exception as e:
        logger.error(f"Erro ao criar configuração eleitoral: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/configuracao-eleitoral", response_model=List[ConfiguracaoEleitoralResponse])
async def listar_configuracoes_eleitorais(
    pais_codigo: Optional[str] = None,
    activo: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Lista configurações eleitorais"""
    try:
        query = db.query(ConfiguracaoEleitoral)
        
        if pais_codigo:
            query = query.filter(ConfiguracaoEleitoral.pais_codigo == pais_codigo)
        
        if activo is not None:
            query = query.filter(ConfiguracaoEleitoral.activo == activo)
        
        configuracoes = query.all()
        return configuracoes
        
    except Exception as e:
        logger.error(f"Erro ao listar configurações eleitorais: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ================================================
# CALENDÁRIO ELEITORAL
# ================================================

@router.post("/calendario-eleitoral", response_model=CalendarioEleitoralResponse)
async def criar_calendario_eleitoral(
    calendario: CalendarioEleitoralCreate,
    db: Session = Depends(get_db)
):
    """Cria novo calendário eleitoral"""
    try:
        novo_calendario = CalendarioEleitoral(**calendario.dict())
        db.add(novo_calendario)
        db.commit()
        db.refresh(novo_calendario)
        
        logger.info(f"Calendário eleitoral criado: {calendario.nome_eleicao}")
        
        return novo_calendario
        
    except Exception as e:
        logger.error(f"Erro ao criar calendário eleitoral: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/calendario-eleitoral", response_model=List[CalendarioEleitoralResponse])
async def listar_calendarios_eleitorais(
    pais_codigo: Optional[str] = None,
    activo: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Lista calendários eleitorais"""
    try:
        query = db.query(CalendarioEleitoral)
        
        if pais_codigo:
            query = query.filter(CalendarioEleitoral.pais_codigo == pais_codigo)
        
        if activo is not None:
            query = query.filter(CalendarioEleitoral.activo == activo)
        
        calendarios = query.order_by(CalendarioEleitoral.data_eleicao.desc()).all()
        return calendarios
        
    except Exception as e:
        logger.error(f"Erro ao listar calendários eleitorais: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ================================================
# CAMPANHAS POLÍTICAS
# ================================================

@router.post("/campanhas", response_model=CampanhaPoliticaResponse)
async def criar_campanha_politica(
    campanha: CampanhaPoliticaCreate,
    db: Session = Depends(get_db)
):
    """Cria nova campanha política"""
    try:
        # Verificar se campanha base existe
        from app.models.campana import Campana
        campanha_base = db.query(Campana).filter(
            Campana.id == campanha.campanha_base_id
        ).first()
        
        if not campanha_base:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha base não encontrada"
            )
        
        # Verificar se já existe campanha política para esta campanha base
        campanha_existente = db.query(CampanhaPolitica).filter(
            CampanhaPolitica.campanha_base_id == campanha.campanha_base_id
        ).first()
        
        if campanha_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe campanha política para esta campanha base"
            )
        
        # Calcular hash de configuração
        service = CampanhaPoliticaService(db)
        hash_config = "temp_hash"  # TODO: Implementar cálculo real
        
        # Criar campanha política
        nova_campanha = CampanhaPolitica(
            **campanha.dict(),
            hash_configuracao=hash_config
        )
        
        db.add(nova_campanha)
        db.commit()
        db.refresh(nova_campanha)
        
        logger.info(f"Campanha política criada: {campanha.candidato_nome}")
        
        return nova_campanha
        
    except Exception as e:
        logger.error(f"Erro ao criar campanha política: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/campanhas", response_model=List[CampanhaPoliticaResponse])
async def listar_campanhas_politicas(
    activo: Optional[bool] = True,
    partido_sigla: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista campanhas políticas"""
    try:
        query = db.query(CampanhaPolitica)
        
        if activo is not None:
            query = query.filter(CampanhaPolitica.activo == activo)
        
        if partido_sigla:
            query = query.filter(CampanhaPolitica.partido_sigla == partido_sigla.upper())
        
        campanhas = query.order_by(CampanhaPolitica.fecha_creacion.desc()).all()
        return campanhas
        
    except Exception as e:
        logger.error(f"Erro ao listar campanhas políticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ================================================
# VALIDAÇÕES DE CONFORMIDADE
# ================================================

@router.post("/validar-horario", response_model=ValidacaoHorarioResponse)
async def validar_horario_legal(
    validacao: ValidacaoHorarioRequest,
    db: Session = Depends(get_db)
):
    """Valida se uma ligação pode ser feita no horário especificado"""
    try:
        service = CampanhaPoliticaService(db)
        resultado = await service.validar_horario_legal(
            validacao.campanha_politica_id,
            validacao.timestamp_ligacao
        )
        
        return resultado
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao validar horário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/validar-periodo/{campanha_id}")
async def validar_periodo_eleitoral(
    campanha_id: int,
    data_verificacao: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Valida se a campanha está dentro do período eleitoral legal"""
    try:
        # Buscar campanha
        campanha = db.query(CampanhaPolitica).filter(
            CampanhaPolitica.id == campanha_id
        ).first()
        
        if not campanha:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha não encontrada"
            )
        
        if not data_verificacao:
            data_verificacao = datetime.utcnow()
        
        calendario = campanha.calendario_eleitoral
        
        # Verificar período
        dentro_periodo = (
            calendario.data_inicio_campanha <= data_verificacao <= calendario.data_fim_campanha
        )
        
        # Verificar silêncio eleitoral
        em_silencio = False
        if calendario.data_inicio_silencio and calendario.data_fim_silencio:
            em_silencio = (
                calendario.data_inicio_silencio <= data_verificacao <= calendario.data_fim_silencio
            )
        
        return {
            "dentro_periodo_legal": dentro_periodo and not em_silencio,
            "periodo_campanha": dentro_periodo,
            "em_silencio_eleitoral": em_silencio,
            "data_inicio_campanha": calendario.data_inicio_campanha,
            "data_fim_campanha": calendario.data_fim_campanha,
            "data_eleicao": calendario.data_eleicao,
            "dias_restantes": (calendario.data_fim_campanha - data_verificacao).days if dentro_periodo else None
        }
        
    except Exception as e:
        logger.error(f"Erro ao validar período eleitoral: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/pode-ligar/{campanha_id}")
async def verificar_pode_ligar(
    campanha_id: int,
    numero_destino: str,
    timestamp_ligacao: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Verificação completa se uma ligação pode ser realizada"""
    try:
        if not timestamp_ligacao:
            timestamp_ligacao = datetime.utcnow()
        
        service = CampanhaPoliticaService(db)
        
        # Validar horário
        validacao_horario = await service.validar_horario_legal(campanha_id, timestamp_ligacao)
        
        # TODO: Implementar outras validações (opt-out, período, etc.)
        
        motivos_bloqueio = []
        if not validacao_horario.dentro_horario_legal:
            motivos_bloqueio.append(validacao_horario.motivo)
        
        return {
            "pode_ligar": len(motivos_bloqueio) == 0,
            "motivos_bloqueio": motivos_bloqueio,
            "validacao_horario": validacao_horario
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar se pode ligar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ================================================
# LOGS ELEITORAIS IMUTÁVEIS
# ================================================

@router.post("/logs-eleitorais", response_model=LogEleitoralResponse)
async def registrar_log_eleitoral(
    log_data: LogEleitoralCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Registra log eleitoral imutável"""
    try:
        # Obter IP do cliente
        endereco_ip = request.client.host
        
        service = CampanhaPoliticaService(db)
        log_criado = await service.registrar_log_eleitoral(log_data, endereco_ip)
        
        return log_criado
        
    except Exception as e:
        logger.error(f"Erro ao registrar log eleitoral: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/logs-eleitorais/{campanha_id}", response_model=List[LogEleitoralResponse])
async def listar_logs_eleitorais(
    campanha_id: int,
    limite: int = 100,
    offset: int = 0,
    tipo_log: Optional[TipoLogEleitoral] = None,
    db: Session = Depends(get_db)
):
    """Lista logs eleitorais de uma campanha (SOMENTE LEITURA)"""
    try:
        query = db.query(LogEleitoralImutavel).filter(
            LogEleitoralImutavel.campanha_politica_id == campanha_id
        )
        
        if tipo_log:
            query = query.filter(LogEleitoralImutavel.tipo_log == tipo_log)
        
        logs = query.order_by(
            LogEleitoralImutavel.timestamp_utc.desc()
        ).offset(offset).limit(limite).all()
        
        return logs
        
    except Exception as e:
        logger.error(f"Erro ao listar logs eleitorais: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ================================================
# EXPORTAÇÃO AUDITÁVEL
# ================================================

@router.post("/exportar-auditoria/{campanha_id}")
async def exportar_dados_auditoria(
    campanha_id: int,
    data_inicio: datetime,
    data_fim: datetime,
    formato: str = "JSON",
    autoridade_solicitante: str = "",
    db: Session = Depends(get_db)
):
    """Exporta dados de auditoria eleitoral em formato seguro"""
    try:
        if not autoridade_solicitante:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Autoridade solicitante é obrigatória"
            )
        
        # Buscar logs do período
        logs = db.query(LogEleitoralImutavel).filter(
            LogEleitoralImutavel.campanha_politica_id == campanha_id,
            LogEleitoralImutavel.timestamp_utc >= data_inicio,
            LogEleitoralImutavel.timestamp_utc <= data_fim
        ).order_by(LogEleitoralImutavel.timestamp_utc).all()
        
        # Buscar dados da campanha
        campanha = db.query(CampanhaPolitica).filter(
            CampanhaPolitica.id == campanha_id
        ).first()
        
        if not campanha:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha não encontrada"
            )
        
        # Preparar dados de exportação
        dados_exportacao = {
            "metadados_exportacao": {
                "campanha_id": campanha_id,
                "candidato": campanha.candidato_nome,
                "partido": campanha.partido_sigla,
                "periodo_exportacao": {
                    "inicio": data_inicio.isoformat(),
                    "fim": data_fim.isoformat()
                },
                "total_registros": len(logs),
                "data_exportacao": datetime.utcnow().isoformat(),
                "autoridade_solicitante": autoridade_solicitante,
                "hash_integridade": "calculado_abaixo"
            },
            "configuracao_eleitoral": {
                "pais": campanha.configuracao_eleitoral.pais_codigo,
                "horarios_legais": {
                    "inicio": campanha.configuracao_eleitoral.horario_inicio_permitido,
                    "fim": campanha.configuracao_eleitoral.horario_fim_permitido
                },
                "dias_permitidos": campanha.configuracao_eleitoral.dias_semana_permitidos
            },
            "logs_eleitorais": [
                {
                    "id": log.id,
                    "uuid": str(log.uuid_log),
                    "hash": log.hash_proprio,
                    "timestamp_utc": log.timestamp_utc.isoformat(),
                    "timestamp_local": log.timestamp_local.isoformat(),
                    "numero_destino": log.numero_destino,
                    "numero_cli": log.numero_cli_usado,
                    "tipo_evento": log.tipo_log,
                    "descricao": log.descricao_evento,
                    "dentro_horario_legal": log.dentro_horario_legal,
                    "ip_servidor": log.endereco_ip_servidor
                }
                for log in logs
            ]
        }
        
        # Calcular hash de integridade
        import hashlib
        dados_json = json.dumps(dados_exportacao["logs_eleitorais"], sort_keys=True)
        hash_integridade = hashlib.sha256(dados_json.encode('utf-8')).hexdigest()
        dados_exportacao["metadados_exportacao"]["hash_integridade"] = hash_integridade
        
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(dados_exportacao, f, indent=2, ensure_ascii=False)
            arquivo_temp = f.name
        
        # TODO: Implementar criptografia do arquivo
        
        return FileResponse(
            arquivo_temp,
            filename=f"auditoria_campanha_{campanha_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar dados de auditoria: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ================================================
# STATUS E ESTATÍSTICAS
# ================================================

@router.get("/status/{campanha_id}")
async def obter_status_campanha(
    campanha_id: int,
    db: Session = Depends(get_db)
):
    """Obtém status completo da campanha política"""
    try:
        campanha = db.query(CampanhaPolitica).filter(
            CampanhaPolitica.id == campanha_id
        ).first()
        
        if not campanha:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha não encontrada"
            )
        
        # Contar logs por tipo
        stats_logs = db.query(
            LogEleitoralImutavel.tipo_log,
            db.func.count(LogEleitoralImutavel.id)
        ).filter(
            LogEleitoralImutavel.campanha_politica_id == campanha_id
        ).group_by(LogEleitoralImutavel.tipo_log).all()
        
        return {
            "campanha_id": campanha_id,
            "status_politica": campanha.status_politica,
            "candidato": campanha.candidato_nome,
            "partido": campanha.partido_sigla,
            "aprovada_por_autoridade": campanha.aprovada_por_autoridade,
            "activo": campanha.activo,
            "contador_ligacoes": campanha.contador_ligacoes_realizadas,
            "contador_opt_outs": campanha.contador_opt_outs,
            "estatisticas_logs": {tipo: count for tipo, count in stats_logs},
            "periodo_legal": {
                "inicio": campanha.calendario_eleitoral.data_inicio_campanha,
                "fim": campanha.calendario_eleitoral.data_fim_campanha,
                "eleicao": campanha.calendario_eleitoral.data_eleicao
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter status da campanha: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        ) 