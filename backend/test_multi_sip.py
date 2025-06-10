#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para demonstrar o Sistema Multi-SIP
Testa as funcionalidades principais sem necessidade de banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from typing import Dict, Any
import json

# Simulacao dos modelos para teste
class MockProvedorSip:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.nome = kwargs.get('nome', 'Provedor Teste')
        self.codigo = kwargs.get('codigo', 'TEST_01')
        self.tipo_provedor = kwargs.get('tipo_provedor', 'twilio')
        self.servidor_sip = kwargs.get('servidor_sip', 'sip.test.com')
        self.porta_sip = kwargs.get('porta_sip', 5060)
        self.usuario_sip = kwargs.get('usuario_sip', 'usuario_teste')
        self.senha_sip = kwargs.get('senha_sip', 'senha_teste')
        self.prioridade = kwargs.get('prioridade', 100)
        self.latencia_media_ms = kwargs.get('latencia_media_ms', 50.0)
        self.taxa_sucesso = kwargs.get('taxa_sucesso', 98.5)
        self.custo_base_por_minuto = kwargs.get('custo_base_por_minuto', 0.015)
        self.status = kwargs.get('status', 'ativo')

# Algoritmo de selecao inteligente
class MultiSipAlgorithm:
    """Algoritmos de selecao de provedores Multi-SIP"""
    
    @staticmethod
    def calcular_custo_estimado(provedor: MockProvedorSip, numero_destino: str, duracao_segundos: int = 60) -> float:
        """Calcula custo estimado baseado no provedor e destino"""
        # Regras de tarifacao por prefixo
        numero_limpo = ''.join(filter(str.isdigit, numero_destino))
        
        # Tarifas simuladas por pais/regiao
        tarifas = {
            '55': {'custo_por_minuto': 0.008, 'taxa_conexao': 0.001},  # Brasil
            '1': {'custo_por_minuto': 0.012, 'taxa_conexao': 0.002},   # EUA/Canada
            '49': {'custo_por_minuto': 0.015, 'taxa_conexao': 0.003},  # Alemanha
        }
        
        # Encontrar tarifa por prefixo
        tarifa_aplicada = None
        for prefixo, tarifa in tarifas.items():
            if numero_limpo.startswith(prefixo):
                tarifa_aplicada = tarifa
                break
        
        if not tarifa_aplicada:
            # Usar custo base do provedor
            custo_por_minuto = provedor.custo_base_por_minuto
            taxa_conexao = 0.0
        else:
            custo_por_minuto = tarifa_aplicada['custo_por_minuto']
            taxa_conexao = tarifa_aplicada['taxa_conexao']
        
        minutos = duracao_segundos / 60
        custo_total = (custo_por_minuto * minutos) + taxa_conexao
        
        return round(custo_total, 4)
    
    @staticmethod
    def selecionar_menor_custo(provedores: list, numero_destino: str) -> Dict[str, Any]:
        """Algoritmo: Menor Custo"""
        melhor_provedor = None
        menor_custo = float('inf')
        
        for provedor in provedores:
            custo = MultiSipAlgorithm.calcular_custo_estimado(provedor, numero_destino)
            if custo < menor_custo:
                menor_custo = custo
                melhor_provedor = provedor
        
        return {
            'provedor': melhor_provedor,
            'score': menor_custo,
            'justificativa': f'Selecionado por menor custo: ${menor_custo:.4f}',
            'metodo': 'MENOR_CUSTO'
        }
    
    @staticmethod
    def selecionar_melhor_qualidade(provedores: list, numero_destino: str) -> Dict[str, Any]:
        """Algoritmo: Melhor Qualidade"""
        melhor_provedor = None
        melhor_score = -1
        
        for provedor in provedores:
            # Score baseado em taxa de sucesso e latencia
            score_qualidade = (provedor.taxa_sucesso / 100) - (provedor.latencia_media_ms / 1000)
            if score_qualidade > melhor_score:
                melhor_score = score_qualidade
                melhor_provedor = provedor
        
        return {
            'provedor': melhor_provedor,
            'score': melhor_score,
            'justificativa': f'Selecionado por qualidade: {melhor_provedor.taxa_sucesso}% sucesso, {melhor_provedor.latencia_media_ms}ms latencia',
            'metodo': 'MELHOR_QUALIDADE'
        }
    
    @staticmethod
    def selecionar_inteligente(provedores: list, numero_destino: str) -> Dict[str, Any]:
        """Algoritmo: Inteligente (40% custo + 40% qualidade + 20% latencia)"""
        melhor_provedor = None
        melhor_score = -1
        melhor_justificativa = ""
        
        # Normalizar valores para comparacao
        custos = [MultiSipAlgorithm.calcular_custo_estimado(p, numero_destino) for p in provedores]
        latencias = [p.latencia_media_ms for p in provedores]
        taxas_sucesso = [p.taxa_sucesso for p in provedores]
        
        min_custo, max_custo = min(custos), max(custos)
        min_latencia, max_latencia = min(latencias), max(latencias)
        min_taxa, max_taxa = min(taxas_sucesso), max(taxas_sucesso)
        
        for i, provedor in enumerate(provedores):
            # Normalizar custo (menor e melhor)
            score_custo = 1 - ((custos[i] - min_custo) / (max_custo - min_custo + 0.001))
            
            # Normalizar qualidade (maior e melhor)
            score_qualidade = (taxas_sucesso[i] - min_taxa) / (max_taxa - min_taxa + 0.001)
            
            # Normalizar latencia (menor e melhor)
            score_latencia = 1 - ((latencias[i] - min_latencia) / (max_latencia - min_latencia + 0.001))
            
            # Score final ponderado
            score_final = (0.4 * score_custo) + (0.4 * score_qualidade) + (0.2 * score_latencia)
            
            if score_final > melhor_score:
                melhor_score = score_final
                melhor_provedor = provedor
                melhor_justificativa = f'Score inteligente: {score_final:.3f} (Custo: ${custos[i]:.4f}, Qualidade: {taxas_sucesso[i]}%, Latencia: {latencias[i]}ms)'
        
        return {
            'provedor': melhor_provedor,
            'score': melhor_score,
            'justificativa': melhor_justificativa,
            'metodo': 'INTELIGENTE'
        }

