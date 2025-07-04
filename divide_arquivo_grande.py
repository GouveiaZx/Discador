#!/usr/bin/env python3
"""
Script para dividir arquivos grandes em partes de até 150 registros
Ideal para arquivos como Slackall.txt que são muito grandes para upload único
"""

import os
import sys

def dividir_arquivo(arquivo_entrada, tamanho_parte=150):
    """
    Divide um arquivo grande em partes menores
    
    Args:
        arquivo_entrada: Caminho do arquivo a ser dividido
        tamanho_parte: Número máximo de linhas por parte (padrão: 150)
    """
    
    print(f"🔧 DIVISOR DE ARQUIVO GRANDE")
    print(f"📁 Arquivo: {arquivo_entrada}")
    print(f"📊 Tamanho por parte: {tamanho_parte} registros")
    print("=" * 60)
    
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
        return False
    
    # Ler arquivo
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except UnicodeDecodeError:
        # Tentar outras codificações
        encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        linhas = None
        for encoding in encodings:
            try:
                with open(arquivo_entrada, 'r', encoding=encoding) as f:
                    linhas = f.readlines()
                print(f"✅ Arquivo lido com codificação: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if linhas is None:
            print("❌ Não foi possível ler o arquivo com nenhuma codificação")
            return False
    
    # Limpar linhas vazias
    linhas_limpas = [linha.strip() for linha in linhas if linha.strip()]
    total_linhas = len(linhas_limpas)
    
    print(f"📄 Total de linhas válidas: {total_linhas}")
    
    if total_linhas <= tamanho_parte:
        print(f"✅ Arquivo já é pequeno o suficiente ({total_linhas} ≤ {tamanho_parte})")
        print("   Não é necessário dividir.")
        return True
    
    # Calcular número de partes
    total_partes = (total_linhas + tamanho_parte - 1) // tamanho_parte
    print(f"📦 Será dividido em {total_partes} partes")
    
    # Criar pasta de destino
    nome_base = os.path.splitext(arquivo_entrada)[0]
    pasta_destino = f"{nome_base}_partes"
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"📂 Pasta criada: {pasta_destino}")
    
    # Dividir arquivo
    arquivos_criados = []
    
    for i in range(0, total_linhas, tamanho_parte):
        parte_atual = (i // tamanho_parte) + 1
        inicio = i
        fim = min(i + tamanho_parte, total_linhas)
        
        linhas_parte = linhas_limpas[inicio:fim]
        
        nome_parte = f"{nome_base}_parte_{parte_atual:04d}.txt"
        caminho_parte = os.path.join(pasta_destino, nome_parte)
        
        with open(caminho_parte, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas_parte))
        
        arquivos_criados.append(caminho_parte)
        print(f"✅ Parte {parte_atual}/{total_partes}: {nome_parte} ({len(linhas_parte)} registros)")
    
    print("\n🎉 DIVISÃO CONCLUÍDA!")
    print(f"📂 Pasta: {pasta_destino}")
    print(f"📊 Total de partes: {len(arquivos_criados)}")
    print(f"📄 Total de registros: {total_linhas}")
    
    print("\n📋 COMO USAR:")
    print("1. Acesse a página de Upload de Listas")
    print("2. Faça upload de cada arquivo da pasta criada")
    print("3. Cada arquivo processará até 150 contatos automaticamente")
    
    print(f"\n📁 Arquivos criados:")
    for arquivo in arquivos_criados[:5]:  # Mostrar apenas primeiros 5
        nome_arquivo = os.path.basename(arquivo)
        print(f"   - {nome_arquivo}")
    
    if len(arquivos_criados) > 5:
        print(f"   ... e mais {len(arquivos_criados) - 5} arquivos")
    
    return True

def main():
    """Função principal"""
    
    if len(sys.argv) < 2:
        print("📋 USO: python divide_arquivo_grande.py <arquivo> [tamanho_parte]")
        print()
        print("Exemplos:")
        print("  python divide_arquivo_grande.py Slackall.txt")
        print("  python divide_arquivo_grande.py minha_lista.csv 150")
        print()
        print("Parâmetros:")
        print("  arquivo        - Arquivo a ser dividido")
        print("  tamanho_parte  - Registros por parte (padrão: 150)")
        return
    
    arquivo = sys.argv[1]
    tamanho = 150
    
    if len(sys.argv) >= 3:
        try:
            tamanho = int(sys.argv[2])
        except ValueError:
            print("❌ Tamanho da parte deve ser um número")
            return
    
    if tamanho < 1 or tamanho > 1000:
        print("❌ Tamanho da parte deve estar entre 1 e 1000")
        return
    
    success = dividir_arquivo(arquivo, tamanho)
    
    if success:
        print("\n✅ Divisão concluída com sucesso!")
    else:
        print("\n❌ Erro na divisão do arquivo.")

if __name__ == "__main__":
    main() 