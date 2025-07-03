#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_database():
    """Verificar estrutura do banco de dados"""
    
    conn = sqlite3.connect('discador.db')
    cursor = conn.cursor()

    try:
        # Verificar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print('Tabelas existentes:')
        for table in tables:
            print(f'  - {table[0]}')
        
        # Verificar estrutura da tabela trunk se existir
        if any('trunk' in table for table in tables):
            print('\nEstrutura da tabela trunk:')
            cursor.execute('PRAGMA table_info(trunk)')
            columns = cursor.fetchall()
            for col in columns:
                print(f'  {col[1]} {col[2]} (nullable: {not col[3]})')
        
        # Verificar estrutura da tabela configuracao_discagem se existir
        if any('configuracao_discagem' in table for table in tables):
            print('\nEstrutura da tabela configuracao_discagem:')
            cursor.execute('PRAGMA table_info(configuracao_discagem)')
            columns = cursor.fetchall()
            for col in columns:
                print(f'  {col[1]} {col[2]} (nullable: {not col[3]})')
        
        return True
        
    except Exception as e:
        print(f'Erro ao verificar banco: {e}')
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_database() 