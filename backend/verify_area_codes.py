import sqlite3

def verify_area_codes():
    try:
        conn = sqlite3.connect('backend/database/discador.db')
        cursor = conn.cursor()
        
        # Contar total de registros
        cursor.execute('SELECT COUNT(*) FROM usa_area_codes')
        count = cursor.fetchone()[0]
        print(f'Total de códigos de área inseridos: {count}')
        
        # Mostrar primeiros 10 registros
        cursor.execute('SELECT area_code, state, city FROM usa_area_codes LIMIT 10')
        rows = cursor.fetchall()
        print('\nPrimeiros 10 registros:')
        for row in rows:
            print(f'{row[0]} - {row[1]} - {row[2]}')
        
        # Verificar alguns códigos específicos
        cursor.execute('SELECT area_code, state, city FROM usa_area_codes WHERE area_code IN ("305", "425", "213")')
        specific_codes = cursor.fetchall()
        print('\nCódigos de área específicos (305, 425, 213):')
        for row in specific_codes:
            print(f'{row[0]} - {row[1]} - {row[2]}')
        
        conn.close()
        print('\nVerificação concluída com sucesso!')
        
    except Exception as e:
        print(f'Erro ao verificar dados: {e}')

if __name__ == '__main__':
    verify_area_codes()