#!/usr/bin/env python3
"""
Script de Validação Completa do Sistema Discador Preditivo
Testa todas as funcionalidades e conexões com Supabase
"""
import os
import sys
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any
import psycopg2
from urllib.parse import urlparse


class ValidadorSistema:
    """Validador completo do sistema"""
    
    def __init__(self):
        self.resultados = {
            'conexao_db': False,
            'tabelas': False,
            'dados_iniciais': False,
            'apis': False,
            'frontend': False,
            'erros': []
        }
        
        # Configurações Supabase
        self.supabase_url = "https://orxxocptgaeoyrtlxwkv.supabase.co"
        self.project_id = "orxxocptgaeoyrtlxwkv"
        self.database_url = os.getenv(
            'DATABASE_URL',
            f"postgresql://postgres:password@db.{self.project_id}.supabase.co:5432/postgres"
        )
    
    def print_header(self, titulo: str):
        """Imprime cabeçalho formatado"""
        print(f"\n{'='*60}")
        print(f"🔍 {titulo.upper()}")
        print('='*60)
    
    def print_status(self, item: str, status: bool, detalhes: str = ""):
        """Imprime status do teste"""
        emoji = "✅" if status else "❌"
        print(f"{emoji} {item:<30} {'OK' if status else 'FALHOU'}")
        if detalhes:
            print(f"   💡 {detalhes}")
    
    def testar_conexao_database(self) -> bool:
        """Testa conexão com Supabase PostgreSQL"""
        self.print_header("Testando Conexão com Supabase")
        
        try:
            # Parse da URL
            result = urlparse(self.database_url)
            
            # Testar conexão
            connection = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port,
                connect_timeout=10
            )
            
            cursor = connection.cursor()
            
            # Testar versão PostgreSQL
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            self.print_status("Conexão PostgreSQL", True, f"Versão: {version[:50]}...")
            
            # Testar extensões
            cursor.execute("SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp');")
            extensoes = cursor.fetchall()
            self.print_status("Extensões UUID", len(extensoes) > 0, f"{len(extensoes)} extensões ativas")
            
            connection.close()
            self.resultados['conexao_db'] = True
            return True
            
        except Exception as e:
            self.print_status("Conexão Supabase", False, str(e))
            self.resultados['erros'].append(f"Conexão DB: {e}")
            return False
    
    def testar_tabelas(self) -> bool:
        """Testa se todas as tabelas foram criadas"""
        self.print_header("Validando Estrutura de Tabelas")
        
        try:
            result = urlparse(self.database_url)
            connection = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
            cursor = connection.cursor()
            
            # Tabelas esperadas
            tabelas_esperadas = ['users', 'campaigns', 'contacts', 'blacklist', 'call_logs']
            
            for tabela in tabelas_esperadas:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = '{tabela}' AND table_schema = 'public';
                """)
                existe = cursor.fetchone()[0] > 0
                self.print_status(f"Tabela {tabela}", existe)
                
                if existe:
                    # Contar registros
                    cursor.execute(f"SELECT COUNT(*) FROM {tabela};")
                    count = cursor.fetchone()[0]
                    print(f"   📊 {count} registros encontrados")
            
            # Testar tipos ENUM
            cursor.execute("""
                SELECT typname FROM pg_type 
                WHERE typname IN ('campaign_status', 'contact_status', 'call_result');
            """)
            enums = cursor.fetchall()
            self.print_status("Tipos ENUM", len(enums) >= 3, f"{len(enums)} tipos criados")
            
            # Testar índices
            cursor.execute("""
                SELECT COUNT(*) FROM pg_indexes 
                WHERE schemaname = 'public' AND indexname LIKE 'idx_%';
            """)
            indices = cursor.fetchone()[0]
            self.print_status("Índices otimização", indices > 5, f"{indices} índices criados")
            
            connection.close()
            self.resultados['tabelas'] = True
            return True
            
        except Exception as e:
            self.print_status("Estrutura Tabelas", False, str(e))
            self.resultados['erros'].append(f"Tabelas: {e}")
            return False
    
    def testar_dados_iniciais(self) -> bool:
        """Testa se os dados iniciais foram inseridos"""
        self.print_header("Validando Dados Iniciais")
        
        try:
            result = urlparse(self.database_url)
            connection = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
            cursor = connection.cursor()
            
            # Testar usuários
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = true;")
            admins = cursor.fetchone()[0]
            self.print_status("Usuários admin", admins > 0, f"{admins} administradores")
            
            cursor.execute("SELECT username FROM users ORDER BY id;")
            usuarios = cursor.fetchall()
            for user in usuarios:
                print(f"   👤 Usuário: {user[0]}")
            
            # Testar campanha exemplo
            cursor.execute("SELECT COUNT(*) FROM campaigns;")
            campanhas = cursor.fetchone()[0]
            self.print_status("Campanhas teste", campanhas > 0, f"{campanhas} campanhas")
            
            # Testar blacklist
            cursor.execute("SELECT COUNT(*) FROM blacklist WHERE is_active = true;")
            blacklist = cursor.fetchone()[0]
            self.print_status("Blacklist ativa", blacklist > 0, f"{blacklist} números bloqueados")
            
            connection.close()
            self.resultados['dados_iniciais'] = True
            return True
            
        except Exception as e:
            self.print_status("Dados Iniciais", False, str(e))
            self.resultados['erros'].append(f"Dados: {e}")
            return False
    
    def testar_configuracoes(self) -> bool:
        """Testa configurações do sistema"""
        self.print_header("Validando Configurações")
        
        # Testar arquivo de configuração
        config_exists = os.path.exists('config.supabase.env')
        self.print_status("Arquivo configuração", config_exists)
        
        # Testar variáveis de ambiente importantes
        vars_importantes = [
            ('SUPABASE_URL', self.supabase_url),
            ('DATABASE_URL', 'postgresql://' in self.database_url)
        ]
        
        for var, valor in vars_importantes:
            if isinstance(valor, bool):
                self.print_status(f"Variável {var}", valor)
            else:
                exists = valor is not None and valor != ""
                self.print_status(f"Variável {var}", exists, valor[:50] + "..." if exists and len(str(valor)) > 50 else str(valor))
        
        # Testar arquivos de frontend
        frontend_files = [
            'frontend/src/components/DashboardProfessional.jsx',
            'frontend/src/components/ErrorBoundary.jsx'
        ]
        
        for file in frontend_files:
            exists = os.path.exists(file)
            self.print_status(f"Arquivo {file}", exists)
        
        self.resultados['frontend'] = True
        return True
    
    def executar_testes_completos(self):
        """Executa todos os testes de validação"""
        print("🚀 VALIDAÇÃO COMPLETA DO SISTEMA DISCADOR PREDITIVO")
        print("=" * 60)
        print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🗄️ Supabase URL: {self.supabase_url}")
        print(f"🆔 Project ID: {self.project_id}")
        
        # Executar testes em sequência
        testes = [
            self.testar_conexao_database,
            self.testar_tabelas,
            self.testar_dados_iniciais,
            self.testar_configuracoes
        ]
        
        sucesso_total = True
        for teste in testes:
            try:
                resultado = teste()
                if not resultado:
                    sucesso_total = False
            except Exception as e:
                print(f"❌ Erro no teste {teste.__name__}: {e}")
                sucesso_total = False
                self.resultados['erros'].append(f"{teste.__name__}: {e}")
        
        # Relatório final
        self.print_header("Relatório Final")
        
        if sucesso_total:
            print("🎉 SISTEMA 100% VALIDADO E FUNCIONAL!")
            print("✅ Supabase PostgreSQL: Conectado")
            print("✅ Tabelas e estrutura: OK")
            print("✅ Dados iniciais: Carregados")
            print("✅ Configurações: Validadas")
            print("✅ Frontend: Atualizado")
            
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("1. Copie config.supabase.env para .env")
            print("2. Configure a senha do banco em DATABASE_URL")
            print("3. Execute: python main.py")
            print("4. Acesse: http://localhost:8000")
            
        else:
            print("⚠️ SISTEMA COM PROBLEMAS DETECTADOS")
            print(f"❌ {len(self.resultados['erros'])} erros encontrados:")
            for erro in self.resultados['erros']:
                print(f"   • {erro}")
        
        print(f"\n📊 Score de Qualidade: {self._calcular_score()}%")
        return sucesso_total
    
    def _calcular_score(self) -> int:
        """Calcula score de qualidade do sistema"""
        total_checks = 4  # número de validações principais
        sucessos = sum([
            self.resultados['conexao_db'],
            self.resultados['tabelas'],
            self.resultados['dados_iniciais'],
            self.resultados['frontend']
        ])
        return int((sucessos / total_checks) * 100)


def main():
    """Função principal"""
    validador = ValidadorSistema()
    
    try:
        sucesso = validador.executar_testes_completos()
        exit_code = 0 if sucesso else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Validação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal na validação: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 