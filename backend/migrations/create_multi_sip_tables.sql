-- ================================================
-- MIGRAÇÃO: Sistema Multi-SIP com Múltiplos Provedores
-- Versão: 1.0
-- Data: 2025-01-09
-- Descrição: Cria estrutura completa para gestão de múltiplos provedores SIP
-- ================================================

-- 1. CRIAR ENUMS PARA SISTEMA MULTI-SIP
DO $$
BEGIN
    -- Tipos de provedor SIP
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_provedor_enum') THEN
        CREATE TYPE tipo_provedor_enum AS ENUM (
            'twilio',
            'gottrunk', 
            'asterisk_peer',
            'sip_trunk',
            'custom'
        );
    END IF;

    -- Status do provedor SIP
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_provedor_enum') THEN
        CREATE TYPE status_provedor_enum AS ENUM (
            'ativo',
            'inativo',
            'teste',
            'erro'
        );
    END IF;

    -- Tipos de ligação
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_ligacao_enum') THEN
        CREATE TYPE tipo_ligacao_enum AS ENUM (
            'celular',
            'fixo',
            'internacional',
            'especial'
        );
    END IF;

    -- Métodos de seleção
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'metodo_selecao_enum') THEN
        CREATE TYPE metodo_selecao_enum AS ENUM (
            'menor_custo',
            'melhor_qualidade',
            'inteligente'
        );
    END IF;
END $$;

