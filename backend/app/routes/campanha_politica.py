#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas API para o sistema de Campanhas Politicas
Endpoints para conformidade com legislacao eleitoral
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

router = APIRouter(tags=["Campanhas Politicas"])

# ================================================
# CONFIGURACAO ELEITORAL
# ================================================

@router.post("/configuracao-eleitoral", response_model=ConfiguracaoEleitoralResponse)
async def criar_configuracao_eleitoral(
    configuracao: ConfiguracaoEleitoralCreate,
    db: Session = Depends(get_db)
):
    """Cria nova configuracao eleitoral para um pais"""
    try:
        # Verificar se ja existe configuracao para o pais
        config_existente = db.query(ConfiguracaoEleitoral).filter(
            ConfiguracaoEleitoral.pais_codigo == configuracao.pais_codigo
        ).first()
        
        if config_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Configuracao eleitoral ja existe para o pais {configuracao.pais_codigo}"
            )
        
        # Criar configuracao
        nova_config = ConfiguracaoEleitoral(**configuracao.dict())
        db.add(nova_config)
        db.commit()
        db.refresh(nova_config)
        
        logger.info(f"Configuracao eleitoral criada para pais: {configuracao.pais_codigo}")
        
        return nova_config
        
    except Exception as e:
        logger.error(f"Erro ao criar configuracao eleitoral: {e}")
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
    """Lista configuracoes eleitorais"""
    try:
        query = db.query(ConfiguracaoEleitoral)
        
        if pais_codigo:
            query = query.filter(ConfiguracaoEleitoral.pais_codigo == pais_codigo)
        
        if activo is not None:
            query = query.filter(ConfiguracaoEleitoral.activo == activo)
        
        configuracoes = query.all()
        return configuracoes
        
    except Exception as e:
        logger.error(f"Erro ao listar configuracoes eleitorais: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ================================================
# CALENDARIO ELEITORAL
# ================================================

@router.post("/calendario-eleitoral", response_model=CalendarioEleitoralResponse)
async def criar_calendario_eleitoral(
    calendario: CalendarioEleitoralCreate,
    db: Session = Depends(get_db)
):
    """Cria novo calendario eleitoral"""
    try:
        novo_calendario = CalendarioEleitoral(**calendario.dict())
        db.add(novo_calendario)
        db.commit()
        db.refresh(novo_calendario)
        
        logger.info(f"Calendario eleitoral criado: {calendario.nome_eleicao}")
        
        return novo_calendario
        
    except Exception as e:
        logger.error(f"Erro ao criar calendario eleitoral: {e}")
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
    """Lista calendarios eleitorais"""
    try:
        query = db.query(CalendarioEleitoral)
        
        if pais_codigo:
            query = query.filter(CalendarioEleitoral.pais_codigo == pais_codigo)
        
        if activo is not None:
            query = query.filter(CalendarioEleitoral.activo == activo)
        
        calendarios = query.order_by(CalendarioEleitoral.data_eleicao.desc()).all()
        return calendarios
        
    except Exception as e:
        logger.error(f"Erro ao listar calendarios eleitorais: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ================================================
# CAMPANHAS POLITICAS
# ================================================

@router.post("/campanhas", response_model=CampanhaPoliticaResponse)
async def criar_campanha_politica(
    campanha: CampanhaPoliticaCreate,
    db: Session = Depends(get_db)
):
    """Cria nova campanha politica"""
    try:
        # Verificar se campanha base existe
        # from app.models.campana import Campana  # Comentado temporariamente - modelo não existe
        # campanha_base = db.query(Campana).filter(
        #     Campana.id == campanha.campanha_base_id
        # ).first()
        
        # if not campanha_base:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="Campanha base nao encontrada"
        #     )
        
        # Verificar se ja existe campanha politica para esta campanha base
        campanha_existente = db.query(CampanhaPolitica).filter(
            CampanhaPolitica.campanha_base_id == campanha.campanha_base_id
        ).first()
        
        if campanha_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ja existe campanha politica para esta campanha base"
            )
        
        # Calcular hash de configuracao
        service = CampanhaPoliticaService(db)
        hash_config = "temp_hash"  # TODO: Implementar calculo real
        
        # Criar campanha politica
        nova_campanha = CampanhaPolitica(
            **campanha.dict(),
            hash_configuracao=hash_config
        )
        
        db.add(nova_campanha)
        db.commit()
        db.refresh(nova_campanha)
        
        logger.info(f"Campanha politica criada: {campanha.candidato_nome}")
        
        return nova_campanha
        
    except Exception as e:
        logger.error(f"Erro ao criar campanha politica: {e}")
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
    """Lista campanhas politicas"""
    try:
        query = db.query(CampanhaPolitica)
        
        if activo is not None:
            query = query.filter(CampanhaPolitica.activo == activo)
        
        if partido_sigla:
            query = query.filter(CampanhaPolitica.partido_sigla == partido_sigla)
        
        campanhas = query.all()
        return campanhas
        
    except Exception as e:
        logger.error(f"Erro ao listar campanhas politicas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ================================================
# VALIDACOES
# ================================================

@router.post("/validar-horario", response_model=ValidacaoHorarioResponse)
async def validar_horario_legal(
    validacao: ValidacaoHorarioRequest,
    db: Session = Depends(get_db)
):
    """Valida se horario de ligacao esta dentro do permitido"""
    try:
        service = CampanhaPoliticaService(db)
        resultado = await service.validar_horario_legal(
            validacao.campanha_politica_id,
            validacao.timestamp_ligacao
        )
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na validacao de horario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# ================================================
# STATUS E MONITORAMENTO
# ================================================

@router.get("/status/{campanha_id}")
async def obter_status_campanha(
    campanha_id: int,
    db: Session = Depends(get_db)
):
    """Obtem status completo da campanha politica"""
    try:
        service = CampanhaPoliticaService(db)
        status = await service.obter_status_completo(campanha_id)
        return status
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        ) 