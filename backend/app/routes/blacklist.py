"""
Rutas para el manejo de blacklist/lista negra.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import obtener_sesion
from app.services.blacklist_service import BlacklistService
from app.schemas.blacklist import (
    BlacklistCreate,
    BlacklistUpdate,
    BlacklistResponse,
    BlacklistVerificationRequest,
    BlacklistVerificationResponse,
    BlacklistBulkAddRequest,
    BlacklistBulkAddResponse,
    BlacklistStatsResponse,
    BlacklistSearchRequest
)
from app.utils.logger import logger

router = APIRouter(prefix="/blacklist", tags=["Blacklist"])


@router.post("/verificar", response_model=BlacklistVerificationResponse)
def verificar_numero_blacklist(
    request: BlacklistVerificationRequest,
    db: Session = Depends(obtener_sesion)
) -> BlacklistVerificationResponse:
    """
    Verifica si un numero esta en la blacklist.
    
    **Uso principal**: Verificar antes de realizar una llamada si el numero esta bloqueado.
    
    **Respuesta**:
    - `en_blacklist`: True si el numero esta bloqueado
    - `motivo`: Razon del bloqueo si aplica
    - `fecha_bloqueo`: Cuando se agrego a la blacklist
    """
    try:
        service = BlacklistService(db)
        resultado = service.verificar_numero_blacklist(request.numero)
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error al verificar numero en blacklist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al verificar numero en blacklist"
        )


@router.post("/agregar", response_model=BlacklistResponse)
def agregar_numero_blacklist(
    numero_data: BlacklistCreate,
    db: Session = Depends(obtener_sesion)
) -> BlacklistResponse:
    """
    Agrega un numero a la blacklist.
    
    **Validaciones**:
    - Numero debe ser valido y en formato argentino
    - No puede estar ya en blacklist activa
    
    **Campos opcionales**:
    - `motivo`: Razon del bloqueo
    - `observaciones`: Notas adicionales
    - `creado_por`: Usuario que agrega el numero
    """
    try:
        service = BlacklistService(db)
        entrada = service.agregar_numero_blacklist(numero_data)
        
        return BlacklistResponse.from_orm(entrada)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al agregar numero a blacklist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al agregar numero a blacklist"
        )


@router.post("/agregar-bulk", response_model=BlacklistBulkAddResponse)
def agregar_numeros_bulk(
    request: BlacklistBulkAddRequest,
    db: Session = Depends(obtener_sesion)
) -> BlacklistBulkAddResponse:
    """
    Agrega multiples numeros a la blacklist de una vez.
    
    **Uso**: Importacion masiva de numeros bloqueados.
    
    **Caracteristicas**:
    - Procesa todos los numeros aunque algunos fallen
    - Reporta estadisticas detalladas del procesamiento
    - Numeros duplicados o invalidos se reportan pero no detienen el proceso
    """
    try:
        service = BlacklistService(db)
        resultado = service.agregar_numeros_bulk(
            request.numeros, 
            request.motivo, 
            request.creado_por
        )
        
        mensaje = (
            f"Procesamiento completado. "
            f"{resultado['numeros_agregados']} numeros agregados exitosamente."
        )
        
        if resultado['numeros_duplicados'] > 0:
            mensaje += f" {resultado['numeros_duplicados']} numeros ya estaban en blacklist."
        
        if resultado['numeros_invalidos'] > 0:
            mensaje += f" {resultado['numeros_invalidos']} numeros invalidos encontrados."
        
        return BlacklistBulkAddResponse(
            mensaje=mensaje,
            numeros_agregados=resultado['numeros_agregados'],
            numeros_duplicados=resultado['numeros_duplicados'],
            numeros_invalidos=resultado['numeros_invalidos'],
            errores=resultado['errores']
        )
        
    except Exception as e:
        logger.error(f"Error en agregado masivo a blacklist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno en agregado masivo a blacklist"
        )


@router.get("/", response_model=List[BlacklistResponse])
def listar_blacklist(
    skip: int = Query(0, description="Numero de registros a saltar"),
    limit: int = Query(100, description="Limite de registros a retornar"),
    apenas_ativos: bool = Query(True, description="Solo numeros activos"),
    db: Session = Depends(obtener_sesion)
) -> List[BlacklistResponse]:
    """
    Lista numeros en la blacklist.
    
    **Parametros**:
    - `skip`: Para paginacion
    - `limit`: Maximo de registros
    - `apenas_ativos`: Si mostrar solo numeros activos (no removidos)
    """
    try:
        service = BlacklistService(db)
        entradas = service.listar_blacklist(skip, limit, apenas_ativos)
        
        return [BlacklistResponse.from_orm(entrada) for entrada in entradas]
        
    except Exception as e:
        logger.error(f"Error al listar blacklist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al listar blacklist"
        )


@router.post("/buscar", response_model=List[BlacklistResponse])
def buscar_blacklist(
    criterios: BlacklistSearchRequest,
    skip: int = Query(0, description="Numero de registros a saltar"),
    limit: int = Query(100, description="Limite de registros a retornar"),
    db: Session = Depends(obtener_sesion)
) -> List[BlacklistResponse]:
    """
    Busca numeros en la blacklist con filtros avanzados.
    
    **Filtros disponibles**:
    - `numero`: Buscar por numero (parcial)
    - `motivo`: Buscar en motivos
    - `creado_por`: Filtrar por usuario
    - `activo`: Solo activos/inactivos
    - `fecha_desde` / `fecha_hasta`: Rango de fechas
    """
    try:
        service = BlacklistService(db)
        entradas = service.buscar_blacklist(criterios, skip, limit)
        
        return [BlacklistResponse.from_orm(entrada) for entrada in entradas]
        
    except Exception as e:
        logger.error(f"Error al buscar en blacklist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al buscar en blacklist"
        )


@router.get("/estadisticas", response_model=BlacklistStatsResponse)
def obtener_estadisticas_blacklist(
    db: Session = Depends(obtener_sesion)
) -> BlacklistStatsResponse:
    """
    Obtiene estadisticas de la blacklist.
    
    **Informacion incluida**:
    - Total de numeros en blacklist
    - Numeros activos vs inactivos
    - Bloqueos realizados hoy y este mes
    - Numero mas frecuentemente bloqueado
    """
    try:
        service = BlacklistService(db)
        estadisticas = service.obter_estatisticas()
        
        return estadisticas
        
    except Exception as e:
        logger.error(f"Error al obtener estadisticas de blacklist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener estadisticas"
        )


@router.put("/{numero_id}", response_model=BlacklistResponse)
def atualizar_numero_blacklist(
    numero_id: int,
    dados_atualizacao: BlacklistUpdate,
    db: Session = Depends(obtener_sesion)
) -> BlacklistResponse:
    """
    Actualiza datos de un numero en la blacklist.
    
    **Campos actualizables**:
    - `motivo`: Cambiar razon del bloqueo
    - `observaciones`: Actualizar notas
    - `activo`: Activar/desactivar bloqueo
    """
    try:
        service = BlacklistService(db)
        entrada = service.atualizar_numero_blacklist(numero_id, dados_atualizacao)
        
        return BlacklistResponse.from_orm(entrada)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar numero en blacklist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al actualizar numero en blacklist"
        )


@router.delete("/{numero_id}")
def remover_numero_blacklist(
    numero_id: int,
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Remueve un numero de la blacklist (marca como inactivo).
    
    **Nota**: No elimina fisicamente el registro, solo lo marca como inactivo
    para mantener historial de bloqueos.
    """
    try:
        service = BlacklistService(db)
        service.remover_numero_blacklist(numero_id)
        
        return {
            "mensaje": f"Numero removido de blacklist exitosamente",
            "numero_id": numero_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al remover numero de blacklist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al remover numero de blacklist"
        )


@router.delete("/numero/{numero}")
def remover_numero_por_telefone(
    numero: str,
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Remueve un numero de la blacklist usando el numero de telefono.
    
    **Mas conveniente** que usar ID cuando se conoce el numero exacto.
    """
    try:
        service = BlacklistService(db)
        service.remover_numero_por_telefone(numero)
        
        return {
            "mensaje": f"Numero {numero} removido de blacklist exitosamente",
            "numero": numero
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al remover numero por telefono: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al remover numero por telefono"
        ) 