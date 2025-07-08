#!/usr/bin/env python3
"""
Script para investigar diretamente as llamadas na base Supabase
"""
import requests
import json

# Configuração do Supabase 
SUPABASE_URL = "https://orxxocptgaeoyrtlxwkv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjitGJCPUNdVnRhZVd5FVLsGQXrMWMI"

def investigar_llamadas():
    print("🔍 Investigando llamadas na base Supabase...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. Buscar TODAS as llamadas da campanha 1
    print("\n📊 Passo 1: Buscando TODAS as llamadas para campana_id = 1")
    try:
        url = f"{SUPABASE_URL}/rest/v1/llamadas_presione1?campana_id=eq.1"
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            llamadas = response.json()
            total = len(llamadas)
            print(f"✅ Total de llamadas encontradas: {total}")
            
            if total > 0:
                # Analisar os primeiros registros
                print(f"\n📋 Primeiros {min(5, total)} registros:")
                for i, llamada in enumerate(llamadas[:5]):
                    print(f"  {i+1}. ID: {llamada.get('id')} | "
                          f"Estado: {llamada.get('estado')} | "
                          f"Número: {llamada.get('numero_normalizado')} | "
                          f"Data: {llamada.get('fecha_inicio')}")
                
                # Contar por estado
                print(f"\n📈 Contagem por estado:")
                estados = {}
                for llamada in llamadas:
                    estado = llamada.get('estado', 'unknown')
                    estados[estado] = estados.get(estado, 0) + 1
                
                for estado, count in estados.items():
                    print(f"  {estado}: {count}")
                    
            else:
                print("✅ Nenhuma llamada encontrada")
                
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
    
    # 2. Buscar llamadas com estado != error
    print("\n📊 Passo 2: Buscando llamadas com estado != error")
    try:
        url = f"{SUPABASE_URL}/rest/v1/llamadas_presione1?campana_id=eq.1&estado=not.eq.error"
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            llamadas_no_error = response.json()
            total_no_error = len(llamadas_no_error)
            print(f"✅ Total com estado != error: {total_no_error}")
            
            if total_no_error > 0:
                # Mostrar números únicos normalizados
                numeros_unicos = set()
                for llamada in llamadas_no_error:
                    numero = llamada.get('numero_normalizado')
                    if numero:
                        numeros_unicos.add(numero)
                
                print(f"📱 Números únicos normalizados: {len(numeros_unicos)}")
                if len(numeros_unicos) <= 10:
                    print(f"   Números: {list(numeros_unicos)}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
    
    # 3. Buscar contatos da campanha principal
    print("\n📊 Passo 3: Verificando contatos da campanha principal")
    try:
        url = f"{SUPABASE_URL}/rest/v1/contacts?campaign_id=eq.1&select=id,phone_number"
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            contatos = response.json()
            total_contatos = len(contatos)
            print(f"✅ Total de contatos: {total_contatos}")
            
            # Verificar primeiros números
            if total_contatos > 0:
                print(f"\n📱 Primeiros 5 números de contatos:")
                for i, contato in enumerate(contatos[:5]):
                    print(f"  {i+1}. ID: {contato.get('id')} | "
                          f"Número: {contato.get('phone_number')}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")

if __name__ == "__main__":
    investigar_llamadas() 