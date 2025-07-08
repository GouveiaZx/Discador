# Paquete de servicios para la API del discador predictivo
"""
Este modulo contiene los servicios que implementan la logica de negocio.
Incluye servicios para interactuar con Asterisk, generacion de CLI, reconocimiento de voz,
el sistema de audio inteligente y el sistema CODE2BASE para selecao inteligente de CLIs.
""" 

# Importar solo los servicios esenciales para evitar problemas de dependencias
try:
    from app.services.asterisk import asterisk_service
    from app.services.cli_generator import generar_cli, validar_cli
    print("Core services imported successfully")
except ImportError as e:
    print(f"Warning: Could not import core services: {e}")
    asterisk_service = None
    generar_cli = None
    validar_cli = None

__all__ = [
    'asterisk_service',
    'generar_cli',
    'validar_cli'
] 