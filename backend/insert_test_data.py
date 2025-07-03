#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from datetime import datetime

def insert_test_data():
    """Inserir dados de teste nas tabelas avançadas"""
    
    conn = sqlite3.connect('discador.db')
    cursor = conn.cursor()

    try:
        # Inserir configuração padrão
        cursor.execute("""
            INSERT OR REPLACE INTO configuracao_discagem 
            (id, nome, descripcion, cps_maximo, cps_inicial, sleep_time_entre_llamadas, 
             wait_time_respuesta, max_intentos_por_numero, amd_habilitado, 
             horario_inicio, horario_fin, activa, es_default)
            VALUES 
            (1, 'Configuração Padrão', 'Configuração conservadora para campanhas pequenas', 
             5.0, 2.0, 1.0, 30.0, 3, 1, '08:00', '18:00', 1, 1)
        """)
        
        # Inserir configuração avançada
        cursor.execute("""
            INSERT OR REPLACE INTO configuracao_discagem 
            (id, nome, descripcion, cps_maximo, cps_inicial, sleep_time_entre_llamadas, 
             wait_time_respuesta, max_intentos_por_numero, amd_habilitado, 
             horario_inicio, horario_fin, activa, es_default)
            VALUES 
            (2, 'Configuração Agressiva', 'Configuração para campanhas de alto volume', 
             15.0, 10.0, 0.5, 45.0, 5, 1, '09:00', '17:00', 1, 0)
        """)
        
        # Inserir trunk principal
        caller_ids_json = json.dumps(["+5511999888777", "+5511888777666", "+5511777666555"])
        cursor.execute("""
            INSERT OR REPLACE INTO trunk 
            (id, nome, descricao, host, porta, usuario, senha, codigo_dv, caller_ids, 
             balanceamento, failover_enabled, protocolo, capacidade_maxima, prioridade, 
             status, ativo)
            VALUES 
            (1, 'Trunk Principal', 'Trunk SIP principal para discagem', 'sip.provedor1.com', 
             5060, 'user001', 'pass123', '10-digit', ?, 'round_robin', 1, 'UDP', 100, 1, 
             'online', 1)
        """, (caller_ids_json,))
        
        # Inserir trunk secundário
        caller_ids_json2 = json.dumps(["+5511555444333", "+5511444333222"])
        cursor.execute("""
            INSERT OR REPLACE INTO trunk 
            (id, nome, descricao, host, porta, usuario, senha, codigo_dv, caller_ids, 
             balanceamento, failover_enabled, protocolo, capacidade_maxima, prioridade, 
             status, ativo)
            VALUES 
            (2, 'Trunk Secundário', 'Trunk SIP de backup', 'sip.provedor2.com', 
             5060, 'user002', 'pass456', '11-digit', ?, 'least_used', 1, 'TCP', 50, 2, 
             'online', 1)
        """, (caller_ids_json2,))
        
        # Inserir trunk para EUA
        caller_ids_usa = json.dumps(["+17865551234", "+13055557890", "+14155559876"])
        cursor.execute("""
            INSERT OR REPLACE INTO trunk 
            (id, nome, descricao, host, porta, usuario, senha, codigo_dv, caller_ids, 
             balanceamento, failover_enabled, protocolo, capacidade_maxima, prioridade, 
             status, ativo)
            VALUES 
            (3, 'Trunk USA', 'Trunk especializado para mercado americano', 'sip.usprovider.com', 
             5060, 'usauser', 'usapass', 'E164', ?, 'priority', 1, 'TLS', 200, 1, 
             'online', 1)
        """, (caller_ids_usa,))
        
        # Inserir histórico de status
        cursor.execute("""
            INSERT OR REPLACE INTO trunk_status_historico 
            (trunk_id, status_anterior, status_novo, chamadas_ativas, motivo)
            VALUES 
            (1, 'unknown', 'online', 0, 'Sistema inicializado'),
            (2, 'unknown', 'online', 0, 'Sistema inicializado'),
            (3, 'unknown', 'online', 0, 'Sistema inicializado')
        """)
        
        # Inserir estatísticas iniciais
        data_hoje = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT OR REPLACE INTO trunk_estatisticas 
            (trunk_id, data_inicio, data_fim, total_chamadas, chamadas_completadas, 
             chamadas_falhadas, latencia_media, uptime_porcentagem)
            VALUES 
            (1, ?, ?, 150, 120, 30, 85.5, 99.2),
            (2, ?, ?, 75, 60, 15, 92.1, 98.8),
            (3, ?, ?, 200, 180, 20, 78.3, 99.5)
        """, (data_hoje, data_hoje, data_hoje, data_hoje, data_hoje, data_hoje))
        
        conn.commit()
        print('✅ Dados de teste inseridos com sucesso!')
        
        # Verificar dados inseridos
        cursor.execute("SELECT COUNT(*) FROM configuracao_discagem")
        config_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trunk")
        trunk_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trunk_status_historico")
        history_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trunk_estatisticas")
        stats_count = cursor.fetchone()[0]
        
        print(f'Registros inseridos:')
        print(f'  - Configurações de discagem: {config_count}')
        print(f'  - Trunks: {trunk_count}')
        print(f'  - Histórico de status: {history_count}')
        print(f'  - Estatísticas: {stats_count}')
        
        return True
        
    except Exception as e:
        print(f'❌ Erro ao inserir dados: {e}')
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = insert_test_data()
    if success:
        print("\n🎉 Dados de teste inseridos com sucesso!")
        print("Sistema pronto para testes avançados!")
    else:
        print("\n💥 Falha ao inserir dados de teste!") 