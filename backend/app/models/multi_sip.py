from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, func, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class ProvedorSip(Base):
    __tablename__ = "provedor_sip"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    tipo_provedor = Column(String(50), nullable=False, default="generico")
    descricao = Column(Text, nullable=True)
    
    # Configurações SIP
    servidor_sip = Column(String(255), nullable=False)
    porta_sip = Column(Integer, default=5060, nullable=False)
    protocolo = Column(String(10), default="UDP", nullable=False)
    
    # Autenticação
    usuario_sip = Column(String(100), nullable=True)
    senha_sip = Column(String(100), nullable=True)
    
    # Status e configurações
    ativo = Column(Boolean, default=True, nullable=False)
    max_chamadas_simultaneas = Column(Integer, default=50, nullable=False)
    timeout_conexao = Column(Integer, default=30, nullable=False)
    prioridade = Column(Integer, default=100, nullable=False)
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    tarifas = relationship("TarifaSip", back_populates="provedor", cascade="all, delete-orphan")
    logs_selecao = relationship("LogSelecaoProvedor", back_populates="provedor")
    
    def __repr__(self):
        return f"<ProvedorSip(id={self.id}, nome={self.nome}, codigo={self.codigo})>"

class TarifaSip(Base):
    __tablename__ = "tarifa_sip"
    
    id = Column(Integer, primary_key=True, index=True)
    provedor_id = Column(Integer, ForeignKey("provedor_sip.id", ondelete="CASCADE"), nullable=False)
    
    # Identificação do destino
    pais_codigo = Column(String(5), nullable=False)
    prefixo = Column(String(20), nullable=False)
    descricao_destino = Column(String(200), nullable=False)
    tipo_ligacao = Column(String(50), default="celular", nullable=False)
    
    # Tarifação
    custo_por_minuto = Column(DECIMAL(10, 6), nullable=False)
    moeda = Column(String(3), default="USD", nullable=False)
    taxa_conexao = Column(DECIMAL(10, 6), default=0.0, nullable=False)
    
    # Controle
    ativo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    provedor = relationship("ProvedorSip", back_populates="tarifas")
    
    def __repr__(self):
        return f"<TarifaSip(id={self.id}, prefixo={self.prefixo}, custo={self.custo_por_minuto})>"

class ConfiguracaoMultiSip(Base):
    __tablename__ = "configuracao_multi_sip"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    
    # Algoritmo de seleção
    algoritmo_selecao = Column(String(50), default="menor_custo", nullable=False)
    
    # Pesos para seleção
    peso_custo = Column(Float, default=0.6, nullable=False)
    peso_qualidade = Column(Float, default=0.3, nullable=False)
    peso_disponibilidade = Column(Float, default=0.1, nullable=False)
    
    # Configurações de failover
    failover_ativo = Column(Boolean, default=True, nullable=False)
    max_tentativas = Column(Integer, default=3, nullable=False)
    timeout_selecao = Column(Integer, default=5, nullable=False)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConfiguracaoMultiSip(id={self.id}, nome={self.nome})>"

class LogSelecaoProvedor(Base):
    __tablename__ = "log_selecao_provedor"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid_selecao = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Dados da chamada
    numero_destino = Column(String(20), nullable=False)
    campanha_id = Column(Integer, nullable=True)
    
    # Provedor selecionado
    provedor_id = Column(Integer, ForeignKey("provedor_sip.id"), nullable=False)
    metodo_selecao = Column(String(50), default="inteligente", nullable=False)
    
    # Resultado
    sucesso = Column(Boolean, default=True, nullable=False)
    custo_estimado = Column(DECIMAL(10, 6), nullable=True)
    latencia_ms = Column(Integer, nullable=True)
    
    # Timestamp
    timestamp_selecao = Column(DateTime, default=func.now(), nullable=False)
    
    # Dados extras
    dados_extras = Column(Text, nullable=True)
    
    # Relationships
    provedor = relationship("ProvedorSip", back_populates="logs_selecao")
    
    def __repr__(self):
        return f"<LogSelecaoProvedor(id={self.id}, uuid={self.uuid_selecao}, provedor_id={self.provedor_id})>" 