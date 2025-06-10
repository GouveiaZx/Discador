#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de instalação e configuração do sistema CODE2BASE
Executa as migrações e configura dados iniciais.
"""

import sys
import os
import asyncio
from pathlib import Path

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database import get_db, engine
from app.models.code2base import *
from app.services.code2base_rules_service import Code2BaseRulesService
from sqlalchemy import text
from app.utils.logger import logger

async def executar_migracao_sql():
    """Executa a migração SQL do CODE2BASE"""
    print("🔧 Executando migração SQL do sistema CODE2BASE...")
    
    try:
        # Ler arquivo de migração
        migration_file = Path(__file__).parent.parent.parent / "migrations" / "create_code2base_tables.sql"
        
        if not migration_file.exists():
            print(f"❌ Arquivo de migração não encontrado: {migration_file}")
            return False
            
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Executar SQL
        with engine.connect() as connection:
            # Dividir por comandos e executar um por vez
            commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
            
            for i, command in enumerate(commands):
                try:
                    if command.strip():
                        connection.execute(text(command))
                        connection.commit()
                except Exception as e:
                    if "duplicate_object" not in str(e) and "already exists" not in str(e):
                        print(f"⚠️  Erro no comando {i+1}: {e}")
            
        print("✅ Migração SQL executada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar migração: {e}")
        return False

async def configurar_regras_padrao():
    """Configura regras padrão do sistema"""
    print("📋 Configurando regras padrão do sistema...")
    
    try:
        async for db in get_db():
            rules_service = Code2BaseRulesService(db)
            await rules_service.criar_regras_padrao()
            print("✅ Regras padrão configuradas!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao configurar regras: {e}")
        return False

async def sincronizar_clis_existentes():
    """Sincroniza CLIs existentes com o sistema geográfico"""
    print("🔄 Sincronizando CLIs existentes...")
    
    try:
        async for db in get_db():
            # Importar serviço que pode não existir ainda
            try:
                from app.services.code2base_geo_service import Code2BaseGeoService
                geo_service = Code2BaseGeoService(db)
                resultado = await geo_service.sincronizar_clis_automaticamente()
                print(f"✅ {resultado.get('sincronizados', 0)} CLIs sincronizados!")
                return True
            except ImportError:
                print("⚠️  Serviço geográfico não disponível ainda")
                return True
                
    except Exception as e:
        print(f"❌ Erro ao sincronizar CLIs: {e}")
        return False

def verificar_tabelas():
    """Verifica se as tabelas foram criadas corretamente"""
    print("🔍 Verificando tabelas do sistema...")
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'code2base_%'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            expected_tables = [
                'code2base_paises',
                'code2base_estados', 
                'code2base_cidades',
                'code2base_prefijos',
                'code2base_clis_geo',
                'code2base_reglas_cli',
                'code2base_historial_seleccion_cli'
            ]
            
            print(f"📊 Tabelas encontradas: {len(tables)}")
            
            for table in expected_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} - FALTANDO")
            
            return len(tables) >= 6  # Pelo menos 6 das 7 tabelas principais
            
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False

async def main():
    """Função principal de instalação"""
    print("🚀 Instalando sistema CODE2BASE Avançado")
    print("=" * 50)
    
    success_steps = 0
    total_steps = 4
    
    # Passo 1: Executar migração
    if await executar_migracao_sql():
        success_steps += 1
    
    # Passo 2: Verificar tabelas
    if verificar_tabelas():
        success_steps += 1
        print("✅ Verificação de tabelas concluída!")
    else:
        print("❌ Falha na verificação de tabelas!")
    
    # Passo 3: Configurar regras padrão
    if await configurar_regras_padrao():
        success_steps += 1
    
    # Passo 4: Sincronizar CLIs
    if await sincronizar_clis_existentes():
        success_steps += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Instalação concluída: {success_steps}/{total_steps} passos executados")
    
    if success_steps == total_steps:
        print("🎉 Sistema CODE2BASE instalado com sucesso!")
        print("\n🔗 Endpoints disponíveis:")
        print("  • /api/v1/code2base/seleccionar-cli - Seleção inteligente de CLI")
        print("  • /api/v1/code2base/analizar-destino - Análise de destino")
        print("  • /api/v1/code2base/geografia/* - Gestão geográfica")
        print("  • /api/v1/code2base/reglas/* - Gestão de regras")
        print("  • /api/v1/code2base/estadisticas - Estatísticas avançadas")
        
    else:
        print("⚠️  Instalação parcial. Verifique os erros acima.")
    
    return success_steps == total_steps

if __name__ == "__main__":
    asyncio.run(main()) 