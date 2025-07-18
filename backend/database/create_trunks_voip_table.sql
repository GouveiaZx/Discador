-- Tabela para armazenar configurações de trunks VoIP
-- Permite criar e gerenciar trunks SIP sem acesso root ao Asterisk

CREATE TABLE IF NOT EXISTS trunks_voip (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE,
    host VARCHAR(255) NOT NULL,
    porta VARCHAR(10) DEFAULT '5060',
    usuario VARCHAR(100),
    senha VARCHAR(255),
    contexto VARCHAR(50) DEFAULT 'from-trunk',
    codec VARCHAR(255) DEFAULT 'ulaw,alaw,g729',
    dtmf_mode VARCHAR(20) DEFAULT 'rfc2833',
    country_code VARCHAR(10),
    dial_prefix VARCHAR(20),
    max_channels VARCHAR(10) DEFAULT '30',
    qualify VARCHAR(20) DEFAULT 'yes',
    nat VARCHAR(100) DEFAULT 'force_rport,comedia',
    insecure VARCHAR(50) DEFAULT 'port,invite',
    type VARCHAR(20) DEFAULT 'peer',
    disallow VARCHAR(100) DEFAULT 'all',
    allow VARCHAR(255) DEFAULT 'ulaw,alaw,g729',
    fromuser VARCHAR(100),
    fromdomain VARCHAR(255),
    register_string VARCHAR(500),
    outbound_proxy VARCHAR(255),
    transport VARCHAR(20) DEFAULT 'udp',
    encryption VARCHAR(20) DEFAULT 'no',
    activo BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_trunks_voip_nome ON trunks_voip(nome);
CREATE INDEX IF NOT EXISTS idx_trunks_voip_activo ON trunks_voip(activo);
CREATE INDEX IF NOT EXISTS idx_trunks_voip_country ON trunks_voip(country_code);

-- Trigger para atualizar timestamp automaticamente
CREATE TRIGGER IF NOT EXISTS update_trunks_voip_timestamp 
    AFTER UPDATE ON trunks_voip
    FOR EACH ROW
BEGIN
    UPDATE trunks_voip SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Inserir alguns trunks de exemplo (opcional)
INSERT OR IGNORE INTO trunks_voip (
    nome, host, porta, usuario, senha, contexto, country_code, dial_prefix,
    max_channels, transport, activo
) VALUES 
(
    'Trunk_Mexico_Principal',
    'sip.proveedormexico.com',
    '5060',
    'usuario_mx',
    'senha_mx',
    'from-trunk',
    '52',
    '9797',
    '50',
    'udp',
    1
),
(
    'Trunk_USA_Canada',
    'sip.proveedorusa.com',
    '5060',
    'usuario_us',
    'senha_us',
    'from-trunk',
    '1',
    '9798',
    '100',
    'udp',
    1
),
(
    'Trunk_Brasil_Backup',
    'sip.proveedorbrasil.com',
    '5060',
    'usuario_br',
    'senha_br',
    'from-trunk',
    '55',
    '979755',
    '30',
    'udp',
    0
);

-- Comentários sobre os campos:
-- nome: Nome único do trunk para identificação
-- host: Endereço IP ou hostname do provedor SIP
-- porta: Porta SIP (geralmente 5060)
-- usuario/senha: Credenciais de autenticação
-- contexto: Contexto Asterisk para chamadas recebidas
-- country_code: Código do país (52=México, 1=USA/Canadá, 55=Brasil)
-- dial_prefix: Prefixo de discagem do provedor (ex: 9797, 979755)
-- max_channels: Máximo de canais simultâneos
-- transport: Protocolo de transporte (udp, tcp, tls)
-- register_string: String de registro SIP (formato: user:pass@host:port)
-- qualify: Verificação de conectividade (yes/no/tempo)
-- nat: Configurações NAT
-- insecure: Configurações de segurança
-- allow/disallow: Codecs permitidos/negados