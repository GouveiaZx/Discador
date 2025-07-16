import sqlite3
import os

# Verificar se o arquivo de banco existe
db_path = 'discador.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar tabelas CLI e usa_area_codes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%cli%' OR name = 'usa_area_codes') ORDER BY name;")
    tables = cursor.fetchall()
    
    print("=== TABELAS CLI/AREA CODES LOCAIS ===")
    if tables:
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"- {table_name}: {count} registros")
    else:
        print("Nenhuma tabela CLI ou usa_area_codes encontrada")
    
    # Verificar se usa_area_codes existe especificamente
    cursor.execute("SELECT COUNT(*) FROM usa_area_codes;")
    area_codes_count = cursor.fetchone()[0]
    print(f"\n=== CÓDIGOS DE ÁREA ===")
    print(f"Total de códigos de área locais: {area_codes_count}")
    
    conn.close()
else:
    print(f"Arquivo de banco {db_path} não encontrado")