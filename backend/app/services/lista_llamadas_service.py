"""
Servico para processar listas de llamadas a partir de arquivos CSV/TXT.
"""

import csv
import io
from typing import List, Set, Tuple, Dict, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.lista_llamadas import ListaLlamadas, NumeroLlamada
from app.schemas.lista_llamadas import validar_numero_telefone, ValidacionNumero
from app.utils.logger import logger


class ListaLlamadasService:
    """Servico para processar listas de llamadas."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def procesar_archivo(
        self, 
        archivo: UploadFile, 
        nombre_lista: str,
        descripcion: str = None
    ) -> Dict[str, Any]:
        """
        Procesa un archivo CSV/TXT con numeros de telefono.
        
        Args:
            archivo: Archivo subido via FastAPI
            nombre_lista: Nombre para la lista de llamadas
            descripcion: Descripcion opcional de la lista
            
        Returns:
            Diccionario con estadisticas del procesamiento
        """
        logger.info(f"Iniciando procesamiento de archivo: {archivo.filename}")
        
        # Validar tipo de archivo
        if not self._validar_tipo_archivo(archivo.filename):
            raise HTTPException(
                status_code=400,
                detail="Tipo de archivo no valido. Solo se aceptan archivos CSV y TXT."
            )
        
        # Verificar si ya existe una lista con ese nombre
        lista_existente = self.db.query(ListaLlamadas).filter(
            ListaLlamadas.nombre == nombre_lista
        ).first()
        
        if lista_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una lista con el nombre '{nombre_lista}'"
            )
        
        try:
            # Leer contenido del archivo
            contenido = await archivo.read()
            contenido_texto = contenido.decode('utf-8')
            
            # Procesar numeros
            estadisticas = await self._procesar_numeros(contenido_texto, archivo.filename)
            
            # Crear lista en la base de datos
            lista = self._crear_lista(
                nombre_lista, 
                descripcion, 
                archivo.filename,
                estadisticas
            )
            
            # Guardar numeros validos
            numeros_guardados = self._guardar_numeros(lista.id, estadisticas['numeros_validos'])
            
            # Actualizar estadisticas finales
            lista.numeros_validos = numeros_guardados
            self.db.commit()
            
            logger.info(f"Archivo procesado exitosamente. Lista ID: {lista.id}")
            
            return {
                'lista_id': lista.id,
                'nombre_lista': lista.nombre,
                'archivo_original': lista.archivo_original,
                'total_numeros_archivo': estadisticas['total_lineas'],
                'numeros_validos': numeros_guardados,
                'numeros_invalidos': estadisticas['numeros_invalidos'],
                'numeros_duplicados': estadisticas['numeros_duplicados'],
                'errores': estadisticas['errores']
            }
            
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Error al leer el archivo. Verifique que este codificado en UTF-8."
            )
        except Exception as e:
            logger.error(f"Error procesando archivo: {str(e)}")
            # Rollback en caso de error
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error interno al procesar el archivo: {str(e)}"
            )
    
    def _validar_tipo_archivo(self, filename: str) -> bool:
        """Valida que el archivo sea CSV o TXT."""
        if not filename:
            return False
        
        extensiones_validas = ['.csv', '.txt']
        return any(filename.lower().endswith(ext) for ext in extensiones_validas)
    
    async def _procesar_numeros(self, contenido: str, filename: str) -> Dict[str, Any]:
        """
        Procesa el contenido del archivo y extrae los numeros.
        
        Args:
            contenido: Contenido del archivo como string
            filename: Nombre del archivo para determinar el formato
            
        Returns:
            Diccionario con estadisticas del procesamiento
        """
        numeros_raw = []
        errores = []
        
        try:
            if filename.lower().endswith('.csv'):
                numeros_raw = self._procesar_csv(contenido)
            else:
                numeros_raw = self._procesar_txt(contenido)
        except Exception as e:
            errores.append(f"Error al parsear archivo: {str(e)}")
            return {
                'total_lineas': 0,
                'numeros_validos': [],
                'numeros_invalidos': 0,
                'numeros_duplicados': 0,
                'errores': errores
            }
        
        # Validar y normalizar numeros
        numeros_validos = []
        numeros_invalidos = 0
        numeros_vistos: Set[str] = set()
        numeros_duplicados = 0
        
        for i, numero_raw in enumerate(numeros_raw, 1):
            if not numero_raw.strip():
                continue
                
            validacion = validar_numero_telefone(numero_raw)
            
            if not validacion.valido:
                numeros_invalidos += 1
                errores.append(f"Linea {i}: {validacion.motivo_invalido} - '{numero_raw}'")
                continue
            
            # Verificar duplicados
            if validacion.numero_normalizado in numeros_vistos:
                numeros_duplicados += 1
                errores.append(f"Linea {i}: Numero duplicado - '{numero_raw}'")
                continue
            
            numeros_vistos.add(validacion.numero_normalizado)
            numeros_validos.append({
                'numero_original': validacion.numero_original,
                'numero_normalizado': validacion.numero_normalizado
            })
        
        return {
            'total_lineas': len(numeros_raw),
            'numeros_validos': numeros_validos,
            'numeros_invalidos': numeros_invalidos,
            'numeros_duplicados': numeros_duplicados,
            'errores': errores
        }
    
    def _procesar_csv(self, contenido: str) -> List[str]:
        """Procesa archivo CSV y extrae numeros."""
        numeros = []
        
        # Detectar si tiene header
        sniffer = csv.Sniffer()
        sample = contenido[:1024]
        has_header = sniffer.has_header(sample)
        
        reader = csv.reader(io.StringIO(contenido))
        
        if has_header:
            next(reader)  # Saltar header
        
        for row in reader:
            if row:  # Ignorar filas vacias
                # Tomar el primer campo como numero
                numeros.append(row[0].strip())
        
        return numeros
    
    def _procesar_txt(self, contenido: str) -> List[str]:
        """Procesa archivo TXT y extrae numeros (uno por linea)."""
        lineas = contenido.strip().split('\n')
        return [linea.strip() for linea in lineas if linea.strip()]
    
    def _crear_lista(
        self, 
        nombre: str, 
        descripcion: str, 
        archivo_original: str,
        estadisticas: Dict[str, Any]
    ) -> ListaLlamadas:
        """Crea una nueva lista en la base de datos."""
        
        lista = ListaLlamadas(
            nombre=nombre,
            descripcion=descripcion,
            archivo_original=archivo_original,
            total_numeros=estadisticas['total_lineas'],
            numeros_validos=len(estadisticas['numeros_validos']),
            numeros_duplicados=estadisticas['numeros_duplicados']
        )
        
        self.db.add(lista)
        self.db.flush()  # Para obtener el ID sin hacer commit
        
        return lista
    
    def _guardar_numeros(self, lista_id: int, numeros_validos: List[Dict[str, str]]) -> int:
        """
        Guarda los numeros validos en la base de datos.
        
        Returns:
            Cantidad de numeros guardados exitosamente
        """
        numeros_guardados = 0
        
        for numero_data in numeros_validos:
            try:
                numero = NumeroLlamada(
                    numero=numero_data['numero_original'],
                    numero_normalizado=numero_data['numero_normalizado'],
                    id_lista=lista_id,
                    valido=True
                )
                
                self.db.add(numero)
                numeros_guardados += 1
                
            except IntegrityError:
                # Manejar duplicados que puedan haber pasado la validacion inicial
                self.db.rollback()
                logger.warning(f"Numero duplicado encontrado en BD: {numero_data['numero_normalizado']}")
                continue
        
        return numeros_guardados
    
    def obtener_lista(self, lista_id: int) -> ListaLlamadas:
        """Obtiene una lista por ID."""
        lista = self.db.query(ListaLlamadas).filter(ListaLlamadas.id == lista_id).first()
        
        if not lista:
            raise HTTPException(
                status_code=404,
                detail=f"Lista con ID {lista_id} no encontrada"
            )
        
        return lista
    
    def listar_listas(self, skip: int = 0, limit: int = 100) -> List[ListaLlamadas]:
        """Lista todas las listas de llamadas."""
        return (
            self.db.query(ListaLlamadas)
            .order_by(ListaLlamadas.fecha_creacion.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def eliminar_lista(self, lista_id: int) -> bool:
        """Elimina una lista y todos sus numeros."""
        lista = self.obtener_lista(lista_id)
        
        try:
            self.db.delete(lista)
            self.db.commit()
            logger.info(f"Lista eliminada: {lista.nombre} (ID: {lista_id})")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar lista {lista_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al eliminar la lista: {str(e)}"
            ) 