"""
Servico para gerenciar CLIs (Caller Line Identification) e geracao aleatoria.
"""

import random
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_
from fastapi import HTTPException

from app.models.cli import Cli
from app.schemas.lista_llamadas import validar_numero_telefone
from app.schemas.cli import (
    CliCreate,
    CliUpdate,
    CliStatsResponse,
    CliRandomResponse
)
from app.utils.logger import logger


class CliService:
    """Servico para operacoes de CLI e geracao aleatoria."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generar_cli_aleatorio(
        self, 
        excluir_cli: Optional[str] = None,
        solo_poco_usados: bool = False
    ) -> CliRandomResponse:
        """
        Gera um CLI aleatorio da lista de CLIs ativos.
        
        Args:
            excluir_cli: CLI a excluir da selecao
            solo_poco_usados: Se deve preferir CLIs menos usados
            
        Returns:
            CliRandomResponse com CLI selecionado
        """
        # Buscar CLIs ativos
        query = self.db.query(Cli).filter(Cli.activo == True)
        
        # Excluir CLI especifico se fornecido
        if excluir_cli:
            validacao = validar_numero_telefone(excluir_cli)
            if validacao.valido:
                query = query.filter(Cli.numero_normalizado != validacao.numero_normalizado)
        
        # Aplicar filtro para CLIs menos usados
        if solo_poco_usados:
            # Buscar a mediana de usos para definir "poco usado"
            sub_query = self.db.query(func.avg(Cli.veces_usado)).filter(Cli.activo == True).scalar()
            media_usos = sub_query or 0
            query = query.filter(Cli.veces_usado <= media_usos)
        
        clis_disponibles = query.all()
        
        if not clis_disponibles:
            raise HTTPException(
                status_code=404,
                detail="Nenhum CLI disponivel para selecao"
            )
        
        # Selecionar CLI aleatorio
        cli_selecionado = random.choice(clis_disponibles)
        
        # Atualizar contador de uso
        cli_selecionado.veces_usado += 1
        cli_selecionado.ultima_vez_usado = func.now()
        self.db.commit()
        self.db.refresh(cli_selecionado)
        
        logger.info(f"CLI {cli_selecionado.numero_normalizado} selecionado aleatoriamente")
        
        return CliRandomResponse(
            cli_seleccionado=cli_selecionado.numero_normalizado,
            cli_id=cli_selecionado.id,
            veces_usado=cli_selecionado.veces_usado,
            mensaje=f"CLI selecionado: {cli_selecionado.numero_normalizado}"
        )
    
    def agregar_cli(self, cli_data: CliCreate) -> Cli:
        """
        Agrega um novo CLI a base de dados.
        
        Args:
            cli_data: Dados do CLI a agregar
            
        Returns:
            Cli criado
        """
        # Validar e normalizar numero
        validacao = validar_numero_telefone(cli_data.numero)
        if not validacao.valido:
            raise HTTPException(
                status_code=400,
                detail=f"Numero CLI invalido: {validacao.motivo_invalido}"
            )
        
        # Verificar se ja existe
        existente = self.db.query(Cli).filter(
            Cli.numero_normalizado == validacao.numero_normalizado
        ).first()
        
        if existente:
            if existente.activo:
                raise HTTPException(
                    status_code=400,
                    detail=f"CLI {validacao.numero_normalizado} ja existe"
                )
            else:
                # Reativar CLI existente
                existente.activo = True
                existente.descripcion = cli_data.descripcion or existente.descripcion
                existente.notas = cli_data.notas or existente.notas
                existente.fecha_actualizacion = func.now()
                self.db.commit()
                self.db.refresh(existente)
                
                logger.info(f"CLI {validacao.numero_normalizado} reativado")
                return existente
        
        # Criar novo CLI
        nuevo_cli = Cli(
            numero=cli_data.numero,
            numero_normalizado=validacao.numero_normalizado,
            descripcion=cli_data.descripcion,
            notas=cli_data.notas,
            activo=True
        )
        
        try:
            self.db.add(nuevo_cli)
            self.db.commit()
            self.db.refresh(nuevo_cli)
            
            logger.info(f"CLI {validacao.numero_normalizado} agregado")
            return nuevo_cli
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Error al agregar CLI"
            )
    
    def agregar_clis_bulk(self, numeros: List[str], descripcion: str = None) -> Dict[str, Any]:
        """
        Agrega multiples CLIs.
        
        Args:
            numeros: Lista de numeros CLI a agregar
            descripcion: Descripcion comun para todos os CLIs
            
        Returns:
            Diccionario com estadisticas do processamento
        """
        clis_agregados = 0
        clis_duplicados = 0
        clis_invalidos = 0
        errores = []
        
        for i, numero in enumerate(numeros, 1):
            try:
                cli_data = CliCreate(
                    numero=numero,
                    descripcion=descripcion
                )
                
                self.agregar_cli(cli_data)
                clis_agregados += 1
                
            except HTTPException as e:
                if "ja existe" in str(e.detail):
                    clis_duplicados += 1
                    errores.append(f"CLI {i}: {e.detail}")
                elif "invalido" in str(e.detail):
                    clis_invalidos += 1
                    errores.append(f"CLI {i}: {e.detail}")
                else:
                    errores.append(f"CLI {i}: Error inesperado - {e.detail}")
            except Exception as e:
                errores.append(f"CLI {i}: Error inesperado - {str(e)}")
        
        return {
            'clis_agregados': clis_agregados,
            'clis_duplicados': clis_duplicados,
            'clis_invalidos': clis_invalidos,
            'errores': errores
        }
    
    def listar_clis(self, skip: int = 0, limit: int = 100, apenas_ativos: bool = True) -> List[Cli]:
        """
        Lista CLIs.
        
        Args:
            skip: Numero de registros a pular
            limit: Limite de registros
            apenas_ativos: Se deve retornar apenas CLIs ativos
            
        Returns:
            Lista de CLIs
        """
        query = self.db.query(Cli)
        
        if apenas_ativos:
            query = query.filter(Cli.activo == True)
        
        return query.order_by(Cli.fecha_creacion.desc()).offset(skip).limit(limit).all()
    
    def atualizar_cli(self, cli_id: int, dados_atualizacao: CliUpdate) -> Cli:
        """
        Atualiza dados de um CLI.
        
        Args:
            cli_id: ID do CLI
            dados_atualizacao: Dados para atualizar
            
        Returns:
            Cli atualizado
        """
        cli = self.db.query(Cli).filter(Cli.id == cli_id).first()
        
        if not cli:
            raise HTTPException(
                status_code=404,
                detail=f"CLI com ID {cli_id} nao encontrado"
            )
        
        # Atualizar campos fornecidos
        if dados_atualizacao.descripcion is not None:
            cli.descripcion = dados_atualizacao.descripcion
        
        if dados_atualizacao.notas is not None:
            cli.notas = dados_atualizacao.notas
        
        if dados_atualizacao.activo is not None:
            cli.activo = dados_atualizacao.activo
        
        cli.fecha_actualizacion = func.now()
        self.db.commit()
        self.db.refresh(cli)
        
        logger.info(f"CLI {cli.numero_normalizado} atualizado")
        return cli
    
    def remover_cli(self, cli_id: int) -> bool:
        """
        Remove um CLI (marca como inativo).
        
        Args:
            cli_id: ID do CLI
            
        Returns:
            True se removido com sucesso
        """
        cli = self.db.query(Cli).filter(Cli.id == cli_id).first()
        
        if not cli:
            raise HTTPException(
                status_code=404,
                detail=f"CLI com ID {cli_id} nao encontrado"
            )
        
        cli.activo = False
        cli.fecha_actualizacion = func.now()
        self.db.commit()
        
        logger.info(f"CLI {cli.numero_normalizado} removido")
        return True
    
    def obter_estatisticas(self) -> CliStatsResponse:
        """
        Obtem estatisticas dos CLIs.
        
        Returns:
            CliStatsResponse com estatisticas
        """
        hoje = datetime.now().date()
        inicio_mes = datetime.now().replace(day=1).date()
        
        # Contadores basicos
        total_clis = self.db.query(Cli).count()
        clis_activos = self.db.query(Cli).filter(Cli.activo == True).count()
        clis_inactivos = total_clis - clis_activos
        
        # Usos hoje
        total_usos_hoy = self.db.query(func.sum(Cli.veces_usado)).filter(
            func.date(Cli.ultima_vez_usado) == hoje
        ).scalar() or 0
        
        # Usos no mes
        total_usos_mes = self.db.query(func.sum(Cli.veces_usado)).filter(
            func.date(Cli.ultima_vez_usado) >= inicio_mes
        ).scalar() or 0
        
        # CLI mais usado
        cli_mas_usado = self.db.query(Cli).filter(
            Cli.activo == True
        ).order_by(Cli.veces_usado.desc()).first()
        
        return CliStatsResponse(
            total_clis=total_clis,
            clis_activos=clis_activos,
            clis_inactivos=clis_inactivos,
            cli_mas_usado=cli_mas_usado.numero_normalizado if cli_mas_usado else None,
            total_usos_hoy=total_usos_hoy,
            total_usos_mes=total_usos_mes
        ) 
