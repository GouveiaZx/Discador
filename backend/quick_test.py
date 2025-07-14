#!/usr/bin/env python3
# Teste rápido das funcionalidades principais

import requests
import json

API_BASE_URL = 'http://localhost:8000/api/v1'
CAMPAIGN_ID = 1

def test_api(endpoint, method='GET', data=None):
    """Teste rápido de API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        print(f"🧪 {method} {endpoint}")
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=5)
        
        if response.ok:
            print(f"✅ Status: {response.status_code}")
            try:
                result = response.json()
                print(f"📄 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)[:150]}...")
                return True
            except:
                print(f"📄 Resposta: {response.text[:100]}...")
                return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        return False

def main():
    print("🚀 TESTE RÁPIDO DE CAMPANHAS")
    print("=" * 40)
    
    tests = [
        ("Health Check", "/health", "GET", None),
        ("Listar Campanhas", "/presione1/campanhas", "GET", None),
        ("Buscar Campanha", f"/presione1/campanhas/{CAMPAIGN_ID}", "GET", None),
        ("Pausar Campanha", f"/presione1/campanhas/{CAMPAIGN_ID}/pausar", "POST", {"pausar": True, "motivo": "Teste"}),
        ("Retomar Campanha", f"/presione1/campanhas/{CAMPAIGN_ID}/pausar", "POST", {"pausar": False, "motivo": "Teste"}),
        ("Estatísticas", f"/presione1/campanhas/{CAMPAIGN_ID}/estadisticas", "GET", None)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, endpoint, method, data in tests:
        print(f"\n📋 {name}:")
        if test_api(endpoint, method, data):
            passed += 1
        print("-" * 30)
    
    print(f"\n🏁 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"⚠️ {total - passed} testes falharam")
    
    return passed == total

if __name__ == "__main__":
    main()