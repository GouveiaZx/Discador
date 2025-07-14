#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das funcionalidades de pausar/retomar campanhas com logging detalhado
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
        logging.FileHandler(f'{log_dir}/test_pause_resume.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('test_pause_resume')

def test_pause_resume_with_logging():
    """Teste das APIs de pausar/retomar com logging detalhado."""
    base_url = "http://127.0.0.1:8000/api/v1/presione1"
    
    logger.info("🔍 Iniciando teste de pausar/retomar campanhas...")
    
    try:
        # 1. Listar campanhas
        logger.info("\n1. Listando campanhas disponíveis...")
        response = requests.get(f"{base_url}/campanhas")
        logger.info(f"Status da listagem: {response.status_code}")
        
        if response.status_code == 200:
            campanhas = response.json()
            logger.info(f"✅ {len(campanhas)} campanhas encontradas")
            
            if not campanhas:
                logger.warning("⚠️ Nenhuma campanha encontrada")
                return
            
            # Usar a primeira campanha
            campanha = campanhas[0]
            campanha_id = campanha.get('id') or campanha.get('campaign_id')
            logger.info(f"📋 Testando com campanha ID: {campanha_id} - {campanha.get('nombre', 'N/A')}")
            logger.info(f"📊 Estado inicial: activa={campanha.get('activa')}, pausada={campanha.get('pausada')}")
            
            # 2. Testar pausar
            logger.info("\n2. Testando pausar campanha...")
            pause_data = {"pausar": True, "motivo": "Teste automatizado"}
            logger.info(f"📤 Enviando dados: {pause_data}")
            
            response = requests.post(f"{base_url}/campanhas/{campanha_id}/pausar", json=pause_data)
            logger.info(f"📥 Status pausar: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Resposta pausar: {result}")
                
                # 3. Verificar estado após pausar
                logger.info("\n3. Verificando estado após pausar...")
                response = requests.get(f"{base_url}/campanhas")
                if response.status_code == 200:
                    campanhas_atualizadas = response.json()
                    campanha_pausada = next((c for c in campanhas_atualizadas if (c.get('id') or c.get('campaign_id')) == campanha_id), None)
                    if campanha_pausada:
                        logger.info(f"📊 Estado após pausar: activa={campanha_pausada.get('activa')}, pausada={campanha_pausada.get('pausada')}")
                    else:
                        logger.warning("⚠️ Campanha não encontrada após pausar")
                
                # 4. Testar retomar
                logger.info("\n4. Testando retomar campanha...")
                resume_data = {"pausar": False, "motivo": "Teste automatizado - retomar"}
                logger.info(f"📤 Enviando dados: {resume_data}")
                
                response = requests.post(f"{base_url}/campanhas/{campanha_id}/pausar", json=resume_data)
                logger.info(f"📥 Status retomar: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Resposta retomar: {result}")
                    
                    # 5. Verificar estado final
                    logger.info("\n5. Verificando estado final...")
                    response = requests.get(f"{base_url}/campanhas")
                    if response.status_code == 200:
                        campanhas_finais = response.json()
                        campanha_final = next((c for c in campanhas_finais if (c.get('id') or c.get('campaign_id')) == campanha_id), None)
                        if campanha_final:
                            logger.info(f"📊 Estado final: activa={campanha_final.get('activa')}, pausada={campanha_final.get('pausada')}")
                        else:
                            logger.warning("⚠️ Campanha não encontrada no estado final")
                    else:
                        logger.error(f"❌ Erro ao verificar estado final: {response.text}")
                else:
                    logger.error(f"❌ Erro ao retomar: {response.text}")
            else:
                logger.error(f"❌ Erro ao pausar: {response.text}")
        else:
            logger.error(f"❌ Erro ao listar campanhas: {response.text}")
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Erro de conexão. Verifique se o servidor está rodando em http://127.0.0.1:8000")
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {str(e)}")
    
    logger.info("\n🏁 Teste finalizado!")
    logger.info(f"📁 Logs salvos em: {os.path.abspath(f'{log_dir}/test_pause_resume.log')}")

if __name__ == "__main__":
    test_pause_resume_with_logging()
