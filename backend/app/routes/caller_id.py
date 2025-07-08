from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from datetime import datetime
import json

router = APIRouter(prefix="/caller-id-configs", tags=["caller-id"])

@router.get("/", response_model=dict)
async def get_caller_id_configs(db: Session = Depends(get_db)):
    """Buscar todas as configurações de Caller ID"""
    try:
        result = db.execute(text("""
            SELECT 
                cid.id,
                cid.trunk_id,
                cid.campaign_id,
                cid.caller_name,
                cid.caller_number,
                cid.is_randomized,
                cid.caller_pool,
                cid.is_active,
                cid.created_at,
                cid.updated_at,
                t.name as trunk_name,
                t.country_code
            FROM caller_id_configs cid
            LEFT JOIN trunks t ON cid.trunk_id = t.id
            ORDER BY cid.created_at DESC
        """))
        
        configs = []
        for row in result:
            config_dict = dict(row._mapping)
            # Converter JSONB para dict se necessário
            if config_dict.get('caller_pool') and isinstance(config_dict['caller_pool'], str):
                config_dict['caller_pool'] = json.loads(config_dict['caller_pool'])
            configs.append(config_dict)
        
        return {"configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar configurações: {str(e)}")

@router.get("/{config_id}", response_model=dict)
async def get_caller_id_config(config_id: int, db: Session = Depends(get_db)):
    """Buscar configuração de Caller ID por ID"""
    try:
        result = db.execute(text("""
            SELECT 
                cid.id,
                cid.trunk_id,
                cid.campaign_id,
                cid.caller_name,
                cid.caller_number,
                cid.is_randomized,
                cid.caller_pool,
                cid.is_active,
                cid.created_at,
                cid.updated_at,
                t.name as trunk_name,
                t.country_code
            FROM caller_id_configs cid
            LEFT JOIN trunks t ON cid.trunk_id = t.id
            WHERE cid.id = :config_id
        """), {"config_id": config_id})
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Configuração não encontrada")
        
        config_dict = dict(row._mapping)
        if config_dict.get('caller_pool') and isinstance(config_dict['caller_pool'], str):
            config_dict['caller_pool'] = json.loads(config_dict['caller_pool'])
        
        return {"config": config_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar configuração: {str(e)}")

@router.post("/", response_model=dict)
async def create_caller_id_config(config_data: dict, db: Session = Depends(get_db)):
    """Criar nova configuração de Caller ID"""
    try:
        trunk_id = config_data.get('trunk_id')
        campaign_id = config_data.get('campaign_id')
        caller_name = config_data.get('caller_name')
        caller_number = config_data.get('caller_number')
        is_randomized = config_data.get('is_randomized', False)
        caller_pool = config_data.get('caller_pool', [])
        
        if not caller_name or not caller_number:
            raise HTTPException(status_code=400, detail="Nome e número do caller são obrigatórios")
        
        if not trunk_id and not campaign_id:
            raise HTTPException(status_code=400, detail="Trunk ID ou Campaign ID deve ser fornecido")
        
        # Verificar se já existe configuração para este trunk/campanha
        check_query = ""
        check_params = {}
        
        if trunk_id:
            check_query = "SELECT id FROM caller_id_configs WHERE trunk_id = :trunk_id"
            check_params = {"trunk_id": trunk_id}
        else:
            check_query = "SELECT id FROM caller_id_configs WHERE campaign_id = :campaign_id"
            check_params = {"campaign_id": campaign_id}
        
        existing = db.execute(text(check_query), check_params).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Já existe configuração para este trunk/campanha")
        
        # Inserir no banco
        result = db.execute(text("""
            INSERT INTO caller_id_configs (
                trunk_id, campaign_id, caller_name, caller_number, 
                is_randomized, caller_pool, is_active, created_at, updated_at
            ) VALUES (
                :trunk_id, :campaign_id, :caller_name, :caller_number,
                :is_randomized, :caller_pool, true, NOW(), NOW()
            ) RETURNING id
        """), {
            "trunk_id": trunk_id,
            "campaign_id": campaign_id,
            "caller_name": caller_name,
            "caller_number": caller_number,
            "is_randomized": is_randomized,
            "caller_pool": json.dumps(caller_pool)
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
async def update_caller_id_config(config_id: int, config_data: dict, db: Session = Depends(get_db)):
    """Atualizar configuração de Caller ID"""
    try:
        # Verificar se configuração existe
        check_result = db.execute(text("SELECT id FROM caller_id_configs WHERE id = :config_id"), {"config_id": config_id})
        if not check_result.fetchone():
            raise HTTPException(status_code=404, detail="Configuração não encontrada")
        
        caller_name = config_data.get('caller_name')
        caller_number = config_data.get('caller_number')
        is_randomized = config_data.get('is_randomized', False)
        caller_pool = config_data.get('caller_pool', [])
        is_active = config_data.get('is_active', True)
        
        # Atualizar no banco
        db.execute(text("""
            UPDATE caller_id_configs SET
                caller_name = :caller_name,
                caller_number = :caller_number,
                is_randomized = :is_randomized,
                caller_pool = :caller_pool,
                is_active = :is_active,
                updated_at = NOW()
            WHERE id = :config_id
        """), {
            "config_id": config_id,
            "caller_name": caller_name,
            "caller_number": caller_number,
            "is_randomized": is_randomized,
            "caller_pool": json.dumps(caller_pool),
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
async def delete_caller_id_config(config_id: int, db: Session = Depends(get_db)):
    """Deletar configuração de Caller ID"""
    try:
        # Verificar se configuração existe
        check_result = db.execute(text("SELECT id FROM caller_id_configs WHERE id = :config_id"), {"config_id": config_id})
        if not check_result.fetchone():
            raise HTTPException(status_code=404, detail="Configuração não encontrada")
        
        # Deletar configuração
        db.execute(text("DELETE FROM caller_id_configs WHERE id = :config_id"), {"config_id": config_id})
        db.commit()
        
        return {"message": "Configuração deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar configuração: {str(e)}")

@router.get("/trunk/{trunk_id}", response_model=dict)
async def get_caller_id_config_by_trunk(trunk_id: int, db: Session = Depends(get_db)):
    """Buscar configuração de Caller ID por trunk"""
    try:
        result = db.execute(text("""
            SELECT 
                cid.id,
                cid.trunk_id,
                cid.caller_name,
                cid.caller_number,
                cid.is_randomized,
                cid.caller_pool,
                cid.is_active,
                t.name as trunk_name,
                t.country_code
            FROM caller_id_configs cid
            JOIN trunks t ON cid.trunk_id = t.id
            WHERE cid.trunk_id = :trunk_id AND cid.is_active = true
        """), {"trunk_id": trunk_id})
        
        row = result.fetchone()
        if not row:
            return {"config": None, "message": "Nenhuma configuração encontrada para este trunk"}
        
        config_dict = dict(row._mapping)
        if config_dict.get('caller_pool') and isinstance(config_dict['caller_pool'], str):
            config_dict['caller_pool'] = json.loads(config_dict['caller_pool'])
        
        return {"config": config_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar configuração: {str(e)}")

@router.get("/campaign/{campaign_id}", response_model=dict)
async def get_caller_id_config_by_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Buscar configuração de Caller ID por campanha"""
    try:
        result = db.execute(text("""
            SELECT 
                cid.id,
                cid.campaign_id,
                cid.caller_name,
                cid.caller_number,
                cid.is_randomized,
                cid.caller_pool,
                cid.is_active
            FROM caller_id_configs cid
            WHERE cid.campaign_id = :campaign_id AND cid.is_active = true
        """), {"campaign_id": campaign_id})
        
        row = result.fetchone()
        if not row:
            return {"config": None, "message": "Nenhuma configuração encontrada para esta campanha"}
        
        config_dict = dict(row._mapping)
        if config_dict.get('caller_pool') and isinstance(config_dict['caller_pool'], str):
            config_dict['caller_pool'] = json.loads(config_dict['caller_pool'])
        
        return {"config": config_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar configuração: {str(e)}")

@router.post("/random-caller/{config_id}", response_model=dict)
async def get_random_caller_id(config_id: int, db: Session = Depends(get_db)):
    """Obter um Caller ID aleatório do pool (para uso durante discagem)"""
    try:
        result = db.execute(text("""
            SELECT caller_name, caller_number, is_randomized, caller_pool
            FROM caller_id_configs 
            WHERE id = :config_id AND is_active = true
        """), {"config_id": config_id})
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Configuração não encontrada")
        
        config = dict(row._mapping)
        
        if not config['is_randomized'] or not config['caller_pool']:
            # Usar configuração padrão
            return {
                "caller_name": config['caller_name'],
                "caller_number": config['caller_number']
            }
        
        # Selecionar aleatoriamente do pool
        import random
        caller_pool = config['caller_pool']
        if isinstance(caller_pool, str):
            caller_pool = json.loads(caller_pool)
        
        if not caller_pool:
            return {
                "caller_name": config['caller_name'],
                "caller_number": config['caller_number']
            }
        
        selected = random.choice(caller_pool)
        return {
            "caller_name": selected.get('name', config['caller_name']),
            "caller_number": selected.get('number', config['caller_number'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter Caller ID: {str(e)}") 