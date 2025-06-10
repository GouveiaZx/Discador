from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.models.llamada import Llamada
from app.models.audio_sistema import TipoEvento, EstadoAudio
from app.services.audio_engine import AudioIntelligentSystem
from app.services.audio_context_manager import AudioContextManager
from app.services.asterisk import AsteriskAMIService

logger = logging.getLogger(__name__)

class AudioIntegrationService:
    """
    Servico de integracao que conecta o sistema de audio inteligente
    com o sistema de chamadas existente.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.audio_system = AudioIntelligentSystem(db)
        self.context_manager = AudioContextManager(db)
        self.asterisk_service = AsteriskAMIService()
    
    async def iniciar_chamada_com_audio_inteligente(
        self,
        numero_destino: str,
        campana_id: int,
        contexto_audio_nome: str = "Presione 1 Padrao",
        cli: Optional[str] = None,
        configuracoes_audio: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Inicia uma chamada com o sistema de audio inteligente.
        
        Args:
            numero_destino: Numero de destino
            campana_id: ID da campanha
            contexto_audio_nome: Nome do contexto de audio
            cli: CLI para a chamada
            configuracoes_audio: Configuracoes especificas do audio
            
        Returns:
            Dict: Resultado da operacao
        """
        try:
            # Buscar contexto de audio
            contexto = self.context_manager.obter_contexto_por_nome(contexto_audio_nome)
            if not contexto:
                return {
                    "sucesso": False,
                    "erro": f"Contexto de audio '{contexto_audio_nome}' nao encontrado"
                }
            
            # Criar registro da chamada
            nova_llamada = Llamada(
                numero_destino=numero_destino,
                numero_normalizado=numero_destino.replace("+", "").replace("-", "").replace(" ", ""),
                cli=cli,
                id_campana=campana_id,
                fecha_inicio=datetime.now(),
                estado="iniciando"
            )
            
            self.db.add(nova_llamada)
            self.db.commit()
            self.db.refresh(nova_llamada)
            
            # Iniciar sessao de audio
            sessao_audio = self.audio_system.iniciar_sessao(
                llamada_id=nova_llamada.id,
                contexto_id=contexto.id,
                configuracoes_personalizadas=configuracoes_audio
            )
            
            # Preparar variaveis para o Asterisk
            variables_asterisk = {
                "LLAMADA_ID": nova_llamada.id,
                "CAMPANA_ID": campana_id,
                "AUDIO_SESSAO_ID": sessao_audio.id,
                "CONTEXTO_AUDIO": contexto.nome,
                "AUDIO_PRINCIPAL_URL": contexto.audio_principal_url,
                "TIMEOUT_DTMF": str(sessao_audio.timeout_dtmf or contexto.timeout_dtmf_padrao),
                "DETECTAR_VOICEMAIL": str(sessao_audio.detectar_voicemail or contexto.detectar_voicemail),
                "AUDIO_VOICEMAIL_URL": contexto.audio_voicemail_url or "",
                "SISTEMA_AUDIO_INTELIGENTE": "true"
            }
            
            # Originar chamada no Asterisk
            resposta_asterisk = await self.asterisk_service.originar_llamada_presione1(
                numero_destino=numero_destino,
                cli=cli or "Unknown",
                audio_url=contexto.audio_principal_url or "default.wav",
                timeout_dtmf=sessao_audio.timeout_dtmf or contexto.timeout_dtmf_padrao,
                llamada_id=nova_llamada.id,
                detectar_voicemail=sessao_audio.detectar_voicemail or contexto.detectar_voicemail,
                mensaje_voicemail_url=contexto.audio_voicemail_url,
                duracao_maxima_voicemail=contexto.duracao_maxima_voicemail
            )
            
            # Atualizar estado da chamada
            nova_llamada.estado = "en_progreso"
            self.db.commit()
            
            logger.info(f"Chamada com audio inteligente iniciada: {nova_llamada.id}")
            
            return {
                "sucesso": True,
                "llamada_id": nova_llamada.id,
                "sessao_audio_id": sessao_audio.id,
                "contexto_audio": contexto.nome,
                "asterisk_response": resposta_asterisk
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao iniciar chamada com audio inteligente: {str(e)}")
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def processar_evento_asterisk(
        self,
        llamada_id: int,
        tipo_evento: str,
        dados_evento: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processa eventos recebidos do Asterisk e os converte para eventos do sistema de audio.
        
        Args:
            llamada_id: ID da chamada
            tipo_evento: Tipo do evento do Asterisk
            dados_evento: Dados do evento
            
        Returns:
            Dict: Resultado do processamento
        """
        try:
            # Mapeamento de eventos do Asterisk para eventos do sistema de audio
            mapeamento_eventos = {
                "Dial": TipoEvento.TELEFONE_TOCANDO,
                "DialEnd": TipoEvento.ATENDEU,
                "DTMF": TipoEvento.DTMF_DETECTADO,
                "DTMFTimeout": TipoEvento.TIMEOUT_DTMF,
                "VoicemailDetected": TipoEvento.VOICEMAIL_DETECTADO,
                "HumanDetected": TipoEvento.HUMANO_CONFIRMADO,
                "Hangup": TipoEvento.CHAMADA_FINALIZADA,
                "Error": TipoEvento.ERRO_SISTEMA
            }
            
            evento_audio = mapeamento_eventos.get(tipo_evento)
            if not evento_audio:
                logger.warning(f"Evento desconhecido do Asterisk: {tipo_evento}")
                return {
                    "sucesso": False,
                    "erro": f"Evento nao mapeado: {tipo_evento}"
                }
            
            # Preparar dados especificos do evento
            dados_processados = {}
            
            if evento_audio == TipoEvento.DTMF_DETECTADO:
                dados_processados["dtmf_tecla"] = dados_evento.get("Digit", "")
            elif evento_audio == TipoEvento.VOICEMAIL_DETECTADO:
                dados_processados["confianca_deteccao"] = dados_evento.get("Confidence", 0.0)
            elif evento_audio == TipoEvento.ATENDEU:
                dados_processados["tempo_resposta"] = dados_evento.get("DialTime", 0)
            
            # Processar evento no sistema de audio
            resultado = self.audio_system.processar_evento_llamada(
                llamada_id=llamada_id,
                evento=evento_audio,
                dados_evento=dados_processados
            )
            
            # Atualizar estado da chamada se necessario
            if resultado.get("sucesso"):
                self._atualizar_estado_llamada_por_audio(llamada_id, evento_audio, dados_processados)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar evento do Asterisk: {str(e)}")
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def _atualizar_estado_llamada_por_audio(
        self,
        llamada_id: int,
        evento: TipoEvento,
        dados_evento: Dict[str, Any]
    ):
        """
        Atualiza o estado da chamada baseado nos eventos do sistema de audio.
        """
        try:
            llamada = self.db.query(Llamada).filter(Llamada.id == llamada_id).first()
            if not llamada:
                return
            
            # Mapear eventos para estados da chamada
            if evento == TipoEvento.DTMF_DETECTADO and dados_evento.get("dtmf_tecla") == "1":
                llamada.estado = "conectada"
                llamada.fecha_conexion = datetime.now()
                llamada.presiono_1 = True
                llamada.dtmf_detectado = "1"
                
            elif evento == TipoEvento.CHAMADA_FINALIZADA:
                llamada.estado = "finalizada"
                llamada.fecha_fin = datetime.now()
                llamada.fecha_finalizacion = datetime.now()
                
            elif evento == TipoEvento.VOICEMAIL_DETECTADO:
                llamada.resultado = "buzon"
                
            elif evento == TipoEvento.ERRO_SISTEMA:
                llamada.estado = "fallida"
                llamada.resultado = "otro"
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar estado da chamada: {str(e)}")
    
    def obter_status_completo_llamada(self, llamada_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtem o status completo de uma chamada, incluindo informacoes do sistema de audio.
        
        Args:
            llamada_id: ID da chamada
            
        Returns:
            Dict: Status completo da chamada
        """
        try:
            # Buscar chamada
            llamada = self.db.query(Llamada).filter(Llamada.id == llamada_id).first()
            if not llamada:
                return None
            
            # Obter status da sessao de audio
            status_audio = self.audio_system.obter_status_sessao(llamada_id)
            
            # Montar resposta completa
            status_completo = {
                "llamada": {
                    "id": llamada.id,
                    "numero_destino": llamada.numero_destino,
                    "cli": llamada.cli,
                    "estado": llamada.estado,
                    "resultado": llamada.resultado,
                    "fecha_inicio": llamada.fecha_inicio.isoformat() if llamada.fecha_inicio else None,
                    "fecha_conexion": llamada.fecha_conexion.isoformat() if llamada.fecha_conexion else None,
                    "fecha_fin": llamada.fecha_fin.isoformat() if llamada.fecha_fin else None,
                    "presiono_1": llamada.presiono_1,
                    "dtmf_detectado": llamada.dtmf_detectado
                },
                "audio_inteligente": status_audio
            }
            
            return status_completo
            
        except Exception as e:
            logger.error(f"Erro ao obter status completo: {str(e)}")
            return None
    
    def finalizar_llamada_audio(
        self,
        llamada_id: int,
        resultado: str,
        motivo_finalizacao: str = "Normal"
    ) -> Dict[str, Any]:
        """
        Finaliza uma chamada e sua sessao de audio.
        
        Args:
            llamada_id: ID da chamada
            resultado: Resultado final da chamada
            motivo_finalizacao: Motivo da finalizacao
            
        Returns:
            Dict: Resultado da operacao
        """
        try:
            # Processar evento de finalizacao no sistema de audio
            resultado_audio = self.audio_system.processar_evento_llamada(
                llamada_id=llamada_id,
                evento=TipoEvento.CHAMADA_FINALIZADA,
                dados_evento={
                    "resultado": resultado,
                    "motivo": motivo_finalizacao
                }
            )
            
            # Atualizar chamada
            llamada = self.db.query(Llamada).filter(Llamada.id == llamada_id).first()
            if llamada:
                llamada.estado = "finalizada"
                llamada.resultado = resultado
                llamada.fecha_fin = datetime.now()
                llamada.fecha_finalizacion = datetime.now()
                self.db.commit()
            
            logger.info(f"Chamada {llamada_id} finalizada com audio inteligente")
            
            return {
                "sucesso": True,
                "llamada_id": llamada_id,
                "resultado": resultado,
                "audio_resultado": resultado_audio
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao finalizar chamada com audio: {str(e)}")
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    async def setup_contextos_padrao(self) -> Dict[str, Any]:
        """
        Configura os contextos padrao do sistema de audio inteligente.
        
        Returns:
            Dict: Resultado da configuracao
        """
        try:
            # Inicializar templates padrao
            templates = self.context_manager.inicializar_templates_padrao()
            
            # Criar contexto Presione 1 padrao se nao existir
            contexto_existente = self.context_manager.obter_contexto_por_nome("Presione 1 Padrao")
            
            if not contexto_existente:
                # URLs de exemplo - em producao, estas devem apontar para arquivos reais
                audio_principal = "https://example.com/audios/presione1_principal.wav"
                audio_voicemail = "https://example.com/audios/presione1_voicemail.wav"
                
                contexto_presione1 = self.context_manager.criar_contexto_presione1(
                    nome="Presione 1 Padrao",
                    audio_principal_url=audio_principal,
                    audio_voicemail_url=audio_voicemail,
                    timeout_dtmf=10,
                    detectar_voicemail=True,
                    tentativas_maximas=3
                )
                
                logger.info(f"Contexto padrao criado: {contexto_presione1.nome}")
            
            # Listar contextos disponiveis
            contextos_disponiveis = self.context_manager.listar_contextos()
            
            return {
                "sucesso": True,
                "templates_criados": len(templates),
                "contextos_disponiveis": [c.nome for c in contextos_disponiveis],
                "contexto_padrao": "Presione 1 Padrao"
            }
            
        except Exception as e:
            logger.error(f"Erro ao configurar contextos padrao: {str(e)}")
            return {
                "sucesso": False,
                "erro": str(e)
            } 