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
    pais_detectado: Optional[str] = None
    es_toll_free: Optional[bool] = None
    es_wireless: Optional[bool] = None


# Códigos de área válidos dos EUA (NANP)
CODIGOS_AREA_USA_VALIDOS = {
    # Estados Unidos continentais
    '201', '202', '203', '205', '206', '207', '208', '209', '210', '212', '213', '214', '215', '216', '217', '218', '219',
    '224', '225', '228', '229', '231', '234', '239', '240', '248', '251', '252', '253', '254', '256', '260', '262', '267',
    '269', '270', '276', '281', '301', '302', '303', '304', '305', '307', '308', '309', '310', '312', '313', '314', '315',
    '316', '317', '318', '319', '320', '321', '323', '325', '330', '331', '334', '336', '337', '339', '347', '351', '352',
    '360', '361', '364', '380', '385', '386', '401', '402', '404', '405', '406', '407', '408', '409', '410', '412', '413',
    '414', '415', '417', '419', '423', '424', '425', '430', '432', '434', '435', '440', '442', '443', '458', '463', '464',
    '469', '470', '475', '478', '479', '480', '484', '501', '502', '503', '504', '505', '507', '508', '509', '510', '512',
    '513', '515', '516', '517', '518', '520', '530', '531', '534', '539', '540', '541', '551', '555', '559', '561', '562', '563',
    '564', '567', '570', '571', '573', '574', '575', '580', '585', '586', '601', '602', '603', '605', '606', '607', '608',
    '609', '610', '612', '614', '615', '616', '617', '618', '619', '620', '623', '626', '628', '629', '630', '631', '636',
    '641', '646', '650', '651', '657', '660', '661', '662', '667', '669', '678', '679', '681', '682', '701', '702', '703',
    '704', '706', '707', '708', '712', '713', '714', '715', '716', '717', '718', '719', '720', '724', '725', '727', '731',
    '732', '734', '737', '740', '743', '747', '754', '757', '760', '762', '763', '765', '769', '770', '772', '773', '774',
    '775', '779', '781', '785', '786', '787', '800', '801', '802', '803', '804', '805', '806', '808', '810', '812', '813', '814',
    '815', '816', '817', '818', '828', '830', '831', '832', '833', '843', '844', '845', '847', '848', '850', '855', '856', '857', '858', '859',
    '860', '862', '863', '864', '865', '866', '870', '872', '877', '878', '888', '901', '903', '904', '906', '907', '908', '909', '910', '912',
    '913', '914', '915', '916', '917', '918', '919', '920', '925', '928', '929', '930', '931', '934', '936', '937', '938',
    '940', '941', '947', '949', '951', '952', '954', '956', '959', '970', '971', '972', '973', '978', '979', '980', '984',
    '985', '989'
}

# Números toll-free dos EUA
TOLL_FREE_USA = {'800', '833', '844', '855', '866', '877', '888'}

# Códigos de área que são principalmente wireless
WIRELESS_AREA_CODES = {
    '310', '323', '424', '747',  # Los Angeles
    '917', '347', '929', '646',  # New York
    '305', '786', '954',         # Florida
    '214', '469', '972',         # Dallas
    '713', '281', '832',         # Houston
    '404', '678', '470',         # Atlanta
}


