-- ================================================
-- Migração: Configurações Avançadas de Discagem
-- Descrição: Adiciona configurações específicas para CPS, timing e controles avançados
-- Versão: 1.0.0
-- Data: 2024
-- ================================================

-- ================================================
-- TABELA: Configurações de Discagem Avançada
-- ================================================
CREATE TABLE IF NOT EXISTS configuracao_discagem (
    id SERIAL PRIMARY KEY,
    
    -- Identificação
    nome VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    
    -- Configurações de velocidade (CPS - Calls Per Second)
    cps_maximo DECIMAL(5,2) DEFAULT 1.0 NOT NULL,
    cps_inicial DECIMAL(5,2) DEFAULT 0.5 NOT NULL,
    auto_ajuste_cps BOOLEAN DEFAULT true,
    
    -- Configurações de timing (em segundos)
    sleep_time_entre_llamadas DECIMAL(5,2) DEFAULT 1.0 NOT NULL,
    wait_time_respuesta DECIMAL(5,2) DEFAULT 30.0 NOT NULL,
    timeout_marcacion DECIMAL(5,2) DEFAULT 60.0 NOT NULL,
    
    -- Configurações de retry
    max_intentos_por_numero INTEGER DEFAULT 3 NOT NULL,
    intervalo_retry_minutos INTEGER DEFAULT 60 NOT NULL,
    
    -- Configurações de detecção
    detectar_contestador BOOLEAN DEFAULT true,
    detectar_fax BOOLEAN DEFAULT true,
    detectar_tono_ocupado BOOLEAN DEFAULT true,
    
    -- Configurações de horário
    horario_inicio VARCHAR(5) DEFAULT '08:00',
    horario_fin VARCHAR(5) DEFAULT '20:00',
    dias_semana_activos JSONB DEFAULT '[1,2,3,4,5]', -- Lunes a Viernes
    
    -- Configurações de trunk/carrier
    balanceamento_trunks BOOLEAN DEFAULT true,
    rotacao_cli BOOLEAN DEFAULT true,
    
    -- Configurações de qualidade
    amd_habilitado BOOLEAN DEFAULT true, -- Answering Machine Detection
    amd_timeout DECIMAL(5,2) DEFAULT 3.0,
    amd_silence_threshold INTEGER DEFAULT 1000,
    
    -- Configurações de compliance
    respetar_dnc BOOLEAN DEFAULT true,
    respetar_horarios_locales BOOLEAN DEFAULT true,
    permitir_manual_override BOOLEAN DEFAULT false,
    
    -- Configurações de performance
    max_canales_simultaneos INTEGER DEFAULT 10,
    buffer_numeros INTEGER DEFAULT 50,
    predictive_ratio DECIMAL(3,2) DEFAULT 1.2,
    
    -- Status e controles
    activa BOOLEAN DEFAULT true,
    es_default BOOLEAN DEFAULT false,
    
    -- Auditoria
    usuario_creador_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para configuração de discagem
CREATE INDEX IF NOT EXISTS idx_configuracao_discagem_nome ON configuracao_discagem(nome);
CREATE INDEX IF NOT EXISTS idx_configuracao_discagem_activa ON configuracao_discagem(activa);
CREATE INDEX IF NOT EXISTS idx_configuracao_discagem_default ON configuracao_discagem(es_default);

-- ================================================
-- TABELA: Histórico de Configurações
-- ================================================
CREATE TABLE IF NOT EXISTS historico_configuracao_discagem (
    id SERIAL PRIMARY KEY,
    configuracao_id INTEGER NOT NULL REFERENCES configuracao_discagem(id),
    
    -- Snapshot da configuração
    configuracao_snapshot JSONB NOT NULL,
    
    -- Metadatos do change
    usuario_modificador_id INTEGER,
    motivo_cambio TEXT,
    
    -- Métricas de performance no período
    llamadas_realizadas INTEGER DEFAULT 0,
    tasa_contacto DECIMAL(5,2),
    tasa_abandono DECIMAL(5,2),
    duracion_promedio DECIMAL(8,2),
    
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP,
    
    CONSTRAINT check_periodo_historico CHECK (fecha_fin IS NULL OR fecha_fin > fecha_inicio)
);

-- Índices para histórico
CREATE INDEX IF NOT EXISTS idx_historico_configuracao_id ON historico_configuracao_discagem(configuracao_id);
CREATE INDEX IF NOT EXISTS idx_historico_periodo ON historico_configuracao_discagem(fecha_inicio, fecha_fin);

-- ================================================
-- TABELA: Associação Campanha-Configuração
-- ================================================
CREATE TABLE IF NOT EXISTS campanha_configuracao_discagem (
    id SERIAL PRIMARY KEY,
    
    -- Referências
    campanha_id INTEGER NOT NULL, -- Referência para tabela campanhas quando existir
    configuracao_discagem_id INTEGER NOT NULL REFERENCES configuracao_discagem(id),
    
    -- Período de aplicação
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP,
    
    -- Override específicos para esta campanha
    override_cps DECIMAL(5,2),
    override_horario_inicio VARCHAR(5),
    override_horario_fin VARCHAR(5),
    override_max_canales INTEGER,
    
    -- Status
    activa BOOLEAN DEFAULT true,
    
    CONSTRAINT check_periodo_campanha_config CHECK (fecha_fin IS NULL OR fecha_fin > fecha_inicio),
    CONSTRAINT unique_campanha_activa UNIQUE(campanha_id, activa) DEFERRABLE INITIALLY DEFERRED
);

-- Índices para associação
CREATE INDEX IF NOT EXISTS idx_campanha_config_campanha ON campanha_configuracao_discagem(campanha_id);
CREATE INDEX IF NOT EXISTS idx_campanha_config_configuracao ON campanha_configuracao_discagem(configuracao_discagem_id);
CREATE INDEX IF NOT EXISTS idx_campanha_config_activa ON campanha_configuracao_discagem(activa);

-- ================================================
-- FUNÇÃO: Trigger para histórico automático
-- ================================================
CREATE OR REPLACE FUNCTION save_configuracao_discagem_history()
RETURNS TRIGGER AS $$
BEGIN
    -- Finalizar histórico anterior
    UPDATE historico_configuracao_discagem 
    SET fecha_fin = CURRENT_TIMESTAMP
    WHERE configuracao_id = NEW.id AND fecha_fin IS NULL;
    
    -- Criar novo registro histórico
    INSERT INTO historico_configuracao_discagem (
        configuracao_id,
        configuracao_snapshot,
        usuario_modificador_id,
        fecha_inicio
    ) VALUES (
        NEW.id,
        row_to_json(NEW),
        NEW.usuario_creador_id,
        CURRENT_TIMESTAMP
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- TRIGGERS
-- ================================================
CREATE TRIGGER trigger_configuracao_discagem_history
    AFTER INSERT OR UPDATE ON configuracao_discagem
    FOR EACH ROW EXECUTE FUNCTION save_configuracao_discagem_history();

-- Trigger para atualizar timestamp
CREATE OR REPLACE FUNCTION update_configuracao_discagem_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_configuracao_discagem_updated_at
    BEFORE UPDATE ON configuracao_discagem
    FOR EACH ROW EXECUTE FUNCTION update_configuracao_discagem_timestamp();

-- ================================================
-- DADOS INICIAIS
-- ================================================

-- Configuração padrão conservadora
INSERT INTO configuracao_discagem (
    nome, descripcion, es_default,
    cps_maximo, cps_inicial, 
    sleep_time_entre_llamadas, wait_time_respuesta,
    max_intentos_por_numero, 
    max_canales_simultaneos, predictive_ratio
) VALUES (
    'Configuración Conservadora',
    'Configuración segura para campañas pequeñas y medianas',
    true,
    1.0, 0.5,
    2.0, 30.0,
    3,
    5, 1.1
) ON CONFLICT (nome) DO NOTHING;

-- Configuração agressiva para high-volume
INSERT INTO configuracao_discagem (
    nome, descripcion,
    cps_maximo, cps_inicial,
    sleep_time_entre_llamadas, wait_time_respuesta,
    max_intentos_por_numero,
    max_canales_simultaneos, predictive_ratio,
    auto_ajuste_cps
) VALUES (
    'Configuración Agresiva',
    'Para campañas de alto volumen con infraestructura robusta',
    5.0, 2.0,
    0.5, 25.0,
    2,
    20, 1.5,
    true
) ON CONFLICT (nome) DO NOTHING;

-- Configuração para compliance rigoroso
INSERT INTO configuracao_discagem (
    nome, descripcion,
    cps_maximo, cps_inicial,
    sleep_time_entre_llamadas, wait_time_respuesta,
    max_intentos_por_numero,
    horario_inicio, horario_fin,
    respetar_dnc, respetar_horarios_locales,
    max_canales_simultaneos, predictive_ratio
) VALUES (
    'Configuración Compliance',
    'Máximo cumplimiento normativo y respeto al usuario',
    0.5, 0.3,
    3.0, 45.0,
    2,
    '09:00', '18:00',
    true, true,
    3, 1.0
) ON CONFLICT (nome) DO NOTHING;

-- ================================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- ================================================

COMMENT ON TABLE configuracao_discagem IS 'Configurações avançadas para controle de discagem preditiva';
COMMENT ON COLUMN configuracao_discagem.cps_maximo IS 'Máximo de llamadas por segundo permitidas';
COMMENT ON COLUMN configuracao_discagem.sleep_time_entre_llamadas IS 'Tiempo de espera entre llamadas en segundos';
COMMENT ON COLUMN configuracao_discagem.wait_time_respuesta IS 'Tiempo máximo de espera por respuesta';
COMMENT ON COLUMN configuracao_discagem.predictive_ratio IS 'Ratio predictivo: cuántas llamadas iniciar por agente disponible';
COMMENT ON COLUMN configuracao_discagem.amd_habilitado IS 'Habilitar detección automática de contestador';
COMMENT ON COLUMN configuracao_discagem.dias_semana_activos IS 'Array JSON con días activos (0=Domingo, 6=Sábado)'; 