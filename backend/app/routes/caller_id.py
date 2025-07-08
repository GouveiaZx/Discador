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

class CallerIdConfig(BaseModel):
    id: Optional[int] = None
    name: str
    number: str
    provider: str
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CallerIdConfigCreate(BaseModel):
    name: str
    number: str
    provider: str
    active: bool = True

class CallerIdConfigUpdate(BaseModel):
    name: Optional[str] = None
    number: Optional[str] = None
    provider: Optional[str] = None
    active: Optional[bool] = None

@router.get("/caller_id", response_model=List[CallerIdConfig])
async def get_caller_id_configs():
    """Obter todas as configurações de Caller ID"""
    try:
        logger.info("🔍 Buscando configurações de Caller ID no Supabase")
        
        url = f"{SUPABASE_URL}/rest/v1/caller_id_configs"
        response = requests.get(url, headers=SUPABASE_HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ {len(data)} configurações de Caller ID encontradas")
            return data
        else:
            logger.error(f"❌ Erro ao buscar configurações de Caller ID: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar configurações de Caller ID")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/caller_id", response_model=CallerIdConfig)
async def create_caller_id_config(config: CallerIdConfigCreate):
    """Criar nova configuração de Caller ID"""
    try:
        logger.info(f"🔧 Criando nova configuração de Caller ID: {config.name}")
        
        # Preparar dados para inserção
        insert_data = {
            "name": config.name,
            "number": config.number,
            "provider": config.provider,
            "active": config.active,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        url = f"{SUPABASE_URL}/rest/v1/caller_id_configs"
        response = requests.post(url, json=insert_data, headers=SUPABASE_HEADERS)
        
        if response.status_code == 201:
            data = response.json()
            logger.info(f"✅ Configuração de Caller ID criada com sucesso: ID {data[0].get('id', 'N/A')}")
            return data[0]
        else:
            logger.error(f"❌ Erro ao criar configuração de Caller ID: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao criar configuração de Caller ID")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/caller_id/{config_id}", response_model=CallerIdConfig)
async def get_caller_id_config(config_id: int):
    """Obter configuração específica de Caller ID por ID"""
    try:
        logger.info(f"🔍 Buscando configuração de Caller ID ID: {config_id}")
        
        url = f"{SUPABASE_URL}/rest/v1/caller_id_configs?id=eq.{config_id}"
        response = requests.get(url, headers=SUPABASE_HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                logger.info(f"✅ Configuração de Caller ID encontrada: {data[0]['name']}")
                return data[0]
            else:
                logger.warning(f"⚠️ Configuração de Caller ID não encontrada: ID {config_id}")
                raise HTTPException(status_code=404, detail="Configuração de Caller ID não encontrada")
        else:
            logger.error(f"❌ Erro ao buscar configuração de Caller ID: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar configuração de Caller ID")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/caller_id/{config_id}", response_model=CallerIdConfig)
async def update_caller_id_config(config_id: int, config: CallerIdConfigUpdate):
    """Atualizar configuração de Caller ID"""
    try:
        logger.info(f"🔧 Atualizando configuração de Caller ID ID: {config_id}")
        
        # Preparar dados para atualização (apenas campos não nulos)
        update_data = {}
        if config.name is not None:
            update_data["name"] = config.name
        if config.number is not None:
            update_data["number"] = config.number
        if config.provider is not None:
            update_data["provider"] = config.provider
        if config.active is not None:
            update_data["active"] = config.active
            
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        url = f"{SUPABASE_URL}/rest/v1/caller_id_configs?id=eq.{config_id}"
        response = requests.patch(url, json=update_data, headers=SUPABASE_HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                logger.info(f"✅ Configuração de Caller ID atualizada: {data[0]['name']}")
                return data[0]
            else:
                logger.warning(f"⚠️ Configuração de Caller ID não encontrada para atualização: ID {config_id}")
                raise HTTPException(status_code=404, detail="Configuração de Caller ID não encontrada")
        else:
            logger.error(f"❌ Erro ao atualizar configuração de Caller ID: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao atualizar configuração de Caller ID")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/caller_id/{config_id}")
async def delete_caller_id_config(config_id: int):
    """Deletar configuração de Caller ID"""
    try:
        logger.info(f"🗑️ Deletando configuração de Caller ID ID: {config_id}")
        
        url = f"{SUPABASE_URL}/rest/v1/caller_id_configs?id=eq.{config_id}"
        response = requests.delete(url, headers=SUPABASE_HEADERS)
        
        if response.status_code == 204:
            logger.info(f"✅ Configuração de Caller ID deletada com sucesso: ID {config_id}")
            return {"message": "Configuração de Caller ID deletada com sucesso"}
        elif response.status_code == 404:
            logger.warning(f"⚠️ Configuração de Caller ID não encontrada para deleção: ID {config_id}")
            raise HTTPException(status_code=404, detail="Configuração de Caller ID não encontrada")
        else:
            logger.error(f"❌ Erro ao deletar configuração de Caller ID: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao deletar configuração de Caller ID")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 