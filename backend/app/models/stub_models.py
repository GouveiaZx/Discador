# Modelos stub básicos para resolver imports
# Este arquivo contém modelos básicos para evitar erros de importação
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON
from datetime import datetime
from . import Base

# Modelos para DNC
class DNCList(Base):
    __tablename__ = "dnc_lists"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class DNCNumber(Base):
    __tablename__ = "dnc_numbers"
    id = Column(Integer, primary_key=True)
    numero = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

# Modelos para Trunk
class Trunk(Base):
    __tablename__ = "trunks"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TrunkEstatistica(Base):
    __tablename__ = "trunk_estadisticas"
    id = Column(Integer, primary_key=True)
    trunk_id = Column(Integer, ForeignKey("trunks.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class TrunkLog(Base):
    __tablename__ = "trunk_logs"
    id = Column(Integer, primary_key=True)
    trunk_id = Column(Integer, ForeignKey("trunks.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

# Modelos para Monitoring
class AgenteMonitoramento(Base):
    __tablename__ = "agentes_monitoramento"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EventoSistema(Base):
    __tablename__ = "eventos_sistema"
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class SessionMonitoramento(Base):
    __tablename__ = "sessions_monitoramento"
    id = Column(Integer, primary_key=True)
    agente_id = Column(Integer, ForeignKey("agentes_monitoramento.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

# Modelos para Multi SIP
class ProvedorSip(Base):
    __tablename__ = "provedores_sip"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TarifaSip(Base):
    __tablename__ = "tarifas_sip"
    id = Column(Integer, primary_key=True)
    proveedor_id = Column(Integer, ForeignKey("provedores_sip.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class ConfiguracaoMultiSip(Base):
    __tablename__ = "configuracao_multi_sip"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class LogSelecaoProvedor(Base):
    __tablename__ = "log_selecao_provedor"
    id = Column(Integer, primary_key=True)
    proveedor_id = Column(Integer, ForeignKey("provedores_sip.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

# Modelos para Audio Sistema
class TipoEvento(Base):
    __tablename__ = "tipos_evento"
    id = Column(Integer, primary_key=True)
    nome = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class EstadoAudio(Base):
    __tablename__ = "estados_audio"
    id = Column(Integer, primary_key=True)
    nome = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class AudioSessao(Base):
    __tablename__ = "audio_sessoes"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class AudioEvento(Base):
    __tablename__ = "audio_eventos"
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

# Modelos para Campanha Política
class CampanhaPolitica(Base):
    __tablename__ = "campanhas_politicas"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100))
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EstadisticaCampanha(Base):
    __tablename__ = "estadisticas_campanhas"
    id = Column(Integer, primary_key=True)
    campanha_id = Column(Integer, ForeignKey("campanhas_politicas.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class ConfiguracaoCampanha(Base):
    __tablename__ = "configuracoes_campanhas"
    id = Column(Integer, primary_key=True)
    campanha_id = Column(Integer, ForeignKey("campanhas_politicas.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

# Modelos para Presione1
class CampanaPresione1(Base):
    __tablename__ = "campanas_presione1"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100))
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LlamadaPresione1(Base):
    __tablename__ = "llamadas_presione1"
    id = Column(Integer, primary_key=True)
    campana_id = Column(Integer, ForeignKey("campanas_presione1.id"))
    numero_destino = Column(String(20))
    presiono_1 = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Modelos para Code2Base
class Pais(Base):
    __tablename__ = "paises"
    id = Column(Integer, primary_key=True)
    codigo = Column(String(10))
    nome = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Estado(Base):
    __tablename__ = "estados"
    id = Column(Integer, primary_key=True)
    pais_id = Column(Integer, ForeignKey("paises.id"))
    nome = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Cidade(Base):
    __tablename__ = "cidades"
    id = Column(Integer, primary_key=True)
    estado_id = Column(Integer, ForeignKey("estados.id"))
    nome = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Prefijo(Base):
    __tablename__ = "prefijos"
    id = Column(Integer, primary_key=True)
    codigo = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

class ReglaCli(Base):
    __tablename__ = "reglas_cli"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class CliGeo(Base):
    __tablename__ = "cli_geo"
    id = Column(Integer, primary_key=True)
    cli_id = Column(Integer)
    prefijo_id = Column(Integer, ForeignKey("prefijos.id"))
    numero_normalizado = Column(String(20))
    tipo_numero = Column(String(20))
    operadora = Column(String(100))
    calidad = Column(Float, default=0.0)
    tasa_exito = Column(Float, default=0.0)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Modelos para Configuração de Discagem
class ConfiguracaoDiscagem(Base):
    __tablename__ = "configuracao_discagem"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class ConfiguracaoAvancada(Base):
    __tablename__ = "configuracao_avancada"
    id = Column(Integer, primary_key=True)
    configuracao_id = Column(Integer, ForeignKey("configuracao_discagem.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class ConfiguracaoTiming(Base):
    __tablename__ = "configuracao_timing"
    id = Column(Integer, primary_key=True)
    configuracao_id = Column(Integer, ForeignKey("configuracao_discagem.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class ConfiguracaoAlgoritmo(Base):
    __tablename__ = "configuracao_algoritmo"
    id = Column(Integer, primary_key=True)
    configuracao_id = Column(Integer, ForeignKey("configuracao_discagem.id"))
    created_at = Column(DateTime, default=datetime.utcnow) 

# Enumerações como classes para compatibilidade
class TipoOperadora:
    DESCONOCIDA = "desconocida"
    CLARO = "claro"
    MOVISTAR = "movistar"
    PERSONAL = "personal"
    OTROS = "otros"

class TipoRegra:
    GEOGRAFIA = "geografia"
    OPERADORA = "operadora"
    CALIDAD = "calidad"
    TIEMPO = "tiempo"

class TipoNumero:
    MOVIL = "movil"
    FIJO = "fijo"
    ESPECIAL = "especial" 

class ConfiguracaoEleitoral(Base):
    __tablename__ = "configuracao_eleitoral"
    id = Column(Integer, primary_key=True)
    pais_codigo = Column(String(10))
    nome = Column(String(100))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CalendarioEleitoral(Base):
    __tablename__ = "calendario_eleitoral"
    id = Column(Integer, primary_key=True)
    pais_codigo = Column(String(10))
    nome_eleicao = Column(String(100))
    data_eleicao = Column(DateTime)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LogEleitoralImutavel(Base):
    __tablename__ = "log_eleitoral_imutavel"
    id = Column(Integer, primary_key=True)
    tipo_log = Column(String(50))
    dados = Column(JSON)
    hash_integridade = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class OptOutEleitoral(Base):
    __tablename__ = "opt_out_eleitoral"
    id = Column(Integer, primary_key=True)
    numero_telefone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

class StatusCampanhaPolitica(Base):
    __tablename__ = "status_campanha_politica"
    id = Column(Integer, primary_key=True)
    nome = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

# Enumeração para Tipo de Log Eleitoral
class TipoLogEleitoral:
    INICIO_CAMPANHA = "inicio_campanha"
    PARADA_CAMPANHA = "parada_campanha"
    CONFIGURACAO_ALTERADA = "configuracao_alterada"
    CHAMADA_REALIZADA = "chamada_realizada"
    ERRO_SISTEMA = "erro_sistema" 