def criar_provedores_exemplo():
    """Cria provedores de exemplo para teste"""
    return [
        MockProvedorSip(
            id=1,
            nome="Twilio Brasil",
            codigo="TWILIO_BR",
            tipo_provedor="twilio",
            servidor_sip="sip.twilio.com",
            prioridade=1,
            latencia_media_ms=45.2,
            taxa_sucesso=99.1,
            custo_base_por_minuto=0.018
        ),
        MockProvedorSip(
            id=2,
            nome="GoTrunk Premium",
            codigo="GOTTRUNK_PREM",
            tipo_provedor="gottrunk",
            servidor_sip="sip.gottrunk.com",
            prioridade=2,
            latencia_media_ms=62.8,
            taxa_sucesso=97.5,
            custo_base_por_minuto=0.012
        ),
        MockProvedorSip(
            id=3,
            nome="SIP Local",
            codigo="SIP_LOCAL",
            tipo_provedor="asterisk_peer",
            servidor_sip="192.168.1.100",
            prioridade=3,
            latencia_media_ms=15.1,
            taxa_sucesso=95.8,
            custo_base_por_minuto=0.006
        ),
        MockProvedorSip(
            id=4,
            nome="Provedor Internacional",
            codigo="INTL_PROVIDER",
            tipo_provedor="sip_trunk",
            servidor_sip="sip.international.com",
            prioridade=4,
            latencia_media_ms=120.5,
            taxa_sucesso=94.2,
            custo_base_por_minuto=0.025
        )
    ]

def testar_selecao_provedor():
    """Testa os algoritmos de selecao"""
    print("🔌 SISTEMA MULTI-SIP - DEMONSTRACAO COMPLETA")
    print("=" * 60)
    
    # Criar provedores
    provedores = criar_provedores_exemplo()
    
    print(f"\n📋 PROVEDORES CADASTRADOS ({len(provedores)}):")
    print("-" * 60)
    for p in provedores:
        print(f"• {p.nome} ({p.codigo})")
        print(f"  ├─ Tipo: {p.tipo_provedor}")
        print(f"  ├─ Servidor: {p.servidor_sip}")
        print(f"  ├─ Latencia: {p.latencia_media_ms}ms")
        print(f"  ├─ Taxa Sucesso: {p.taxa_sucesso}%")
        print(f"  └─ Custo Base: ${p.custo_base_por_minuto:.4f}/min")
        print()
    
    # Numeros de teste
    numeros_teste = [
        ("5511999887766", "Brasil - Sao Paulo (Celular)"),
        ("12125551234", "EUA - Nova York"),
        ("4930123456789", "Alemanha - Berlim"),
        ("85012345678", "Numero Internacional Generico")
    ]
    
    print("\n🎯 TESTES DE SELECAO:")
    print("=" * 60)
    
    for numero, descricao in numeros_teste:
        print(f"\n📞 DESTINO: {descricao}")
        print(f"   Numero: {numero}")
        print("-" * 40)
        
        # Testar cada algoritmo
        algoritmos = [
            ("MENOR_CUSTO", MultiSipAlgorithm.selecionar_menor_custo),
            ("MELHOR_QUALIDADE", MultiSipAlgorithm.selecionar_melhor_qualidade),
            ("INTELIGENTE", MultiSipAlgorithm.selecionar_inteligente)
        ]
        
        for nome_algoritmo, funcao_algoritmo in algoritmos:
            resultado = funcao_algoritmo(provedores, numero)
            custo = MultiSipAlgorithm.calcular_custo_estimado(resultado['provedor'], numero)
            
            print(f"\n🧠 {nome_algoritmo}:")
            print(f"   ✅ Provedor: {resultado['provedor'].nome}")
            print(f"   💰 Custo: ${custo:.4f}")
            print(f"   📊 Score: {resultado['score']:.4f}")
            print(f"   💡 Justificativa: {resultado['justificativa']}")

