import random
from typing import Optional, List
import re

def generar_cli(prefijo: Optional[str] = None, lista_prefijos: Optional[List[str]] = None) -> str:
    """
    Genera un numero CLI (Caller Line Identification) aleatorio para llamadas salientes.
    
    Args:
        prefijo: Prefijo especifico para el CLI (opcional)
        lista_prefijos: Lista de prefijos posibles para elegir aleatoriamente (opcional)
    
    Returns:
        str: Numero CLI generado
    
    Ejemplo:
        >>> generar_cli(prefijo="91")
        "917654321"
        >>> generar_cli(lista_prefijos=["91", "93", "94"])
        "937654321"
    """
    # Si no hay prefijo especifico pero hay lista, elegir uno aleatorio
    if prefijo is None and lista_prefijos:
        prefijo = random.choice(lista_prefijos)
    
    # Si aun no hay prefijo, usar uno por defecto
    if prefijo is None:
        prefijo = "9" + str(random.randint(1, 9))
    
    # Asegurar que el prefijo es un string
    prefijo = str(prefijo)
    
    # Generar el resto del numero
    # La longitud total debe ser 9 digitos (estandar espanol)
    digitos_restantes = 9 - len(prefijo)
    
    # Si el prefijo es demasiado largo, truncarlo
    if digitos_restantes <= 0:
        prefijo = prefijo[:9]
        return prefijo
    
    # Generar los digitos restantes
    resto = ''.join(str(random.randint(0, 9)) for _ in range(digitos_restantes))
    
    # Combinar prefijo y resto
    numero_cli = prefijo + resto
    
    return numero_cli

def validar_cli(numero: str) -> bool:
    """
    Valida si un numero CLI tiene el formato correcto.
    
    Args:
        numero: Numero a validar
    
    Returns:
        bool: True si el numero es valido, False en caso contrario
    """
    # Verificar que solo contiene digitos y tiene la longitud correcta
    patron = re.compile(r'^\d{9}$')
    return bool(patron.match(numero)) 