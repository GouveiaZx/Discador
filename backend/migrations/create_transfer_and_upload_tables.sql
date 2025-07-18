-- Migração para criar tabelas de configuração de transferência e upload otimizado
-- Data: 2024-12-19
-- Descrição: Adiciona suporte para configurações flexíveis de transferência e upload otimizado de listas

-- Tabela para configurações de transferência
CREATE TABLE IF NOT EXISTS transfer_configurations (
    id SERIAL PRIMARY KEY,
    campanha_id INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,
    numeros_transferencia JSONB NOT NULL DEFAULT '[]'::jsonb,
    estrategia_selecao VARCHAR(20) NOT NULL DEFAULT 'round-robin',
    horario_funcionamento JSONB,
    ativo BOOLEAN NOT NULL DEFAULT true,
    prioridades JSONB,
    contador_uso INTEGER NOT NULL DEFAULT 0,
    ultimo_numero_usado VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_estrategia CHECK (estrategia_selecao IN ('round-robin', 'aleatoria', 'prioridade')),
    CONSTRAINT nome_unique_per_campaign UNIQUE (campanha_id, nome)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_transfer_config_campanha ON transfer_configurations(campanha_id);
CREATE INDEX IF NOT EXISTS idx_transfer_config_ativo ON transfer_configurations(ativo);
CREATE INDEX IF NOT EXISTS idx_transfer_config_created ON transfer_configurations(created_at);

-- Tabela para histórico de transferências
CREATE TABLE IF NOT EXISTS transfer_history (
    id SERIAL PRIMARY KEY,
    config_id INTEGER NOT NULL REFERENCES transfer_configurations(id) ON DELETE CASCADE,
    numero_usado VARCHAR(20) NOT NULL,
    sucesso BOOLEAN NOT NULL,
    detalhes TEXT,
    duracao_segundos INTEGER,
    timestamp_transferencia TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices para consultas rápidas
    INDEX idx_transfer_history_config (config_id),
    INDEX idx_transfer_history_timestamp (timestamp_transferencia),
    INDEX idx_transfer_history_sucesso (sucesso)
);

-- Tabela para tarefas de upload otimizado
CREATE TABLE IF NOT EXISTS upload_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    total_records INTEGER DEFAULT 0,
    processed_records INTEGER DEFAULT 0,
    valid_records INTEGER DEFAULT 0,
    invalid_records INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    detected_format JSONB,
    processing_stats JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_progress CHECK (progress_percentage >= 0 AND progress_percentage <= 100)
);

-- Índices para tarefas de upload
CREATE INDEX IF NOT EXISTS idx_upload_tasks_status ON upload_tasks(status);
CREATE INDEX IF NOT EXISTS idx_upload_tasks_created ON upload_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_upload_tasks_progress ON upload_tasks(progress_percentage);

-- Tabela para logs de processamento de upload
CREATE TABLE IF NOT EXISTS upload_processing_logs (
    id SERIAL PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES upload_tasks(id) ON DELETE CASCADE,
    log_level VARCHAR(10) NOT NULL DEFAULT 'INFO',
    message TEXT NOT NULL,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_log_level CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
);

-- Índices para logs
CREATE INDEX IF NOT EXISTS idx_upload_logs_task ON upload_processing_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_upload_logs_level ON upload_processing_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_upload_logs_timestamp ON upload_processing_logs(timestamp);

-- Tabela para estatísticas de performance de upload
CREATE TABLE IF NOT EXISTS upload_performance_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_uploads INTEGER DEFAULT 0,
    successful_uploads INTEGER DEFAULT 0,
    failed_uploads INTEGER DEFAULT 0,
    total_records_processed BIGINT DEFAULT 0,
    total_file_size_mb DECIMAL(10,2) DEFAULT 0,
    avg_processing_time_seconds DECIMAL(8,2) DEFAULT 0,
    peak_memory_usage_mb DECIMAL(8,2) DEFAULT 0,
    stats_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint para uma entrada por dia
    UNIQUE(date)
);

-- Índice para estatísticas por data
CREATE INDEX IF NOT EXISTS idx_upload_stats_date ON upload_performance_stats(date);

