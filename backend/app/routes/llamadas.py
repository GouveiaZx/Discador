from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Optional, Union
from pydantic import BaseModel, Field, UUID4
from datetime import datetime

from app.database import obtener_sesion
from app.models.llamada import Llamada
from app.models.usuario import Usuario
from app.services.llamadas import llamadas_service
from app.services.distribuidor_llamadas import distribuidor_llamadas_service
from app.auth.dependencies import get_current_user_simulado
from app.auth.webhook import verificar_api_key
from app.schemas.llamada import (
    LlamadaProximaResponse,
    LlamadaNoDisponibleResponse,
    ErrorResponse,
    FinalizarLlamadaRequest,
    FinalizarLlamadaResponse
)
from app.schemas.estadisticas import EstadisticasLlamadasResponse
from app.schemas.webhook import WebhookLlamadaRequest, WebhookLlamadaResponse, WebhookErrorResponse

router = APIRouter(tags=["Llamadas"])

# Esquema para la solicitud de iniciar llamada
class IniciarLlamadaRequest(BaseModel):
    numero_destino: str = Field(..., description="Número de teléfono al que se realizará la llamada")
    campana_id: int = Field(..., description="ID de la campaña a la que pertenece la llamada")
    prefijo_cli: Optional[str] = Field(None, description="Prefijo para el CLI (opcional)")
    variables_adicionales: Optional[dict] = Field(None, description="Variables adicionales para la llamada")
    
    class Config:
        schema_extra = {
            "example": {
                "numero_destino": "666123456",
                "campana_id": 1,
                "prefijo_cli": "91",
                "variables_adicionales": {"lead_id": 123, "intento": 1}
            }
        }

# Esquema para la respuesta de iniciar llamada
class IniciarLlamadaResponse(BaseModel):
    mensaje: str = Field(..., description="Mensaje informativo sobre el resultado de la operación")
    estado: str = Field(..., description="Estado de la llamada")
    llamada_id: int = Field(..., description="ID de la llamada registrada en la base de datos")
    cli_utilizado: str = Field(..., description="Número CLI utilizado para la llamada saliente")
    detalles: Optional[dict] = Field(None, description="Detalles adicionales de la operación")

# Esquema para la solicitud de presione1
class Presione1Request(BaseModel):
    llamada_id: int = Field(..., description="ID de la llamada en la que se detectó la tecla 1")
    
    class Config:
        schema_extra = {
            "example": {
                "llamada_id": 123
            }
        }

# Esquema para la respuesta de presione1
class Presione1Response(BaseModel):
    mensaje: str = Field(..., description="Mensaje informativo sobre el resultado de la operación")
    estado: str = Field(..., description="Estado de la llamada después de procesar el evento")
    llamada_id: int = Field(..., description="ID de la llamada procesada")
    detalles: Optional[dict] = Field(None, description="Detalles adicionales de la operación")

@router.post("/iniciar", response_model=IniciarLlamadaResponse, summary="Iniciar una llamada")
async def iniciar_llamada(
    datos: IniciarLlamadaRequest,
    db: Session = Depends(obtener_sesion)
):
    """
    Inicia una llamada usando Asterisk AMI.
    
    Esta ruta realiza las siguientes acciones:
    1. Genera un número CLI para la llamada saliente
    2. Registra la llamada en la base de datos con estado "en_progreso"
    3. Inicia la llamada a través de Asterisk AMI (simulado por ahora)
    4. Devuelve los detalles de la llamada iniciada
    
    Returns:
        IniciarLlamadaResponse: Detalles de la llamada iniciada
    """
    try:
        # Usar el servicio para iniciar la llamada
        nueva_llamada, respuesta_asterisk = await llamadas_service.iniciar_llamada(
            db=db,
            numero_destino=datos.numero_destino,
            campana_id=datos.campana_id,
            prefijo_cli=datos.prefijo_cli,
            variables_adicionales=datos.variables_adicionales
        )
        
        # Construir respuesta
        return IniciarLlamadaResponse(
            mensaje="Llamada iniciada correctamente",
            estado=nueva_llamada.estado,
            llamada_id=nueva_llamada.id,
            cli_utilizado=nueva_llamada.cli,
            detalles={
                "asterisk_unique_id": respuesta_asterisk.get("UniqueID"),
                "timestamp": nueva_llamada.fecha_inicio.isoformat()
            }
        )
    
    except HTTPException:
        # Re-lanzar excepciones HTTP ya formateadas
        raise
        
    except Exception as e:
        # Manejar cualquier otro error
        raise HTTPException(status_code=500, detail=f"Error al iniciar llamada: {str(e)}")

