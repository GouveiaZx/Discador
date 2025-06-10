#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para o Sistema de Audio Inteligente
Demonstra o funcionamento completo do sistema com exemplos praticos.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Adicionar o diretorio pai ao path para importar os modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db, inicializar_bd
from app.services.audio_integration_service import AudioIntegrationService
from app.services.audio_context_manager import AudioContextManager
from app.services.audio_engine import AudioIntelligentSystem
from app.models.audio_sistema import TipoEvento, EstadoAudio

def print_separador(titulo: str):
    """Imprime um separador visual com titulo."""
    print("\n" + "="*60)
    print(f" {titulo}")
    print("="*60)

def print_resultado(resultado: dict, titulo: str = "Resultado"):
    """Imprime um resultado de forma formatada."""
    print(f"\n{titulo}:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str))

async def teste_configuracao_inicial():
    """Testa a configuracao inicial do sistema."""
    print_separador("TESTE 1: Configuracao Inicial do Sistema")
    
    # Obter sessao do banco
    db = next(get_db())
    
    try:
        # Inicializar servico de integracao
        integration_service = AudioIntegrationService(db)
        
        # Configurar sistema inicial
        print("Configurando sistema inicial...")
        resultado = await integration_service.setup_contextos_padrao()
        print_resultado(resultado, "Configuracao Inicial")
        
        # Listar contextos disponiveis
        context_manager = AudioContextManager(db)
        contextos = context_manager.listar_contextos()
        
        print(f"\nContextos disponiveis ({len(contextos)}):")
        for contexto in contextos:
            print(f"- {contexto.nome}: {contexto.descricao}")
        
        # Listar templates
        templates = context_manager.listar_templates()
        print(f"\nTemplates disponiveis ({len(templates)}):")
        for template in templates:
            print(f"- {template.nome} ({template.categoria}): {template.descricao}")
        
        return True
        
    except Exception as e:
        print(f"Erro na configuracao inicial: {str(e)}")
        return False
    finally:
        db.close()

async def teste_criacao_contexto():
    """Testa a criacao de um contexto personalizado."""
    print_separador("TESTE 2: Criacao de Contexto Personalizado")
    
    db = next(get_db())
    
    try:
        context_manager = AudioContextManager(db)
        
        # Criar contexto personalizado
        print("Criando contexto personalizado...")
        contexto = context_manager.criar_contexto_presione1(
            nome="Teste Campanha Demo",
            audio_principal_url="https://example.com/demo_principal.wav",
            audio_voicemail_url="https://example.com/demo_voicemail.wav",
            timeout_dtmf=15,
            detectar_voicemail=True,
            tentativas_maximas=2
        )
        
        print(f"Contexto criado: {contexto.nome} (ID: {contexto.id})")
        print(f"Regras criadas: {len(contexto.regras)}")
        
        # Listar regras do contexto
        print("\nRegras do contexto:")
        for regra in contexto.regras:
            print(f"- {regra.nome}: {regra.estado_origem.value} → {regra.estado_destino.value}")
        
        return contexto.id
        
    except Exception as e:
        print(f"Erro na criacao do contexto: {str(e)}")
        return None
    finally:
        db.close()

async def teste_chamada_completa():
    """Testa uma chamada completa com o sistema de audio inteligente."""
    print_separador("TESTE 3: Simulacao de Chamada Completa")
    
    db = next(get_db())
    
    try:
        integration_service = AudioIntegrationService(db)
        
        # Iniciar chamada
        print("Iniciando chamada com audio inteligente...")
        resultado_chamada = await integration_service.iniciar_chamada_com_audio_inteligente(
            numero_destino="+5511999999999",
            campana_id=1,
            contexto_audio_nome="Presione 1 Padrao",
            cli="+5511888888888",
            configuracoes_audio={
                "timeout_dtmf": 12,
                "detectar_voicemail": True
            }
        )
        
        print_resultado(resultado_chamada, "Chamada Iniciada")
        
        if not resultado_chamada.get("sucesso"):
            print("Falha ao iniciar chamada!")
            return False
        
        llamada_id = resultado_chamada["llamada_id"]
        
        # Simular sequencia de eventos
        eventos_simulados = [
            {
                "tipo": "Dial",
                "dados": {},
                "descricao": "Telefone comecou a tocar"
            },
            {
                "tipo": "DialEnd", 
                "dados": {"DialTime": 8},
                "descricao": "Chamada foi atendida"
            },
            {
                "tipo": "DTMF",
                "dados": {"Digit": "1"},
                "descricao": "Cliente pressionou tecla 1"
            }
        ]
        
        print(f"\nSimulando eventos para chamada {llamada_id}:")
        
        for i, evento in enumerate(eventos_simulados, 1):
            print(f"\n--- Evento {i}: {evento['descricao']} ---")
            
            # Processar evento
            resultado_evento = integration_service.processar_evento_asterisk(
                llamada_id=llamada_id,
                tipo_evento=evento["tipo"],
                dados_evento=evento["dados"]
            )
            
            print_resultado(resultado_evento, f"Processamento Evento {i}")
            
            # Obter status atualizado
            status = integration_service.obter_status_completo_llamada(llamada_id)
            if status and status.get("audio_inteligente"):
                audio_status = status["audio_inteligente"]
                print(f"Estado atual: {audio_status['estado_atual']}")
                print(f"Tempo no estado: {audio_status['tempo_no_estado_segundos']}s")
            
            # Pequena pausa para simular tempo real
            await asyncio.sleep(1)
        
        # Status final
        print("\n--- Status Final da Chamada ---")
        status_final = integration_service.obter_status_completo_llamada(llamada_id)
        print_resultado(status_final, "Status Final")
        
        # Finalizar chamada
        print("\n--- Finalizando Chamada ---")
        resultado_finalizacao = integration_service.finalizar_llamada_audio(
            llamada_id=llamada_id,
            resultado="contestada",
            motivo_finalizacao="Cliente conectado via DTMF"
        )
        print_resultado(resultado_finalizacao, "Finalizacao")
        
        return True
        
    except Exception as e:
        print(f"Erro na simulacao da chamada: {str(e)}")
        return False
    finally:
        db.close()

async def teste_motor_regras():
    """Testa o motor de regras com diferentes cenarios."""
    print_separador("TESTE 4: Motor de Regras - Cenarios Diversos")
    
    db = next(get_db())
    
    try:
        integration_service = AudioIntegrationService(db)
        
        # Cenario 1: Timeout DTMF
        print("Cenario 1: Timeout aguardando DTMF")
        resultado1 = await integration_service.iniciar_chamada_com_audio_inteligente(
            numero_destino="+5511888888888",
            campana_id=1,
            contexto_audio_nome="Presione 1 Padrao"
        )
        
        if resultado1.get("sucesso"):
            llamada_id1 = resultado1["llamada_id"]
            
            # Simular atendimento e timeout
            integration_service.processar_evento_asterisk(llamada_id1, "DialEnd", {"DialTime": 3})
            resultado_timeout = integration_service.processar_evento_asterisk(
                llamada_id1, "DTMFTimeout", {}
            )
            print_resultado(resultado_timeout, "Resultado Timeout DTMF")
        
        # Cenario 2: Deteccao de Voicemail
        print("\nCenario 2: Deteccao de Voicemail")
        resultado2 = await integration_service.iniciar_chamada_com_audio_inteligente(
            numero_destino="+5511777777777",
            campana_id=1,
            contexto_audio_nome="Presione 1 Padrao"
        )
        
        if resultado2.get("sucesso"):
            llamada_id2 = resultado2["llamada_id"]
            
            # Simular deteccao de voicemail
            integration_service.processar_evento_asterisk(llamada_id2, "DialEnd", {})
            resultado_voicemail = integration_service.processar_evento_asterisk(
                llamada_id2, "VoicemailDetected", {"Confidence": 0.95}
            )
            print_resultado(resultado_voicemail, "Resultado Deteccao Voicemail")
        
        # Cenario 3: Erro no sistema
        print("\nCenario 3: Erro no Sistema")
        resultado3 = await integration_service.iniciar_chamada_com_audio_inteligente(
            numero_destino="+5511666666666",
            campana_id=1,
            contexto_audio_nome="Presione 1 Padrao"
        )
        
        if resultado3.get("sucesso"):
            llamada_id3 = resultado3["llamada_id"]
            
            # Simular erro
            resultado_erro = integration_service.processar_evento_asterisk(
                llamada_id3, "Error", {"ErrorCode": "NETWORK_FAILURE"}
            )
            print_resultado(resultado_erro, "Resultado Erro Sistema")
        
        return True
        
    except Exception as e:
        print(f"Erro no teste do motor de regras: {str(e)}")
        return False
    finally:
        db.close()

async def teste_performance():
    """Testa a performance do sistema com multiplas chamadas."""
    print_separador("TESTE 5: Performance - Multiplas Chamadas")
    
    db = next(get_db())
    
    try:
        integration_service = AudioIntegrationService(db)
        
        num_chamadas = 5
        print(f"Iniciando {num_chamadas} chamadas simultaneas...")
        
        inicio = datetime.now()
        
        # Iniciar multiplas chamadas
        chamadas = []
        for i in range(num_chamadas):
            resultado = await integration_service.iniciar_chamada_com_audio_inteligente(
                numero_destino=f"+551199999{i:04d}",
                campana_id=1,
                contexto_audio_nome="Presione 1 Padrao"
            )
            
            if resultado.get("sucesso"):
                chamadas.append(resultado["llamada_id"])
                print(f"Chamada {i+1} iniciada: ID {resultado['llamada_id']}")
        
        # Processar eventos para todas as chamadas
        for llamada_id in chamadas:
            integration_service.processar_evento_asterisk(llamada_id, "DialEnd", {})
            integration_service.processar_evento_asterisk(
                llamada_id, "DTMF", {"Digit": "1"}
            )
        
        fim = datetime.now()
        duracao = (fim - inicio).total_seconds()
        
        print(f"\nPerformance:")
        print(f"- Chamadas processadas: {len(chamadas)}")
        print(f"- Tempo total: {duracao:.2f}s")
        print(f"- Media por chamada: {duracao/len(chamadas):.2f}s")
        
        return True
        
    except Exception as e:
        print(f"Erro no teste de performance: {str(e)}")
        return False
    finally:
        db.close()

async def main():
    """Funcao principal que executa todos os testes."""
    print_separador("SISTEMA DE AUDIO INTELIGENTE - TESTES COMPLETOS")
    print("Iniciando bateria de testes do sistema...")
    
    # Inicializar banco de dados
    try:
        print("Inicializando banco de dados...")
        inicializar_bd()
        print("Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar banco: {str(e)}")
        return
    
    # Lista de testes
    testes = [
        ("Configuracao Inicial", teste_configuracao_inicial),
        ("Criacao de Contexto", teste_criacao_contexto),
        ("Chamada Completa", teste_chamada_completa),
        ("Motor de Regras", teste_motor_regras),
        ("Performance", teste_performance)
    ]
    
    resultados = []
    
    # Executar testes
    for nome, teste_func in testes:
        try:
            print(f"\nExecutando: {nome}...")
            resultado = await teste_func()
            resultados.append((nome, resultado))
            
            if resultado:
                print(f"✅ {nome}: SUCESSO")
            else:
                print(f"❌ {nome}: FALHA")
                
        except Exception as e:
            print(f"❌ {nome}: ERRO - {str(e)}")
            resultados.append((nome, False))
    
    # Resumo final
    print_separador("RESUMO DOS TESTES")
    
    sucessos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    print(f"Testes executados: {total}")
    print(f"Sucessos: {sucessos}")
    print(f"Falhas: {total - sucessos}")
    print(f"Taxa de sucesso: {(sucessos/total)*100:.1f}%")
    
    print("\nDetalhes:")
    for nome, resultado in resultados:
        status = "✅ SUCESSO" if resultado else "❌ FALHA"
        print(f"- {nome}: {status}")
    
    if sucessos == total:
        print("\n🎉 Todos os testes passaram! Sistema funcionando corretamente.")
    else:
        print(f"\n⚠️  {total - sucessos} teste(s) falharam. Verifique os logs acima.")
    
    print_separador("TESTES CONCLUIDOS")

if __name__ == "__main__":
    # Executar testes
    asyncio.run(main()) 