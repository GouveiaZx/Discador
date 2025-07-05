import requests
import time

# Aguardar o servidor inicializar
print("🔍 Aguardando servidor inicializar...")
time.sleep(5)

try:
    print("🔍 Testando API de campanhas...")
    response = requests.get('http://localhost:8000/api/v1/campaigns', timeout=10)
    
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        campaigns = data.get('campaigns', [])
        print(f"✅ Campanhas encontradas: {len(campaigns)}")
        
        total_contacts = 0
        for camp in campaigns:
            contacts = camp.get('contacts_total', 0)
            total_contacts += contacts
            print(f"📋 {camp['name']} (ID: {camp['id']}): {contacts:,} contatos")
        
        print(f"\n🎯 Total de contatos: {total_contacts:,}")
        
        if total_contacts > 0:
            print("✅ CORREÇÃO FUNCIONOU! Contatos estão sendo contados corretamente.")
        else:
            print("❌ AINDA HÁ PROBLEMA: Nenhum contato foi contado.")
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        print(f"❌ Resposta: {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print("❌ Erro: Servidor não está rodando ou não acessível")
except Exception as e:
    print(f"❌ Erro inesperado: {e}") 