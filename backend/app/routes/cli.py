"""
Rutas para el manejo de CLIs (Caller Line Identification).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import obtener_sesion
from app.services.cli_service import CliService
from app.schemas.cli import (
    CliCreate,
    CliUpdate,
    CliResponse,
    CliBulkAddRequest,
    CliBulkAddResponse,
    CliStatsResponse,
    CliRandomRequest,
    CliRandomResponse
)
from app.utils.logger import logger

router = APIRouter(prefix="/cli", tags=["CLI Management"])


@router.get("/generar-aleatorio", response_model=CliRandomResponse)
def generar_cli_aleatorio(
    excluir_cli: Optional[str] = Query(None, description="CLI a excluir de la seleccion"),
    solo_poco_usados: bool = Query(False, description="Preferir CLIs menos usados"),
    db: Session = Depends(obtener_sesion)
) -> CliRandomResponse:
    """
    Genera un CLI aleatorio de los CLIs activos disponibles.
    
    **Uso principal**: Obtener un CLI para una nueva llamada.
    
    **Parametros**:
    - `excluir_cli`: CLI especifico a excluir de la seleccion
    - `solo_poco_usados`: Si debe preferir CLIs que han sido menos utilizados
    
    **Respuesta**:
    - `cli_seleccionado`: El CLI seleccionado aleatoriamente
    - `veces_usado`: Cuantas veces se ha usado este CLI
    """
    try:
        service = CliService(db)
        resultado = service.generar_cli_aleatorio(excluir_cli, solo_poco_usados)
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar CLI aleatorio: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al generar CLI aleatorio"
        )


@router.post("/agregar", response_model=CliResponse)
def agregar_cli(
    cli_data: CliCreate,
    db: Session = Depends(obtener_sesion)
) -> CliResponse:
    """
    Agrega un nuevo CLI a la base de datos.
    
    **Validaciones**:
    - Numero debe ser valido y en formato argentino
    - No puede estar ya registrado como activo
    
    **Campos opcionales**:
    - `descripcion`: Descripcion del CLI
    - `notas`: Notas adicionales sobre el CLI
    """
    try:
        service = CliService(db)
        cli = service.agregar_cli(cli_data)
        
        return CliResponse.from_orm(cli)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al agregar CLI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al agregar CLI"
        )


@router.post("/agregar-bulk", response_model=CliBulkAddResponse)
def agregar_clis_bulk(
    request: CliBulkAddRequest,
    db: Session = Depends(obtener_sesion)
) -> CliBulkAddResponse:
    """
    Agrega multiples CLIs de una vez.
    
    **Uso**: Importacion masiva de CLIs permitidos.
    
    **Caracteristicas**:
    - Procesa todos los numeros aunque algunos fallen
    - Reporta estadisticas detalladas del procesamiento
    - CLIs duplicados o invalidos se reportan pero no detienen el proceso
    """
    try:
        service = CliService(db)
        resultado = service.agregar_clis_bulk(request.numeros, request.descripcion)
        
        mensaje = (
            f"Procesamiento completado. "
            f"{resultado['clis_agregados']} CLIs agregados exitosamente."
        )
        
        if resultado['clis_duplicados'] > 0:
            mensaje += f" {resultado['clis_duplicados']} CLIs ya existian."
        
        if resultado['clis_invalidos'] > 0:
            mensaje += f" {resultado['clis_invalidos']} CLIs invalidos encontrados."
        
        return CliBulkAddResponse(
            mensaje=mensaje,
            clis_agregados=resultado['clis_agregados'],
            clis_duplicados=resultado['clis_duplicados'],
            clis_invalidos=resultado['clis_invalidos'],
            errores=resultado['errores']
        )
        
    except Exception as e:
        logger.error(f"Error en agregado masivo de CLIs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno en agregado masivo de CLIs"
        )


@router.get("/", response_model=List[CliResponse])
def listar_clis(
    skip: int = Query(0, description="Numero de registros a saltar"),
    limit: int = Query(100, description="Limite de registros a retornar"),
    apenas_ativos: bool = Query(True, description="Solo CLIs activos"),
    db: Session = Depends(obtener_sesion)
) -> List[CliResponse]:
    """
    Lista CLIs registrados.
    
    **Parametros**:
    - `skip`: Para paginacion
    - `limit`: Maximo de registros
    - `apenas_ativos`: Si mostrar solo CLIs activos (no removidos)
    """
    try:
        service = CliService(db)
        clis = service.listar_clis(skip, limit, apenas_ativos)
        
        return [CliResponse.from_orm(cli) for cli in clis]
        
    except Exception as e:
        logger.error(f"Error al listar CLIs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al listar CLIs"
        )


@router.get("/estadisticas", response_model=CliStatsResponse)
def obtener_estadisticas_cli(
    db: Session = Depends(obtener_sesion)
) -> CliStatsResponse:
    """
    Obtiene estadisticas de los CLIs.
    
    **Informacion incluida**:
    - Total de CLIs registrados
    - CLIs activos vs inactivos
    - CLI mas utilizado
    - Usos realizados hoy y este mes
    """
    try:
        service = CliService(db)
        estadisticas = service.obter_estatisticas()
        
        return estadisticas
        
    except Exception as e:
        logger.error(f"Error al obtener estadisticas de CLIs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener estadisticas"
        )


@router.put("/{cli_id}", response_model=CliResponse)
def atualizar_cli(
    cli_id: int,
    dados_atualizacao: CliUpdate,
    db: Session = Depends(obtener_sesion)
) -> CliResponse:
    """
    Actualiza datos de un CLI.
    
    **Campos actualizables**:
    - `descripcion`: Cambiar descripcion del CLI
    - `notas`: Actualizar notas
    - `activo`: Activar/desactivar CLI
    """
    try:
        service = CliService(db)
        cli = service.atualizar_cli(cli_id, dados_atualizacao)
        
        return CliResponse.from_orm(cli)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar CLI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al actualizar CLI"
        )


@router.delete("/{cli_id}")
def remover_cli(
    cli_id: int,
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Remueve un CLI (marca como inactivo).
    
    **Nota**: No elimina fisicamente el registro, solo lo marca como inactivo
    para mantener historial de uso.
    """
    try:
        service = CliService(db)
        service.remover_cli(cli_id)
        
        return {
            "mensaje": "CLI removido exitosamente",
            "cli_id": cli_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al remover CLI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al remover CLI"
        ) 