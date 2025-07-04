#!/usr/bin/env python3
"""
Script para testar e diagnosticar problemas no endpoint de upload
"""

import requests
import json
import sys
import os

def test_upload_endpoint():
    """Testa o endpoint de upload com diferentes cenários"""
    
    BASE_URL = "https://discador.onrender.com"
    
    print("🔍 DIAGNÓSTICO COMPLETO DO SISTEMA DE UPLOAD")
    print("=" * 60)
    
    # 1. Teste de conectividade do backend
    print("\n1. 🌐 TESTANDO CONECTIVIDADE DO BACKEND...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"✅ Backend conectado: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Versão: {data.get('version')}")
        else:
            print(f"❌ Backend retornou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conectividade: {e}")
        return False
    
    # 2. Teste da documentação do endpoint
    print("\n2. 📚 TESTANDO DOCUMENTAÇÃO API...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=10)
        print(f"✅ Documentação disponível: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na documentação: {e}")
    
    # 3. Criar arquivo de teste
    print("\n3. 📄 CRIANDO ARQUIVO DE TESTE...")
    test_file = "test_diagnostic.txt"
    test_numbers = [
        "7542348734",
        "9564044921", 
        "9563290923",
        "7865432109",
        "5551234567"
    ]
    
    with open(test_file, 'w') as f:
        for number in test_numbers:
            f.write(f"{number}\n")
    
    print(f"✅ Arquivo criado: {test_file} com {len(test_numbers)} números")
    
    # 4. Teste do endpoint de upload - SEM campaign_id
    print("\n4. 🧪 TESTE 1: UPLOAD SEM CAMPAIGN_ID...")
    try:
        with open(test_file, 'rb') as f:
            files = {'arquivo': (test_file, f, 'text/plain')}
            data = {
                'incluir_nome': 'true',
                'pais_preferido': 'auto'
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/contacts/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCESSO: {result.get('mensaje', 'Upload realizado')}")
                print(f"   Contatos inseridos: {result.get('contatos_validos', 0)}")
            else:
                print(f"❌ FALHA: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # 5. Teste do endpoint de upload - COM campaign_id
    print("\n5. 🧪 TESTE 2: UPLOAD COM CAMPAIGN_ID...")
    try:
        with open(test_file, 'rb') as f:
            files = {'arquivo': (test_file, f, 'text/plain')}
            data = {
                'incluir_nome': 'true',
                'pais_preferido': 'auto',
                'campaign_id': '1'
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/contacts/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCESSO: {result.get('mensaje', 'Upload realizado')}")
                print(f"   Contatos inseridos: {result.get('contatos_validos', 0)}")
            else:
                print(f"❌ FALHA: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # 6. Teste de listagem de contatos
    print("\n6. 👥 TESTANDO LISTAGEM DE CONTATOS...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/contacts/", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            contacts = response.json()
            print(f"✅ Contatos encontrados: {len(contacts)}")
            if contacts:
                print(f"   Primeiro contato: {contacts[0].get('phone_number', 'N/A')}")
        else:
            print(f"❌ Erro ao listar contatos: {response.text}")
    except Exception as e:
        print(f"❌ Erro na listagem: {e}")
    
    # 7. Teste de campanhas
    print("\n7. 📋 TESTANDO CAMPANHAS...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/campaigns/", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ Campanhas encontradas: {len(campaigns)}")
            if campaigns:
                print(f"   Primeira campanha: ID={campaigns[0].get('id')}, Nome={campaigns[0].get('name', 'N/A')}")
        else:
            print(f"❌ Erro ao listar campanhas: {response.text}")
    except Exception as e:
        print(f"❌ Erro na listagem: {e}")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    test_upload_endpoint() 