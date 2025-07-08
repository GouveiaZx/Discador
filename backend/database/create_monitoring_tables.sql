-- ===============================================
-- TABELAS PARA SISTEMA DE MONITORAMENTO EM TEMPO REAL
-- ===============================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===============================================
-- ENUMS PARA MONITORAMENTO
-- ===============================================

-- Status dos agentes
DROP TYPE IF EXISTS status_agente CASCADE;
CREATE TYPE status_agente AS ENUM (
    'livre',
    'em_chamada', 
    'ausente',
    'pausado',
    'offline'
);

-- Status das chamadas
DROP TYPE IF EXISTS status_chamada CASCADE;
CREATE TYPE status_chamada AS ENUM (
    'pendente',
    'marcando',
    'tocando',
    'atendida',
    'em_andamento',
    'transferida',
    'finalizada',
    'erro',
    'abandonada'
);

-- Tipos de eventos
DROP TYPE IF EXISTS tipo_evento CASCADE;
CREATE TYPE tipo_evento AS ENUM (
    'chamada_iniciada',
    'chamada_atendida',
    'chamada_finalizada',
    'agente_login',
    'agente_logout',
    'agente_pausa',
    'campanha_iniciada',
    'campanha_pausada',
    'provedor_falha',
    'provedor_recuperado'
);

-- Níveis de severidade
DROP TYPE IF EXISTS nivel_severidade CASCADE;
CREATE TYPE nivel_severidade AS ENUM (
    'info',
    'warning',
    'error',
    'critical'
);

-- ===============================================
-- TABELA DE AGENTES DE MONITORAMENTO
-- ===============================================

