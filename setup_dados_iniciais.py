#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar dados iniciais do Sistema Discador Preditivo no Supabase
"""

# Comandos SQL para popular dados iniciais
SQL_INITIAL_DATA = """
-- INSERIR ROLES INICIAIS
INSERT INTO roles (name, description, permissions, created_at) VALUES
('admin', 'Administrador do sistema', 'all', NOW()),
('supervisor', 'Supervisor de campanhas', 'campaigns,monitoring,lists', NOW()),
('operator', 'Operador básico', 'monitoring', NOW())
ON CONFLICT (name) DO NOTHING;

-- INSERIR TRUNKS INICIAIS  
INSERT INTO trunks (name, provider, host, port, username, password, max_channels, active, created_at) VALUES
('Trunk Principal', 'Provider1', 'sip.provider1.com', 5060, 'trunk_user1', 'trunk_pass1', 30, true, NOW()),
('Trunk Secundário', 'Provider2', 'sip.provider2.com', 5060, 'trunk_user2', 'trunk_pass2', 20, true, NOW())
ON CONFLICT (name) DO NOTHING;

-- INSERIR ÁUDIOS INICIAIS
INSERT INTO audios (name, description, file_path, duration_seconds, active, created_at, campaign_id) VALUES
('Áudio Principal', 'Áudio principal para campanhas', '/audios/principal.wav', 30, true, NOW(), 1),
('Áudio Presione 1', 'Áudio para sistema Presione 1', '/audios/presione1.wav', 15, true, NOW(), 1)
ON CONFLICT (name) DO NOTHING;

-- INSERIR LISTAS DNC INICIAIS
INSERT INTO dnc_lists (name, description, country, active, created_at) VALUES
('DNC Brasil', 'Lista DNC nacional do Brasil', 'BR', true, NOW())
ON CONFLICT (name) DO NOTHING;

-- INSERIR CONTATOS DE TESTE
INSERT INTO contacts (phone_number, name, campaign_id, status, created_at) VALUES
('+5511999887766', 'Contato Teste 1', 1, 'not_started', NOW()),
('+5511888776655', 'Contato Teste 2', 1, 'not_started', NOW()),
('+5511777665544', 'Contato Teste 3', 1, 'not_started', NOW()),
('+5511666554433', 'Contato Teste 4', 1, 'not_started', NOW()),
('+5511555443322', 'Contato Teste 5', 1, 'not_started', NOW())
ON CONFLICT (phone_number, campaign_id) DO NOTHING;

-- ATUALIZAR CAMPANHA EXISTENTE
UPDATE campaigns SET
    description = 'Campanha principal do sistema com configurações completas para discado preditivo',
    start_time = '09:00',
    end_time = '18:00', 
    timezone = 'America/Sao_Paulo',
    max_attempts = 3,
    retry_interval = 300,
    max_concurrent_calls = 10,
    cps = 5,
    sleep_time = 1,
    wait_time = 0.5,
    language = 'pt-BR',
    shuffle_contacts = true,
    allow_multiple_calls_same_number = false,
    max_channels = 10,
    updated_at = NOW()
WHERE id = 1;

-- INSERIR USER_ROLES
INSERT INTO user_roles (user_id, role_id, created_at) VALUES
(1, 1, NOW()), -- admin -> admin role
(2, 2, NOW()), -- supervisor -> supervisor role
(3, 3, NOW())  -- operador -> operator role  
ON CONFLICT (user_id, role_id) DO NOTHING;

-- INSERIR MAIS NÚMEROS NA BLACKLIST
INSERT INTO blacklist (phone_number, reason, added_by, is_active, created_at) VALUES
('+5511000000000', 'Número de teste bloqueado', 'admin', true, NOW()),
('+5511111111111', 'Solicitação do cliente', 'supervisor', true, NOW()),
('+5511222222222', 'Número inválido', 'admin', true, NOW()),
('+5511333333333', 'Reclamação registrada', 'admin', true, NOW()),
('+5511444444444', 'Não deseja receber chamadas', 'supervisor', true, NOW())
ON CONFLICT (phone_number) DO NOTHING;

-- INSERIR NÚMEROS DNC
INSERT INTO dnc_numbers (phone_number, dnc_list_id, added_at, source) VALUES
('+5511000000001', 1, NOW(), 'manual'),
('+5511000000002', 1, NOW(), 'manual'),
('+5511000000003', 1, NOW(), 'import')
ON CONFLICT (phone_number, dnc_list_id) DO NOTHING;
"""

def main():
    """Função principal"""
    print("🎯 CONFIGURAÇÃO DE DADOS INICIAIS - SISTEMA DISCADOR PREDITIVO")
    print("=" * 70)
    print()
    print("📋 Execute os comandos SQL abaixo no Supabase SQL Editor:")
    print("   https://supabase.com/dashboard/project/orxxocptgaeoyrtlxwkv/sql")
    print()
    print("=" * 70)
    print()
    print(SQL_INITIAL_DATA)
    print()
    print("=" * 70)
    print()
    print("✅ APÓS EXECUTAR OS COMANDOS, O SISTEMA TERÁ:")
    print("   📋 3 roles configurados (admin, supervisor, operator)")
    print("   📞 2 trunks SIP de exemplo")
    print("   🔊 2 áudios configurados")
    print("   🚫 1 lista DNC do Brasil")
    print("   👥 5 contatos de teste na campanha")
    print("   ⛔ 5 números na blacklist")
    print("   🔗 Usuários associados a roles")
    print("   📊 Campanha atualizada com configurações completas")
    print("   📵 3 números na lista DNC")
    print()
    print("🚀 Sistema 100% configurado e pronto para uso!")

if __name__ == "__main__":
    main() 