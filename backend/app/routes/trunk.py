from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json
import os
import requests
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trunks", tags=["trunks"])

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

@router.get("/", response_model=dict)
async def get_trunks():
    """Buscar todos os trunks"""
    try:
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/trunks"
        response = requests.get(url, headers=supabase_config['headers'])
        
        if response.status_code == 200:
            trunks = response.json()
            # Converter JSONB strings para dict
            for trunk in trunks:
                if trunk.get('dv_codes') and isinstance(trunk['dv_codes'], str):
                    trunk['dv_codes'] = json.loads(trunk['dv_codes'])
                if trunk.get('sip_config') and isinstance(trunk['sip_config'], str):
                    trunk['sip_config'] = json.loads(trunk['sip_config'])
            
            return {"trunks": trunks}
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar trunks do Supabase")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com Supabase: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar trunks: {str(e)}")

@router.get("/{trunk_id}", response_model=dict)
async def get_trunk(trunk_id: int):
    """Buscar trunk por ID"""
    try:
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/trunks?id=eq.{trunk_id}"
        response = requests.get(url, headers=supabase_config['headers'])
        
        if response.status_code == 200:
            trunks = response.json()
            if not trunks:
                raise HTTPException(status_code=404, detail="Trunk não encontrado")
            
            trunk = trunks[0]
            # Converter JSONB strings para dict
            if trunk.get('dv_codes') and isinstance(trunk['dv_codes'], str):
                trunk['dv_codes'] = json.loads(trunk['dv_codes'])
            if trunk.get('sip_config') and isinstance(trunk['sip_config'], str):
                trunk['sip_config'] = json.loads(trunk['sip_config'])
            
            return {"trunk": trunk}
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar trunk do Supabase")
    except HTTPException:
        raise
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com Supabase: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar trunk: {str(e)}")