DROP TABLE IF EXISTS agente_monitoramento CASCADE;
CREATE TABLE agente_monitoramento (
    id SERIAL PRIMARY KEY,
    
    -- Identificação do agente
    nome_agente VARCHAR(100) NOT NULL,
    codigo_agente VARCHAR(20) NOT NULL UNIQUE,
    extensao_sip VARCHAR(50),
    email VARCHAR(100),
    
    -- Status atual
    status_atual status_agente NOT NULL DEFAULT 'offline',
    ultima_atualizacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Dados da sessão atual
    login_timestamp TIMESTAMP,
    chamada_atual_id VARCHAR(50),
    tempo_em_chamada INTEGER DEFAULT 0, -- segundos
    
    -- Estatísticas do dia
    total_chamadas_atendidas INTEGER DEFAULT 0,
    tempo_total_atendimento INTEGER DEFAULT 0, -- segundos
    tempo_total_pausa INTEGER DEFAULT 0, -- segundos
    
    -- Configurações
    max_chamadas_simultaneas INTEGER DEFAULT 1,
    skills JSONB, -- Habilidades do agente
    
    -- Auditoria
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para agentes
CREATE INDEX idx_agente_codigo ON agente_monitoramento(codigo_agente);
CREATE INDEX idx_agente_status ON agente_monitoramento(status_atual);
CREATE INDEX idx_agente_ultima_atualizacao ON agente_monitoramento(ultima_atualizacao);
CREATE INDEX idx_agente_activo ON agente_monitoramento(activo);

-- Trigger para atualizar fecha_actualizacion
CREATE OR REPLACE FUNCTION update_agente_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    NEW.ultima_atualizacao = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_agente_timestamp
    BEFORE UPDATE ON agente_monitoramento
    FOR EACH ROW
    EXECUTE FUNCTION update_agente_timestamp();

-- ===============================================
-- TABELA DE CHAMADAS DE MONITORAMENTO
-- ===============================================

DROP TABLE IF EXISTS chamada_monitoramento CASCADE;
CREATE TABLE chamada_monitoramento (
    id SERIAL PRIMARY KEY,
    
    -- Identificação única
    uuid_chamada UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    call_id_asterisk VARCHAR(100) UNIQUE,
    
    -- Dados básicos
    numero_origem VARCHAR(20),
    numero_destino VARCHAR(20) NOT NULL,
    campanha_id INTEGER,
    
    -- Status e timing
    status_atual status_chamada NOT NULL DEFAULT 'pendente',
    timestamp_inicio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    timestamp_atendida TIMESTAMP,
    timestamp_finalizada TIMESTAMP,
    
    -- Duração e métricas
    duracao_total INTEGER, -- segundos
    tempo_espera INTEGER, -- segundos até atender
    
    -- Provedor SIP utilizado
    provedor_sip_id INTEGER,
    provedor_nome VARCHAR(100),
    
    -- Agente responsável
    agente_id INTEGER REFERENCES agente_monitoramento(id),
    
    -- Resultado e dados
    resultado_chamada VARCHAR(50),
    dtmf_recebido VARCHAR(10),
    transferida_para VARCHAR(50),
    
    -- Dados técnicos
    canal_asterisk VARCHAR(100),
    codec_utilizado VARCHAR(20),
    qualidade_audio REAL,
    
    -- Metadados
    dados_extras JSONB,
    
    -- Auditoria
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para chamadas
CREATE INDEX idx_chamada_uuid ON chamada_monitoramento(uuid_chamada);
CREATE INDEX idx_chamada_call_id ON chamada_monitoramento(call_id_asterisk);
CREATE INDEX idx_chamada_status ON chamada_monitoramento(status_atual);
CREATE INDEX idx_chamada_campanha ON chamada_monitoramento(campanha_id);
CREATE INDEX idx_chamada_timestamp ON chamada_monitoramento(timestamp_inicio);
CREATE INDEX idx_chamada_provedor ON chamada_monitoramento(provedor_sip_id);
CREATE INDEX idx_chamada_agente ON chamada_monitoramento(agente_id);
CREATE INDEX idx_chamada_numero_destino ON chamada_monitoramento(numero_destino);

-- ===============================================
-- TABELA DE EVENTOS DO SISTEMA
-- ===============================================

DROP TABLE IF EXISTS evento_sistema CASCADE;
CREATE TABLE evento_sistema (
    id SERIAL PRIMARY KEY,
    
    -- Identificação do evento
    uuid_evento UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    tipo_evento tipo_evento NOT NULL,
    
    -- Dados do evento
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    dados_evento JSONB,
    
    -- Contexto
    campanha_id INTEGER,
    agente_id INTEGER,
    chamada_id VARCHAR(100),
    
    -- Severidade e status
    nivel_severidade nivel_severidade DEFAULT 'info',
    resolvido BOOLEAN DEFAULT false,
    
    -- Timestamp
    timestamp_evento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Usuário que visualizou
    visualizado_por JSONB -- Lista de user_ids
);

-- Índices para eventos
CREATE INDEX idx_evento_uuid ON evento_sistema(uuid_evento);
CREATE INDEX idx_evento_tipo ON evento_sistema(tipo_evento);
CREATE INDEX idx_evento_timestamp ON evento_sistema(timestamp_evento);
CREATE INDEX idx_evento_severidade ON evento_sistema(nivel_severidade);
CREATE INDEX idx_evento_resolvido ON evento_sistema(resolvido);
CREATE INDEX idx_evento_campanha ON evento_sistema(campanha_id);
CREATE INDEX idx_evento_agente ON evento_sistema(agente_id);

-- ===============================================
-- TABELA DE SESSÕES DE MONITORAMENTO
-- ===============================================

DROP TABLE IF EXISTS session_monitoramento CASCADE;
CREATE TABLE session_monitoramento (
    id SERIAL PRIMARY KEY,
    
    -- Identificação da sessão
    session_uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    usuario_id INTEGER NOT NULL,
    usuario_nome VARCHAR(100) NOT NULL,
    
    -- Dados da sessão
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamps
    login_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_timestamp TIMESTAMP,
    
    -- Atividade
    paginas_acessadas INTEGER DEFAULT 0,
    total_refreshes INTEGER DEFAULT 0,
    tempo_ativo INTEGER DEFAULT 0, -- segundos
    
    -- Status
    sessao_ativa BOOLEAN DEFAULT true
);

-- Índices para sessões
CREATE INDEX idx_session_uuid ON session_monitoramento(session_uuid);
CREATE INDEX idx_session_usuario ON session_monitoramento(usuario_id);
CREATE INDEX idx_session_ativa ON session_monitoramento(sessao_ativa);
CREATE INDEX idx_session_ultimo_acesso ON session_monitoramento(ultimo_acesso);

-- ===============================================
-- TABELA DE CACHE DE MÉTRICAS
-- ===============================================

DROP TABLE IF EXISTS cache_metricas CASCADE;
CREATE TABLE cache_metricas (
    id SERIAL PRIMARY KEY,
    
    -- Identificação do cache
    chave_cache VARCHAR(100) NOT NULL UNIQUE,
    tipo_metrica VARCHAR(50) NOT NULL,
    
    -- Dados em cache
    dados_json JSONB NOT NULL,
    
    -- Controle de validade
    timestamp_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    timestamp_expiracao TIMESTAMP NOT NULL,
    
    -- Metadados
    contexto JSONB, -- Dados adicionais do contexto
    versao_cache INTEGER DEFAULT 1
);

-- Índices para cache
CREATE INDEX idx_cache_chave ON cache_metricas(chave_cache);
CREATE INDEX idx_cache_expiracao ON cache_metricas(timestamp_expiracao);
CREATE INDEX idx_cache_tipo ON cache_metricas(tipo_metrica);

-- ===============================================
-- VIEWS PARA CONSULTAS OTIMIZADAS
-- ===============================================

-- View de estatísticas de agentes
CREATE OR REPLACE VIEW v_agentes_estatisticas AS
SELECT 
    a.id,
    a.nome_agente,
    a.codigo_agente,
    a.status_atual,
    a.login_timestamp,
    a.total_chamadas_atendidas,
    a.tempo_total_atendimento,
    a.tempo_total_pausa,
    
    -- Chamadas ativas do agente
    COUNT(c.id) FILTER (WHERE c.status_atual IN ('atendida', 'em_andamento')) AS chamadas_ativas,
    
    -- Tempo médio por chamada
    CASE 
        WHEN a.total_chamadas_atendidas > 0 
        THEN a.tempo_total_atendimento / a.total_chamadas_atendidas 
        ELSE 0 
    END AS tempo_medio_por_chamada,
    
    -- Taxa de ocupação (% do tempo online em chamada)
    CASE 
        WHEN a.login_timestamp IS NOT NULL 
        THEN (a.tempo_total_atendimento::REAL / EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.login_timestamp))) * 100
        ELSE 0 
    END AS taxa_ocupacao
    
