# Models package
# Modelos SQLAlchemy para o sistema de discagem

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Este arquivo serve como base para os modelos SQLAlchemy
# Os modelos específicos são definidos em arquivos separados 