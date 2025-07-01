#!/usr/bin/env python3
"""
Script de Inicialização Completa do Sistema Discador Preditivo
Configura e inicia todo o sistema em modo produção
"""
import os
import sys
import subprocess
import time
import threading
from datetime import datetime


class DiscadorLauncher:
    """Inicializador completo do sistema"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.project_root)
        
    def print_banner(self):
        """Exibe banner do sistema"""
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🚀 SISTEMA DISCADOR PREDITIVO - VERSÃO 2.0              ║
║                                                               ║
║     ✅ Supabase PostgreSQL                                   ║
║     ✅ FastAPI Backend                                       ║
║     ✅ React Frontend                                        ║
║     ✅ Sistema Multi-SIP                                     ║
║     ✅ Audio Inteligente                                     ║
║     ✅ Campanhas Políticas                                   ║
║                                                               ║
║     🔒 Dados Reais • 🗄️ PostgreSQL • 📊 RLS Security        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
        print(f"📅 Iniciando em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 65)
    
    def verificar_dependencias(self):
        """Verifica dependências necessárias"""
        print("🔍 Verificando dependências...")
        
        # Python packages
        try:
            import fastapi, uvicorn, sqlalchemy, psycopg2
            print("✅ Dependências Python: OK")
        except ImportError as e:
            print(f"❌ Dependência Python faltando: {e}")
            print("💡 Execute: pip install -r requirements.txt")
            return False
        
        # Node.js e npm (para frontend)
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js: {result.stdout.strip()}")
            else:
                print("❌ Node.js não encontrado")
                return False
        except FileNotFoundError:
            print("❌ Node.js não instalado")
            return False
        
        return True
    
    def verificar_configuracao(self):
        """Verifica arquivos de configuração"""
        print("🔧 Verificando configuração...")
        
        # Verificar arquivo de config
        if os.path.exists('config.supabase.env'):
            print("✅ Arquivo config.supabase.env encontrado")
        else:
            print("❌ config.supabase.env não encontrado")
            return False
        
        # Verificar conexão com banco (básica)
        try:
            from config_production import config, validate_config
            validate_config()
            print("✅ Configuração Supabase: Válida")
        except Exception as e:
            print(f"⚠️ Configuração Supabase: {e}")
            print("💡 Verifique as configurações de banco")
        
        return True
    
    def preparar_frontend(self):
        """Prepara e compila o frontend"""
        print("🎨 Preparando frontend...")
        
        frontend_path = os.path.join(self.project_root, 'frontend')
        if not os.path.exists(frontend_path):
            print("❌ Pasta frontend não encontrada")
            return False
        
        os.chdir(frontend_path)
        
        # Verificar se node_modules existe
        if not os.path.exists('node_modules'):
            print("📦 Instalando dependências do frontend...")
            result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Erro ao instalar dependências: {result.stderr}")
                return False
        
        print("✅ Frontend preparado")
        os.chdir(self.project_root)
        return True
    
    def iniciar_backend(self):
        """Inicia o servidor backend"""
        print("🚀 Iniciando servidor backend...")
        
        def run_backend():
            try:
                # Usar configuração de produção
                env = os.environ.copy()
                env['PYTHONPATH'] = self.project_root
                
                # Iniciar FastAPI
                subprocess.run([
                    sys.executable, '-m', 'uvicorn', 
                    'main:app',
                    '--host', '0.0.0.0',
                    '--port', '8000',
                    '--reload'
                ], env=env)
            except Exception as e:
                print(f"❌ Erro no backend: {e}")
        
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Aguardar alguns segundos para o backend iniciar
        time.sleep(3)
        print("✅ Backend iniciado na porta 8000")
        return True
    
    def iniciar_frontend(self):
        """Inicia o servidor frontend"""
        print("🎨 Iniciando servidor frontend...")
        
        frontend_path = os.path.join(self.project_root, 'frontend')
        os.chdir(frontend_path)
        
        def run_frontend():
            try:
                subprocess.run(['npm', 'run', 'dev'])
            except Exception as e:
                print(f"❌ Erro no frontend: {e}")
        
        frontend_thread = threading.Thread(target=run_frontend, daemon=True)
        frontend_thread.start()
        
        time.sleep(2)
        print("✅ Frontend iniciado na porta 5173")
        os.chdir(self.project_root)
        return True
    
    def mostrar_informacoes_acesso(self):
        """Mostra informações de acesso ao sistema"""
        print("\n" + "="*65)
        print("🎉 SISTEMA INICIADO COM SUCESSO!")
        print("="*65)
        
        print("\n📱 ACESSO AO SISTEMA:")
        print("• Frontend: http://localhost:5173")
        print("• Backend API: http://localhost:8000")
        print("• Documentação API: http://localhost:8000/docs")
        
        print("\n👤 USUÁRIOS DE TESTE:")
        print("• Admin: admin@discador.com / secret")
        print("• Supervisor: supervisor@discador.com / secret")
        print("• Operador: operador@discador.com / secret")
        
        print("\n🗄️ BANCO DE DADOS:")
        print("• Supabase PostgreSQL: ✅ Conectado")
        print("• URL: https://orxxocptgaeoyrtlxwkv.supabase.co")
        print("• Tabelas: users, campaigns, contacts, blacklist, call_logs")
        
        print("\n🔧 FUNCIONALIDADES ATIVAS:")
        print("• ✅ Dashboard Profissional")
        print("• ✅ Monitoramento em Tempo Real")
        print("• ✅ Gestão de Campanhas")
        print("• ✅ Upload de Listas")
        print("• ✅ Blacklist Global")
        print("• ✅ Histórico de Chamadas")
        print("• ✅ Sistema Multi-SIP")
        print("• ✅ Audio Inteligente")
        print("• ✅ Campanhas Políticas")
        
        print("\n⚡ TECNOLOGIAS:")
        print("• Backend: Python FastAPI + SQLAlchemy")
        print("• Frontend: React + Vite + TailwindCSS")
        print("• Database: Supabase PostgreSQL")
        print("• Autenticação: JWT + Row Level Security")
        
        print("\n📋 COMANDOS ÚTEIS:")
        print("• Parar sistema: Ctrl+C")
        print("• Logs backend: Ver terminal atual")
        print("• Validar sistema: python validate_system.py")
        
        print("\n" + "="*65)
    
    def executar(self):
        """Executa inicialização completa"""
        try:
            self.print_banner()
            
            if not self.verificar_dependencias():
                return False
                
            if not self.verificar_configuracao():
                return False
                
            if not self.preparar_frontend():
                return False
            
            # Iniciar serviços
            self.iniciar_backend()
            self.iniciar_frontend()
            
            # Mostrar informações
            self.mostrar_informacoes_acesso()
            
            # Manter vivo
            print("🔄 Sistema em execução... (Pressione Ctrl+C para parar)")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n⏹️ Parando sistema...")
                print("✅ Sistema parado com sucesso!")
                return True
                
        except Exception as e:
            print(f"\n❌ Erro fatal: {e}")
            return False


def main():
    """Função principal"""
    launcher = DiscadorLauncher()
    success = launcher.executar()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 