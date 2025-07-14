#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Funcionalidade Pause/Resume - Servidor Real Corrigido
Testa as funcionalidades de pausar e retomar campanhas contra o servidor real main.py
com os endpoints corretos identificados no código.
"""

import requests
import json
import logging
from datetime import datetime
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_pause_resume_real_corrected.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configurações
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1/presione1"
HEALTH_URL = f"{BASE_URL}/health"

def test_health_check():
    """Testa se o servidor está funcionando"""
    try:
        logger.info("=== TESTE DE SAÚDE DO SERVIDOR ===")
        response = requests.get(HEALTH_URL, timeout=5)
        logger.info(f"Status do servidor: {response.status_code}")
        if response.status_code == 200:
            logger.info("Servidor está funcionando corretamente")
            return True
        else:
            logger.error(f"Servidor retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao conectar com o servidor: {e}")
        return False

def list_campaigns():
    """Lista todas as campanhas disponíveis"""
    try:
        logger.info("=== LISTANDO CAMPANHAS ===")
        url = f"{API_BASE}/campanhas"
        logger.info(f"Fazendo GET para: {url}")
        
        response = requests.get(url, timeout=10)
        logger.info(f"Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            campaigns = response.json()
            logger.info(f"Número de campanhas encontradas: {len(campaigns)}")
            
            for i, campaign in enumerate(campaigns, 1):
                logger.info(f"Campanha {i}:")
                logger.info(f"  ID: {campaign.get('id')}")
                logger.info(f"  Nome: {campaign.get('nombre')}")
                logger.info(f"  Ativa: {campaign.get('activa')}")
                logger.info(f"  Pausada: {campaign.get('pausada')}")
                logger.info(f"  Descrição: {campaign.get('descripcion')}")
            
            return campaigns
        else:
            logger.error(f"Erro ao listar campanhas: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão ao listar campanhas: {e}")
        return None

def pause_campaign(campaign_id, motivo="Teste automatizado"):
    """Pausa uma campanha específica"""
    try:
        logger.info(f"=== PAUSANDO CAMPANHA {campaign_id} ===")
        url = f"{API_BASE}/campanhas/{campaign_id}/pausar"
        
        # Payload correto baseado no modelo PausarCampanaRequest
        payload = {
            "pausar": True,
            "motivo": motivo
        }
        
        logger.info(f"URL: {url}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=10)
        logger.info(f"Status da resposta: {response.status_code}")
        logger.info(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info("Campanha pausada com sucesso!")
            return result
        else:
            logger.error(f"Erro ao pausar campanha: {response.status_code}")
            logger.error(f"Detalhes: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão ao pausar campanha: {e}")
        return None

def resume_campaign(campaign_id, motivo="Teste automatizado - retomar"):
    """Retoma uma campanha pausada usando o endpoint /retomar"""
    try:
        logger.info(f"=== RETOMANDO CAMPANHA {campaign_id} ===")
        url = f"{API_BASE}/campanhas/{campaign_id}/retomar"
        
        # Para o endpoint /retomar, pode não precisar de payload ou usar payload vazio
        payload = {
            "motivo": motivo
        }
        
        logger.info(f"URL: {url}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=10)
        logger.info(f"Status da resposta: {response.status_code}")
        logger.info(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info("Campanha retomada com sucesso!")
            return result
        else:
            logger.error(f"Erro ao retomar campanha: {response.status_code}")
            logger.error(f"Detalhes: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão ao retomar campanha: {e}")
        return None

def get_campaign_details(campaign_id):
    """Obtém detalhes de uma campanha específica"""
    try:
        logger.info(f"=== OBTENDO DETALHES DA CAMPANHA {campaign_id} ===")
        url = f"{API_BASE}/campanhas/{campaign_id}"
        
        response = requests.get(url, timeout=10)
        logger.info(f"Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            campaign = response.json()
            logger.info("Detalhes da campanha:")
            logger.info(f"  ID: {campaign.get('id')}")
            logger.info(f"  Nome: {campaign.get('nombre')}")
            logger.info(f"  Ativa: {campaign.get('activa')}")
            logger.info(f"  Pausada: {campaign.get('pausada')}")
            logger.info(f"  Descrição: {campaign.get('descripcion')}")
            return campaign
        else:
            logger.error(f"Erro ao obter detalhes: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão ao obter detalhes: {e}")
        return None

def main():
    """Função principal do teste"""
    logger.info("INICIANDO TESTE DE PAUSE/RESUME - SERVIDOR REAL CORRIGIDO")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info(f"Servidor: {BASE_URL}")
    
    # 1. Teste de saúde
    if not test_health_check():
        logger.error("Servidor não está funcionando. Abortando teste.")
        return
    
    # 2. Listar campanhas
    campaigns = list_campaigns()
    if not campaigns:
        logger.error("Não foi possível obter lista de campanhas. Abortando teste.")
        return
    
    # 3. Selecionar primeira campanha para teste
    if len(campaigns) == 0:
        logger.error("Nenhuma campanha encontrada para teste.")
        return
    
    test_campaign = campaigns[0]
    campaign_id = test_campaign.get('id')
    
    logger.info(f"Campanha selecionada para teste: ID {campaign_id}")
    
    # 4. Obter estado inicial
    logger.info("=== ESTADO INICIAL ===")
    initial_state = get_campaign_details(campaign_id)
    if initial_state:
        initial_paused = initial_state.get('pausada', False)
        logger.info(f"Estado inicial - Pausada: {initial_paused}")
    
    # 5. Pausar campanha
    pause_result = pause_campaign(campaign_id)
    if pause_result:
        logger.info("Aguardando 2 segundos...")
        time.sleep(2)
        
        # Verificar estado após pausar
        logger.info("=== ESTADO APÓS PAUSAR ===")
        after_pause_state = get_campaign_details(campaign_id)
        if after_pause_state:
            paused_after_pause = after_pause_state.get('pausada', False)
            logger.info(f"Estado após pausar - Pausada: {paused_after_pause}")
    
    # 6. Retomar campanha
    resume_result = resume_campaign(campaign_id)
    if resume_result:
        logger.info("Aguardando 2 segundos...")
        time.sleep(2)
        
        # Verificar estado final
        logger.info("=== ESTADO FINAL ===")
        final_state = get_campaign_details(campaign_id)
        if final_state:
            final_paused = final_state.get('pausada', False)
            logger.info(f"Estado final - Pausada: {final_paused}")
    
    logger.info("=== TESTE CONCLUÍDO ===")
    logger.info(f"Timestamp final: {datetime.now()}")

if __name__ == "__main__":
    main()