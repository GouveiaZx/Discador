from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
import logging
from datetime import datetime, time
import pytz

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def get_supabase_config():
    """Obter configuração do Supabase com validação"""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        logger.error("❌ Variáveis de ambiente SUPABASE_URL ou SUPABASE_ANON_KEY não configuradas")
        raise HTTPException(status_code=500, detail="Configuração do Supabase incompleta")
    
    return {
        "url": SUPABASE_URL,
        "headers": {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    }

class TimingConfig(BaseModel):
    id: Optional[int] = None
    name: str
    call_timeout: int
    answer_timeout: int
    between_calls_delay: int
    max_retry_attempts: int
    active: bool = True
    # Configurações de horário
    horario_inicio: Optional[str] = "08:00"
    horario_fim: Optional[str] = "20:00"
    # Timer de almoço
    pausar_almoco: Optional[bool] = False
    horario_almoco_inicio: Optional[str] = "12:00"
    horario_almoco_fim: Optional[str] = "13:00"
    # Dias da semana (1=Segunda, 7=Domingo)
    dias_semana: Optional[List[int]] = [1, 2, 3, 4, 5]
    timezone: Optional[str] = "America/Sao_Paulo"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TimingConfigCreate(BaseModel):
    name: str
    call_timeout: int
    answer_timeout: int
    between_calls_delay: int
    max_retry_attempts: int
    active: bool = True
    # Configurações de horário
    horario_inicio: Optional[str] = "08:00"
    horario_fim: Optional[str] = "20:00"
    # Timer de almoço
    pausar_almoco: Optional[bool] = False
    horario_almoco_inicio: Optional[str] = "12:00"
    horario_almoco_fim: Optional[str] = "13:00"
    # Dias da semana (1=Segunda, 7=Domingo)
    dias_semana: Optional[List[int]] = [1, 2, 3, 4, 5]
    timezone: Optional[str] = "America/Sao_Paulo"

class TimingConfigUpdate(BaseModel):
    name: Optional[str] = None
    call_timeout: Optional[int] = None
    answer_timeout: Optional[int] = None
    between_calls_delay: Optional[int] = None
    max_retry_attempts: Optional[int] = None
    active: Optional[bool] = None
    # Configurações de horário
    horario_inicio: Optional[str] = None
    horario_fim: Optional[str] = None
    # Timer de almoço
    pausar_almoco: Optional[bool] = None
    horario_almoco_inicio: Optional[str] = None
    horario_almoco_fim: Optional[str] = None
    # Dias da semana (1=Segunda, 7=Domingo)
    dias_semana: Optional[List[int]] = None
    timezone: Optional[str] = None

@router.get("/timing", response_model=List[TimingConfig])
async def get_timing_configs():
    """Obter todas as configurações de timing"""
    try:
        logger.info("🔍 Buscando configurações de timing no Supabase")
        
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/timing_configs"
        response = requests.get(url, headers=supabase_config['headers'])
        
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
        
        supabase_config = get_supabase_config()
        # Preparar dados para inserção
        insert_data = {
            "name": config.name,
            "call_timeout": config.call_timeout,
            "answer_timeout": config.answer_timeout,
            "between_calls_delay": config.between_calls_delay,
            "max_retry_attempts": config.max_retry_attempts,
            "active": config.active,
            "horario_inicio": config.horario_inicio,
            "horario_fim": config.horario_fim,
            "pausar_almoco": config.pausar_almoco,
            "horario_almoco_inicio": config.horario_almoco_inicio,
            "horario_almoco_fim": config.horario_almoco_fim,
            "dias_semana": config.dias_semana,
            "timezone": config.timezone,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        url = f"{supabase_config['url']}/rest/v1/timing_configs"
        response = requests.post(url, json=insert_data, headers=supabase_config['headers'])
        
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
        
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/timing_configs?id=eq.{config_id}"
        response = requests.get(url, headers=supabase_config['headers'])
        
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
        
        supabase_config = get_supabase_config()
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
        if config.horario_inicio is not None:
            update_data["horario_inicio"] = config.horario_inicio
        if config.horario_fim is not None:
            update_data["horario_fim"] = config.horario_fim
        if config.pausar_almoco is not None:
            update_data["pausar_almoco"] = config.pausar_almoco
        if config.horario_almoco_inicio is not None:
            update_data["horario_almoco_inicio"] = config.horario_almoco_inicio
        if config.horario_almoco_fim is not None:
            update_data["horario_almoco_fim"] = config.horario_almoco_fim
        if config.dias_semana is not None:
            update_data["dias_semana"] = config.dias_semana
        if config.timezone is not None:
            update_data["timezone"] = config.timezone
            
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        url = f"{supabase_config['url']}/rest/v1/timing_configs?id=eq.{config_id}"
        response = requests.patch(url, json=update_data, headers=supabase_config['headers'])
        
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
        
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/timing_configs?id=eq.{config_id}"
        response = requests.delete(url, headers=supabase_config['headers'])
        
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
                "max_retry_attempts": 2,
                "horario_inicio": "09:00",
                "horario_fim": "18:00",
                "pausar_almoco": True,
                "horario_almoco_inicio": "12:00",
                "horario_almoco_fim": "13:00",
                "dias_semana": [1, 2, 3, 4, 5],
                "timezone": "America/Sao_Paulo"
            },
            {
                "name": "Balanceado",
                "description": "Configuração equilibrada para maior eficiência",
                "call_timeout": 30,
                "answer_timeout": 20,
                "between_calls_delay": 3,
                "max_retry_attempts": 3,
                "horario_inicio": "08:00",
                "horario_fim": "20:00",
                "pausar_almoco": True,
                "horario_almoco_inicio": "12:00",
                "horario_almoco_fim": "13:00",
                "dias_semana": [1, 2, 3, 4, 5],
                "timezone": "America/Sao_Paulo"
            },
            {
                "name": "Agressivo",
                "description": "Configuração para máxima velocidade de discagem",
                "call_timeout": 20,
                "answer_timeout": 15,
                "between_calls_delay": 1,
                "max_retry_attempts": 4,
                "horario_inicio": "08:00",
                "horario_fim": "21:00",
                "pausar_almoco": False,
                "horario_almoco_inicio": "12:00",
                "horario_almoco_fim": "13:00",
                "dias_semana": [1, 2, 3, 4, 5, 6],
                "timezone": "America/Sao_Paulo"
            },
            {
                "name": "Brasil Padrão",
                "description": "Configuração padrão para o Brasil com timer de almoço",
                "call_timeout": 30,
                "answer_timeout": 20,
                "between_calls_delay": 2,
                "max_retry_attempts": 3,
                "horario_inicio": "08:00",
                "horario_fim": "20:00",
                "pausar_almoco": True,
                "horario_almoco_inicio": "12:00",
                "horario_almoco_fim": "14:00",
                "dias_semana": [1, 2, 3, 4, 5],
                "timezone": "America/Sao_Paulo"
            }
        ]
        
        logger.info(f"✅ {len(presets)} presets de timing retornados")
        return presets
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter presets: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter presets de timing")

