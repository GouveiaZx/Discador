# Paquete de rutas para la API del discador predictivo
"""
Este modulo contiene todas las rutas de la API organizadas por funcionalidad.
Incluye endpoints para gestionar llamadas, listas, CLI, reconocimiento de voz y reportes.
"""

# Importar routers para que fiquem disponíveis quando importado
from . import presione1 
from . import trunk
from . import caller_id
from . import timing
from . import dnc 