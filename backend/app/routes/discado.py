"""
Rutas para el servicio de discado integrado con blacklist, múltiples listas y CLI aleatorio.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import obtener_sesion
from app.services.discado_service import DiscadoService
from app.utils.logger import logger

router = APIRouter(prefix="/discado", tags=["Discado"])


class IniciarLlamadaRequest(BaseModel):
    """Schema para iniciar una llamada."""
    numero_destino: str = Field(..., description="Número de teléfono a llamar")
    campana_id: Optional[int] = Field(None, description="ID de la campaña")
    lista_llamadas_id: Optional[int] = Field(None, description="ID de la lista de llamadas")
    usuario_id: Optional[str] = Field(None, description="ID del usuario")
    cli_personalizado: Optional[str] = Field(None, description="CLI específico a usar (opcional)")


class LlamarSiguienteListaRequest(BaseModel):
    """Schema para llamar al siguiente número de una lista."""
    lista_llamadas_id: int = Field(..., description="ID de la lista de llamadas")
    campana_id: Optional[int] = Field(None, description="ID de la campaña")
    usuario_id: Optional[str] = Field(None, description="ID del usuario")
    cli_personalizado: Optional[str] = Field(None, description="CLI específico a usar (opcional)")


@router.post("/iniciar-llamada")
async def iniciar_llamada(
    request: IniciarLlamadaRequest,
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Inicia una llamada individual verificando blacklist automáticamente y usando CLI aleatorio.
    
    **Proceso automático**:
    1. Valida el número de teléfono
    2. Verifica si está en blacklist
    3. Genera CLI aleatorio (o usa CLI personalizado si se proporciona)
    4. Si no está bloqueado, inicia la llamada via Asterisk
    5. Registra la llamada en base de datos
    
    **Nuevas características**:
    - **CLI aleatorio**: Selecciona automáticamente un CLI de la base de datos
    - **CLI personalizado**: Opción para especificar un CLI específico
    - **Seguimiento de uso**: Registra cuántas veces se usa cada CLI
    
    **Respuestas posibles**:
    - `estado: "iniciado"` - Llamada iniciada exitosamente
    - `estado: "bloqueado"` - Número en blacklist
    - `estado: "error"` - Número inválido o error del sistema
    """
    try:
        service = DiscadoService(db)
        resultado = await service.iniciar_llamada(
            numero_destino=request.numero_destino,
            campana_id=request.campana_id,
            lista_llamadas_id=request.lista_llamadas_id,
            usuario_id=request.usuario_id,
            cli_personalizado=request.cli_personalizado
        )
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al iniciar llamada: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al iniciar llamada"
        )


@router.post("/llamar-siguiente-lista")
async def llamar_siguiente_de_lista(
    request: LlamarSiguienteListaRequest,
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Llama al siguiente número disponible de una lista específica con CLI aleatorio.
    
    **Funcionalidad**:
    - Busca el próximo número no llamado en la lista
    - Excluye automáticamente números en blacklist
    - Genera CLI aleatorio para la llamada
    - Inicia la llamada si hay números disponibles
    
    **Nuevas características**:
    - **CLI aleatorio por llamada**: Cada llamada usa un CLI diferente
    - **Distribución equitativa**: Prefiere CLIs menos usados
    - **CLI personalizado opcional**: Permite especificar CLI específico
    
    **Útil para**:
    - Discado automático secuencial
    - Campañas basadas en listas específicas
    - Sistemas de discado predictivo con rotación de CLI
    """
    try:
        service = DiscadoService(db)
        resultado = await service.llamar_siguiente_de_lista(
            lista_llamadas_id=request.lista_llamadas_id,
            campana_id=request.campana_id,
            usuario_id=request.usuario_id
        )
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al llamar siguiente de lista: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al llamar siguiente de lista"
        )


@router.get("/proximo-numero-lista/{lista_id}")
def obtener_proximo_numero_lista(
    lista_id: int,
    usuario_id: Optional[str] = Query(None, description="ID del usuario"),
    excluir_blacklist: bool = Query(True, description="Excluir números en blacklist"),
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Obtiene el próximo número a llamar de una lista sin iniciar la llamada.
    
    **Uso**: Para sistemas que quieren revisar el próximo número antes de llamar.
    
    **Respuesta**:
    - Datos del próximo número disponible
    - `null` si no hay más números en la lista
    """
    try:
        service = DiscadoService(db)
        proximo = service.obtener_proxima_llamada_lista(
            lista_llamadas_id=lista_id,
            usuario_id=usuario_id,
            excluir_blacklist=excluir_blacklist
        )
        
        if proximo:
            return {
                "estado": "disponible",
                "proximo_numero": proximo
            }
        else:
            return {
                "estado": "sin_numeros",
                "mensaje": f"No hay más números disponibles en la lista {lista_id}",
                "proximo_numero": None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener próximo número: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener próximo número"
        )


@router.get("/estadisticas-lista/{lista_id}")
def obtener_estadisticas_lista(
    lista_id: int,
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Obtiene estadísticas detalladas de una lista de llamadas.
    
    **Métricas incluidas**:
    - Total de números en la lista
    - Llamadas realizadas vs pendientes  
    - Llamadas bloqueadas por blacklist
    - Llamadas exitosas
    - Porcentajes de completado y éxito
    
    **Útil para**: Dashboards y reportes de progreso de campañas.
    """
    try:
        service = DiscadoService(db)
        estadisticas = service.obtener_estadisticas_lista(lista_id)
        
        return estadisticas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener estadísticas"
        ) 