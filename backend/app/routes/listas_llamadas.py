"""
Rutas para el manejo de listas de llamadas.
"""

from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtener_sesion
from app.services.lista_llamadas_service import ListaLlamadasService
from app.models.lista_llamadas import ListaLlamadas
from app.schemas.lista_llamadas import (
    ListaLlamadasResponse,
    ListaLlamadasDetailResponse,
    UploadArchivoResponse,
    ListaLlamadasCreate,
    ListaLlamadasUpdate,
    NumeroLlamadaResponse
)
from app.utils.logger import logger

router = APIRouter(prefix="/listas-llamadas", tags=["Listas de Llamadas"])


@router.post("/upload", response_model=UploadArchivoResponse)
async def upload_archivo_numeros(
    archivo: UploadFile = File(..., description="Archivo CSV o TXT con números de teléfono"),
    nombre_lista: str = Form(..., description="Nombre para la lista de llamadas"),
    descripcion: Optional[str] = Form(None, description="Descripción opcional de la lista"),
    db: Session = Depends(obtener_sesion)
) -> UploadArchivoResponse:
    """
    Sube un archivo CSV o TXT con números de teléfono y crea una nueva lista de llamadas.
    
    **Formato del archivo:**
    - CSV: Primera columna debe contener los números (puede tener header)
    - TXT: Un número por línea
    
    **Formatos de números aceptados:**
    - +54 9 11 1234-5678
    - 011 1234-5678  
    - 11 1234 5678
    - 1112345678
    
    **Validaciones aplicadas:**
    - Números duplicados son removidos
    - Números inválidos son reportados pero no guardados
    - Solo números argentinos son procesados
    """
    logger.info(f"Inicio upload de archivo: {archivo.filename}, Lista: {nombre_lista}")
    
    # Validar tamaño del archivo (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if archivo.size and archivo.size > max_size:
        raise HTTPException(
            status_code=413,
            detail="El archivo es demasiado grande. Tamaño máximo: 10MB"
        )
    
    try:
        service = ListaLlamadasService(db)
        resultado = await service.procesar_archivo(archivo, nombre_lista, descripcion)
        
        mensaje_resultado = (
            f"Archivo procesado exitosamente. "
            f"{resultado['numeros_validos']} números válidos guardados "
            f"de {resultado['total_numeros_archivo']} líneas procesadas."
        )
        
        if resultado['numeros_invalidos'] > 0:
            mensaje_resultado += f" {resultado['numeros_invalidos']} números inválidos encontrados."
        
        if resultado['numeros_duplicados'] > 0:
            mensaje_resultado += f" {resultado['numeros_duplicados']} números duplicados removidos."
        
        return UploadArchivoResponse(
            mensaje=mensaje_resultado,
            lista_id=resultado['lista_id'],
            nombre_lista=resultado['nombre_lista'],
            archivo_original=resultado['archivo_original'],
            total_numeros_archivo=resultado['total_numeros_archivo'],
            numeros_validos=resultado['numeros_validos'],
            numeros_invalidos=resultado['numeros_invalidos'],
            numeros_duplicados=resultado['numeros_duplicados'],
            errores=resultado['errores']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al procesar el archivo"
        )


@router.get("/", response_model=List[ListaLlamadasResponse])
def listar_listas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(obtener_sesion)
) -> List[ListaLlamadasResponse]:
    """
    Lista todas las listas de llamadas disponibles.
    
    **Parámetros:**
    - skip: Número de registros a saltar (para paginación)
    - limit: Número máximo de registros a retornar
    """
    try:
        service = ListaLlamadasService(db)
        listas = service.listar_listas(skip=skip, limit=limit)
        
        return [ListaLlamadasResponse.from_orm(lista) for lista in listas]
        
    except Exception as e:
        logger.error(f"Error al listar listas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener las listas"
        )


@router.get("/{lista_id}", response_model=ListaLlamadasDetailResponse)
def obtener_lista(
    lista_id: int,
    incluir_numeros: bool = False,
    db: Session = Depends(obtener_sesion)
) -> ListaLlamadasDetailResponse:
    """
    Obtiene los detalles de una lista de llamadas específica.
    
    **Parámetros:**
    - lista_id: ID de la lista a obtener
    - incluir_numeros: Si incluir la lista completa de números (puede ser lenta para listas grandes)
    """
    try:
        service = ListaLlamadasService(db)
        lista = service.obtener_lista(lista_id)
        
        # Convertir a schema response
        lista_response = ListaLlamadasDetailResponse.from_orm(lista)
        
        # Incluir números si se solicita (cuidado con listas grandes)
        if incluir_numeros:
            lista_response.numeros = [
                NumeroLlamadaResponse.from_orm(numero) 
                for numero in lista.numeros
            ]
        
        return lista_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener lista {lista_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener la lista"
        )


@router.delete("/{lista_id}")
def eliminar_lista(
    lista_id: int,
    db: Session = Depends(obtener_sesion)
) -> dict:
    """
    Elimina una lista de llamadas y todos sus números asociados.
    
    **Advertencia:** Esta operación no se puede deshacer.
    """
    try:
        service = ListaLlamadasService(db)
        service.eliminar_lista(lista_id)
        
        return {
            "mensaje": f"Lista {lista_id} eliminada exitosamente",
            "lista_id": lista_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar lista {lista_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al eliminar la lista"
        )


@router.put("/{lista_id}", response_model=ListaLlamadasResponse)
def actualizar_lista(
    lista_id: int,
    datos_actualizacion: ListaLlamadasUpdate,
    db: Session = Depends(obtener_sesion)
) -> ListaLlamadasResponse:
    """
    Actualiza los metadatos de una lista de llamadas.
    
    **Nota:** Solo se pueden actualizar nombre, descripción y estado activo.
    Los números de la lista no se modifican por esta ruta.
    """
    try:
        service = ListaLlamadasService(db)
        lista = service.obtener_lista(lista_id)
        
        # Actualizar campos proporcionados
        if datos_actualizacion.nombre is not None:
            # Verificar que el nuevo nombre no exista
            lista_existente = db.query(ListaLlamadas).filter(
                ListaLlamadas.nombre == datos_actualizacion.nombre,
                ListaLlamadas.id != lista_id
            ).first()
            
            if lista_existente:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe una lista con el nombre '{datos_actualizacion.nombre}'"
                )
            
            lista.nombre = datos_actualizacion.nombre
            
        if datos_actualizacion.descripcion is not None:
            lista.descripcion = datos_actualizacion.descripcion
            
        if datos_actualizacion.activa is not None:
            lista.activa = datos_actualizacion.activa
        
        db.commit()
        db.refresh(lista)
        
        return ListaLlamadasResponse.from_orm(lista)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar lista {lista_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error interno al actualizar la lista"
        ) 