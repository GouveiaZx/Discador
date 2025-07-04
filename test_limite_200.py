#!/usr/bin/env python3
"""
Teste simplificado para verificar limite de 200 registros
"""

import requests
import time

def test_200_limit():
    """Testar limite de 200 registros"""
    
    print("🎯 TESTE LIMITE 200 REGISTROS")
    print("=" * 50)
    
    # Criar números de teste
    base_numbers = ["7542348734", "9564044921", "9563290923", "2813903426", "8136453764"]
    
    # Teste 1: 150 números (abaixo do limite)
    print("\n📋 TESTE 1: 150 números (deve funcionar)")
    print("-" * 40)
    
    numbers_150 = []
    for i in range(150):
        base_idx = i % len(base_numbers)
        base_num = base_numbers[base_idx]
        variation = f"{i:04d}"[-4:]
        number = base_num[:-4] + variation
        numbers_150.append(number)
    
    with open("test_150.txt", "w") as f:
        f.write('\n'.join(numbers_150))
    
    success_150 = test_upload("test_150.txt", 150)
    
    # Teste 2: 200 números (no limite)
    print("\n📋 TESTE 2: 200 números (deve funcionar)")
    print("-" * 40)
    
    numbers_200 = []
    for i in range(200):
        base_idx = i % len(base_numbers)
        base_num = base_numbers[base_idx]
        variation = f"{i:04d}"[-4:]
        number = base_num[:-4] + variation
        numbers_200.append(number)
    
    with open("test_200.txt", "w") as f:
        f.write('\n'.join(numbers_200))
    
    success_200 = test_upload("test_200.txt", 200)
    
    # Teste 3: 300 números (deve truncar para 200)
    print("\n📋 TESTE 3: 300 números (deve truncar para 200)")
    print("-" * 40)
    
    numbers_300 = []
    for i in range(300):
        base_idx = i % len(base_numbers)
        base_num = base_numbers[base_idx]
        variation = f"{i:04d}"[-4:]
        number = base_num[:-4] + variation
        numbers_300.append(number)
    
    with open("test_300.txt", "w") as f:
        f.write('\n'.join(numbers_300))
    
    success_300 = test_upload("test_300.txt", 300, expect_truncation=True)
    
    # Limpar arquivos
    import os
    for filename in ["test_150.txt", "test_200.txt", "test_300.txt"]:
        try:
            os.remove(filename)
        except:
            pass
    
    print("\n" + "=" * 50)
    print("📊 RESUMO")
    print("=" * 50)
    
    results = [
        ("150 números", success_150),
        ("200 números", success_200),
        ("300 números (truncado)", success_300)
    ]
    
    for desc, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {desc}: {'SUCESSO' if success else 'FALHOU'}")
    
    total_success = sum(1 for _, success in results if success)
    
    if total_success == 3:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema otimizado com limite de 200 registros funcionando!")
    else:
        print(f"\n⚠️ {total_success}/3 testes passaram")
    
    return total_success == 3

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
            response = requests.post(url, files=files, data=data, timeout=120)
            duration = time.time() - start_time
            
            print(f"⏱️ Duração: {duration:.2f}s")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                contatos_validos = result.get('contatos_validos', 0)
                arquivo_truncado = result.get('arquivo_truncado', False)
                
                print(f"✅ Contatos processados: {contatos_validos}")
                print(f"✂️ Truncado: {'SIM' if arquivo_truncado else 'NÃO'}")
                
                if expect_truncation:
                    if arquivo_truncado and contatos_validos == 200:
                        print("✅ Truncamento funcionou!")
                        return True
                    else:
                        print("❌ Truncamento não funcionou como esperado")
                        return False
                else:
                    if not arquivo_truncado and contatos_validos == expected_numbers:
                        print("✅ Upload completo funcionou!")
                        return True
                    else:
                        print("❌ Upload não funcionou como esperado")
                        return False
            else:
                print(f"❌ ERRO: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    test_200_limit() 