# Paquete de servicios para la API del discador predictivo
"""
Este módulo contiene los servicios que implementan la lógica de negocio.
Incluye servicios para interactuar con Asterisk, generación de CLI y reconocimiento de voz.
""" 

from app.services.asterisk import asterisk_service
from app.services.cli_generator import generar_cli, validar_cli
from app.services.llamadas import llamadas_service
from app.services.distribuidor_llamadas import distribuidor_llamadas_service

__all__ = [
    'asterisk_service',
    'generar_cli',
    'validar_cli',
    'llamadas_service',
    'distribuidor_llamadas_service'
] 