def testar_roteamento_geografico():
    """Testa roteamento baseado em geografia"""
    print("\n\n🌍 TESTE DE ROTEAMENTO GEOGRAFICO:")
    print("=" * 60)
    
    # Regras de roteamento por regiao
    regras_roteamento = {
        '55': 'Brasil - Preferir provedores locais',
        '1': 'America do Norte - Usar Twilio',
        '49': 'Europa - Usar provedores internacionais',
        '86': 'Asia - Routing especial necessario'
    }
    
    provedores = criar_provedores_exemplo()
    
    for prefixo, descricao in regras_roteamento.items():
        numero_exemplo = prefixo + "123456789"
        print(f"\n📍 {descricao}")
        print(f"   Numero exemplo: {numero_exemplo}")
        
        # Aplicar logica de roteamento
        resultado = MultiSipAlgorithm.selecionar_inteligente(provedores, numero_exemplo)
        custo = MultiSipAlgorithm.calcular_custo_estimado(resultado['provedor'], numero_exemplo)
        
        print(f"   🎯 Provedor selecionado: {resultado['provedor'].nome}")
        print(f"   💰 Custo estimado: ${custo:.4f}")

def demonstrar_falhas_e_failover():
    """Demonstra tratamento de falhas e failover"""
    print("\n\n⚠️  TESTE DE FAILOVER E RECUPERACAO:")
    print("=" * 60)
    
    provedores = criar_provedores_exemplo()
    
    # Simular falha no provedor principal
    print("\n🔴 SIMULANDO FALHA:")
    provedores[0].status = 'erro'
    provedores[0].taxa_sucesso = 0.0
    print(f"   Provedor '{provedores[0].nome}' indisponivel")
    
    # Filtrar apenas provedores disponiveis
    provedores_disponiveis = [p for p in provedores if p.status == 'ativo']
    
    print(f"\n✅ PROVEDORES DISPONIVEIS ({len(provedores_disponiveis)}):")
    for p in provedores_disponiveis:
        print(f"   • {p.nome} - Status: {p.status}")
    
    # Selecao com failover
    numero_teste = "5511999887766"
    resultado = MultiSipAlgorithm.selecionar_inteligente(provedores_disponiveis, numero_teste)
    
    print(f"\n🚀 FAILOVER AUTOMATICO:")
    print(f"   ✅ Provedor backup: {resultado['provedor'].nome}")
    print(f"   📊 Score: {resultado['score']:.4f}")
    print(f"   💡 Justificativa: {resultado['justificativa']}")

def mostrar_estatisticas():
    """Mostra estatisticas simuladas do sistema"""
    print("\n\n📊 ESTATISTICAS DO SISTEMA:")
    print("=" * 60)
    
    estatisticas = {
        'Total de provedores': 4,
        'Provedores ativos': 3,
        'Chamadas hoje': 1247,
        'Taxa de sucesso geral': '97.8%',
        'Custo medio por minuto': '$0.0135',
        'Latencia media': '68.2ms',
        'Economia vs. provedor unico': '23.4%'
    }
    
    for metrica, valor in estatisticas.items():
        print(f"   {metrica:.<30} {valor}")

def main():
    """Funcao principal de demonstracao"""
    try:
        print("🚀 INICIANDO DEMONSTRACAO DO SISTEMA MULTI-SIP...")
        
        # Executar todos os testes
        testar_selecao_provedor()
        testar_roteamento_geografico()
        demonstrar_falhas_e_failover()
        mostrar_estatisticas()
        
        print("\n\n✅ DEMONSTRACAO CONCLUIDA COM SUCESSO!")
        print("\n🔌 O Sistema Multi-SIP esta pronto para:")
        print("   • Integracao com multiplos provedores VoIP")
        print("   • Selecao inteligente baseada em custo e qualidade")
        print("   • Roteamento geografico otimizado")
        print("   • Failover automatico em caso de falhas")
        print("   • Monitoramento em tempo real")
        print("   • Integracao completa com Asterisk via AGI")
        
        print(f"\n📚 Para instalacao completa, consulte:")
        print(f"   backend/docs/MULTI_SIP_INSTALL.md")
        
    except Exception as e:
        print(f"❌ Erro durante demonstracao: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)

print("🔌 SISTEMA MULTI-SIP - DEMONSTRACAO")
print("Teste basico funcionando!") 