@router.post("/timing/{config_id}/validar-horario")
async def validar_horario_timing(config_id: int):
    """Validar se o horário atual está dentro dos períodos permitidos"""
    try:
        logger.info(f"🕐 Validando horário para configuração ID: {config_id}")
        
        # Buscar configuração
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/timing_configs?id=eq.{config_id}"
        response = requests.get(url, headers=supabase_config['headers'])
        
        if response.status_code != 200 or not response.json():
            raise HTTPException(status_code=404, detail="Configuração de timing não encontrada")
            
        config = response.json()[0]
        
        # Obter horário atual no timezone configurado
        tz = pytz.timezone(config.get('timezone', 'America/Sao_Paulo'))
        agora = datetime.now(tz)
        hora_atual = agora.time()
        dia_semana = agora.weekday() + 1  # Python usa 0-6, nossa config usa 1-7
        
        # Verificar se é dia da semana permitido
        dias_permitidos = config.get('dias_semana', [1, 2, 3, 4, 5])
        if dia_semana not in dias_permitidos:
            return {
                "permitido": False,
                "motivo": "Dia da semana não permitido",
                "horario_atual": hora_atual.strftime("%H:%M:%S"),
                "dia_semana": dia_semana
            }
        
        # Verificar horário de funcionamento
        inicio = time.fromisoformat(config.get('horario_inicio', '08:00'))
        fim = time.fromisoformat(config.get('horario_fim', '20:00'))
        
        if not (inicio <= hora_atual <= fim):
            return {
                "permitido": False,
                "motivo": "Fora do horário de funcionamento",
                "horario_atual": hora_atual.strftime("%H:%M:%S"),
                "horario_funcionamento": f"{inicio.strftime('%H:%M')} - {fim.strftime('%H:%M')}"
            }
        
        # Verificar timer de almoço
        if config.get('pausar_almoco', False):
            almoco_inicio = time.fromisoformat(config.get('horario_almoco_inicio', '12:00'))
            almoco_fim = time.fromisoformat(config.get('horario_almoco_fim', '13:00'))
            
            if almoco_inicio <= hora_atual <= almoco_fim:
                return {
                    "permitido": False,
                    "motivo": "Horário de almoço - discagem pausada",
                    "horario_atual": hora_atual.strftime("%H:%M:%S"),
                    "horario_almoco": f"{almoco_inicio.strftime('%H:%M')} - {almoco_fim.strftime('%H:%M')}"
                }
        
        return {
            "permitido": True,
            "motivo": "Horário permitido para discagem",
            "horario_atual": hora_atual.strftime("%H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao validar horário: {e}")
        raise HTTPException(status_code=500, detail="Erro ao validar horário")