@router.post("/presione1", response_model=Presione1Response, summary="Procesar evento de tecla 1 presionada")
async def procesar_presione1(
    datos: Presione1Request,
    db: Session = Depends(obtener_sesion)
):
    """
    Procesa el evento cuando un usuario presiona la tecla 1 durante una llamada.
    
    Esta ruta realiza las siguientes acciones:
    1. Verifica si la llamada existe y está en el estado correcto
    2. Actualiza el estado de la llamada a "conectada"
    3. Registra la fecha y hora de la conexión
    4. Marca que el usuario presionó la tecla 1
    
    Returns:
        Presione1Response: Resultado del procesamiento
    """
    try:
        # Usar el servicio para procesar la tecla presionada
        llamada_actualizada = llamadas_service.procesar_tecla_presionada(
            db=db,
            llamada_id=datos.llamada_id,
            tecla="1"
        )
        
        # Construir respuesta
        return Presione1Response(
            mensaje="Tecla 1 detectada correctamente",
            estado=llamada_actualizada.estado,
            llamada_id=llamada_actualizada.id,
            detalles={
                "fecha_conexion": llamada_actualizada.fecha_conexion.isoformat(),
                "dtmf": "1"
            }
        )
        
    except HTTPException:
        # Re-lanzar excepciones HTTP ya formateadas
        raise
    
    except Exception as e:
        # Manejar cualquier otro error
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar tecla 1: {str(e)}"
        )

@router.get(
    "/proxima", 
    summary="Obtener la próxima llamada pendiente",
    response_model=Union[LlamadaProximaResponse, LlamadaNoDisponibleResponse],
    responses={
        403: {"model": ErrorResponse, "description": "Permiso denegado"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)
async def obtener_proxima_llamada(
    usuario_actual: Usuario = Depends(get_current_user_simulado),
    db: Session = Depends(obtener_sesion)
):
    """
    Obtiene la próxima llamada pendiente y la asigna al usuario actual.
    
    Esta ruta realiza las siguientes acciones:
    1. Verifica que el usuario tenga permisos (administrador o integrador)
    2. Si el usuario ya tiene una llamada en progreso, devuelve esa misma
    3. Busca la próxima llamada pendiente y la asigna al usuario
    4. Devuelve los detalles de la llamada asignada
    
    Returns:
        Union[LlamadaProximaResponse, LlamadaNoDisponibleResponse]: Detalles de la llamada asignada 
        o mensaje indicando que no hay llamadas disponibles
    """
    try:
        # Verificar que el usuario tenga permisos
        if not usuario_actual.tiene_permiso_llamadas:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "No tienes permisos para acceder a este recurso"}
            )
        
        # Asignar la próxima llamada pendiente al usuario
        llamada = distribuidor_llamadas_service.asignar_llamada(db, usuario_actual)
        
        # Si no hay llamadas pendientes
        if not llamada:
            return LlamadaNoDisponibleResponse(
                mensaje="No hay llamadas pendientes para asignar"
            )
        
        # Devolver detalles de la llamada asignada
        return LlamadaProximaResponse(
            mensaje="Llamada asignada correctamente",
            llamada_id=llamada.id,
            numero_destino=llamada.numero_destino,
            estado=llamada.estado
        )
    
    except ValueError as e:
        # Error de validación (usuario sin permisos)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": str(e)}
        )
    
    except HTTPException:
        # Re-lanzar excepciones HTTP ya formateadas
        raise
    
    except Exception as e:
        # Manejar cualquier otro error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={"error": f"Error al asignar llamada: {str(e)}"}
        )

