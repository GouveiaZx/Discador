-- Migração Completa: Tabelas Faltantes do Sistema Discador
-- Sistema Audio Inteligente, CODE2BASE, Campanha Política e Monitoramento
-- Data: 2025-01-07

-- ==================================================
-- SISTEMA AUDIO INTELIGENTE
-- ==================================================

-- Enum Estado Audio
CREATE TYPE estado_audio AS ENUM (
    'aguardando_inicio', 'audio_reproduzindo', 'aguardando_dtmf', 'dtmf_recebido',
    'transferindo', 'transferencia_concluida', 'voicemail_detectado',
    'audio_voicemail_reproduzindo', 'finalizada', 'erro'
);

-- Enum Tipo Evento
CREATE TYPE tipo_evento_audio AS ENUM (
    'audio_iniciado', 'audio_finalizado', 'dtmf_recebido', 'voicemail_detectado',
    'transferencia_iniciada', 'transferencia_finalizada', 'erro_detectado',
    'timeout_atingido', 'regra_aplicada', 'contexto_alterado',
    'sessao_iniciada', 'sessao_finalizada'
);

-- Enum Tipo Operador Regra
CREATE TYPE tipo_operador_regra AS ENUM (
    'igual', 'diferente', 'contem', 'nao_contem', 'maior_que',
    'menor_que', 'maior_igual', 'menor_igual', 'regex'
);

-- Audio Contexto
CREATE TABLE audio_contexto (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    contexto_asterisk VARCHAR(100) NOT NULL,
    prioridade INTEGER DEFAULT 1,
    timeout_padrao INTEGER DEFAULT 10 CHECK (timeout_padrao >= 1 AND timeout_padrao <= 300),
    max_tentativas INTEGER DEFAULT 3 CHECK (max_tentativas >= 1 AND max_tentativas <= 10),
    permite_voicemail BOOLEAN DEFAULT true,
    permite_transferencia BOOLEAN DEFAULT true,
    log_detalhado BOOLEAN DEFAULT false,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMPTZ DEFAULT now(),
    atualizado_em TIMESTAMPTZ DEFAULT now()
);

