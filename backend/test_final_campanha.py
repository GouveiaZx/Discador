#!/usr/bin/env python3
"""
Teste final da campanha após correções
"""
import requests
import time

def test_campanha_final():
    print("🧪 Teste final da campanha...")
    
    # 1. Parar campanha (se estiver ativa)
    print("\n🛑 Passo 1: Parando campanha se estiver ativa...")
    try:
        response = requests.post('https://discador.onrender.com/api/v1/presione1/campanhas/1/parar')
        print(f"Status parar: {response.status_code}")
    except:
        print("⚠️ Campanha provavelmente já estava parada")
    
    time.sleep(3)
    
    # 2. Iniciar campanha
    print("\n🚀 Passo 2: Iniciando campanha...")
    try:
        response = requests.post(
            'https://discador.onrender.com/api/v1/presione1/campanhas/1/iniciar',
            json={"usuario_id": "1"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🎉 SUCESSO! {data.get('mensaje', '')}")
            print(f"📞 Próximo número: {data.get('proximo_numero', '')}")
            print(f"📊 Llamadas simultâneas: {data.get('llamadas_simultaneas', '')}")
            print(f"⏱️ Tempo entre llamadas: {data.get('tiempo_entre_llamadas', '')}s")
        else:
            print(f"❌ Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        return False
    
    time.sleep(5)
    
    # 3. Verificar estado
    print("\n📊 Passo 3: Verificando estado da campanha...")
    try:
        response = requests.get('https://discador.onrender.com/api/v1/presione1/campanhas/1')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Campanha ativa: {data.get('activa', False)}")
            print(f"✅ Campanha pausada: {data.get('pausada', False)}")
        else:
            print(f"❌ Erro ao verificar estado: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
    
    # 4. Parar campanha
    print("\n🛑 Passo 4: Parando campanha...")
    try:
        response = requests.post('https://discador.onrender.com/api/v1/presione1/campanhas/1/parar')
        print(f"Status parar: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data.get('mensaje', 'Campanha parada')}")
        else:
            print(f"❌ Erro ao parar: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
    
    return True

if __name__ == "__main__":
    test_campanha_final() 