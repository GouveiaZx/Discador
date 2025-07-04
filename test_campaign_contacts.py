#!/usr/bin/env python3
"""
🔍 Diagnóstico de Contatos por Campanha
Verifica se os contatos estão sendo corretamente associados às campanhas
"""

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

def diagnosticar_campanhas():
    """Diagnóstico completo de campanhas e contatos"""
    
    print("🔍 DIAGNÓSTICO DE CAMPANHAS E CONTATOS\n")
    print("=" * 60)
    
    # 1. Buscar todas as campanhas
    print("\n📋 1. BUSCANDO CAMPANHAS...")
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/campaigns",
            headers=headers
        )
        
        if response.status_code == 200:
            campanhas = response.json()
            print(f"✅ Encontradas {len(campanhas)} campanhas")
            
            # Mostrar campanhas
            for i, camp in enumerate(campanhas, 1):
                print(f"\n   Campanha {i}:")
                print(f"   - ID: {camp['id']}")
                print(f"   - Nome: {camp['name']}")
                print(f"   - Status: {camp['status']}")
                print(f"   - CLI: {camp.get('cli_number', 'Não definido')}")
        else:
            print(f"❌ Erro ao buscar campanhas: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return
    
    # 2. Buscar contatos por campanha
    print("\n\n📞 2. BUSCANDO CONTATOS POR CAMPANHA...")
    print("-" * 60)
    
    for camp in campanhas:
        camp_id = camp['id']
        camp_name = camp['name']
        
        print(f"\n🎯 Campanha: {camp_name} (ID: {camp_id})")
        
        try:
            # Buscar contatos dessa campanha
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=eq.{camp_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                contatos = response.json()
                print(f"   ✅ Total de contatos: {len(contatos)}")
                
                # Mostrar primeiros 5 contatos
                if contatos:
                    print(f"   📱 Primeiros contatos:")
                    for i, contact in enumerate(contatos[:5], 1):
                        print(f"      {i}. {contact['phone_number']} - Status: {contact.get('status', 'N/A')}")
                    
                    if len(contatos) > 5:
                        print(f"      ... e mais {len(contatos) - 5} contatos")
                else:
                    print("   ⚠️  Nenhum contato encontrado para esta campanha")
                    
            else:
                print(f"   ❌ Erro ao buscar contatos: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    # 3. Buscar total geral de contatos
    print("\n\n📊 3. ESTATÍSTICAS GERAIS...")
    print("-" * 60)
    
    try:
        # Total de contatos
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/contacts?select=count",
            headers={**headers, "Prefer": "count=exact"}
        )
        
        if response.status_code == 200:
            total_contatos = response.headers.get('content-range', '0').split('/')[-1]
            print(f"📞 Total geral de contatos: {total_contatos}")
        
        # Contatos sem campanha
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=is.null&select=count",
            headers={**headers, "Prefer": "count=exact"}
        )
        
        if response.status_code == 200:
            sem_campanha = response.headers.get('content-range', '0').split('/')[-1]
            print(f"⚠️  Contatos sem campanha: {sem_campanha}")
            
    except Exception as e:
        print(f"❌ Erro nas estatísticas: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📋 DIAGNÓSTICO CONCLUÍDO!\n")

def testar_upload_com_campanha():
    """Testa upload de contatos associando a uma campanha"""
    
    print("\n\n🧪 TESTE DE UPLOAD COM CAMPANHA")
    print("=" * 60)
    
    # 1. Criar campanha de teste
    print("\n1️⃣ Criando campanha de teste...")
    
    campaign_data = {
        "name": "Teste Upload Contatos",
        "description": "Campanha para testar associação de contatos",
        "cli_number": "+5511999999999",
        "status": "draft"
    }
    
    try:
        response = requests.post(
            "https://discador.onrender.com/api/v1/campaigns",
            json=campaign_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            campaign_id = result.get('id') or result.get('campaign', {}).get('id')
            print(f"✅ Campanha criada! ID: {campaign_id}")
        else:
            print(f"❌ Erro ao criar campanha: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return
    
    # 2. Fazer upload de contatos
    print(f"\n2️⃣ Fazendo upload de contatos para campanha {campaign_id}...")
    
    # Criar arquivo temporário
    test_numbers = ["5511999999901", "5511999999902", "5511999999903", "5511999999904", "5511999999905"]
    
    with open("test_upload_campaign.txt", "w") as f:
        for num in test_numbers:
            f.write(f"{num}\n")
    
    # Fazer upload
    with open("test_upload_campaign.txt", "rb") as f:
        files = {"arquivo": ("test_numbers.txt", f, "text/plain")}
        data = {
            "campaign_id": campaign_id,
            "incluir_nome": "true",
            "pais_preferido": "auto"
        }
        
        try:
            response = requests.post(
                "https://discador.onrender.com/api/v1/contacts/upload",
                files=files,
                data=data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Upload concluído!")
                print(f"   - Contatos válidos: {result.get('contatos_validos', 0)}")
                print(f"   - Contatos inseridos: {result.get('contatos_inseridos', 0)}")
            else:
                print(f"❌ Erro no upload: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
    
    # 3. Verificar contatos da campanha
    print(f"\n3️⃣ Verificando contatos da campanha {campaign_id}...")
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=eq.{campaign_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            contatos = response.json()
            print(f"✅ Encontrados {len(contatos)} contatos na campanha")
            
            for i, contact in enumerate(contatos, 1):
                print(f"   {i}. {contact['phone_number']} - Campaign ID: {contact['campaign_id']}")
        else:
            print(f"❌ Erro ao verificar: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # Limpar arquivo temporário
    import os
    if os.path.exists("test_upload_campaign.txt"):
        os.remove("test_upload_campaign.txt")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Executar diagnóstico
    diagnosticar_campanhas()
    
    # Perguntar se quer fazer teste
    print("\n\n❓ Deseja executar teste de upload? (s/n): ", end="")
    resposta = input().strip().lower()
    
    if resposta == 's':
        testar_upload_com_campanha()
    
    print("\n✅ Diagnóstico finalizado!") 