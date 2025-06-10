from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
import json

from app.models.audio_sistema import (
    AudioContexto, AudioRegra, AudioSessao, AudioEvento, AudioTemplate,
    EstadoAudio, TipoEvento, TipoOperadorRegra
)
from app.models.llamada import Llamada

# Configurar logger
logger = logging.getLogger(__name__)

class AudioStateMachine:
    """
    Maquina de estados para o sistema de audio inteligente.
    Gerencia transicoes de estado baseadas em eventos e regras.
    """
    
    # Transicoes validas de estado (estado_atual -> [estados_permitidos])
    TRANSICOES_VALIDAS = {
        EstadoAudio.INICIANDO: [
            EstadoAudio.TOCANDO, 
            EstadoAudio.ERRO, 
            EstadoAudio.FINALIZADO
        ],
        EstadoAudio.TOCANDO: [
            EstadoAudio.AGUARDANDO_DTMF,
            EstadoAudio.DETECTANDO_VOICEMAIL,
            EstadoAudio.AGUARDANDO_HUMANO,
            EstadoAudio.ERRO,
            EstadoAudio.FINALIZADO
        ],
        EstadoAudio.AGUARDANDO_DTMF: [
            EstadoAudio.CONECTADO,
            EstadoAudio.DETECTANDO_VOICEMAIL,
            EstadoAudio.AGUARDANDO_HUMANO,
            EstadoAudio.ERRO,
            EstadoAudio.FINALIZADO
        ],
        EstadoAudio.DETECTANDO_VOICEMAIL: [
            EstadoAudio.REPRODUZINDO_VOICEMAIL,
            EstadoAudio.AGUARDANDO_HUMANO,
            EstadoAudio.ERRO,
            EstadoAudio.FINALIZADO
        ],
        EstadoAudio.REPRODUZINDO_VOICEMAIL: [
            EstadoAudio.FINALIZADO,
            EstadoAudio.ERRO
        ],
        EstadoAudio.AGUARDANDO_HUMANO: [
            EstadoAudio.CONECTADO,
            EstadoAudio.DETECTANDO_VOICEMAIL,
            EstadoAudio.ERRO,
            EstadoAudio.FINALIZADO
        ],
        EstadoAudio.CONECTADO: [
            EstadoAudio.TRANSFERINDO,
            EstadoAudio.FINALIZADO,
            EstadoAudio.ERRO
        ],
        EstadoAudio.TRANSFERINDO: [
            EstadoAudio.FINALIZADO,
            EstadoAudio.ERRO
        ],
        EstadoAudio.ERRO: [
            EstadoAudio.FINALIZADO
        ],
        EstadoAudio.FINALIZADO: []  # Estado terminal
    }
    
    def __init__(self, db: Session):
        self.db = db
        
    def validar_transicao(
        self, 
        estado_atual: EstadoAudio, 
        estado_destino: EstadoAudio
    ) -> bool:
        """
        Valida se uma transicao de estado e permitida.
        """
        estados_permitidos = self.TRANSICOES_VALIDAS.get(estado_atual, [])
        return estado_destino in estados_permitidos
    
    def alterar_estado(
        self,
        sessao: AudioSessao,
        novo_estado: EstadoAudio,
        evento: TipoEvento,
        dados_evento: Optional[Dict[str, Any]] = None,
        regra_aplicada: Optional[AudioRegra] = None
    ) -> bool:
        """
        Altera o estado de uma sessao de audio.
        
        Args:
            sessao: Sessao de audio a ser atualizada
            novo_estado: Novo estado desejado
            evento: Evento que disparou a mudanca
            dados_evento: Dados especificos do evento
            regra_aplicada: Regra que foi aplicada (se houver)
            
        Returns:
            bool: True se a mudanca foi aplicada com sucesso
        """
        estado_anterior = sessao.estado_atual
        
        # Validar transicao
        if not self.validar_transicao(estado_anterior, novo_estado):
            logger.warning(
                f"Transicao invalida: {estado_anterior} -> {novo_estado} "
                f"para sessao {sessao.id}"
            )
            return False
        
        try:
            # Registrar evento
            evento_registro = AudioEvento(
                sessao_id=sessao.id,
                tipo_evento=evento,
                estado_origem=estado_anterior,
                estado_destino=novo_estado,
                dados_evento=dados_evento or {},
                regra_aplicada_id=regra_aplicada.id if regra_aplicada else None
            )
            self.db.add(evento_registro)
            
            # Atualizar sessao
            sessao.estado_anterior = estado_anterior
            sessao.estado_atual = novo_estado
            sessao.ultima_mudanca_estado = datetime.utcnow()
            
            # Se finalizando, marcar timestamp
            if novo_estado == EstadoAudio.FINALIZADO:
                sessao.finalizado_em = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(
                f"Estado alterado: {estado_anterior} -> {novo_estado} "
                f"para sessao {sessao.id} (evento: {evento})"
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao alterar estado da sessao {sessao.id}: {str(e)}")
            return False

class AudioRulesEngine:
    """
    Motor de regras para reproducao dinamica de audio.
    Avalia condicoes e determina proximas acoes baseadas em regras configuraveis.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.state_machine = AudioStateMachine(db)
        
    def avaliar_condicao(
        self,
        condicao: Dict[str, Any],
        contexto_dados: Dict[str, Any]
    ) -> bool:
        """
        Avalia uma condicao especifica.
        
        Args:
            condicao: Condicao a ser avaliada
            contexto_dados: Dados do contexto atual da sessao
            
        Returns:
            bool: True se a condicao e atendida
        """
        try:
            campo = condicao.get("campo")
            operador = condicao.get("operador")
            valor = condicao.get("valor")
            
            if not all([campo, operador]):
                return False
                
            # Obter valor do campo do contexto
            valor_campo = contexto_dados.get(campo)
            
            # Aplicar operador
            if operador == TipoOperadorRegra.IGUAL.value:
                return valor_campo == valor
            elif operador == TipoOperadorRegra.DIFERENTE.value:
                return valor_campo != valor
            elif operador == TipoOperadorRegra.MAIOR_QUE.value:
                return valor_campo is not None and valor_campo > valor
            elif operador == TipoOperadorRegra.MENOR_QUE.value:
                return valor_campo is not None and valor_campo < valor
            elif operador == TipoOperadorRegra.CONTEM.value:
                return valor_campo is not None and valor in str(valor_campo)
            elif operador == TipoOperadorRegra.NAO_CONTEM.value:
                return valor_campo is not None and valor not in str(valor_campo)
            elif operador == TipoOperadorRegra.ENTRE.value:
                if isinstance(valor, list) and len(valor) == 2:
                    return valor_campo is not None and valor[0] <= valor_campo <= valor[1]
            elif operador == TipoOperadorRegra.EXISTE.value:
                return valor_campo is not None
                
            return False
            
        except Exception as e:
            logger.error(f"Erro ao avaliar condicao: {str(e)}")
            return False
    
    def avaliar_regra(
        self,
        regra: AudioRegra,
        sessao: AudioSessao,
        evento: TipoEvento,
        dados_evento: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Avalia se uma regra especifica deve ser aplicada.
        
        Args:
            regra: Regra a ser avaliada
            sessao: Sessao atual
            evento: Evento que disparou a avaliacao
            dados_evento: Dados especificos do evento
            
        Returns:
            bool: True se a regra deve ser aplicada
        """
        # Verificar estado origem
        if regra.estado_origem != sessao.estado_atual:
            return False
            
        # Verificar evento disparador (se especificado)
        if regra.evento_disparador and regra.evento_disparador != evento:
            return False
            
        # Preparar dados do contexto para avaliacao
        contexto_dados = sessao.dados_contexto or {}
        contexto_dados.update(dados_evento or {})
        
        # Adicionar dados temporais
        agora = datetime.utcnow()
        tempo_no_estado = (agora - sessao.ultima_mudanca_estado).total_seconds()
        tempo_total = (agora - sessao.iniciado_em).total_seconds()
        
        contexto_dados.update({
            "tempo_no_estado_atual": tempo_no_estado,
            "tempo_total_sessao": tempo_total,
            "tentativas_realizadas": sessao.tentativas_realizadas,
            "estado_atual": sessao.estado_atual.value,
            "evento_atual": evento.value
        })
        
        # Avaliar condicoes adicionais
        if regra.condicoes:
            for condicao in regra.condicoes:
                if not self.avaliar_condicao(condicao, contexto_dados):
                    return False
                    
        return True
    
    def buscar_regras_aplicaveis(
        self,
        sessao: AudioSessao,
        evento: TipoEvento,
        dados_evento: Optional[Dict[str, Any]] = None
    ) -> List[AudioRegra]:
        """
        Busca todas as regras aplicaveis para uma sessao e evento.
        
        Returns:
            List[AudioRegra]: Lista de regras ordenadas por prioridade
        """
        # Buscar regras do contexto atual
        regras_query = self.db.query(AudioRegra).filter(
            and_(
                AudioRegra.contexto_id == sessao.contexto_id,
                AudioRegra.estado_origem == sessao.estado_atual,
                AudioRegra.ativo == True
            )
        )
        
        # Filtrar por evento se especificado
        if evento:
            regras_query = regras_query.filter(
                or_(
                    AudioRegra.evento_disparador == evento,
                    AudioRegra.evento_disparador.is_(None)
                )
            )
        
        # Ordenar por prioridade (maior prioridade primeiro)
        regras = regras_query.order_by(AudioRegra.prioridade.desc()).all()
        
        # Filtrar regras que atendem as condicoes
        regras_aplicaveis = []
        for regra in regras:
            if self.avaliar_regra(regra, sessao, evento, dados_evento):
                regras_aplicaveis.append(regra)
                
        return regras_aplicaveis
    
    def aplicar_regra(
        self,
        regra: AudioRegra,
        sessao: AudioSessao,
        evento: TipoEvento,
        dados_evento: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Aplica uma regra especifica a uma sessao.
        
        Returns:
            Dict: Resultado da aplicacao da regra
        """
        try:
            # Alterar estado se necessario
            sucesso_mudanca = True
            if regra.estado_destino != sessao.estado_atual:
                sucesso_mudanca = self.state_machine.alterar_estado(
                    sessao=sessao,
                    novo_estado=regra.estado_destino,
                    evento=evento,
                    dados_evento=dados_evento,
                    regra_aplicada=regra
                )
            
            if not sucesso_mudanca:
                return {
                    "sucesso": False,
                    "erro": "Falha ao alterar estado",
                    "regra_id": regra.id
                }
            
            # Aplicar acoes adicionais
            acoes_resultado = {}
            
            # Atualizar URL do audio se especificado
            if regra.audio_url:
                sessao.audio_atual_url = regra.audio_url
                acoes_resultado["audio_alterado"] = regra.audio_url
            
            # Aplicar parametros da acao
            if regra.parametros_acao:
                for parametro, valor in regra.parametros_acao.items():
                    if parametro == "timeout_dtmf":
                        sessao.timeout_dtmf = valor
                    elif parametro == "detectar_voicemail":
                        sessao.detectar_voicemail = valor
                    elif parametro == "incrementar_tentativas":
                        sessao.tentativas_realizadas += valor
                        
                acoes_resultado["parametros_aplicados"] = regra.parametros_acao
            
            # Atualizar dados do contexto
            if dados_evento:
                dados_contexto = sessao.dados_contexto or {}
                dados_contexto.update(dados_evento)
                sessao.dados_contexto = dados_contexto
            
            self.db.commit()
            
            logger.info(f"Regra {regra.id} aplicada com sucesso a sessao {sessao.id}")
            
            return {
                "sucesso": True,
                "regra_id": regra.id,
                "novo_estado": sessao.estado_atual.value,
                "acoes": acoes_resultado
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao aplicar regra {regra.id}: {str(e)}")
            return {
                "sucesso": False,
                "erro": str(e),
                "regra_id": regra.id
            }
    
    def processar_evento(
        self,
        sessao_id: int,
        evento: TipoEvento,
        dados_evento: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa um evento para uma sessao especifica.
        
        Args:
            sessao_id: ID da sessao
            evento: Tipo do evento
            dados_evento: Dados especificos do evento
            
        Returns:
            Dict: Resultado do processamento
        """
        try:
            # Buscar sessao
            sessao = self.db.query(AudioSessao).filter(
                AudioSessao.id == sessao_id
            ).first()
            
            if not sessao:
                return {
                    "sucesso": False,
                    "erro": f"Sessao {sessao_id} nao encontrada"
                }
            
            # Buscar regras aplicaveis
            regras_aplicaveis = self.buscar_regras_aplicaveis(
                sessao, evento, dados_evento
            )
            
            if not regras_aplicaveis:
                logger.info(
                    f"Nenhuma regra aplicavel para evento {evento} "
                    f"na sessao {sessao_id}"
                )
                return {
                    "sucesso": True,
                    "mensagem": "Nenhuma regra aplicavel",
                    "regras_avaliadas": 0
                }
            
            # Aplicar primeira regra aplicavel (maior prioridade)
            regra_escolhida = regras_aplicaveis[0]
            resultado = self.aplicar_regra(
                regra_escolhida, sessao, evento, dados_evento
            )
            
            resultado["regras_avaliadas"] = len(regras_aplicaveis)
            resultado["regras_descartadas"] = len(regras_aplicaveis) - 1
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar evento {evento}: {str(e)}")
            return {
                "sucesso": False,
                "erro": str(e)
            }

class AudioIntelligentSystem:
    """
    Sistema principal de audio inteligente.
    Coordena a maquina de estados e o motor de regras.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.rules_engine = AudioRulesEngine(db)
        self.state_machine = AudioStateMachine(db)
    
    def iniciar_sessao(
        self,
        llamada_id: int,
        contexto_id: int,
        configuracoes_personalizadas: Optional[Dict[str, Any]] = None
    ) -> AudioSessao:
        """
        Inicia uma nova sessao de audio para uma chamada.
        
        Args:
            llamada_id: ID da chamada
            contexto_id: ID do contexto de audio
            configuracoes_personalizadas: Configuracoes especificas para esta sessao
            
        Returns:
            AudioSessao: Sessao criada
        """
        try:
            # Verificar se ja existe sessao para esta chamada
            sessao_existente = self.db.query(AudioSessao).filter(
                AudioSessao.llamada_id == llamada_id
            ).first()
            
            if sessao_existente:
                logger.warning(f"Sessao ja existe para chamada {llamada_id}")
                return sessao_existente
            
            # Buscar contexto
            contexto = self.db.query(AudioContexto).filter(
                AudioContexto.id == contexto_id
            ).first()
            
            if not contexto:
                raise ValueError(f"Contexto {contexto_id} nao encontrado")
            
            # Criar nova sessao
            nova_sessao = AudioSessao(
                llamada_id=llamada_id,
                contexto_id=contexto_id,
                estado_atual=EstadoAudio.INICIANDO,
                audio_atual_url=contexto.audio_principal_url,
                timeout_dtmf=configuracoes_personalizadas.get("timeout_dtmf") if configuracoes_personalizadas else None,
                detectar_voicemail=configuracoes_personalizadas.get("detectar_voicemail") if configuracoes_personalizadas else None,
                dados_contexto=configuracoes_personalizadas or {}
            )
            
            self.db.add(nova_sessao)
            self.db.commit()
            self.db.refresh(nova_sessao)
            
            logger.info(f"Sessao de audio iniciada: {nova_sessao.id} para chamada {llamada_id}")
            
            # Processar evento inicial
            self.rules_engine.processar_evento(
                nova_sessao.id,
                TipoEvento.CHAMADA_INICIADA
            )
            
            return nova_sessao
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao iniciar sessao de audio: {str(e)}")
            raise
    
    def processar_evento_llamada(
        self,
        llamada_id: int,
        evento: TipoEvento,
        dados_evento: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa um evento relacionado a uma chamada.
        
        Args:
            llamada_id: ID da chamada
            evento: Tipo do evento
            dados_evento: Dados especificos do evento
            
        Returns:
            Dict: Resultado do processamento
        """
        try:
            # Buscar sessao ativa para a chamada
            sessao = self.db.query(AudioSessao).filter(
                AudioSessao.llamada_id == llamada_id
            ).first()
            
            if not sessao:
                logger.warning(f"Nenhuma sessao ativa encontrada para chamada {llamada_id}")
                return {
                    "sucesso": False,
                    "erro": "Sessao nao encontrada"
                }
            
            # Processar evento atraves do motor de regras
            resultado = self.rules_engine.processar_evento(
                sessao.id, evento, dados_evento
            )
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar evento da chamada {llamada_id}: {str(e)}")
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def obter_status_sessao(self, llamada_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtem o status atual de uma sessao de audio.
        
        Args:
            llamada_id: ID da chamada
            
        Returns:
            Dict: Status da sessao ou None se nao encontrada
        """
        try:
            sessao = self.db.query(AudioSessao).filter(
                AudioSessao.llamada_id == llamada_id
            ).first()
            
            if not sessao:
                return None
            
            # Calcular tempos
            agora = datetime.utcnow()
            tempo_total = (agora - sessao.iniciado_em).total_seconds()
            tempo_no_estado = (agora - sessao.ultima_mudanca_estado).total_seconds()
            
            return {
                "sessao_id": sessao.id,
                "llamada_id": sessao.llamada_id,
                "estado_atual": sessao.estado_atual.value,
                "estado_anterior": sessao.estado_anterior.value if sessao.estado_anterior else None,
                "audio_atual_url": sessao.audio_atual_url,
                "tempo_total_segundos": round(tempo_total),
                "tempo_no_estado_segundos": round(tempo_no_estado),
                "tentativas_realizadas": sessao.tentativas_realizadas,
                "timeout_dtmf": sessao.timeout_dtmf,
                "detectar_voicemail": sessao.detectar_voicemail,
                "dados_contexto": sessao.dados_contexto,
                "finalizado": sessao.estado_atual == EstadoAudio.FINALIZADO,
                "finalizado_em": sessao.finalizado_em.isoformat() if sessao.finalizado_em else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status da sessao: {str(e)}")
            return None 