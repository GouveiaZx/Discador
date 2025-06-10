# Paquete de modelos para la API del discador predictivo
"""
Este modulo contiene los modelos de datos para interactuar con la base de datos.
Incluye modelos para llamadas, listas negras, leads, campanas, listas de llamadas,
el sistema de discado preditivo Presione 1, el sistema de audio inteligente,
el sistema CODE2BASE para selecao inteligente de CLIs, campanhas politicas
y el sistema Multi-SIP para multiples provedores VoIP.
"""

from app.models.llamada import Llamada
from app.models.campana import Campana
from app.models.lead import Lead
from app.models.lista_negra import ListaNegra
from app.models.usuario import Usuario
from app.models.lista_llamadas import ListaLlamadas, NumeroLlamada
from app.models.campana_presione1 import CampanaPresione1, LlamadaPresione1
from app.models.audio_sistema import (
    AudioContexto, AudioRegra, AudioSessao, AudioEvento, AudioTemplate,
    EstadoAudio, TipoEvento, TipoOperadorRegra
)
from app.models.code2base import (
    Pais, Estado, Cidade, Prefijo, CliGeo, ReglaCli, HistorialSeleccionCli,
    TipoOperadora, TipoRegra, TipoNumero
)
from app.models.campanha_politica import (
    ConfiguracaoEleitoral, CalendarioEleitoral, CampanhaPolitica,
    LogEleitoralImutavel, OptOutEleitoral, ExportacaoEleitoral,
    TipoEleicao, StatusCampanhaPolitica, TipoLogEleitoral
)
from app.models.multi_sip import (
    ProvedorSip, TarifaSip, LogSelecaoProvedor,
    TipoProvedor, StatusProvedor, TipoLigacao, MetodoSelecao
)

# Importar todos los modelos aqui para facilitar las migraciones de Alembic
__all__ = [
    'Llamada',
    'Campana',
    'Lead',
    'ListaNegra',
    'Usuario',
    'ListaLlamadas',
    'NumeroLlamada',
    'CampanaPresione1',
    'LlamadaPresione1',
    # Sistema de Audio Inteligente
    'AudioContexto',
    'AudioRegra',
    'AudioSessao',
    'AudioEvento',
    'AudioTemplate',
    'EstadoAudio',
    'TipoEvento',
    'TipoOperadorRegra',
    # Sistema CODE2BASE Avancado
    'Pais',
    'Estado',
    'Cidade',
    'Prefijo',
    'CliGeo',
    'ReglaCli',
    'HistorialSeleccionCli',
    'TipoOperadora',
    'TipoRegra',
    'TipoNumero',
    # Sistema de Campanhas Politicas
    'ConfiguracaoEleitoral',
    'CalendarioEleitoral',
    'CampanhaPolitica',
    'LogEleitoralImutavel',
    'OptOutEleitoral',
    'ExportacaoEleitoral',
    'TipoEleicao',
    'StatusCampanhaPolitica',
    'TipoLogEleitoral',
    # Sistema Multi-SIP
    'ProvedorSip',
    'TarifaSip',
    'LogSelecaoProvedor',
    'TipoProvedor',
    'StatusProvedor',
    'TipoLigacao',
    'MetodoSelecao'
] 