from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from app.schemas.trunk import TrunkCreate, TrunkUpdate, TrunkResponse
from datetime import datetime
import json

router = APIRouter(prefix="/trunks", tags=["trunks"])

@router.get("/", response_model=dict)
async def get_trunks(db: Session = Depends(get_db)):
    """Buscar todos os trunks"""
    try:
        result = db.execute(text("""
            SELECT 
                id,
                name,
                host,
                prefix,
                codecs,
                max_channels,
                is_active,
                created_at,
                updated_at,
                country_code,
                dv_codes,
                trunk_type,
                sip_config
            FROM trunks 
            ORDER BY created_at DESC
        """))
        
        trunks = []
        for row in result:
            trunk_dict = dict(row._mapping)
            # Converter JSONB para dict se necessário
            if trunk_dict.get('dv_codes') and isinstance(trunk_dict['dv_codes'], str):
                trunk_dict['dv_codes'] = json.loads(trunk_dict['dv_codes'])
            if trunk_dict.get('sip_config') and isinstance(trunk_dict['sip_config'], str):
                trunk_dict['sip_config'] = json.loads(trunk_dict['sip_config'])
            trunks.append(trunk_dict)
        
        return {"trunks": trunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar trunks: {str(e)}")

@router.get("/{trunk_id}", response_model=dict)
async def get_trunk(trunk_id: int, db: Session = Depends(get_db)):
    """Buscar trunk por ID"""
    try:
        result = db.execute(text("""
            SELECT 
                id,
                name,
                host,
                prefix,
                codecs,
                max_channels,
                is_active,
                created_at,
                updated_at,
                country_code,
                dv_codes,
                trunk_type,
                sip_config
            FROM trunks 
            WHERE id = :trunk_id
        """), {"trunk_id": trunk_id})
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        
        trunk_dict = dict(row._mapping)
        # Converter JSONB para dict se necessário
        if trunk_dict.get('dv_codes') and isinstance(trunk_dict['dv_codes'], str):
            trunk_dict['dv_codes'] = json.loads(trunk_dict['dv_codes'])
        if trunk_dict.get('sip_config') and isinstance(trunk_dict['sip_config'], str):
            trunk_dict['sip_config'] = json.loads(trunk_dict['sip_config'])
        
        return {"trunk": trunk_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar trunk: {str(e)}")

@router.post("/", response_model=dict)
async def create_trunk(trunk_data: dict, db: Session = Depends(get_db)):
    """Criar novo trunk"""
    try:
        # Preparar dados
        name = trunk_data.get('name')
        host = trunk_data.get('host')
        country_code = trunk_data.get('country_code')
        dv_codes = trunk_data.get('dv_codes', [])
        max_channels = trunk_data.get('max_channels', 10)
        trunk_type = trunk_data.get('trunk_type', 'dv_voip')
        sip_config = trunk_data.get('sip_config', {})
        
        if not name or not host or not country_code:
            raise HTTPException(status_code=400, detail="Nome, host e código do país são obrigatórios")
        
        # Inserir no banco
        result = db.execute(text("""
            INSERT INTO trunks (
                name, host, country_code, dv_codes, max_channels, 
                trunk_type, sip_config, is_active, created_at, updated_at
            ) VALUES (
                :name, :host, :country_code, :dv_codes, :max_channels,
                :trunk_type, :sip_config, true, NOW(), NOW()
            ) RETURNING id
        """), {
            "name": name,
            "host": host,
            "country_code": country_code,
            "dv_codes": json.dumps(dv_codes),
            "max_channels": max_channels,
            "trunk_type": trunk_type,
            "sip_config": json.dumps(sip_config)
        })
        
        trunk_id = result.fetchone()[0]
        db.commit()
        
        return {"message": "Trunk criado com sucesso", "trunk_id": trunk_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar trunk: {str(e)}")

@router.put("/{trunk_id}", response_model=dict)
async def update_trunk(trunk_id: int, trunk_data: dict, db: Session = Depends(get_db)):
    """Atualizar trunk existente"""
    try:
        # Verificar se trunk existe
        check_result = db.execute(text("SELECT id FROM trunks WHERE id = :trunk_id"), {"trunk_id": trunk_id})
        if not check_result.fetchone():
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        
        # Preparar dados
        name = trunk_data.get('name')
        host = trunk_data.get('host')
        country_code = trunk_data.get('country_code')
        dv_codes = trunk_data.get('dv_codes', [])
        max_channels = trunk_data.get('max_channels', 10)
        trunk_type = trunk_data.get('trunk_type', 'dv_voip')
        sip_config = trunk_data.get('sip_config', {})
        is_active = trunk_data.get('is_active', True)
        
        # Atualizar no banco
        db.execute(text("""
            UPDATE trunks SET
                name = :name,
                host = :host,
                country_code = :country_code,
                dv_codes = :dv_codes,
                max_channels = :max_channels,
                trunk_type = :trunk_type,
                sip_config = :sip_config,
                is_active = :is_active,
                updated_at = NOW()
            WHERE id = :trunk_id
        """), {
            "trunk_id": trunk_id,
            "name": name,
            "host": host,
            "country_code": country_code,
            "dv_codes": json.dumps(dv_codes),
            "max_channels": max_channels,
            "trunk_type": trunk_type,
            "sip_config": json.dumps(sip_config),
            "is_active": is_active
        })
        
        db.commit()
        return {"message": "Trunk atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar trunk: {str(e)}")

@router.delete("/{trunk_id}", response_model=dict)
async def delete_trunk(trunk_id: int, db: Session = Depends(get_db)):
    """Deletar trunk"""
    try:
        # Verificar se trunk existe
        check_result = db.execute(text("SELECT id FROM trunks WHERE id = :trunk_id"), {"trunk_id": trunk_id})
        if not check_result.fetchone():
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        
        # Deletar trunk
        db.execute(text("DELETE FROM trunks WHERE id = :trunk_id"), {"trunk_id": trunk_id})
        db.commit()
        
        return {"message": "Trunk deletado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar trunk: {str(e)}")

@router.get("/{trunk_id}/config", response_model=dict)
async def get_trunk_asterisk_config(trunk_id: int, db: Session = Depends(get_db)):
    """Gerar configuração do Asterisk para o trunk"""
    try:
        result = db.execute(text("""
            SELECT name, host, country_code, dv_codes, sip_config
            FROM trunks 
            WHERE id = :trunk_id AND is_active = true
        """), {"trunk_id": trunk_id})
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        
        trunk = dict(row._mapping)
        sip_config = trunk['sip_config']
        if isinstance(sip_config, str):
            sip_config = json.loads(sip_config)
        
        dv_codes = trunk['dv_codes']
        if isinstance(dv_codes, str):
            dv_codes = json.loads(dv_codes)
        
        # Gerar configuração do Asterisk
        config = f"""[{trunk['name']}]
type={sip_config.get('type', 'friend')}
host={trunk['host']}
dtmfmode={sip_config.get('dtmfmode', 'rfc2833')}
disallow={sip_config.get('disallow', 'all')}
allow={','.join(sip_config.get('allow', ['g729']))}
directmedia={sip_config.get('directmedia', 'nonat')}
qualify={sip_config.get('qualify', 'yes')}

; Configurações específicas do país
; País: +{trunk['country_code']}
; Códigos DV disponíveis: {', '.join(dv_codes) if dv_codes else 'N/A'}

; Exemplo de dialplan
[outbound-{trunk['name']}]
exten => _X.,1,Set(CALLERID(num)=+{trunk['country_code']}xxxxxxxxx)
exten => _X.,n,Dial(SIP/{trunk['name']}/${{EXTEN}})
exten => _X.,n,Hangup()
"""
        
        return {"config": config}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar configuração: {str(e)}")

@router.get("/country/{country_code}", response_model=dict)
async def get_trunks_by_country(country_code: str, db: Session = Depends(get_db)):
    """Buscar trunks por código do país"""
    try:
        result = db.execute(text("""
            SELECT 
                id, name, host, country_code, dv_codes, max_channels, 
                is_active, trunk_type, sip_config
            FROM trunks 
            WHERE country_code = :country_code 
            ORDER BY name
        """), {"country_code": country_code})
        
        trunks = []
        for row in result:
            trunk_dict = dict(row._mapping)
            if trunk_dict.get('dv_codes') and isinstance(trunk_dict['dv_codes'], str):
                trunk_dict['dv_codes'] = json.loads(trunk_dict['dv_codes'])
            if trunk_dict.get('sip_config') and isinstance(trunk_dict['sip_config'], str):
                trunk_dict['sip_config'] = json.loads(trunk_dict['sip_config'])
            trunks.append(trunk_dict)
        
        return {"trunks": trunks, "country_code": country_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar trunks: {str(e)}") 