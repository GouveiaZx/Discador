-- Migração para atualizar modelos com blacklist melhorada e múltiplas listas
-- Executar após criar as tablas base

-- ========================================
-- 1. ATUALIZAR TABLA LISTA_NEGRA
-- ========================================

-- Adicionar novas colunas à tabla lista_negra
ALTER TABLE lista_negra 
ADD COLUMN IF NOT EXISTS numero_normalizado VARCHAR(20),
ADD COLUMN IF NOT EXISTS observaciones TEXT,
ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE NOT NULL,
ADD COLUMN IF NOT EXISTS creado_por VARCHAR(100),
ADD COLUMN IF NOT EXISTS veces_bloqueado INTEGER DEFAULT 0 NOT NULL,
ADD COLUMN IF NOT EXISTS ultima_vez_bloqueado TIMESTAMP WITH TIME ZONE;

-- Atualizar registros existentes
UPDATE lista_negra 
SET numero_normalizado = numero 
WHERE numero_normalizado IS NULL;

-- Fazer numero_normalizado NOT NULL e UNIQUE
ALTER TABLE lista_negra 
ALTER COLUMN numero_normalizado SET NOT NULL;

-- Remover constraint UNIQUE do campo numero (se existir)
DO $$ 
BEGIN 
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints 
               WHERE constraint_name = 'lista_negra_numero_key' 
               AND table_name = 'lista_negra') THEN
        ALTER TABLE lista_negra DROP CONSTRAINT lista_negra_numero_key;
    END IF;
END $$;

-- Adicionar constraint UNIQUE para numero_normalizado
ALTER TABLE lista_negra 
ADD CONSTRAINT lista_negra_numero_normalizado_key UNIQUE (numero_normalizado);

-- Adicionar novos índices
CREATE INDEX IF NOT EXISTS idx_lista_negra_normalizado ON lista_negra(numero_normalizado);
CREATE INDEX IF NOT EXISTS idx_lista_negra_activo ON lista_negra(activo);
CREATE INDEX IF NOT EXISTS idx_lista_negra_fecha ON lista_negra(fecha_creacion);

-- ========================================
-- 2. ATUALIZAR TABLA LLAMADAS
-- ========================================

-- Adicionar novas colunas à tabla llamadas
ALTER TABLE llamadas 
ADD COLUMN IF NOT EXISTS numero_normalizado VARCHAR(20),
ADD COLUMN IF NOT EXISTS id_lista_llamadas INTEGER,
ADD COLUMN IF NOT EXISTS bloqueado_blacklist BOOLEAN DEFAULT FALSE NOT NULL;

-- Atualizar registros existentes (normalizar números existentes)
-- Esta função pode precisar ser ajustada dependendo dos dados existentes
UPDATE llamadas 
SET numero_normalizado = 
    CASE 
        WHEN numero_destino LIKE '+549%' THEN numero_destino
        WHEN numero_destino LIKE '+54%' THEN '+549' || SUBSTRING(numero_destino FROM 4)
        WHEN numero_destino LIKE '011%' THEN '+549' || SUBSTRING(numero_destino FROM 3)
        WHEN numero_destino LIKE '11%' AND LENGTH(numero_destino) = 10 THEN '+549' || numero_destino
        ELSE '+549' || numero_destino
    END
WHERE numero_normalizado IS NULL;

-- Fazer numero_normalizado NOT NULL
ALTER TABLE llamadas 
ALTER COLUMN numero_normalizado SET NOT NULL;

-- Adicionar foreign key para lista_llamadas (se tabla existe)
DO $$ 
BEGIN 
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_name = 'listas_llamadas') THEN
        ALTER TABLE llamadas 
        ADD CONSTRAINT fk_llamadas_lista_llamadas 
        FOREIGN KEY (id_lista_llamadas) 
        REFERENCES listas_llamadas(id);
    END IF;
END $$;