-- Audio Regra
CREATE TABLE audio_regra (
    id SERIAL PRIMARY KEY,
    contexto_id INTEGER REFERENCES audio_contexto(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    condicao_campo VARCHAR(50) NOT NULL,
    operador tipo_operador_regra NOT NULL,
    valor_comparacao TEXT,
    acao_resultante VARCHAR(50) NOT NULL,
    parametros_acao JSONB DEFAULT '{}',
    prioridade INTEGER DEFAULT 10,
    ativa BOOLEAN DEFAULT true,
    descricao TEXT,
    criado_em TIMESTAMPTZ DEFAULT now(),
    atualizado_em TIMESTAMPTZ DEFAULT now()
);

-- Audio Sessão
CREATE TABLE audio_sessao (
    id SERIAL PRIMARY KEY,
    contexto_id INTEGER REFERENCES audio_contexto(id) ON DELETE CASCADE,
    call_id VARCHAR(100) NOT NULL UNIQUE,
    unique_id_asterisk VARCHAR(100),
    canal_asterisk VARCHAR(100),
    numero_origem VARCHAR(20),
    numero_destino VARCHAR(20),
    cli_utilizado VARCHAR(20),
    estado_atual estado_audio DEFAULT 'aguardando_inicio',
    estado_anterior estado_audio,
    data_mudanca_estado TIMESTAMPTZ DEFAULT now(),
    tentativas_atuais INTEGER DEFAULT 0,
    timeout_configurado INTEGER DEFAULT 10,
    audio_url VARCHAR(500),
    audio_voicemail_url VARCHAR(500),
    dtmf_detectado VARCHAR(10),
    timestamp_dtmf TIMESTAMPTZ,
    voicemail_detectado BOOLEAN DEFAULT false,
    timestamp_voicemail TIMESTAMPTZ,
    transferencia_realizada BOOLEAN DEFAULT false,
    numero_transferencia VARCHAR(20),
    timestamp_transferencia TIMESTAMPTZ,
    duracao_total INTEGER DEFAULT 0,
    metadados JSONB DEFAULT '{}',
    iniciado_em TIMESTAMPTZ DEFAULT now(),
    finalizado_em TIMESTAMPTZ,
    resultado_final VARCHAR(50),
    motivo_finalizacao TEXT
);

-- Audio Evento
CREATE TABLE audio_evento (
    id SERIAL PRIMARY KEY,
    sessao_id INTEGER REFERENCES audio_sessao(id) ON DELETE CASCADE,
    tipo_evento tipo_evento_audio NOT NULL,
    descricao TEXT,
    dados_evento JSONB DEFAULT '{}',
    timestamp_evento TIMESTAMPTZ DEFAULT now(),
    estado_antes estado_audio,
    estado_depois estado_audio,
    regra_aplicada_id INTEGER REFERENCES audio_regra(id),
    sucesso BOOLEAN DEFAULT true,
    erro_detalhes TEXT
);

-- Audio Template
CREATE TABLE audio_template (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    tipo VARCHAR(50) NOT NULL,
    audio_url VARCHAR(500),
    descricao TEXT,
    parametros_configuracao JSONB DEFAULT '{}',
    usado_por_contexto INTEGER[] DEFAULT '{}',
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMPTZ DEFAULT now(),
    atualizado_em TIMESTAMPTZ DEFAULT now()
);

-- ==================================================
-- SISTEMA CODE2BASE - SELEÇÃO INTELIGENTE DE CLI
-- ==================================================

-- Enum Tipo Operadora
CREATE TYPE tipo_operadora AS ENUM (
    'vivo', 'claro', 'tim', 'oi', 'nextel', 'algar', 'sercomtel',
    'unifique', 'brisanet', 'outras', 'fixo', 'internacional'
);

-- Enum Tipo Regra
CREATE TYPE tipo_regra_cli AS ENUM (
    'por_geografia', 'por_operadora', 'por_qualidade', 'por_horario',
    'por_volume', 'por_custo', 'balanceamento', 'por_prefixo', 'personalizada'
);

-- Enum Tipo Número
CREATE TYPE tipo_numero AS ENUM (
    'celular', 'fixo', 'especial', 'internacional', 'voip', 'outros'
);

-- País
CREATE TABLE pais (
    id SERIAL PRIMARY KEY,
    codigo_iso VARCHAR(3) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    codigo_telefone VARCHAR(5) NOT NULL,
    formato_numero VARCHAR(50),
    ativo BOOLEAN DEFAULT true
);

-- Estado
CREATE TABLE estado (
    id SERIAL PRIMARY KEY,
    pais_id INTEGER REFERENCES pais(id) ON DELETE CASCADE,
    codigo VARCHAR(5) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    sigla VARCHAR(5) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'America/Sao_Paulo',
    ativo BOOLEAN DEFAULT true,
    UNIQUE(pais_id, codigo)
);

-- Cidade
CREATE TABLE cidade (
    id SERIAL PRIMARY KEY,
    estado_id INTEGER REFERENCES estado(id) ON DELETE CASCADE,
    codigo_ibge VARCHAR(10),
    nome VARCHAR(100) NOT NULL,
    ddd VARCHAR(3),
    populacao INTEGER DEFAULT 0,
    longitude DECIMAL(10, 7),
    latitude DECIMAL(10, 7),
    ativo BOOLEAN DEFAULT true
);

-- Prefixo
CREATE TABLE prefixo (
    id SERIAL PRIMARY KEY,
    cidade_id INTEGER REFERENCES cidade(id) ON DELETE CASCADE,
    prefixo VARCHAR(10) NOT NULL,
    operadora tipo_operadora NOT NULL,
    tipo_numero tipo_numero NOT NULL,
    qualidade_score DECIMAL(3, 2) DEFAULT 0.80 CHECK (qualidade_score >= 0 AND qualidade_score <= 1),
    custo_por_minuto DECIMAL(8, 4) DEFAULT 0.10,
    limite_cps INTEGER DEFAULT 5,
    ativo BOOLEAN DEFAULT true,
    observacoes TEXT,
    UNIQUE(prefixo, operadora)
);

-- CLI Geo
CREATE TABLE cli_geo (
    id SERIAL PRIMARY KEY,
    cli VARCHAR(20) NOT NULL UNIQUE,
    cidade_id INTEGER REFERENCES cidade(id) ON DELETE SET NULL,
    operadora tipo_operadora NOT NULL,
    tipo_numero tipo_numero NOT NULL,
    qualidade_historica DECIMAL(3, 2) DEFAULT 0.80,
    total_chamadas INTEGER DEFAULT 0,
    chamadas_conectadas INTEGER DEFAULT 0,
    chamadas_com_dtmf INTEGER DEFAULT 0,
    ultima_utilizacao TIMESTAMPTZ,
    bloqueado BOOLEAN DEFAULT false,
    motivo_bloqueio TEXT,
    custo_por_minuto DECIMAL(8, 4) DEFAULT 0.10,
    limite_diario INTEGER DEFAULT 1000,
    usado_hoje INTEGER DEFAULT 0,
    ativo BOOLEAN DEFAULT true,
    metadados JSONB DEFAULT '{}',
    criado_em TIMESTAMPTZ DEFAULT now(),
    atualizado_em TIMESTAMPTZ DEFAULT now()
);

-- Regla CLI
CREATE TABLE regla_cli (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    tipo_regra tipo_regra_cli NOT NULL,
    prioridade INTEGER DEFAULT 10,
    condicoes JSONB NOT NULL DEFAULT '{}',
    acao_selecao JSONB NOT NULL DEFAULT '{}',
    fallback_regra_id INTEGER REFERENCES regla_cli(id),
    ativa BOOLEAN DEFAULT true,
    descricao TEXT,
    estatisticas JSONB DEFAULT '{}',
    criado_em TIMESTAMPTZ DEFAULT now(),
    atualizado_em TIMESTAMPTZ DEFAULT now()
);

-- Historial Selección CLI
CREATE TABLE historial_seleccion_cli (
    id SERIAL PRIMARY KEY,
    numero_destino VARCHAR(20) NOT NULL,
    cli_selecionado VARCHAR(20) NOT NULL,
    regra_aplicada_id INTEGER REFERENCES regla_cli(id),
    motivo_selecao TEXT,
    call_id VARCHAR(100),
    campaign_id INTEGER,
    timestamp_selecao TIMESTAMPTZ DEFAULT now(),
    resultado_chamada VARCHAR(50),
    duracao_chamada INTEGER DEFAULT 0,
    dtmf_detectado VARCHAR(10),
    qualidade_obtida DECIMAL(3, 2),
    custo_real DECIMAL(8, 4),
    observacoes TEXT
);

-- ==================================================
-- SISTEMA CAMPANHA POLÍTICA - CONFORMIDADE ELEITORAL
-- ==================================================

-- Enum Tipo Eleição
CREATE TYPE tipo_eleicao AS ENUM (
    'municipal', 'estadual', 'federal', 'referendo', 'plebiscito'
);

-- Enum Status Campanha Política
CREATE TYPE status_campanha_politica AS ENUM (
    'planejamento', 'aprovada', 'ativa', 'pausada', 'finalizada', 'cancelada'
);

-- Enum Tipo Log Eleitoral
CREATE TYPE tipo_log_eleitoral AS ENUM (
    'criacao_campanha', 'inicio_discagem', 'pausa_campanha', 'fim_discagem',
    'alteracao_configuracao', 'violacao_detectada', 'auditoria_externa'
);

-- Configuração Eleitoral
CREATE TABLE configuracao_eleitoral (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    tipo_eleicao tipo_eleicao NOT NULL,
    ano_eleitoral INTEGER NOT NULL,
    horario_inicio_permitido TIME DEFAULT '08:00:00',
    horario_fim_permitido TIME DEFAULT '22:00:00',
    dias_semana_permitidos INTEGER[] DEFAULT '{1,2,3,4,5,6}',
    max_tentativas_numero INTEGER DEFAULT 3,
    intervalo_minimo_tentativas INTEGER DEFAULT 86400,
    limite_diario_numeros INTEGER DEFAULT 10000,
    requer_opt_in BOOLEAN DEFAULT true,
    permite_voicemail BOOLEAN DEFAULT false,
    duracao_maxima_audio INTEGER DEFAULT 60,
    requer_identificacao_candidato BOOLEAN DEFAULT true,
    registro_tse VARCHAR(20),
    partido_politico VARCHAR(10),
    candidato_nome VARCHAR(200),
    candidato_numero VARCHAR(10),
    cargo_disputado VARCHAR(100),
    municipio_candidatura VARCHAR(100),
    estado_candidatura VARCHAR(5),
    observacoes_legais TEXT,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMPTZ DEFAULT now(),
    atualizado_em TIMESTAMPTZ DEFAULT now()
);

-- Calendario Eleitoral
CREATE TABLE calendario_eleitoral (
    id SERIAL PRIMARY KEY,
    configuracao_id INTEGER REFERENCES configuracao_eleitoral(id) ON DELETE CASCADE,
    data_evento DATE NOT NULL,
    tipo_evento VARCHAR(50) NOT NULL,
    descricao TEXT,
    permite_campanha BOOLEAN DEFAULT true,
    restricoes_especiais JSONB DEFAULT '{}',
    criado_em TIMESTAMPTZ DEFAULT now()
);

-- Campanha Política
CREATE TABLE campanha_politica (
    id SERIAL PRIMARY KEY,
    configuracao_eleitoral_id INTEGER REFERENCES configuracao_eleitoral(id) ON DELETE CASCADE,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    nome VARCHAR(200) NOT NULL,
    numero_candidato VARCHAR(10) NOT NULL,
    partido VARCHAR(10) NOT NULL,
    cargo VARCHAR(100) NOT NULL,
    municipio VARCHAR(100),
    estado VARCHAR(5),
    status status_campanha_politica DEFAULT 'planejamento',
    data_inicio_planejada DATE,
    data_fim_planejada DATE,
    data_inicio_real TIMESTAMPTZ,
    data_fim_real TIMESTAMPTZ,
    total_contatos_autorizados INTEGER DEFAULT 0,
    total_chamadas_realizadas INTEGER DEFAULT 0,
    total_opt_outs INTEGER DEFAULT 0,
    audio_identificacao_url VARCHAR(500),
    texto_identificacao TEXT,
    hash_auditoria VARCHAR(128) UNIQUE,
    aprovado_por VARCHAR(100),
    aprovado_em TIMESTAMPTZ,
    observacoes TEXT,
    metadados_conformidade JSONB DEFAULT '{}',
    criado_em TIMESTAMPTZ DEFAULT now(),
    atualizado_em TIMESTAMPTZ DEFAULT now()
);

-- Log Eleitoral Imutável
CREATE TABLE log_eleitoral_imutavel (
    id SERIAL PRIMARY KEY,
    campanha_politica_id INTEGER REFERENCES campanha_politica(id) ON DELETE CASCADE,
    tipo_evento tipo_log_eleitoral NOT NULL,
    timestamp_evento TIMESTAMPTZ DEFAULT now(),
    usuario_responsavel VARCHAR(100),
    dados_evento JSONB NOT NULL,
    hash_anterior VARCHAR(128),
    hash_atual VARCHAR(128) NOT NULL UNIQUE,
    assinatura_digital TEXT,
    ip_origem INET,
    user_agent TEXT,
    verificado BOOLEAN DEFAULT false,
    observacoes TEXT
);

-- Opt Out Eleitoral
CREATE TABLE opt_out_eleitoral (
    id SERIAL PRIMARY KEY,
    numero_telefone VARCHAR(20) NOT NULL,
    campanha_politica_id INTEGER REFERENCES campanha_politica(id) ON DELETE CASCADE,
    motivo VARCHAR(100),
    data_opt_out TIMESTAMPTZ DEFAULT now(),
    canal_opt_out VARCHAR(50) DEFAULT 'telefone',
    ip_origem INET,
    confirmado BOOLEAN DEFAULT false,
    data_confirmacao TIMESTAMPTZ,
    valido_ate DATE,
    observacoes TEXT,
    UNIQUE(numero_telefone, campanha_politica_id)
);

-- Exportação Eleitoral
CREATE TABLE exportacao_eleitoral (
    id SERIAL PRIMARY KEY,
    campanha_politica_id INTEGER REFERENCES campanha_politica(id) ON DELETE CASCADE,
    tipo_exportacao VARCHAR(50) NOT NULL,
    solicitado_por VARCHAR(100) NOT NULL,
    data_solicitacao TIMESTAMPTZ DEFAULT now(),
    data_inicio_periodo DATE NOT NULL,
    data_fim_periodo DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pendente',
    arquivo_gerado_url VARCHAR(500),
    hash_arquivo VARCHAR(128),
    dados_criptografados BYTEA,
    chave_criptografia_hash VARCHAR(128),
    data_geracao TIMESTAMPTZ,
    data_expiracao TIMESTAMPTZ,
    total_registros INTEGER DEFAULT 0,
    observacoes TEXT
);

-- ==================================================
-- SISTEMA MONITORAMENTO - TEMPO REAL
-- ==================================================

-- Enum Status Agente
CREATE TYPE status_agente AS ENUM (
    'online', 'offline', 'ocupado', 'pausado', 'erro'
);

-- Enum Status Chamada
CREATE TYPE status_chamada AS ENUM (
    'iniciando', 'tocando', 'atendida', 'falha', 'ocupado',
    'nao_atende', 'transferindo', 'transferida', 'finalizada'
);

-- Enum Tipo Evento Monitoramento
CREATE TYPE tipo_evento_monitoramento AS ENUM (
    'login_agente', 'logout_agente', 'inicio_chamada', 'fim_chamada',
    'pausa_campanha', 'resume_campanha', 'erro_sistema', 'alerta_performance',
    'transferencia_realizada', 'dtmf_detectado'
);

-- Enum Nível Severidade
CREATE TYPE nivel_severidade AS ENUM (
    'info', 'warning', 'error', 'critical'
);

-- Agente Monitoramento
CREATE TABLE agente_monitoramento (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    nome_agente VARCHAR(100) NOT NULL,
    extension VARCHAR(20),
    status_atual status_agente DEFAULT 'offline',
    ultima_atividade TIMESTAMPTZ DEFAULT now(),
    campanhas_ativas INTEGER[] DEFAULT '{}',
    chamadas_em_andamento INTEGER DEFAULT 0,
    total_chamadas_hoje INTEGER DEFAULT 0,
    tempo_online_hoje INTEGER DEFAULT 0,
    qualidade_media DECIMAL(3, 2) DEFAULT 0.80,
    configuracoes JSONB DEFAULT '{}',
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMPTZ DEFAULT now(),
    atualizado_em TIMESTAMPTZ DEFAULT now()
);

-- Chamada Monitoramento
CREATE TABLE chamada_monitoramento (
    id SERIAL PRIMARY KEY,
    agente_id INTEGER REFERENCES agente_monitoramento(id) ON DELETE SET NULL,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    call_id VARCHAR(100) NOT NULL UNIQUE,
    numero_origem VARCHAR(20),
    numero_destino VARCHAR(20) NOT NULL,
    cli_utilizado VARCHAR(20),
    status_atual status_chamada DEFAULT 'iniciando',
    inicio_chamada TIMESTAMPTZ DEFAULT now(),
    atendimento_chamada TIMESTAMPTZ,
    fim_chamada TIMESTAMPTZ,
    duracao_total INTEGER DEFAULT 0,
    duracao_conversa INTEGER DEFAULT 0,
    canal_asterisk VARCHAR(100),
    codec_utilizado VARCHAR(20),
    qualidade_audio FLOAT,
    metadados JSONB DEFAULT '{}',
    resultado_final VARCHAR(50),
    dtmf_recebido VARCHAR(10),
    transferida_para VARCHAR(20),
    observacoes TEXT
);

-- Evento Sistema
CREATE TABLE evento_sistema (
    id SERIAL PRIMARY KEY,
    tipo_evento tipo_evento_monitoramento NOT NULL,
    severidade nivel_severidade DEFAULT 'info',
    timestamp_evento TIMESTAMPTZ DEFAULT now(),
    origem_sistema VARCHAR(50) NOT NULL,
    agente_relacionado INTEGER REFERENCES agente_monitoramento(id),
    chamada_relacionada INTEGER REFERENCES chamada_monitoramento(id),
    dados_evento JSONB DEFAULT '{}',
    mensagem TEXT,
    stack_trace TEXT,
    resolvido BOOLEAN DEFAULT false,
    resolvido_por VARCHAR(100),
    resolvido_em TIMESTAMPTZ,
    observacoes TEXT
);

-- Session Monitoramento
CREATE TABLE session_monitoramento (
    id SERIAL PRIMARY KEY,
    agente_id INTEGER REFERENCES agente_monitoramento(id) ON DELETE CASCADE,
    session_token VARCHAR(128) NOT NULL UNIQUE,
    inicio_sessao TIMESTAMPTZ DEFAULT now(),
    fim_sessao TIMESTAMPTZ,
    ip_origem INET,
    user_agent TEXT,
    ativa BOOLEAN DEFAULT true,
    dados_sessao JSONB DEFAULT '{}',
    ultima_atividade TIMESTAMPTZ DEFAULT now()
);

-- Cache Métricas
CREATE TABLE cache_metricas (
    id SERIAL PRIMARY KEY,
    chave_cache VARCHAR(100) NOT NULL UNIQUE,
    dados_metricas JSONB NOT NULL,
    timestamp_geracao TIMESTAMPTZ DEFAULT now(),
    expiracao TIMESTAMPTZ NOT NULL,
    tipo_metrica VARCHAR(50) NOT NULL,
    relacionado_id INTEGER,
    relacionado_tipo VARCHAR(50),
    versao_cache INTEGER DEFAULT 1
);

-- Heartbeat Agente
CREATE TABLE heartbeat_agente (
    id SERIAL PRIMARY KEY,
    agente_id INTEGER REFERENCES agente_monitoramento(id) ON DELETE CASCADE,
    timestamp_heartbeat TIMESTAMPTZ DEFAULT now(),
    status_reportado status_agente NOT NULL,
    metricas_sistema JSONB DEFAULT '{}',
    latencia_ms INTEGER DEFAULT 0,
    memoria_uso_mb INTEGER DEFAULT 0,
    cpu_uso_pct DECIMAL(5, 2) DEFAULT 0.0,
    campanhas_ativas INTEGER[] DEFAULT '{}',
    observacoes TEXT
);

-- ==================================================
-- ÍNDICES PARA PERFORMANCE
-- ==================================================

-- Audio Sistema
CREATE INDEX idx_audio_sessao_call_id ON audio_sessao(call_id);
CREATE INDEX idx_audio_sessao_estado ON audio_sessao(estado_atual);
CREATE INDEX idx_audio_evento_sessao_tipo ON audio_evento(sessao_id, tipo_evento);
CREATE INDEX idx_audio_regra_contexto_prioridade ON audio_regra(contexto_id, prioridade);

-- CODE2BASE
CREATE INDEX idx_cli_geo_cidade_ativo ON cli_geo(cidade_id, ativo);
CREATE INDEX idx_cli_geo_operadora_qualidade ON cli_geo(operadora, qualidade_historica);
CREATE INDEX idx_historial_cli_timestamp ON historial_seleccion_cli(timestamp_selecao);
CREATE INDEX idx_prefixo_operadora_ativo ON prefixo(operadora, ativo);

-- Campanha Política
CREATE INDEX idx_campanha_politica_status ON campanha_politica(status);
CREATE INDEX idx_campanha_politica_candidato ON campanha_politica(numero_candidato, partido);
CREATE INDEX idx_log_eleitoral_campanha_timestamp ON log_eleitoral_imutavel(campanha_politica_id, timestamp_evento);
CREATE INDEX idx_opt_out_telefone ON opt_out_eleitoral(numero_telefone);

-- Monitoramento
CREATE INDEX idx_agente_monitoramento_status ON agente_monitoramento(status_atual, ativo);
CREATE INDEX idx_chamada_monitoramento_call_id ON chamada_monitoramento(call_id);
CREATE INDEX idx_chamada_monitoramento_status_timestamp ON chamada_monitoramento(status_atual, inicio_chamada);
CREATE INDEX idx_evento_sistema_timestamp_severidade ON evento_sistema(timestamp_evento, severidade);
CREATE INDEX idx_cache_metricas_chave_expiracao ON cache_metricas(chave_cache, expiracao);
CREATE INDEX idx_heartbeat_agente_timestamp ON heartbeat_agente(agente_id, timestamp_heartbeat);

-- ==================================================
-- TRIGGERS PARA TIMESTAMPS AUTOMÁTICOS
-- ==================================================

-- Função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para Audio Sistema
CREATE TRIGGER update_audio_contexto_updated_at BEFORE UPDATE ON audio_contexto FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_audio_regra_updated_at BEFORE UPDATE ON audio_regra FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_audio_template_updated_at BEFORE UPDATE ON audio_template FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Triggers para CODE2BASE
CREATE TRIGGER update_cli_geo_updated_at BEFORE UPDATE ON cli_geo FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_regla_cli_updated_at BEFORE UPDATE ON regla_cli FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Triggers para Campanha Política
CREATE TRIGGER update_configuracao_eleitoral_updated_at BEFORE UPDATE ON configuracao_eleitoral FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campanha_politica_updated_at BEFORE UPDATE ON campanha_politica FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Triggers para Monitoramento
CREATE TRIGGER update_agente_monitoramento_updated_at BEFORE UPDATE ON agente_monitoramento FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================================================
-- DADOS INICIAIS
-- ==================================================

-- País padrão
INSERT INTO pais (codigo_iso, nome, codigo_telefone, formato_numero) 
VALUES ('BRA', 'Brasil', '+55', '(DD) NNNNN-NNNN');

-- Estados brasileiros principais
INSERT INTO estado (pais_id, codigo, nome, sigla, timezone) VALUES
((SELECT id FROM pais WHERE codigo_iso = 'BRA'), '11', 'São Paulo', 'SP', 'America/Sao_Paulo'),
((SELECT id FROM pais WHERE codigo_iso = 'BRA'), '21', 'Rio de Janeiro', 'RJ', 'America/Sao_Paulo'),
((SELECT id FROM pais WHERE codigo_iso = 'BRA'), '31', 'Minas Gerais', 'MG', 'America/Sao_Paulo'),
((SELECT id FROM pais WHERE codigo_iso = 'BRA'), '41', 'Paraná', 'PR', 'America/Sao_Paulo'),
((SELECT id FROM pais WHERE codigo_iso = 'BRA'), '51', 'Rio Grande do Sul', 'RS', 'America/Sao_Paulo');

-- Configuração eleitoral padrão
INSERT INTO configuracao_eleitoral (
    nome, tipo_eleicao, ano_eleitoral, registro_tse, 
    partido_politico, observacoes_legais
) VALUES (
    'Configuração Padrão 2024', 'municipal', 2024, 'TSE-2024-DEFAULT',
    'GENÉRICO', 'Configuração base para campanhas municipais conforme Lei 9.504/97'
);

-- Templates de áudio padrão
INSERT INTO audio_template (nome, tipo, descricao) VALUES
('Saudação Padrão', 'saudacao', 'Template padrão para saudação inicial'),
('Aguardando DTMF', 'aguardo', 'Template para aguardar tecla 1'),
('Mensagem Voicemail', 'voicemail', 'Template para deixar mensagem em caixa postal');

-- Contexto de áudio padrão
INSERT INTO audio_contexto (nome, descricao, contexto_asterisk) VALUES
('Presione1 Padrão', 'Contexto padrão para campanhas Presione 1', 'presione1-context');

COMMENT ON TABLE audio_contexto IS 'Sistema de áudio inteligente com máquina de estados';
COMMENT ON TABLE cli_geo IS 'Sistema CODE2BASE para seleção inteligente de CLIs por geografia';
COMMENT ON TABLE campanha_politica IS 'Sistema de campanhas políticas com conformidade eleitoral';
COMMENT ON TABLE agente_monitoramento IS 'Sistema de monitoramento em tempo real com WebSocket'; 