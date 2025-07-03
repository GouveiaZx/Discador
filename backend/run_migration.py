#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def run_migration():
    """Executar migração para configuração avançada"""
    
    # Ler o arquivo de migração compatível com SQLite
    migration_file = 'migrations/create_configuracao_discagem_sqlite.sql'
    
    if not os.path.exists(migration_file):
        print(f"❌ Arquivo de migração não encontrado: {migration_file}")
        return False
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Conectar ao banco de dados
    db_path = 'discador.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Executar as migrações
        cursor.executescript(sql_content)
        conn.commit()
        print('✅ Migração executada com sucesso!')
        print('Tabelas criadas/atualizadas:')
        print('- configuracao_discagem')
        print('- trunk (expandida)')
        print('- trunk_status_historico')
        print('- trunk_estatisticas')
        
        # Verificar se as tabelas foram criadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('configuracao_discagem', 'trunk', 'trunk_status_historico', 'trunk_estatisticas')")
        tables = cursor.fetchall()
        print(f'Tabelas encontradas: {[t[0] for t in tables]}')
        
        # Inserir configuração padrão
        cursor.execute("""
            INSERT OR IGNORE INTO configuracao_discagem 
            (nome, descricao, cps, sleep_time, wait_time, amd_enabled, timezone, horario_inicio, horario_fim, eh_padrao, ativo)
            VALUES 
            ('Configuração Padrão', 'Configuração padrão do sistema', 5.0, 1.0, 30.0, 1, 'America/Sao_Paulo', '08:00', '18:00', 1, 1)
        """)
        
        # Inserir trunk padrão se não existir
        cursor.execute("""
            INSERT OR IGNORE INTO trunk 
            (nome, descricao, host, porta, usuario, senha, codigo_dv, caller_ids, balanceamento, failover_enabled, 
             protocolo, capacidade_maxima, prioridade, status, ativo)
            VALUES 
            ('Trunk Principal', 'Trunk SIP principal do sistema', 'sip.provedor.com', 5060, 'usuario', 'senha', '10-digit', 
             '["5511999888777", "5511888777666"]', 'round_robin', 1, 'UDP', 100, 1, 'unknown', 1)
        """)
        
        # Inserir configuração avançada
        cursor.execute("""
            INSERT OR IGNORE INTO configuracao_discagem 
            (nome, descricao, cps, sleep_time, wait_time, amd_enabled, timezone, horario_inicio, horario_fim, max_tentativas, ativo)
            VALUES 
            ('Configuração Avançada', 'Configuração para campanhas de alto volume', 10.0, 0.5, 45.0, 1, 'America/Sao_Paulo', '09:00', '17:00', 5, 1)
        """)
        
        conn.commit()
        print('✅ Dados padrão inseridos!')
        
        return True
        
    except Exception as e:
        print(f'❌ Erro na migração: {e}')
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n🎉 Migração concluída com sucesso!")
        print("Sistema pronto para configurações avançadas de discagem!")
    else:
        print("\n💥 Falha na migração!") 