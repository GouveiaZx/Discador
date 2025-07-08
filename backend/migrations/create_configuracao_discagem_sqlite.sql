-- ================================================
-- Migração: Configurações Avançadas de Discagem (SQLite)
-- Descrição: Adiciona configurações específicas para CPS, timing e controles avançados
-- Versão: 1.0.0 (SQLite Compatible)
-- Data: 2024
-- ================================================

-- ================================================
-- TABELA: Configurações de Discagem Avançada
-- ================================================
CREATE TABLE IF NOT EXISTS configuracao_discagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identificação
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    
    -- Configurações básicas (CPS - Calls Per Second)
    cps DECIMAL(5,2) DEFAULT 1.0 NOT NULL,
    sleep_time DECIMAL(5,2) DEFAULT 1.0 NOT NULL,
    wait_time DECIMAL(5,2) DEFAULT 30.0 NOT NULL,
    
    -- Configurações de detecção
    amd_enabled BOOLEAN DEFAULT 1,
    amd_timeout DECIMAL(5,2) DEFAULT 3.0,
    
    -- Configurações de horário
    timezone VARCHAR(50) DEFAULT 'America/Sao_Paulo',
    horario_inicio VARCHAR(5) DEFAULT '08:00',
    horario_fim VARCHAR(5) DEFAULT '18:00',
    
    -- Configurações de retry
    max_tentativas INTEGER DEFAULT 3,
    intervalo_retry INTEGER DEFAULT 60,
    
    -- Configurações de compliance
    respeitar_dnc BOOLEAN DEFAULT 1,
    respeitar_horarios BOOLEAN DEFAULT 1,
    
    -- Status
    ativo BOOLEAN DEFAULT 1,
    eh_padrao BOOLEAN DEFAULT 0,
    
    -- Auditoria
    usuario_criador_id INTEGER,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: Trunks SIP Avançados
-- ================================================
CREATE TABLE IF NOT EXISTS trunk (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identificação
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    
    -- Configurações básicas SIP
    host VARCHAR(255) NOT NULL,
    porta INTEGER DEFAULT 5060,
    usuario VARCHAR(100),
    senha VARCHAR(255),
    
    -- Configurações avançadas
    codigo_dv VARCHAR(20) DEFAULT '10-digit', -- 10-digit, 11-digit, E164
    caller_ids TEXT, -- JSON array de caller IDs
    balanceamento VARCHAR(20) DEFAULT 'round_robin', -- round_robin, least_used, priority
    failover_enabled BOOLEAN DEFAULT 1,
    
    -- Configurações de protocolo
    protocolo VARCHAR(10) DEFAULT 'UDP', -- UDP, TCP, TLS
    codec_preferido VARCHAR(20) DEFAULT 'ulaw',
    
    -- Configurações de capacidade
    capacidade_maxima INTEGER DEFAULT 10,
    chamadas_ativas INTEGER DEFAULT 0,
    prioridade INTEGER DEFAULT 1,
    
    -- Configurações de qualidade
    timeout_conexao INTEGER DEFAULT 30,
    timeout_resposta INTEGER DEFAULT 60,
    
    -- Monitoramento
    status VARCHAR(20) DEFAULT 'unknown', -- online, offline, unknown, error
    ultima_verificacao TIMESTAMP,
    latencia_ms INTEGER,
    
    -- Status
    ativo BOOLEAN DEFAULT 1,
    
    -- Auditoria
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: Histórico de Status dos Trunks
-- ================================================
CREATE TABLE IF NOT EXISTS trunk_status_historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trunk_id INTEGER NOT NULL,
    
    -- Status anterior e novo
    status_anterior VARCHAR(20),
    status_novo VARCHAR(20) NOT NULL,
    
    -- Métricas no momento da mudança
    chamadas_ativas INTEGER DEFAULT 0,
    latencia_ms INTEGER,
    
    -- Detalhes da mudança
    motivo TEXT,
    detalhes_erro TEXT,
    
    data_mudanca TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (trunk_id) REFERENCES trunk(id)
);

-- ================================================
-- TABELA: Estatísticas de Trunks
-- ================================================
CREATE TABLE IF NOT EXISTS trunk_estatisticas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trunk_id INTEGER NOT NULL,
    
    -- Período das estatísticas
    data_inicio TIMESTAMP NOT NULL,
    data_fim TIMESTAMP NOT NULL,
    
    -- Métricas de chamadas
    total_chamadas INTEGER DEFAULT 0,
    chamadas_completadas INTEGER DEFAULT 0,
    chamadas_falhadas INTEGER DEFAULT 0,
    
    -- Métricas de qualidade
    latencia_media DECIMAL(8,2),
    latencia_maxima INTEGER,
    uptime_porcentagem DECIMAL(5,2),
    
    -- Métricas de uso
    tempo_total_uso INTEGER, -- segundos
    pico_chamadas_simultaneas INTEGER,
    
    data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (trunk_id) REFERENCES trunk(id)
);

-- ================================================
-- ÍNDICES
-- ================================================

-- Configuração de discagem
CREATE INDEX IF NOT EXISTS idx_configuracao_nome ON configuracao_discagem(nome);
CREATE INDEX IF NOT EXISTS idx_configuracao_ativo ON configuracao_discagem(ativo);
CREATE INDEX IF NOT EXISTS idx_configuracao_padrao ON configuracao_discagem(eh_padrao);

-- Trunks
CREATE INDEX IF NOT EXISTS idx_trunk_nome ON trunk(nome);
CREATE INDEX IF NOT EXISTS idx_trunk_ativo ON trunk(ativo);
CREATE INDEX IF NOT EXISTS idx_trunk_status ON trunk(status);
CREATE INDEX IF NOT EXISTS idx_trunk_prioridade ON trunk(prioridade);

-- Histórico de status
CREATE INDEX IF NOT EXISTS idx_trunk_historico_trunk ON trunk_status_historico(trunk_id);
CREATE INDEX IF NOT EXISTS idx_trunk_historico_data ON trunk_status_historico(data_mudanca);

-- Estatísticas
CREATE INDEX IF NOT EXISTS idx_trunk_stats_trunk ON trunk_estatisticas(trunk_id);
CREATE INDEX IF NOT EXISTS idx_trunk_stats_periodo ON trunk_estatisticas(data_inicio, data_fim);

-- ================================================
-- TRIGGERS PARA SQLITE
-- ================================================

-- Trigger para atualizar data_atualizacao na configuracao_discagem
CREATE TRIGGER IF NOT EXISTS update_configuracao_timestamp 
    AFTER UPDATE ON configuracao_discagem
BEGIN
    UPDATE configuracao_discagem 
    SET data_atualizacao = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Trigger para atualizar data_atualizacao no trunk
CREATE TRIGGER IF NOT EXISTS update_trunk_timestamp 
    AFTER UPDATE ON trunk
BEGIN
    UPDATE trunk 
    SET data_atualizacao = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Trigger para registrar mudanças de status do trunk
CREATE TRIGGER IF NOT EXISTS trunk_status_change 
    AFTER UPDATE OF status ON trunk
    WHEN OLD.status != NEW.status
BEGIN
    INSERT INTO trunk_status_historico (
        trunk_id, status_anterior, status_novo, 
        chamadas_ativas, latencia_ms, motivo
    ) VALUES (
        NEW.id, OLD.status, NEW.status,
        NEW.chamadas_ativas, NEW.latencia_ms,
        'Status change detected'
    );
END; 