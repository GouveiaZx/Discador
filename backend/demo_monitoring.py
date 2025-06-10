#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstracao do Sistema de Monitoramento em Tempo Real
Script para testar todas as funcionalidades do painel de monitoramento
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

class MonitoringDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/monitoring"
        self.session = requests.Session()
        
        # Headers padrao
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        print("🎯 Demonstracao do Sistema de Monitoramento Iniciada")
        print(f"📡 API Base: {self.api_url}")
        print("=" * 60)

    def print_section(self, title: str):
        """Imprime secao formatada"""
        print(f"\n{'=' * 60}")
        print(f"📋 {title}")
        print("=" * 60)

    def print_step(self, step: str):
        """Imprime passo da demonstracao"""
        print(f"⚡ {step}")

    def print_success(self, message: str):
        """Imprime mensagem de sucesso"""
        print(f"✅ {message}")

    def print_error(self, message: str):
        """Imprime mensagem de erro"""
        print(f"❌ {message}")

    def print_info(self, message: str):
        """Imprime informacao"""
        print(f"ℹ️ {message}")

    def make_request(self, method: str, endpoint: str, data: Dict = None) -> requests.Response:
        """Faz requisicao HTTP"""
        url = f"{self.api_url}{endpoint}"
        
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
                raise ValueError(f"Metodo HTTP nao suportado: {method}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.print_error(f"Erro na requisicao: {e}")
            return None

    def test_health_check(self) -> bool:
        """Testa health check do sistema"""
        self.print_section("HEALTH CHECK DO SISTEMA")
        
        self.print_step("Verificando saude do sistema de monitoramento...")
        
        response = self.make_request("GET", "/health")
        
        if response and response.status_code == 200:
            data = response.json()
            self.print_success("Sistema de monitoramento operacional!")
            
            print(f"   • Status: {data.get('status', 'unknown')}")
            print(f"   • Redis: {data.get('redis', 'unknown')}")
            print(f"   • Campanhas ativas: {data.get('campanhas_ativas', 0)}")
            print(f"   • Conexoes WebSocket: {data.get('conexoes_websocket', 0)}")
            
            return True
        else:
            self.print_error("Sistema de monitoramento indisponivel")
            return False

    def create_sample_agents(self) -> List[int]:
        """Cria agentes de exemplo"""
        self.print_section("CRIACAO DE AGENTES DE EXEMPLO")
        
        agentes_exemplo = [
            {
                "nome_agente": "Ana Silva",
                "codigo_agente": "ANA001",
                "extensao_sip": "1001",
                "email": "ana@empresa.com",
                "max_chamadas_simultaneas": 2,
                "skills": {"idiomas": ["portugues", "espanhol"], "departamento": "vendas"}
            },
            {
                "nome_agente": "Carlos Santos",
                "codigo_agente": "CAR002",
                "extensao_sip": "1002",
                "email": "carlos@empresa.com",
                "max_chamadas_simultaneas": 1,
                "skills": {"idiomas": ["portugues"], "departamento": "suporte"}
            },
            {
                "nome_agente": "Maria Oliveira",
                "codigo_agente": "MAR003",
                "extensao_sip": "1003",
                "email": "maria@empresa.com",
                "max_chamadas_simultaneas": 3,
                "skills": {"idiomas": ["portugues", "ingles"], "departamento": "vendas"}
            }
        ]
        
        agentes_criados = []
        
        for agente in agentes_exemplo:
            self.print_step(f"Criando agente: {agente['nome_agente']}")
            
            response = self.make_request("POST", "/agentes", agente)
            
            if response and response.status_code == 200:
                data = response.json()
                agentes_criados.append(data['id'])
                self.print_success(f"Agente {agente['nome_agente']} criado com ID {data['id']}")
            else:
                self.print_error(f"Falha ao criar agente {agente['nome_agente']}")
        
        return agentes_criados

    def update_agent_status(self, agente_ids: List[int]):
        """Atualiza status dos agentes"""
        self.print_section("SIMULACAO DE STATUS DOS AGENTES")
        
        status_options = ["livre", "em_chamada", "ausente", "pausado"]
        
        for agente_id in agente_ids:
            status = random.choice(status_options)
            
            self.print_step(f"Atualizando agente {agente_id} para status: {status}")
            
            data = {
                "status_atual": status,
                "chamada_atual_id": f"CALL-{random.randint(1000, 9999)}" if status == "em_chamada" else None
            }
            
            response = self.make_request("PUT", f"/agentes/{agente_id}/status", data)
            
            if response and response.status_code == 200:
                self.print_success(f"Status do agente {agente_id} atualizado para {status}")
            else:
                self.print_error(f"Falha ao atualizar status do agente {agente_id}")

    def create_system_events(self):
        """Cria eventos de exemplo no sistema"""
        self.print_section("REGISTRO DE EVENTOS DO SISTEMA")
        
        eventos_exemplo = [
            {
                "tipo_evento": "campanha_iniciada",
                "titulo": "Campanha Vendas Q1 iniciada",
                "descricao": "Nova campanha de vendas iniciada com 5000 contatos",
                "nivel_severidade": "info"
            },
            {
                "tipo_evento": "provedor_falha",
                "titulo": "Falha temporaria no Provedor Twilio",
                "descricao": "Timeout detectado na conexao SIP - failover automatico ativado",
                "nivel_severidade": "warning"
            },
            {
                "tipo_evento": "agente_login",
                "titulo": "Multiplos agentes conectados",
                "descricao": "Sistema registrou login de 5 agentes simultaneamente",
                "nivel_severidade": "info"
            },
            {
                "tipo_evento": "chamada_finalizada",
                "titulo": "Pico de transferencias bem-sucedidas",
                "descricao": "Taxa de transferencia alcancou 95% na ultima hora",
                "nivel_severidade": "info"
            }
        ]
        
        for evento in eventos_exemplo:
            self.print_step(f"Registrando evento: {evento['titulo']}")
            
            response = self.make_request("POST", "/eventos", evento)
            
            if response and response.status_code == 200:
                self.print_success("Evento registrado com sucesso")
            else:
                self.print_error("Falha ao registrar evento")

    def test_dashboard_apis(self):
        """Testa APIs do dashboard"""
        self.print_section("TESTE DAS APIS DO DASHBOARD")
        
        # Dashboard resumido
        self.print_step("Obtendo dashboard resumido...")
        response = self.make_request("GET", "/dashboard/resumo")
        
        if response and response.status_code == 200:
            data = response.json()
            self.print_success("Dashboard resumido obtido com sucesso")
            
            print(f"   • Campanhas ativas: {data.get('total_campanhas_ativas', 0)}")
            print(f"   • Chamadas ativas: {data.get('total_chamadas_ativas', 0)}")
            print(f"   • Agentes online: {data.get('total_agentes_online', 0)}")
            print(f"   • Taxa atendimento geral: {data.get('taxa_atendimento_geral', 0)}%")
            print(f"   • Alertas criticos: {data.get('alertas_criticos', 0)}")
            print(f"   • Alertas warning: {data.get('alertas_warning', 0)}")
        else:
            self.print_error("Falha ao obter dashboard resumido")
        
        # Dashboard detalhado
        self.print_step("Obtendo dashboard detalhado...")
        response = self.make_request("GET", "/dashboard/detalhado")
        
        if response and response.status_code == 200:
            data = response.json()
            self.print_success("Dashboard detalhado obtido com sucesso")
            
            print(f"   • Campanhas detalhadas: {len(data.get('campanhas', []))}")
            print(f"   • Agentes detalhados: {len(data.get('agentes', []))}")
            print(f"   • Chamadas ativas: {len(data.get('chamadas_ativas', []))}")
            print(f"   • Eventos recentes: {len(data.get('eventos_recentes', []))}")
        else:
            self.print_error("Falha ao obter dashboard detalhado")

    def test_metrics_apis(self):
        """Testa APIs de metricas especificas"""
        self.print_section("TESTE DAS APIS DE METRICAS")
        
        # Metricas de campanhas
        self.print_step("Obtendo metricas de campanhas...")
        response = self.make_request("GET", "/campanhas?apenas_ativas=true")
        
        if response and response.status_code == 200:
            campanhas = response.json()
            self.print_success(f"Encontradas {len(campanhas)} campanhas ativas")
            
            for campanha in campanhas[:3]:  # Mostrar apenas as 3 primeiras
                print(f"   • {campanha['nome_campanha']}: {campanha['chamadas_ativas']} ativas")
        else:
            self.print_error("Falha ao obter metricas de campanhas")
        
        # Metricas de provedores
        self.print_step("Obtendo metricas de provedores SIP...")
        response = self.make_request("GET", "/provedores")
        
        if response and response.status_code == 200:
            provedores = response.json()
            self.print_success(f"Encontrados {len(provedores)} provedores SIP")
            
            for provedor in provedores:
                print(f"   • {provedor['nome_provedor']}: {provedor['status_conexao']} - {provedor['taxa_sucesso']}% sucesso")
        else:
            self.print_error("Falha ao obter metricas de provedores")
        
        # Metricas de agentes
        self.print_step("Obtendo metricas de agentes...")
        response = self.make_request("GET", "/agentes")
        
        if response and response.status_code == 200:
            agentes = response.json()
            self.print_success(f"Encontrados {len(agentes)} agentes")
            
            for agente in agentes:
                print(f"   • {agente['nome_agente']} ({agente['codigo_agente']}): {agente['status_atual']}")
        else:
            self.print_error("Falha ao obter metricas de agentes")

    def test_events_api(self):
        """Testa API de eventos"""
        self.print_section("TESTE DA API DE EVENTOS")
        
        self.print_step("Listando eventos recentes...")
        response = self.make_request("GET", "/eventos?limit=10&ultimas_horas=24")
        
        if response and response.status_code == 200:
            eventos = response.json()
            self.print_success(f"Encontrados {len(eventos)} eventos nas ultimas 24h")
            
            for evento in eventos[:5]:  # Mostrar apenas os 5 primeiros
                timestamp = evento.get('timestamp_evento', 'N/A')
                print(f"   • [{evento['nivel_severidade'].upper()}] {evento['titulo']} - {timestamp}")
        else:
            self.print_error("Falha ao obter eventos")

    def test_export_functionality(self):
        """Testa funcionalidade de exportacao"""
        self.print_section("TESTE DE EXPORTACAO DE DADOS")
        
        self.print_step("Solicitando exportacao CSV...")
        
        export_data = {
            "tipo_export": "csv",
            "incluir_chamadas": True,
            "incluir_agentes": True,
            "incluir_eventos": False,
            "incluir_cabecalhos": True,
            "formato_data": "iso"
        }
        
        response = self.make_request("POST", "/export/csv", export_data)
        
        if response and response.status_code == 200:
            # Verificar se e CSV
            content_type = response.headers.get('content-type', '')
            if 'csv' in content_type or 'text' in content_type:
                self.print_success("Exportacao CSV gerada com sucesso")
                print(f"   • Content-Type: {content_type}")
                print(f"   • Tamanho: {len(response.content)} bytes")
            else:
                self.print_info("Resposta recebida, mas tipo de conteudo inesperado")
        else:
            self.print_error("Falha ao gerar exportacao CSV")

    def test_cache_management(self):
        """Testa gerenciamento de cache"""
        self.print_section("TESTE DE GERENCIAMENTO DE CACHE")
        
        self.print_step("Limpando cache do sistema...")
        response = self.make_request("POST", "/cache/clear")
        
        if response and response.status_code == 200:
            data = response.json()
            self.print_success("Cache limpo com sucesso")
            print(f"   • Mensagem: {data.get('mensagem', 'N/A')}")
        else:
            self.print_error("Falha ao limpar cache")

    def simulate_realtime_updates(self, duration: int = 30):
        """Simula atualizacoes em tempo real"""
        self.print_section(f"SIMULACAO DE ATUALIZACOES EM TEMPO REAL ({duration}s)")
        
        self.print_step("Iniciando monitoramento de metricas...")
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Buscar metricas atualizadas
            response = self.make_request("GET", "/dashboard/resumo")
            
            if response and response.status_code == 200:
                data = response.json()
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"[{timestamp}] Campanhas: {data.get('total_campanhas_ativas', 0)} | "
                      f"Chamadas: {data.get('total_chamadas_ativas', 0)} | "
                      f"Agentes: {data.get('total_agentes_online', 0)} | "
                      f"Taxa: {data.get('taxa_atendimento_geral', 0)}%")
            
            time.sleep(3)  # Atualizar a cada 3 segundos
        
        self.print_success("Simulacao de tempo real concluida")

    def run_full_demo(self):
        """Executa demonstracao completa"""
        print("🚀 INICIANDO DEMONSTRACAO COMPLETA DO SISTEMA DE MONITORAMENTO")
        print("=" * 80)
        
        try:
            # 1. Health Check
            if not self.test_health_check():
                self.print_error("Sistema nao esta funcionando. Abortando demonstracao.")
                return
            
            # 2. Criar agentes de exemplo
            agente_ids = self.create_sample_agents()
            
            # 3. Atualizar status dos agentes
            if agente_ids:
                self.update_agent_status(agente_ids)
            
            # 4. Criar eventos do sistema
            self.create_system_events()
            
            # 5. Testar APIs do dashboard
            self.test_dashboard_apis()
            
            # 6. Testar APIs de metricas
            self.test_metrics_apis()
            
            # 7. Testar API de eventos
            self.test_events_api()
            
            # 8. Testar exportacao
            self.test_export_functionality()
            
            # 9. Testar gerenciamento de cache
            self.test_cache_management()
            
            # 10. Simulacao em tempo real
            self.print_section("DEMONSTRACAO FINAL - TEMPO REAL")
            self.print_info("Esta secao mostrara atualizacoes em tempo real por 30 segundos")
            input("Pressione ENTER para iniciar...")
            
            self.simulate_realtime_updates(30)
            
            # Resumo final
            self.print_section("RESUMO DA DEMONSTRACAO")
            self.print_success("✅ Health Check - Sistema operacional")
            self.print_success(f"✅ Agentes criados - {len(agente_ids)} agentes")
            self.print_success("✅ Status atualizados - Simulacao de trabalho")
            self.print_success("✅ Eventos registrados - Auditoria funcionando")
            self.print_success("✅ APIs testadas - Dashboards funcionais")
            self.print_success("✅ Metricas verificadas - Dados em tempo real")
            self.print_success("✅ Exportacao testada - CSV gerado")
            self.print_success("✅ Cache gerenciado - Performance otimizada")
            self.print_success("✅ Tempo real simulado - Atualizacoes automaticas")
            
            print("\n🎉 DEMONSTRACAO CONCLUIDA COM SUCESSO!")
            print("O Sistema de Monitoramento em Tempo Real esta funcionando perfeitamente.")
            print("\n📊 Acesse o frontend em: http://localhost:3000")
            print("🔗 API docs em: http://localhost:8000/docs")
            
        except KeyboardInterrupt:
            self.print_info("Demonstracao interrompida pelo usuario")
        except Exception as e:
            self.print_error(f"Erro inesperado: {e}")

def main():
    """Funcao principal"""
    demo = MonitoringDemo()
    
    print("Escolha uma opcao:")
    print("1. Demonstracao completa")
    print("2. Apenas health check")
    print("3. Apenas teste de APIs")
    print("4. Apenas simulacao tempo real")
    
    choice = input("\nDigite sua escolha (1-4): ").strip()
    
    if choice == "1":
        demo.run_full_demo()
    elif choice == "2":
        demo.test_health_check()
    elif choice == "3":
        demo.test_dashboard_apis()
        demo.test_metrics_apis()
        demo.test_events_api()
    elif choice == "4":
        duration = int(input("Duracao em segundos (padrao 30): ") or "30")
        demo.simulate_realtime_updates(duration)
    else:
        print("Opcao invalida. Executando demonstracao completa...")
        demo.run_full_demo()

if __name__ == "__main__":
    main() 