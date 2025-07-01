#!/usr/bin/env python3
"""
Teste dos endpoints do discador API
"""
import requests
import time
import json

# URLs de teste
# BASE_URL = "http://localhost:8000"  # Local
BASE_URL = "https://web-production-c192b.up.railway.app"  # Railway

def test_discador_endpoints():
    """
    Testa todos os endpoints relacionados ao discador
    """
    print("🧪 TESTANDO ENDPOINTS DO DISCADOR")
    print("=" * 50)
    
    # 1. Testar status do discador
    print("\n1. 📊 Status do Discador:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/discador/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # 2. Testar estatísticas da campanha
    print("\n2. 📈 Estatísticas da Campanha:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/campaigns/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # 3. Testar dados reais do dashboard
    print("\n3. 📋 Dashboard Real Stats:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/dashboard/real-stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard: Dados reais carregados!")
            print(f"   KPIs: {data['data']['kpis']}")
            print(f"   Sistema: {data['data']['system_status']}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # 4. Testar iniciar campanha
    print("\n4. 🚀 Iniciar Campanha:")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/campaigns/1/start")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Campanha iniciada: {data['message']}")
            print(f"   Contatos: {data['total_contacts']}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # 5. Aguardar e verificar chamadas ativas
    print("\n5. 📞 Chamadas Ativas (aguardando 3s):")
    time.sleep(3)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/campaigns/active-calls")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chamadas ativas: {data['total']}")
            if data['data']:
                for call in data['data']:
                    print(f"   📞 {call['phone_number']} - {call['duration']}s")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # 6. Verificar estatísticas atualizadas
    print("\n6. 📊 Estatísticas Atualizadas:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/campaigns/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data['data']
            print(f"✅ Calls totais: {stats['total_calls']}")
            print(f"   Sucessos: {stats['successful_calls']}")
            print(f"   Taxa de sucesso: {stats['success_rate']}%")
            print(f"   Rodando: {stats['is_running']}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # 7. Parar campanha
    print("\n7. 🛑 Parar Campanha:")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/campaigns/1/stop")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Campanha parada: {data['message']}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def test_existing_endpoints():
    """
    Testa endpoints existentes para verificar compatibilidade
    """
    print("\n\n🔍 TESTANDO ENDPOINTS EXISTENTES")
    print("=" * 50)
    
    # Testar campanhas
    print("\n1. 📋 Listar Campanhas:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/campaigns")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Campanhas: {len(data.get('data', []))} encontradas")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # Testar blacklist
    print("\n2. 🚫 Blacklist:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/blacklist")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Blacklist: {len(data.get('data', []))} números")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    print("🎯 TESTE COMPLETO DO DISCADOR API")
    print("=" * 60)
    
    # Verificar se servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Servidor ativo em: {BASE_URL}")
    except:
        print(f"❌ Servidor não encontrado em: {BASE_URL}")
        print("💡 Inicie o servidor com: python main.py")
        exit(1)
    
    # Executar testes
    test_discador_endpoints()
    test_existing_endpoints()
    
    print("\n\n🎉 TESTE CONCLUÍDO!")
    print("=" * 60)
    print("📋 PRÓXIMOS PASSOS:")
    print("1. Deploy no Railway com novos endpoints")
    print("2. Atualizar frontend para usar dados reais")
    print("3. Integrar com Supabase PostgreSQL")
    print("4. Adicionar logs reais de chamadas") 