# Paquete de modelos para la API del discador predictivo
"""
Este módulo contiene los modelos de datos para interactuar con la base de datos.
Incluye modelos para llamadas, listas negras, leads, campañas, listas de llamadas
y el sistema de discado preditivo Presione 1.
"""

from app.models.llamada import Llamada
from app.models.campana import Campana
from app.models.lead import Lead
from app.models.lista_negra import ListaNegra
from app.models.usuario import Usuario
from app.models.lista_llamadas import ListaLlamadas, NumeroLlamada
from app.models.campana_presione1 import CampanaPresione1, LlamadaPresione1

# Importar todos los modelos aquí para facilitar las migraciones de Alembic
__all__ = [
    'Llamada',
    'Campana',
    'Lead',
    'ListaNegra',
    'Usuario',
    'ListaLlamadas',
    'NumeroLlamada',
    'CampanaPresione1',
    'LlamadaPresione1'
] 