@router.post(
    "/finalizar",
    summary="Finalizar una llamada y registrar su resultado",
    response_model=FinalizarLlamadaResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Solicitud inválida"},
        403: {"model": ErrorResponse, "description": "Permiso denegado"},
        404: {"model": ErrorResponse, "description": "Llamada no encontrada"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)
async def finalizar_llamada(
    datos: FinalizarLlamadaRequest,
    usuario_actual: Usuario = Depends(get_current_user_simulado),
    db: Session = Depends(obtener_sesion)
):
    """
    Finaliza una llamada en curso y registra su resultado.
    
    Esta ruta realiza las siguientes acciones:
    1. Verifica que el usuario tenga permisos (administrador o integrador)
    2. Verifica que la llamada exista y pertenezca al usuario (a menos que sea administrador)
    3. Verifica que el resultado sea válido
    4. Actualiza el estado de la llamada a "finalizada"
    5. Registra el resultado y la fecha de finalización
    
    Returns:
        FinalizarLlamadaResponse: Detalles de la llamada finalizada
    """
    try:
        # Verificar que el usuario tenga permisos
        if not usuario_actual.tiene_permiso_llamadas:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "No tienes permisos para finalizar llamadas"}
            )
        
        # Finalizar la llamada
        llamada_finalizada = llamadas_service.finalizar_llamada(
            db=db,
            llamada_id=datos.llamada_id,
            resultado=datos.resultado,
            usuario=usuario_actual
        )
        
        # Devolver detalles de la llamada finalizada
        return FinalizarLlamadaResponse(
            mensaje="Llamada finalizada correctamente",
            llamada_id=llamada_finalizada.id,
            estado=llamada_finalizada.estado,
            resultado=llamada_finalizada.resultado
        )
    
    except ValueError as e:
        # Error de validación
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )
    
    except HTTPException:
        # Re-lanzar excepciones HTTP ya formateadas
        raise
    
    except Exception as e:
        # Manejar cualquier otro error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Error al finalizar llamada: {str(e)}"}
        )

@router.get(
    "/estadisticas",
    summary="Obtener estadísticas agregadas de llamadas",
    response_model=EstadisticasLlamadasResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Permiso denegado"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)
async def obtener_estadisticas_llamadas(
    usuario_actual: Usuario = Depends(get_current_user_simulado),
    db: Session = Depends(obtener_sesion)
):
    """
    Obtiene estadísticas agregadas sobre las llamadas realizadas por el sistema.
    
    Esta ruta realiza las siguientes acciones:
    1. Verifica que el usuario tenga permisos de administrador
    2. Calcula las métricas agregadas utilizando consultas optimizadas:
       - Total de llamadas en el sistema
       - Llamadas agrupadas por estado
       - Llamadas agrupadas por resultado
       - Llamadas en progreso agrupadas por usuario
    
    Esta ruta está optimizada para grandes volúmenes de datos y utiliza
    consultas agregadas directamente en la base de datos.
    
    Returns:
        EstadisticasLlamadasResponse: Métricas agregadas de llamadas
    """
    try:
        # Verificar que el usuario sea administrador
        if not usuario_actual.es_administrador:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "Solo los administradores pueden acceder a las estadísticas"}
            )
        
        # Obtener las estadísticas
        estadisticas = llamadas_service.obtener_estadisticas(db)
        
        # Devolver las estadísticas formateadas
        return EstadisticasLlamadasResponse(
            total_llamadas=estadisticas["total_llamadas"],
            por_estado=estadisticas["por_estado"],
            por_resultado=estadisticas["por_resultado"],
            en_progreso_por_usuario=estadisticas["en_progreso_por_usuario"]
        )
    
    except HTTPException:
        # Re-lanzar excepciones HTTP ya formateadas
        raise
    
    except Exception as e:
        # Manejar cualquier otro error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Error al obtener estadísticas: {str(e)}"}
        )

@router.get(
    "/exportar",
    summary="Exportar llamadas finalizadas en formato CSV",
    response_description="Archivo CSV con todas las llamadas finalizadas",
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "CSV con las llamadas finalizadas"
        },
        403: {"model": ErrorResponse, "description": "Permiso denegado"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)
