#!/usr/bin/env python3
"""
Script para debug detalhado da campanha presione1
"""
import requests
import json

def debug_campanha_detalhado():
    print("🔍 Debug Detalhado da Campanha 1...")
    
    # URLs para testar
    urls = [
        "https://discador.onrender.com/api/v1/presione1/campanhas/1/debug-detalhado",
        "https://discador.onrender.com/api/v1/presione1/campanhas/1/debug"
    ]
    
    for url in urls:
        print(f"\n🌐 Testando: {url}")
        try:
            response = requests.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Print logs passo a passo
                if "logs_passos" in data:
                    print("\n📋 LOGS PASSO A PASSO:")
                    for step in data["logs_passos"]:
                        print(f"  {step}")
                
                # Print problemas identificados
                if "problemas_identificados" in data:
                    print("\n⚠️ PROBLEMAS IDENTIFICADOS:")
                    for problema in data["problemas_identificados"]:
                        print(f"  ❌ {problema}")
                
                # Print dados específicos
                if "passo_3_contatos_raw" in data:
                    contatos_info = data["passo_3_contatos_raw"]
                    print(f"\n📞 CONTATOS RAW: {contatos_info.get('count', 0)} encontrados")
                
                if "passo_4_contatos_validos" in data:
                    validos_info = data["passo_4_contatos_validos"]
                    print(f"✅ CONTATOS VÁLIDOS: {validos_info.get('count', 0)}")
                
                if "passo_6_numeros_discados" in data:
                    discados_info = data["passo_6_numeros_discados"]
                    print(f"📱 NÚMEROS DISCADOS: {discados_info.get('count', 0)} únicos")
                
                if "passo_7_primeiro_disponivel" in data:
                    disponivel = data["passo_7_primeiro_disponivel"]
                    if disponivel:
                        print(f"🎯 PRIMEIRO DISPONÍVEL: Posição {disponivel.get('posicao')}")
                    else:
                        print("❌ NENHUM DISPONÍVEL")
                
                break
            else:
                print(f"❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"❌ Exceção: {str(e)}")
    
    # Se nenhum debug funcionou, testar a campanha básica
    print(f"\n🏷️ Testando campanha básica...")
    try:
        response = requests.get("https://discador.onrender.com/api/v1/presione1/campanhas/1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Campaign ID: {data.get('campaign_id')}")
            print(f"Status: {data.get('activa')}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Exceção: {str(e)}")

if __name__ == "__main__":
    debug_campanha_detalhado() 