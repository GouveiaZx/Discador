#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def run_trunks_migration():
    """Executar migração para tabela de trunks VoIP"""
    
    # Ler o arquivo de migração para trunks VoIP
    migration_file = 'database/create_trunks_voip_table.sql'
    
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
        print('✅ Migração de trunks VoIP executada com sucesso!')
        print('Tabelas criadas/atualizadas:')
        print('- trunks_voip')
        
        # Verificar se a tabela foi criada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trunks_voip'")
        table = cursor.fetchone()
        if table:
            print(f'✅ Tabela encontrada: {table[0]}')
            
            # Verificar estrutura da tabela
            cursor.execute("PRAGMA table_info(trunks_voip)")
            columns = cursor.fetchall()
            print(f"📋 Colunas da tabela ({len(columns)}):")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
        else:
            print('❌ Tabela trunks_voip não foi criada')
            return False
        
        # Verificar se existem dados de exemplo
        cursor.execute("SELECT COUNT(*) FROM trunks_voip")
        count = cursor.fetchone()[0]
        print(f"📊 Registros na tabela: {count}")
        
        if count > 0:
            cursor.execute("SELECT nome, host, country_code, activo FROM trunks_voip")
            trunks = cursor.fetchall()
            print("🔧 Trunks configurados:")
            for trunk in trunks:
                status = "✅ Ativo" if trunk[3] else "❌ Inativo"
                print(f"   - {trunk[0]} ({trunk[1]}) - País: {trunk[2]} - {status}")
        
        return True
        
    except Exception as e:
        print(f'❌ Erro na migração: {e}')
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_trunks_table():
    """Verificar se a tabela de trunks existe e está funcionando"""
    
    db_path = 'discador.db'
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trunks_voip'")
        if not cursor.fetchone():
            print("❌ Tabela trunks_voip não existe")
            return False
        
        # Testar inserção de um trunk de teste
        test_trunk = {
            'nome': 'Teste_Trunk_Temp',
            'host': 'test.example.com',
            'porta': '5060',
            'country_code': '1',
            'dial_prefix': '9999',
            'activo': 1
        }
        
        cursor.execute("""
            INSERT INTO trunks_voip (nome, host, porta, country_code, dial_prefix, activo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            test_trunk['nome'], test_trunk['host'], test_trunk['porta'],
            test_trunk['country_code'], test_trunk['dial_prefix'], test_trunk['activo']
        ))
        
        # Verificar se foi inserido
        cursor.execute("SELECT id FROM trunks_voip WHERE nome = ?", (test_trunk['nome'],))
        test_id = cursor.fetchone()
        
        if test_id:
            print("✅ Teste de inserção bem-sucedido")
            
            # Remover o registro de teste
            cursor.execute("DELETE FROM trunks_voip WHERE id = ?", (test_id[0],))
            print("🧹 Registro de teste removido")
        
        conn.commit()
        print("✅ Tabela trunks_voip está funcionando corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando migração de trunks VoIP...")
    
    success = run_trunks_migration()
    
    if success:
        print("\n🔍 Verificando funcionamento da tabela...")
        verify_success = verify_trunks_table()
        
        if verify_success:
            print("\n🎉 Migração de trunks VoIP concluída com sucesso!")
            print("Sistema pronto para gerenciar trunks VoIP via interface!")
            print("\n📋 Próximos passos:")
            print("1. Reiniciar o backend para carregar as novas rotas")
            print("2. Acessar a interface de gestão de trunks")
            print("3. Configurar seus trunks VoIP")
        else:
            print("\n⚠️ Migração executada, mas verificação falhou")
    else:
        print("\n💥 Falha na migração de trunks VoIP!")