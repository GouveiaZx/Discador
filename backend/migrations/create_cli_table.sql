-- Migração para criar a tabela CLI (Caller Line Identification)
-- Esta tabela armazena os números CLI permitidos para usar nas chamadas

-- ========================================
-- 1. CRIAR TABLA CLI
-- ========================================

CREATE TABLE IF NOT EXISTS cli (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(20) NOT NULL UNIQUE,
    numero_normalizado VARCHAR(20) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    veces_usado INTEGER DEFAULT 0 NOT NULL,
    ultima_vez_usado TIMESTAMP WITH TIME ZONE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    notas TEXT
);

-- ========================================
-- 2. CRIAR ÍNDICES
-- ========================================

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_cli_numero ON cli(numero);
CREATE INDEX IF NOT EXISTS idx_cli_normalizado ON cli(numero_normalizado);
CREATE INDEX IF NOT EXISTS idx_cli_activo ON cli(activo);
CREATE INDEX IF NOT EXISTS idx_cli_fecha ON cli(fecha_creacion);
CREATE INDEX IF NOT EXISTS idx_cli_veces_usado ON cli(veces_usado);

-- ========================================
-- 3. TRIGGERS PARA ATUALIZAÇÃO AUTOMÁTICA
-- ========================================

-- Função para atualizar fecha_actualizacion automaticamente
CREATE OR REPLACE FUNCTION update_fecha_actualizacion_cli()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar fecha_actualizacion
DROP TRIGGER IF EXISTS trigger_update_cli_fecha ON cli;
CREATE TRIGGER trigger_update_cli_fecha
BEFORE UPDATE ON cli
FOR EACH ROW
EXECUTE FUNCTION update_fecha_actualizacion_cli();

-- ========================================
-- 4. COMENTÁRIOS DA TABELA
-- ========================================

COMMENT ON TABLE cli IS 'Tabla para almacenar números CLI (Caller Line Identification) permitidos';
COMMENT ON COLUMN cli.numero IS 'Número CLI original como fue ingresado';
COMMENT ON COLUMN cli.numero_normalizado IS 'Número CLI normalizado en formato +549XXXXXXXXXX';
COMMENT ON COLUMN cli.descripcion IS 'Descripción del CLI';
COMMENT ON COLUMN cli.activo IS 'Si el CLI está activo y disponible para uso';
COMMENT ON COLUMN cli.veces_usado IS 'Contador de veces que se ha usado este CLI';
COMMENT ON COLUMN cli.ultima_vez_usado IS 'Última vez que se usó este CLI';
COMMENT ON COLUMN cli.fecha_creacion IS 'Fecha de creación del registro';
COMMENT ON COLUMN cli.fecha_actualizacion IS 'Fecha de última actualización del registro';
COMMENT ON COLUMN cli.notas IS 'Notas adicionales sobre el CLI';

-- ========================================
-- 5. DATOS DE EJEMPLO (OPCIONAL)
-- ========================================

-- Insertar algunos CLIs de ejemplo
-- Estos son números de ejemplo - reemplazar con números reales permitidos
INSERT INTO cli (numero, numero_normalizado, descripcion, activo)
VALUES 
    ('+5491122334455', '+5491122334455', 'CLI principal de ejemplo', true),
    ('+5491133445566', '+5491133445566', 'CLI secundario de ejemplo', true),
    ('+5491144556677', '+5491144556677', 'CLI terciario de ejemplo', true),
    ('011 2233-4455', '+54911223344855', 'CLI con formato local', true),
    ('011 3344-5566', '+5491133445566', 'CLI con formato local 2', false)
ON CONFLICT (numero_normalizado) DO NOTHING;

-- ========================================
-- 6. VERIFICAÇÃO FINAL
-- ========================================

-- Verificar que la tabla fue creada correctamente
DO $$ 
BEGIN 
    -- Verificar que la tabla existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_name = 'cli') THEN
        RAISE EXCEPTION 'Tabla cli não foi criada';
    END IF;
    
    -- Verificar columnas essenciais
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'cli' AND column_name = 'numero_normalizado') THEN
        RAISE EXCEPTION 'Coluna numero_normalizado não foi criada';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'cli' AND column_name = 'veces_usado') THEN
        RAISE EXCEPTION 'Coluna veces_usado não foi criada';
    END IF;
    
    -- Verificar índices
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_cli_normalizado') THEN
        RAISE EXCEPTION 'Índice idx_cli_normalizado não foi criado';
    END IF;
    
    RAISE NOTICE 'Tabla CLI criada com sucesso!';
    RAISE NOTICE 'Registros CLI de exemplo: %', (SELECT COUNT(*) FROM cli);
END $$; 