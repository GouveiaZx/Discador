"""
Servico para gerenciar blacklist/lista negra de numeros.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_
from fastapi import HTTPException

from app.models.lista_negra import ListaNegra
from app.schemas.lista_llamadas import validar_numero_telefone
from app.schemas.blacklist import (
    BlacklistCreate,
    BlacklistUpdate, 
    BlacklistSearchRequest,
    BlacklistVerificationResponse,
    BlacklistStatsResponse
)
from app.utils.logger import logger


class BlacklistService:
    """Servico para operacoes de blacklist."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verificar_numero_blacklist(self, numero: str) -> BlacklistVerificationResponse:
        """
        Verifica se um numero esta na blacklist.
        
        Args:
            numero: Numero a verificar
            
        Returns:
            BlacklistVerificationResponse com resultado da verificacao
        """
        # Normalizar numero
        validacao = validar_numero_telefone(numero)
        if not validacao.valido:
            return BlacklistVerificationResponse(
                numero_original=numero,
                numero_normalizado="",
                en_blacklist=False,
                motivo="Numero invalido para verificacion"
            )
        
        # Buscar en blacklist
        entrada_blacklist = self.db.query(ListaNegra).filter(
            and_(
                ListaNegra.numero_normalizado == validacao.numero_normalizado,
                ListaNegra.activo == True
            )
        ).first()
        
        if entrada_blacklist:
            # Incrementar contador y actualizar fecha
            entrada_blacklist.veces_bloqueado += 1
            entrada_blacklist.ultima_vez_bloqueado = func.now()
            self.db.commit()
            
            logger.info(f"Numero {validacao.numero_normalizado} bloqueado por blacklist")
            
            return BlacklistVerificationResponse(
                numero_original=numero,
                numero_normalizado=validacao.numero_normalizado,
                en_blacklist=True,
                motivo=entrada_blacklist.motivo,
                fecha_bloqueo=entrada_blacklist.fecha_creacion
            )
        
        return BlacklistVerificationResponse(
            numero_original=numero,
            numero_normalizado=validacao.numero_normalizado,
            en_blacklist=False
        )
    
    def agregar_numero_blacklist(self, numero_data: BlacklistCreate) -> ListaNegra:
        """
        Agrega un numero a la blacklist.
        
        Args:
            numero_data: Datos del numero a agregar
            
        Returns:
            ListaNegra creada
        """
        # Validar y normalizar numero
        validacion = validar_numero_telefone(numero_data.numero)
        if not validacion.valido:
            raise HTTPException(
                status_code=400,
                detail=f"Numero invalido: {validacion.motivo_invalido}"
            )
        
        # Verificar si ya existe
        existente = self.db.query(ListaNegra).filter(
            ListaNegra.numero_normalizado == validacion.numero_normalizado
        ).first()
        
        if existente:
            if existente.activo:
                raise HTTPException(
                    status_code=400,
                    detail=f"El numero {validacion.numero_normalizado} ya esta en blacklist"
                )
            else:
                # Reactivar entrada existente
                existente.activo = True
                existente.motivo = numero_data.motivo or existente.motivo
                existente.observaciones = numero_data.observaciones or existente.observaciones
                existente.creado_por = numero_data.creado_por or existente.creado_por
                existente.fecha_actualizacion = func.now()
                self.db.commit()
                self.db.refresh(existente)
                
                logger.info(f"Numero {validacion.numero_normalizado} reactivado en blacklist")
                return existente
        
        # Crear nueva entrada
        nueva_entrada = ListaNegra(
            numero=numero_data.numero,
            numero_normalizado=validacion.numero_normalizado,
            motivo=numero_data.motivo,
            observaciones=numero_data.observaciones,
            creado_por=numero_data.creado_por,
            activo=True
        )
        
        try:
            self.db.add(nueva_entrada)
            self.db.commit()
            self.db.refresh(nueva_entrada)
            
            logger.info(f"Numero {validacion.numero_normalizado} agregado a blacklist")
            return nueva_entrada
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Error al agregar numero a blacklist"
            )
    
    def agregar_numeros_bulk(self, numeros: List[str], motivo: str = None, creado_por: str = None) -> Dict[str, Any]:
        """
        Agrega multiples numeros a la blacklist.
        
        Args:
            numeros: Lista de numeros a agregar
            motivo: Motivo comun para todos los numeros
            creado_por: Usuario que agrega los numeros
            
        Returns:
            Diccionario con estadisticas del procesamiento
        """
        numeros_agregados = 0
        numeros_duplicados = 0
        numeros_invalidos = 0
        errores = []
        
        for i, numero in enumerate(numeros, 1):
            try:
                numero_data = BlacklistCreate(
                    numero=numero,
                    motivo=motivo,
                    creado_por=creado_por
                )
                
                self.agregar_numero_blacklist(numero_data)
                numeros_agregados += 1
                
            except HTTPException as e:
                if "ya esta en blacklist" in str(e.detail):
                    numeros_duplicados += 1
                    errores.append(f"Numero {i}: {e.detail}")
                elif "invalido" in str(e.detail):
                    numeros_invalidos += 1
                    errores.append(f"Numero {i}: {e.detail}")
                else:
                    errores.append(f"Numero {i}: Error inesperado - {e.detail}")
            except Exception as e:
                errores.append(f"Numero {i}: Error inesperado - {str(e)}")
        
        return {
            'numeros_agregados': numeros_agregados,
            'numeros_duplicados': numeros_duplicados,
            'numeros_invalidos': numeros_invalidos,
            'errores': errores
        }
    
    def remover_numero_blacklist(self, numero_id: int) -> bool:
        """
        Remove um numero da blacklist (marca como inativo).
        
        Args:
            numero_id: ID do numero na blacklist
            
        Returns:
            True se removido com sucesso
        """
        entrada = self.db.query(ListaNegra).filter(ListaNegra.id == numero_id).first()
        
        if not entrada:
            raise HTTPException(
                status_code=404,
                detail=f"Numero com ID {numero_id} nao encontrado na blacklist"
            )
        
        entrada.activo = False
        entrada.fecha_actualizacion = func.now()
        self.db.commit()
        
        logger.info(f"Numero {entrada.numero_normalizado} removido da blacklist")
        return True
    
    def remover_numero_por_telefone(self, numero: str) -> bool:
        """
        Remove um numero da blacklist por numero de telefone.
        
        Args:
            numero: Numero de telefone a remover
            
        Returns:
            True se removido com sucesso
        """
        validacao = validar_numero_telefone(numero)
        if not validacao.valido:
            raise HTTPException(
                status_code=400,
                detail=f"Numero invalido: {validacao.motivo_invalido}"
            )
        
        entrada = self.db.query(ListaNegra).filter(
            and_(
                ListaNegra.numero_normalizado == validacao.numero_normalizado,
                ListaNegra.activo == True
            )
        ).first()
        
        if not entrada:
            raise HTTPException(
                status_code=404,
                detail=f"Numero {validacao.numero_normalizado} nao encontrado na blacklist ativa"
            )
        
        entrada.activo = False
        entrada.fecha_actualizacion = func.now()
        self.db.commit()
        
        logger.info(f"Numero {validacao.numero_normalizado} removido da blacklist")
        return True
    
    def atualizar_numero_blacklist(self, numero_id: int, dados_atualizacao: BlacklistUpdate) -> ListaNegra:
        """
        Atualiza dados de um numero na blacklist.
        
        Args:
            numero_id: ID do numero na blacklist
            dados_atualizacao: Dados para atualizar
            
        Returns:
            ListaNegra atualizada
        """
        entrada = self.db.query(ListaNegra).filter(ListaNegra.id == numero_id).first()
        
        if not entrada:
            raise HTTPException(
                status_code=404,
                detail=f"Numero com ID {numero_id} nao encontrado na blacklist"
            )
        
        # Atualizar campos fornecidos
        if dados_atualizacao.motivo is not None:
            entrada.motivo = dados_atualizacao.motivo
        
        if dados_atualizacao.observaciones is not None:
            entrada.observaciones = dados_atualizacao.observaciones
        
        if dados_atualizacao.activo is not None:
            entrada.activo = dados_atualizacao.activo
        
        entrada.fecha_actualizacion = func.now()
        self.db.commit()
        self.db.refresh(entrada)
        
        logger.info(f"Numero {entrada.numero_normalizado} atualizado na blacklist")
        return entrada
    
    def buscar_blacklist(self, criterios: BlacklistSearchRequest, skip: int = 0, limit: int = 100) -> List[ListaNegra]:
        """
        Busca numeros na blacklist com filtros.
        
        Args:
            criterios: Criterios de busca
            skip: Numero de registros a pular
            limit: Limite de registros a retornar
            
        Returns:
            Lista de numeros encontrados
        """
        query = self.db.query(ListaNegra)
        
        # Aplicar filtros
        if criterios.numero:
            validacao = validar_numero_telefone(criterios.numero)
            if validacao.valido:
                query = query.filter(
                    or_(
                        ListaNegra.numero.ilike(f"%{criterios.numero}%"),
                        ListaNegra.numero_normalizado.ilike(f"%{validacao.numero_normalizado}%")
                    )
                )
        
        if criterios.motivo:
            query = query.filter(ListaNegra.motivo.ilike(f"%{criterios.motivo}%"))
        
        if criterios.creado_por:
            query = query.filter(ListaNegra.creado_por.ilike(f"%{criterios.creado_por}%"))
        
        if criterios.activo is not None:
            query = query.filter(ListaNegra.activo == criterios.activo)
        
        if criterios.fecha_desde:
            query = query.filter(ListaNegra.fecha_creacion >= criterios.fecha_desde)
        
        if criterios.fecha_hasta:
            query = query.filter(ListaNegra.fecha_creacion <= criterios.fecha_hasta)
        
        return query.order_by(ListaNegra.fecha_creacion.desc()).offset(skip).limit(limit).all()
    
    def obter_estatisticas(self) -> BlacklistStatsResponse:
        """
        Obtem estatisticas da blacklist.
        
        Returns:
            BlacklistStatsResponse com estatisticas
        """
        hoje = datetime.now().date()
        inicio_mes = datetime.now().replace(day=1).date()
        
        # Contadores basicos
        total_numeros = self.db.query(ListaNegra).count()
        numeros_activos = self.db.query(ListaNegra).filter(ListaNegra.activo == True).count()
        numeros_inactivos = total_numeros - numeros_activos
        
        # Bloqueos hoje
        total_bloqueos_hoy = self.db.query(func.sum(ListaNegra.veces_bloqueado)).filter(
            func.date(ListaNegra.ultima_vez_bloqueado) == hoje
        ).scalar() or 0
        
        # Bloqueos no mes
        total_bloqueos_mes = self.db.query(func.sum(ListaNegra.veces_bloqueado)).filter(
            func.date(ListaNegra.ultima_vez_bloqueado) >= inicio_mes
        ).scalar() or 0
        
        # Numero mais bloqueado
        numero_mais_bloqueado = self.db.query(ListaNegra).filter(
            ListaNegra.activo == True
        ).order_by(ListaNegra.veces_bloqueado.desc()).first()
        
        return BlacklistStatsResponse(
            total_numeros=total_numeros,
            numeros_activos=numeros_activos,
            numeros_inactivos=numeros_inactivos,
            total_bloqueos_hoy=total_bloqueos_hoy,
            total_bloqueos_mes=total_bloqueos_mes,
            numero_mas_bloqueado=numero_mais_bloqueado.numero_normalizado if numero_mais_bloqueado else None
        )
    
    def listar_blacklist(self, skip: int = 0, limit: int = 100, apenas_ativos: bool = True) -> List[ListaNegra]:
        """
        Lista numeros da blacklist.
        
        Args:
            skip: Numero de registros a pular
            limit: Limite de registros
            apenas_ativos: Se deve retornar apenas numeros ativos
            
        Returns:
            Lista de numeros na blacklist
        """
        query = self.db.query(ListaNegra)
        
        if apenas_ativos:
            query = query.filter(ListaNegra.activo == True)
        
        return query.order_by(ListaNegra.fecha_creacion.desc()).offset(skip).limit(limit).all() 
