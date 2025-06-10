"""
Rutas para el servicio de discado integrado con blacklist, multiples listas y CLI aleatorio.
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
    numero_destino: str = Field(..., description="Numero de telefono a llamar")
    campana_id: Optional[int] = Field(None, description="ID de la campana")
    lista_llamadas_id: Optional[int] = Field(None, description="ID de la lista de llamadas")
    usuario_id: Optional[str] = Field(None, description="ID del usuario")
    cli_personalizado: Optional[str] = Field(None, description="CLI especifico a usar (opcional)")


class LlamarSiguienteListaRequest(BaseModel):
    """Schema para llamar al siguiente numero de una lista."""
    lista_llamadas_id: int = Field(..., description="ID de la lista de llamadas")
    campana_id: Optional[int] = Field(None, description="ID de la campana")
    usuario_id: Optional[str] = Field(None, description="ID del usuario")
    cli_personalizado: Optional[str] = Field(None, description="CLI especifico a usar (opcional)")


@router.post("/iniciar-llamada")
async def iniciar_llamada(
    request: IniciarLlamadaRequest,
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Inicia una llamada individual verificando blacklist automaticamente y usando CLI aleatorio.
    
    **Proceso automatico**:
    1. Valida el numero de telefono
    2. Verifica si esta en blacklist
    3. Genera CLI aleatorio (o usa CLI personalizado si se proporciona)
    4. Si no esta bloqueado, inicia la llamada via Asterisk
    5. Registra la llamada en base de datos
    
    **Nuevas caracteristicas**:
    - **CLI aleatorio**: Selecciona automaticamente un CLI de la base de datos
    - **CLI personalizado**: Opcion para especificar un CLI especifico
    - **Seguimiento de uso**: Registra cuantas veces se usa cada CLI
    
    **Respuestas posibles**:
    - `estado: "iniciado"` - Llamada iniciada exitosamente
    - `estado: "bloqueado"` - Numero en blacklist
    - `estado: "error"` - Numero invalido o error del sistema
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
    Llama al siguiente numero disponible de una lista especifica con CLI aleatorio.
    
    **Funcionalidad**:
    - Busca el proximo numero no llamado en la lista
    - Excluye automaticamente numeros en blacklist
    - Genera CLI aleatorio para la llamada
    - Inicia la llamada si hay numeros disponibles
    
    **Nuevas caracteristicas**:
    - **CLI aleatorio por llamada**: Cada llamada usa un CLI diferente
    - **Distribucion equitativa**: Prefiere CLIs menos usados
    - **CLI personalizado opcional**: Permite especificar CLI especifico
    
    **Util para**:
    - Discado automatico secuencial
    - Campanas basadas en listas especificas
    - Sistemas de discado predictivo con rotacion de CLI
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
    excluir_blacklist: bool = Query(True, description="Excluir numeros en blacklist"),
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Obtiene el proximo numero a llamar de una lista sin iniciar la llamada.
    
    **Uso**: Para sistemas que quieren revisar el proximo numero antes de llamar.
    
    **Respuesta**:
    - Datos del proximo numero disponible
    - `null` si no hay mas numeros en la lista
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
                "mensaje": f"No hay mas numeros disponibles en la lista {lista_id}",
                "proximo_numero": None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener proximo numero: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener proximo numero"
        )


@router.get("/estadisticas-lista/{lista_id}")
def obtener_estadisticas_lista(
    lista_id: int,
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Obtiene estadisticas detalladas de una lista de llamadas.
    
    **Metricas incluidas**:
    - Total de numeros en la lista
    - Llamadas realizadas vs pendientes  
    - Llamadas bloqueadas por blacklist
    - Llamadas exitosas
    - Porcentajes de completado y exito
    
    **Util para**: Dashboards y reportes de progreso de campanas.
    """
    try:
        service = DiscadoService(db)
        estadisticas = service.obtener_estadisticas_lista(lista_id)
        
        return estadisticas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener estadisticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener estadisticas"
        ) 