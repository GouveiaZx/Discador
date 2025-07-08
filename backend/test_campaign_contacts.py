#!/usr/bin/env python3
"""
Script para testar se campanhas têm contatos e debug do erro 400
"""
import requests
import json

def test_campaigns():
    print("🔍 Testando campanhas e contatos...")
    
    # 1. Verificar campanhas principais
    print("\n📋 Verificando campanhas principais:")
    try:
        response = requests.get('https://discador.onrender.com/api/v1/campaigns')
        if response.status_code == 200:
            data = response.json()
            campaigns = data.get('campaigns', [])
            
            for c in campaigns:
                if c.get('id') == 1:
                    print(f"✅ Campanha ID 1: {c['name']} - {c.get('contacts_total', 0)} contatos")
                    break
            else:
                print("❌ Campanha ID 1 não encontrada")
        else:
            print(f"❌ Erro ao buscar campanhas: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 2. Verificar campanhas presione1
    print("\n📞 Verificando campanhas presione1:")
    try:
        response = requests.get('https://discador.onrender.com/api/v1/presione1/campanhas')
        if response.status_code == 200:
            campanhas = response.json()
            for c in campanhas:
                print(f"📋 ID {c['id']}: {c['nombre']} (campaign_id: {c.get('campaign_id')})")
        else:
            print(f"❌ Erro ao buscar campanhas presione1: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 3. Testar iniciar campanha para ver erro detalhado
    print("\n🚀 Testando iniciar campanha:")
    try:
        response = requests.post(
            'https://discador.onrender.com/api/v1/presione1/campanhas/1/iniciar',
            json={'usuario_id': '1'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_campaigns() 