-- ================================================
-- Migração: Sistema CODE2BASE Avançado
-- Descrição: Cria tabelas para seleção inteligente de CLIs
-- Versão: 1.0.0
-- Data: 2024
-- ================================================

-- Criar ENUMs necessários
DO $$ BEGIN
    -- Enum para tipos de operadoras
    CREATE TYPE tipo_operadora AS ENUM (
        'movistar', 'vodafone', 'orange', 'yoigo', 
        'pepephone', 'mas_movil', 'otra', 'desconocida'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Enum para tipos de números
    CREATE TYPE tipo_numero AS ENUM (
        'fijo', 'movil', 'especial', 'internacional', 
        'premium', 'gratuito', 'otro'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Enum para tipos de regras
    CREATE TYPE tipo_regla AS ENUM (
        'geografia', 'operadora', 'campana', 'horario', 
        'calidad', 'costo', 'fallback', 'personalizada'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ================================================
-- TABELA: Países
-- ================================================
CREATE TABLE IF NOT EXISTS code2base_paises (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(5) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    codigo_telefone VARCHAR(10) NOT NULL,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para paises
CREATE INDEX IF NOT EXISTS idx_code2base_paises_codigo ON code2base_paises(codigo);
CREATE INDEX IF NOT EXISTS idx_code2base_paises_activo ON code2base_paises(activo);

-- ================================================
-- TABELA: Estados/Províncias
-- ================================================
CREATE TABLE IF NOT EXISTS code2base_estados (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    pais_id INTEGER NOT NULL REFERENCES code2base_paises(id) ON DELETE CASCADE,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(codigo, pais_id)
);

-- Índices para estados
CREATE INDEX IF NOT EXISTS idx_code2base_estados_codigo ON code2base_estados(codigo);
CREATE INDEX IF NOT EXISTS idx_code2base_estados_pais_id ON code2base_estados(pais_id);
CREATE INDEX IF NOT EXISTS idx_code2base_estados_activo ON code2base_estados(activo);

-- ================================================
-- TABELA: Cidades
-- ================================================
CREATE TABLE IF NOT EXISTS code2base_cidades (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    codigo_postal VARCHAR(20),
    estado_id INTEGER NOT NULL REFERENCES code2base_estados(id) ON DELETE CASCADE,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para cidades
CREATE INDEX IF NOT EXISTS idx_code2base_cidades_nome ON code2base_cidades(nome);
CREATE INDEX IF NOT EXISTS idx_code2base_cidades_estado_id ON code2base_cidades(estado_id);
CREATE INDEX IF NOT EXISTS idx_code2base_cidades_activo ON code2base_cidades(activo);
CREATE INDEX IF NOT EXISTS idx_code2base_cidades_codigo_postal ON code2base_cidades(codigo_postal);

-- ================================================
-- TABELA: Prefixos Telefônicos
-- ================================================
CREATE TABLE IF NOT EXISTS code2base_prefijos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    tipo_numero tipo_numero NOT NULL DEFAULT 'fijo',
    operadora tipo_operadora DEFAULT 'desconocida',
    pais_id INTEGER NOT NULL REFERENCES code2base_paises(id) ON DELETE CASCADE,
    estado_id INTEGER REFERENCES code2base_estados(id) ON DELETE SET NULL,
    cidade_id INTEGER REFERENCES code2base_cidades(id) ON DELETE SET NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    prioridad INTEGER DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para prefixos
CREATE INDEX IF NOT EXISTS idx_code2base_prefijos_codigo ON code2base_prefijos(codigo);
CREATE INDEX IF NOT EXISTS idx_code2base_prefijos_tipo_numero ON code2base_prefijos(tipo_numero);
CREATE INDEX IF NOT EXISTS idx_code2base_prefijos_operadora ON code2base_prefijos(operadora);
CREATE INDEX IF NOT EXISTS idx_code2base_prefijos_pais_id ON code2base_prefijos(pais_id);
CREATE INDEX IF NOT EXISTS idx_code2base_prefijos_estado_id ON code2base_prefijos(estado_id);
CREATE INDEX IF NOT EXISTS idx_code2base_prefijos_activo ON code2base_prefijos(activo);

-- ================================================
-- TABELA: CLIs Geográficos
-- ================================================
CREATE TABLE IF NOT EXISTS code2base_clis_geo (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(20) NOT NULL,
    numero_normalizado VARCHAR(20) NOT NULL UNIQUE,
    cli_id INTEGER NOT NULL REFERENCES cli(id) ON DELETE CASCADE,
    prefijo_id INTEGER NOT NULL REFERENCES code2base_prefijos(id) ON DELETE CASCADE,
    tipo_numero tipo_numero NOT NULL DEFAULT 'fijo',
    operadora tipo_operadora DEFAULT 'desconocida',
    calidad DECIMAL(3,2) DEFAULT 1.0 CHECK (calidad >= 0.0 AND calidad <= 1.0),
    tasa_exito DECIMAL(5,4) DEFAULT 0.0 CHECK (tasa_exito >= 0.0 AND tasa_exito <= 1.0),
    veces_usado INTEGER DEFAULT 0,
    ultima_vez_usado TIMESTAMP,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(cli_id)
);

-- Índices para CLIs geográficos
CREATE INDEX IF NOT EXISTS idx_code2base_clis_geo_numero_normalizado ON code2base_clis_geo(numero_normalizado);
CREATE INDEX IF NOT EXISTS idx_code2base_clis_geo_cli_id ON code2base_clis_geo(cli_id);
CREATE INDEX IF NOT EXISTS idx_code2base_clis_geo_prefijo_id ON code2base_clis_geo(prefijo_id);
CREATE INDEX IF NOT EXISTS idx_code2base_clis_geo_tipo_numero ON code2base_clis_geo(tipo_numero);
CREATE INDEX IF NOT EXISTS idx_code2base_clis_geo_operadora ON code2base_clis_geo(operadora);
CREATE INDEX IF NOT EXISTS idx_code2base_clis_geo_calidad ON code2base_clis_geo(calidad);
CREATE INDEX IF NOT EXISTS idx_code2base_clis_geo_tasa_exito ON code2base_clis_geo(tasa_exito);
CREATE INDEX IF NOT EXISTS idx_code2base_clis_geo_activo ON code2base_clis_geo(activo);

-- ================================================
-- TABELA: Regras de Seleção de CLI
-- ================================================
CREATE TABLE IF NOT EXISTS code2base_reglas_cli (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    tipo_regra tipo_regla NOT NULL DEFAULT 'geografia',
    condiciones JSONB NOT NULL DEFAULT '{}',
    prioridad INTEGER DEFAULT 1,
    peso DECIMAL(3,2) DEFAULT 1.0 CHECK (peso >= 0.0 AND peso <= 2.0),
    activo BOOLEAN DEFAULT true,
    aplica_a_campaña BOOLEAN DEFAULT false,
    campaña_ids INTEGER[] DEFAULT '{}',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para regras
CREATE INDEX IF NOT EXISTS idx_code2base_reglas_cli_nome ON code2base_reglas_cli(nome);
CREATE INDEX IF NOT EXISTS idx_code2base_reglas_cli_tipo_regra ON code2base_reglas_cli(tipo_regra);
CREATE INDEX IF NOT EXISTS idx_code2base_reglas_cli_prioridad ON code2base_reglas_cli(prioridad);
CREATE INDEX IF NOT EXISTS idx_code2base_reglas_cli_activo ON code2base_reglas_cli(activo);
CREATE INDEX IF NOT EXISTS idx_code2base_reglas_cli_condiciones ON code2base_reglas_cli USING GIN(condiciones);

-- ================================================
-- TABELA: Histórico de Seleções de CLI
-- ================================================
CREATE TABLE IF NOT EXISTS code2base_historial_seleccion_cli (
    id SERIAL PRIMARY KEY,
    numero_destino VARCHAR(20) NOT NULL,
    numero_destino_normalizado VARCHAR(20) NOT NULL,
    prefijo_destino VARCHAR(10),
    cli_geo_id INTEGER NOT NULL REFERENCES code2base_clis_geo(id) ON DELETE CASCADE,
    campaña_id INTEGER,
    algoritmo_usado VARCHAR(50) DEFAULT 'weighted_score',
    score_seleccion DECIMAL(5,4) DEFAULT 0.0,
    reglas_aplicadas JSONB DEFAULT '[]',
    tiempo_seleccion_ms INTEGER DEFAULT 0,
    llamada_exitosa BOOLEAN,
    duracion_segundos INTEGER,
    fecha_seleccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion_resultado TIMESTAMP
);

-- Índices para histórico
CREATE INDEX IF NOT EXISTS idx_code2base_historial_numero_destino ON code2base_historial_seleccion_cli(numero_destino_normalizado);
CREATE INDEX IF NOT EXISTS idx_code2base_historial_cli_geo_id ON code2base_historial_seleccion_cli(cli_geo_id);
CREATE INDEX IF NOT EXISTS idx_code2base_historial_fecha_seleccion ON code2base_historial_seleccion_cli(fecha_seleccion);
CREATE INDEX IF NOT EXISTS idx_code2base_historial_exitosa ON code2base_historial_seleccion_cli(llamada_exitosa);

-- ================================================
-- TRIGGERS PARA ATUALIZAÇÃO AUTOMÁTICA
-- ================================================

-- Função para atualizar timestamps
CREATE OR REPLACE FUNCTION update_code2base_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar triggers
DROP TRIGGER IF EXISTS trigger_code2base_paises_updated_at ON code2base_paises;
CREATE TRIGGER trigger_code2base_paises_updated_at
    BEFORE UPDATE ON code2base_paises
    FOR EACH ROW EXECUTE FUNCTION update_code2base_timestamp();

DROP TRIGGER IF EXISTS trigger_code2base_estados_updated_at ON code2base_estados;
CREATE TRIGGER trigger_code2base_estados_updated_at
    BEFORE UPDATE ON code2base_estados
    FOR EACH ROW EXECUTE FUNCTION update_code2base_timestamp();

DROP TRIGGER IF EXISTS trigger_code2base_cidades_updated_at ON code2base_cidades;
CREATE TRIGGER trigger_code2base_cidades_updated_at
    BEFORE UPDATE ON code2base_cidades
    FOR EACH ROW EXECUTE FUNCTION update_code2base_timestamp();

DROP TRIGGER IF EXISTS trigger_code2base_prefijos_updated_at ON code2base_prefijos;
CREATE TRIGGER trigger_code2base_prefijos_updated_at
    BEFORE UPDATE ON code2base_prefijos
    FOR EACH ROW EXECUTE FUNCTION update_code2base_timestamp();

DROP TRIGGER IF EXISTS trigger_code2base_clis_geo_updated_at ON code2base_clis_geo;
CREATE TRIGGER trigger_code2base_clis_geo_updated_at
    BEFORE UPDATE ON code2base_clis_geo
    FOR EACH ROW EXECUTE FUNCTION update_code2base_timestamp();

DROP TRIGGER IF EXISTS trigger_code2base_reglas_cli_updated_at ON code2base_reglas_cli;
CREATE TRIGGER trigger_code2base_reglas_cli_updated_at
    BEFORE UPDATE ON code2base_reglas_cli
    FOR EACH ROW EXECUTE FUNCTION update_code2base_timestamp();

-- ================================================
-- DADOS INICIAIS
-- ================================================

-- Inserir país España
INSERT INTO code2base_paises (codigo, nome, codigo_telefone, activo)
VALUES ('ES', 'España', '+34', true)
ON CONFLICT (codigo) DO NOTHING;

-- Inserir alguns estados da Espanha
DO $$
DECLARE
    espanha_id INTEGER;
BEGIN
    SELECT id INTO espanha_id FROM code2base_paises WHERE codigo = 'ES';
    
    IF espanha_id IS NOT NULL THEN
        INSERT INTO code2base_estados (codigo, nome, pais_id, activo) VALUES
        ('MD', 'Madrid', espanha_id, true),
        ('CT', 'Cataluña', espanha_id, true),
        ('AN', 'Andalucía', espanha_id, true),
        ('VC', 'Valencia', espanha_id, true),
        ('PV', 'País Vasco', espanha_id, true)
        ON CONFLICT (codigo, pais_id) DO NOTHING;
    END IF;
END
$$;

-- Inserir prefixos básicos
DO $$
DECLARE
    espanha_id INTEGER;
    madrid_estado_id INTEGER;
    barcelona_estado_id INTEGER;
BEGIN
    SELECT id INTO espanha_id FROM code2base_paises WHERE codigo = 'ES';
    SELECT id INTO madrid_estado_id FROM code2base_estados WHERE codigo = 'MD';
    SELECT id INTO barcelona_estado_id FROM code2base_estados WHERE codigo = 'CT';
    
    IF espanha_id IS NOT NULL THEN
        INSERT INTO code2base_prefijos (codigo, tipo_numero, operadora, pais_id, estado_id, descripcion, prioridad, activo) VALUES
        ('91', 'fijo', 'movistar', espanha_id, madrid_estado_id, 'Madrid - Fijo', 1, true),
        ('93', 'fijo', 'movistar', espanha_id, barcelona_estado_id, 'Barcelona - Fijo', 1, true),
        ('6', 'movil', 'movistar', espanha_id, null, 'Móvel - Movistar', 2, true),
        ('7', 'movil', 'vodafone', espanha_id, null, 'Móvel - Vodafone', 2, true)
        ON CONFLICT (codigo) DO NOTHING;
    END IF;
END
$$;

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
    AND table_name LIKE 'code2base_%';
    
    RAISE NOTICE 'Sistema CODE2BASE: % tabelas criadas com sucesso', table_count;
END
$$;
