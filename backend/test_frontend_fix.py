#!/usr/bin/env python3
"""
Teste para validar a correção do frontend
Simula exatamente o que o frontend faz
"""
import requests
import json

def simular_frontend_request():
    print("🧪 Simulando request do frontend após correção...")
    
    # 1. Simular exatamente o que o frontend faz
    url = "https://discador.onrender.com/api/v1/presione1/campanhas/1/iniciar"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "usuario_id": "1"
    }
    
    print(f"🔗 URL: {url}")
    print(f"📝 Data: {data}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Response Data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verificar se tem as propriedades que o frontend agora busca
            has_mensaje = 'mensaje' in response_data
            has_message = 'message' in response_data  
            has_success = 'success' in response_data
            
            print(f"\n🔍 Validação Frontend:")
            print(f"   - Tem 'mensaje': {has_mensaje}")
            print(f"   - Tem 'message': {has_message}")
            print(f"   - Tem 'success': {has_success}")
            
            # Simular a validação do frontend corrigida
            if response_data and (has_mensaje or has_message or has_success):
                success_message = response_data.get('mensaje') or 'Campaña iniciada con éxito'
                print(f"✅ Frontend mostrará SUCESSO: '{success_message}'")
                return True
            else:
                print("❌ Frontend ainda mostraria ERRO")
                return False
                
        else:
            print(f"❌ Status não é 200: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        return False

def test_pause_response():
    print("\n🔄 Testando resposta de pausar campanha...")
    
    url = "https://discador.onrender.com/api/v1/presione1/campanhas/1/pausar"
    data = {
        "pausar": True,
        "motivo": "Teste frontend"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verificar validação do frontend para pausar
            has_mensaje = 'mensaje' in response_data
            has_message = 'message' in response_data
            
            if has_mensaje or has_message:
                print("✅ Pausar funcionará no frontend")
            else:
                print("❌ Pausar pode ter problema no frontend")
        else:
            print(f"⚠️ Status pausar: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar pausar: {str(e)}")

if __name__ == "__main__":
    print("🎯 Testando se correção do frontend resolve o problema")
    print("=" * 60)
    
    success = simular_frontend_request()
    test_pause_response()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCESSO! Frontend deve mostrar campanha iniciada corretamente")
    else:
        print("❌ Ainda há problemas que precisam ser resolvidos") 