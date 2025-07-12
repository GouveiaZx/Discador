#!/usr/bin/env python3
"""
Script para testar o sistema CLI Pattern Generator após as correções
"""

import requests
import json
import os
from datetime import datetime

# Configurações
BASE_URL = "https://discador.onrender.com/api/v1"
LOCAL_URL = "http://localhost:8000/api/v1"

def test_cli_pattern_system():
    """Testa o sistema CLI Pattern Generator"""
    
    print("🔍 Testando Sistema CLI Pattern Generator")
    print("=" * 60)
    
    # Teste 1: Verificar diagnóstico do Supabase
    print("\n1. Diagnóstico do Supabase:")
    try:
        response = requests.get(f"{BASE_URL}/diagnostics/supabase", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📊 URL configurada: {data['diagnostics']['supabase_url_configured']}")
            print(f"🔑 Key configurada: {data['diagnostics']['supabase_key_configured']}")
            if data['diagnostics']['connection_tests']:
                for test in data['diagnostics']['connection_tests']:
                    print(f"🧪 {test['test']}: {'✅' if test['success'] else '❌'}")
        else:
            print(f"❌ Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Verificar diagnóstico do CLI Pattern
    print("\n2. Diagnóstico do CLI Pattern:")
    try:
        response = requests.get(f"{BASE_URL}/diagnostics/cli-pattern", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"🛠️ Fallback funcionando: {data['fallback_working']}")
            if data['test_result'].get('data', {}).get('generated_clis'):
                print(f"📞 CLI gerado: {data['test_result']['data']['generated_clis'][0]}")
        else:
            print(f"❌ Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 3: Verificar países suportados
    print("\n3. Países suportados:")
    try:
        response = requests.get(f"{BASE_URL}/performance/cli-pattern/countries", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            if data.get('success') and data.get('data'):
                print(f"🌍 Países encontrados: {len(data['data'])}")
                for country in data['data'][:3]:  # Mostrar apenas os primeiros 3
                    print(f"   - {country['name']} ({country['country_code']})")
        else:
            print(f"❌ Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 4: Gerar CLIs (teste principal)
    print("\n4. Geração de CLIs:")
    test_cases = [
        {"destination_number": "+14165551234", "quantity": 2, "desc": "Canadá"},
        {"destination_number": "+13055551234", "quantity": 2, "desc": "USA"},
        {"destination_number": "+525555551234", "quantity": 2, "desc": "México"},
        {"destination_number": "+5511999999999", "quantity": 2, "desc": "Brasil"}
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/performance/cli-pattern/generate",
                json=test_case,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    clis = data.get('generated_clis', []) or data.get('data', {}).get('generated_clis', [])
                    if clis:
                        print(f"✅ {test_case['desc']}: {', '.join(clis)}")
                    else:
                        print(f"⚠️ {test_case['desc']}: Sucesso mas sem CLIs")
                else:
                    print(f"❌ {test_case['desc']}: {data.get('error', 'Erro desconhecido')}")
            else:
                print(f"❌ {test_case['desc']}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {test_case['desc']}: Erro {e}")

if __name__ == "__main__":
    test_cli_pattern_system() 