FROM agente_monitoramento a
LEFT JOIN chamada_monitoramento c ON a.id = c.agente_id
WHERE a.activo = true
GROUP BY a.id;

-- View de estatísticas de campanhas
CREATE OR REPLACE VIEW v_campanhas_estatisticas AS
SELECT 
    cp.id AS campanha_id,
    cp.nombre AS nome_campanha,
    cp.activa,
    cp.pausada,
    
    -- Contadores de chamadas
    COUNT(cm.id) AS total_chamadas,
    COUNT(cm.id) FILTER (WHERE cm.status_atual IN ('marcando', 'tocando', 'atendida', 'em_andamento')) AS chamadas_ativas,
    COUNT(cm.id) FILTER (WHERE cm.status_atual = 'finalizada') AS chamadas_finalizadas,
    COUNT(cm.id) FILTER (WHERE cm.status_atual = 'erro') AS chamadas_erro,
    COUNT(cm.id) FILTER (WHERE cm.timestamp_atendida IS NOT NULL) AS chamadas_atendidas,
    
    -- Taxas
    CASE 
        WHEN COUNT(cm.id) > 0 
        THEN (COUNT(cm.id) FILTER (WHERE cm.timestamp_atendida IS NOT NULL)::REAL / COUNT(cm.id)) * 100
        ELSE 0 
    END AS taxa_atendimento,
    
    -- Tempos médios
    AVG(cm.duracao_total) FILTER (WHERE cm.duracao_total IS NOT NULL) AS tempo_medio_chamada,
    AVG(cm.tempo_espera) FILTER (WHERE cm.tempo_espera IS NOT NULL) AS tempo_medio_espera
    
FROM campanas_presione1 cp
LEFT JOIN chamada_monitoramento cm ON cp.id = cm.campanha_id
GROUP BY cp.id, cp.nombre, cp.activa, cp.pausada;

-- View de eventos recentes
CREATE OR REPLACE VIEW v_eventos_recentes AS
SELECT 
    e.*,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - e.timestamp_evento)) AS segundos_desde_evento
FROM evento_sistema e
WHERE e.timestamp_evento >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY e.timestamp_evento DESC;

-- ===============================================
-- FUNÇÕES AUXILIARES
-- ===============================================

-- Função para limpar cache expirado
CREATE OR REPLACE FUNCTION limpar_cache_expirado()
RETURNS INTEGER AS $$
DECLARE
    linhas_removidas INTEGER;
BEGIN
    DELETE FROM cache_metricas 
    WHERE timestamp_expiracao < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS linhas_removidas = ROW_COUNT;
    
    RETURN linhas_removidas;
END;
$$ LANGUAGE plpgsql;

-- Função para resetar estatísticas diárias dos agentes
CREATE OR REPLACE FUNCTION resetar_estatisticas_agentes_diarias()
RETURNS INTEGER AS $$
DECLARE
    agentes_atualizados INTEGER;
BEGIN
    UPDATE agente_monitoramento SET
        total_chamadas_atendidas = 0,
        tempo_total_atendimento = 0,
        tempo_total_pausa = 0
    WHERE activo = true;
    
    GET DIAGNOSTICS agentes_atualizados = ROW_COUNT;
    
    -- Registrar evento
    INSERT INTO evento_sistema (tipo_evento, titulo, nivel_severidade)
    VALUES ('agente_login', 'Estatísticas diárias dos agentes resetadas', 'info');
    
    RETURN agentes_atualizados;