def validar_numero_telefone(numero: str, pais_preferido: str = "auto") -> ValidacionNumero:
    """
    Valida y normaliza un numero de telefono para Argentina o EUA.
    
    Args:
        numero: Numero a validar
        pais_preferido: "argentina", "usa", "auto" (detecta automaticamente)
        
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
    
    # Remover espacios, guiones, parentesis y puntos
    numero_limpio = re.sub(r'[^\d+]', '', numero_original)
    
    # Detectar país automaticamente o usar preferencia
    if pais_preferido == "auto":
        pais_detectado = detectar_pais_numero(numero_limpio)
    else:
        pais_detectado = pais_preferido
    
    # Validar según el país detectado
    if pais_detectado == "usa":
        return validar_numero_usa(numero_original, numero_limpio)
    else:
        return validar_numero_argentina(numero_original, numero_limpio)


def detectar_pais_numero(numero_limpio: str) -> str:
    """Detecta el país basado en el formato del número."""
    
    if not numero_limpio:
        return "argentina"  # Default
    
    # Remover + inicial si existe
    if numero_limpio.startswith('+'):
        numero_limpio = numero_limpio[1:]
    
    # Verificar código de país
    if numero_limpio.startswith('1') and len(numero_limpio) == 11:
        # +1 seguido de 10 dígitos = EUA/Canadá
        return "usa"
    elif numero_limpio.startswith('54'):
        # +54 = Argentina
        return "argentina"
    elif len(numero_limpio) == 10 and numero_limpio[0] in '2356789':
        # 10 dígitos empezando con 2-9 = probablemente EUA
        codigo_area = numero_limpio[:3]
        if codigo_area in CODIGOS_AREA_USA_VALIDOS:
            return "usa"
    
    # Default para Argentina
    return "argentina"


def validar_numero_usa(numero_original: str, numero_limpio: str) -> ValidacionNumero:
    """
    Valida un número de teléfono de EUA (NANP - North American Numbering Plan).
    
    Formatos aceptados:
    - +1 555 123 4567
    - 1 555 123 4567
    - (555) 123-4567
    - 555-123-4567
    - 5551234567
    """
    
    # Remover + inicial si existe
    if numero_limpio.startswith('+'):
        numero_limpio = numero_limpio[1:]
    
    # Remover código de país 1 si está presente
    if numero_limpio.startswith('1') and len(numero_limpio) == 11:
        numero_sin_codigo_pais = numero_limpio[1:]
    elif len(numero_limpio) == 10:
        numero_sin_codigo_pais = numero_limpio
    else:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado="",
            valido=False,
            motivo_invalido=f"Longitud inválida para número USA: {len(numero_limpio)} dígitos",
            pais_detectado="usa"
        )
    
    # Verificar que tenga exactamente 10 dígitos
    if len(numero_sin_codigo_pais) != 10:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado="",
            valido=False,
            motivo_invalido=f"Número USA debe tener 10 dígitos, tiene {len(numero_sin_codigo_pais)}",
            pais_detectado="usa"
        )
    
    # Extraer código de área y número
    codigo_area = numero_sin_codigo_pais[:3]
    central_office = numero_sin_codigo_pais[3:6]
    numero_final = numero_sin_codigo_pais[6:]
    
    # Validar código de área
    if codigo_area not in CODIGOS_AREA_USA_VALIDOS:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado="",
            valido=False,
            motivo_invalido=f"Código de área inválido: {codigo_area}",
            pais_detectado="usa"
        )
    
    # Validar que el primer dígito del código de área no sea 0 o 1
    if codigo_area[0] in '01':
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado="",
            valido=False,
            motivo_invalido=f"Código de área no puede empezar con {codigo_area[0]}",
            pais_detectado="usa"
        )
    
    # Validar que el primer dígito del central office no sea 0 o 1
    if central_office[0] in '01':
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado="",
            valido=False,
            motivo_invalido=f"Código central no puede empezar con {central_office[0]}",
            pais_detectado="usa"
        )
    
    # Verificar si es toll-free
    es_toll_free = codigo_area in TOLL_FREE_USA
    
    # Verificar si es probablemente wireless
    es_wireless = codigo_area in WIRELESS_AREA_CODES
    
    # Número normalizado en formato E.164
    numero_normalizado = f"+1{numero_sin_codigo_pais}"
    
    return ValidacionNumero(
        numero_original=numero_original,
        numero_normalizado=numero_normalizado,
        valido=True,
        pais_detectado="usa",
        es_toll_free=es_toll_free,
        es_wireless=es_wireless
    )


def validar_numero_argentina(numero_original: str, numero_limpio: str) -> ValidacionNumero:
    """Valida un número argentino (función existente)."""
    
    # Normalizar numero argentino
    numero_normalizado = normalizar_numero_argentino(numero_limpio)
    
    # Validar formato final
    if not numero_normalizado:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado="",
            valido=False,
            motivo_invalido="Formato de numero invalido",
            pais_detectado="argentina"
        )
    
    # Validar longitud (numeros argentinos tienen 13 digitos con +54)
    if len(numero_normalizado) < 11 or len(numero_normalizado) > 15:
        return ValidacionNumero(
            numero_original=numero_original,
            numero_normalizado=numero_normalizado,
            valido=False,
            motivo_invalido=f"Longitud invalida: {len(numero_normalizado)} digitos",
            pais_detectado="argentina"
        )
    
    return ValidacionNumero(
        numero_original=numero_original,
        numero_normalizado=numero_normalizado,
        valido=True,
        pais_detectado="argentina"
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


def formatear_numero_para_discado(numero_normalizado: str, formato: str = "e164") -> str:
    """
    Formatea un número normalizado para discado.
    
    Args:
        numero_normalizado: Número en formato E.164 (+1xxxxxxxxxx o +549xxxxxxxxxx)
        formato: "e164", "national", "international", "10digit", "11digit"
        
    Returns:
        Número formatado según el formato solicitado
    """
    
    if not numero_normalizado or not numero_normalizado.startswith('+'):
        return numero_normalizado
    
    if numero_normalizado.startswith('+1'):
        # Número USA
        numero_sin_codigo = numero_normalizado[2:]  # Remover +1
        
        if formato == "e164":
            return numero_normalizado
        elif formato == "11digit":
            return f"1{numero_sin_codigo}"
        elif formato == "10digit":
            return numero_sin_codigo
        elif formato == "national":
            return f"({numero_sin_codigo[:3]}) {numero_sin_codigo[3:6]}-{numero_sin_codigo[6:]}"
        elif formato == "international":
            return f"+1 {numero_sin_codigo[:3]} {numero_sin_codigo[3:6]} {numero_sin_codigo[6:]}"
    
    elif numero_normalizado.startswith('+54'):
        # Número Argentina
        if formato == "e164":
            return numero_normalizado
        elif formato == "national":
            # Remover +549 y formatear
            numero_sin_codigo = numero_normalizado[4:]
            if len(numero_sin_codigo) >= 10:
                return f"{numero_sin_codigo[:2]} {numero_sin_codigo[2:6]}-{numero_sin_codigo[6:]}"
        elif formato == "international":
            return numero_normalizado.replace('+549', '+54 9 ')
    
    return numero_normalizado 