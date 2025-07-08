"""
Servico de discagem que integra blacklist e multiplas listas de llamadas.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.llamada import Llamada
from app.models.lista_llamadas import ListaLlamadas, NumeroLlamada
from app.services.blacklist_service import BlacklistService
from app.services.cli_service import CliService
from app.services.asterisk import asterisk_service
from app.schemas.lista_llamadas import validar_numero_telefone
from app.utils.logger import logger


class DiscadoService:
    """Servico para gerenciar o discado com verificacao de blacklist e geracao de CLI."""
    
    def __init__(self, db: Session):
        self.db = db
        self.blacklist_service = BlacklistService(db)
        self.cli_service = CliService(db)
    
    async def iniciar_llamada(
        self,
        numero_destino: str,
        campana_id: Optional[int] = None,
        lista_llamadas_id: Optional[int] = None,
        usuario_id: Optional[str] = None,
        cli_personalizado: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Inicia una llamada verificando primero la blacklist y generando CLI aleatorio.
        
        Args:
            numero_destino: Numero a llamar
            campana_id: ID de la campana (opcional)
            lista_llamadas_id: ID de la lista de llamadas (opcional)
            usuario_id: ID del usuario que inicia la llamada
            cli_personalizado: CLI especifico a usar (opcional, caso contrario sera aleatorio)
            
        Returns:
            Diccionario con resultado del intento de llamada
        """
        logger.info(f"Iniciando llamada a {numero_destino}")
        
        # Validar y normalizar numero
        validacion = validar_numero_telefone(numero_destino)
        if not validacion.valido:
            return {
                "estado": "error",
                "mensaje": f"Numero invalido: {validacion.motivo_invalido}",
                "numero_destino": numero_destino,
                "bloqueado_blacklist": False
            }
        
        numero_normalizado = validacion.numero_normalizado
        
        # Verificar blacklist
        verificacion_blacklist = self.blacklist_service.verificar_numero_blacklist(numero_destino)
        
        if verificacion_blacklist.en_blacklist:
            logger.warning(f"Llamada bloqueada por blacklist: {numero_normalizado}")
            
            # Registrar llamada bloqueada
            llamada_bloqueada = Llamada(
                numero_destino=numero_destino,
                numero_normalizado=numero_normalizado,
                id_campana=campana_id,
                id_lista_llamadas=lista_llamadas_id,
                usuario_id=usuario_id,
                estado="bloqueada",
                resultado="blacklist",
                bloqueado_blacklist=True
            )
            
            self.db.add(llamada_bloqueada)
            self.db.commit()
            self.db.refresh(llamada_bloqueada)
            
            return {
                "estado": "bloqueado",
                "mensaje": f"Numero bloqueado por blacklist: {verificacion_blacklist.motivo}",
                "numero_destino": numero_destino,
                "numero_normalizado": numero_normalizado,
                "bloqueado_blacklist": True,
                "motivo_bloqueo": verificacion_blacklist.motivo,
                "fecha_bloqueo": verificacion_blacklist.fecha_bloqueo,
                "llamada_id": llamada_bloqueada.id
            }
        
        # Generar o usar CLI
        if cli_personalizado:
            cli_generado = cli_personalizado
            cli_aleatorio_info = {"mensaje": f"CLI personalizado usado: {cli_personalizado}"}
        else:
            try:
                # Generar CLI aleatorio
                cli_aleatorio_info = self.cli_service.generar_cli_aleatorio(
                    solo_poco_usados=True  # Preferir CLIs menos usados
                )
                cli_generado = cli_aleatorio_info.cli_seleccionado
                logger.info(f"CLI aleatorio generado: {cli_generado}")
            except HTTPException as e:
                # Si no hay CLIs disponibles, usar CLI de fallback
                cli_generado = "+5491122334455"  # CLI de fallback
                cli_aleatorio_info = {"mensaje": "CLI de fallback usado (sin CLIs disponibles)"}
                logger.warning(f"No hay CLIs disponibles, usando CLI de fallback: {cli_generado}")
        
        try:
            # Originar llamada traves do Asterisk
            respuesta_asterisk = await asterisk_service.originar_llamada(
                numero_destino=numero_normalizado,
                cli=cli_generado
            )
            
            # Registrar llamada en BD
            nueva_llamada = Llamada(
                numero_destino=numero_destino,
                numero_normalizado=numero_normalizado,
                cli=cli_generado,
                id_campana=campana_id,
                id_lista_llamadas=lista_llamadas_id,
                usuario_id=usuario_id,
                estado="en_progreso",
                bloqueado_blacklist=False
            )
            
            self.db.add(nueva_llamada)
            self.db.commit()
            self.db.refresh(nueva_llamada)
            
            logger.info(f"Llamada iniciada exitosamente: {numero_normalizado} [ID: {nueva_llamada.id}] CLI: {cli_generado}")
            
            return {
                "estado": "iniciado",
                "mensaje": "Llamada iniciada exitosamente",
                "numero_destino": numero_destino,
                "numero_normalizado": numero_normalizado,
                "cli_utilizado": cli_generado,
                "cli_info": cli_aleatorio_info,
                "llamada_id": nueva_llamada.id,
                "unique_id": respuesta_asterisk.get("UniqueID"),
                "channel": respuesta_asterisk.get("Channel"),
                "bloqueado_blacklist": False
            }
            
        except Exception as e:
            logger.error(f"Error al iniciar llamada: {str(e)}")
            
            # Registrar llamada fallida
            llamada_fallida = Llamada(
                numero_destino=numero_destino,
                numero_normalizado=numero_normalizado,
                cli=cli_generado,
                id_campana=campana_id,
                id_lista_llamadas=lista_llamadas_id,
                usuario_id=usuario_id,
                estado="fallida",
                resultado="error_sistema",
                bloqueado_blacklist=False
            )
            
            self.db.add(llamada_fallida)
            self.db.commit()
            
            raise HTTPException(
                status_code=500,
                detail=f"Error al iniciar llamada: {str(e)}"
            )
    
    def obtener_proxima_llamada_lista(
        self,
        lista_llamadas_id: int,
        usuario_id: Optional[str] = None,
        excluir_blacklist: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene el proximo numero a llamar de una lista especifica.
        
        Args:
            lista_llamadas_id: ID de la lista de llamadas
            usuario_id: ID del usuario (opcional)
            excluir_blacklist: Si debe excluir numeros en blacklist
            
        Returns:
            Diccionario con datos del proximo numero o None si no hay
        """
        # Verificar que la lista existe y esta activa
        lista = self.db.query(ListaLlamadas).filter(
            ListaLlamadas.id == lista_llamadas_id,
            ListaLlamadas.activa == True
        ).first()
        
        if not lista:
            raise HTTPException(
                status_code=404,
                detail=f"Lista de llamadas {lista_llamadas_id} no encontrada o inactiva"
            )
        
        # Buscar numeros de la lista que no han sido llamados
        query = self.db.query(NumeroLlamada).filter(
            NumeroLlamada.id_lista == lista_llamadas_id,
            NumeroLlamada.valido == True
        )
        
        # Excluir numeros que ya tienen llamadas registradas
        subquery_llamadas = self.db.query(Llamada.numero_normalizado).filter(
            Llamada.id_lista_llamadas == lista_llamadas_id
        )
        
        query = query.filter(
            ~NumeroLlamada.numero_normalizado.in_(subquery_llamadas)
        )
        
        # Si se debe excluir blacklist, filtrar numeros bloqueados
        if excluir_blacklist:
            from app.models.lista_negra import ListaNegra
            
            subquery_blacklist = self.db.query(ListaNegra.numero_normalizado).filter(
                ListaNegra.activo == True
            )
            
            query = query.filter(
                ~NumeroLlamada.numero_normalizado.in_(subquery_blacklist)
            )
        
        # Obtener el primer numero disponible
        proximo_numero = query.first()
        
        if not proximo_numero:
            logger.info(f"No hay mas numeros disponibles en lista {lista_llamadas_id}")
            return None
        
        return {
            "numero_id": proximo_numero.id,
            "numero": proximo_numero.numero,
            "numero_normalizado": proximo_numero.numero_normalizado,
            "lista_id": lista_llamadas_id,
            "lista_nombre": lista.nombre
        }
    
    async def llamar_siguiente_de_lista(
        self,
        lista_llamadas_id: int,
        campana_id: Optional[int] = None,
        usuario_id: Optional[str] = None,
        cli_personalizado: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Llama al siguiente numero disponible de una lista con CLI aleatorio.
        
        Args:
            lista_llamadas_id: ID de la lista de llamadas
            campana_id: ID de la campana (opcional)
            usuario_id: ID del usuario
            cli_personalizado: CLI especifico a usar (opcional)
            
        Returns:
            Resultado del intento de llamada
        """
        # Obtener proximo numero
        proximo = self.obtener_proxima_llamada_lista(lista_llamadas_id, usuario_id)
        
        if not proximo:
            return {
                "estado": "sin_numeros",
                "mensaje": f"No hay mas numeros disponibles en la lista {lista_llamadas_id}",
                "lista_id": lista_llamadas_id
            }
        
        # Iniciar llamada con CLI personalizado o aleatorio
        resultado = await self.iniciar_llamada(
            numero_destino=proximo["numero_normalizado"],
            campana_id=campana_id,
            lista_llamadas_id=lista_llamadas_id,
            usuario_id=usuario_id,
            cli_personalizado=cli_personalizado
        )
        
        # Agregar informacion de la lista al resultado
        resultado.update({
            "lista_id": lista_llamadas_id,
            "lista_nombre": proximo["lista_nombre"],
            "numero_id": proximo["numero_id"]
        })
        
        return resultado
    
    def obtener_estadisticas_lista(self, lista_llamadas_id: int) -> Dict[str, Any]:
        """
        Obtiene estadisticas de una lista de llamadas.
        
        Args:
            lista_llamadas_id: ID de la lista
            
        Returns:
            Diccionario con estadisticas
        """
        lista = self.db.query(ListaLlamadas).filter(ListaLlamadas.id == lista_llamadas_id).first()
        
        if not lista:
            raise HTTPException(
                status_code=404,
                detail=f"Lista {lista_llamadas_id} no encontrada"
            )
        
        # Contar numeros totales en la lista
        total_numeros = self.db.query(NumeroLlamada).filter(
            NumeroLlamada.id_lista == lista_llamadas_id,
            NumeroLlamada.valido == True
        ).count()
        
        # Contar llamadas realizadas
        llamadas_realizadas = self.db.query(Llamada).filter(
            Llamada.id_lista_llamadas == lista_llamadas_id
        ).count()
        
        # Contar llamadas bloqueadas por blacklist
        llamadas_bloqueadas = self.db.query(Llamada).filter(
            Llamada.id_lista_llamadas == lista_llamadas_id,
            Llamada.bloqueado_blacklist == True
        ).count()
        
        # Contar llamadas exitosas
        llamadas_exitosas = self.db.query(Llamada).filter(
            Llamada.id_lista_llamadas == lista_llamadas_id,
            Llamada.estado.in_(["conectada", "finalizada"]),
            Llamada.bloqueado_blacklist == False
        ).count()
        
        # Calcular pendientes
        numeros_pendientes = total_numeros - llamadas_realizadas
        
        return {
            "lista_id": lista_llamadas_id,
            "nombre_lista": lista.nombre,
            "total_numeros": total_numeros,
            "llamadas_realizadas": llamadas_realizadas,
            "llamadas_bloqueadas": llamadas_bloqueadas,
            "llamadas_exitosas": llamadas_exitosas,
            "numeros_pendientes": numeros_pendientes,
            "porcentaje_completado": round((llamadas_realizadas / total_numeros) * 100, 2) if total_numeros > 0 else 0,
            "tasa_exito": round((llamadas_exitosas / llamadas_realizadas) * 100, 2) if llamadas_realizadas > 0 else 0
        } 