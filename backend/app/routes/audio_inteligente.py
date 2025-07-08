from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import logging

from app.database import get_db
from app.services.audio_integration_service import AudioIntegrationService
from app.services.audio_context_manager import AudioContextManager
from app.services.audio_engine import AudioIntelligentSystem
from app.models.audio_sistema import TipoEvento, AudioSessao, AudioEvento

# Configurar logger
logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(prefix="/audio-inteligente", tags=["Audio Inteligente"])

@router.post("/iniciar-chamada")
async def iniciar_chamada_audio_inteligente(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Inicia uma chamada com o sistema de audio inteligente.
    
    Body:
    {
        "numero_destino": "+5511999999999",
        "campana_id": 1,
        "contexto_audio": "Presione 1 Padrao",
        "cli": "+5511888888888",
        "configuracoes_audio": {
            "timeout_dtmf": 15,
            "detectar_voicemail": true
        }
    }
    """
    try:
        integration_service = AudioIntegrationService(db)
        
        # Validar campos obrigatorios
        numero_destino = request.get("numero_destino")
        campana_id = request.get("campana_id")
        
        if not numero_destino or not campana_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campos obrigatorios: numero_destino, campana_id"
            )
        
        resultado = await integration_service.iniciar_chamada_com_audio_inteligente(
            numero_destino=numero_destino,
            campana_id=campana_id,
            contexto_audio_nome=request.get("contexto_audio", "Presione 1 Padrao"),
            cli=request.get("cli"),
            configuracoes_audio=request.get("configuracoes_audio")
        )
        
        if not resultado.get("sucesso"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=resultado.get("erro", "Erro desconhecido")
            )
        
        return {
            "success": True,
            "message": "Chamada iniciada com sistema de audio inteligente",
            "data": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar chamada: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/evento-asterisk")
def processar_evento_asterisk(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Processa eventos recebidos do Asterisk.
    
    Body:
    {
        "llamada_id": 123,
        "tipo_evento": "DTMF",
        "dados_evento": {
            "Digit": "1",
            "Channel": "SIP/123-00000001"
        }
    }
    """
    try:
        integration_service = AudioIntegrationService(db)
        
        llamada_id = request.get("llamada_id")
        tipo_evento = request.get("tipo_evento")
        dados_evento = request.get("dados_evento", {})
        
        if not llamada_id or not tipo_evento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campos obrigatorios: llamada_id, tipo_evento"
            )
        
        resultado = integration_service.processar_evento_asterisk(
            llamada_id=llamada_id,
            tipo_evento=tipo_evento,
            dados_evento=dados_evento
        )
        
        return {
            "success": True,
            "message": "Evento processado",
            "data": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar evento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/status-llamada/{llamada_id}")
def obter_status_llamada(
    llamada_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtem o status completo de uma chamada, incluindo audio inteligente.
    """
    try:
        integration_service = AudioIntegrationService(db)
        
        status = integration_service.obter_status_completo_llamada(llamada_id)
        
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chamada {llamada_id} nao encontrada"
            )
        
        return {
            "success": True,
            "data": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/finalizar-llamada/{llamada_id}")
def finalizar_llamada(
    llamada_id: int,
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Finaliza uma chamada e sua sessao de audio.
    
    Body:
    {
        "resultado": "contestada",
        "motivo_finalizacao": "Normal"
    }
    """
    try:
        integration_service = AudioIntegrationService(db)
        
        resultado = request.get("resultado", "outro")
        motivo = request.get("motivo_finalizacao", "Normal")
        
        resultado_operacao = integration_service.finalizar_llamada_audio(
            llamada_id=llamada_id,
            resultado=resultado,
            motivo_finalizacao=motivo
        )
        
        if not resultado_operacao.get("sucesso"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=resultado_operacao.get("erro", "Erro ao finalizar")
            )
        
        return {
            "success": True,
            "message": "Chamada finalizada",
            "data": resultado_operacao
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao finalizar chamada: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/contextos")
def listar_contextos(
    ativo_apenas: bool = True,
    db: Session = Depends(get_db)
):
    """
    Lista todos os contextos de audio disponiveis.
    """
    try:
        context_manager = AudioContextManager(db)
        contextos = context_manager.listar_contextos(ativo_apenas=ativo_apenas)
        
        contextos_data = []
        for contexto in contextos:
            contextos_data.append({
                "id": contexto.id,
                "nome": contexto.nome,
                "descricao": contexto.descricao,
                "timeout_dtmf_padrao": contexto.timeout_dtmf_padrao,
                "detectar_voicemail": contexto.detectar_voicemail,
                "audio_principal_url": contexto.audio_principal_url,
                "audio_voicemail_url": contexto.audio_voicemail_url,
                "tentativas_maximas": contexto.tentativas_maximas,
                "ativo": contexto.ativo,
                "total_regras": len(contexto.regras) if contexto.regras else 0
            })
        
        return {
            "success": True,
            "data": contextos_data,
            "total": len(contextos_data)
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar contextos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/templates")
def listar_templates(
    categoria: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos os templates de audio disponiveis.
    """
    try:
        context_manager = AudioContextManager(db)
        templates = context_manager.listar_templates(categoria=categoria)
        
        templates_data = []
        for template in templates:
            templates_data.append({
                "id": template.id,
                "nome": template.nome,
                "descricao": template.descricao,
                "categoria": template.categoria,
                "versao": template.versao,
                "ativo": template.ativo,
                "total_regras": len(template.regras_template) if template.regras_template else 0
            })
        
        return {
            "success": True,
            "data": templates_data,
            "total": len(templates_data)
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/criar-contexto")
def criar_contexto(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Cria um novo contexto de audio.
    
    Body:
    {
        "nome": "Meu Contexto",
        "descricao": "Contexto personalizado",
        "audio_principal_url": "https://example.com/audio.wav",
        "timeout_dtmf": 10,
        "detectar_voicemail": true,
        "audio_voicemail_url": "https://example.com/voicemail.wav"
    }
    """
    try:
        context_manager = AudioContextManager(db)
        
        nome = request.get("nome")
        descricao = request.get("descricao", "")
        audio_principal_url = request.get("audio_principal_url")
        
        if not nome or not audio_principal_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campos obrigatorios: nome, audio_principal_url"
            )
        
        contexto = context_manager.criar_contexto_basico(
            nome=nome,
            descricao=descricao,
            audio_principal_url=audio_principal_url,
            timeout_dtmf=request.get("timeout_dtmf", 10),
            detectar_voicemail=request.get("detectar_voicemail", True),
            audio_voicemail_url=request.get("audio_voicemail_url")
        )
        
        return {
            "success": True,
            "message": "Contexto criado com sucesso",
            "data": {
                "id": contexto.id,
                "nome": contexto.nome,
                "descricao": contexto.descricao
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar contexto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/criar-contexto-template")
def criar_contexto_a_partir_template(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Cria um contexto baseado em um template.
    
    Body:
    {
        "template_id": 1,
        "nome_contexto": "Minha Campanha Presione 1",
        "audio_principal_url": "https://example.com/audio.wav",
        "audio_voicemail_url": "https://example.com/voicemail.wav",
        "configuracoes_personalizadas": {
            "timeout_dtmf_padrao": 15
        }
    }
    """
    try:
        context_manager = AudioContextManager(db)
        
        template_id = request.get("template_id")
        nome_contexto = request.get("nome_contexto")
        audio_principal_url = request.get("audio_principal_url")
        
        if not all([template_id, nome_contexto, audio_principal_url]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campos obrigatorios: template_id, nome_contexto, audio_principal_url"
            )
        
        contexto = context_manager.criar_contexto_a_partir_template(
            template_id=template_id,
            nome_contexto=nome_contexto,
            audio_principal_url=audio_principal_url,
            audio_voicemail_url=request.get("audio_voicemail_url"),
            configuracoes_personalizadas=request.get("configuracoes_personalizadas")
        )
        
        return {
            "success": True,
            "message": "Contexto criado a partir do template",
            "data": {
                "id": contexto.id,
                "nome": contexto.nome,
                "template_origem": template_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar contexto a partir do template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/setup-inicial")
async def configurar_sistema_inicial(
    db: Session = Depends(get_db)
):
    """
    Configura o sistema de audio inteligente com contextos e templates padrao.
    """
    try:
        integration_service = AudioIntegrationService(db)
        
        resultado = await integration_service.setup_contextos_padrao()
        
        if not resultado.get("sucesso"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=resultado.get("erro", "Erro na configuracao inicial")
            )
        
        return {
            "success": True,
            "message": "Sistema de audio inteligente configurado",
            "data": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na configuracao inicial: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/eventos-disponiveis")
def listar_eventos_disponiveis():
    """
    Lista todos os tipos de eventos disponiveis no sistema.
    """
    try:
        eventos = []
        for evento in TipoEvento:
            eventos.append({
                "valor": evento.value,
                "descricao": evento.name
            })
        
        return {
            "success": True,
            "data": eventos,
            "total": len(eventos)
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# Rota de teste para demonstrar o sistema
@router.post("/teste-demo")
async def teste_sistema_demo(
    db: Session = Depends(get_db)
):
    """
    Rota de demonstracao do sistema de audio inteligente.
    Cria um contexto de teste e simula uma chamada.
    """
    try:
        integration_service = AudioIntegrationService(db)
        
        # Configurar sistema inicial se necessario
        await integration_service.setup_contextos_padrao()
        
        # Simular inicio de chamada
        numero_teste = "+5511999999999"
        resultado_chamada = await integration_service.iniciar_chamada_com_audio_inteligente(
            numero_destino=numero_teste,
            campana_id=1,
            contexto_audio_nome="Presione 1 Padrao",
            cli="+5511888888888"
        )
        
        if not resultado_chamada.get("sucesso"):
            return {
                "success": False,
                "message": "Erro ao iniciar chamada de teste",
                "error": resultado_chamada.get("erro")
            }
        
        llamada_id = resultado_chamada["llamada_id"]
        
        # Simular eventos da chamada
        eventos_simulados = [
            {"tipo": "Dial", "dados": {}},
            {"tipo": "DialEnd", "dados": {"DialTime": 5}},
            {"tipo": "DTMF", "dados": {"Digit": "1"}},
        ]
        
        resultados_eventos = []
        for evento in eventos_simulados:
            resultado_evento = integration_service.processar_evento_asterisk(
                llamada_id=llamada_id,
                tipo_evento=evento["tipo"],
                dados_evento=evento["dados"]
            )
            resultados_eventos.append({
                "evento": evento["tipo"],
                "resultado": resultado_evento
            })
        
        # Obter status final
        status_final = integration_service.obter_status_completo_llamada(llamada_id)
        
        return {
            "success": True,
            "message": "Demonstracao concluida com sucesso",
            "data": {
                "chamada_iniciada": resultado_chamada,
                "eventos_processados": resultados_eventos,
                "status_final": status_final
            }
        }
        
    except Exception as e:
        logger.error(f"Erro na demonstracao: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/campanhas/{campana_id}/sessoes")
def listar_sessoes_campana(
    campana_id: int,
    db: Session = Depends(get_db)
):
    """
    Lista todas as sessões de áudio inteligente de uma campanha.
    
    Retorna informações sobre:
    - Sessões ativas de DTMF
    - Detecções de voicemail
    - Estados de áudio por chamada
    - Durações e resultados
    """
    try:
        # Buscar sessões da campanha
        sessoes = db.query(AudioSessao).filter(
            AudioSessao.campana_id == campana_id
        ).all()
        
        # Converter para formato de resposta
        sessoes_formatadas = []
        for sessao in sessoes:
            # Buscar eventos relacionados
            eventos = db.query(AudioEvento).filter(
                AudioEvento.sessao_id == sessao.id
            ).all()
            
            # Detectar DTMF e voicemail
            dtmf_detectado = None
            voicemail_detectado = False
            
            for evento in eventos:
                if evento.tipo_evento == 'dtmf_recebido':
                    dtmf_detectado = evento.dados_evento.get('tecla') if evento.dados_evento else None
                elif evento.tipo_evento == 'voicemail_detectado':
                    voicemail_detectado = True
            
            sessoes_formatadas.append({
                "id": sessao.id,
                "llamada_id": sessao.llamada_id,
                "estado": sessao.estado.value if sessao.estado else 'finalizada',
                "dtmf_detectado": dtmf_detectado,
                "voicemail_detectado": voicemail_detectado,
                "duracao": str(sessao.duracao_total) if sessao.duracao_total else '0:00',
                "inicio": sessao.inicio_sessao.isoformat() if sessao.inicio_sessao else None,
                "fim": sessao.fim_sessao.isoformat() if sessao.fim_sessao else None
            })
        
        return {
            "success": True,
            "data": sessoes_formatadas,
            "total": len(sessoes_formatadas)
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar sessões da campanha {campana_id}: {str(e)}")
        # Retornar lista vazia em caso de erro
        return {
            "success": True,
            "data": [],
            "total": 0,
            "error": f"Erro interno: {str(e)}"
        } 