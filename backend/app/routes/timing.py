from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from datetime import datetime
import json

router = APIRouter(prefix="/timing-configs", tags=["timing"])

@router.get("/", response_model=dict)
async def get_timing_configs(db: Session = Depends(get_db)):
    """Buscar todas as configurações de timing"""
    try:
        result = db.execute(text("""
            SELECT 
                tc.id,
                tc.campaign_id,
                tc.wait_time,
                tc.sleep_time,
                tc.preset_name,
                tc.progressive_delay,
                tc.adaptive_timing,
                tc.weekend_multiplier,
                tc.night_hours_multiplier,
                tc.retry_attempts,
                tc.retry_interval,
                tc.timeout_settings,
                tc.is_active,
                tc.created_at,
                tc.updated_at
            FROM timing_configs tc
            ORDER BY tc.created_at DESC
        """))
        
        configs = []
        for row in result:
            config_dict = dict(row._mapping)
            # Converter JSONB para dict se necessário
            if config_dict.get('timeout_settings') and isinstance(config_dict['timeout_settings'], str):
                config_dict['timeout_settings'] = json.loads(config_dict['timeout_settings'])
            configs.append(config_dict)
        
        return {"configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar configurações: {str(e)}")

@router.get("/{config_id}", response_model=dict)
async def get_timing_config(config_id: int, db: Session = Depends(get_db)):
    """Buscar configuração de timing por ID"""
    try:
        result = db.execute(text("""
            SELECT 
                tc.id,
                tc.campaign_id,
                tc.wait_time,
                tc.sleep_time,
                tc.preset_name,
                tc.progressive_delay,
                tc.adaptive_timing,
                tc.weekend_multiplier,
                tc.night_hours_multiplier,
                tc.retry_attempts,
                tc.retry_interval,
                tc.timeout_settings,
                tc.is_active,
                tc.created_at,
                tc.updated_at
            FROM timing_configs tc
            WHERE tc.id = :config_id
        """), {"config_id": config_id})
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Configuração não encontrada")
        
        config_dict = dict(row._mapping)
        if config_dict.get('timeout_settings') and isinstance(config_dict['timeout_settings'], str):
            config_dict['timeout_settings'] = json.loads(config_dict['timeout_settings'])
        
        return {"config": config_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar configuração: {str(e)}")

@router.post("/", response_model=dict)
async def create_timing_config(config_data: dict, db: Session = Depends(get_db)):
    """Criar nova configuração de timing"""
    try:
        campaign_id = config_data.get('campaign_id')
        wait_time = config_data.get('wait_time', 30)
        sleep_time = config_data.get('sleep_time', 2)
        preset_name = config_data.get('preset_name', 'balanced')
        progressive_delay = config_data.get('progressive_delay', False)
        adaptive_timing = config_data.get('adaptive_timing', False)
        weekend_multiplier = config_data.get('weekend_multiplier', 1.0)
        night_hours_multiplier = config_data.get('night_hours_multiplier', 1.0)
        retry_attempts = config_data.get('retry_attempts', 3)
        retry_interval = config_data.get('retry_interval', 300)
        timeout_settings = config_data.get('timeout_settings', {})
        
        # Validações básicas
        if wait_time < 5 or wait_time > 120:
            raise HTTPException(status_code=400, detail="Wait time deve estar entre 5 e 120 segundos")
        
        if sleep_time < 1 or sleep_time > 60:
            raise HTTPException(status_code=400, detail="Sleep time deve estar entre 1 e 60 segundos")
        
        if retry_attempts < 0 or retry_attempts > 10:
            raise HTTPException(status_code=400, detail="Retry attempts deve estar entre 0 e 10")
        
        # Verificar se já existe configuração para esta campanha
        if campaign_id:
            existing = db.execute(text("""
                SELECT id FROM timing_configs WHERE campaign_id = :campaign_id
            """), {"campaign_id": campaign_id}).fetchone()
            
            if existing:
                raise HTTPException(status_code=400, detail="Já existe configuração para esta campanha")
        
        # Inserir no banco
        result = db.execute(text("""
            INSERT INTO timing_configs (
                campaign_id, wait_time, sleep_time, preset_name, progressive_delay,
                adaptive_timing, weekend_multiplier, night_hours_multiplier,
                retry_attempts, retry_interval, timeout_settings, is_active,
                created_at, updated_at
            ) VALUES (
                :campaign_id, :wait_time, :sleep_time, :preset_name, :progressive_delay,
                :adaptive_timing, :weekend_multiplier, :night_hours_multiplier,
                :retry_attempts, :retry_interval, :timeout_settings, true,
                NOW(), NOW()
            ) RETURNING id
        """), {
            "campaign_id": campaign_id,
            "wait_time": wait_time,
            "sleep_time": sleep_time,
            "preset_name": preset_name,
            "progressive_delay": progressive_delay,
            "adaptive_timing": adaptive_timing,
            "weekend_multiplier": weekend_multiplier,
            "night_hours_multiplier": night_hours_multiplier,
            "retry_attempts": retry_attempts,
            "retry_interval": retry_interval,
            "timeout_settings": json.dumps(timeout_settings)
        })
        
        config_id = result.fetchone()[0]
        db.commit()
        
        return {"message": "Configuração criada com sucesso", "config_id": config_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar configuração: {str(e)}")

@router.put("/{config_id}", response_model=dict)
async def update_timing_config(config_id: int, config_data: dict, db: Session = Depends(get_db)):
    """Atualizar configuração de timing"""
    try:
        # Verificar se configuração existe
        check_result = db.execute(text("SELECT id FROM timing_configs WHERE id = :config_id"), {"config_id": config_id})
        if not check_result.fetchone():
            raise HTTPException(status_code=404, detail="Configuração não encontrada")
        
        wait_time = config_data.get('wait_time', 30)
        sleep_time = config_data.get('sleep_time', 2)
        preset_name = config_data.get('preset_name', 'balanced')
        progressive_delay = config_data.get('progressive_delay', False)
        adaptive_timing = config_data.get('adaptive_timing', False)
        weekend_multiplier = config_data.get('weekend_multiplier', 1.0)
        night_hours_multiplier = config_data.get('night_hours_multiplier', 1.0)
        retry_attempts = config_data.get('retry_attempts', 3)
        retry_interval = config_data.get('retry_interval', 300)
        timeout_settings = config_data.get('timeout_settings', {})
        is_active = config_data.get('is_active', True)
        
        # Validações básicas
        if wait_time < 5 or wait_time > 120:
            raise HTTPException(status_code=400, detail="Wait time deve estar entre 5 e 120 segundos")
        
        if sleep_time < 1 or sleep_time > 60:
            raise HTTPException(status_code=400, detail="Sleep time deve estar entre 1 e 60 segundos")
        
        if retry_attempts < 0 or retry_attempts > 10:
            raise HTTPException(status_code=400, detail="Retry attempts deve estar entre 0 e 10")
        
        # Atualizar no banco
        db.execute(text("""
            UPDATE timing_configs SET
                wait_time = :wait_time,
                sleep_time = :sleep_time,
                preset_name = :preset_name,
                progressive_delay = :progressive_delay,
                adaptive_timing = :adaptive_timing,
                weekend_multiplier = :weekend_multiplier,
                night_hours_multiplier = :night_hours_multiplier,
                retry_attempts = :retry_attempts,
                retry_interval = :retry_interval,
                timeout_settings = :timeout_settings,
                is_active = :is_active,
                updated_at = NOW()
            WHERE id = :config_id
        """), {
            "config_id": config_id,
            "wait_time": wait_time,
            "sleep_time": sleep_time,
            "preset_name": preset_name,
            "progressive_delay": progressive_delay,
            "adaptive_timing": adaptive_timing,
            "weekend_multiplier": weekend_multiplier,
            "night_hours_multiplier": night_hours_multiplier,
            "retry_attempts": retry_attempts,
            "retry_interval": retry_interval,
            "timeout_settings": json.dumps(timeout_settings),
            "is_active": is_active
        })
        
        db.commit()
        return {"message": "Configuração atualizada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar configuração: {str(e)}")

@router.delete("/{config_id}", response_model=dict)
async def delete_timing_config(config_id: int, db: Session = Depends(get_db)):
    """Deletar configuração de timing"""
    try:
        # Verificar se configuração existe
        check_result = db.execute(text("SELECT id FROM timing_configs WHERE id = :config_id"), {"config_id": config_id})
        if not check_result.fetchone():
            raise HTTPException(status_code=404, detail="Configuração não encontrada")
        
        # Deletar configuração
        db.execute(text("DELETE FROM timing_configs WHERE id = :config_id"), {"config_id": config_id})
        db.commit()
        
        return {"message": "Configuração deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar configuração: {str(e)}")

@router.get("/campaign/{campaign_id}", response_model=dict)
async def get_timing_config_by_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Buscar configuração de timing por campanha"""
    try:
        result = db.execute(text("""
            SELECT 
                tc.id,
                tc.campaign_id,
                tc.wait_time,
                tc.sleep_time,
                tc.preset_name,
                tc.progressive_delay,
                tc.adaptive_timing,
                tc.weekend_multiplier,
                tc.night_hours_multiplier,
                tc.retry_attempts,
                tc.retry_interval,
                tc.timeout_settings,
                tc.is_active
            FROM timing_configs tc
            WHERE tc.campaign_id = :campaign_id AND tc.is_active = true
        """), {"campaign_id": campaign_id})
        
        row = result.fetchone()
        if not row:
            return {"config": None, "message": "Nenhuma configuração encontrada para esta campanha"}
        
        config_dict = dict(row._mapping)
        if config_dict.get('timeout_settings') and isinstance(config_dict['timeout_settings'], str):
            config_dict['timeout_settings'] = json.loads(config_dict['timeout_settings'])
        
        return {"config": config_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar configuração: {str(e)}")

@router.get("/presets", response_model=dict)
async def get_timing_presets():
    """Obter presets de configuração de timing"""
    try:
        presets = [
            {
                "id": "aggressive",
                "name": "Agressivo",
                "description": "Máximo de chamadas por minuto",
                "settings": {
                    "wait_time": 20,
                    "sleep_time": 1,
                    "progressive_delay": False,
                    "adaptive_timing": False,
                    "retry_attempts": 5,
                    "retry_interval": 180,
                    "weekend_multiplier": 1.0,
                    "night_hours_multiplier": 1.0
                }
            },
            {
                "id": "balanced",
                "name": "Balanceado",
                "description": "Equilíbrio entre volume e qualidade",
                "settings": {
                    "wait_time": 30,
                    "sleep_time": 2,
                    "progressive_delay": True,
                    "adaptive_timing": False,
                    "retry_attempts": 3,
                    "retry_interval": 300,
                    "weekend_multiplier": 1.5,
                    "night_hours_multiplier": 1.5
                }
            },
            {
                "id": "conservative",
                "name": "Conservador",
                "description": "Prioriza qualidade de conexão",
                "settings": {
                    "wait_time": 45,
                    "sleep_time": 5,
                    "progressive_delay": True,
                    "adaptive_timing": True,
                    "retry_attempts": 2,
                    "retry_interval": 600,
                    "weekend_multiplier": 2.0,
                    "night_hours_multiplier": 2.0
                }
            }
        ]
        
        return {"presets": presets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter presets: {str(e)}")

@router.post("/calculate-stats", response_model=dict)
async def calculate_timing_stats(config_data: dict):
    """Calcular estatísticas baseadas na configuração de timing"""
    try:
        wait_time = config_data.get('wait_time', 30)
        sleep_time = config_data.get('sleep_time', 2)
        retry_attempts = config_data.get('retry_attempts', 3)
        retry_interval = config_data.get('retry_interval', 300)
        
        # Cálculos básicos
        total_time_per_call = wait_time + sleep_time
        calls_per_minute = 60 / total_time_per_call if total_time_per_call > 0 else 0
        calls_per_hour = calls_per_minute * 60
        calls_per_day = calls_per_hour * 8  # assumindo 8h de trabalho
        
        # Tempo total considerando retries
        max_time_with_retries = wait_time + (retry_attempts * (wait_time + retry_interval))
        
        return {
            "calls_per_minute": round(calls_per_minute, 2),
            "calls_per_hour": round(calls_per_hour, 0),
            "calls_per_day": round(calls_per_day, 0),
            "total_time_per_call": total_time_per_call,
            "max_time_with_retries": max_time_with_retries,
            "efficiency_score": min(100, round((calls_per_minute / 30) * 100, 1))  # score baseado em 30 calls/min = 100%
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular estatísticas: {str(e)}")

@router.get("/global", response_model=dict)
async def get_global_timing_configs(db: Session = Depends(get_db)):
    """Buscar configurações globais de timing (não associadas a campanhas específicas)"""
    try:
        result = db.execute(text("""
            SELECT 
                tc.id,
                tc.wait_time,
                tc.sleep_time,
                tc.preset_name,
                tc.progressive_delay,
                tc.adaptive_timing,
                tc.weekend_multiplier,
                tc.night_hours_multiplier,
                tc.retry_attempts,
                tc.retry_interval,
                tc.timeout_settings,
                tc.is_active
            FROM timing_configs tc
            WHERE tc.campaign_id IS NULL AND tc.is_active = true
            ORDER BY tc.preset_name
        """))
        
        configs = []
        for row in result:
            config_dict = dict(row._mapping)
            if config_dict.get('timeout_settings') and isinstance(config_dict['timeout_settings'], str):
                config_dict['timeout_settings'] = json.loads(config_dict['timeout_settings'])
            configs.append(config_dict)
        
        return {"configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar configurações globais: {str(e)}") 