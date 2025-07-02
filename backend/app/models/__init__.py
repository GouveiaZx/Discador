# Imports dos modelos do sistema
from .audio import Audio
from .usuario import Usuario
from .llamada import Llamada
from .trunk import Trunk
from .dnc import DNCList, DNCNumber
from .role import Role, UserRole
from .multi_sip import ProvedorSip, TarifaSip, LogSelecaoProvedor
from .monitoring import AgenteMonitoramento, EventoSistema, SessionMonitoramento
from .lista_llamadas import ListaLlamadas
from .code2base import TipoOperadora, TipoRegra, TipoNumero, Pais, Estado, Cidade, Prefijo, ReglaCli
from .campanha_politica import CampanhaPolitica, AudioCampanha, EstatisticaCampanha
from .campana import Campana
from .audio_sistema import TipoEvento, AudioSistema

# Lista de todos os modelos para facilitar importações
__all__ = [
    "Audio",
    "Usuario", 
    "Llamada",
    "Trunk",
    "DNCList",
    "DNCNumber",
    "Role",
    "UserRole",
    "ProvedorSip",
    "TarifaSip", 
    "LogSelecaoProvedor",
    "AgenteMonitoramento",
    "EventoSistema",
    "SessionMonitoramento",
    "ListaLlamadas",
    "TipoOperadora",
    "TipoRegra",
    "TipoNumero",
    "Pais",
    "Estado",
    "Cidade", 
    "Prefijo",
    "ReglaCli",
    "CampanhaPolitica",
    "AudioCampanha",
    "EstatisticaCampanha",
    "Campana",
    "TipoEvento",
    "AudioSistema"
] 