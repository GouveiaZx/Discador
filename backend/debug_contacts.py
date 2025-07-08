#!/usr/bin/env python3
"""
Script para debugar o problema específico de obter próximo número
"""
import requests
import json
import os

# Configuração do Supabase
SUPABASE_URL = "https://orxxocptgaeoyrtlxwkv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjitGJCPUNdVnRhZVd5FVLsGQXrMWMI"

def debug_campaign_contacts():
    print("🔍 Debug do problema de contatos...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. Buscar contatos para campaign_id = 1
    print("\n📞 Buscando contatos para campaign_id = 1:")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=eq.1&phone_number=not.is.null&select=id,phone_number,name",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            contacts = response.json()
            print(f"✅ Encontrados {len(contacts)} contatos")
            
            # Mostrar primeiros 5
            for i, contact in enumerate(contacts[:5]):
                print(f"  {i+1}. {contact.get('phone_number')} - {contact.get('name', 'Sem nome')}")
                
            if len(contacts) > 5:
                print(f"  ... e mais {len(contacts) - 5} contatos")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 2. Buscar chamadas já realizadas para campanha presione1 ID 1
    print("\n📊 Buscando chamadas já realizadas para campanha presione1 ID 1:")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/llamadas_presione1?campana_id=eq.1&estado=not.eq.error&select=numero_normalizado,estado",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            llamadas = response.json()
            print(f"📊 Encontradas {len(llamadas)} chamadas realizadas")
            
            # Mostrar primeiras 5
            for i, llamada in enumerate(llamadas[:5]):
                print(f"  {i+1}. {llamada.get('numero_normalizado')} - {llamada.get('estado')}")
                
            if len(llamadas) > 5:
                print(f"  ... e mais {len(llamadas) - 5} chamadas")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 3. Verificar a campanha presione1
    print("\n📋 Detalhes da campanha presione1 ID 1:")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/campanas_presione1?id=eq.1",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            campanhas = response.json()
            if campanhas:
                campana = campanhas[0]
                print(f"✅ Campanha: {campana.get('nombre')}")
                print(f"   Campaign_id: {campana.get('campaign_id')}")
                print(f"   Ativa: {campana.get('activa')}")
                print(f"   Pausada: {campana.get('pausada')}")
            else:
                print("❌ Campanha não encontrada")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    debug_campaign_contacts() 