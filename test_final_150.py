#!/usr/bin/env python3
"""
Teste final para confirmar limite de 150 registros
"""

import requests
import time

def test_final():
    """Teste final com limite de 150"""
    
    print("🎯 TESTE FINAL - LIMITE 150 REGISTROS")
    print("=" * 50)
    
    base_numbers = ["7542348734", "9564044921", "9563290923", "2813903426", "8136453764"]
    
    # Teste 1: 150 números (deve funcionar)
    print("\n📋 TESTE 1: 150 números")
    numbers_150 = []
    for i in range(150):
        base_idx = i % len(base_numbers)
        base_num = base_numbers[base_idx]
        variation = f"{i:04d}"[-4:]
        number = base_num[:-4] + variation
        numbers_150.append(number)
    
    with open("test_150_final.txt", "w") as f:
        f.write('\n'.join(numbers_150))
    
    success_150 = test_upload("test_150_final.txt", 150)
    
    # Teste 2: 200 números (deve truncar para 150)
    print("\n📋 TESTE 2: 200 números (deve truncar)")
    numbers_200 = []
    for i in range(200):
        base_idx = i % len(base_numbers)
        base_num = base_numbers[base_idx]
        variation = f"{i:04d}"[-4:]
        number = base_num[:-4] + variation
        numbers_200.append(number)
    
    with open("test_200_final.txt", "w") as f:
        f.write('\n'.join(numbers_200))
    
    success_200 = test_upload("test_200_final.txt", 200, expect_truncation=True)
    
    # Limpar
    import os
    for filename in ["test_150_final.txt", "test_200_final.txt"]:
        try:
            os.remove(filename)
        except:
            pass
    
    print("\n" + "=" * 50)
    if success_150 and success_200:
        print("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("✅ Limite de 150 registros validado")
        print("✅ Truncamento automático funcionando")
        return True
    else:
        print("❌ Ainda há problemas no sistema")
        return False

def test_upload(filename, expected_numbers, expect_truncation=False):
    """Testar upload"""
    url = "https://discador.onrender.com/api/v1/contacts/upload"
    
    try:
        with open(filename, 'rb') as f:
            files = {'arquivo': (filename, f, 'text/plain')}
            data = {
                'campaign_id': '1',
                'incluir_nome': 'true',
                'pais_preferido': 'auto'
            }
            
            print(f"📤 Enviando {expected_numbers} números...")
            
            start_time = time.time()
            response = requests.post(url, files=files, data=data, timeout=60)
            duration = time.time() - start_time
            
            print(f"⏱️ Duração: {duration:.2f}s | Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                contatos_validos = result.get('contatos_validos', 0)
                arquivo_truncado = result.get('arquivo_truncado', False)
                
                print(f"✅ Processados: {contatos_validos} | Truncado: {'SIM' if arquivo_truncado else 'NÃO'}")
                
                if expect_truncation:
                    return arquivo_truncado and contatos_validos == 150
                else:
                    return not arquivo_truncado and contatos_validos == expected_numbers
            else:
                print(f"❌ ERRO: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    test_final() 