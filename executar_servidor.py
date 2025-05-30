#!/usr/bin/env python3
"""
Script para executar o servidor de desenvolvimento do Discador Preditivo
"""
import uvicorn
import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Executa o servidor de desenvolvimento"""
    
    print("🚀 Iniciando servidor do Discador Preditivo...")
    print("📍 URL: http://localhost:8000")
    print("📖 Documentação da API: http://localhost:8000/docs")
    print("🔧 Interface alternativa: http://localhost:8000/redoc")
    print("⏹️  Para parar o servidor, pressione Ctrl+C")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Recarregar automaticamente quando os arquivos mudarem
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar servidor: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 