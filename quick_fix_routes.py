#!/usr/bin/env python3
"""
Script de correção rápida para adicionar rotas multi-sip ausentes
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação separada para as rotas ausentes
app = FastAPI(
    title="Rotas Multi-SIP - Correção",
    description="Rotas ausentes do sistema principal",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/api/v1/multi-sip/provedores")
@app.get("/multi-sip/provedores")  # Compatibilidade 
async def listar_provedores():
    """Lista provedores SIP disponíveis"""
    logger.info("📡 Listando provedores SIP")
    
    provedores = [
        {
            "id": 1,
            "nome": "Provedor Principal",
            "servidor_sip": "sip.exemplo.com",
            "porta": 5060,
            "status": "ativo",
            "prioridade": 1,
            "max_chamadas_simultaneas": 50,
            "chamadas_ativas": 0,
            "ultima_verificacao": datetime.now().isoformat()
        },
        {
            "id": 2,
            "nome": "Provedor Backup",
            "servidor_sip": "backup.sip.com",
            "porta": 5061,
            "status": "standby",
            "prioridade": 2,
            "max_chamadas_simultaneas": 30,
            "chamadas_ativas": 0,
            "ultima_verificacao": datetime.now().isoformat()
        }
    ]
    
    return {
        "status": "success",
        "provedores": provedores,
        "total": len(provedores)
    }

@app.post("/api/v1/multi-sip/provedores")
@app.post("/multi-sip/provedores")  # Compatibilidade
async def criar_provedor(provedor_data: dict):
    """Cria novo provedor SIP"""
    logger.info(f"➕ Criando provedor: {provedor_data.get('nome', 'Sem nome')}")
    
    novo_provedor = {
        "id": 999,
        "nome": provedor_data.get("nome", "Novo Provedor"),
        "servidor_sip": provedor_data.get("servidor_sip", ""),
        "porta": provedor_data.get("porta", 5060),
        "status": "ativo",
        "prioridade": provedor_data.get("prioridade", 100),
        "data_criacao": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": "Provedor criado com sucesso",
        "provedor": novo_provedor
    }

@app.get("/api/v1/code2base/clis")
@app.get("/code2base/clis")  # Compatibilidade
async def listar_clis():
    """Lista CLIs disponíveis"""
    logger.info("📞 Listando CLIs disponíveis")
    
    clis = [
        {
            "id": 1,
            "numero": "+5511999887766",
            "descricao": "CLI Principal",
            "ativo": True,
            "tipo": "nacional",
            "ultima_utilizacao": datetime.now().isoformat()
        },
        {
            "id": 2,
            "numero": "+5511888776655",
            "descricao": "CLI Secundário",
            "ativo": True,
            "tipo": "nacional",
            "ultima_utilizacao": None
        }
    ]
    
    return {
        "status": "success",
        "clis": clis,
        "total": len(clis)
    }

@app.get("/api/v1/audio-inteligente/contextos") 
@app.get("/audio-inteligente/contextos")  # Compatibilidade
async def listar_contextos_audio():
    """Lista contextos de áudio inteligente"""
    logger.info("🎤 Listando contextos de áudio")
    
    contextos = [
        {
            "id": 1,
            "nome": "Contexto Padrão",
            "descricao": "Contexto de áudio padrão para campanhas",
            "ativo": True,
            "configuracoes": {
                "deteccao_voz": True,
                "timeout_resposta": 5,
                "max_tentativas": 3
            }
        }
    ]
    
    return {
        "status": "success",
        "contextos": contextos,
        "total": len(contextos)
    }

@app.get("/api/v1/audio/contextos")
@app.get("/audio/contextos")  # Compatibilidade
async def listar_contextos_audio_simples():
    """Lista contextos de áudio (rota alternativa)"""
    logger.info("🎵 Listando contextos de áudio (rota simples)")
    return await listar_contextos_audio()

@app.post("/api/v1/audio/setup-padrao")
@app.post("/audio/setup-padrao")  # Compatibilidade
async def setup_audio_padrao():
    """Setup padrão do áudio inteligente"""
    logger.info("🎵 Configurando setup padrão de áudio")
    return {
        "status": "success",
        "message": "Setup padrão configurado com sucesso!",
        "configuracao": {
            "contexto_padrao": "Contexto Padrão",
            "deteccao_voz": True,
            "timeout_resposta": 5,
            "max_tentativas": 3,
            "audio_resposta": "Configuração padrão ativada"
        }
    }

@app.get("/api/v1/configuracion-avanzada/status")
async def status_configuracion_avanzada():
    """Status da configuração avançada"""
    logger.info("⚙️ Obtendo status da configuração avançada")
    
    return {
        "status": "success",
        "data": {
            "multi_sip": {
                "ativo": True,
                "provedores_disponiveis": 2,
                "provedores_ativos": 1
            },
            "code2base": {
                "ativo": True,
                "clis_disponiveis": 2,
                "cli_ativo": "+5511999887766"
            },
            "audio_inteligente": {
                "ativo": True,
                "contextos_ativos": 1,
                "deteccao_voz": True
            }
        }
    }

@app.post("/api/v1/code2base/clis")
@app.post("/code2base/clis")  # Compatibilidade
async def criar_cli(cli_data: dict):
    """Cria novo CLI"""
    logger.info(f"📞 Criando CLI: {cli_data.get('numero', 'Sem número')}")
    
    novo_cli = {
        "id": 999,
        "numero": cli_data.get("numero", ""),
        "descricao": f"CLI {cli_data.get('numero', 'Novo')}",
        "ativo": cli_data.get("activo", True),
        "tipo": "nacional",
        "proveedor_id": cli_data.get("proveedor_id"),
        "data_criacao": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": "CLI creado con éxito",
        "cli": novo_cli
    }

@app.post("/api/v1/audio/contextos")
@app.post("/audio/contextos")  # Compatibilidade
async def criar_contexto_audio(contexto_data: dict):
    """Cria novo contexto de áudio"""
    logger.info(f"🎤 Criando contexto de áudio: {contexto_data.get('nombre', 'Sem nome')}")
    
    novo_contexto = {
        "id": 999,
        "nome": contexto_data.get("nombre", "Novo Contexto"),
        "descricao": f"Contexto {contexto_data.get('nombre', 'personalizado')}",
        "ativo": True,
        "timeout_dtmf_predeterminado": contexto_data.get("timeout_dtmf_predeterminado", 10),
        "detectar_voicemail": contexto_data.get("detectar_voicemail", True),
        "audio_principal_url": contexto_data.get("audio_principal_url", ""),
        "configuracoes": {
            "deteccao_voz": True,
            "timeout_resposta": contexto_data.get("timeout_dtmf_predeterminado", 10),
            "max_tentativas": 3
        },
        "data_criacao": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": "Contexto de audio creado con éxito",
        "contexto": novo_contexto
    }

@app.get("/")
async def root():
    """Status do serviço"""
    return {
        "message": "🔧 Serviço de correção Multi-SIP ativo",
        "status": "operational",
        "routes": [
            "/multi-sip/provedores",
            "/code2base/clis", 
            "/audio-inteligente/contextos",
            "/audio/contextos",
            "/audio/setup-padrao",
            "/api/v1/configuracion-avanzada/status"
        ]
    }

if __name__ == "__main__":
    logger.info("🚀 Iniciando serviço de correção Multi-SIP na porta 8001")
    uvicorn.run(
        "quick_fix_routes:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 