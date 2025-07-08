from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import requests
import os
from datetime import datetime
import logging

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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dnc", tags=["DNC Management"])

# Headers para Supabase (usando a função get_supabase_config)
def get_supabase_headers():
    config = get_supabase_config()
    return config["headers"]

@router.get("/messages")
async def get_dnc_messages():
    """Obtém todas as mensagens DNC configuradas"""
    try:
        config = get_supabase_config()
        response = requests.get(
            f"{config['url']}/rest/v1/dnc_messages",
            headers=config["headers"]
        )
        
        logger.info(f"Supabase DNC messages response: {response.status_code}")
        
        if response.status_code == 200:
            messages = response.json()
            return {"status": "success", "data": messages}
        else:
            # Se não existe tabela, retornar mensagens default
            default_messages = [
                {
                    "id": "en_opt_out",
                    "language_code": "en",
                    "language_name": "English",
                    "message_type": "opt_out",
                    "title": "Opt-Out - English",
                    "message": "Thank you for your call. To remove your number from our calling list, please press 2 now. Your number will be removed within 24 hours. Thank you.",
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "es_opt_out",
                    "language_code": "es",
                    "language_name": "Español",
                    "message_type": "opt_out",
                    "title": "Opt-Out - Español",
                    "message": "Gracias por su llamada. Para remover su número de nuestra lista de llamadas, presione 2 ahora. Su número será removido en 24 horas. Gracias.",
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "pt_opt_out",
                    "language_code": "pt",
                    "language_name": "Português",
                    "message_type": "opt_out",
                    "title": "Opt-Out - Português",
                    "message": "Obrigado pela sua ligação. Para remover seu número da nossa lista de chamadas, pressione 2 agora. Seu número será removido em 24 horas. Obrigado.",
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                }
            ]
            return {"status": "success", "data": default_messages}
            
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens DNC: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar mensagens DNC: {str(e)}")

@router.post("/messages")
async def create_dnc_message(message_data: dict):
    """Cria uma nova mensagem DNC"""
    try:
        # Adicionar timestamp
        message_data["created_at"] = datetime.now().isoformat()
        message_data["updated_at"] = datetime.now().isoformat()
        
        config = get_supabase_config()
        response = requests.post(
            f"{config['url']}/rest/v1/dnc_messages",
            headers=config["headers"],
            json=message_data
        )
        
        logger.info(f"Supabase create DNC message response: {response.status_code}")
        
        if response.status_code == 201:
            created_message = response.json()
            return {"status": "success", "data": created_message}
        else:
            error_text = response.text
            logger.error(f"Erro Supabase create DNC message: {error_text}")
            raise HTTPException(status_code=response.status_code, detail=error_text)
            
    except Exception as e:
        logger.error(f"Erro ao criar mensagem DNC: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar mensagem DNC: {str(e)}")

@router.put("/messages/{message_id}")
async def update_dnc_message(message_id: str, message_data: dict):
    """Atualiza uma mensagem DNC existente"""
    try:
        # Adicionar timestamp de atualização
        message_data["updated_at"] = datetime.now().isoformat()
        
        config = get_supabase_config()
        response = requests.patch(
            f"{config['url']}/rest/v1/dnc_messages?id=eq.{message_id}",
            headers=config["headers"],
            json=message_data
        )
        
        logger.info(f"Supabase update DNC message response: {response.status_code}")
        
        if response.status_code == 200:
            updated_message = response.json()
            return {"status": "success", "data": updated_message}
        else:
            error_text = response.text
            logger.error(f"Erro Supabase update DNC message: {error_text}")
            raise HTTPException(status_code=response.status_code, detail=error_text)
            
    except Exception as e:
        logger.error(f"Erro ao atualizar mensagem DNC: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar mensagem DNC: {str(e)}")

@router.delete("/messages/{message_id}")
async def delete_dnc_message(message_id: str):
    """Exclui uma mensagem DNC"""
    try:
        config = get_supabase_config()
        response = requests.delete(
            f"{config['url']}/rest/v1/dnc_messages?id=eq.{message_id}",
            headers=config["headers"]
        )
        
        logger.info(f"Supabase delete DNC message response: {response.status_code}")
        
        if response.status_code == 204:
            return {"status": "success", "message": "Mensagem DNC removida com sucesso"}
        else:
            error_text = response.text
            logger.error(f"Erro Supabase delete DNC message: {error_text}")
            raise HTTPException(status_code=response.status_code, detail=error_text)
            
    except Exception as e:
        logger.error(f"Erro ao excluir mensagem DNC: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir mensagem DNC: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """Retorna os idiomas suportados para mensagens DNC"""
    languages = [
        {"code": "en", "name": "English", "flag": "🇺🇸"},
        {"code": "es", "name": "Español", "flag": "🇪🇸"},
        {"code": "pt", "name": "Português", "flag": "🇧🇷"},
        {"code": "fr", "name": "Français", "flag": "🇫🇷"},
        {"code": "de", "name": "Deutsch", "flag": "🇩🇪"}
    ]
    return {"status": "success", "data": languages}

@router.get("/message-types")
async def get_message_types():
    """Retorna os tipos de mensagem DNC disponíveis"""
    message_types = [
        {"value": "opt_out", "label": "Opt-Out (Pressione 2)", "icon": "🚫"},
        {"value": "confirmation", "label": "Confirmação", "icon": "✅"},
        {"value": "error", "label": "Erro", "icon": "❌"}
    ]
    return {"status": "success", "data": message_types} 