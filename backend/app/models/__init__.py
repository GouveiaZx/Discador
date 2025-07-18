# Models package
# Modelos SQLAlchemy para o sistema de discagem

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Importar modelos específicos
from .cli import Cli
from .trunk import Trunk
from .stub_models import *

# Este arquivo serve como base para os modelos SQLAlchemy
# Os modelos específicos são definidos em arquivos separados

__all__ = ['Base', 'Cli', 'Trunk']