END;
$$ LANGUAGE plpgsql;

-- Função para calcular métricas de dashboard
CREATE OR REPLACE FUNCTION calcular_metricas_dashboard()
RETURNS JSONB AS $$
DECLARE
    resultado JSONB;
BEGIN
    SELECT jsonb_build_object(
        'campanhas_ativas', (
            SELECT COUNT(*) FROM campanas_presione1 WHERE activa = true
        ),
        'chamadas_ativas', (
            SELECT COUNT(*) FROM chamada_monitoramento 
            WHERE status_atual IN ('marcando', 'tocando', 'atendida', 'em_andamento')
        ),
        'agentes_online', (
            SELECT COUNT(*) FROM agente_monitoramento 
            WHERE status_atual != 'offline' AND activo = true
        ),
        'eventos_criticos', (
            SELECT COUNT(*) FROM evento_sistema 
            WHERE nivel_severidade = 'critical' 
            AND resolvido = false 
            AND timestamp_evento >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
        ),
        'timestamp_calculo', EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)
    ) INTO resultado;
    
    RETURN resultado;
END;
$$ LANGUAGE plpgsql;

-- ===============================================
-- DADOS DE EXEMPLO PARA DESENVOLVIMENTO
-- ===============================================

-- Agentes de exemplo
INSERT INTO agente_monitoramento (nome_agente, codigo_agente, extensao_sip, email, status_atual) VALUES
('Ana Silva', 'ANA001', '1001', 'ana@empresa.com', 'livre'),
('Carlos Santos', 'CAR002', '1002', 'carlos@empresa.com', 'em_chamada'),
('Maria Oliveira', 'MAR003', '1003', 'maria@empresa.com', 'pausado'),
('João Pereira', 'JOA004', '1004', 'joao@empresa.com', 'livre'),
('Fernanda Costa', 'FER005', '1005', 'fernanda@empresa.com', 'offline');

-- Atualizar estatísticas dos agentes
UPDATE agente_monitoramento SET
    total_chamadas_atendidas = FLOOR(RANDOM() * 50) + 10,
    tempo_total_atendimento = FLOOR(RANDOM() * 7200) + 1800, -- 30min a 2h
    tempo_total_pausa = FLOOR(RANDOM() * 1800) + 300, -- 5min a 30min
    login_timestamp = CURRENT_TIMESTAMP - INTERVAL '4 hours'
WHERE status_atual != 'offline';

-- Eventos de exemplo
INSERT INTO evento_sistema (tipo_evento, titulo, descricao, nivel_severidade) VALUES
('campanha_iniciada', 'Campanha Vendas Q1 iniciada', 'Campanha iniciada com 5000 contatos', 'info'),
('provedor_falha', 'Falha no Provedor Twilio', 'Timeout na conexão SIP', 'error'),
('agente_login', 'Agente Ana Silva fez login', 'Login realizado via extensão 1001', 'info'),
('chamada_finalizada', 'Chamada transferida com sucesso', 'Cliente transferido para setor comercial', 'info');

-- ===============================================
-- TRIGGERS PARA AUDITORIA
-- ===============================================

-- Trigger para registrar mudanças de status do agente
CREATE OR REPLACE FUNCTION log_mudanca_status_agente()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status_atual != NEW.status_atual THEN
        INSERT INTO evento_sistema (
            tipo_evento, 
            titulo, 
            descricao, 
            agente_id,
            dados_evento,
            nivel_severidade
        ) VALUES (
            'agente_login',
            'Mudança de status do agente',
            'Status alterado de ' || OLD.status_atual || ' para ' || NEW.status_atual,
            NEW.id,
            jsonb_build_object(
                'status_anterior', OLD.status_atual,
                'status_novo', NEW.status_atual,
                'agente_codigo', NEW.codigo_agente
            ),
            'info'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_status_agente
    AFTER UPDATE ON agente_monitoramento
    FOR EACH ROW
    EXECUTE FUNCTION log_mudanca_status_agente();

-- ===============================================
-- PROCEDIMENTOS DE MANUTENÇÃO
-- ===============================================

-- Criar job para limpeza automática (executar diariamente)
-- Este seria configurado via cron ou task scheduler
/*
-- Exemplo de comando cron:
-- 0 2 * * * psql -d discador -c "SELECT limpar_cache_expirado();"
-- 0 0 * * * psql -d discador -c "SELECT resetar_estatisticas_agentes_diarias();"
*/

-- ===============================================
-- GRANTS E PERMISSÕES
-- ===============================================

-- Conceder permissões ao usuário da aplicação
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO discador_user;
-- GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA public TO discador_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO discador_user;

COMMIT; 