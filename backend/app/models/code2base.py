# Modelos Code2Base
from .stub_models import Pais, Estado, Cidade, Prefijo, ReglaCli, CliGeo

# Adicionar classes faltantes
class HistorialSeleccionCli:
    def __init__(self, *args, **kwargs):
        pass

class Cli:
    def __init__(self, *args, **kwargs):
        pass

__all__ = ["Pais", "Estado", "Cidade", "Prefijo", "ReglaCli", "CliGeo", "HistorialSeleccionCli", "Cli"] 