# Paquete de servicios para la API del discador predictivo
"""
Este modulo contiene los servicios que implementan la logica de negocio.
Incluye servicios para interactuar con Asterisk, generacion de CLI, reconocimiento de voz,
el sistema de audio inteligente y el sistema CODE2BASE para selecao inteligente de CLIs.
""" 

# Importar solo los servicios esenciales para evitar problemas de dependencias
try:
    # Importar o serviço real do Asterisk AMI ao invés do mock
    from app.services.asterisk_ami import asterisk_ami as asterisk_service
    from app.services.cli_generator import generar_cli, validar_cli
    print("Core services imported successfully - Real Asterisk AMI activated")
except ImportError as e:
    print(f"Warning: Could not import core services: {e}")
    asterisk_service = None
    generar_cli = None
    validar_cli = None

# Importar presione1_service
try:
    from app.services import presione1_service
    print("Presione1 service imported successfully")
except ImportError as e:
    print(f"Warning: Could not import presione1_service: {e}")
    presione1_service = None

__all__ = [
    'asterisk_service',
    'generar_cli',
    'validar_cli',
    'presione1_service'
]