#!/usr/bin/env python3
"""
Script para testar o fix da campanha
"""
import requests
import time

def test_campanha():
    print("🧪 Testando fix da campanha...")
    
    base_url = "https://discador.onrender.com/api/v1/presione1/campanhas/1"
    
    # 1. Reset llamadas
    print("\n🗑️ Passo 1: Resetando llamadas...")
    try:
        response = requests.post(f"{base_url}/resetar-llamadas", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reset realizado: {data.get('llamadas_deletadas', 0)} llamadas deletadas")
        elif response.status_code == 404:
            print("⚠️ Endpoint não encontrado (ainda não aplicado no servidor)")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
    
    time.sleep(2)
    
    # 2. Debug da campanha
    print("\n🔍 Passo 2: Verificando estado da campanha...")
    try:
        response = requests.get(f"{base_url}/debug", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Contatos: {data.get('contatos', {}).get('total', 0)}")
            print(f"✅ Llamadas: {data.get('llamadas_realizadas', {}).get('total', 0)}")
            print(f"✅ Pode iniciar: {data.get('pode_iniciar', False)}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
    
    time.sleep(2)
    
    # 3. Iniciar campanha
    print("\n🚀 Passo 3: Tentando iniciar campanha...")
    try:
        response = requests.post(f"{base_url}/iniciar", 
                               json={"usuario_id": "1"}, 
                               timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"🎉 SUCESSO! Campanha iniciada: {data.get('mensaje', '')}")
            print(f"📞 Próximo número: {data.get('proximo_numero', '')}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")

if __name__ == "__main__":
    test_campanha() 