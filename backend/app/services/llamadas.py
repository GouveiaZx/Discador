from typing import Dict, Any, Optional, Tuple, List, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import func, case, literal_column, desc
import logging
import uuid
import csv
import io

from app.models.llamada import Llamada
from app.models.usuario import Usuario
from app.services.asterisk import asterisk_service
from app.services.cli_generator import generar_cli

# Configurar logger
logger = logging.getLogger(__name__)

# Constantes para resultados validos
RESULTADOS_VALIDOS = ["contestada", "no_contesta", "buzon", "numero_invalido", "otro"]

# Estados validos para webhook
ESTADOS_WEBHOOK_VALIDOS = ["en_progreso", "conectada", "finalizada", "fallida", "cancelada"]

# Transiciones de estado validas (estado_actual -> [estados_permitidos])
TRANSICIONES_ESTADO_VALIDAS = {
    "pendiente": ["en_progreso", "cancelada", "fallida"],
    "en_progreso": ["conectada", "finalizada", "fallida", "cancelada"],
    "conectada": ["finalizada", "fallida", "cancelada"],
    "finalizada": [],  # Estado terminal, no se puede cambiar
    "fallida": [],     # Estado terminal, no se puede cambiar
    "cancelada": []    # Estado terminal, no se puede cambiar
}

# Columnas para exportacion CSV
COLUMNAS_CSV = [
    "llamada_id", "numero_destino", "estado", "resultado", 
    "fecha_asignacion", "fecha_conexion", "fecha_finalizacion", 
    "duracion_segundos", "usuario_email"
]

