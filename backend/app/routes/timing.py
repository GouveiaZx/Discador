from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    logger.error("❌ Variáveis de ambiente SUPABASE_URL ou SUPABASE_ANON_KEY não configuradas")
    raise ValueError("Configuração do Supabase incompleta")

# Headers para requests do Supabase
SUPABASE_HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

class TimingConfig(BaseModel):
    id: Optional[int] = None
    name: str
    call_timeout: int
    answer_timeout: int
    between_calls_delay: int
    max_retry_attempts: int
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TimingConfigCreate(BaseModel):
    name: str
    call_timeout: int
    answer_timeout: int
    between_calls_delay: int
    max_retry_attempts: int
    active: bool = True

class TimingConfigUpdate(BaseModel):
    name: Optional[str] = None
    call_timeout: Optional[int] = None
    answer_timeout: Optional[int] = None
    between_calls_delay: Optional[int] = None
    max_retry_attempts: Optional[int] = None
    active: Optional[bool] = None

@router.get("/timing", response_model=List[TimingConfig])
async def get_timing_configs():
    """Obter todas as configurações de timing"""
    try:
        logger.info("🔍 Buscando configurações de timing no Supabase")
        
        url = f"{SUPABASE_URL}/rest/v1/timing_configs"
        response = requests.get(url, headers=SUPABASE_HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ {len(data)} configurações de timing encontradas")
            return data
        else:
            logger.error(f"❌ Erro ao buscar configurações de timing: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar configurações de timing")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/timing", response_model=TimingConfig)
async def create_timing_config(config: TimingConfigCreate):
    """Criar nova configuração de timing"""
    try:
        logger.info(f"🔧 Criando nova configuração de timing: {config.name}")
        
        # Preparar dados para inserção
        insert_data = {
            "name": config.name,
            "call_timeout": config.call_timeout,
            "answer_timeout": config.answer_timeout,
            "between_calls_delay": config.between_calls_delay,
            "max_retry_attempts": config.max_retry_attempts,
            "active": config.active,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        url = f"{SUPABASE_URL}/rest/v1/timing_configs"
        response = requests.post(url, json=insert_data, headers=SUPABASE_HEADERS)
        
        if response.status_code == 201:
            data = response.json()
            logger.info(f"✅ Configuração de timing criada com sucesso: ID {data[0].get('id', 'N/A')}")
            return data[0]
        else:
            logger.error(f"❌ Erro ao criar configuração de timing: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao criar configuração de timing")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/timing/{config_id}", response_model=TimingConfig)
async def get_timing_config(config_id: int):
    """Obter configuração específica de timing por ID"""
    try:
        logger.info(f"🔍 Buscando configuração de timing ID: {config_id}")
        
        url = f"{SUPABASE_URL}/rest/v1/timing_configs?id=eq.{config_id}"
        response = requests.get(url, headers=SUPABASE_HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                logger.info(f"✅ Configuração de timing encontrada: {data[0]['name']}")
                return data[0]
            else:
                logger.warning(f"⚠️ Configuração de timing não encontrada: ID {config_id}")
                raise HTTPException(status_code=404, detail="Configuração de timing não encontrada")
        else:
            logger.error(f"❌ Erro ao buscar configuração de timing: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar configuração de timing")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/timing/{config_id}", response_model=TimingConfig)
async def update_timing_config(config_id: int, config: TimingConfigUpdate):
    """Atualizar configuração de timing"""
    try:
        logger.info(f"🔧 Atualizando configuração de timing ID: {config_id}")
        
        # Preparar dados para atualização (apenas campos não nulos)
        update_data = {}
        if config.name is not None:
            update_data["name"] = config.name
        if config.call_timeout is not None:
            update_data["call_timeout"] = config.call_timeout
        if config.answer_timeout is not None:
            update_data["answer_timeout"] = config.answer_timeout
        if config.between_calls_delay is not None:
            update_data["between_calls_delay"] = config.between_calls_delay
        if config.max_retry_attempts is not None:
            update_data["max_retry_attempts"] = config.max_retry_attempts
        if config.active is not None:
            update_data["active"] = config.active
            
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        url = f"{SUPABASE_URL}/rest/v1/timing_configs?id=eq.{config_id}"
        response = requests.patch(url, json=update_data, headers=SUPABASE_HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                logger.info(f"✅ Configuração de timing atualizada: {data[0]['name']}")
                return data[0]
            else:
                logger.warning(f"⚠️ Configuração de timing não encontrada para atualização: ID {config_id}")
                raise HTTPException(status_code=404, detail="Configuração de timing não encontrada")
        else:
            logger.error(f"❌ Erro ao atualizar configuração de timing: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao atualizar configuração de timing")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/timing/{config_id}")
async def delete_timing_config(config_id: int):
    """Deletar configuração de timing"""
    try:
        logger.info(f"🗑️ Deletando configuração de timing ID: {config_id}")
        
        url = f"{SUPABASE_URL}/rest/v1/timing_configs?id=eq.{config_id}"
        response = requests.delete(url, headers=SUPABASE_HEADERS)
        
        if response.status_code == 204:
            logger.info(f"✅ Configuração de timing deletada com sucesso: ID {config_id}")
            return {"message": "Configuração de timing deletada com sucesso"}
        elif response.status_code == 404:
            logger.warning(f"⚠️ Configuração de timing não encontrada para deleção: ID {config_id}")
            raise HTTPException(status_code=404, detail="Configuração de timing não encontrada")
        else:
            logger.error(f"❌ Erro ao deletar configuração de timing: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao deletar configuração de timing")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Endpoints para configurações pré-definidas
@router.get("/timing/presets", response_model=List[dict])
async def get_timing_presets():
    """Obter configurações de timing pré-definidas"""
    try:
        logger.info("📋 Obtendo presets de timing")
        
        presets = [
            {
                "name": "Conservador",
                "description": "Configuração para discagem respeitosa",
                "call_timeout": 45,
                "answer_timeout": 25,
                "between_calls_delay": 5,
                "max_retry_attempts": 2
            },
            {
                "name": "Balanceado",
                "description": "Configuração equilibrada para maior eficiência",
                "call_timeout": 30,
                "answer_timeout": 20,
                "between_calls_delay": 3,
                "max_retry_attempts": 3
            },
            {
                "name": "Agressivo",
                "description": "Configuração para máxima velocidade de discagem",
                "call_timeout": 20,
                "answer_timeout": 15,
                "between_calls_delay": 1,
                "max_retry_attempts": 4
            }
        ]
        
        logger.info(f"✅ {len(presets)} presets de timing retornados")
        return presets
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter presets: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter presets de timing") 