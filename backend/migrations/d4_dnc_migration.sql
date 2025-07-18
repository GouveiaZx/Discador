
-- Migração de Dados DNC do Sistema D4 para Sistema Atual
-- Gerado automaticamente em: 2025-07-16 13:45:49,868

-- 1. Criar tabela DNC compatível se não existir
CREATE TABLE IF NOT EXISTS dnc_numbers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(15) NOT NULL UNIQUE,
    status VARCHAR(50) DEFAULT 'active',
    country_code VARCHAR(5) DEFAULT '+1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'd4_migration',
    notes TEXT
);

-- 2. Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_dnc_phone_number ON dnc_numbers(phone_number);
CREATE INDEX IF NOT EXISTS idx_dnc_status ON dnc_numbers(status);
CREATE INDEX IF NOT EXISTS idx_dnc_country_code ON dnc_numbers(country_code);

-- 3. Inserir dados de exemplo baseados no template D4
-- Nota: Dados reais devem ser importados de backup do sistema D4
INSERT INTO dnc_numbers (phone_number, status, country_code, source, notes) VALUES
('5551234567', 'active', '+1', 'd4_migration', 'Migrado do sistema D4 - Template'),
('5559876543', 'active', '+1', 'd4_migration', 'Migrado do sistema D4 - Template')
ON CONFLICT (phone_number) DO NOTHING;

-- 4. Criar tabela para áudios DNC
CREATE TABLE IF NOT EXISTS dnc_audio_files (
    id SERIAL PRIMARY KEY,
    language VARCHAR(10) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    original_format VARCHAR(10) DEFAULT 'g729',
    converted_format VARCHAR(10) DEFAULT 'wav',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'd4_migration'
);

-- 5. Inserir informações dos áudios convertidos


-- 6. Criar configurações DNC multilíngue
CREATE TABLE IF NOT EXISTS dnc_configurations (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(5) NOT NULL,
    language VARCHAR(10) NOT NULL,
    audio_file_id INTEGER REFERENCES dnc_audio_files(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country_code, language)
);

-- 7. Configurações padrão baseadas no D4
INSERT INTO dnc_configurations (country_code, language, audio_file_id, is_active)
SELECT '+1', 'english', id, true FROM dnc_audio_files WHERE language = 'english' AND source = 'd4_migration'
UNION ALL
SELECT '+1', 'spanish', id, true FROM dnc_audio_files WHERE language = 'spanish' AND source = 'd4_migration'
ON CONFLICT (country_code, language) DO NOTHING;

-- 8. Comentários e documentação
COMMENT ON TABLE dnc_numbers IS 'Números DNC migrados do sistema D4 antigo';
COMMENT ON TABLE dnc_audio_files IS 'Arquivos de áudio DNC convertidos de G.729 para WAV';
COMMENT ON TABLE dnc_configurations IS 'Configurações DNC multilíngue baseadas no sistema D4';

-- Migração concluída
SELECT 'Migração DNC do sistema D4 concluída com sucesso!' as status;
