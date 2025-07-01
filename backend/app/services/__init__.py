# Paquete de servicios para la API del discador predictivo
"""
Este modulo contiene los servicios que implementan la logica de negocio.
Incluye servicios para interactuar con Asterisk, generacion de CLI, reconocimiento de voz,
el sistema de audio inteligente y el sistema CODE2BASE para selecao inteligente de CLIs.
""" 

from app.services.asterisk import asterisk_service
from app.services.cli_generator import generar_cli, validar_cli
from app.services.llamadas import llamadas_service
from app.services.distribuidor_llamadas import distribuidor_llamadas_service

# Nuevos servicios del sistema de audio inteligente
from app.services.audio_engine import AudioIntelligentSystem, AudioRulesEngine, AudioStateMachine
from app.services.audio_context_manager import AudioContextManager
from app.services.audio_integration_service import AudioIntegrationService

# Nuevos servicios del sistema CODE2BASE Avancado
from app.services.code2base_engine import Code2BaseEngine
from app.services.code2base_geo_service import Code2BaseGeoService
from app.services.code2base_rules_service import Code2BaseRulesService

__all__ = [
    'asterisk_service',
    'generar_cli',
    'validar_cli',
    'llamadas_service',
    'distribuidor_llamadas_service',
    # Sistema de Audio Inteligente
    'AudioIntelligentSystem',
    'AudioRulesEngine', 
    'AudioStateMachine',
    'AudioContextManager',
    'AudioIntegrationService',
    # Sistema CODE2BASE Avancado
    'Code2BaseEngine',
    'Code2BaseGeoService',
    'Code2BaseRulesService'
] 