# Imports dos modelos do sistema
from .audio import Audio
from .usuario import Usuario
from .llamada import Llamada
from .trunk import Trunk
from .dnc import DNCList, DNCNumber
from .role import Role, UserRole
from .multi_sip import ProvedorSip, TarifaSip, LogSelecaoProvedor, ConfiguracaoMultiSip
from .monitoring import AgenteMonitoramento, EventoSistema, SessionMonitoramento
from .lista_llamadas import ListaLlamadas, NumeroLlamada
from .lista_negra import ListaNegra
from .code2base import TipoOperadora, TipoRegra, TipoNumero, Pais, Estado, Cidade, Prefijo, ReglaCli, CliGeo, HistorialSeleccionCli
from .campanha_politica import (
    CampanhaPolitica, AudioCampanha, EstatisticaCampanha,
    ConfiguracaoEleitoral, CalendarioEleitoral, LogEleitoralImutavel,
    OptOutEleitoral, TipoLogEleitoral, TipoEleicao, StatusCampanhaPolitica
)
from .campana import Campana
from .cli import Cli
from .audio_sistema import (
    TipoEvento, AudioSistema, AudioContexto, AudioRegra, AudioSessao, 
    AudioEvento, AudioTemplate, EstadoAudio, TipoOperadorRegra
)

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
    "ConfiguracaoMultiSip",
    "AgenteMonitoramento",
    "EventoSistema",
    "SessionMonitoramento",
    "ListaLlamadas",
    "NumeroLlamada",
    "ListaNegra",
    "TipoOperadora",
    "TipoRegra",
    "TipoNumero",
    "Pais",
    "Estado",
    "Cidade", 
    "Prefijo",
    "ReglaCli",
    "CliGeo",
    "HistorialSeleccionCli",
    "CampanhaPolitica",
    "AudioCampanha",
    "EstatisticaCampanha",
    "ConfiguracaoEleitoral",
    "CalendarioEleitoral",
    "LogEleitoralImutavel",
    "OptOutEleitoral",
    "TipoLogEleitoral",
    "TipoEleicao",
    "StatusCampanhaPolitica",
    "Campana",
    "Cli",
    "TipoEvento",
    "AudioSistema",
    "AudioContexto",
    "AudioRegra",
    "AudioSessao",
    "AudioEvento",
    "AudioTemplate",
    "EstadoAudio",
    "TipoOperadorRegra"
] 