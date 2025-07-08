#!/usr/bin/env python3
import requests

print("🔄 Parando campanha...")
try:
    r = requests.post('https://discador.onrender.com/api/v1/presione1/campanhas/1/parar')
    print(f"Status parar: {r.status_code}")
except:
    print("Campanha provavelmente já estava parada")

print("\n🚀 Testando iniciar campanha...")
try:
    r = requests.post(
        'https://discador.onrender.com/api/v1/presione1/campanhas/1/iniciar',
        json={"usuario_id": "1"}
    )
    print(f"Status iniciar: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Resposta: {data}")
        
        # Simular validação do frontend corrigida
        has_mensaje = 'mensaje' in data
        print(f"Frontend detectará sucesso: {has_mensaje}")
        
    else:
        print(f"❌ Erro: {r.text}")
        
except Exception as e:
    print(f"❌ Exceção: {e}") 