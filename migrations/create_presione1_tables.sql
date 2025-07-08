-- Migração para criar tabelas do discado preditivo "Presione 1"
-- Esta migração cria as estruturas necessárias para campanhas automatizadas
-- onde o sistema toca um áudio e aguarda o usuário pressionar a tecla 1

-- ========================================
-- 1. CRIAR TABLA CAMPANHAS PRESIONE 1
-- ========================================

BEGIN;

-- Criar extensão para geração de IDs únicos se não existir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS campanas_presione1 (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    
    -- Configuração da campanha
    lista_llamadas_id INTEGER NOT NULL REFERENCES listas_llamadas(id) ON DELETE CASCADE,
    mensaje_audio_url VARCHAR(500) NOT NULL,
    timeout_presione1 INTEGER NOT NULL DEFAULT 10 CHECK (timeout_presione1 BETWEEN 3 AND 60),
    
    -- Configuração de voicemail
    detectar_voicemail BOOLEAN NOT NULL DEFAULT TRUE,
    mensaje_voicemail_url VARCHAR(500),
    duracion_minima_voicemail INTEGER NOT NULL DEFAULT 3 CHECK (duracion_minima_voicemail BETWEEN 1 AND 10),
    duracion_maxima_voicemail INTEGER NOT NULL DEFAULT 30 CHECK (duracion_maxima_voicemail BETWEEN 10 AND 180),
    
    -- Configuração de transferência
    extension_transferencia VARCHAR(20),
    cola_transferencia VARCHAR(50),
    
    -- Estados da campanha
    activa BOOLEAN NOT NULL DEFAULT FALSE,
    pausada BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Configuração de discado
    llamadas_simultaneas INTEGER NOT NULL DEFAULT 1 CHECK (llamadas_simultaneas BETWEEN 1 AND 10),
    tiempo_entre_llamadas INTEGER NOT NULL DEFAULT 5 CHECK (tiempo_entre_llamadas BETWEEN 1 AND 60),
    
    -- Notas adicionais
    notas TEXT,
    
    -- Constraints
    CONSTRAINT campana_transferencia_check CHECK (
        extension_transferencia IS NOT NULL OR cola_transferencia IS NOT NULL
    ),
    CONSTRAINT campana_voicemail_url_check CHECK (
        detectar_voicemail = FALSE OR mensaje_voicemail_url IS NOT NULL
    ),
    CONSTRAINT campana_duracao_voicemail_check CHECK (
        duracion_maxima_voicemail > duracion_minima_voicemail
    )
);

-- ========================================
-- 2. CRIAR TABLA LLAMADAS PRESIONE 1
-- ========================================

CREATE TABLE IF NOT EXISTS llamadas_presione1 (
    id SERIAL PRIMARY KEY,
    campana_id INTEGER NOT NULL REFERENCES campanas_presione1(id) ON DELETE CASCADE,
    numero_destino VARCHAR(20) NOT NULL,
    numero_normalizado VARCHAR(20) NOT NULL,
    cli_utilizado VARCHAR(20),
    
    -- Estados do fluxo (incluindo voicemail)
    estado VARCHAR(30) NOT NULL DEFAULT 'pendiente' CHECK (estado IN (
        'pendiente', 'marcando', 'contestada', 'audio_reproducido', 'esperando_dtmf',
        'presiono_1', 'no_presiono', 'transferida', 'finalizada', 'error',
        'voicemail_detectado', 'voicemail_audio_reproducido', 'voicemail_finalizado'
    )),
    
    -- Timestamps da chamada
    fecha_inicio TIMESTAMP WITH TIME ZONE,
    fecha_contestada TIMESTAMP WITH TIME ZONE,
    fecha_audio_inicio TIMESTAMP WITH TIME ZONE,
    fecha_dtmf_recibido TIMESTAMP WITH TIME ZONE,
    fecha_transferencia TIMESTAMP WITH TIME ZONE,
    fecha_fin TIMESTAMP WITH TIME ZONE,
    
    -- Dados específicos de voicemail
    voicemail_detectado BOOLEAN,
    fecha_voicemail_detectado TIMESTAMP WITH TIME ZONE,
    fecha_voicemail_audio_inicio TIMESTAMP WITH TIME ZONE,
    fecha_voicemail_audio_fin TIMESTAMP WITH TIME ZONE,
    duracion_mensaje_voicemail INTEGER CHECK (duracion_mensaje_voicemail >= 0),
    
    -- Resultados da chamada
    presiono_1 BOOLEAN,
    dtmf_recibido VARCHAR(10),
    tiempo_respuesta_dtmf REAL CHECK (tiempo_respuesta_dtmf >= 0),
    transferencia_exitosa BOOLEAN,
    
    -- Dados técnicos
    unique_id_asterisk VARCHAR(50),
    channel VARCHAR(100),
    duracion_total INTEGER CHECK (duracion_total >= 0),
    duracion_audio INTEGER CHECK (duracion_audio >= 0),
    motivo_finalizacion VARCHAR(100)
);

