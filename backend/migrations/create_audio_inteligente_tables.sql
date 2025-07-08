-- Migração para criar as tabelas do Sistema de Áudio Inteligente
-- Data: 2024
-- Descrição: Cria as tabelas necessárias para o sistema de áudio inteligente

-- Criar tipos ENUM para PostgreSQL
CREATE TYPE estado_audio AS ENUM (
    'iniciando',
    'tocando', 
    'aguardando_dtmf',
    'detectando_voicemail',
    'reproduzindo_voicemail',
    'aguardando_humano',
    'conectado',
    'erro',
    'finalizado',
    'transferindo'
);

CREATE TYPE tipo_evento AS ENUM (
    'chamada_iniciada',
    'telefone_tocando',
    'atendeu',
    'voicemail_detectado',
    'dtmf_detectado',
    'timeout_dtmf',
    'humano_confirmado',
    'chamada_finalizada',
    'erro_sistema',
    'transferencia_solicitada'
);

-- Tabela de contextos de áudio
CREATE TABLE audio_contextos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    
    -- Configurações básicas
    timeout_dtmf_padrao INTEGER DEFAULT 10,
    detectar_voicemail BOOLEAN DEFAULT TRUE,
    duracao_maxima_voicemail INTEGER DEFAULT 30,
    tentativas_maximas INTEGER DEFAULT 3,
    
    -- URLs de áudio
    audio_principal_url VARCHAR(500),
    audio_voicemail_url VARCHAR(500),
    audio_erro_url VARCHAR(500),
    
    -- Configurações avançadas (JSON)
    configuracoes_avancadas JSONB,
    
    -- Metadados
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de regras de áudio
CREATE TABLE audio_regras (
    id SERIAL PRIMARY KEY,
    contexto_id INTEGER NOT NULL REFERENCES audio_contextos(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    prioridade INTEGER DEFAULT 0,
    
    -- Condições da regra
    estado_origem estado_audio NOT NULL,
    evento_disparador tipo_evento,
    
    -- Condições adicionais (JSON)
    condicoes JSONB,
    
    -- Ação da regra
    estado_destino estado_audio NOT NULL,
    audio_url VARCHAR(500),
    parametros_acao JSONB,
    
    -- Configuração
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de sessões de áudio
CREATE TABLE audio_sessoes (
    id SERIAL PRIMARY KEY,
    llamada_id INTEGER NOT NULL UNIQUE REFERENCES llamadas(id) ON DELETE CASCADE,
    contexto_id INTEGER NOT NULL REFERENCES audio_contextos(id),
    
    -- Estado atual
    estado_atual estado_audio DEFAULT 'iniciando' NOT NULL,
    estado_anterior estado_audio,
    
    -- Timestamps
    iniciado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_mudanca_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finalizado_em TIMESTAMP,
    
    -- Dados da sessão
    audio_atual_url VARCHAR(500),
    tempo_no_estado_atual INTEGER DEFAULT 0,
    tentativas_realizadas INTEGER DEFAULT 0,
    
    -- Dados contextuais (JSON)
    dados_contexto JSONB,
    
    -- Configurações específicas
    timeout_dtmf INTEGER,
    detectar_voicemail BOOLEAN
);

-- Tabela de eventos de áudio
CREATE TABLE audio_eventos (
    id SERIAL PRIMARY KEY,
    sessao_id INTEGER NOT NULL REFERENCES audio_sessoes(id) ON DELETE CASCADE,
    
    -- Detalhes do evento
    tipo_evento tipo_evento NOT NULL,
    estado_origem estado_audio NOT NULL,
    estado_destino estado_audio,
    
    -- Dados do evento
    dados_evento JSONB,
    regra_aplicada_id INTEGER REFERENCES audio_regras(id),
    
    -- Metadados
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processado_com_sucesso BOOLEAN DEFAULT TRUE,
    erro_detalhes TEXT
);

-- Tabela de templates de áudio
CREATE TABLE audio_templates (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    categoria VARCHAR(50) NOT NULL,
    
    -- Template do contexto
    configuracao_contexto JSONB NOT NULL,
    regras_template JSONB NOT NULL,
    
    -- Metadados
    ativo BOOLEAN DEFAULT TRUE,
    versao VARCHAR(10) DEFAULT '1.0',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para performance
CREATE INDEX idx_audio_contextos_nome ON audio_contextos(nome);
CREATE INDEX idx_audio_contextos_ativo ON audio_contextos(ativo);

CREATE INDEX idx_audio_regras_contexto_estado ON audio_regras(contexto_id, estado_origem);
CREATE INDEX idx_audio_regras_evento ON audio_regras(evento_disparador);
CREATE INDEX idx_audio_regras_prioridade ON audio_regras(prioridade DESC);
CREATE INDEX idx_audio_regras_ativo ON audio_regras(ativo);

CREATE INDEX idx_audio_sessoes_llamada ON audio_sessoes(llamada_id);
CREATE INDEX idx_audio_sessoes_estado ON audio_sessoes(estado_atual);
CREATE INDEX idx_audio_sessoes_contexto ON audio_sessoes(contexto_id);
CREATE INDEX idx_audio_sessoes_finalizado ON audio_sessoes(finalizado_em);

CREATE INDEX idx_audio_eventos_sessao ON audio_eventos(sessao_id);
CREATE INDEX idx_audio_eventos_tipo ON audio_eventos(tipo_evento);
CREATE INDEX idx_audio_eventos_timestamp ON audio_eventos(timestamp);

CREATE INDEX idx_audio_templates_categoria ON audio_templates(categoria);
CREATE INDEX idx_audio_templates_ativo ON audio_templates(ativo);

-- Trigger para atualizar timestamp de atualização
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_audio_contextos_updated_at 
    BEFORE UPDATE ON audio_contextos 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Inserir template padrão "Presione 1"
INSERT INTO audio_templates (nome, descricao, categoria, configuracao_contexto, regras_template) VALUES (
    'Presione 1 Padrão',
    'Template padrão para campanhas Presione 1 com detecção de voicemail',
    'presione1',
    '{
        "timeout_dtmf_padrao": 10,
        "detectar_voicemail": true,
        "duracao_maxima_voicemail": 30,
        "tentativas_maximas": 3
    }',
    '[
        {
            "nome": "Iniciar Chamada",
            "descricao": "Transição inicial quando a chamada é iniciada",
            "prioridade": 100,
            "estado_origem": "iniciando",
            "evento_disparador": "chamada_iniciada",
            "estado_destino": "tocando"
        },
        {
            "nome": "Atendimento Detectado",
            "descricao": "Quando a chamada é atendida, aguardar DTMF",
            "prioridade": 90,
            "estado_origem": "tocando",
            "evento_disparador": "atendeu",
            "estado_destino": "aguardando_dtmf"
        },
        {
            "nome": "Tecla 1 Pressionada",
            "descricao": "Cliente pressionou tecla 1, conectar",
            "prioridade": 95,
            "estado_origem": "aguardando_dtmf",
            "evento_disparador": "dtmf_detectado",
            "estado_destino": "conectado",
            "condicoes": [
                {
                    "campo": "dtmf_tecla",
                    "operador": "igual",
                    "valor": "1"
                }
            ]
        },
        {
            "nome": "Timeout DTMF",
            "descricao": "Timeout aguardando DTMF, verificar se é voicemail",
            "prioridade": 80,
            "estado_origem": "aguardando_dtmf",
            "evento_disparador": "timeout_dtmf",
            "estado_destino": "detectando_voicemail"
        },
        {
            "nome": "Voicemail Detectado",
            "descricao": "Voicemail detectado, reproduzir mensagem",
            "prioridade": 85,
            "estado_origem": "detectando_voicemail",
            "evento_disparador": "voicemail_detectado",
            "estado_destino": "reproduzindo_voicemail"
        },
        {
            "nome": "Humano Após Voicemail",
            "descricao": "Humano detectado após análise de voicemail",
            "prioridade": 75,
            "estado_origem": "detectando_voicemail",
            "evento_disparador": "humano_confirmado",
            "estado_destino": "aguardando_dtmf"
        }
    ]'
);

-- Comentários nas tabelas
COMMENT ON TABLE audio_contextos IS 'Contextos de áudio que definem configurações para diferentes tipos de campanhas';
COMMENT ON TABLE audio_regras IS 'Regras do motor de reprodução dinâmica que definem transições de estado';
COMMENT ON TABLE audio_sessoes IS 'Sessões de áudio que acompanham o estado de cada chamada';
COMMENT ON TABLE audio_eventos IS 'Registro de eventos que ocorrem durante as sessões de áudio';
COMMENT ON TABLE audio_templates IS 'Templates pré-configurados para facilitar criação de contextos';

-- Verificar se as tabelas foram criadas
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename LIKE 'audio_%'
ORDER BY tablename; 