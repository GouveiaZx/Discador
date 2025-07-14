#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das funcionalidades de pausar/retomar campanhas contra o servidor REAL (main.py)
"""

import requests
import json
import os
import logging
from datetime import datetime

# Configurar logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/test_pause_resume_real_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('test_pause_resume_real')

def test_pause_resume_real_server():
    """Teste das APIs de pausar/retomar contra o servidor REAL."""
    base_url = "http://127.0.0.1:8000/api/v1/presione1"
    
    logger.info("INICIANDO teste contra SERVIDOR REAL (main.py)...")
    logger.info(f"URL base: {base_url}")
    
    try:
        # 1. Testar se o servidor está respondendo
        logger.info("\n1. Testando conectividade com servidor real...")
        health_response = requests.get("http://127.0.0.1:8000/health")
        logger.info(f"Health check status: {health_response.status_code}")
        if health_response.status_code == 200:
            logger.info(f"Health check response: {health_response.json()}")
        
        # 2. Listar campanhas
        logger.info("\n2. Listando campanhas no servidor real...")
        response = requests.get(f"{base_url}/campanhas")
        logger.info(f"Status da listagem: {response.status_code}")
        logger.info(f"Response text: {response.text}")
        
        if response.status_code == 200:
            try:
                campanhas = response.json()
                logger.info(f"SUCESSO: {len(campanhas)} campanhas encontradas")
                logger.info(f"Dados das campanhas: {json.dumps(campanhas, indent=2)}")
                
                if not campanhas:
                    logger.warning("AVISO: Nenhuma campanha encontrada no servidor real")
                    return
                
                # Usar a primeira campanha
                campanha = campanhas[0]
                campanha_id = campanha.get('id') or campanha.get('campaign_id')
                logger.info(f"Testando com campanha ID: {campanha_id} - {campanha.get('nombre', 'N/A')}")
                logger.info(f"Estado inicial: activa={campanha.get('activa')}, pausada={campanha.get('pausada')}")
                
                # 3. Testar pausar
                logger.info("\n3. Testando pausar campanha no servidor real...")
                pause_data = {"pausar": True, "motivo": "Teste automatizado - servidor real"}
                logger.info(f"Enviando dados para pausar: {pause_data}")
                
                response = requests.post(f"{base_url}/campanhas/{campanha_id}/pausar", json=pause_data)
                logger.info(f"Status pausar: {response.status_code}")
                logger.info(f"Response text pausar: {response.text}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        logger.info(f"SUCESSO pausar: {result}")
                    except:
                        logger.info(f"SUCESSO pausar (texto): {response.text}")
                    
                    # 4. Verificar estado após pausar
                    logger.info("\n4. Verificando estado após pausar...")
                    response = requests.get(f"{base_url}/campanhas")
                    if response.status_code == 200:
                        campanhas_atualizadas = response.json()
                        logger.info(f"Campanhas após pausar: {json.dumps(campanhas_atualizadas, indent=2)}")
                        campanha_pausada = next((c for c in campanhas_atualizadas if (c.get('id') or c.get('campaign_id')) == campanha_id), None)
                        if campanha_pausada:
                            logger.info(f"Estado após pausar: activa={campanha_pausada.get('activa')}, pausada={campanha_pausada.get('pausada')}")
                            
                            # Verificar se houve mudança real no estado
                            if campanha_pausada.get('pausada') != campanha.get('pausada'):
                                logger.info("✅ SUCESSO: Estado da campanha foi alterado no servidor real!")
                            else:
                                logger.warning("⚠️ AVISO: Estado não foi alterado (pode ser comportamento esperado)")
                        else:
                            logger.warning("AVISO: Campanha não encontrada após pausar")
                    
                    # 5. Testar retomar
                    logger.info("\n5. Testando retomar campanha no servidor real...")
                    resume_data = {"pausar": False, "motivo": "Teste automatizado - retomar servidor real"}
                    logger.info(f"Enviando dados para retomar: {resume_data}")
                    
                    response = requests.post(f"{base_url}/campanhas/{campanha_id}/pausar", json=resume_data)
                    logger.info(f"Status retomar: {response.status_code}")
                    logger.info(f"Response text retomar: {response.text}")
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            logger.info(f"SUCESSO retomar: {result}")
                        except:
                            logger.info(f"SUCESSO retomar (texto): {response.text}")
                        
                        # 6. Verificar estado final
                        logger.info("\n6. Verificando estado final...")
                        response = requests.get(f"{base_url}/campanhas")
                        if response.status_code == 200:
                            campanhas_finais = response.json()
                            logger.info(f"Campanhas finais: {json.dumps(campanhas_finais, indent=2)}")
                            campanha_final = next((c for c in campanhas_finais if (c.get('id') or c.get('campaign_id')) == campanha_id), None)
                            if campanha_final:
                                logger.info(f"Estado final: activa={campanha_final.get('activa')}, pausada={campanha_final.get('pausada')}")
                                
                                # Comparar estados
                                logger.info("\n=== COMPARAÇÃO DE ESTADOS ===")
                                logger.info(f"Estado inicial: activa={campanha.get('activa')}, pausada={campanha.get('pausada')}")
                                logger.info(f"Estado final:   activa={campanha_final.get('activa')}, pausada={campanha_final.get('pausada')}")
                                
                                if (campanha.get('activa') != campanha_final.get('activa') or 
                                    campanha.get('pausada') != campanha_final.get('pausada')):
                                    logger.info("✅ SUCESSO: Estados foram alterados durante o teste!")
                                else:
                                    logger.info("ℹ️ INFO: Estados permaneceram iguais")
                            else:
                                logger.warning("AVISO: Campanha não encontrada no estado final")
                        else:
                            logger.error(f"ERRO ao verificar estado final: {response.text}")
                    else:
                        logger.error(f"ERRO ao retomar: {response.text}")
                else:
                    logger.error(f"ERRO ao pausar: {response.text}")
                    
            except json.JSONDecodeError:
                logger.error(f"ERRO: Resposta não é JSON válido: {response.text}")
        elif response.status_code == 404:
            logger.error("ERRO 404: Endpoint não encontrado no servidor real")
            logger.info("Isso pode indicar que as rotas presione1 não estão disponíveis")
        else:
            logger.error(f"ERRO ao listar campanhas: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        logger.error("ERRO de conexão. Verifique se o servidor real está rodando em http://127.0.0.1:8000")
    except Exception as e:
        logger.error(f"ERRO inesperado: {str(e)}")
    
    logger.info("\n=== TESTE CONTRA SERVIDOR REAL FINALIZADO! ===")
    logger.info(f"Logs salvos em: {os.path.abspath(f'{log_dir}/test_pause_resume_real_server.log')}")

if __name__ == "__main__":
    test_pause_resume_real_server()