@router.post("/", response_model=dict)
async def create_trunk(trunk_data: dict):
    """Criar novo trunk"""
    try:
        print(f"🔵 [TRUNK-CREATE] Recebendo dados: {trunk_data}")
        
        # Preparar dados
        name = trunk_data.get('name')
        host = trunk_data.get('host')
        country_code = trunk_data.get('country_code')
        dv_codes = trunk_data.get('dv_codes', [])
        max_channels = trunk_data.get('max_channels', 10)
        trunk_type = trunk_data.get('trunk_type', 'dv_voip')
        sip_config = trunk_data.get('sip_config', {})
        
        print(f"🔵 [TRUNK-CREATE] Dados processados - name: {name}, host: {host}, country: {country_code}")
        
        if not name or not host or not country_code:
            error_msg = f"Nome, host e código do país são obrigatórios. Recebido: name={name}, host={host}, country_code={country_code}"
            print(f"❌ [TRUNK-CREATE] Validação falhou: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Dados para inserção
        insert_data = {
            "name": name,
            "host": host,
            "country_code": country_code,
            "dv_codes": dv_codes,
            "max_channels": max_channels,
            "trunk_type": trunk_type,
            "sip_config": sip_config,
            "is_active": True
        }
        
        print(f"🔵 [TRUNK-CREATE] Dados para inserção: {insert_data}")
        
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/trunks"
        print(f"🔵 [TRUNK-CREATE] URL Supabase: {url}")
        
        # Adicionar header para retornar os dados criados
        create_headers = supabase_config['headers']
        response = requests.post(url, headers=create_headers, json=insert_data)
        
        print(f"🔵 [TRUNK-CREATE] Resposta Supabase: Status={response.status_code}, Text={response.text[:200]}")
        
        if response.status_code == 201:
            created_trunk = response.json()
            print(f"🔵 [TRUNK-CREATE] Resposta completa: {created_trunk}")
            
            if created_trunk and len(created_trunk) > 0:
                trunk_id = created_trunk[0].get('id', 'N/A')
                print(f"✅ [TRUNK-CREATE] Trunk criado com sucesso: ID={trunk_id}")
                return {"message": "Trunk criado com sucesso", "trunk": created_trunk[0]}
            else:
                print("✅ [TRUNK-CREATE] Trunk criado (sem dados de retorno)")
                return {"message": "Trunk criado com sucesso", "trunk": None}
        else:
            error_detail = f"Erro ao criar trunk no Supabase. Status: {response.status_code}, Response: {response.text}"
            print(f"❌ [TRUNK-CREATE] {error_detail}")
            raise HTTPException(status_code=response.status_code, detail=error_detail)
            
    except HTTPException:
        raise
    except requests.RequestException as e:
        error_msg = f"Erro de conexão com Supabase: {str(e)}"
        print(f"❌ [TRUNK-CREATE] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Erro ao criar trunk: {str(e)}"
        print(f"❌ [TRUNK-CREATE] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.put("/{trunk_id}", response_model=dict)
async def update_trunk(trunk_id: int, trunk_data: dict):
    """Atualizar trunk existente"""
    try:
        # Preparar dados para atualização
        update_data = {}
        
        if 'name' in trunk_data:
            update_data['name'] = trunk_data['name']
        if 'host' in trunk_data:
            update_data['host'] = trunk_data['host']
        if 'country_code' in trunk_data:
            update_data['country_code'] = trunk_data['country_code']
        if 'dv_codes' in trunk_data:
            update_data['dv_codes'] = trunk_data['dv_codes']
        if 'max_channels' in trunk_data:
            update_data['max_channels'] = trunk_data['max_channels']
        if 'trunk_type' in trunk_data:
            update_data['trunk_type'] = trunk_data['trunk_type']
        if 'sip_config' in trunk_data:
            update_data['sip_config'] = trunk_data['sip_config']
        if 'is_active' in trunk_data:
            update_data['is_active'] = trunk_data['is_active']
        
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/trunks?id=eq.{trunk_id}"
        response = requests.patch(url, headers=supabase_config['headers'], json=update_data)
        
        if response.status_code == 204:
            return {"message": "Trunk atualizado com sucesso"}
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao atualizar trunk no Supabase")
            
    except HTTPException:
        raise
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com Supabase: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar trunk: {str(e)}")

@router.delete("/{trunk_id}", response_model=dict)
async def delete_trunk(trunk_id: int):
    """Deletar trunk"""
    try:
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/trunks?id=eq.{trunk_id}"
        response = requests.delete(url, headers=supabase_config['headers'])
        
        if response.status_code == 204:
            return {"message": "Trunk deletado com sucesso"}
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao deletar trunk no Supabase")
            
    except HTTPException:
        raise
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com Supabase: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar trunk: {str(e)}")

@router.get("/country/{country_code}", response_model=dict)
async def get_trunks_by_country(country_code: str):
    """Buscar trunks por código do país"""
    try:
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/trunks?country_code=eq.{country_code}"
        response = requests.get(url, headers=supabase_config['headers'])
        
        if response.status_code == 200:
            trunks = response.json()
            # Converter JSONB strings para dict
            for trunk in trunks:
                if trunk.get('dv_codes') and isinstance(trunk['dv_codes'], str):
                    trunk['dv_codes'] = json.loads(trunk['dv_codes'])
                if trunk.get('sip_config') and isinstance(trunk['sip_config'], str):
                    trunk['sip_config'] = json.loads(trunk['sip_config'])
            
            return {"trunks": trunks, "country_code": country_code}
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar trunks do Supabase")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com Supabase: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar trunks: {str(e)}")

@router.get("/{trunk_id}/config", response_model=dict)
async def get_trunk_asterisk_config(trunk_id: int):
    """Gerar configuração do Asterisk para o trunk"""
    try:
        # Buscar trunk primeiro
        supabase_config = get_supabase_config()
        url = f"{supabase_config['url']}/rest/v1/trunks?id=eq.{trunk_id}&is_active=eq.true"
        response = requests.get(url, headers=supabase_config['headers'])
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar trunk do Supabase")
        
        trunks = response.json()
        if not trunks:
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        
        trunk = trunks[0]
        sip_config = trunk.get('sip_config', {})
        if isinstance(sip_config, str):
            sip_config = json.loads(sip_config)
        
        dv_codes = trunk.get('dv_codes', [])
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
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com Supabase: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar configuração: {str(e)}") 