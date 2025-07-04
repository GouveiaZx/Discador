#!/usr/bin/env python3
"""
Script para dividir o arquivo Slackall.txt (671k linhas) em partes menores
Para upload no sistema de discado
"""

import os
import sys

def dividir_arquivo_slackall(arquivo_original, linhas_por_parte=300):
    """
    Divide o arquivo Slackall.txt em partes menores
    
    Args:
        arquivo_original: Caminho para o arquivo original
        linhas_por_parte: Número de linhas por parte (padrão: 1000)
    """
    
    print(f"🗂️ Dividindo arquivo: {arquivo_original}")
    print(f"📊 Linhas por parte: {linhas_por_parte}")
    
    if not os.path.exists(arquivo_original):
        print(f"❌ Arquivo não encontrado: {arquivo_original}")
        return False
    
    try:
        # Ler arquivo original
        print("📖 Lendo arquivo original...")
        with open(arquivo_original, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        total_linhas = len(linhas)
        total_partes = (total_linhas + linhas_por_parte - 1) // linhas_por_parte
        
        print(f"📄 Total de linhas: {total_linhas:,}")
        print(f"📦 Será dividido em: {total_partes} partes")
        
        # Criar diretório para as partes
        dir_partes = "slackall_partes"
        if not os.path.exists(dir_partes):
            os.makedirs(dir_partes)
            print(f"📁 Criado diretório: {dir_partes}")
        
        # Dividir em partes
        partes_criadas = []
        
        for i in range(0, total_linhas, linhas_por_parte):
            parte_num = (i // linhas_por_parte) + 1
            fim = min(i + linhas_por_parte, total_linhas)
            
            nome_parte = f"{dir_partes}/slackall_parte_{parte_num:03d}.txt"
            
            with open(nome_parte, 'w', encoding='utf-8') as f:
                for linha in linhas[i:fim]:
                    # Limpar linha (remover \r extra se houver)
                    linha_limpa = linha.strip()
                    if linha_limpa:
                        f.write(linha_limpa + '\n')
            
            linhas_parte = fim - i
            partes_criadas.append({
                'arquivo': nome_parte,
                'linhas': linhas_parte,
                'inicio': i + 1,
                'fim': fim
            })
            
            print(f"✅ Parte {parte_num:3d}/{total_partes}: {nome_parte} ({linhas_parte:,} linhas)")
        
        print(f"\n🎉 Divisão concluída!")
        print(f"📦 Total de partes criadas: {len(partes_criadas)}")
        print(f"📁 Localização: {dir_partes}/")
        
        # Criar arquivo de instruções
        criar_instrucoes(dir_partes, partes_criadas, total_linhas)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao dividir arquivo: {e}")
        return False

def criar_instrucoes(dir_partes, partes_criadas, total_linhas):
    """Cria arquivo com instruções de upload"""
    
    instrucoes = f"""🚀 INSTRUÇÕES PARA UPLOAD DAS PARTES DO SLACKALL.TXT

📊 RESUMO:
- Arquivo original: {total_linhas:,} linhas
- Total de partes: {len(partes_criadas)}
- Linhas por parte: {partes_criadas[0]['linhas']:,} (aprox.)

📋 COMO FAZER UPLOAD:

1. 🌐 Acesse: https://discador.vercel.app/
2. 👤 Faça login como admin
3. 📂 Vá em "Listas" → "Subida de Listas"
4. 📤 Faça upload de uma parte por vez:

"""
    
    for i, parte in enumerate(partes_criadas[:10]):  # Mostrar apenas primeiras 10
        instrucoes += f"   ✅ {parte['arquivo']} ({parte['linhas']:,} linhas)\n"
    
    if len(partes_criadas) > 10:
        instrucoes += f"   ... e mais {len(partes_criadas) - 10} partes\n"
    
    instrucoes += f"""
⚠️ IMPORTANTE:
- Faça upload de UMA parte por vez
- Aguarde cada upload terminar antes do próximo
- Cada parte será processada em lotes pequenos automaticamente
- O sistema está otimizado para processar até 300 registros por upload

🎯 RESULTADO ESPERADO:
- Cada upload processará todos os números da parte
- Sistema detecta automaticamente números americanos (10 dígitos)
- Tempo estimado: 30-60 segundos por parte

📞 NÚMEROS SUPORTADOS:
✅ 7542348734 (formato americano)
✅ 9564044921
✅ 9563290923
✅ etc...

🔄 PROGRESSO:
Marque aqui conforme faz upload:
"""
    
    for i, parte in enumerate(partes_criadas, 1):
        instrucoes += f"[ ] Parte {i:03d}: {os.path.basename(parte['arquivo'])}\n"
    
    instrucoes += f"""
✅ QUANDO TERMINAR:
Você terá todos os {total_linhas:,} números carregados no sistema!
"""
    
    # Salvar instruções
    arquivo_instrucoes = f"{dir_partes}/INSTRUCOES_UPLOAD.txt"
    with open(arquivo_instrucoes, 'w', encoding='utf-8') as f:
        f.write(instrucoes)
    
    print(f"📋 Instruções salvas em: {arquivo_instrucoes}")

def main():
    """Função principal"""
    
    print("🗂️ DIVISOR DE ARQUIVO SLACKALL.TXT")
    print("=" * 50)
    
    # Verificar se arquivo existe
    arquivo_original = "Slackall.txt"
    
    if not os.path.exists(arquivo_original):
        print(f"❌ Arquivo '{arquivo_original}' não encontrado no diretório atual")
        print("💡 Coloque o arquivo Slackall.txt neste diretório e execute novamente")
        return
    
    # Verificar tamanho do arquivo
    tamanho_mb = os.path.getsize(arquivo_original) / (1024 * 1024)
    print(f"📁 Arquivo encontrado: {arquivo_original}")
    print(f"📊 Tamanho: {tamanho_mb:.1f} MB")
    
    # Perguntar confirmação
    resposta = input("\n🤔 Deseja dividir o arquivo em partes de 300 linhas? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        sucesso = dividir_arquivo_slackall(arquivo_original, 300)
        
        if sucesso:
            print("\n🎉 PRONTO!")
            print("📁 Verifique a pasta 'slackall_partes'")
            print("📋 Leia o arquivo 'INSTRUCOES_UPLOAD.txt'")
            print("🚀 Comece fazendo upload das partes!")
        else:
            print("\n❌ Falha na divisão do arquivo")
    else:
        print("❌ Operação cancelada")

if __name__ == "__main__":
    main() 