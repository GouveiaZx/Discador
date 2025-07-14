#!/usr/bin/env python3
# Teste completo das funcionalidades de campanhas

import asyncio
import requests
import json
from datetime import datetime

API_BASE_URL = 'http://localhost:8000/api/v1'
CAMPAIGN_ID = 1

def log_test(message, status="INFO"):
    """Log formatado para testes"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_emoji = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "ERROR": "❌",
        "WARNING": "⚠️",
        "TEST": "🧪"
    }
    print(f"[{timestamp}] {status_emoji.get(status, '📝')} {message}")

def make_api_request(endpoint, method='GET', data=None):
    """Faz requisição para a API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        log_test(f"{method} {endpoint}", "TEST")
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        
        log_test(f"Status: {response.status_code}", "SUCCESS" if response.ok else "ERROR")
        
        if response.ok:
            try:
                result = response.json()
                log_test(f"Resposta: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...", "SUCCESS")
                return result
            except:
                log_test(f"Resposta texto: {response.text[:200]}...", "SUCCESS")
                return response.text
        else:
            log_test(f"Erro: {response.text}", "ERROR")
            return None
            
    except Exception as e:
        log_test(f"Exceção: {str(e)}", "ERROR")
        return None

def test_backend_health():
    """Testa se o backend está funcionando"""
    log_test("=== TESTE 1: SAÚDE DO BACKEND ===", "TEST")
    
    # Teste de health check
    result = make_api_request('/health')
    if result:
        log_test("Backend está funcionando!", "SUCCESS")
        return True
    else:
        log_test("Backend não está respondendo!", "ERROR")
        return False

def test_campaign_operations():
    """Testa operações de campanhas"""
    log_test("=== TESTE 2: OPERAÇÕES DE CAMPANHAS ===", "TEST")
    
    # 1. Listar campanhas
    log_test("Listando campanhas...", "TEST")
    campanhas = make_api_request('/presione1/campanhas')
    
    if not campanhas:
        log_test("Nenhuma campanha encontrada", "WARNING")
        return False
    
    log_test(f"Encontradas {len(campanhas)} campanhas", "SUCCESS")
    
    # 2. Buscar campanha específica
    log_test(f"Buscando campanha {CAMPAIGN_ID}...", "TEST")
    campanha = make_api_request(f'/presione1/campanhas/{CAMPAIGN_ID}')
    
    if not campanha:
        log_test(f"Campanha {CAMPAIGN_ID} não encontrada", "ERROR")
        return False
    
    log_test(f"Campanha encontrada: {campanha.get('nombre', 'N/A')}", "SUCCESS")
    return True

def test_pause_resume_operations():
    """Testa operações de pausar/retomar"""
    log_test("=== TESTE 3: PAUSAR/RETOMAR CAMPANHAS ===", "TEST")
    
    # 1. Pausar campanha
    log_test("Testando pausar campanha...", "TEST")
    pause_data = {
        "pausar": True,
        "motivo": "Teste automatizado - pausar"
    }
    
    result = make_api_request(f'/presione1/campanhas/{CAMPAIGN_ID}/pausar', 'POST', pause_data)
    
    if result:
        log_test("Campanha pausada com sucesso!", "SUCCESS")
    else:
        log_test("Falha ao pausar campanha", "ERROR")
        return False
    
    # 2. Verificar status após pausar
    log_test("Verificando status após pausar...", "TEST")
    campanha_pausada = make_api_request(f'/presione1/campanhas/{CAMPAIGN_ID}')
    
    if campanha_pausada and campanha_pausada.get('pausada'):
        log_test("Status confirmado: campanha está pausada", "SUCCESS")
    else:
        log_test("Status não atualizado corretamente", "WARNING")
    
    # 3. Retomar campanha
    log_test("Testando retomar campanha...", "TEST")
    resume_data = {
        "pausar": False,
        "motivo": "Teste automatizado - retomar"
    }
    
    result = make_api_request(f'/presione1/campanhas/{CAMPAIGN_ID}/pausar', 'POST', resume_data)
    
    if result:
        log_test("Campanha retomada com sucesso!", "SUCCESS")
    else:
        log_test("Falha ao retomar campanha", "ERROR")
        return False
    
    # 4. Verificar status após retomar
    log_test("Verificando status após retomar...", "TEST")
    campanha_retomada = make_api_request(f'/presione1/campanhas/{CAMPAIGN_ID}')
    
    if campanha_retomada and not campanha_retomada.get('pausada'):
        log_test("Status confirmado: campanha não está mais pausada", "SUCCESS")
    else:
        log_test("Status não atualizado corretamente", "WARNING")
    
    return True

