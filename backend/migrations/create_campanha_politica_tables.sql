-- ================================================
-- Migração: Sistema de Campanhas Políticas
-- Descrição: Cria tabelas para conformidade com legislação eleitoral
-- Versão: 1.0.0
-- Data: 2024
-- ================================================

-- ================================================
-- ENUMS ESPECÍFICOS ELEITORAIS
-- ================================================

DO $$ BEGIN
    CREATE TYPE tipo_eleicao AS ENUM (
        'municipal', 'estadual', 'federal', 'referendo', 'consulta_popular'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE status_campanha_politica AS ENUM (
        'pendente_aprovacao', 'ativa_periodo_legal', 'pausada_fora_horario',
        'bloqueada_fora_periodo', 'suspensa_autoridade', 'finalizada'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE tipo_log_eleitoral AS ENUM (
        'ligacao_iniciada', 'ligacao_atendida', 'ligacao_finalizada',
        'mensagem_reproduzida', 'opt_out_solicitado', 'violacao_horario',
        'bloqueio_automatico'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ================================================
-- TABELA: Configuração Eleitoral
-- ================================================
CREATE TABLE IF NOT EXISTS configuracao_eleitoral (
    id SERIAL PRIMARY KEY,
    pais_codigo VARCHAR(5) NOT NULL UNIQUE,
    pais_nome VARCHAR(100) NOT NULL,
    
    -- Horários legais de campanha
    horario_inicio_permitido VARCHAR(5) NOT NULL DEFAULT '08:00',
    horario_fim_permitido VARCHAR(5) NOT NULL DEFAULT '22:00',
    
    -- Dias da semana permitidos (JSON array)
    dias_semana_permitidos JSONB NOT NULL DEFAULT '[0,1,2,3,4,5,6]',
    
    -- Mensagens obrigatórias
    mensagem_inicial_obrigatoria TEXT NOT NULL,
    mensagem_opt_out_obrigatoria TEXT NOT NULL,
    
    -- Configurações de logs
    retencao_logs_dias INTEGER NOT NULL DEFAULT 2555,
    hash_algorithm VARCHAR(20) NOT NULL DEFAULT 'SHA256',
    
    -- Configurações de criptografia
    usar_criptografia_exportacao BOOLEAN DEFAULT true,
    algoritmo_criptografia VARCHAR(20) DEFAULT 'AES256',
    
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para configuração eleitoral
CREATE INDEX IF NOT EXISTS idx_configuracao_eleitoral_pais ON configuracao_eleitoral(pais_codigo);
CREATE INDEX IF NOT EXISTS idx_configuracao_eleitoral_activo ON configuracao_eleitoral(activo);

-- ================================================
-- TABELA: Calendário Eleitoral
-- ================================================
CREATE TABLE IF NOT EXISTS calendario_eleitoral (
    id SERIAL PRIMARY KEY,
    pais_codigo VARCHAR(5) NOT NULL,
    estado_codigo VARCHAR(10),
    
    tipo_eleicao tipo_eleicao NOT NULL,
    nome_eleicao VARCHAR(200) NOT NULL,
    
    -- Período eleitoral legal
    data_inicio_campanha TIMESTAMP NOT NULL,
    data_fim_campanha TIMESTAMP NOT NULL,
    data_eleicao TIMESTAMP NOT NULL,
    
    -- Período de silêncio eleitoral
    data_inicio_silencio TIMESTAMP,
    data_fim_silencio TIMESTAMP,
    
    -- Metadados oficiais
    orgao_responsavel VARCHAR(200) NOT NULL,
    numero_resolucao VARCHAR(100),
    url_oficial VARCHAR(500),
    
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_periodo_campanha_valido CHECK (data_fim_campanha > data_inicio_campanha)
);

-- Índices para calendário eleitoral
CREATE INDEX IF NOT EXISTS idx_calendario_periodo ON calendario_eleitoral(data_inicio_campanha, data_fim_campanha);
CREATE INDEX IF NOT EXISTS idx_calendario_eleicao ON calendario_eleitoral(data_eleicao);
CREATE INDEX IF NOT EXISTS idx_calendario_pais_tipo ON calendario_eleitoral(pais_codigo, tipo_eleicao);

-- ================================================
-- TABELA: Campanhas Políticas
-- ================================================
CREATE TABLE IF NOT EXISTS campanha_politica (
    id SERIAL PRIMARY KEY,
    
    -- Referência à campanha base (extends campanha existente)
    campanha_base_id INTEGER NOT NULL UNIQUE,
    -- FOREIGN KEY será adicionada quando a tabela campanas existir
    
    -- Identificação política
    candidato_nome VARCHAR(200) NOT NULL,
    candidato_numero VARCHAR(10),
    partido_sigla VARCHAR(10) NOT NULL,
    partido_nome VARCHAR(200) NOT NULL,
    cargo_candidatura VARCHAR(100) NOT NULL,
    
    -- Configurações eleitorais
    configuracao_eleitoral_id INTEGER NOT NULL REFERENCES configuracao_eleitoral(id),
    calendario_eleitoral_id INTEGER NOT NULL REFERENCES calendario_eleitoral(id),
    
    -- Status e controles
    status_politica status_campanha_politica NOT NULL DEFAULT 'pendente_aprovacao',
    aprovada_por_autoridade BOOLEAN DEFAULT false,
    data_aprovacao TIMESTAMP,
    autoridade_responsavel VARCHAR(200),
    
    -- Controle de opt-out
    permitir_opt_out BOOLEAN DEFAULT true NOT NULL,
    contador_opt_outs INTEGER DEFAULT 0,
    
    -- Limites e quotas
    limite_diario_ligacoes INTEGER,
    limite_total_ligacoes INTEGER,
    contador_ligacoes_realizadas INTEGER DEFAULT 0,
    
    -- Auditoria e compliance
    hash_configuracao VARCHAR(64) NOT NULL,
    uuid_campanha UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para campanhas políticas
CREATE INDEX IF NOT EXISTS idx_campanha_politica_candidato ON campanha_politica(candidato_nome);
CREATE INDEX IF NOT EXISTS idx_campanha_politica_partido ON campanha_politica(partido_sigla);
CREATE INDEX IF NOT EXISTS idx_campanha_politica_status ON campanha_politica(status_politica);
CREATE INDEX IF NOT EXISTS idx_campanha_politica_uuid ON campanha_politica(uuid_campanha);
CREATE INDEX IF NOT EXISTS idx_campanha_politica_hash ON campanha_politica(hash_configuracao);

-- ================================================
-- TABELA: Logs Eleitorais Imutáveis
-- ================================================
CREATE TABLE IF NOT EXISTS log_eleitoral_imutavel (
    id SERIAL PRIMARY KEY,
    
    -- Identificação única e imutável
    uuid_log UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    hash_anterior VARCHAR(64),
    hash_proprio VARCHAR(64) NOT NULL UNIQUE,
    
    -- Referências
    campanha_politica_id INTEGER NOT NULL REFERENCES campanha_politica(id),
    campanha_base_id INTEGER NOT NULL,
    
    -- Dados da ligação
    numero_destino VARCHAR(20) NOT NULL,
    numero_cli_usado VARCHAR(20) NOT NULL,
    
    -- Dados temporais (críticos para auditoria)
    timestamp_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    timestamp_local TIMESTAMP NOT NULL,
    timezone_local VARCHAR(50) NOT NULL,
    
    -- Evento específico
    tipo_log tipo_log_eleitoral NOT NULL,
    descricao_evento TEXT NOT NULL,
    
    -- Dados técnicos da chamada
    canal_asterisk VARCHAR(100),
    duracao_segundos INTEGER,
    resultado_ligacao VARCHAR(50),
    
    -- Conformidade eleitoral
    dentro_horario_legal BOOLEAN NOT NULL,
    mensagem_obrigatoria_reproduzida BOOLEAN DEFAULT false,
    opt_out_oferecido BOOLEAN DEFAULT false,
    
    -- Metadados técnicos
    endereco_ip_servidor VARCHAR(45) NOT NULL,
    versao_sistema VARCHAR(20) NOT NULL,
    checksum_arquivo_audio VARCHAR(64),
    
    -- Dados de auditoria
    operador_responsavel VARCHAR(100),
    validado_automaticamente BOOLEAN DEFAULT true,
    
    -- IMUTABILIDADE: apenas inserção, sem updates/deletes
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índices para logs eleitorais
CREATE INDEX IF NOT EXISTS idx_log_eleitoral_timestamp ON log_eleitoral_imutavel(timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_log_eleitoral_campanha ON log_eleitoral_imutavel(campanha_politica_id);
CREATE INDEX IF NOT EXISTS idx_log_eleitoral_numero ON log_eleitoral_imutavel(numero_destino);
CREATE INDEX IF NOT EXISTS idx_log_eleitoral_tipo ON log_eleitoral_imutavel(tipo_log);
CREATE INDEX IF NOT EXISTS idx_log_eleitoral_uuid ON log_eleitoral_imutavel(uuid_log);
CREATE INDEX IF NOT EXISTS idx_log_eleitoral_hash ON log_eleitoral_imutavel(hash_proprio);
CREATE INDEX IF NOT EXISTS idx_log_eleitoral_horario_legal ON log_eleitoral_imutavel(dentro_horario_legal);

-- ================================================
-- TABELA: Opt-Out Eleitoral
-- ================================================
CREATE TABLE IF NOT EXISTS opt_out_eleitoral (
    id SERIAL PRIMARY KEY,
    
    -- Identificação
    numero_telefone VARCHAR(20) NOT NULL,
    numero_normalizado VARCHAR(20) NOT NULL,
    
    -- Contexto da solicitação
    campanha_politica_id INTEGER NOT NULL REFERENCES campanha_politica(id),
    log_solicitacao_id INTEGER NOT NULL REFERENCES log_eleitoral_imutavel(id),
    
    -- Metadados da solicitação
    data_solicitacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metodo_solicitacao VARCHAR(50) NOT NULL,
    confirmado_verbalmente BOOLEAN DEFAULT false,
    
    -- Validade do opt-out
    data_expiracao TIMESTAMP,
    opt_out_permanente BOOLEAN DEFAULT true,
    
    -- Auditoria
    hash_solicitacao VARCHAR(64) NOT NULL,
    uuid_opt_out UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para opt-out eleitoral
CREATE INDEX IF NOT EXISTS idx_opt_out_numero ON opt_out_eleitoral(numero_normalizado);
CREATE INDEX IF NOT EXISTS idx_opt_out_campanha ON opt_out_eleitoral(campanha_politica_id);
CREATE INDEX IF NOT EXISTS idx_opt_out_data ON opt_out_eleitoral(data_solicitacao);
CREATE INDEX IF NOT EXISTS idx_opt_out_uuid ON opt_out_eleitoral(uuid_opt_out);
CREATE INDEX IF NOT EXISTS idx_opt_out_activo ON opt_out_eleitoral(activo);

-- ================================================
-- TABELA: Exportações Eleitorais
-- ================================================
CREATE TABLE IF NOT EXISTS exportacao_eleitoral (
    id SERIAL PRIMARY KEY,
    
    -- Identificação da exportação
    uuid_exportacao UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    nome_arquivo VARCHAR(200) NOT NULL,
    
    -- Dados exportados
    campanha_politica_ids JSONB NOT NULL,
    data_inicio_periodo TIMESTAMP NOT NULL,
    data_fim_periodo TIMESTAMP NOT NULL,
    total_registros INTEGER NOT NULL,
    
    -- Solicitante
    autoridade_solicitante VARCHAR(200) NOT NULL,
    email_solicitante VARCHAR(200) NOT NULL,
    documento_oficial VARCHAR(100),
    
    -- Metadados técnicos
    hash_arquivo VARCHAR(64) NOT NULL,
    tamanho_arquivo_bytes INTEGER NOT NULL,
    formato_exportacao VARCHAR(20) NOT NULL,
    criptografado BOOLEAN DEFAULT true,
    algoritmo_criptografia VARCHAR(20),
    
    -- Entrega
    data_exportacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_entrega TIMESTAMP,
    metodo_entrega VARCHAR(50),
    confirmacao_recebimento BOOLEAN DEFAULT false,
    
    -- Auditoria
    operador_responsavel VARCHAR(100) NOT NULL,
    aprovada_por_supervisor BOOLEAN DEFAULT false,
    supervisor_responsavel VARCHAR(100),
    
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para exportações
CREATE INDEX IF NOT EXISTS idx_exportacao_uuid ON exportacao_eleitoral(uuid_exportacao);
CREATE INDEX IF NOT EXISTS idx_exportacao_data ON exportacao_eleitoral(data_exportacao);
CREATE INDEX IF NOT EXISTS idx_exportacao_autoridade ON exportacao_eleitoral(autoridade_solicitante);
CREATE INDEX IF NOT EXISTS idx_exportacao_periodo ON exportacao_eleitoral(data_inicio_periodo, data_fim_periodo);

-- ================================================
-- TRIGGERS PARA IMUTABILIDADE E AUDITORIA
-- ================================================

-- Função para atualizar timestamps
CREATE OR REPLACE FUNCTION update_campanha_politica_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualização de timestamps
DROP TRIGGER IF EXISTS trigger_configuracao_eleitoral_updated_at ON configuracao_eleitoral;
CREATE TRIGGER trigger_configuracao_eleitoral_updated_at
    BEFORE UPDATE ON configuracao_eleitoral
    FOR EACH ROW EXECUTE FUNCTION update_campanha_politica_timestamp();

DROP TRIGGER IF EXISTS trigger_calendario_eleitoral_updated_at ON calendario_eleitoral;
CREATE TRIGGER trigger_calendario_eleitoral_updated_at
    BEFORE UPDATE ON calendario_eleitoral
    FOR EACH ROW EXECUTE FUNCTION update_campanha_politica_timestamp();

DROP TRIGGER IF EXISTS trigger_campanha_politica_updated_at ON campanha_politica;
CREATE TRIGGER trigger_campanha_politica_updated_at
    BEFORE UPDATE ON campanha_politica
    FOR EACH ROW EXECUTE FUNCTION update_campanha_politica_timestamp();

-- Função para prevenir updates/deletes em logs imutáveis
CREATE OR REPLACE FUNCTION prevent_log_eleitoral_changes()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Logs eleitorais são imutáveis. Operação não permitida.';
END;
$$ LANGUAGE plpgsql;

-- Triggers para prevenir alterações em logs
DROP TRIGGER IF EXISTS trigger_prevent_log_update ON log_eleitoral_imutavel;
CREATE TRIGGER trigger_prevent_log_update
    BEFORE UPDATE ON log_eleitoral_imutavel
    FOR EACH ROW EXECUTE FUNCTION prevent_log_eleitoral_changes();

DROP TRIGGER IF EXISTS trigger_prevent_log_delete ON log_eleitoral_imutavel;
CREATE TRIGGER trigger_prevent_log_delete
    BEFORE DELETE ON log_eleitoral_imutavel
    FOR EACH ROW EXECUTE FUNCTION prevent_log_eleitoral_changes();

-- ================================================
-- DADOS INICIAIS
-- ================================================

-- Configuração eleitoral padrão para Brasil
INSERT INTO configuracao_eleitoral (
    pais_codigo, pais_nome, 
    horario_inicio_permitido, horario_fim_permitido,
    dias_semana_permitidos,
    mensagem_inicial_obrigatoria,
    mensagem_opt_out_obrigatoria,
    retencao_logs_dias
) VALUES (
    'BR', 'Brasil',
    '08:00', '22:00',
    '[0,1,2,3,4,5,6]'::jsonb,
    'Esta é uma chamada de conteúdo eleitoral, conforme previsto na legislação brasileira.',
    'Para não receber mais chamadas desta campanha, pressione 9 ou diga SAIR.',
    2555
) ON CONFLICT (pais_codigo) DO NOTHING;

-- Configuração eleitoral padrão para Espanha
INSERT INTO configuracao_eleitoral (
    pais_codigo, pais_nome,
    horario_inicio_permitido, horario_fim_permitido, 
    dias_semana_permitidos,
    mensagem_inicial_obrigatoria,
    mensagem_opt_out_obrigatoria
) VALUES (
    'ES', 'España',
    '09:00', '21:00',
    '[0,1,2,3,4]'::jsonb,
    'Esta es una llamada de contenido electoral, conforme a la legislación española.',
    'Para no recibir más llamadas de esta campaña, pulse 9 o diga SALIR.'
) ON CONFLICT (pais_codigo) DO NOTHING;

-- ================================================
-- VERIFICAÇÃO FINAL
-- ================================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND (
        table_name LIKE '%eleitoral%' OR 
        table_name LIKE 'campanha_politica%' OR
        table_name LIKE 'opt_out_%' OR
        table_name LIKE 'exportacao_%'
    );
    
    RAISE NOTICE 'Sistema de Campanhas Políticas: % tabelas criadas com sucesso', table_count;
END
$$; 