-- ========================================
-- 3. CRIAR ÍNDICES
-- ========================================

-- Índices para campanas_presione1
CREATE INDEX IF NOT EXISTS idx_campanas_presione1_nombre ON campanas_presione1(nombre);
CREATE INDEX IF NOT EXISTS idx_campanas_presione1_activa ON campanas_presione1(activa);
CREATE INDEX IF NOT EXISTS idx_campanas_presione1_lista ON campanas_presione1(lista_llamadas_id);
CREATE INDEX IF NOT EXISTS idx_campanas_presione1_voicemail ON campanas_presione1(detectar_voicemail);

-- Índices para llamadas_presione1
CREATE INDEX IF NOT EXISTS idx_llamadas_presione1_campana ON llamadas_presione1(campana_id);
CREATE INDEX IF NOT EXISTS idx_llamadas_presione1_numero ON llamadas_presione1(numero_destino);
CREATE INDEX IF NOT EXISTS idx_llamadas_presione1_numero_norm ON llamadas_presione1(numero_normalizado);
CREATE INDEX IF NOT EXISTS idx_llamadas_presione1_estado ON llamadas_presione1(estado);
CREATE INDEX IF NOT EXISTS idx_llamadas_presione1_fecha ON llamadas_presione1(fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_llamadas_presione1_presiono1 ON llamadas_presione1(presiono_1);
CREATE INDEX IF NOT EXISTS idx_llamadas_presione1_voicemail ON llamadas_presione1(voicemail_detectado);
CREATE INDEX IF NOT EXISTS idx_llamadas_presione1_motivo ON llamadas_presione1(motivo_finalizacion);

-- ========================================
-- 4. TRIGGERS PARA ATUALIZAÇÃO AUTOMÁTICA
-- ========================================

-- Função para atualizar fecha_actualizacion automaticamente
CREATE OR REPLACE FUNCTION actualizar_fecha_campana_presione1()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para campanas_presione1
DROP TRIGGER IF EXISTS trigger_actualizar_fecha_campana_presione1 ON campanas_presione1;
CREATE TRIGGER trigger_actualizar_fecha_campana_presione1
    BEFORE UPDATE ON campanas_presione1
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_campana_presione1();

-- ========================================
-- 5. COMENTÁRIOS DAS TABELAS
-- ========================================

-- Comentários para campanas_presione1
COMMENT ON TABLE campanas_presione1 IS 'Campanhas de discado preditivo com modo Presione 1 com detecção de voicemail';
COMMENT ON COLUMN campanas_presione1.nombre IS 'Nome da campanha';
COMMENT ON COLUMN campanas_presione1.descripcion IS 'Descrição da campanha';
COMMENT ON COLUMN campanas_presione1.lista_llamadas_id IS 'ID da lista de números a discar';
COMMENT ON COLUMN campanas_presione1.mensaje_audio_url IS 'URL do arquivo de áudio a reproduzir';
COMMENT ON COLUMN campanas_presione1.timeout_presione1 IS 'Segundos para aguardar DTMF (3-60)';
COMMENT ON COLUMN campanas_presione1.extension_transferencia IS 'Extensão para transferir chamadas que pressionaram 1';
COMMENT ON COLUMN campanas_presione1.cola_transferencia IS 'Fila de agentes para transferir';
COMMENT ON COLUMN campanas_presione1.activa IS 'Se a campanha está ativa (executando)';
COMMENT ON COLUMN campanas_presione1.pausada IS 'Se a campanha está pausada';
COMMENT ON COLUMN campanas_presione1.llamadas_simultaneas IS 'Número máximo de chamadas simultâneas (1-10)';
COMMENT ON COLUMN campanas_presione1.tiempo_entre_llamadas IS 'Segundos entre início de chamadas (1-60)';
COMMENT ON COLUMN campanas_presione1.detectar_voicemail IS 'Se deve detectar e processar correio de voz automaticamente';
COMMENT ON COLUMN campanas_presione1.mensaje_voicemail_url IS 'URL do arquivo de áudio para reproduzir no voicemail';
COMMENT ON COLUMN campanas_presione1.duracion_minima_voicemail IS 'Duração mínima em segundos para considerar como voicemail válido';
COMMENT ON COLUMN campanas_presione1.duracion_maxima_voicemail IS 'Duração máxima em segundos de gravação no voicemail';

-- Comentários para llamadas_presione1
COMMENT ON TABLE llamadas_presione1 IS 'Registros de chamadas individuais do modo Presione 1 com dados de voicemail';
COMMENT ON COLUMN llamadas_presione1.campana_id IS 'ID da campanha';
COMMENT ON COLUMN llamadas_presione1.numero_destino IS 'Número discado (formato original)';
COMMENT ON COLUMN llamadas_presione1.numero_normalizado IS 'Número normalizado (+549XXXXXXXXXX)';
COMMENT ON COLUMN llamadas_presione1.cli_utilizado IS 'CLI usado na chamada';
COMMENT ON COLUMN llamadas_presione1.estado IS 'Estado atual da chamada';
COMMENT ON COLUMN llamadas_presione1.fecha_inicio IS 'Início da tentativa de chamada';
COMMENT ON COLUMN llamadas_presione1.fecha_contestada IS 'Momento em que foi atendida';
COMMENT ON COLUMN llamadas_presione1.fecha_audio_inicio IS 'Início da reprodução do áudio';
COMMENT ON COLUMN llamadas_presione1.fecha_dtmf_recibido IS 'Momento em que recebeu DTMF';
COMMENT ON COLUMN llamadas_presione1.fecha_transferencia IS 'Início da transferência';
COMMENT ON COLUMN llamadas_presione1.fecha_fin IS 'Fim da chamada';
COMMENT ON COLUMN llamadas_presione1.presiono_1 IS 'Se pressionou a tecla 1';
COMMENT ON COLUMN llamadas_presione1.dtmf_recibido IS 'Tecla DTMF recebida';
COMMENT ON COLUMN llamadas_presione1.tiempo_respuesta_dtmf IS 'Segundos até pressionar tecla';
COMMENT ON COLUMN llamadas_presione1.transferencia_exitosa IS 'Se a transferência foi bem-sucedida';
COMMENT ON COLUMN llamadas_presione1.unique_id_asterisk IS 'UniqueID da chamada no Asterisk';
COMMENT ON COLUMN llamadas_presione1.channel IS 'Channel da chamada no Asterisk';
COMMENT ON COLUMN llamadas_presione1.duracion_total IS 'Duração total em segundos';
COMMENT ON COLUMN llamadas_presione1.duracion_audio IS 'Duração do áudio em segundos';
COMMENT ON COLUMN llamadas_presione1.motivo_finalizacion IS 'Motivo pelo qual a chamada finalizou';
COMMENT ON COLUMN llamadas_presione1.voicemail_detectado IS 'Indica se a chamada foi identificada como correio de voz';
COMMENT ON COLUMN llamadas_presione1.duracion_mensaje_voicemail IS 'Duração em segundos da mensagem deixada no voicemail';
COMMENT ON COLUMN llamadas_presione1.fecha_voicemail_detectado IS 'Timestamp de quando o voicemail foi detectado';
COMMENT ON COLUMN llamadas_presione1.fecha_voicemail_audio_inicio IS 'Timestamp de início da reprodução no voicemail';
COMMENT ON COLUMN llamadas_presione1.fecha_voicemail_audio_fin IS 'Timestamp de fim da reprodução no voicemail';

-- ========================================
-- 6. DADOS DE EXEMPLO (OPCIONAL)
-- ========================================

-- Inserir uma campanha de exemplo
-- Nota: Assumindo que existe lista_llamadas com ID 1
INSERT INTO campanas_presione1 (
    nombre, 
    descripcion, 
    lista_llamadas_id, 
    mensaje_audio_url, 
    timeout_presione1,
    detectar_voicemail,
    mensaje_voicemail_url,
    duracion_minima_voicemail,
    duracion_maxima_voicemail,
    extension_transferencia,
    llamadas_simultaneas,
    tiempo_entre_llamadas,
    notas
)
VALUES (
    'Campanha Exemplo Presione 1',
    'Campanha de demonstração do modo Presione 1',
    1,
    '/sounds/presione1_demo.wav',
    10,
    TRUE,
    '/sounds/demo_voicemail.wav',
    3,
    30,
    '100',
    2,
    5,
    'Campanha criada automaticamente para demonstração'
)
ON CONFLICT DO NOTHING;

-- ========================================
-- 7. VIEWS ÚTEIS
-- ========================================

-- View para estatísticas rápidas por campanha
CREATE OR REPLACE VIEW vista_estadisticas_presione1 AS
SELECT 
    c.id AS campana_id,
    c.nombre AS campana_nombre,
    c.activa,
    c.pausada,
    COUNT(l.id) AS total_llamadas,
    COUNT(CASE WHEN l.fecha_contestada IS NOT NULL THEN 1 END) AS llamadas_contestadas,
    COUNT(CASE WHEN l.presiono_1 = TRUE THEN 1 END) AS llamadas_presiono_1,
    COUNT(CASE WHEN l.presiono_1 = FALSE THEN 1 END) AS llamadas_no_presiono,
    COUNT(CASE WHEN l.transferencia_exitosa = TRUE THEN 1 END) AS llamadas_transferidas,
    COUNT(CASE WHEN l.estado = 'error' THEN 1 END) AS llamadas_error,
    
    -- Estatísticas de voicemail
    COUNT(CASE WHEN l.voicemail_detectado = TRUE THEN 1 END) AS llamadas_voicemail,
    COUNT(CASE WHEN l.motivo_finalizacion = 'voicemail_mensaje_dejado' THEN 1 END) AS llamadas_voicemail_mensaje_dejado,
    
    -- Percentuais
    CASE WHEN COUNT(l.id) > 0 
         THEN ROUND((COUNT(CASE WHEN l.fecha_contestada IS NOT NULL THEN 1 END)::DECIMAL / COUNT(l.id)) * 100, 2)
         ELSE 0 END AS tasa_contestacion,
    
    CASE WHEN COUNT(CASE WHEN l.fecha_contestada IS NOT NULL THEN 1 END) > 0
         THEN ROUND((COUNT(CASE WHEN l.presiono_1 = TRUE THEN 1 END)::DECIMAL / COUNT(CASE WHEN l.fecha_contestada IS NOT NULL THEN 1 END)) * 100, 2)
         ELSE 0 END AS tasa_presiono_1,
    
    CASE WHEN COUNT(l.id) > 0
         THEN ROUND((COUNT(CASE WHEN l.voicemail_detectado = TRUE THEN 1 END)::DECIMAL / COUNT(l.id)) * 100, 2)
         ELSE 0 END AS tasa_voicemail,
    
    CASE WHEN COUNT(CASE WHEN l.voicemail_detectado = TRUE THEN 1 END) > 0
         THEN ROUND((COUNT(CASE WHEN l.motivo_finalizacion = 'voicemail_mensaje_dejado' THEN 1 END)::DECIMAL / COUNT(CASE WHEN l.voicemail_detectado = TRUE THEN 1 END)) * 100, 2)
         ELSE 0 END AS tasa_mensaje_voicemail,
    
    -- Tempos médios
    ROUND(AVG(l.tiempo_respuesta_dtmf), 2) AS tiempo_medio_respuesta,
    ROUND(AVG(l.duracion_total), 2) AS duracion_media_llamada,
    ROUND(AVG(l.duracion_mensaje_voicemail), 2) AS duracion_media_mensaje_voicemail
    
FROM campanas_presione1 c
LEFT JOIN llamadas_presione1 l ON c.id = l.campana_id
GROUP BY c.id, c.nombre, c.activa, c.pausada;

COMMENT ON VIEW vista_estadisticas_presione1 IS 'Estatísticas resumidas por campanha Presione 1';

-- ========================================
-- 8. VERIFICAÇÃO FINAL
-- ========================================

DO $$ 
BEGIN 
    -- Verificar se as tabelas foram criadas
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_name = 'campanas_presione1') THEN
        RAISE EXCEPTION 'Tabela campanas_presione1 não foi criada';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_name = 'llamadas_presione1') THEN
        RAISE EXCEPTION 'Tabela llamadas_presione1 não foi criada';
    END IF;
    
    -- Verificar algumas colunas essenciais
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'campanas_presione1' AND column_name = 'mensaje_audio_url') THEN
        RAISE EXCEPTION 'Coluna mensaje_audio_url não encontrada';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'llamadas_presione1' AND column_name = 'presiono_1') THEN
        RAISE EXCEPTION 'Coluna presiono_1 não encontrada';
    END IF;
    
    -- Verificar alguns índices
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_campanas_presione1_activa') THEN
        RAISE EXCEPTION 'Índice idx_campanas_presione1_activa não criado';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_llamadas_presione1_presiono1') THEN
        RAISE EXCEPTION 'Índice idx_llamadas_presione1_presiono1 não criado';
    END IF;
    
    -- Verificar view
    IF NOT EXISTS (SELECT 1 FROM information_schema.views 
                   WHERE table_name = 'vista_estadisticas_presione1') THEN
        RAISE EXCEPTION 'View vista_estadisticas_presione1 não criada';
    END IF;
    
    RAISE NOTICE 'Migração Presione 1 executada com sucesso!';
    RAISE NOTICE 'Tabelas criadas: campanas_presione1, llamadas_presione1';
    RAISE NOTICE 'View criada: vista_estadisticas_presione1';
    RAISE NOTICE 'Total de índices: %', (
        SELECT COUNT(*) FROM pg_indexes 
        WHERE indexname LIKE '%presione1%'
    );
END $$; 
COMMIT; 