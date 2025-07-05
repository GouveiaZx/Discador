import requests
import json

# Configurações do Supabase
SUPABASE_URL = "https://orxxocptgaeoyrtlxwkv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjVzdbZcnlN_jiT1mNijqWEWylVrhdQ"

headers = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

print("🔍 Testando consultas Supabase diretamente...")

# 1. Buscar campanhas
print("\n1️⃣ Buscando campanhas...")
try:
    response = requests.get(f"{SUPABASE_URL}/rest/v1/campaigns", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        campaigns = response.json()
        print(f"Campanhas encontradas: {len(campaigns)}")
        for camp in campaigns[:3]:
            print(f"  - ID {camp['id']}: {camp['name']}")
    else:
        print(f"Erro: {response.text}")
except Exception as e:
    print(f"Erro: {e}")

# 2. Teste de contagem direta - campanha 1
print("\n2️⃣ Testando contagem para campanha ID 1...")
campaign_id = 1

# Método 1: count()
print("  Método 1: count()")
try:
    count_url = f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=eq.{campaign_id}&select=count()"
    response = requests.get(count_url, headers=headers)
    print(f"  Status: {response.status_code}")
    print(f"  URL: {count_url}")
    print(f"  Resposta: {response.text}")
    if response.status_code == 200:
        result = response.json()
        print(f"  Resultado tipo: {type(result)}")
        print(f"  Resultado: {result}")
except Exception as e:
    print(f"  Erro: {e}")

# Método 2: content-range
print("  Método 2: content-range")
try:
    range_url = f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=eq.{campaign_id}&select=id&limit=1"
    response = requests.get(range_url, headers={**headers, "Prefer": "count=exact"})
    print(f"  Status: {response.status_code}")
    print(f"  URL: {range_url}")
    print(f"  Headers: {dict(response.headers)}")
    content_range = response.headers.get('content-range', 'N/A')
    print(f"  Content-Range: '{content_range}'")
    print(f"  Resposta: {response.text}")
except Exception as e:
    print(f"  Erro: {e}")

# Método 3: buscar alguns registros
print("  Método 3: buscar registros")
try:
    simple_url = f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=eq.{campaign_id}&limit=5"
    response = requests.get(simple_url, headers=headers)
    print(f"  Status: {response.status_code}")
    print(f"  URL: {simple_url}")
    if response.status_code == 200:
        contacts = response.json()
        print(f"  Tipo: {type(contacts)}")
        print(f"  Quantidade: {len(contacts) if isinstance(contacts, list) else 'N/A'}")
        if isinstance(contacts, list) and len(contacts) > 0:
            print(f"  Primeiro contato: {contacts[0]}")
        print(f"  Resposta completa: {response.text[:200]}...")
    else:
        print(f"  Erro: {response.text}")
except Exception as e:
    print(f"  Erro: {e}")

# 3. Teste para campanha 3 (que sabemos ter 700k contatos)
print(f"\n3️⃣ Testando contagem para campanha ID 3 (700k contatos)...")
campaign_id = 3

print("  Método content-range:")
try:
    range_url = f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=eq.{campaign_id}&select=id&limit=1"
    response = requests.get(range_url, headers={**headers, "Prefer": "count=exact"})
    print(f"  Status: {response.status_code}")
    content_range = response.headers.get('content-range', 'N/A')
    print(f"  Content-Range: '{content_range}'")
    if '/' in content_range:
        total = content_range.split('/')[-1]
        print(f"  Total extraído: '{total}'")
except Exception as e:
    print(f"  Erro: {e}")

print("\n🎯 Diagnóstico concluído!") 