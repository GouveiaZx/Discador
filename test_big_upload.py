#!/usr/bin/env python3
"""
Script para testar upload de lista grande (simulando Slackall.txt)
"""

import requests
import time

def create_test_file(num_lines=1000):
    """Criar arquivo de teste com números americanos"""
    print(f"🔧 Criando arquivo de teste com {num_lines} números...")
    
    # Números base americanos de 10 dígitos
    base_numbers = [
        "7542348734", "9564044921", "9563290923", "2813903426", "8136453764",
        "5234567890", "3456789012", "7890123456", "2345678901", "6789012345"
    ]
    
    lines = []
    for i in range(num_lines):
        # Usar número base e adicionar variação no final
        base_idx = i % len(base_numbers)
        base_num = base_numbers[base_idx]
        # Modificar últimos dígitos para criar números únicos
        variation = f"{i:04d}"[-4:]  # Últimos 4 dígitos do índice
        number = base_num[:-4] + variation
        lines.append(number)
    
    filename = f"test_lista_grande_{num_lines}.txt"
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Arquivo criado: {filename}")
    return filename

def test_upload_big_file(filename, num_lines):
    """Testar upload de arquivo grande"""
    
    print(f"\n🚀 TESTE UPLOAD LISTA GRANDE")
    print(f"📁 Arquivo: {filename}")
    print(f"📊 Números: {num_lines}")
    print("=" * 60)
    
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
            
            print(f"📤 Enviando {num_lines} números...")
            print(f"🔗 URL: {url}")
            print(f"⏰ Início: {time.strftime('%H:%M:%S')}")
            
            start_time = time.time()
            
            # Timeout maior para arquivos grandes
            timeout = 300 if num_lines > 500 else 120  # 5 min para grandes, 2 min para pequenos
            
            response = requests.post(url, files=files, data=data, timeout=timeout)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏰ Fim: {time.strftime('%H:%M:%S')}")
            print(f"⏱️ Duração: {duration:.2f} segundos")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n✅ UPLOAD BEM-SUCEDIDO!")
                print(f"📋 Arquivo original: {result.get('archivo_original', 'N/A')}")
                print(f"📄 Total linhas: {result.get('total_lineas_archivo', 0)}")
                print(f"✅ Contatos válidos: {result.get('contatos_validos', 0)}")
                print(f"❌ Contatos inválidos: {result.get('contatos_invalidos', 0)}")
                print(f"🔄 Contatos duplicados: {result.get('contatos_duplicados', 0)}")
                print(f"📦 Lotes processados: {result.get('lotes_processados', 'N/A')}")
                print(f"📊 Tamanho do lote: {result.get('lote_size_usado', 'N/A')}")
                print(f"🎯 Taxa de sucesso: {(result.get('contatos_validos', 0) / max(result.get('total_lineas_archivo', 1), 1)) * 100:.1f}%")
                
                if result.get('errores'):
                    print(f"\n⚠️ Primeiros erros:")
                    for erro in result.get('errores', []):
                        print(f"   - {erro}")
                
                print(f"\n💬 Mensagem: {result.get('mensaje', 'N/A')}")
                
                return True
                
            else:
                print(f"\n❌ ERRO NO UPLOAD!")
                print(f"📄 Resposta: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT! O upload demorou mais que {timeout} segundos")
        return False
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        return False

def main():
    """Função principal"""
    
    print("🎯 TESTE DE UPLOAD DE LISTAS GRANDES")
    print("=" * 60)
    
    # Testes progressivos
    test_cases = [
        {"lines": 50, "desc": "Lista pequena"},
        {"lines": 200, "desc": "Lista média"},
        {"lines": 1000, "desc": "Lista grande"},
        {"lines": 5000, "desc": "Lista muito grande (simulando Slackall parcial)"}
    ]
    
    results = []
    
    for test_case in test_cases:
        lines = test_case["lines"]
        desc = test_case["desc"]
        
        print(f"\n📋 TESTE: {desc} ({lines} números)")
        print("-" * 40)
        
        # Criar arquivo de teste
        filename = create_test_file(lines)
        
        # Testar upload
        success = test_upload_big_file(filename, lines)
        
        results.append({
            "desc": desc,
            "lines": lines,
            "success": success
        })
        
        # Limpar arquivo de teste
        import os
        try:
            os.remove(filename)
            print(f"🗑️ Arquivo {filename} removido")
        except:
            pass
        
        if not success:
            print(f"❌ Teste falhou para {desc}. Parando aqui.")
            break
        
        print(f"✅ Teste {desc} concluído com sucesso!")
        
        # Pausa entre testes
        if lines < 5000:
            print("⏳ Aguardando 5 segundos...")
            time.sleep(5)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['desc']}: {result['lines']} números - {'SUCESSO' if result['success'] else 'FALHOU'}")
    
    total_success = sum(1 for r in results if r["success"])
    print(f"\n🎯 RESULTADO: {total_success}/{len(results)} testes bem-sucedidos")
    
    if total_success == len(results):
        print("🎉 TODOS OS TESTES PASSARAM! Sistema otimizado para listas grandes!")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main() 