class LlamadasService:
    """
    Servicio para gestionar las operaciones relacionadas con llamadas.
    Encapsula la logica de negocio separandola de las rutas.
    """
    
    @staticmethod
    async def iniciar_llamada(
        db: Session,
        numero_destino: str,
        campana_id: int,
        prefijo_cli: Optional[str] = None,
        variables_adicionales: Optional[Dict[str, Any]] = None
    ) -> Tuple[Llamada, Dict[str, Any]]:
        """
        Inicia una llamada y registra la informacion en la base de datos.
        
        Args:
            db: Sesion de base de datos
            numero_destino: Numero al que se realizara la llamada
            campana_id: ID de la campana a la que pertenece la llamada
            prefijo_cli: Prefijo para el numero CLI (opcional)
            variables_adicionales: Variables adicionales para la llamada
            
        Returns:
            Tuple[Llamada, Dict]: Llamada creada y respuesta de Asterisk
            
        Raises:
            HTTPException: Si ocurre algun error durante el proceso
        """
        try:
            # Generar CLI para la llamada
            cli_generado = generar_cli(prefijo=prefijo_cli)
            
            # Crear registro de llamada en la base de datos
            nueva_llamada = Llamada(
                numero_destino=numero_destino,
                cli=cli_generado,
                id_campana=campana_id,
                fecha_inicio=datetime.now(),
                estado="en_progreso"
            )
            
            # Guardar en la base de datos
            db.add(nueva_llamada)
            db.commit()
            db.refresh(nueva_llamada)
            
            # Preparar variables para Asterisk
            variables_asterisk = variables_adicionales or {}
            variables_asterisk["llamada_id"] = nueva_llamada.id
            variables_asterisk["campana_id"] = campana_id
            
            # Iniciar llamada a traves de Asterisk AMI
            respuesta_asterisk = await asterisk_service.originar_llamada(
                numero_destino=numero_destino,
                cli=cli_generado,
                variables=variables_asterisk
            )
            
            return nueva_llamada, respuesta_asterisk
            
        except Exception as e:
            # En caso de error, revertir transaccion
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al iniciar llamada: {str(e)}")
    
    @staticmethod
    def procesar_tecla_presionada(
        db: Session,
        llamada_id: int,
        tecla: str = "1"
    ) -> Llamada:
        """
        Procesa el evento cuando un usuario presiona una tecla durante una llamada.
        
        Args:
            db: Sesion de base de datos
            llamada_id: ID de la llamada en la que se detecto la tecla
            tecla: Tecla DTMF detectada (por defecto "1")
            
        Returns:
            Llamada: Llamada actualizada
            
        Raises:
            HTTPException: Si la llamada no existe o no esta en el estado correcto
        """
        # Buscar la llamada en la base de datos
        llamada = db.query(Llamada).filter(Llamada.id == llamada_id).first()
        
        # Verificar si la llamada existe
        if not llamada:
            raise HTTPException(
                status_code=404, 
                detail=f"La llamada con ID {llamada_id} no existe"
            )
        
        # Verificar que el estado sea 'en_progreso'
        if llamada.estado != "en_progreso":
            raise HTTPException(
                status_code=400, 
                detail=f"La llamada no esta en estado 'en_progreso'. Estado actual: {llamada.estado}"
            )
        
        # Obtener fecha y hora actual
        ahora = datetime.now()
        
        # Actualizar la llamada
        llamada.estado = "conectada"
        llamada.fecha_conexion = ahora
        llamada.presiono_1 = tecla == "1"  # True si la tecla es "1"
        llamada.dtmf_detectado = tecla
        
        # Guardar cambios en la base de datos
        try:
            db.commit()
            return llamada
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Error al actualizar la llamada: {str(e)}"
            )
    
    @staticmethod
    def finalizar_llamada(
        db: Session,
        llamada_id: int,
        resultado: str,
        usuario: Usuario
    ) -> Llamada:
        """
        Finaliza una llamada en curso y registra su resultado.
        
        Args:
            db: Sesion de base de datos
            llamada_id: ID de la llamada a finalizar
            resultado: Resultado de la llamada (contestada, no_contesta, buzon, etc.)
            usuario: Usuario que esta finalizando la llamada
            
        Returns:
            Llamada: Llamada finalizada
            
        Raises:
            HTTPException: Si la llamada no existe, no pertenece al usuario o ya esta finalizada
        """
        # Verificar que el resultado sea valido
        if resultado not in RESULTADOS_VALIDOS:
            logger.warning(f"Intento de finalizar llamada con resultado invalido: {resultado}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El resultado '{resultado}' no es valido. Valores permitidos: {', '.join(RESULTADOS_VALIDOS)}"
            )
        
        # Buscar la llamada en la base de datos
        llamada = db.query(Llamada).filter(Llamada.id == llamada_id).first()
        
        # Verificar si la llamada existe
        if not llamada:
            logger.warning(f"Intento de finalizar llamada inexistente: {llamada_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La llamada con ID {llamada_id} no existe"
            )
        
        # Verificar que la llamada pertenezca al usuario (a menos que sea administrador)
        if not usuario.es_administrador and llamada.usuario_id != usuario.id:
            logger.warning(f"Usuario {usuario.email} intento finalizar llamada que no le pertenece: {llamada_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para finalizar esta llamada"
            )
        
        # Verificar que la llamada este en progreso o conectada
        estados_validos = ["en_progreso", "conectada"]
        if llamada.estado not in estados_validos:
            logger.warning(f"Intento de finalizar llamada en estado incorrecto: {llamada.estado}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La llamada no puede ser finalizada. Estado actual: {llamada.estado}"
            )
        
        # Obtener fecha y hora actual
        ahora = datetime.utcnow()
        
        # Actualizar la llamada
        llamada.estado = "finalizada"
        llamada.resultado = resultado
        llamada.fecha_finalizacion = ahora
        
        # Calcular duracion si tenemos fecha de inicio
        if llamada.fecha_inicio:
            duracion_segundos = int((ahora - llamada.fecha_inicio).total_seconds())
            llamada.duracion = duracion_segundos
        
        # Guardar cambios en la base de datos
        try:
            db.commit()
            logger.info(f"Llamada {llamada_id} finalizada con resultado: {resultado}")
            return llamada
        except Exception as e:
            db.rollback()
            logger.error(f"Error al finalizar llamada: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al finalizar la llamada: {str(e)}"
            )
    
    @staticmethod
    def obtener_estadisticas(db: Session) -> Dict[str, Any]:
        """
        Obtiene estadisticas agregadas sobre las llamadas en el sistema.
        
        Esta funcion realiza consultas optimizadas utilizando SQLAlchemy para obtener:
        - Total de llamadas
        - Llamadas por estado
        - Llamadas por resultado
        - Llamadas en progreso por usuario
        
        Args:
            db: Sesion de base de datos
            
        Returns:
            Dict[str, Any]: Diccionario con las estadisticas calculadas
            
        Raises:
            HTTPException: Si ocurre algun error durante la consulta
        """
        try:
            logger.info("Generando estadisticas de llamadas")
            resultado = {}
            
            # 1. Total de llamadas
            total_llamadas = db.query(func.count(Llamada.id)).scalar() or 0
            resultado["total_llamadas"] = total_llamadas
            
            # 2. Llamadas por estado
            estados_query = db.query(
                Llamada.estado, 
                func.count(Llamada.id).label('cantidad')
            ).group_by(Llamada.estado).all()
            
            # Convertir a diccionario
            por_estado = {
                "pendiente": 0,
                "en_progreso": 0,
                "conectada": 0,
                "finalizada": 0
            }
            
            for estado, cantidad in estados_query:
                if estado in por_estado:
                    por_estado[estado] = cantidad
            
            resultado["por_estado"] = por_estado
            
            # 3. Llamadas por resultado
            resultados_query = db.query(
                Llamada.resultado, 
                func.count(Llamada.id).label('cantidad')
            ).filter(Llamada.resultado.isnot(None)).group_by(Llamada.resultado).all()
            
            # Convertir a diccionario
            por_resultado = {resultado: 0 for resultado in RESULTADOS_VALIDOS}
            
            for resultado_llamada, cantidad in resultados_query:
                if resultado_llamada in por_resultado:
                    por_resultado[resultado_llamada] = cantidad
            
            resultado["por_resultado"] = por_resultado
            
            # 4. Llamadas en progreso por usuario
            # Usamos join para obtener directamente el email del usuario
            en_progreso_por_usuario_query = db.query(
                Usuario.email, 
                func.count(Llamada.id).label('cantidad')
            ).join(
                Usuario, 
                Llamada.usuario_id == Usuario.id
            ).filter(
                Llamada.estado == "en_progreso",
                Llamada.usuario_id.isnot(None)
            ).group_by(
                Usuario.email
            ).order_by(
                desc('cantidad')
            ).all()
            
            en_progreso_por_usuario = {email: cantidad for email, cantidad in en_progreso_por_usuario_query}
            resultado["en_progreso_por_usuario"] = en_progreso_por_usuario
            
            logger.info(f"Estadisticas generadas exitosamente: {len(en_progreso_por_usuario)} usuarios con llamadas en progreso")
            return resultado
            
        except Exception as e:
            logger.error(f"Error al obtener estadisticas: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener estadisticas: {str(e)}"
            )

    @staticmethod
    def exportar_llamadas_finalizadas_csv(db: Session) -> str:
        """
        Exporta todas las llamadas con estado 'finalizada' a un formato CSV.
        
        Esta funcion realiza las siguientes operaciones:
        1. Consulta todas las llamadas con estado 'finalizada'
        2. Hace join con la tabla de usuarios para obtener el email
        3. Formatea las fechas y calcula la duracion
        4. Genera un archivo CSV en memoria
        
        Args:
            db: Sesion de base de datos
        
        Returns:
            str: Contenido del CSV como string
            
        Raises:
            HTTPException: Si ocurre algun error durante la exportacion
        """
        try:
            logger.info("Iniciando exportacion de llamadas finalizadas a CSV")
            
            # Consultamos las llamadas finalizadas con join a usuarios
            llamadas_query = (
                db.query(
                    Llamada,
                    Usuario.email.label("usuario_email")
                )
                .outerjoin(
                    Usuario,
                    Llamada.usuario_id == Usuario.id
                )
                .filter(
                    Llamada.estado == "finalizada"
                )
                .order_by(
                    desc(Llamada.fecha_finalizacion)
                )
                .all()
            )
            
            # Creamos un buffer en memoria para el CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=COLUMNAS_CSV)
            
            # Escribimos la cabecera
            writer.writeheader()
            
            # Formato para fechas ISO
            formato_fecha = "%Y-%m-%dT%H:%M:%S"
            
            # Escribimos los datos
            for llamada, usuario_email in llamadas_query:
                # Formatear fechas o usar string vacio si es None
                fecha_asignacion = (
                    llamada.fecha_asignacion.strftime(formato_fecha) 
                    if llamada.fecha_asignacion else ""
                )
                fecha_conexion = (
                    llamada.fecha_conexion.strftime(formato_fecha) 
                    if llamada.fecha_conexion else ""
                )
                fecha_finalizacion = (
                    llamada.fecha_finalizacion.strftime(formato_fecha) 
                    if llamada.fecha_finalizacion else ""
                )
                
                # Calcular duracion en segundos
                duracion_segundos = llamada.duracion or 0
                
                # Escribir fila
                writer.writerow({
                    "llamada_id": llamada.id,
                    "numero_destino": llamada.numero_destino,
                    "estado": llamada.estado,
                    "resultado": llamada.resultado or "",
                    "fecha_asignacion": fecha_asignacion,
                    "fecha_conexion": fecha_conexion,
                    "fecha_finalizacion": fecha_finalizacion,
                    "duracion_segundos": duracion_segundos,
                    "usuario_email": usuario_email or ""
                })
            
            # Obtener el contenido como string
            csv_content = output.getvalue()
            
            # Cerramos el buffer
            output.close()
            
            logger.info(f"Exportacion CSV completada. {len(llamadas_query)} llamadas exportadas.")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error al exportar llamadas a CSV: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al exportar llamadas a CSV: {str(e)}"
            )

    @staticmethod
    def actualizar_estado_llamada_desde_webhook(
        db: Session,
        llamada_id: int,
        nuevo_estado: str
    ) -> Llamada:
        """
        Actualiza el estado de una llamada a partir de una notificacion webhook externa.
        
        Esta funcion:
        1. Verifica que la llamada exista
        2. Valida que la transicion de estado sea permitida
        3. Actualiza el estado sin modificar otros campos como resultado o fecha_finalizacion
        
        Args:
            db: Sesion de base de datos
            llamada_id: ID de la llamada a actualizar
            nuevo_estado: Nuevo estado para la llamada
            
        Returns:
            Llamada: Llamada actualizada
            
        Raises:
            HTTPException: Si la llamada no existe, el estado es invalido o la transicion no es permitida
        """
        try:
            # Verificar que el estado es valido
            if nuevo_estado not in ESTADOS_WEBHOOK_VALIDOS:
                logger.warning(f"Intento de actualizar llamada con estado invalido: {nuevo_estado}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"El estado '{nuevo_estado}' no es valido para webhook. Estados validos: {', '.join(ESTADOS_WEBHOOK_VALIDOS)}"
                )
            
            # Buscar la llamada en la base de datos
            llamada = db.query(Llamada).filter(Llamada.id == llamada_id).first()
            
            # Verificar si la llamada existe
            if not llamada:
                logger.warning(f"Intento de actualizar llamada inexistente via webhook: {llamada_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"La llamada con ID {llamada_id} no existe"
                )
            
            # Verificar que la transicion de estado sea valida
            estado_actual = llamada.estado
            estados_permitidos = TRANSICIONES_ESTADO_VALIDAS.get(estado_actual, [])
            
            if nuevo_estado not in estados_permitidos:
                logger.warning(
                    f"Transicion de estado invalida via webhook: {estado_actual} -> {nuevo_estado}. "
                    f"Transiciones permitidas: {estado_actual} -> {', '.join(estados_permitidos)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"No se puede cambiar el estado de '{estado_actual}' a '{nuevo_estado}'. "
                           f"Transiciones permitidas: {', '.join(estados_permitidos)}"
                )
            
            # Obtener fecha actual
            ahora = datetime.now()
            
            # Actualizar estado de la llamada
            llamada.estado = nuevo_estado
            
            # Si el estado es "finalizada" y no tiene fecha de finalizacion, agregarla
            if nuevo_estado == "finalizada" and not llamada.fecha_finalizacion:
                llamada.fecha_finalizacion = ahora
            
            # Si el estado es "conectada" y no tiene fecha de conexion, agregarla
            if nuevo_estado == "conectada" and not llamada.fecha_conexion:
                llamada.fecha_conexion = ahora
            
            # Guardar cambios en la base de datos
            try:
                db.commit()
                logger.info(f"Llamada {llamada_id} actualizada via webhook. Nuevo estado: {nuevo_estado}")
                return llamada
            except Exception as e:
                db.rollback()
                logger.error(f"Error al actualizar llamada via webhook: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al actualizar la llamada: {str(e)}"
                )
                
        except HTTPException:
            # Re-lanzar excepciones HTTP ya formateadas
            raise
        except Exception as e:
            # Manejar cualquier otro error
            logger.error(f"Error inesperado al procesar webhook de llamada: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inesperado al procesar la solicitud: {str(e)}"
            )

# Crear instancia del servicio para ser usada en las rutas
llamadas_service = LlamadasService() 