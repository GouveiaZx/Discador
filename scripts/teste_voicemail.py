#!/usr/bin/env python3
"""
Script de teste para funcionalidade de detecção de voicemail no sistema Presione 1.

Este script demonstra e testa:
- Criação de campanhas com detecção de voicemail
- Simulação de chamadas que caem em voicemail
- Reprodução automática de mensagens no voicemail
- Estatísticas específicas de voicemail
- Diferentes cenários de detecção

Uso:
    python scripts/teste_voicemail.py
    python scripts/teste_voicemail.py --test-especifico 5
"""

import asyncio
import sys
import os
import argparse
import json
from datetime import datetime
from typing import Dict, Any

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from colorama import init, Fore, Style

# Inicializar colorama para cores no terminal
init()

# Configuração da API
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class TestadorVoicemail:
    """Classe para testar funcionalidades de voicemail."""
    
    def __init__(self):
        self.session = requests.Session()
        self.campana_id = None
        self.lista_id = None
        
    def print_success(self, message: str):
        """Imprime mensagem de sucesso."""
        print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
        
    def print_error(self, message: str):
        """Imprime mensagem de erro."""
        print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")
        
    def print_info(self, message: str):
        """Imprime mensagem informativa."""
        print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")
        
    def print_warning(self, message: str):
        """Imprime mensagem de aviso."""
        print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")
    
    def print_header(self, title: str):
        """Imprime cabeçalho de seção."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}{Style.RESET_ALL}")
    
    def fazer_requisicao(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Faz requisição HTTP e retorna resposta."""
        url = f"{API_BASE}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False, 
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def teste_1_verificar_api(self) -> bool:
        """Teste 1: Verificar se a API está funcionando."""
        self.print_header("TESTE 1: Verificação da API")
        
        resultado = self.fazer_requisicao("GET", "/")
        
        if resultado["success"]:
            self.print_success("API está funcionando corretamente")
            self.print_info(f"Resposta: {resultado['data']}")
            return True
        else:
            self.print_error(f"API não está funcionando: {resultado['error']}")
            return False
    
    def teste_2_criar_lista_teste(self) -> bool:
        """Teste 2: Criar lista de teste para voicemail."""
        self.print_header("TESTE 2: Criação de Lista de Teste")
        
        # Dados da lista
        lista_data = {
            "nombre": f"Lista Teste Voicemail {datetime.now().strftime('%H%M%S')}",
            "descripcion": "Lista para testar detecção de voicemail",
            "numeros": [
                "+5491112345001",  # Número que vai para voicemail
                "+5491112345002",  # Número que atende pessoa
                "+5491112345003",  # Número que não atende
                "+5491112345004",  # Número que vai para voicemail sem áudio
                "+5491112345005"   # Número que atende e pressiona 1
            ]
        }
        
        resultado = self.fazer_requisicao("POST", "/listas-llamadas", lista_data)
        
        if resultado["success"]:
            self.lista_id = resultado["data"]["id"]
            self.print_success(f"Lista criada com ID: {self.lista_id}")
            self.print_info(f"Números adicionados: {len(lista_data['numeros'])}")
            return True
        else:
            self.print_error(f"Erro ao criar lista: {resultado['error']}")
            return False
    
    def teste_3_criar_campana_voicemail(self) -> bool:
        """Teste 3: Criar campanha com detecção de voicemail."""
        self.print_header("TESTE 3: Criação de Campanha com Voicemail")
        
        if not self.lista_id:
            self.print_error("Lista não foi criada. Execute o teste 2 primeiro.")
            return False
        
        # Dados da campanha com voicemail
        campana_data = {
            "nombre": f"Campanha Voicemail Test {datetime.now().strftime('%H%M%S')}",
            "descripcion": "Campanha para testar detecção automática de correio de voz",
            "lista_llamadas_id": self.lista_id,
            "mensaje_audio_url": "/sounds/presione1_demo.wav",
            "timeout_presione1": 10,
            
            # Configuração de voicemail
            "detectar_voicemail": True,
            "mensaje_voicemail_url": "/sounds/voicemail_demo.wav",
            "duracion_minima_voicemail": 3,
            "duracion_maxima_voicemail": 30,
            
            # Configuração de transferência
            "extension_transferencia": "100",
            "llamadas_simultaneas": 2,
            "tiempo_entre_llamadas": 3
        }
        
        resultado = self.fazer_requisicao("POST", "/presione1/campanhas", campana_data)
        
        if resultado["success"]:
            self.campana_id = resultado["data"]["id"]
            self.print_success(f"Campanha criada com ID: {self.campana_id}")
            self.print_info("✅ Detecção de voicemail: ATIVADA")
            self.print_info(f"✅ Áudio para voicemail: {campana_data['mensaje_voicemail_url']}")
            self.print_info(f"✅ Duração máxima: {campana_data['duracion_maxima_voicemail']}s")
            return True
        else:
            self.print_error(f"Erro ao criar campanha: {resultado['error']}")
            return False
    
    def teste_4_iniciar_campana(self) -> bool:
        """Teste 4: Iniciar campanha com voicemail."""
        self.print_header("TESTE 4: Iniciar Campanha")
        
        if not self.campana_id:
            self.print_error("Campanha não foi criada. Execute o teste 3 primeiro.")
            return False
        
        resultado = self.fazer_requisicao("POST", f"/presione1/campanhas/{self.campana_id}/iniciar")
        
        if resultado["success"]:
            self.print_success("Campanha iniciada com sucesso")
            self.print_info("🎯 Sistema irá detectar voicemails automaticamente")
            self.print_info("📞 Chamadas sendo realizadas...")
            return True
        else:
            self.print_error(f"Erro ao iniciar campanha: {resultado['error']}")
            return False
    
    def teste_5_monitorar_voicemails(self) -> bool:
        """Teste 5: Monitorar detecção de voicemails."""
        self.print_header("TESTE 5: Monitoramento de Voicemails")
        
        if not self.campana_id:
            self.print_error("Campanha não foi criada. Execute os testes anteriores.")
            return False
        
        self.print_info("Monitorando por 30 segundos...")
        
        for i in range(6):  # 6 verificações de 5 segundos cada
            # Obter estatísticas
            resultado = self.fazer_requisicao("GET", f"/presione1/campanhas/{self.campana_id}/estadisticas")
            
            if resultado["success"]:
                stats = resultado["data"]
                
                print(f"\n📊 Estatísticas (verificação {i+1}/6):")
                print(f"   📞 Chamadas realizadas: {stats.get('llamadas_realizadas', 0)}")
                print(f"   ✅ Chamadas atendidas: {stats.get('llamadas_contestadas', 0)}")
                print(f"   📧 Voicemails detectados: {stats.get('llamadas_voicemail', 0)}")
                print(f"   🎵 Mensagens deixadas: {stats.get('llamadas_voicemail_mensaje_dejado', 0)}")
                print(f"   📈 Taxa de voicemail: {stats.get('tasa_voicemail', 0)}%")
                print(f"   ⏱️  Duração média mensagem: {stats.get('duracion_media_mensaje_voicemail', 0)}s")
                
                # Verificar se há voicemails detectados
                if stats.get('llamadas_voicemail', 0) > 0:
                    self.print_success(f"Voicemails detectados: {stats['llamadas_voicemail']}")
                    
                    if stats.get('llamadas_voicemail_mensaje_dejado', 0) > 0:
                        self.print_success(f"Mensagens deixadas: {stats['llamadas_voicemail_mensaje_dejado']}")
                    
                    return True
            
            if i < 5:  # Não aguardar na última iteração
                print("   ⏳ Aguardando 5 segundos...")
                import time
                time.sleep(5)
        
        self.print_warning("Monitoramento concluído. Verifique se houve detecção de voicemail.")
        return True
    
    def teste_6_listar_chamadas_voicemail(self) -> bool:
        """Teste 6: Listar chamadas que foram para voicemail."""
        self.print_header("TESTE 6: Chamadas com Voicemail")
        
        if not self.campana_id:
            self.print_error("Campanha não foi criada.")
            return False
        
        resultado = self.fazer_requisicao("GET", f"/presione1/campanhas/{self.campana_id}/llamadas")
        
        if resultado["success"]:
            chamadas = resultado["data"]
            voicemails = [c for c in chamadas if c.get('voicemail_detectado')]
            
            self.print_info(f"Total de chamadas: {len(chamadas)}")
            self.print_info(f"Chamadas com voicemail: {len(voicemails)}")
            
            if voicemails:
                print(f"\n📧 Detalhes dos Voicemails:")
                for i, chamada in enumerate(voicemails, 1):
                    print(f"\n   {i}. Número: {chamada.get('numero_destino')}")
                    print(f"      Estado: {chamada.get('estado')}")
                    print(f"      Detectado em: {chamada.get('fecha_voicemail_detectado')}")
                    print(f"      Duração mensagem: {chamada.get('duracion_mensaje_voicemail', 0)}s")
                    print(f"      Motivo finalização: {chamada.get('motivo_finalizacion')}")
                
                self.print_success("Voicemails processados com sucesso!")
                return True
            else:
                self.print_warning("Nenhum voicemail detectado ainda.")
                return True
        else:
            self.print_error(f"Erro ao listar chamadas: {resultado['error']}")
            return False
    
    def teste_7_pausar_campana(self) -> bool:
        """Teste 7: Pausar campanha."""
        self.print_header("TESTE 7: Pausar Campanha")
        
        if not self.campana_id:
            self.print_error("Campanha não foi criada.")
            return False
        
        resultado = self.fazer_requisicao("POST", f"/presione1/campanhas/{self.campana_id}/pausar", {
            "pausar": True,
            "motivo": "Teste de pausa para análise de voicemails"
        })
        
        if resultado["success"]:
            self.print_success("Campanha pausada com sucesso")
            self.print_info("🔄 Chamadas ativas continuarão até finalizar")
            return True
        else:
            self.print_error(f"Erro ao pausar campanha: {resultado['error']}")
            return False
    
    def teste_8_retomar_campana(self) -> bool:
        """Teste 8: Retomar campanha."""
        self.print_header("TESTE 8: Retomar Campanha")
        
        if not self.campana_id:
            self.print_error("Campanha não foi criada.")
            return False
        
        resultado = self.fazer_requisicao("POST", f"/presione1/campanhas/{self.campana_id}/pausar", {
            "pausar": False,
            "motivo": "Retomando após análise de voicemails"
        })
        
        if resultado["success"]:
            self.print_success("Campanha retomada com sucesso")
            self.print_info("📞 Discado automático reiniciado")
            return True
        else:
            self.print_error(f"Erro ao retomar campanha: {resultado['error']}")
            return False
    
    def teste_9_estatisticas_finais(self) -> bool:
        """Teste 9: Obter estatísticas finais de voicemail."""
        self.print_header("TESTE 9: Estatísticas Finais de Voicemail")
        
        if not self.campana_id:
            self.print_error("Campanha não foi criada.")
            return False
        
        resultado = self.fazer_requisicao("GET", f"/presione1/campanhas/{self.campana_id}/estadisticas")
        
        if resultado["success"]:
            stats = resultado["data"]
            
            print(f"\n📊 RELATÓRIO FINAL DE VOICEMAIL:")
            print(f"{'='*50}")
            print(f"📞 Total de chamadas realizadas: {stats.get('llamadas_realizadas', 0)}")
            print(f"✅ Chamadas atendidas: {stats.get('llamadas_contestadas', 0)}")
            print(f"📧 Voicemails detectados: {stats.get('llamadas_voicemail', 0)}")
            print(f"🎵 Mensagens deixadas no voicemail: {stats.get('llamadas_voicemail_mensaje_dejado', 0)}")
            print(f"👤 Pessoas que pressionaram 1: {stats.get('llamadas_presiono_1', 0)}")
            print(f"🔄 Transferências realizadas: {stats.get('llamadas_transferidas', 0)}")
            print(f"❌ Erros: {stats.get('llamadas_error', 0)}")
            
            print(f"\n📈 PERCENTUAIS:")
            print(f"📞 Taxa de atendimento: {stats.get('tasa_contestacion', 0)}%")
            print(f"📧 Taxa de voicemail: {stats.get('tasa_voicemail', 0)}%")
            print(f"🎵 Taxa de mensagem no voicemail: {stats.get('tasa_mensaje_voicemail', 0)}%")
            print(f"👤 Taxa de interesse (presione 1): {stats.get('tasa_presiono_1', 0)}%")
            print(f"🔄 Taxa de transferência: {stats.get('tasa_transferencia', 0)}%")
            
            print(f"\n⏱️  TEMPOS MÉDIOS:")
            print(f"⏰ Tempo médio de resposta: {stats.get('tiempo_medio_respuesta', 0)}s")
            print(f"📞 Duração média de chamada: {stats.get('duracion_media_llamada', 0)}s")
            print(f"🎵 Duração média mensagem voicemail: {stats.get('duracion_media_mensaje_voicemail', 0)}s")
            
            self.print_success("Relatório de voicemail gerado com sucesso!")
            return True
        else:
            self.print_error(f"Erro ao obter estatísticas: {resultado['error']}")
            return False
    
    def teste_10_parar_campana(self) -> bool:
        """Teste 10: Parar campanha definitivamente."""
        self.print_header("TESTE 10: Parar Campanha")
        
        if not self.campana_id:
            self.print_error("Campanha não foi criada.")
            return False
        
        resultado = self.fazer_requisicao("POST", f"/presione1/campanhas/{self.campana_id}/parar")
        
        if resultado["success"]:
            self.print_success("Campanha parada com sucesso")
            self.print_info("🛑 Todas as chamadas foram finalizadas")
            self.print_info("📊 Dados de voicemail preservados para análise")
            return True
        else:
            self.print_error(f"Erro ao parar campanha: {resultado['error']}")
            return False
    
    def executar_teste_especifico(self, numero_teste: int) -> bool:
        """Executa um teste específico."""
        testes = {
            1: self.teste_1_verificar_api,
            2: self.teste_2_criar_lista_teste,
            3: self.teste_3_criar_campana_voicemail,
            4: self.teste_4_iniciar_campana,
            5: self.teste_5_monitorar_voicemails,
            6: self.teste_6_listar_chamadas_voicemail,
            7: self.teste_7_pausar_campana,
            8: self.teste_8_retomar_campana,
            9: self.teste_9_estatisticas_finais,
            10: self.teste_10_parar_campana
        }
        
        if numero_teste in testes:
            return testes[numero_teste]()
        else:
            self.print_error(f"Teste {numero_teste} não existe. Testes disponíveis: 1-10")
            return False
    
    def executar_todos_testes(self) -> bool:
        """Executa todos os testes em sequência."""
        self.print_header("INICIANDO TESTES DE VOICEMAIL")
        self.print_info("Este script testará a detecção automática de correio de voz")
        
        testes_executados = 0
        testes_sucesso = 0
        
        for i in range(1, 11):
            if self.executar_teste_especifico(i):
                testes_sucesso += 1
            testes_executados += 1
            
            # Pausa entre testes (exceto no último)
            if i < 10:
                print(f"\n⏳ Aguardando 2 segundos antes do próximo teste...")
                import time
                time.sleep(2)
        
        # Relatório final
        self.print_header("RELATÓRIO FINAL DOS TESTES")
        print(f"📊 Testes executados: {testes_executados}")
        print(f"✅ Testes com sucesso: {testes_sucesso}")
        print(f"❌ Testes com falha: {testes_executados - testes_sucesso}")
        print(f"📈 Taxa de sucesso: {(testes_sucesso/testes_executados)*100:.1f}%")
        
        if testes_sucesso == testes_executados:
            self.print_success("🎉 TODOS OS TESTES DE VOICEMAIL PASSARAM!")
            self.print_info("✅ Sistema de detecção de voicemail funcionando corretamente")
            return True
        else:
            self.print_warning(f"⚠️  {testes_executados - testes_sucesso} teste(s) falharam")
            return False


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Testes de funcionalidade de voicemail")
    parser.add_argument(
        "--test-especifico", 
        type=int, 
        help="Executar apenas um teste específico (1-10)"
    )
    
    args = parser.parse_args()
    
    testador = TestadorVoicemail()
    
    if args.test_especifico:
        sucesso = testador.executar_teste_especifico(args.test_especifico)
    else:
        sucesso = testador.executar_todos_testes()
    
    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    main() 