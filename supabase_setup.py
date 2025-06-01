#!/usr/bin/env python3
"""
Script de configuração completa para Supabase
Migra do SQLite local para Supabase PostgreSQL
"""
import os
import asyncio
from database.models import Base, User, Campaign, Contact, Blacklist, CallLog
from database.connection import engine, SessionLocal, DATABASE_URL
import requests
import json

class SupabaseSetup:
    def __init__(self, project_id=None, api_key=None):
        self.project_id = project_id
        self.api_key = api_key
        self.supabase_url = f"https://{project_id}.supabase.co" if project_id else None
        
    def generate_sql_migrations(self):
        """
        Gera SQL para criar todas as tabelas no Supabase
        """
        
        # SQL para criar as tabelas com todos os campos necessários
        sql_migrations = """
-- ================================
-- DISCADOR PREDITIVO - SUPABASE SETUP
-- ================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tipos ENUM
DO $$ BEGIN
    CREATE TYPE campaign_status AS ENUM ('draft', 'active', 'paused', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE contact_status AS ENUM ('not_started', 'calling', 'answered', 'pressed_1', 'no_answer', 'busy', 'rejected', 'blacklisted', 'error');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE call_result AS ENUM ('success_pressed_1', 'success_transferred', 'no_answer', 'busy', 'rejected', 'hangup', 'error', 'blacklisted');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Tabela de campanhas
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status campaign_status DEFAULT 'draft',
    cli_number VARCHAR(20) NOT NULL,
    audio_url VARCHAR(255),
    audio_file_path VARCHAR(255),
    start_time VARCHAR(5) DEFAULT '09:00',
    end_time VARCHAR(5) DEFAULT '18:00',
    timezone VARCHAR(50) DEFAULT 'America/Argentina/Buenos_Aires',
    max_attempts INTEGER DEFAULT 3,
    retry_interval INTEGER DEFAULT 30,
    max_concurrent_calls INTEGER DEFAULT 5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    owner_id INTEGER REFERENCES users(id)
);

-- Índices para campaigns
CREATE INDEX IF NOT EXISTS idx_campaigns_name ON campaigns(name);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_owner_id ON campaigns(owner_id);

-- Tabela de contatos
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    status contact_status DEFAULT 'not_started',
    attempts INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    extra_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE
);

-- Índices para contacts
CREATE INDEX IF NOT EXISTS idx_contacts_phone_number ON contacts(phone_number);
CREATE INDEX IF NOT EXISTS idx_contacts_campaign_id ON contacts(campaign_id);
CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);

-- Tabela de blacklist
CREATE TABLE IF NOT EXISTS blacklist (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    reason VARCHAR(255),
    added_by VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para blacklist
CREATE INDEX IF NOT EXISTS idx_blacklist_phone_number ON blacklist(phone_number);
CREATE INDEX IF NOT EXISTS idx_blacklist_is_active ON blacklist(is_active);

-- Tabela de call_logs
CREATE TABLE IF NOT EXISTS call_logs (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(50) UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    cli_number VARCHAR(20) NOT NULL,
    initiated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    answered_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    result call_result,
    dtmf_pressed VARCHAR(10),
    duration_seconds INTEGER DEFAULT 0,
    asterisk_channel VARCHAR(100),
    transfer_number VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    campaign_id INTEGER REFERENCES campaigns(id),
    contact_id INTEGER REFERENCES contacts(id)
);

-- Índices para call_logs
CREATE INDEX IF NOT EXISTS idx_call_logs_call_id ON call_logs(call_id);
CREATE INDEX IF NOT EXISTS idx_call_logs_phone_number ON call_logs(phone_number);
CREATE INDEX IF NOT EXISTS idx_call_logs_campaign_id ON call_logs(campaign_id);
CREATE INDEX IF NOT EXISTS idx_call_logs_contact_id ON call_logs(contact_id);
CREATE INDEX IF NOT EXISTS idx_call_logs_initiated_at ON call_logs(initiated_at);

-- Triggers para updated_at automático
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_blacklist_updated_at BEFORE UPDATE ON blacklist FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Dados iniciais para teste
INSERT INTO users (username, email, is_admin, hashed_password) 
VALUES 
    ('admin', 'admin@discador.com', true, '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'),
    ('supervisor', 'supervisor@discador.com', false, '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'),
    ('operador', 'operador@discador.com', false, '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW')
ON CONFLICT (username) DO NOTHING;

-- Campaign de exemplo
INSERT INTO campaigns (name, description, cli_number, status, owner_id)
VALUES 
    ('Campanha Teste', 'Campanha de teste para demonstração', '+5411123456789', 'draft', 1)
ON CONFLICT DO NOTHING;

-- Blacklist de exemplo
INSERT INTO blacklist (phone_number, reason, added_by)
VALUES 
    ('+5411999999999', 'Número de teste bloqueado', 'admin'),
    ('+5411888888888', 'Solicitação do cliente', 'supervisor')
ON CONFLICT (phone_number) DO NOTHING;

-- ================================
-- POLÍTICAS RLS (Row Level Security)
-- ================================

-- Habilitar RLS nas tabelas principais
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_logs ENABLE ROW LEVEL SECURITY;

-- Políticas para usuários autenticados
CREATE POLICY "Usuários podem ver próprios dados" ON users FOR ALL USING (auth.uid()::text = id::text);
CREATE POLICY "Admins podem ver tudo" ON users FOR ALL USING (
    EXISTS (
        SELECT 1 FROM users 
        WHERE id::text = auth.uid()::text AND is_admin = true
    )
);

-- Políticas para campanhas (todos podem ver, apenas proprietários/admins podem modificar)
CREATE POLICY "Todos podem ver campanhas" ON campaigns FOR SELECT USING (true);
CREATE POLICY "Proprietários podem modificar campanhas" ON campaigns FOR ALL USING (
    owner_id::text = auth.uid()::text OR 
    EXISTS (
        SELECT 1 FROM users 
        WHERE id::text = auth.uid()::text AND is_admin = true
    )
);

-- Views para relatórios
CREATE OR REPLACE VIEW campaign_stats AS
SELECT 
    c.id,
    c.name,
    c.status,
    COUNT(ct.id) as total_contacts,
    COUNT(CASE WHEN ct.status = 'pressed_1' THEN 1 END) as successful_contacts,
    COUNT(cl.id) as total_calls,
    ROUND(
        CASE 
            WHEN COUNT(ct.id) > 0 
            THEN (COUNT(CASE WHEN ct.status = 'pressed_1' THEN 1 END) * 100.0 / COUNT(ct.id))
            ELSE 0 
        END, 2
    ) as success_rate
FROM campaigns c
LEFT JOIN contacts ct ON c.id = ct.campaign_id
LEFT JOIN call_logs cl ON c.id = cl.campaign_id
GROUP BY c.id, c.name, c.status;

COMMENT ON TABLE users IS 'Usuários do sistema de discador preditivo';
COMMENT ON TABLE campaigns IS 'Campanhas de discagem com configurações';
COMMENT ON TABLE contacts IS 'Lista de contatos para cada campanha';
COMMENT ON TABLE blacklist IS 'Números bloqueados globalmente';
COMMENT ON TABLE call_logs IS 'Logs detalhados de todas as chamadas realizadas';

-- ================================
-- FINALIZAÇÃO
-- ================================
SELECT 'Supabase configurado com sucesso! 🎉' as status;
"""
        
        return sql_migrations
    
    def save_migration_file(self):
        """
        Salva a migração SQL em arquivo
        """
        sql = self.generate_sql_migrations()
        
        with open("supabase_migration.sql", "w", encoding="utf-8") as f:
            f.write(sql)
        
        print("✅ Arquivo 'supabase_migration.sql' criado com sucesso!")
        return "supabase_migration.sql"
    
    def generate_env_config(self, project_url, anon_key, service_role_key=None):
        """
        Gera configuração de ambiente para Supabase
        """
        env_config = f"""
# ================================
# CONFIGURAÇÃO SUPABASE
# ================================

# URLs
SUPABASE_URL={project_url}
SUPABASE_ANON_KEY={anon_key}
"""
        
        if service_role_key:
            env_config += f"SUPABASE_SERVICE_ROLE_KEY={service_role_key}\n"
            
        env_config += f"""
# Database URL para SQLAlchemy (PostgreSQL)
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres

# Configurações do FastAPI
DEBUG=true
HOST=0.0.0.0
PUERTO=8000
SECRET_KEY=sua_chave_secreta_super_segura_aqui_123456789

# ================================
# CONFIGURAÇÃO FRONTEND
# ================================
REACT_APP_SUPABASE_URL={project_url}
REACT_APP_SUPABASE_ANON_KEY={anon_key}
REACT_APP_API_URL=https://web-production-c192b.up.railway.app
"""
        
        with open("config.supabase.env", "w", encoding="utf-8") as f:
            f.write(env_config)
            
        print("✅ Arquivo 'config.supabase.env' criado!")
        return env_config

if __name__ == "__main__":
    setup = SupabaseSetup()
    
    print("🚀 INICIANDO CONFIGURAÇÃO DO SUPABASE")
    print("=" * 50)
    
    # Gerar SQL de migração
    migration_file = setup.save_migration_file()
    print(f"📁 Migração SQL salva em: {migration_file}")
    
    print("\n✅ PRÓXIMOS PASSOS:")
    print("1. Configure seu projeto Supabase")
    print("2. Execute o SQL no editor do Supabase")
    print("3. Configure as variáveis de ambiente")
    print("4. Reinicie o backend com o novo DATABASE_URL")
    
    print("\n🔧 COMANDOS ÚTEIS:")
    print("- Ver projetos: list_projects")
    print("- Executar migração: apply_migration")
    print("- Testar conexão: python test_supabase.py") 