#!/usr/bin/env python3
"""
Script para testar CORS em produção
Uso: python test_cors_production.py
"""

import requests
import json
from datetime import datetime

def test_cors_production():
    """Testa configuração de CORS em produção"""
    
    base_url = "https://discador.onrender.com/api/v1"
    origin = "https://discador.vercel.app"
    
    print("🧪 Testando CORS em Produção")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print(f"Origin: {origin}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Teste 1: Endpoint básico de campanhas
    print("📋 Teste 1: GET /campaigns")
    try:
        response = requests.get(
            f"{base_url}/campaigns",
            headers={
                "Origin": origin,
                "Accept": "application/json"
            },
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"CORS Headers:")
        cors_headers = {
            k: v for k, v in response.headers.items() 
            if k.lower().startswith('access-control')
        }
        for header, value in cors_headers.items():
            print(f"  {header}: {value}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso - {len(data.get('campaigns', []))} campanhas encontradas")
        else:
            print(f"❌ Erro - Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()
    
    # Teste 2: Endpoint específico de teste CORS
    print("🔧 Teste 2: GET /cors-test")
    try:
        response = requests.get(
            f"{base_url}/cors-test",
            headers={
                "Origin": origin,
                "Accept": "application/json"
            },
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"CORS Headers:")
        cors_headers = {
            k: v for k, v in response.headers.items() 
            if k.lower().startswith('access-control')
        }
        for header, value in cors_headers.items():
            print(f"  {header}: {value}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso - {data.get('message', 'N/A')}")
            print(f"CORS Origins configuradas: {data.get('cors_origins', [])}")
        else:
            print(f"❌ Erro - Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()
    
    # Teste 3: OPTIONS request
    print("⚙️ Teste 3: OPTIONS /campaigns")
    try:
        response = requests.options(
            f"{base_url}/campaigns",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"CORS Headers:")
        cors_headers = {
            k: v for k, v in response.headers.items() 
            if k.lower().startswith('access-control')
        }
        for header, value in cors_headers.items():
            print(f"  {header}: {value}")
        
        if response.status_code in [200, 204]:
            print(f"✅ Sucesso - OPTIONS funcionando")
        else:
            print(f"❌ Erro - Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()
    print("🎯 Resumo dos Testes")
    print("=" * 50)
    print("Se todos os testes mostraram ✅ e headers CORS corretos,")
    print("o problema de CORS deve estar resolvido!")
    print()
    print("Headers CORS esperados:")
    print("- Access-Control-Allow-Origin: https://discador.vercel.app")
    print("- Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS")
    print("- Access-Control-Allow-Headers: *")
    print("- Access-Control-Allow-Credentials: true")

if __name__ == "__main__":
    test_cors_production()