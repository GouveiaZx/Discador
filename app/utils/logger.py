import os
import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

from app.config import configuracion

# Niveles de logging
NIVELES = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

def configurar_logger(nombre_logger: str = "discador") -> logging.Logger:
    """
    Configura un logger con los parámetros de configuración.
    
    Args:
        nombre_logger: Nombre del logger a configurar
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Obtener o crear logger
    logger = logging.getLogger(nombre_logger)
    
    # Evitar configurar el mismo logger múltiples veces
    if logger.handlers:
        return logger
        
    # Establecer nivel de log
    nivel = NIVELES.get(configuracion.LOG_NIVEL, logging.INFO)
    logger.setLevel(nivel)
    
    # Formato de logs
    formato = logging.Formatter(configuracion.LOG_FORMATO)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formato)
    logger.addHandler(console_handler)
    
    # Handler para archivo si está configurado
    if configuracion.LOG_ARCHIVO:
        # Crear directorio de logs si no existe
        directorio_logs = os.path.dirname(configuracion.LOG_ARCHIVO)
        if directorio_logs:
            Path(directorio_logs).mkdir(parents=True, exist_ok=True)
            
        # Usar RotatingFileHandler o FileHandler según configuración
        if configuracion.LOG_ROTACION:
            file_handler = RotatingFileHandler(
                configuracion.LOG_ARCHIVO,
                maxBytes=configuracion.LOG_MAX_TAMANO_MB * 1024 * 1024,
                backupCount=configuracion.LOG_COPIAS_RESPALDO
            )
        else:
            file_handler = logging.FileHandler(configuracion.LOG_ARCHIVO)
            
        file_handler.setFormatter(formato)
        logger.addHandler(file_handler)
    
    return logger

# Logger principal de la aplicación
logger = configurar_logger("discador")

# Función para obtener un logger específico para un módulo
def obtener_logger(nombre: str) -> logging.Logger:
    """
    Obtiene un logger específico para un módulo.
    
    Args:
        nombre: Nombre del módulo o componente
        
    Returns:
        logging.Logger: Logger configurado
    """
    return configurar_logger(f"discador.{nombre}") 