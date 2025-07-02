from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, func, Float, JSON
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

class CliGeo(Base):
    __tablename__ = "cli_geo"
    
    id = Column(Integer, primary_key=True, index=True)
    cli_id = Column(Integer, ForeignKey("clis.id"), nullable=False)
    prefijo_id = Column(Integer, ForeignKey("prefijo.id"), nullable=False)
    numero = Column(String(20), nullable=False)
    numero_normalizado = Column(String(20), nullable=False, unique=True)
    tipo_numero = Column(String(20), nullable=False)
    operadora = Column(String(50), nullable=False)
    
    # Métricas de qualidade
    calidad = Column(Float, default=1.0, nullable=False)
    tasa_exito = Column(Float, default=0.0, nullable=False)
    total_llamadas = Column(Integer, default=0, nullable=False)
    llamadas_exitosas = Column(Integer, default=0, nullable=False)
    
    # Configurações
    limite_diario = Column(Integer, default=1000, nullable=False)
    usos_hoy = Column(Integer, default=0, nullable=False)
    
    # Status
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    ultimo_uso = Column(DateTime, nullable=True)
    
    # Relationships
    prefijo = relationship("Prefijo")
    historiales = relationship("HistorialSeleccionCli", back_populates="cli_geo")
    
    def __repr__(self):
        return f"<CliGeo(id={self.id}, numero={self.numero}, operadora={self.operadora})>"

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

class HistorialSeleccionCli(Base):
    __tablename__ = "historial_seleccion_cli"
    
    id = Column(Integer, primary_key=True, index=True)
    cli_geo_id = Column(Integer, ForeignKey("cli_geo.id"), nullable=False)
    numero_destino = Column(String(20), nullable=False)
    numero_destino_normalizado = Column(String(20), nullable=False)
    
    # Dados da seleção
    score_seleccion = Column(Float, nullable=False)
    reglas_aplicadas = Column(JSON, default=[])
    total_candidatos = Column(Integer, nullable=False)
    tiempo_seleccion_ms = Column(Float, nullable=False)
    
    # Resultado da chamada (atualizado posteriormente)
    llamada_exitosa = Column(Boolean, nullable=True)
    duracion_llamada = Column(Integer, nullable=True)  # em segundos
    motivo_finalizacion = Column(String(50), nullable=True)
    
    # Timestamps
    fecha_seleccion = Column(DateTime, default=func.now())
    fecha_actualizacion_resultado = Column(DateTime, nullable=True)
    
    # Relationships
    cli_geo = relationship("CliGeo", back_populates="historiales")
    
    def __repr__(self):
        return f"<HistorialSeleccionCli(id={self.id}, cli_geo_id={self.cli_geo_id}, numero_destino={self.numero_destino})>" 