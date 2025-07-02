from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import re


class NumeroLlamadaBase(BaseModel):
    """Schema base para numeros de llamadas."""
    numero: str = Field(..., description="Numero de telefono original")
    numero_normalizado: str = Field(..., description="Numero normalizado")
    valido: bool = Field(True, description="Si el numero es valido")
    notas: Optional[str] = Field(None, description="Notas adicionales sobre el numero")


class NumeroLlamadaCreate(BaseModel):
    """Schema para crear un numero de llamada."""
    numero: str = Field(..., description="Numero de telefono")
    id_lista: int = Field(..., description="ID de la lista a la que pertenece")


class NumeroLlamadaResponse(NumeroLlamadaBase):
    """Schema para respuesta de numero de llamada."""
    id: int = Field(..., description="ID unico del numero")
    id_lista: int = Field(..., description="ID de la lista")
    fecha_creacion: datetime = Field(..., description="Fecha de creacion")
    
    class Config:
        from_attributes = True


class ListaLlamadasBase(BaseModel):
    """Schema base para listas de llamadas."""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la lista")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripcion de la lista")
    activa: bool = Field(True, description="Si la lista esta activa")


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
    id: int = Field(..., description="ID unico de la lista")
    archivo_original: str = Field(..., description="Nombre del archivo original")
    total_numeros: int = Field(..., description="Total de numeros en el archivo")
    numeros_validos: int = Field(..., description="Numeros validos procesados")
    numeros_duplicados: int = Field(..., description="Numeros duplicados encontrados")
    fecha_creacion: datetime = Field(..., description="Fecha de creacion")
    fecha_actualizacion: datetime = Field(..., description="Fecha de ultima actualizacion")
    
    class Config:
        from_attributes = True


class ListaLlamadasDetailResponse(ListaLlamadasResponse):
    """Schema detallado de lista con numeros incluidos."""
    numeros: List[NumeroLlamadaResponse] = Field([], description="Lista de numeros")


class UploadArchivoResponse(BaseModel):
    """Schema para respuesta del upload de archivo."""
    mensaje: str = Field(..., description="Mensaje de resultado")
    lista_id: int = Field(..., description="ID de la lista creada")
    nombre_lista: str = Field(..., description="Nombre de la lista")
    archivo_original: str = Field(..., description="Nombre del archivo procesado")
    total_numeros_archivo: int = Field(..., description="Total de lineas en el archivo")
    numeros_validos: int = Field(..., description="Numeros validos guardados")
    numeros_invalidos: int = Field(..., description="Numeros invalidos encontrados")
    numeros_duplicados: int = Field(..., description="Numeros duplicados removidos")
    errores: List[str] = Field([], description="Lista de errores encontrados")


class ValidacionNumero(BaseModel):
    """Schema para validacion de numeros individuales."""
    numero_original: str
    numero_normalizado: str
    valido: bool
    motivo_invalido: Optional[str] = None


def validar_numero_telefone(numero: str) -> ValidacionNumero:
    """
    Valida y normaliza un numero de telefono.
    
    Aceita formatos como:
    - +54 9 11 1234-5678
    - 011 1234-5678
    - 11 1234 5678
    - 1112345678
    
    Args:
        numero: Numero a validar
        
    Returns:
        ValidacionNumero con resultado de la validacion
    """
    numero_original = numero.strip()
    
    if not numero_original:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado="",
            valido=False,
            motivo_invalido="Numero vacio"
        )
    
    # Remover espacios, guiones y parentesis
    numero_limpio = re.sub(r'[^\d+]', '', numero_original)
    
    # Normalizar numero argentino
    numero_normalizado = normalizar_numero_argentino(numero_limpio)
    
    # Validar formato final
    if not numero_normalizado:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado="",
            valido=False,
            motivo_invalido="Formato de numero invalido"
        )
    
    # Validar longitud (numeros argentinos tienen 13 digitos con +54)
    if len(numero_normalizado) < 11 or len(numero_normalizado) > 15:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado=numero_normalizado,
            valido=False,
            motivo_invalido=f"Longitud invalida: {len(numero_normalizado)} digitos"
        )
    
    return ValidacionNumero(
        numero_original=numero_original,
        numero_normalizado=numero_normalizado,
        valido=True
    )


def normalizar_numero_argentino(numero: str) -> str:
    """
    Normaliza un numero argentino al formato +549XXXXXXXXXX
    
    Args:
        numero: Numero limpio (solo digitos y +)
        
    Returns:
        Numero normalizado o string vacio si es invalido
    """
    if not numero:
        return ""
    
    # Remover + inicial si existe
    if numero.startswith('+'):
        numero = numero[1:]
    
    # Casos comunes de numeros argentinos
    if numero.startswith('54'):
        # Ya tiene codigo de pais
        if numero.startswith('549'):
            # Ya normalizado
            return f"+{numero}"
        elif len(numero) >= 12:
            # Agregar 9 despues del codigo de pais
            return f"+549{numero[2:]}"
    elif numero.startswith('9'):
        # Numero con 9 pero sin codigo de pais
        return f"+54{numero}"
    elif numero.startswith('11') or numero.startswith('2') or numero.startswith('3'):
        # Numero de area sin 9 ni codigo de pais
        return f"+549{numero}"
    elif len(numero) == 8:
        # Numero corto, asumir Buenos Aires (11)
        return f"+54911{numero}"
    elif len(numero) == 10:
        # Numero completo sin codigo de pais ni 9
        return f"+549{numero}"
    
    # Si no coincide con ningun patron conocido, intentar como esta
    if numero.isdigit() and len(numero) >= 8:
        return f"+549{numero}"
    
    return "" 