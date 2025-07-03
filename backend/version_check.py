#!/usr/bin/env python3
"""
Arquivo de verificação de versão para debug de deploy.
"""

import sys
import os
from datetime import datetime

VERSION = "1.1.0-fix-imports"
BUILD_DATE = "2025-01-03T16:30:00Z"

def verificar_imports():
    """Verifica se os imports estão funcionando."""
    try:
        # Testar import dos models
        import app.models
        print("✓ app.models importado com sucesso")
        
        # Testar import específico do configuracao_discagem
        try:
            from app.models.configuracao_discagem import ConfiguracaoDiscagem
            print("✓ ConfiguracaoDiscagem importado com sucesso")
        except ImportError:
            print("⚠ ConfiguracaoDiscagem não disponível (fallback ativo)")
        
        # Testar import das rotas
        try:
            from app.routes import configuracao_discagem
            print("✓ Rota configuracao_discagem importada com sucesso")
        except ImportError:
            print("⚠ Rota configuracao_discagem não disponível (fallback ativo)")
        
        # Testar criação da app
        from main import app
        print("✓ App FastAPI criada com sucesso")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro nos imports: {str(e)}")
        return False

def info_ambiente():
    """Mostra informações do ambiente."""
    print(f"Versão: {VERSION}")
    print(f"Build: {BUILD_DATE}")
    print(f"Python: {sys.version}")
    print(f"Diretório de trabalho: {os.getcwd()}")
    print(f"Timestamp atual: {datetime.now().isoformat()}")

if __name__ == "__main__":
    print("=== Verificação de Versão do Backend ===")
    info_ambiente()
    print("\n=== Teste de Imports ===")
    sucesso = verificar_imports()
    
    if sucesso:
        print("\n✓ Todos os imports funcionaram corretamente!")
        sys.exit(0)
    else:
        print("\n✗ Problemas encontrados nos imports!")
        sys.exit(1) 