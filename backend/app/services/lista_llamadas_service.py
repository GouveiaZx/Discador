"""
Servico para processar listas de llamadas a partir de arquivos CSV/TXT.
"""

import csv
import io
import random
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
            
            # RANDOMIZAR NÚMEROS PARA EVITAR DISCAGEM SEQUENCIAL
            if estadisticas['numeros_validos']:
                random.shuffle(estadisticas['numeros_validos'])
                logger.info(f"Números randomizados: {len(estadisticas['numeros_validos'])} números misturados")
            
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
                'archivo_original': lista.archivo_origen,
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
        contactos_raw = []
        errores = []
        
        try:
            if filename.lower().endswith('.csv'):
                contactos_raw = self._procesar_csv(contenido)
            else:
                contactos_raw = self._procesar_txt(contenido)
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
        
        for i, contacto in enumerate(contactos_raw, 1):
            numero_raw = contacto.get('telefono', '').strip()
            
            if not numero_raw:
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
                'numero_normalizado': validacion.numero_normalizado,
                'nombre': contacto.get('nombre', '').strip(),
                'apellido': contacto.get('apellido', '').strip(),
                'empresa': contacto.get('empresa', '').strip()
            })
        
        return {
            'total_lineas': len(contactos_raw),
            'numeros_validos': numeros_validos,
            'numeros_invalidos': numeros_invalidos,
            'numeros_duplicados': numeros_duplicados,
            'errores': errores
        }
    
    def _procesar_csv(self, contenido: str) -> List[Dict[str, str]]:
        """
        Procesa archivo CSV y extrae contactos con múltiples columnas.
        
        Formatos soportados:
        1. telefono,nombre,apellido
        2. nombre,apellido,telefono  
        3. telefono,nombre
        4. nome,telefone (português)
        5. phone_number,name,last_name (inglés)
        """
        contactos = []
        
        # Detectar si tiene header
        sniffer = csv.Sniffer()
        sample = contenido[:1024]
        has_header = sniffer.has_header(sample)
        
        reader = csv.reader(io.StringIO(contenido))
        
        headers = []
        if has_header:
            headers = [h.strip().lower() for h in next(reader)]
            logger.info(f"Headers detectados: {headers}")
        
        # Mapear headers para campos conhecidos
        campo_telefone = self._detectar_campo_telefone(headers)
        campo_nombre = self._detectar_campo_nombre(headers) 
        campo_apellido = self._detectar_campo_apellido(headers)
        campo_empresa = self._detectar_campo_empresa(headers)
        
        for row_num, row in enumerate(reader, 2):  # Começar em 2 por causa do header
            if not row or not any(cell.strip() for cell in row):  # Ignorar filas vazias
                continue
                
            contacto = {}
            
            if headers and len(row) >= len(headers):
                # Usar headers detectados
                for i, header in enumerate(headers):
                    if i < len(row):
                        if header == campo_telefone:
                            contacto['telefono'] = row[i].strip()
                        elif header == campo_nombre:
                            contacto['nombre'] = row[i].strip()
                        elif header == campo_apellido:
                            contacto['apellido'] = row[i].strip()
                        elif header == campo_empresa:
                            contacto['empresa'] = row[i].strip()
            else:
                # Fallback: assumir primeira coluna como telefone
                if len(row) >= 1:
                    contacto['telefono'] = row[0].strip()
                if len(row) >= 2:
                    contacto['nombre'] = row[1].strip()
                if len(row) >= 3:
                    contacto['apellido'] = row[2].strip()
                if len(row) >= 4:
                    contacto['empresa'] = row[3].strip()
            
            if contacto.get('telefono'):  # Só adicionar se tiver telefone
                contactos.append(contacto)
        
        logger.info(f"CSV processado: {len(contactos)} contactos extraídos")
        return contactos
    
    def _detectar_campo_telefone(self, headers: List[str]) -> str:
        """Detecta qual campo contém o telefone."""
        campos_telefone = [
            'telefono', 'phone', 'phone_number', 'numero', 'tel', 'celular',
            'mobile', 'whatsapp', 'fone', 'telefone'
        ]
        
        for header in headers:
            if any(campo in header for campo in campos_telefone):
                return header
        
        # Se não encontrar, assumir primeira coluna
        return headers[0] if headers else None
    
    def _detectar_campo_nombre(self, headers: List[str]) -> str:
        """Detecta qual campo contém o nome."""
        campos_nombre = [
            'nombre', 'name', 'first_name', 'nome', 'primeiro_nome',
            'firstname', 'given_name'
        ]
        
        for header in headers:
            if any(campo in header for campo in campos_nombre):
                return header
        
        return None
    
    def _detectar_campo_apellido(self, headers: List[str]) -> str:
        """Detecta qual campo contém o sobrenome."""
        campos_apellido = [
            'apellido', 'last_name', 'surname', 'sobrenome', 'lastname',
            'family_name', 'segundo_nome'
        ]
        
        for header in headers:
            if any(campo in header for campo in campos_apellido):
                return header
        
        return None
    
    def _detectar_campo_empresa(self, headers: List[str]) -> str:
        """Detecta qual campo contém a empresa."""
        campos_empresa = [
            'empresa', 'company', 'organizacion', 'organization',
            'negocio', 'business', 'firma'
        ]
        
        for header in headers:
            if any(campo in header for campo in campos_empresa):
                return header
        
        return None
    
    def _procesar_txt(self, contenido: str) -> List[Dict[str, str]]:
        """Procesa archivo TXT y extrae numeros (uno por linea)."""
        lineas = contenido.strip().split('\n')
        contactos = []
        
        for linea in lineas:
            linea = linea.strip()
            if linea:
                # Para TXT, assumir que só tem telefone
                contactos.append({
                    'telefono': linea,
                    'nombre': '',
                    'apellido': '',
                    'empresa': ''
                })
        
        return contactos
    
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
            archivo_origen=archivo_original,
            total_contactos=estadisticas['total_lineas'],
            contactos_pendientes=len(estadisticas['numeros_validos'])
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
                    lista_id=lista_id,  # Corrigido: era id_lista
                    nombre=numero_data.get('nombre', ''),
                    apellido=numero_data.get('apellido', ''),
                    empresa=numero_data.get('empresa', ''),
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