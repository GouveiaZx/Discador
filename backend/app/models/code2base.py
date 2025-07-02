from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class TipoOperadora(Base):
    __tablename__ = "tipo_operadora"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True)
    codigo = Column(String(10), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<TipoOperadora(id={self.id}, nome={self.nome}, codigo={self.codigo})>"

class TipoRegra(Base):
    __tablename__ = "tipo_regra"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True)
    codigo = Column(String(20), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<TipoRegra(id={self.id}, nome={self.nome}, codigo={self.codigo})>"

class TipoNumero(Base):
    __tablename__ = "tipo_numero"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True)
    codigo = Column(String(20), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<TipoNumero(id={self.id}, nome={self.nome}, codigo={self.codigo})>"

class Pais(Base):
    __tablename__ = "pais"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    codigo_iso = Column(String(3), nullable=False, unique=True)
    codigo_pais = Column(String(5), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relationships
    estados = relationship("Estado", back_populates="pais", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Pais(id={self.id}, nome={self.nome}, codigo_iso={self.codigo_iso})>"

class Estado(Base):
    __tablename__ = "estado"
    
    id = Column(Integer, primary_key=True, index=True)
    pais_id = Column(Integer, ForeignKey("pais.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    codigo_estado = Column(String(10), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relationships
    pais = relationship("Pais", back_populates="estados")
    cidades = relationship("Cidade", back_populates="estado", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Estado(id={self.id}, nome={self.nome}, codigo={self.codigo_estado})>"

class Cidade(Base):
    __tablename__ = "cidade"
    
    id = Column(Integer, primary_key=True, index=True)
    estado_id = Column(Integer, ForeignKey("estado.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    codigo_cidade = Column(String(10), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relationships
    estado = relationship("Estado", back_populates="cidades")
    prefijos = relationship("Prefijo", back_populates="cidade", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cidade(id={self.id}, nome={self.nome}, estado_id={self.estado_id})>"

class Prefijo(Base):
    __tablename__ = "prefijo"
    
    id = Column(Integer, primary_key=True, index=True)
    cidade_id = Column(Integer, ForeignKey("cidade.id"), nullable=False)
    prefijo = Column(String(10), nullable=False)
    tipo_numero_id = Column(Integer, ForeignKey("tipo_numero.id"), nullable=False)
    tipo_operadora_id = Column(Integer, ForeignKey("tipo_operadora.id"), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relationships
    cidade = relationship("Cidade", back_populates="prefijos")
    tipo_numero = relationship("TipoNumero")
    tipo_operadora = relationship("TipoOperadora")
    
    def __repr__(self):
        return f"<Prefijo(id={self.id}, prefijo={self.prefijo}, cidade_id={self.cidade_id})>"

class ReglaCli(Base):
    __tablename__ = "regla_cli"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo_regra_id = Column(Integer, ForeignKey("tipo_regra.id"), nullable=False)
    prefijo_origem = Column(String(10), nullable=True)
    prefijo_destino = Column(String(10), nullable=True)
    cli_gerado = Column(String(20), nullable=False)
    prioridade = Column(Integer, default=1, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relationships
    tipo_regra = relationship("TipoRegra")
    
    def __repr__(self):
        return f"<ReglaCli(id={self.id}, nome={self.nome}, cli_gerado={self.cli_gerado})>" 