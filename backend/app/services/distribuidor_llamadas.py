from typing import Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.llamada import Llamada
from app.models.usuario import Usuario

# Configurar logger
logger = logging.getLogger(__name__)

class DistribuidorLlamadasService:
    """
    Servicio para gestionar la distribucion de llamadas pendientes a usuarios con permisos.
    Encapsula la logica de asignacion y control de llamadas en progreso.
    """
    
    @staticmethod
    def asignar_llamada(
        db: Session,
        usuario: Usuario
    ) -> Optional[Llamada]:
        """
        Asigna una llamada pendiente a un usuario con permisos validos.
        
        Si el usuario ya tiene una llamada en progreso, devuelve esa misma.
        Si no, busca la siguiente llamada pendiente y la asigna al usuario.
        
        Args:
            db: Sesion de base de datos
            usuario: Usuario al que se asignara la llamada
            
        Returns:
            Optional[Llamada]: Llamada asignada o None si no hay disponibles
            
        Raises:
            ValueError: Si el usuario no tiene permisos para gestionar llamadas
        """
        # Verificar que el usuario tenga permisos
        if not usuario.tiene_permiso_llamadas:
            logger.warning(f"Usuario {usuario.email} intento asignar llamada sin permisos")
            raise ValueError("El usuario no tiene permisos para gestionar llamadas")
        
        # Verificar si el usuario ya tiene una llamada en progreso
        llamada_existente = db.query(Llamada).filter(
            and_(
                Llamada.usuario_id == usuario.id,
                Llamada.estado == "en_progreso"
            )
        ).first()
        
        if llamada_existente:
            logger.info(f"Usuario {usuario.email} ya tiene una llamada en progreso (ID: {llamada_existente.id})")
            return llamada_existente
        
        # Buscar la siguiente llamada pendiente (ordenada por fecha de inicio)
        llamada_pendiente = db.query(Llamada).filter(
            Llamada.estado == "pendiente"
        ).order_by(
            Llamada.fecha_inicio
        ).first()
        
        if not llamada_pendiente:
            logger.info("No hay llamadas pendientes para asignar")
            return None
        
        # Obtener fecha y hora actual
        ahora = datetime.utcnow()
        
        try:
            # Actualizar la llamada con el usuario asignado
            llamada_pendiente.usuario_id = usuario.id
            llamada_pendiente.estado = "en_progreso"
            llamada_pendiente.fecha_asignacion = ahora
            
            # Guardar cambios en la base de datos
            db.commit()
            
            logger.info(f"Llamada ID {llamada_pendiente.id} asignada al usuario {usuario.email}")
            return llamada_pendiente
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error al asignar llamada: {str(e)}")
            raise

# Crear instancia del servicio para ser usada en las rutas
distribuidor_llamadas_service = DistribuidorLlamadasService() 