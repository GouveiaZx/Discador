from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
import re


class NumeroLlamadaBase(BaseModel):
    """Schema base para números de llamadas."""
    numero: str = Field(..., description="Número de teléfono original")
    numero_normalizado: str = Field(..., description="Número normalizado")
    valido: bool = Field(True, description="Si el número es válido")
    notas: Optional[str] = Field(None, description="Notas adicionales sobre el número")


class NumeroLlamadaCreate(BaseModel):
    """Schema para crear un número de llamada."""
    numero: str = Field(..., description="Número de teléfono")
    id_lista: int = Field(..., description="ID de la lista a la que pertenece")


class NumeroLlamadaResponse(NumeroLlamadaBase):
    """Schema para respuesta de número de llamada."""
    id: int = Field(..., description="ID único del número")
    id_lista: int = Field(..., description="ID de la lista")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    
    class Config:
        from_attributes = True


class ListaLlamadasBase(BaseModel):
    """Schema base para listas de llamadas."""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la lista")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción de la lista")
    activa: bool = Field(True, description="Si la lista está activa")


class ListaLlamadasCreate(ListaLlamadasBase):
    """Schema para crear una lista de llamadas."""
    pass


class ListaLlamadasUpdate(BaseModel):
    """Schema para actualizar una lista de llamadas."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activa: Optional[bool] = None


class ListaLlamadasResponse(ListaLlamadasBase):
    """Schema para respuesta de lista de llamadas."""
    id: int = Field(..., description="ID único de la lista")
    archivo_original: str = Field(..., description="Nombre del archivo original")
    total_numeros: int = Field(..., description="Total de números en el archivo")
    numeros_validos: int = Field(..., description="Números válidos procesados")
    numeros_duplicados: int = Field(..., description="Números duplicados encontrados")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")
    
    class Config:
        from_attributes = True


class ListaLlamadasDetailResponse(ListaLlamadasResponse):
    """Schema detallado de lista con números incluidos."""
    numeros: List[NumeroLlamadaResponse] = Field([], description="Lista de números")


class UploadArchivoResponse(BaseModel):
    """Schema para respuesta del upload de archivo."""
    mensaje: str = Field(..., description="Mensaje de resultado")
    lista_id: int = Field(..., description="ID de la lista creada")
    nombre_lista: str = Field(..., description="Nombre de la lista")
    archivo_original: str = Field(..., description="Nombre del archivo procesado")
    total_numeros_archivo: int = Field(..., description="Total de líneas en el archivo")
    numeros_validos: int = Field(..., description="Números válidos guardados")
    numeros_invalidos: int = Field(..., description="Números inválidos encontrados")
    numeros_duplicados: int = Field(..., description="Números duplicados removidos")
    errores: List[str] = Field([], description="Lista de errores encontrados")


class ValidacionNumero(BaseModel):
    """Schema para validación de números individuales."""
    numero_original: str
    numero_normalizado: str
    valido: bool
    motivo_invalido: Optional[str] = None


def validar_numero_telefono(numero: str) -> ValidacionNumero:
    """
    Valida y normaliza un número de teléfono.
    
    Aceita formatos como:
    - +54 9 11 1234-5678
    - 011 1234-5678
    - 11 1234 5678
    - 1112345678
    
    Args:
        numero: Número a validar
        
    Returns:
        ValidacionNumero con resultado de la validación
    """
    numero_original = numero.strip()
    
    if not numero_original:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado="",
            valido=False,
            motivo_invalido="Número vacío"
        )
    
    # Remover espacios, guiones y paréntesis
    numero_limpio = re.sub(r'[^\d+]', '', numero_original)
    
    # Normalizar número argentino
    numero_normalizado = normalizar_numero_argentino(numero_limpio)
    
    # Validar formato final
    if not numero_normalizado:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado="",
            valido=False,
            motivo_invalido="Formato de número inválido"
        )
    
    # Validar longitud (números argentinos tienen 13 dígitos con +54)
    if len(numero_normalizado) < 11 or len(numero_normalizado) > 15:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado=numero_normalizado,
            valido=False,
            motivo_invalido=f"Longitud inválida: {len(numero_normalizado)} dígitos"
        )
    
    return ValidacionNumero(
        numero_original=numero_original,
        numero_normalizado=numero_normalizado,
        valido=True
    )


def normalizar_numero_argentino(numero: str) -> str:
    """
    Normaliza un número argentino al formato +549XXXXXXXXXX
    
    Args:
        numero: Número limpio (solo dígitos y +)
        
    Returns:
        Número normalizado o string vacío si es inválido
    """
    if not numero:
        return ""
    
    # Remover + inicial si existe
    if numero.startswith('+'):
        numero = numero[1:]
    
    # Casos comunes de números argentinos
    if numero.startswith('54'):
        # Ya tiene código de país
        if numero.startswith('549'):
            # Ya normalizado
            return f"+{numero}"
        elif len(numero) >= 12:
            # Agregar 9 después del código de país
            return f"+549{numero[2:]}"
    elif numero.startswith('9'):
        # Número con 9 pero sin código de país
        return f"+54{numero}"
    elif numero.startswith('11') or numero.startswith('2') or numero.startswith('3'):
        # Número de área sin 9 ni código de país
        return f"+549{numero}"
    elif len(numero) == 8:
        # Número corto, asumir Buenos Aires (11)
        return f"+54911{numero}"
    elif len(numero) == 10:
        # Número completo sin código de país ni 9
        return f"+549{numero}"
    
    # Si no coincide con ningún patrón conocido, intentar como está
    if numero.isdigit() and len(numero) >= 8:
        return f"+549{numero}"
    
    return "" 