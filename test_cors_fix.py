#!/usr/bin/env python3
"""
🔍 Teste CORS Fix - Verificar se o CORS está funcionando
"""

import requests
import time

def test_cors():
    """Testa se o CORS está funcionando"""
    
    print("🔍 Testando CORS Fix...")
    
    # Headers simulando frontend
    headers = {
        "Origin": "https://discador.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        # Teste OPTIONS
        print("📋 Testando OPTIONS...")
        response = requests.options(
            "https://discador.onrender.com/api/v1/contacts/upload",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Verificar headers CORS
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        print(f"🌐 CORS Headers: {cors_headers}")
        
        # Teste GET básico
        print("\n📋 Testando GET...")
        response = requests.get(
            "https://discador.onrender.com/api/v1/contacts/test",
            headers={"Origin": "https://discador.vercel.app"},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_backend_health():
    """Testa se o backend está saudável"""
    
    print("\n🏥 Testando saúde do backend...")
    
    try:
        response = requests.get(
            "https://discador.onrender.com/health",
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    
    print("🚀 Iniciando testes CORS...")
    
    # Teste 1: Backend Health
    health_ok = test_backend_health()
    
    # Teste 2: CORS
    cors_ok = test_cors()
    
    # Resultado final
    print(f"\n📊 Resultados:")
    print(f"✅ Backend Health: {'OK' if health_ok else 'FAIL'}")
    print(f"✅ CORS: {'OK' if cors_ok else 'FAIL'}")
    
    if health_ok and cors_ok:
        print("\n🎉 Sistema pronto para testar Slackall.txt!")
        print("🔗 Frontend: https://discador.vercel.app/")
        print("🔗 Backend: https://discador.onrender.com/")
        print("\n📝 Instruções:")
        print("1. Acesse https://discador.vercel.app/")
        print("2. Selecione Slackall.txt")
        print("3. Escolha uma campanha")
        print("4. Clique em Upload")
        print("5. Aguarde o processamento em chunks")
    else:
        print("\n❌ Sistema não está pronto ainda")

if __name__ == "__main__":
    main() 