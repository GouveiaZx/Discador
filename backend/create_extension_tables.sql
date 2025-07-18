-- Script SQL para criar tabelas de extensões
-- Execute este script no seu banco de dados PostgreSQL

-- Tabela principal de extensões
CREATE TABLE IF NOT EXISTS extensions (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(10) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    campanha_id INTEGER REFERENCES campaigns(id) ON DELETE SET NULL,
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    configuracoes JSONB,
    horario_funcionamento JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_extensions_numero ON extensions(numero);
CREATE INDEX IF NOT EXISTS idx_extensions_ativo ON extensions(ativo);
CREATE INDEX IF NOT EXISTS idx_extensions_campanha_id ON extensions(campanha_id);
CREATE INDEX IF NOT EXISTS idx_extensions_created_at ON extensions(created_at);

-- Tabela de estatísticas das extensões
CREATE TABLE IF NOT EXISTS extension_stats (
    id SERIAL PRIMARY KEY,
    extension_id INTEGER NOT NULL REFERENCES extensions(id) ON DELETE CASCADE,
    total_calls INTEGER DEFAULT 0 NOT NULL,
    successful_calls INTEGER DEFAULT 0 NOT NULL,
    failed_calls INTEGER DEFAULT 0 NOT NULL,
    active_calls INTEGER DEFAULT 0 NOT NULL,
    total_talk_time INTEGER DEFAULT 0 NOT NULL,
    avg_talk_time INTEGER DEFAULT 0 NOT NULL,
    online BOOLEAN DEFAULT FALSE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para estatísticas
CREATE INDEX IF NOT EXISTS idx_extension_stats_extension_id ON extension_stats(extension_id);
CREATE INDEX IF NOT EXISTS idx_extension_stats_date ON extension_stats(date);
CREATE INDEX IF NOT EXISTS idx_extension_stats_online ON extension_stats(online);
CREATE INDEX IF NOT EXISTS idx_extension_stats_last_activity ON extension_stats(last_activity);

-- Tabela de logs de atividades das extensões
CREATE TABLE IF NOT EXISTS extension_logs (
    id SERIAL PRIMARY KEY,
    extension_id INTEGER NOT NULL REFERENCES extensions(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    details JSONB,
    call_id VARCHAR(100),
    caller_number VARCHAR(20),
    called_number VARCHAR(20),
    duration INTEGER,
    status VARCHAR(20),
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índices para logs
CREATE INDEX IF NOT EXISTS idx_extension_logs_extension_id ON extension_logs(extension_id);
CREATE INDEX IF NOT EXISTS idx_extension_logs_event_type ON extension_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_extension_logs_timestamp ON extension_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_extension_logs_call_id ON extension_logs(call_id);
CREATE INDEX IF NOT EXISTS idx_extension_logs_status ON extension_logs(status);

-- Tabela de configurações avançadas das extensões
CREATE TABLE IF NOT EXISTS extension_configs (
    id SERIAL PRIMARY KEY,
    extension_id INTEGER NOT NULL REFERENCES extensions(id) ON DELETE CASCADE,
    sip_username VARCHAR(50),
    sip_password VARCHAR(100),
    sip_domain VARCHAR(100),
    sip_proxy VARCHAR(100),
    sip_port INTEGER DEFAULT 5060,
    preferred_codec VARCHAR(20) DEFAULT 'ulaw',
    allowed_codecs VARCHAR(200) DEFAULT 'ulaw,alaw,gsm',
    nat_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    stun_server VARCHAR(100),
    qualify_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    qualify_frequency INTEGER DEFAULT 60,
    dtmf_mode VARCHAR(20) DEFAULT 'rfc2833',
    call_limit INTEGER DEFAULT 5,
    call_timeout INTEGER DEFAULT 30,
    context VARCHAR(50) DEFAULT 'default',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para configurações
CREATE INDEX IF NOT EXISTS idx_extension_configs_extension_id ON extension_configs(extension_id);
CREATE INDEX IF NOT EXISTS idx_extension_configs_sip_username ON extension_configs(sip_username);
CREATE INDEX IF NOT EXISTS idx_extension_configs_context ON extension_configs(context);

-- Constraint para garantir uma configuração por extensão
ALTER TABLE extension_configs ADD CONSTRAINT unique_extension_config UNIQUE (extension_id);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger nas tabelas
DROP TRIGGER IF EXISTS update_extensions_updated_at ON extensions;
CREATE TRIGGER update_extensions_updated_at
    BEFORE UPDATE ON extensions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_extension_stats_updated_at ON extension_stats;
CREATE TRIGGER update_extension_stats_updated_at
    BEFORE UPDATE ON extension_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_extension_configs_updated_at ON extension_configs;
CREATE TRIGGER update_extension_configs_updated_at
    BEFORE UPDATE ON extension_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Função para calcular tempo médio de conversa
CREATE OR REPLACE FUNCTION calculate_avg_talk_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.total_calls > 0 THEN
        NEW.avg_talk_time = NEW.total_talk_time / NEW.total_calls;
    ELSE
        NEW.avg_talk_time = 0;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para calcular tempo médio automaticamente
DROP TRIGGER IF EXISTS calculate_avg_talk_time_trigger ON extension_stats;
CREATE TRIGGER calculate_avg_talk_time_trigger
    BEFORE INSERT OR UPDATE ON extension_stats
    FOR EACH ROW
    EXECUTE FUNCTION calculate_avg_talk_time();

-- Função para limpar logs antigos (manter apenas últimos 30 dias)
CREATE OR REPLACE FUNCTION cleanup_old_extension_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM extension_logs 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ language 'plpgsql';

-- Função para obter estatísticas resumidas de extensões
CREATE OR REPLACE FUNCTION get_extensions_summary()
RETURNS TABLE (
    total_extensions INTEGER,
    active_extensions INTEGER,
    online_extensions INTEGER,
    total_calls INTEGER,
    successful_calls INTEGER,
    failed_calls INTEGER,
    avg_success_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(e.id)::INTEGER as total_extensions,
        COUNT(CASE WHEN e.ativo = true THEN 1 END)::INTEGER as active_extensions,
        COUNT(CASE WHEN es.online = true THEN 1 END)::INTEGER as online_extensions,
        COALESCE(SUM(es.total_calls), 0)::INTEGER as total_calls,
        COALESCE(SUM(es.successful_calls), 0)::INTEGER as successful_calls,
        COALESCE(SUM(es.failed_calls), 0)::INTEGER as failed_calls,
        CASE 
            WHEN COALESCE(SUM(es.total_calls), 0) > 0 THEN
                ROUND((COALESCE(SUM(es.successful_calls), 0)::NUMERIC / COALESCE(SUM(es.total_calls), 1)::NUMERIC) * 100, 2)
            ELSE 0
        END as avg_success_rate
    FROM extensions e
    LEFT JOIN extension_stats es ON e.id = es.extension_id;
END;
$$ language 'plpgsql';

-- Função para verificar disponibilidade de extensão baseada no horário
CREATE OR REPLACE FUNCTION is_extension_available(extension_id_param INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    ext_record RECORD;
    current_time TIME;
    current_day INTEGER; -- 0 = domingo, 1 = segunda, etc.
    horario JSONB;
    dia_config JSONB;
BEGIN
    -- Buscar extensão
    SELECT * INTO ext_record FROM extensions WHERE id = extension_id_param AND ativo = true;
    
    -- Se extensão não existe ou está inativa
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Se não há configuração de horário, considerar sempre disponível
    IF ext_record.horario_funcionamento IS NULL THEN
        RETURN TRUE;
    END IF;
    
    horario := ext_record.horario_funcionamento;
    current_time := CURRENT_TIME;
    current_day := EXTRACT(DOW FROM CURRENT_DATE); -- 0 = domingo
    
    -- Mapear dia da semana
    dia_config := CASE current_day
        WHEN 0 THEN horario->'domingo'
        WHEN 1 THEN horario->'segunda'
        WHEN 2 THEN horario->'terca'
        WHEN 3 THEN horario->'quarta'
        WHEN 4 THEN horario->'quinta'
        WHEN 5 THEN horario->'sexta'
        WHEN 6 THEN horario->'sabado'
    END;
    
    -- Se não há configuração para o dia atual
    IF dia_config IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Verificar se está ativo no dia
    IF (dia_config->>'ativo')::BOOLEAN = false THEN
        RETURN FALSE;
    END IF;
    
    -- Verificar horário
    IF current_time >= (dia_config->>'inicio')::TIME AND 
       current_time <= (dia_config->>'fim')::TIME THEN
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ language 'plpgsql';

-- Função para obter extensões disponíveis para discagem
CREATE OR REPLACE FUNCTION get_available_extensions_for_dialing(campanha_id_param INTEGER DEFAULT NULL)
RETURNS TABLE (
    id INTEGER,
    numero VARCHAR(10),
    nome VARCHAR(100),
    campanha_id INTEGER,
    active_calls INTEGER,
    call_limit INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.numero,
        e.nome,
        e.campanha_id,
        COALESCE(es.active_calls, 0) as active_calls,
        COALESCE(ec.call_limit, 5) as call_limit
    FROM extensions e
    LEFT JOIN extension_stats es ON e.id = es.extension_id
    LEFT JOIN extension_configs ec ON e.id = ec.extension_id
    WHERE e.ativo = true
    AND is_extension_available(e.id) = true
    AND (campanha_id_param IS NULL OR e.campanha_id = campanha_id_param OR e.campanha_id IS NULL)
    AND COALESCE(es.active_calls, 0) < COALESCE(ec.call_limit, 5)
    ORDER BY COALESCE(es.active_calls, 0) ASC, e.id ASC;
END;
$$ language 'plpgsql';

-- Inserir dados de exemplo (opcional)
INSERT INTO extensions (numero, nome, ativo, configuracoes, horario_funcionamento) VALUES
('1001', 'Extensão Principal', true, 
 '{"max_calls": 5, "timeout": 30, "codec": "ulaw"}',
 '{
   "segunda": {"ativo": true, "inicio": "08:00", "fim": "18:00"},
   "terca": {"ativo": true, "inicio": "08:00", "fim": "18:00"},
   "quarta": {"ativo": true, "inicio": "08:00", "fim": "18:00"},
   "quinta": {"ativo": true, "inicio": "08:00", "fim": "18:00"},
   "sexta": {"ativo": true, "inicio": "08:00", "fim": "18:00"},
   "sabado": {"ativo": false},
   "domingo": {"ativo": false}
 }'),
('1002', 'Extensão Secundária', true, 
 '{"max_calls": 3, "timeout": 25, "codec": "alaw"}',
 '{
   "segunda": {"ativo": true, "inicio": "09:00", "fim": "17:00"},
   "terca": {"ativo": true, "inicio": "09:00", "fim": "17:00"},
   "quarta": {"ativo": true, "inicio": "09:00", "fim": "17:00"},
   "quinta": {"ativo": true, "inicio": "09:00", "fim": "17:00"},
   "sexta": {"ativo": true, "inicio": "09:00", "fim": "17:00"},
   "sabado": {"ativo": true, "inicio": "09:00", "fim": "13:00"},
   "domingo": {"ativo": false}
 }')
ON CONFLICT (numero) DO NOTHING;

-- Inserir estatísticas iniciais
INSERT INTO extension_stats (extension_id, total_calls, successful_calls, failed_calls, online)
SELECT id, 0, 0, 0, false FROM extensions
ON CONFLICT DO NOTHING;

-- Inserir configurações padrão
INSERT INTO extension_configs (extension_id, sip_username, context)
SELECT id, numero, 'default' FROM extensions
ON CONFLICT (extension_id) DO NOTHING;

COMMIT;

-- Comentários sobre uso:
-- 1. Para verificar se uma extensão está disponível: SELECT is_extension_available(1);
-- 2. Para obter extensões disponíveis: SELECT * FROM get_available_extensions_for_dialing();
-- 3. Para obter resumo: SELECT * FROM get_extensions_summary();
-- 4. Para limpar logs antigos: SELECT cleanup_old_extension_logs();