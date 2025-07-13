-- Migração para Sistema de Performance Avançado
-- Adiciona tabelas e campos para suporte a 20-30 CPS e limites por país

-- =========== TABELA DE HISTÓRICO DE MÉTRICAS ===========
CREATE TABLE IF NOT EXISTS performance_metrics_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    current_cps REAL NOT NULL DEFAULT 0.0,
    target_cps REAL NOT NULL DEFAULT 0.0,
    concurrent_calls INTEGER NOT NULL DEFAULT 0,
    calls_initiated INTEGER NOT NULL DEFAULT 0,
    calls_answered INTEGER NOT NULL DEFAULT 0,
    calls_failed INTEGER NOT NULL DEFAULT 0,
    success_rate REAL NOT NULL DEFAULT 0.0,
    average_setup_time REAL NOT NULL DEFAULT 0.0,
    system_load REAL NOT NULL DEFAULT 0.0,
    queue_size INTEGER NOT NULL DEFAULT 0,
    emergency_brake_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_performance_timestamp ON performance_metrics_history(timestamp);
CREATE INDEX idx_performance_cps ON performance_metrics_history(current_cps);

-- =========== TABELA DE LIMITES DE CLI POR PAÍS ===========
CREATE TABLE IF NOT EXISTS cli_country_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country VARCHAR(10) NOT NULL,
    daily_limit INTEGER NOT NULL DEFAULT 0,
    reset_time TIME DEFAULT '00:00:00',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dados iniciais de limites por país
INSERT OR REPLACE INTO cli_country_limits (country, daily_limit) VALUES
('usa', 100),
('canada', 100),
('mexico', 0),
('brasil', 0),
('colombia', 0),
('argentina', 0),
('chile', 0),
('peru', 0),
('venezuela', 0),
('default', 0);

-- =========== TABELA DE USO DIÁRIO DE CLI ===========
CREATE TABLE IF NOT EXISTS cli_daily_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cli_numero VARCHAR(20) NOT NULL,
    country VARCHAR(10) NOT NULL,
    usage_date DATE NOT NULL,
    usage_count INTEGER NOT NULL DEFAULT 0,
    first_use_time DATETIME,
    last_use_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE UNIQUE INDEX idx_cli_usage_unique ON cli_daily_usage(cli_numero, usage_date);
CREATE INDEX idx_cli_usage_country ON cli_daily_usage(country);
CREATE INDEX idx_cli_usage_date ON cli_daily_usage(usage_date);

-- =========== TABELA DE CONFIGURAÇÕES DTMF POR PAÍS ===========
CREATE TABLE IF NOT EXISTS dtmf_country_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country VARCHAR(10) NOT NULL UNIQUE,
    connect_key VARCHAR(1) NOT NULL DEFAULT '1',
    disconnect_key VARCHAR(1) NOT NULL DEFAULT '9',
    repeat_key VARCHAR(1) NOT NULL DEFAULT '0',
    menu_timeout INTEGER NOT NULL DEFAULT 10,
    instructions TEXT NOT NULL,
    instructions_audio VARCHAR(255),
    context_suffix VARCHAR(20),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dados iniciais de configurações DTMF
