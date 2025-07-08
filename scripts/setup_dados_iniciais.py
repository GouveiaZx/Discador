#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar dados iniciais do Sistema Discador Preditivo no Supabase
"""

import os
import sys
from datetime import datetime

# Simular dados iniciais via SQL direto no Supabase
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
INSERT INTO audios (name, description, file_path, duration_seconds, active, created_at) VALUES
('Áudio Principal', 'Áudio principal para campanhas', '/audios/principal.wav', 30, true, NOW()),
('Áudio Presione 1', 'Áudio para sistema Presione 1', '/audios/presione1.wav', 15, true, NOW())
ON CONFLICT (name) DO NOTHING;

-- INSERIR LISTAS DNC INICIAIS
INSERT INTO dnc_lists (name, description, country, active, created_at) VALUES
('DNC Brasil', 'Lista DNC nacional do Brasil', 'BR', true, NOW())
ON CONFLICT (name) DO NOTHING;

-- INSERIR CONTATOS DE TESTE
INSERT INTO contacts (phone_number, name, campaign_id, status, created_at) VALUES
('+5511999887766', 'Contato Teste 1', 1, 'not_started', NOW()),
('+5511888776655', 'Contato Teste 2', 1, 'not_started', NOW()),
('+5511777665544', 'Contato Teste 3', 1, 'not_started', NOW())
ON CONFLICT (phone_number, campaign_id) DO NOTHING;

-- ATUALIZAR CAMPANHA EXISTENTE COM MAIS DADOS
UPDATE campaigns SET
    description = 'Campanha principal do sistema com configurações completas',
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
    max_channels = 10
WHERE id = 1;

-- INSERIR USER_ROLES PARA ASSOCIAR USUÁRIOS A ROLES
INSERT INTO user_roles (user_id, role_id, created_at) VALUES
(1, 1, NOW()), -- admin -> admin role
(2, 2, NOW()), -- supervisor -> supervisor role  
(3, 3, NOW())  -- operador -> operator role
ON CONFLICT (user_id, role_id) DO NOTHING;

-- INSERIR ALGUNS NÚMEROS NA BLACKLIST DE EXEMPLO
INSERT INTO blacklist (phone_number, reason, added_by, is_active, created_at) VALUES
('+5511000000000', 'Número de teste bloqueado', 'admin', true, NOW()),
('+5511111111111', 'Solicitação do cliente', 'supervisor', true, NOW()),
('+5511222222222', 'Número inválido', 'admin', true, NOW())
ON CONFLICT (phone_number) DO NOTHING;
"""

def print_sql_commands():
    """Imprimir comandos SQL para execução manual no Supabase"""
    print("🎯 COMANDOS SQL PARA CONFIGURAR DADOS INICIAIS")
    print("=" * 60)
    print("Execute os comandos abaixo no SQL Editor do Supabase:")
    print()
    print(SQL_INITIAL_DATA)
    print()
    print("=" * 60)
    print("✅ Após executar, o sistema terá:")
    print("  - 3 roles configurados")
    print("  - 2 trunks SIP de exemplo")
    print("  - 2 áudios configurados")
    print("  - 1 lista DNC")
    print("  - 3 contatos de teste")
    print("  - 3 números na blacklist")
    print("  - Usuários associados a roles")
    print("  - Campanha atualizada com configurações completas")

if __name__ == "__main__":
    print_sql_commands() 