-- Função para atualizar timestamp de updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at automaticamente
CREATE TRIGGER update_transfer_config_updated_at 
    BEFORE UPDATE ON transfer_configurations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_upload_stats_updated_at 
    BEFORE UPDATE ON upload_performance_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Função para limpeza automática de dados antigos
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Limpar logs de upload mais antigos que 30 dias
    DELETE FROM upload_processing_logs 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '30 days';
    
    -- Limpar tarefas de upload completadas/falhadas mais antigas que 7 dias
    DELETE FROM upload_tasks 
    WHERE status IN ('completed', 'failed', 'cancelled') 
    AND created_at < CURRENT_TIMESTAMP - INTERVAL '7 days';
    
    -- Limpar histórico de transferências mais antigo que 90 dias
    DELETE FROM transfer_history 
    WHERE timestamp_transferencia < CURRENT_TIMESTAMP - INTERVAL '90 days';
    
    -- Limpar estatísticas de performance mais antigas que 1 ano
    DELETE FROM upload_performance_stats 
    WHERE date < CURRENT_DATE - INTERVAL '1 year';
    
    RAISE NOTICE 'Limpeza de dados antigos concluída';
END;
$$ LANGUAGE plpgsql;

-- Função para obter estatísticas de transferência
CREATE OR REPLACE FUNCTION get_transfer_stats(config_id_param INTEGER, days_param INTEGER DEFAULT 30)
RETURNS TABLE (
    config_id INTEGER,
    total_transferencias BIGINT,
    transferencias_sucesso BIGINT,
    transferencias_falha BIGINT,
    taxa_sucesso DECIMAL(5,2),
    numero_mais_usado VARCHAR(20),
    ultimo_uso TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        config_id_param,
        COUNT(*) as total_transferencias,
        COUNT(*) FILTER (WHERE sucesso = true) as transferencias_sucesso,
        COUNT(*) FILTER (WHERE sucesso = false) as transferencias_falha,
        CASE 
            WHEN COUNT(*) > 0 THEN 
                ROUND((COUNT(*) FILTER (WHERE sucesso = true)::DECIMAL / COUNT(*)) * 100, 2)
            ELSE 0
        END as taxa_sucesso,
        (
            SELECT numero_usado 
            FROM transfer_history th2 
            WHERE th2.config_id = config_id_param 
            AND th2.timestamp_transferencia >= CURRENT_TIMESTAMP - (days_param || ' days')::INTERVAL
            GROUP BY numero_usado 
            ORDER BY COUNT(*) DESC 
            LIMIT 1
        ) as numero_mais_usado,
        MAX(timestamp_transferencia) as ultimo_uso
    FROM transfer_history th
    WHERE th.config_id = config_id_param
    AND th.timestamp_transferencia >= CURRENT_TIMESTAMP - (days_param || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- Inserir dados de exemplo para teste (opcional)
INSERT INTO transfer_configurations (campanha_id, nome, numeros_transferencia, estrategia_selecao, ativo)
VALUES 
    (1, 'Configuração Padrão', '["1140001234", "1140005678", "1140009999"]'::jsonb, 'round-robin', true),
    (2, 'Suporte Técnico', '["1150001111", "1150002222"]'::jsonb, 'aleatoria', true)
ON CONFLICT (campanha_id, nome) DO NOTHING;

-- Comentários nas tabelas
COMMENT ON TABLE transfer_configurations IS 'Configurações flexíveis de transferência por campanha';
COMMENT ON TABLE transfer_history IS 'Histórico de transferências realizadas';
COMMENT ON TABLE upload_tasks IS 'Tarefas de upload de listas grandes com processamento assíncrono';
COMMENT ON TABLE upload_processing_logs IS 'Logs detalhados do processamento de uploads';
COMMENT ON TABLE upload_performance_stats IS 'Estatísticas de performance de uploads por dia';

-- Comentários nas colunas principais
COMMENT ON COLUMN transfer_configurations.numeros_transferencia IS 'Array JSON com números para transferência';
COMMENT ON COLUMN transfer_configurations.estrategia_selecao IS 'Estratégia: round-robin, aleatoria, prioridade';
COMMENT ON COLUMN transfer_configurations.horario_funcionamento IS 'JSON com horários e dias de funcionamento';
COMMENT ON COLUMN transfer_configurations.prioridades IS 'JSON com prioridades dos números (para estratégia prioridade)';
COMMENT ON COLUMN upload_tasks.detected_format IS 'Formato detectado automaticamente do arquivo';
COMMENT ON COLUMN upload_tasks.processing_stats IS 'Estatísticas detalhadas do processamento';

PRINT 'Migração concluída: Tabelas de transferência e upload otimizado criadas com sucesso!';