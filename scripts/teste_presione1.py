#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste funcional para o sistema de discado preditivo "Presione 1".

Este script demonstra o uso completo da API do Presione 1:
1. Criar uma lista de números de teste
2. Criar campanha Presione 1
3. Iniciar campanha
4. Monitorar progresso
5. Pausar/retomar
6. Obter estatísticas
7. Parar campanha

Uso: python teste_presione1.py
"""

import asyncio
import requests
import json
import time
from typing import Dict, Any
from datetime import datetime


class TestPresione1:
    """Classe para testes funcionais do sistema Presione 1."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.lista_id = None
        self.campana_id = None
        
    def print_section(self, title: str):
        """Imprime seção formatada."""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)
    
    def print_step(self, step: str):
        """Imprime passo do teste."""
        print(f"\n🔸 {step}")
    
    def print_success(self, message: str):
        """Imprime mensagem de sucesso."""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Imprime mensagem de erro."""
        print(f"❌ {message}")
    
    def print_info(self, data: Dict[Any, Any], title: str = "Resposta"):
        """Imprime dados formatados."""
        print(f"\n📋 {title}:")
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Faz requisição HTTP."""
        url = f"{self.api_url}{endpoint}"
        print(f"\n🌐 {method.upper()} {url}")
        
        if 'json' in kwargs:
            print(f"📤 Body: {json.dumps(kwargs['json'], indent=2, ensure_ascii=False)}")
        
        response = self.session.request(method, url, **kwargs)
        
        print(f"📥 Status: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                response_data = response.json()
                if response.status_code < 400:
                    self.print_success("Requisição bem-sucedida")
                else:
                    self.print_error("Erro na requisição")
                self.print_info(response_data)
                return response
            except json.JSONDecodeError:
                pass
        
        if response.status_code >= 400:
            self.print_error(f"Erro HTTP {response.status_code}: {response.text}")
        
        return response
    
    def test_1_criar_lista_teste(self):
        """Teste 1: Criar lista de números para teste."""
        self.print_section("TESTE 1: CRIAR LISTA DE NÚMEROS")
        
        self.print_step("Criando lista de teste...")
        
        lista_data = {
            "nombre": f"Lista Teste Presione 1 - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "descripcion": "Lista criada automaticamente para testes do sistema Presione 1"
        }
        
        response = self.make_request("POST", "/listas-llamadas", json=lista_data)
        
        if response.status_code == 200:
            self.lista_id = response.json()["id"]
            self.print_success(f"Lista criada com ID: {self.lista_id}")
            
            # Adicionar números de teste
            self.print_step("Adicionando números de teste...")
            
            numeros_teste = [
                "+5491122334455",
                "+5491122334456", 
                "+5491122334457",
                "+5491122334458",
                "+5491122334459"
            ]
            
            for numero in numeros_teste:
                numero_data = {
                    "numero": numero,
                    "nombre": f"Teste {numero[-4:]}",
                    "empresa": "Empresa Teste"
                }
                
                response = self.make_request(
                    "POST", 
                    f"/listas-llamadas/{self.lista_id}/numeros",
                    json=numero_data
                )
                
                if response.status_code == 200:
                    print(f"  ✅ Número {numero} adicionado")
                else:
                    print(f"  ❌ Erro ao adicionar {numero}")
            
            return True
        else:
            self.print_error("Falha ao criar lista")
            return False
    
    def test_2_criar_campana(self):
        """Teste 2: Criar campanha Presione 1."""
        self.print_section("TESTE 2: CRIAR CAMPANHA PRESIONE 1")
        
        if not self.lista_id:
            self.print_error("Lista não criada. Execute test_1_criar_lista_teste() primeiro")
            return False
        
        self.print_step("Criando campanha...")
        
        campana_data = {
            "nombre": f"Campanha Teste - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "descripcion": "Campanha de teste do sistema Presione 1",
            "lista_llamadas_id": self.lista_id,
            "mensaje_audio_url": "/sounds/teste_presione1.wav",
            "timeout_presione1": 10,
            "extension_transferencia": "100",
            "llamadas_simultaneas": 2,
            "tiempo_entre_llamadas": 3,
            "notas": "Campanha criada automaticamente para testes"
        }
        
        response = self.make_request("POST", "/presione1/campanhas", json=campana_data)
        
        if response.status_code == 200:
            self.campana_id = response.json()["id"]
            self.print_success(f"Campanha criada com ID: {self.campana_id}")
            return True
        else:
            self.print_error("Falha ao criar campanha")
            return False
    
    def test_3_listar_campanhas(self):
        """Teste 3: Listar campanhas."""
        self.print_section("TESTE 3: LISTAR CAMPANHAS")
        
        self.print_step("Listando todas as campanhas...")
        response = self.make_request("GET", "/presione1/campanhas")
        
        if response.status_code == 200:
            campanhas = response.json()
            self.print_success(f"Encontradas {len(campanhas)} campanhas")
            
            # Listar apenas ativas
            self.print_step("Listando apenas campanhas ativas...")
            response = self.make_request("GET", "/presione1/campanhas?apenas_ativas=true")
            
            if response.status_code == 200:
                ativas = response.json()
                self.print_success(f"Encontradas {len(ativas)} campanhas ativas")
                return True
        
        return False
    
    def test_4_obter_campana(self):
        """Teste 4: Obter detalhes da campanha."""
        self.print_section("TESTE 4: OBTER DETALHES DA CAMPANHA")
        
        if not self.campana_id:
            self.print_error("Campanha não criada")
            return False
        
        self.print_step(f"Obtendo detalhes da campanha {self.campana_id}...")
        
        response = self.make_request("GET", f"/presione1/campanhas/{self.campana_id}")
        
        if response.status_code == 200:
            self.print_success("Detalhes obtidos com sucesso")
            return True
        else:
            return False
    
    def test_5_iniciar_campana(self):
        """Teste 5: Iniciar campanha."""
        self.print_section("TESTE 5: INICIAR CAMPANHA")
        
        if not self.campana_id:
            self.print_error("Campanha não criada")
            return False
        
        self.print_step("Iniciando campanha...")
        
        iniciar_data = {
            "campana_id": self.campana_id,
            "usuario_id": "teste_automatico"
        }
        
        response = self.make_request(
            "POST", 
            f"/presione1/campanhas/{self.campana_id}/iniciar",
            json=iniciar_data
        )
        
        if response.status_code == 200:
            self.print_success("Campanha iniciada com sucesso")
            
            # Aguardar um pouco para o sistema processar
            self.print_step("Aguardando sistema processar...")
            time.sleep(2)
            
            return True
        else:
            return False
    
    def test_6_monitorar_campana(self):
        """Teste 6: Monitorar campanha."""
        self.print_section("TESTE 6: MONITORAR CAMPANHA")
        
        if not self.campana_id:
            self.print_error("Campanha não criada")
            return False
        
        # Estatísticas
        self.print_step("Obtendo estatísticas...")
        response = self.make_request("GET", f"/presione1/campanhas/{self.campana_id}/estadisticas")
        
        if response.status_code != 200:
            return False
        
        # Monitor em tempo real
        self.print_step("Obtendo monitoramento em tempo real...")
        response = self.make_request("GET", f"/presione1/campanhas/{self.campana_id}/monitor")
        
        if response.status_code != 200:
            return False
        
        # Próximo número
        self.print_step("Verificando próximo número...")
        response = self.make_request("GET", f"/presione1/campanhas/{self.campana_id}/proximo-numero")
        
        if response.status_code == 200:
            self.print_success("Monitoramento funcionando")
            return True
        
        return False
    
    def test_7_pausar_retomar(self):
        """Teste 7: Pausar e retomar campanha."""
        self.print_section("TESTE 7: PAUSAR E RETOMAR CAMPANHA")
        
        if not self.campana_id:
            self.print_error("Campanha não criada")
            return False
        
        # Pausar
        self.print_step("Pausando campanha...")
        pausar_data = {
            "campana_id": self.campana_id,
            "pausar": True,
            "motivo": "Teste de pausa"
        }
        
        response = self.make_request(
            "POST",
            f"/presione1/campanhas/{self.campana_id}/pausar",
            json=pausar_data
        )
        
        if response.status_code != 200:
            return False
        
        self.print_success("Campanha pausada")
        
        # Aguardar
        self.print_step("Aguardando 3 segundos...")
        time.sleep(3)
        
        # Retomar
        self.print_step("Retomando campanha...")
        retomar_data = {
            "campana_id": self.campana_id,
            "pausar": False,
            "motivo": "Fim do teste de pausa"
        }
        
        response = self.make_request(
            "POST",
            f"/presione1/campanhas/{self.campana_id}/pausar",
            json=retomar_data
        )
        
        if response.status_code == 200:
            self.print_success("Campanha retomada")
            return True
        
        return False
    
    def test_8_parar_campana(self):
        """Teste 8: Parar campanha."""
        self.print_section("TESTE 8: PARAR CAMPANHA")
        
        if not self.campana_id:
            self.print_error("Campanha não criada")
            return False
        
        self.print_step("Parando campanha...")
        
        response = self.make_request("POST", f"/presione1/campanhas/{self.campana_id}/parar")
        
        if response.status_code == 200:
            self.print_success("Campanha parada")
            
            # Verificar estado final
            self.print_step("Verificando estado final...")
            response = self.make_request("GET", f"/presione1/campanhas/{self.campana_id}")
            
            if response.status_code == 200:
                campana = response.json()
                if not campana.get("activa", True):
                    self.print_success("Campanha confirmada como inativa")
                    return True
                else:
                    self.print_error("Campanha ainda aparece como ativa")
        
        return False
    
    def test_9_obter_llamadas(self):
        """Teste 9: Obter chamadas da campanha."""
        self.print_section("TESTE 9: OBTER CHAMADAS DA CAMPANHA")
        
        if not self.campana_id:
            self.print_error("Campanha não criada")
            return False
        
        self.print_step("Listando chamadas da campanha...")
        
        response = self.make_request("GET", f"/presione1/campanhas/{self.campana_id}/llamadas")
        
        if response.status_code == 200:
            llamadas = response.json()
            self.print_success(f"Encontradas {len(llamadas)} chamadas")
            
            # Filtrar por estado
            self.print_step("Listando chamadas finalizadas...")
            response = self.make_request(
                "GET", 
                f"/presione1/campanhas/{self.campana_id}/llamadas?estado=finalizada"
            )
            
            if response.status_code == 200:
                finalizadas = response.json()
                self.print_success(f"Encontradas {len(finalizadas)} chamadas finalizadas")
                return True
        
        return False
    
    def test_10_estadisticas_finais(self):
        """Teste 10: Estatísticas finais."""
        self.print_section("TESTE 10: ESTATÍSTICAS FINAIS")
        
        if not self.campana_id:
            self.print_error("Campanha não criada")
            return False
        
        self.print_step("Obtendo estatísticas finais...")
        
        response = self.make_request("GET", f"/presione1/campanhas/{self.campana_id}/estadisticas")
        
        if response.status_code == 200:
            stats = response.json()
            
            print("\n📊 RESUMO FINAL:")
            print(f"   📞 Total números: {stats.get('total_numeros', 0)}")
            print(f"   📱 Realizadas: {stats.get('llamadas_realizadas', 0)}")
            print(f"   ✅ Atendidas: {stats.get('llamadas_contestadas', 0)}")
            print(f"   1️⃣  Pressionaram 1: {stats.get('llamadas_presiono_1', 0)}")
            print(f"   🔄 Transferidas: {stats.get('llamadas_transferidas', 0)}")
            print(f"   📈 Taxa atendimento: {stats.get('tasa_contestacion', 0)}%")
            print(f"   🎯 Taxa interesse: {stats.get('tasa_presiono_1', 0)}%")
            
            return True
        
        return False
    
    def run_all_tests(self):
        """Executa todos os testes na sequência."""
        print("🚀 INICIANDO TESTES DO SISTEMA PRESIONE 1")
        print(f"🌐 URL Base: {self.base_url}")
        print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("Criar Lista de Teste", self.test_1_criar_lista_teste),
            ("Criar Campanha", self.test_2_criar_campana),
            ("Listar Campanhas", self.test_3_listar_campanhas),
            ("Obter Campanha", self.test_4_obter_campana),
            ("Iniciar Campanha", self.test_5_iniciar_campana),
            ("Monitorar Campanha", self.test_6_monitorar_campana),
            ("Pausar/Retomar", self.test_7_pausar_retomar),
            ("Parar Campanha", self.test_8_parar_campana),
            ("Obter Chamadas", self.test_9_obter_llamadas),
            ("Estatísticas Finais", self.test_10_estadisticas_finais)
        ]
        
        resultados = []
        
        for nome, teste in tests:
            try:
                sucesso = teste()
                resultados.append((nome, sucesso))
                
                if sucesso:
                    self.print_success(f"{nome} - PASSOU")
                else:
                    self.print_error(f"{nome} - FALHOU")
                
                # Pausa entre testes
                time.sleep(1)
                
            except Exception as e:
                self.print_error(f"{nome} - ERRO: {str(e)}")
                resultados.append((nome, False))
        
        # Relatório final
        self.print_section("RELATÓRIO FINAL")
        
        sucessos = sum(1 for _, sucesso in resultados if sucesso)
        total = len(resultados)
        
        print(f"\n📋 RESULTADOS:")
        for nome, sucesso in resultados:
            status = "✅ PASSOU" if sucesso else "❌ FALHOU"
            print(f"   {status} - {nome}")
        
        print(f"\n🎯 RESUMO:")
        print(f"   ✅ Sucessos: {sucessos}/{total}")
        print(f"   ❌ Falhas: {total - sucessos}/{total}")
        print(f"   📊 Taxa de sucesso: {(sucessos/total)*100:.1f}%")
        
        if self.lista_id:
            print(f"\n🗂️  Lista criada: ID {self.lista_id}")
        if self.campana_id:
            print(f"📋 Campanha criada: ID {self.campana_id}")
        
        print(f"\n⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return sucessos == total


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste funcional do sistema Presione 1")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="URL base da API (padrão: http://localhost:8000)"
    )
    parser.add_argument(
        "--test",
        type=int,
        help="Executar teste específico (1-10)"
    )
    
    args = parser.parse_args()
    
    tester = TestPresione1(args.url)
    
    if args.test:
        # Executar teste específico
        test_methods = {
            1: tester.test_1_criar_lista_teste,
            2: tester.test_2_criar_campana,
            3: tester.test_3_listar_campanhas,
            4: tester.test_4_obter_campana,
            5: tester.test_5_iniciar_campana,
            6: tester.test_6_monitorar_campana,
            7: tester.test_7_pausar_retomar,
            8: tester.test_8_parar_campana,
            9: tester.test_9_obter_llamadas,
            10: tester.test_10_estadisticas_finais
        }
        
        if args.test in test_methods:
            print(f"🧪 Executando teste {args.test}...")
            sucesso = test_methods[args.test]()
            exit(0 if sucesso else 1)
        else:
            print("❌ Número de teste inválido. Use 1-10.")
            exit(1)
    else:
        # Executar todos os testes
        sucesso = tester.run_all_tests()
        exit(0 if sucesso else 1)


if __name__ == "__main__":
    main() 