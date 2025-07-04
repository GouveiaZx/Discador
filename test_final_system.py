#!/usr/bin/env python3
"""
Teste final do sistema com limite prático de 400 registros
"""

import requests
import time

def test_system_limits():
    """Testar limites do sistema"""
    
    print("🎯 TESTE FINAL - SISTEMA COM LIMITES PRÁTICOS")
    print("=" * 60)
    
    # Criar arquivo de teste com números americanos
    test_numbers = []
    base_numbers = [
        "7542348734", "9564044921", "9563290923", "2813903426", "8136453764"
    ]
    
    # Teste 1: 100 números (deve funcionar)
    print("\n📋 TESTE 1: Lista pequena (100 números)")
    print("-" * 40)
    
    numbers_100 = []
    for i in range(100):
        base_idx = i % len(base_numbers)
        base_num = base_numbers[base_idx]
        variation = f"{i:04d}"[-4:]
        number = base_num[:-4] + variation
        numbers_100.append(number)
    
    # Salvar arquivo
    with open("test_100.txt", "w") as f:
        f.write('\n'.join(numbers_100))
    
    # Testar upload
    success_100 = test_upload("test_100.txt", 100)
    
    if not success_100:
        print("❌ Teste de 100 números falhou!")
        return False
    
    # Teste 2: 400 números (limite máximo)
    print("\n📋 TESTE 2: Lista no limite (400 números)")
    print("-" * 40)
    
    numbers_400 = []
    for i in range(400):
        base_idx = i % len(base_numbers)
        base_num = base_numbers[base_idx]
        variation = f"{i:04d}"[-4:]
        number = base_num[:-4] + variation
        numbers_400.append(number)
    
    # Salvar arquivo
    with open("test_400.txt", "w") as f:
        f.write('\n'.join(numbers_400))
    
    # Testar upload
    success_400 = test_upload("test_400.txt", 400)
    
    if not success_400:
        print("❌ Teste de 400 números falhou!")
        return False
    
    # Teste 3: 600 números (deve ser truncado para 400)
    print("\n📋 TESTE 3: Lista grande (600 números - deve truncar)")
    print("-" * 40)
    
    numbers_600 = []
    for i in range(600):
        base_idx = i % len(base_numbers)
        base_num = base_numbers[base_idx]
        variation = f"{i:04d}"[-4:]
        number = base_num[:-4] + variation
        numbers_600.append(number)
    
    # Salvar arquivo
    with open("test_600.txt", "w") as f:
        f.write('\n'.join(numbers_600))
    
    # Testar upload
    success_600 = test_upload("test_600.txt", 600, expect_truncation=True)
    
    # Limpar arquivos de teste
    import os
    for filename in ["test_100.txt", "test_400.txt", "test_600.txt"]:
        try:
            os.remove(filename)
        except:
            pass
    
    return success_100 and success_400 and success_600

def test_upload(filename, expected_numbers, expect_truncation=False):
    """Testar upload de arquivo"""
    
    url = "https://discador.onrender.com/api/v1/contacts/upload"
    
    try:
        with open(filename, 'rb') as f:
            files = {
                'arquivo': (filename, f, 'text/plain')
            }
            
            data = {
                'campaign_id': '1',
                'incluir_nome': 'true',
                'pais_preferido': 'auto'
            }
            
            print(f"📤 Enviando {expected_numbers} números...")
            print(f"⏰ Início: {time.strftime('%H:%M:%S')}")
            
            start_time = time.time()
            response = requests.post(url, files=files, data=data, timeout=120)
            end_time = time.time()
            
            duration = end_time - start_time
            
            print(f"⏰ Fim: {time.strftime('%H:%M:%S')}")
            print(f"⏱️ Duração: {duration:.2f} segundos")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n✅ UPLOAD BEM-SUCEDIDO!")
                print(f"📋 Arquivo: {result.get('archivo_original', 'N/A')}")
                print(f"📄 Total linhas arquivo: {result.get('total_linhas_arquivo_original', 0)}")
                print(f"📊 Linhas processadas: {result.get('total_lineas_archivo', 0)}")
                print(f"✅ Contatos válidos: {result.get('contatos_validos', 0)}")
                print(f"❌ Contatos inválidos: {result.get('contatos_invalidos', 0)}")
                print(f"🔄 Contatos duplicados: {result.get('contatos_duplicados', 0)}")
                
                arquivo_truncado = result.get('arquivo_truncado', False)
                print(f"✂️ Arquivo truncado: {'SIM' if arquivo_truncado else 'NÃO'}")
                
                if expect_truncation:
                    if arquivo_truncado and result.get('contatos_validos', 0) == 400:
                        print("✅ Truncamento funcionou como esperado!")
                        return True
                    else:
                        print("❌ Truncamento não funcionou como esperado")
                        return False
                else:
                    if not arquivo_truncado and result.get('contatos_validos', 0) == expected_numbers:
                        print("✅ Upload completo funcionou como esperado!")
                        return True
                    else:
                        print("❌ Upload completo não funcionou como esperado")
                        return False
                
            else:
                print(f"\n❌ ERRO NO UPLOAD!")
                print(f"📄 Resposta: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        return False

def main():
    """Função principal"""
    
    success = test_system_limits()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL")
    print("=" * 60)
    
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema funcionando com limites práticos:")
        print("   - Listas até 400 registros: Processamento completo")
        print("   - Listas maiores: Truncamento automático para 400")
        print("   - Mensagem clara sobre truncamento")
        print("   - Script divisor disponível para arquivos grandes")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("⚠️ Verifique os logs acima para identificar problemas")
    
    return success

if __name__ == "__main__":
    main() 