-- Adicionar novos índices
CREATE INDEX IF NOT EXISTS idx_llamadas_numero_normalizado ON llamadas(numero_normalizado);
CREATE INDEX IF NOT EXISTS idx_llamadas_lista ON llamadas(id_lista_llamadas);
CREATE INDEX IF NOT EXISTS idx_llamadas_bloqueado ON llamadas(bloqueado_blacklist);

-- ========================================
-- 3. ATUALIZAR TABLA LISTAS_LLAMADAS (se precisar)
-- ========================================

-- Adicionar índices adicionais se a tabla já existe
DO $$ 
BEGIN 
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_name = 'listas_llamadas') THEN
        
        -- Verificar se índices já existem antes de criar
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_listas_nombre') THEN
            CREATE INDEX idx_listas_nombre ON listas_llamadas(nombre);
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_listas_activa') THEN
            CREATE INDEX idx_listas_activa ON listas_llamadas(activa);
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_listas_fecha') THEN
            CREATE INDEX idx_listas_fecha ON listas_llamadas(fecha_creacion);
        END IF;
    END IF;
END $$;

-- ========================================
-- 4. TRIGGERS E FUNÇÕES
-- ========================================

-- Atualizar trigger para fecha_actualizacion em lista_negra
CREATE OR REPLACE FUNCTION update_fecha_actualizacion_lista_negra()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_lista_negra_fecha ON lista_negra;
CREATE TRIGGER trigger_update_lista_negra_fecha
BEFORE UPDATE ON lista_negra
FOR EACH ROW
EXECUTE FUNCTION update_fecha_actualizacion_lista_negra();

-- ========================================
-- 5. COMENTÁRIOS ATUALIZADOS
-- ========================================

-- Atualizar comentários das tabelas
COMMENT ON TABLE lista_negra IS 'Tabla para almacenar números de teléfono bloqueados (blacklist)';
COMMENT ON COLUMN lista_negra.numero_normalizado IS 'Número normalizado en formato +549XXXXXXXXXX';
COMMENT ON COLUMN lista_negra.activo IS 'Si el bloqueo está activo (soft delete)';
COMMENT ON COLUMN lista_negra.veces_bloqueado IS 'Contador de veces que se intentó llamar a este número';
COMMENT ON COLUMN lista_negra.ultima_vez_bloqueado IS 'Última vez que se bloqueó una llamada a este número';
COMMENT ON COLUMN lista_negra.creado_por IS 'Usuario que agregó el número a la blacklist';
COMMENT ON COLUMN lista_negra.observaciones IS 'Observaciones adicionales sobre el bloqueo';

COMMENT ON COLUMN llamadas.numero_normalizado IS 'Número normalizado para comparaciones con blacklist';
COMMENT ON COLUMN llamadas.id_lista_llamadas IS 'Referencia a la lista de llamadas de origen';
COMMENT ON COLUMN llamadas.bloqueado_blacklist IS 'Si la llamada fue bloqueada por blacklist';

-- ========================================
-- 6. DATOS DE EJEMPLO (OPCIONAL)
-- ========================================

-- Insertar algunos números de ejemplo en blacklist (comentado por seguridad)
/*
INSERT INTO lista_negra (numero, numero_normalizado, motivo, activo, creado_por)
VALUES 
    ('+5491100000000', '+5491100000000', 'Número de test - no llamar', true, 'system'),
    ('011 0000-0000', '+54911000000000', 'Número inválido de ejemplo', true, 'system')
ON CONFLICT (numero_normalizado) DO NOTHING;
*/

-- ========================================
-- 7. VERIFICAÇÃO FINAL
-- ========================================

-- Verificar que las tablas fueron actualizadas correctamente
DO $$ 
BEGIN 
    -- Verificar colunas de lista_negra
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'lista_negra' AND column_name = 'numero_normalizado') THEN
        RAISE EXCEPTION 'Coluna numero_normalizado não foi criada em lista_negra';
    END IF;
    
    -- Verificar colunas de llamadas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'llamadas' AND column_name = 'numero_normalizado') THEN
        RAISE EXCEPTION 'Coluna numero_normalizado não foi criada em llamadas';
    END IF;
    
    RAISE NOTICE 'Migração executada com sucesso!';
END $$; 