# Paquete de modelos para la API del discador predictivo

from app.models.lista_negra import ListaNegra
from app.models.campana import Campana
from app.models.lead import Lead
from app.models.llamada import Llamada

# Importar todos los modelos aquí para facilitar las migraciones de Alembic
__all__ = ["ListaNegra", "Campana", "Lead", "Llamada"] 