"""
Serviço para gerenciar blacklist/lista negra de números.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_
from fastapi import HTTPException

from app.models.lista_negra import ListaNegra
from app.schemas.lista_llamadas import validar_numero_telefono
from app.schemas.blacklist import (
    BlacklistCreate,
    BlacklistUpdate, 
    BlacklistSearchRequest,
    BlacklistVerificationResponse,
    BlacklistStatsResponse
)
from app.utils.logger import logger


class BlacklistService:
    """Serviço para operações de blacklist."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verificar_numero_blacklist(self, numero: str) -> BlacklistVerificationResponse:
        """
        Verifica se um número está na blacklist.
        
        Args:
            numero: Número a verificar
            
        Returns:
            BlacklistVerificationResponse com resultado da verificação
        """
        # Normalizar número
        validacao = validar_numero_telefono(numero)
        if not validacao.valido:
            return BlacklistVerificationResponse(
                numero_original=numero,
                numero_normalizado="",
                en_blacklist=False,
                motivo="Número inválido para verificación"
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
            
            logger.info(f"Número {validacao.numero_normalizado} bloqueado por blacklist")
            
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
        Agrega un número a la blacklist.
        
        Args:
            numero_data: Datos del número a agregar
            
        Returns:
            ListaNegra creada
        """
        # Validar y normalizar número
        validacion = validar_numero_telefono(numero_data.numero)
        if not validacion.valido:
            raise HTTPException(
                status_code=400,
                detail=f"Número inválido: {validacion.motivo_invalido}"
            )
        
        # Verificar si ya existe
        existente = self.db.query(ListaNegra).filter(
            ListaNegra.numero_normalizado == validacion.numero_normalizado
        ).first()
        
        if existente:
            if existente.activo:
                raise HTTPException(
                    status_code=400,
                    detail=f"El número {validacion.numero_normalizado} ya está en blacklist"
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
                
                logger.info(f"Número {validacion.numero_normalizado} reactivado en blacklist")
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
            
            logger.info(f"Número {validacion.numero_normalizado} agregado a blacklist")
            return nueva_entrada
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Error al agregar número a blacklist"
            )
    
    def agregar_numeros_bulk(self, numeros: List[str], motivo: str = None, creado_por: str = None) -> Dict[str, Any]:
        """
        Agrega múltiples números a la blacklist.
        
        Args:
            numeros: Lista de números a agregar
            motivo: Motivo común para todos los números
            creado_por: Usuario que agrega los números
            
        Returns:
            Diccionario con estadísticas del procesamiento
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
                if "ya está en blacklist" in str(e.detail):
                    numeros_duplicados += 1
                    errores.append(f"Número {i}: {e.detail}")
                elif "inválido" in str(e.detail):
                    numeros_invalidos += 1
                    errores.append(f"Número {i}: {e.detail}")
                else:
                    errores.append(f"Número {i}: Error inesperado - {e.detail}")
            except Exception as e:
                errores.append(f"Número {i}: Error inesperado - {str(e)}")
        
        return {
            'numeros_agregados': numeros_agregados,
            'numeros_duplicados': numeros_duplicados,
            'numeros_invalidos': numeros_invalidos,
            'errores': errores
        }
    
    def remover_numero_blacklist(self, numero_id: int) -> bool:
        """
        Remove um número da blacklist (marca como inativo).
        
        Args:
            numero_id: ID do número na blacklist
            
        Returns:
            True se removido com sucesso
        """
        entrada = self.db.query(ListaNegra).filter(ListaNegra.id == numero_id).first()
        
        if not entrada:
            raise HTTPException(
                status_code=404,
                detail=f"Número com ID {numero_id} não encontrado na blacklist"
            )
        
        entrada.activo = False
        entrada.fecha_actualizacion = func.now()
        self.db.commit()
        
        logger.info(f"Número {entrada.numero_normalizado} removido da blacklist")
        return True
    
    def remover_numero_por_telefone(self, numero: str) -> bool:
        """
        Remove um número da blacklist por número de telefone.
        
        Args:
            numero: Número de telefone a remover
            
        Returns:
            True se removido com sucesso
        """
        validacao = validar_numero_telefone(numero)
        if not validacao.valido:
            raise HTTPException(
                status_code=400,
                detail=f"Número inválido: {validacao.motivo_invalido}"
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
                detail=f"Número {validacao.numero_normalizado} não encontrado na blacklist ativa"
            )
        
        entrada.activo = False
        entrada.fecha_actualizacion = func.now()
        self.db.commit()
        
        logger.info(f"Número {validacao.numero_normalizado} removido da blacklist")
        return True
    
    def atualizar_numero_blacklist(self, numero_id: int, dados_atualizacao: BlacklistUpdate) -> ListaNegra:
        """
        Atualiza dados de um número na blacklist.
        
        Args:
            numero_id: ID do número na blacklist
            dados_atualizacao: Dados para atualizar
            
        Returns:
            ListaNegra atualizada
        """
        entrada = self.db.query(ListaNegra).filter(ListaNegra.id == numero_id).first()
        
        if not entrada:
            raise HTTPException(
                status_code=404,
                detail=f"Número com ID {numero_id} não encontrado na blacklist"
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
        
        logger.info(f"Número {entrada.numero_normalizado} atualizado na blacklist")
        return entrada
    
    def buscar_blacklist(self, criterios: BlacklistSearchRequest, skip: int = 0, limit: int = 100) -> List[ListaNegra]:
        """
        Busca números na blacklist com filtros.
        
        Args:
            criterios: Critérios de busca
            skip: Número de registros a pular
            limit: Limite de registros a retornar
            
        Returns:
            Lista de números encontrados
        """
        query = self.db.query(ListaNegra)
        
        # Aplicar filtros
        if criterios.numero:
            validacao = validar_numero_telefono(criterios.numero)
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
        Obtém estatísticas da blacklist.
        
        Returns:
            BlacklistStatsResponse com estatísticas
        """
        hoje = datetime.now().date()
        inicio_mes = datetime.now().replace(day=1).date()
        
        # Contadores básicos
        total_numeros = self.db.query(ListaNegra).count()
        numeros_activos = self.db.query(ListaNegra).filter(ListaNegra.activo == True).count()
        numeros_inactivos = total_numeros - numeros_activos
        
        # Bloqueos hoje
        total_bloqueos_hoy = self.db.query(func.sum(ListaNegra.veces_bloqueado)).filter(
            func.date(ListaNegra.ultima_vez_bloqueado) == hoje
        ).scalar() or 0
        
        # Bloqueos no mês
        total_bloqueos_mes = self.db.query(func.sum(ListaNegra.veces_bloqueado)).filter(
            func.date(ListaNegra.ultima_vez_bloqueado) >= inicio_mes
        ).scalar() or 0
        
        # Número mais bloqueado
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
        Lista números da blacklist.
        
        Args:
            skip: Número de registros a pular
            limit: Limite de registros
            apenas_ativos: Se deve retornar apenas números ativos
            
        Returns:
            Lista de números na blacklist
        """
        query = self.db.query(ListaNegra)
        
        if apenas_ativos:
            query = query.filter(ListaNegra.activo == True)
        
        return query.order_by(ListaNegra.fecha_creacion.desc()).offset(skip).limit(limit).all() 