-- 2. TABELA PRINCIPAL: PROVEDORES SIP
CREATE TABLE IF NOT EXISTS provedor_sip (
    id SERIAL PRIMARY KEY,
    
    -- Identificação do provedor
    nome VARCHAR(100) NOT NULL,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    tipo_provedor tipo_provedor_enum NOT NULL,
    descricao TEXT,
    
    -- Configurações SIP
    servidor_sip VARCHAR(255) NOT NULL,
    porta_sip INTEGER NOT NULL DEFAULT 5060,
    protocolo VARCHAR(10) NOT NULL DEFAULT 'UDP',
    
    -- Autenticação
    usuario_sip VARCHAR(100) NOT NULL,
    senha_sip VARCHAR(255) NOT NULL,
    realm VARCHAR(100),
    
    -- Limitações e configurações
    max_chamadas_simultaneas INTEGER DEFAULT 50,
    max_chamadas_por_segundo INTEGER DEFAULT 5,
    timeout_conexao INTEGER DEFAULT 30,
    
    -- Prioridade e balanceamento
    prioridade INTEGER DEFAULT 100,
    peso_balanceamento INTEGER DEFAULT 10,
    
    -- Status e monitoramento
    status status_provedor_enum NOT NULL DEFAULT 'teste',
    ultima_verificacao TIMESTAMP,
    latencia_media_ms FLOAT DEFAULT 0.0,
    taxa_sucesso FLOAT DEFAULT 0.0,
    
    -- Custos base
    custo_base_por_minuto DECIMAL(10,6) DEFAULT 0.0,
    moeda VARCHAR(3) DEFAULT 'USD',
    
    -- Auditoria
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABELA DE TARIFAS POR PROVEDOR
CREATE TABLE IF NOT EXISTS tarifa_sip (
    id SERIAL PRIMARY KEY,
    
    -- Referência ao provedor
    provedor_id INTEGER NOT NULL REFERENCES provedor_sip(id) ON DELETE CASCADE,
    
    -- Identificação do destino
    pais_codigo VARCHAR(5) NOT NULL,
    prefixo VARCHAR(20) NOT NULL,
    descricao_destino VARCHAR(200) NOT NULL,
    tipo_ligacao tipo_ligacao_enum NOT NULL,
    
    -- Tarifação específica
    custo_por_minuto DECIMAL(10,6) NOT NULL,
    moeda VARCHAR(3) DEFAULT 'USD',
    taxa_conexao DECIMAL(10,6) DEFAULT 0.0,
    
    -- Controle de ativação
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. TABELA DE LOGS DE SELEÇÃO
CREATE TABLE IF NOT EXISTS log_selecao_provedor (
    id SERIAL PRIMARY KEY,
    
    -- Identificação única da seleção
    uuid_selecao UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    -- Dados da chamada
    numero_destino VARCHAR(20) NOT NULL,
    campanha_id INTEGER,
    
    -- Resultado da seleção
    provedor_id INTEGER NOT NULL REFERENCES provedor_sip(id),
    metodo_usado VARCHAR(30) NOT NULL,
    
    -- Métricas da decisão
    score_final FLOAT NOT NULL,
    justificativa TEXT NOT NULL,
    tempo_selecao_ms INTEGER NOT NULL,
    
    -- Resultado da chamada
    chamada_estabelecida BOOLEAN,
    duracao_segundos INTEGER,
    custo_final DECIMAL(10,4),
    
    -- Timestamp da seleção
    timestamp_selecao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. ÍNDICES PARA PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_provedor_sip_nome ON provedor_sip(nome);
CREATE INDEX IF NOT EXISTS idx_provedor_sip_codigo ON provedor_sip(codigo);
CREATE INDEX IF NOT EXISTS idx_provedor_sip_status ON provedor_sip(status);
CREATE INDEX IF NOT EXISTS idx_provedor_sip_prioridade ON provedor_sip(prioridade);

CREATE INDEX IF NOT EXISTS idx_tarifa_sip_provedor ON tarifa_sip(provedor_id);
CREATE INDEX IF NOT EXISTS idx_tarifa_sip_prefixo ON tarifa_sip(prefixo);
CREATE INDEX IF NOT EXISTS idx_tarifa_sip_custo ON tarifa_sip(custo_por_minuto);

CREATE INDEX IF NOT EXISTS idx_log_selecao_timestamp ON log_selecao_provedor(timestamp_selecao);
CREATE INDEX IF NOT EXISTS idx_log_selecao_provedor ON log_selecao_provedor(provedor_id);
CREATE INDEX IF NOT EXISTS idx_log_selecao_destino ON log_selecao_provedor(numero_destino);

-- 6. TRIGGER PARA ATUALIZAÇÃO AUTOMÁTICA
CREATE OR REPLACE FUNCTION atualizar_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_provedor_sip_update
    BEFORE UPDATE ON provedor_sip
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_fecha_actualizacion();

CREATE TRIGGER trigger_tarifa_sip_update
    BEFORE UPDATE ON tarifa_sip
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_fecha_actualizacion();

-- 7. DADOS INICIAIS DE EXEMPLO
INSERT INTO provedor_sip (
    nome, codigo, tipo_provedor, descricao,
    servidor_sip, porta_sip, protocolo,
    usuario_sip, senha_sip, realm,
    prioridade, custo_base_por_minuto
) VALUES (
    'Provedor Local Teste', 'LOCAL_TEST', 'asterisk_peer', 
    'Provedor SIP local para testes do sistema',
    'localhost', 5060, 'UDP',
    'test_user', 'test_password', 'localhost',
    100, 0.010
) ON CONFLICT (codigo) DO NOTHING;

-- 8. VIEW PARA ESTATÍSTICAS
CREATE OR REPLACE VIEW v_estatisticas_provedor AS
SELECT 
    p.id,
    p.nome,
    p.codigo,
    p.status,
    p.taxa_sucesso,
    p.latencia_media_ms,
    COUNT(l.id) as total_selecoes,
    COUNT(CASE WHEN l.chamada_estabelecida = true THEN 1 END) as selecoes_sucesso
FROM provedor_sip p
LEFT JOIN log_selecao_provedor l ON p.id = l.provedor_id
WHERE p.activo = true
GROUP BY p.id, p.nome, p.codigo, p.status, p.taxa_sucesso, p.latencia_media_ms;

-- ================================================
-- SUCESSO: Migração Multi-SIP aplicada!
-- ================================================
