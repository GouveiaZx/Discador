#!/usr/bin/env python3
# Teste simples para verificar se o backend está funcionando

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Testando importações...")
    
    # Testar importação do FastAPI
    from fastapi import FastAPI
    print("✅ FastAPI importado com sucesso")
    
    # Testar importação do main
    from main import app
    print("✅ App principal importado com sucesso")
    
    # Testar importação do serviço
    from app.services.presione1_service import PresionE1Service
    print("✅ PresionE1Service importado com sucesso")
    
    # Criar uma instância do serviço
    service = PresionE1Service()
    print("✅ Instância do serviço criada com sucesso")
    
    print("\n🎉 Todas as importações funcionaram!")
    print("\n🔧 Testando método pausar_campana...")
    
    # Testar se o método existe
    if hasattr(service, 'pausar_campana'):
        print("✅ Método pausar_campana existe")
    else:
        print("❌ Método pausar_campana não encontrado")
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()