async def exportar_llamadas_finalizadas(
    usuario_actual: Usuario = Depends(get_current_user_simulado),
    db: Session = Depends(obtener_sesion)
):
    """
    Exporta todas las llamadas con estado 'finalizada' a un archivo CSV descargable.
    
    Esta ruta está restringida a usuarios con rol de administrador y genera un archivo
    CSV con las siguientes columnas:
    
    - llamada_id: Identificador único de la llamada
    - numero_destino: Número de teléfono al que se realizó la llamada
    - estado: Estado de la llamada (siempre 'finalizada' en este caso)
    - resultado: Resultado de la llamada (contestada, no_contesta, etc.)
    - fecha_asignacion: Fecha y hora en que se asignó la llamada a un usuario
    - fecha_conexion: Fecha y hora en que se estableció la conexión
    - fecha_finalizacion: Fecha y hora en que finalizó la llamada
    - duracion_segundos: Duración total de la llamada en segundos
    - usuario_email: Correo electrónico del usuario que atendió la llamada
    
    Las fechas se formatean en formato ISO (YYYY-MM-DDTHH:MM:SS).
    
    Returns:
        Response: Archivo CSV para descargar
    """
    try:
        # Verificar que el usuario sea administrador
        if not usuario_actual.es_administrador:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "Solo los administradores pueden exportar llamadas"}
            )
        
        # Obtener el contenido CSV
        csv_content = llamadas_service.exportar_llamadas_finalizadas_csv(db)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"llamadas_finalizadas_{timestamp}.csv"
        
        # Devolver el archivo CSV como respuesta descargable
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        # Re-lanzar excepciones HTTP ya formateadas
        raise
    
    except Exception as e:
        # Manejar cualquier otro error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Error al exportar llamadas: {str(e)}"}
        )

@router.post(
    "/webhook",
    summary="Actualizar estado de llamada desde sistema externo",
    description=(
        "Permite a sistemas externos (ej. central telefónica) notificar cambios de estado en llamadas. "
        "Requiere autenticación mediante API Key en el encabezado X-API-Key. "
        "La API Key debe configurarse en la variable de entorno WEBHOOK_API_KEY."
    ),
    response_model=WebhookLlamadaResponse,
    responses={
        200: {"model": WebhookLlamadaResponse, "description": "Estado actualizado correctamente"},
        403: {"model": WebhookErrorResponse, "description": "API Key inválida"},
        404: {"model": WebhookErrorResponse, "description": "Llamada no encontrada"},
        422: {"model": WebhookErrorResponse, "description": "Estado inválido o transición no permitida"},
        500: {"model": WebhookErrorResponse, "description": "Error interno del servidor"}
    }
)
async def actualizar_estado_via_webhook(
    datos: WebhookLlamadaRequest,
    db: Session = Depends(obtener_sesion),
    _: None = Depends(verificar_api_key)
):
    """
    Recibe notificaciones de sistemas externos para actualizar el estado de una llamada.
    
    Esta ruta:
    1. Verifica la autenticación mediante API Key (header X-API-Key)
    2. Valida que la llamada exista y el estado sea válido
    3. Actualiza el estado respetando las transiciones permitidas
    
    Estados válidos:
    - "en_progreso": Llamada en curso
    - "conectada": Usuario atendió la llamada
    - "finalizada": Llamada terminada correctamente
    - "fallida": Error técnico o problema en la llamada
    - "cancelada": Llamada cancelada por el sistema o usuario
    
    Transiciones no permitidas:
    - No se puede cambiar estado de llamadas ya finalizadas, fallidas o canceladas
    - No se puede regresar de un estado avanzado a uno anterior
    
    Ejemplo de uso:
    ```bash
    curl -X 'POST' \\
      'https://api.example.com/api/v1/llamadas/webhook' \\
      -H 'X-API-Key: api_key_value' \\
      -H 'Content-Type: application/json' \\
      -d '{
        "llamada_id": 123,
        "nuevo_estado": "fallida"
      }'
    ```
    
    Returns:
        WebhookLlamadaResponse: Información sobre la actualización del estado
    """
    try:
        # Actualizar el estado de la llamada
        llamada_actualizada = llamadas_service.actualizar_estado_llamada_desde_webhook(
            db=db,
            llamada_id=datos.llamada_id,
            nuevo_estado=datos.nuevo_estado
        )
        
        # Devolver respuesta
        return WebhookLlamadaResponse(
            mensaje="Estado de llamada actualizado",
            estado_actual=llamada_actualizada.estado
        )
    
    except HTTPException as e:
        # Re-formatear errores HTTP para usar nuestro formato de respuesta
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.detail}
        )
        
    except Exception as e:
        # Manejar cualquier otro error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Error inesperado: {str(e)}"}
        ) 