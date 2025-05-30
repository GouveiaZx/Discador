#!/usr/bin/env python3
"""
Script para testar o novo backend no Railway
"""
import requests
import json

def test_backend():
    backend_url = "https://web-production-c192b.up.railway.app"
    
    print("🧪 Testando novo backend...")
    
    try:
        # Teste endpoint root
        print(f"\n1️⃣ Testando {backend_url}/")
        response = requests.get(f"{backend_url}/", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data.get('message', 'N/A')}")
            print(f"Version: {data.get('version', 'N/A')}")
        
        # Teste endpoint health
        print(f"\n2️⃣ Testando {backend_url}/health")
        response = requests.get(f"{backend_url}/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Health: {data}")
        
        # Teste endpoint campanhas
        print(f"\n3️⃣ Testando {backend_url}/api/v1/campaigns")
        response = requests.get(f"{backend_url}/api/v1/campaigns", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Campanhas: {data.get('total', 0)} encontradas")
        
        # Teste endpoint chamadas em progresso (compatibilidade)
        print(f"\n4️⃣ Testando {backend_url}/api/v1/llamadas/en-progreso")
        response = requests.get(f"{backend_url}/api/v1/llamadas/en-progreso", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Chamadas ativas: {data.get('total', 0)}")
        
        print("\n✅ Todos os testes completados!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_backend() 