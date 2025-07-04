#!/usr/bin/env python3
"""
Script para testar o servidor e verificar por que o erro 422 persiste
"""

import requests
import json
import time
from io import StringIO

def test_server_connection():
    """Testa conexão com o servidor"""
    print("🔍 Testando conexão com servidor...")
    
    try:
        # Testar endpoint de debug (POST)
        url = "https://discador.onrender.com/api/v1/contacts/debug-supabase"
        response = requests.post(url, timeout=10)
        
        print(f"✅ Status: {response.status_code}")
        print(f"📡 Response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_small_upload():
    """Testa upload com arquivo pequeno"""
    print("\n🧪 Testando upload com arquivo pequeno...")
    
    # Criar arquivo pequeno de teste
    test_numbers = [
        "7542348734",
        "9564044921", 
        "9563290923",
        "5551234567",
        "4441234567"
    ]
    
    try:
        url = "https://discador.onrender.com/api/v1/contacts/upload"
        
        # Criar arquivo em memória
        file_content = "\n".join(test_numbers)
        
        files = {
            'arquivo': ('test_numbers.txt', file_content, 'text/plain')
        }
        
        data = {
            'incluir_nome': 'true',
            'pais_preferido': 'auto'
        }
        
        print(f"📤 Enviando {len(test_numbers)} números de teste...")
        
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📡 Response: {response.text}")
        
        if response.status_code == 422:
            print("❌ Erro 422 persistindo mesmo com arquivo pequeno!")
            return False
        elif response.status_code == 200:
            print("✅ Upload pequeno funcionou!")
            return True
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_large_file_limits():
    """Testa como o sistema lida com arquivos grandes"""
    print("\n📊 Testando limites de arquivo grande...")
    
    # Criar arquivo com diferentes tamanhos
    test_sizes = [100, 500, 1000, 2000, 5000]
    
    for size in test_sizes:
        print(f"\n🧪 Testando com {size} números...")
        
        # Gerar números de teste
        test_numbers = [f"555{i:07d}" for i in range(size)]
        
        try:
            url = "https://discador.onrender.com/api/v1/contacts/upload"
            
            file_content = "\n".join(test_numbers)
            
            files = {
                'arquivo': (f'test_{size}.txt', file_content, 'text/plain')
            }
            
            data = {
                'incluir_nome': 'true',
                'pais_preferido': 'auto'
            }
            
            print(f"📤 Enviando {size} números...")
            start_time = time.time()
            
            response = requests.post(url, files=files, data=data, timeout=60)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️ Tempo: {duration:.2f}s")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 422:
                print(f"❌ Erro 422 com {size} números!")
                print(f"📡 Response: {response.text}")
                break
            elif response.status_code == 200:
                print(f"✅ Sucesso com {size} números!")
                try:
                    result = response.json()
                    print(f"📈 Processados: {result.get('total_processados', 'N/A')}")
                    print(f"📈 Válidos: {result.get('total_validos', 'N/A')}")
                except:
                    print("📡 Resposta não é JSON válido")
            else:
                print(f"⚠️ Status: {response.status_code}")
                print(f"📡 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            break

def check_server_logs():
    """Verifica logs do servidor"""
    print("\n📋 Verificando logs do servidor...")
    
    try:
        # Tentar endpoint de status
        url = "https://discador.onrender.com/api/v1/status"
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"📡 Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao verificar logs: {e}")

def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO COMPLETO DO SERVIDOR")
    print("=" * 50)
    
    # 1. Testar conexão
    if not test_server_connection():
        print("❌ Servidor não está respondendo!")
        return
    
    print("\n" + "=" * 50)
    
    # 2. Testar upload pequeno
    if not test_small_upload():
        print("❌ Upload pequeno falhou - problema no servidor!")
        return
    
    print("\n" + "=" * 50)
    
    # 3. Testar diferentes tamanhos
    test_large_file_limits()
    
    print("\n" + "=" * 50)
    
    # 4. Verificar logs
    check_server_logs()
    
    print("\n🎯 DIAGNÓSTICO CONCLUÍDO!")

if __name__ == "__main__":
    main() 