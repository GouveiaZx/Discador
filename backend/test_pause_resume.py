#!/usr/bin/env python3
# Teste simples das funcionalidades de pausar/retomar campanhas

import requests
import time
import json

def test_pause_resume_simple():
    """Teste simples das APIs de pausar/retomar via HTTP."""
    base_url = "http://127.0.0.1:8000/api/v1/presione1"
    
    print("🔍 Testando APIs de pausar/retomar campanhas...")
    
    try:
        # 1. Listar campanhas
        print("\n1. Listando campanhas...")
        response = requests.get(f"{base_url}/campanhas")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            campanhas = response.json()
            print(f"✅ Encontradas {len(campanhas)} campanhas")
            
            if not campanhas:
                print("❌ Nenhuma campanha encontrada")
                return
            
            # Usar a primeira campanha
            campanha = campanhas[0]
            campanha_id = campanha["id"]
            print(f"📋 Usando campanha ID: {campanha_id} - {campanha.get('nombre', 'Sem nome')}")
            print(f"📊 Estado inicial: activa={campanha.get('activa')}, pausada={campanha.get('pausada')}")
            
            # 2. Testar pausar (se a campanha estiver ativa)
            if campanha.get("activa"):
                print("\n2. Testando pausar campanha...")
                pause_data = {"pausar": True, "motivo": "Teste"}
                response = requests.post(f"{base_url}/campanhas/{campanha_id}/pausar", json=pause_data)
                print(f"Status pausar: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Resposta pausar: {response.json()}")
                else:
                    print(f"❌ Erro pausar: {response.text}")
                
                # 3. Verificar estado após pausar
                time.sleep(1)
                print("\n3. Verificando estado após pausar...")
                response = requests.get(f"{base_url}/campanhas/{campanha_id}")
                if response.status_code == 200:
                    campanha_pausada = response.json()
                    print(f"📊 Estado após pausar: activa={campanha_pausada.get('activa')}, pausada={campanha_pausada.get('pausada')}")
                
                # 4. Testar retomar
                print("\n4. Testando retomar campanha...")
                response = requests.post(f"{base_url}/campanhas/{campanha_id}/retomar")
                print(f"Status retomar: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Resposta retomar: {response.json()}")
                else:
                    print(f"❌ Erro retomar: {response.text}")
                
                # 5. Verificar estado após retomar
                time.sleep(1)
                print("\n5. Verificando estado após retomar...")
                response = requests.get(f"{base_url}/campanhas/{campanha_id}")
                if response.status_code == 200:
                    campanha_retomada = response.json()
                    print(f"📊 Estado após retomar: activa={campanha_retomada.get('activa')}, pausada={campanha_retomada.get('pausada')}")
            else:
                print("⚠️ Campanha não está ativa, não é possível testar pausar/retomar")
            
        else:
            print(f"❌ Erro ao listar campanhas: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"💥 Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pause_resume_simple()