INSERT OR REPLACE INTO dtmf_country_config (country, connect_key, disconnect_key, repeat_key, menu_timeout, instructions, instructions_audio, context_suffix) VALUES
-- América do Norte
('usa', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_en.wav', '_usa'),
('canada', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_en.wav', '_canada'),
('republica_dominicana', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_do.wav', '_republica_dominicana'),
('porto_rico', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_pr.wav', '_porto_rico'),

-- América Latina
('mexico', '3', '9', '0', 15, 'Presione 3 para conectar, 9 para salir de la lista', 'presione_3_conectar_mx.wav', '_mexico'),
('brasil', '1', '9', '0', 10, 'Pressione 1 para conectar, 9 para sair da lista', 'pressione_1_conectar_br.wav', '_brasil'),
('argentina', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_ar.wav', '_argentina'),
('colombia', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_co.wav', '_colombia'),
('chile', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_cl.wav', '_chile'),
('peru', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_pe.wav', '_peru'),
('venezuela', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_ve.wav', '_venezuela'),
('ecuador', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_ec.wav', '_ecuador'),
('bolivia', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_bo.wav', '_bolivia'),
('uruguay', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_uy.wav', '_uruguay'),
('paraguay', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_py.wav', '_paraguay'),
('costa_rica', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_cr.wav', '_costa_rica'),
('panama', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_pa.wav', '_panama'),
('guatemala', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_gt.wav', '_guatemala'),
('honduras', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_hn.wav', '_honduras'),
('el_salvador', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_sv.wav', '_el_salvador'),
('nicaragua', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_ni.wav', '_nicaragua'),

-- Europa
('espanha', '1', '9', '0', 10, 'Presione 1 para conectar, 9 para salir de la lista', 'presione_1_conectar_es.wav', '_espanha'),
('portugal', '1', '9', '0', 10, 'Pressione 1 para conectar, 9 para sair da lista', 'pressione_1_conectar_pt.wav', '_portugal'),
('franca', '1', '9', '0', 10, 'Appuyez sur 1 pour vous connecter, 9 pour être supprimé de la liste', 'appuyez_1_connecter_fr.wav', '_franca'),
('alemanha', '1', '9', '0', 10, 'Drücken Sie 1 um zu verbinden, 9 um aus der Liste entfernt zu werden', 'drucken_1_verbinden_de.wav', '_alemanha'),
('italia', '1', '9', '0', 10, 'Premi 1 per connettere, 9 per essere rimosso dall\'elenco', 'premi_1_connettere_it.wav', '_italia'),
('reino_unido', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_uk.wav', '_reino_unido'),
('holanda', '1', '9', '0', 10, 'Druk op 1 om te verbinden, 9 om uit de lijst te worden verwijderd', 'druk_1_verbinden_nl.wav', '_holanda'),
('belgica', '1', '9', '0', 10, 'Appuyez sur 1 pour vous connecter, 9 pour être supprimé de la liste', 'appuyez_1_connecter_be.wav', '_belgica'),
('suica', '1', '9', '0', 10, 'Drücken Sie 1 um zu verbinden, 9 um aus der Liste entfernt zu werden', 'drucken_1_verbinden_ch.wav', '_suica'),
('austria', '1', '9', '0', 10, 'Drücken Sie 1 um zu verbinden, 9 um aus der Liste entfernt zu werden', 'drucken_1_verbinden_at.wav', '_austria'),

-- Ásia
('india', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_in.wav', '_india'),
('filipinas', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_ph.wav', '_filipinas'),
('malasia', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_my.wav', '_malasia'),
('singapura', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_sg.wav', '_singapura'),
('tailandia', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_th.wav', '_tailandia'),
('indonesia', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_id.wav', '_indonesia'),

-- Oceania
('australia', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_au.wav', '_australia'),
('nova_zelandia', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_nz.wav', '_nova_zelandia'),

-- África
('africa_do_sul', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_za.wav', '_africa_do_sul'),

-- Oriente Médio
('israel', '1', '9', '0', 10, 'Press 1 to connect, 9 to be removed from list', 'press_1_connect_il.wav', '_israel');

-- =========== TABELA DE TESTES DE CARGA ===========
CREATE TABLE IF NOT EXISTS load_test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id VARCHAR(50) NOT NULL UNIQUE,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    
    -- Configuração do teste
    target_cps REAL NOT NULL,
    duration_minutes INTEGER NOT NULL,
    countries_tested TEXT NOT NULL, -- JSON array
    number_of_clis INTEGER NOT NULL,
    
    -- Resultados gerais
    total_calls_attempted INTEGER NOT NULL DEFAULT 0,
    total_calls_successful INTEGER NOT NULL DEFAULT 0,
    total_calls_failed INTEGER NOT NULL DEFAULT 0,
    success_rate REAL NOT NULL DEFAULT 0.0,
    
    -- Métricas de performance
    actual_cps REAL NOT NULL DEFAULT 0.0,
    max_cps_achieved REAL NOT NULL DEFAULT 0.0,
    average_setup_time REAL NOT NULL DEFAULT 0.0,
    max_concurrent_calls INTEGER NOT NULL DEFAULT 0,
    
    -- Estatísticas por país (JSON)
    country_stats TEXT,
    
    -- Estatísticas de CLI (JSON)
    cli_usage_stats TEXT,
    
    -- Métricas de sistema
    system_load_avg REAL NOT NULL DEFAULT 0.0,
    memory_usage_avg REAL NOT NULL DEFAULT 0.0,
    
    -- Status do teste
    test_completed BOOLEAN NOT NULL DEFAULT FALSE,
    test_interrupted BOOLEAN NOT NULL DEFAULT FALSE,
    interruption_reason TEXT,
    
    -- Detalhes de erro (JSON)
    error_details TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_load_test_start_time ON load_test_results(start_time);
CREATE INDEX idx_load_test_target_cps ON load_test_results(target_cps);
CREATE INDEX idx_load_test_completed ON load_test_results(test_completed);

-- =========== TABELA DE CONFIGURAÇÕES DE PERFORMANCE ===========
CREATE TABLE IF NOT EXISTS performance_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_name VARCHAR(50) NOT NULL UNIQUE,
    max_cps REAL NOT NULL DEFAULT 30.0,
    initial_cps REAL NOT NULL DEFAULT 5.0,
    ramp_up_step REAL NOT NULL DEFAULT 2.0,
    ramp_up_interval INTEGER NOT NULL DEFAULT 10,
    max_concurrent_calls INTEGER NOT NULL DEFAULT 500,
    thread_pool_size INTEGER NOT NULL DEFAULT 50,
    monitoring_interval INTEGER NOT NULL DEFAULT 1,
    auto_adjust_cps BOOLEAN NOT NULL DEFAULT TRUE,
    emergency_brake_threshold REAL NOT NULL DEFAULT 0.1,
    quality_threshold REAL NOT NULL DEFAULT 0.8,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Configuração padrão
INSERT OR REPLACE INTO performance_config (config_name, max_cps, initial_cps, ramp_up_step, ramp_up_interval, max_concurrent_calls, thread_pool_size, auto_adjust_cps, emergency_brake_threshold, quality_threshold) VALUES
('default', 30.0, 5.0, 2.0, 10, 500, 50, TRUE, 0.1, 0.8),
('high_performance', 50.0, 10.0, 5.0, 5, 1000, 100, TRUE, 0.05, 0.9),
('conservative', 15.0, 2.0, 1.0, 20, 200, 25, TRUE, 0.2, 0.7);

-- =========== ALTERAÇÕES NA TABELA CLI EXISTENTE ===========
-- Adicionar campos para controle de uso avançado
ALTER TABLE cli ADD COLUMN last_country_used VARCHAR(10) DEFAULT 'unknown';
ALTER TABLE cli ADD COLUMN daily_usage_count INTEGER DEFAULT 0;
ALTER TABLE cli ADD COLUMN last_daily_reset DATE DEFAULT CURRENT_DATE;
ALTER TABLE cli ADD COLUMN performance_score REAL DEFAULT 100.0;
ALTER TABLE cli ADD COLUMN blocked_until DATETIME NULL;
ALTER TABLE cli ADD COLUMN block_reason TEXT NULL;

-- Índices para performance
CREATE INDEX idx_cli_daily_usage ON cli(daily_usage_count);
CREATE INDEX idx_cli_last_reset ON cli(last_daily_reset);
CREATE INDEX idx_cli_performance ON cli(performance_score);

-- =========== ALTERAÇÕES NA TABELA LLAMADAS EXISTENTE ===========
-- Adicionar campos para métricas de performance
ALTER TABLE llamadas ADD COLUMN setup_time_ms INTEGER DEFAULT 0;
ALTER TABLE llamadas ADD COLUMN dtmf_key_pressed VARCHAR(5) DEFAULT NULL;
ALTER TABLE llamadas ADD COLUMN country_detected VARCHAR(10) DEFAULT 'unknown';
ALTER TABLE llamadas ADD COLUMN cli_limit_exceeded BOOLEAN DEFAULT FALSE;
ALTER TABLE llamadas ADD COLUMN performance_test_id VARCHAR(50) DEFAULT NULL;

-- Índices para performance
CREATE INDEX idx_llamadas_setup_time ON llamadas(setup_time_ms);
CREATE INDEX idx_llamadas_country ON llamadas(country_detected);
CREATE INDEX idx_llamadas_test_id ON llamadas(performance_test_id);

-- =========== TABELA DE EVENTOS DE SISTEMA ===========
CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(50) NOT NULL,
    event_subtype VARCHAR(50),
    severity VARCHAR(20) NOT NULL DEFAULT 'info', -- debug, info, warning, error, critical
    message TEXT NOT NULL,
    details TEXT, -- JSON com detalhes extras
    component VARCHAR(50), -- dialer, load_test, cli_manager, etc.
    user_id INTEGER,
    ip_address VARCHAR(45),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_system_events_type ON system_events(event_type);
CREATE INDEX idx_system_events_severity ON system_events(severity);
CREATE INDEX idx_system_events_timestamp ON system_events(timestamp);
CREATE INDEX idx_system_events_component ON system_events(component);

-- =========== TRIGGERS PARA AUDITORIA ===========

-- Trigger para auditar mudanças em cli_country_limits
CREATE TRIGGER tr_cli_limits_audit
AFTER UPDATE ON cli_country_limits
FOR EACH ROW
BEGIN
    INSERT INTO system_events (event_type, severity, message, details, component)
    VALUES (
        'cli_limit_changed',
        'info',
        'Limite de CLI alterado para país: ' || NEW.country,
        json_object(
            'country', NEW.country,
            'old_limit', OLD.daily_limit,
            'new_limit', NEW.daily_limit,
            'timestamp', datetime('now')
        ),
        'cli_manager'
    );
END;

-- Trigger para auditar mudanças em dtmf_country_config
CREATE TRIGGER tr_dtmf_config_audit
AFTER UPDATE ON dtmf_country_config
FOR EACH ROW
BEGIN
    INSERT INTO system_events (event_type, severity, message, details, component)
    VALUES (
        'dtmf_config_changed',
        'info',
        'Configuração DTMF alterada para país: ' || NEW.country,
        json_object(
            'country', NEW.country,
            'old_connect_key', OLD.connect_key,
            'new_connect_key', NEW.connect_key,
            'timestamp', datetime('now')
        ),
        'dtmf_manager'
    );
END;

-- Trigger para resetar uso diário de CLI
CREATE TRIGGER tr_cli_daily_reset
AFTER UPDATE ON cli
FOR EACH ROW
WHEN NEW.last_daily_reset != OLD.last_daily_reset
BEGIN
    INSERT INTO system_events (event_type, severity, message, details, component)
    VALUES (
        'cli_daily_reset',
        'info',
        'Reset diário executado para CLI: ' || NEW.numero_normalizado,
        json_object(
            'cli', NEW.numero_normalizado,
            'old_usage', OLD.daily_usage_count,
            'new_usage', NEW.daily_usage_count,
            'reset_date', NEW.last_daily_reset,
            'timestamp', datetime('now')
        ),
        'cli_manager'
    );
END;

-- =========== VIEWS PARA RELATÓRIOS ===========

-- View para estatísticas de performance por país
CREATE VIEW v_performance_by_country AS
SELECT 
    country_detected,
    COUNT(*) as total_calls,
    AVG(setup_time_ms) as avg_setup_time,
    AVG(CASE WHEN resultado = 'ANSWERED' THEN 1 ELSE 0 END) as success_rate,
    COUNT(DISTINCT cli_utilizado) as unique_clis_used,
    DATE(fecha_inicio) as call_date
FROM llamadas 
WHERE country_detected IS NOT NULL
GROUP BY country_detected, DATE(fecha_inicio)
ORDER BY call_date DESC, total_calls DESC;

-- View para estatísticas de CLI por dia
CREATE VIEW v_cli_daily_stats AS
SELECT 
    cli_numero,
    country,
    usage_date,
    usage_count,
    (SELECT daily_limit FROM cli_country_limits WHERE country = cli_daily_usage.country) as daily_limit,
    ROUND(CAST(usage_count AS FLOAT) / NULLIF((SELECT daily_limit FROM cli_country_limits WHERE country = cli_daily_usage.country), 0) * 100, 2) as usage_percentage
FROM cli_daily_usage
ORDER BY usage_date DESC, usage_count DESC;

-- View para métricas de performance em tempo real
CREATE VIEW v_current_performance AS
SELECT 
    *,
    ROUND(CAST(calls_answered AS FLOAT) / NULLIF(calls_initiated, 0) * 100, 2) as success_rate_percentage,
    ROUND(current_cps / NULLIF(target_cps, 0) * 100, 2) as cps_efficiency_percentage
FROM performance_metrics_history
WHERE timestamp > datetime('now', '-1 hour')
ORDER BY timestamp DESC;

-- =========== FUNÇÕES UTILITÁRIAS ===========

-- Função para limpar dados antigos (via trigger ou cron job)
CREATE TRIGGER tr_cleanup_old_metrics
AFTER INSERT ON performance_metrics_history
FOR EACH ROW
WHEN (SELECT COUNT(*) FROM performance_metrics_history) > 10000
BEGIN
    DELETE FROM performance_metrics_history 
    WHERE timestamp < datetime('now', '-7 days');
END;

-- =========== DADOS INICIAIS PARA TESTE ===========

-- Inserir algumas métricas iniciais para teste
INSERT INTO performance_metrics_history (current_cps, target_cps, concurrent_calls, success_rate, system_load) VALUES
(0.0, 5.0, 0, 0.0, 0.0);

-- Inserir evento de inicialização
INSERT INTO system_events (event_type, severity, message, component) VALUES
('system_migration', 'info', 'Migração de performance enhancement aplicada com sucesso', 'migration');

-- Commit das alterações
COMMIT; 