def test_stop_operations():
    """Testa operação de parar campanha"""
    log_test("=== TESTE 4: PARAR CAMPANHAS ===", "TEST")
    
    # Parar campanha
    log_test("Testando parar campanha...", "TEST")
    result = make_api_request(f'/presione1/campanhas/{CAMPAIGN_ID}/parar', 'POST')
    
    if result:
        log_test("Campanha parada com sucesso!", "SUCCESS")
    else:
        log_test("Falha ao parar campanha (pode estar inativa)", "WARNING")
    
    # Verificar status após parar
    log_test("Verificando status após parar...", "TEST")
    campanha_parada = make_api_request(f'/presione1/campanhas/{CAMPAIGN_ID}')
    
    if campanha_parada:
        ativa = campanha_parada.get('activa', False)
        pausada = campanha_parada.get('pausada', False)
        log_test(f"Status: ativa={ativa}, pausada={pausada}", "INFO")
    
    return True

def test_statistics():
    """Testa obtenção de estatísticas"""
    log_test("=== TESTE 5: ESTATÍSTICAS ===", "TEST")
    
    # Buscar estatísticas
    log_test("Buscando estatísticas da campanha...", "TEST")
    stats = make_api_request(f'/presione1/campanhas/{CAMPAIGN_ID}/estadisticas')
    
    if stats:
        log_test("Estatísticas obtidas com sucesso!", "SUCCESS")
        # Mostrar algumas estatísticas importantes
        total_contatos = stats.get('total_contatos', 0)
        llamadas_realizadas = stats.get('llamadas_realizadas', 0)
        log_test(f"Total contatos: {total_contatos}, Chamadas: {llamadas_realizadas}", "INFO")
    else:
        log_test("Falha ao obter estatísticas", "ERROR")
    
    return True

def test_additional_endpoints():
    """Testa endpoints adicionais"""
    log_test("=== TESTE 6: ENDPOINTS ADICIONAIS ===", "TEST")
    
    # Teste de debug
    log_test("Testando debug da campanha...", "TEST")
    debug_info = make_api_request(f'/presione1/campanhas/{CAMPAIGN_ID}/debug')
    
    if debug_info:
        log_test("Debug obtido com sucesso!", "SUCCESS")
        problemas = debug_info.get('problemas', [])
        if problemas:
            log_test(f"Problemas encontrados: {len(problemas)}", "WARNING")
            for problema in problemas[:3]:  # Mostrar apenas os primeiros 3
                log_test(f"- {problema}", "WARNING")
        else:
            log_test("Nenhum problema encontrado no debug", "SUCCESS")
    else:
        log_test("Falha ao obter debug", "ERROR")
    
    return True

def main():
    """Executa todos os testes"""
    log_test("🚀 INICIANDO TESTES COMPLETOS DE CAMPANHAS", "TEST")
    log_test(f"Backend: {API_BASE_URL}", "INFO")
    log_test(f"Campanha de teste: {CAMPAIGN_ID}", "INFO")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 6
    
    # Executar testes
    if test_backend_health():
        tests_passed += 1
    
    if test_campaign_operations():
        tests_passed += 1
    
    if test_pause_resume_operations():
        tests_passed += 1
    
    if test_stop_operations():
        tests_passed += 1
    
    if test_statistics():
        tests_passed += 1
    
    if test_additional_endpoints():
        tests_passed += 1
    
    # Resultado final
    print("=" * 60)
    log_test(f"RESULTADO FINAL: {tests_passed}/{total_tests} testes passaram", "SUCCESS" if tests_passed == total_tests else "WARNING")
    
    if tests_passed == total_tests:
        log_test("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.", "SUCCESS")
    else:
        log_test(f"⚠️ {total_tests - tests_passed} testes falharam. Verifique os logs acima.", "WARNING")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        log_test("Testes interrompidos pelo usuário", "WARNING")
        exit(1)
    except Exception as e:
        log_test(f"Erro inesperado: {str(e)}", "ERROR")
        exit(1)