"""
Serviço para gerenciar campanhas de discado preditivo com modo "Presione 1".
"""

import asyncio
import random
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_
from fastapi import HTTPException
from sqlalchemy.sql import text

from app.models.campana_presione1 import CampanaPresione1, LlamadaPresione1
# Removido: from app.models.lista_llamadas import ListaLlamadas, NumeroLlamada
from app.schemas.presione1 import (
    CampanaPresione1Create,
    CampanaPresione1Update,
    EstadisticasCampanaResponse,
    MonitorCampanaResponse
)
from app.services.cli_service import CliService
from app.services.blacklist_service import BlacklistService
# from app.services.asterisk import asterisk_service  # TODO: Implementar integração com Asterisk
from app.utils.logger import logger


class PresionE1Service:
    """Serviço para campanhas de discado preditivo con modo 'Presione 1'."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cli_service = CliService(db)
        self.blacklist_service = BlacklistService(db)
        self.campanhas_ativas = {}  # Armazena campanhas em execução
    
    def crear_campana(self, campana_data: CampanaPresione1Create) -> CampanaPresione1:
        """
        Cria uma nova campanha Presione 1.
        
        Args:
            campana_data: Dados da campanha a criar
            
        Returns:
            CampanaPresione1 criada
        """
        # Verificar se a campanha principal existe
        query_campanha = """
        SELECT id, name FROM campaigns WHERE id = :campaign_id
        """
        
        resultado = self.db.execute(
            text(query_campanha), 
            {"campaign_id": campana_data.campaign_id}
        ).fetchone()
        
        if not resultado:
            raise HTTPException(
                status_code=404,
                detail=f"Campanha principal {campana_data.campaign_id} não encontrada"
            )
        
        # Verificar se já existe uma campanha presione1 ativa para esta campanha principal
        campana_existente = self.db.query(CampanaPresione1).filter(
            CampanaPresione1.campaign_id == campana_data.campaign_id,
            CampanaPresione1.activa == True
        ).first()
        
        if campana_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe uma campanha presione1 ativa para a campanha {campana_data.campaign_id}"
            )
        
        # Crear nova campanha
        nova_campana = CampanaPresione1(
            nombre=campana_data.nombre,
            descripcion=campana_data.descripcion,
            campaign_id=campana_data.campaign_id,
            mensaje_audio_url=campana_data.mensaje_audio_url,
            timeout_presione1=campana_data.timeout_presione1,
            detectar_voicemail=campana_data.detectar_voicemail,
            mensaje_voicemail_url=campana_data.mensaje_voicemail_url,
            duracion_minima_voicemail=campana_data.duracion_minima_voicemail,
            duracion_maxima_voicemail=campana_data.duracion_maxima_voicemail,
            extension_transferencia=campana_data.extension_transferencia,
            cola_transferencia=campana_data.cola_transferencia,
            llamadas_simultaneas=campana_data.llamadas_simultaneas,
            tiempo_entre_llamadas=campana_data.tiempo_entre_llamadas,
            notas=campana_data.notas
        )
        
        try:
            self.db.add(nova_campana)
            self.db.commit()
            self.db.refresh(nova_campana)
            
            logger.info(f"Campanha Presione 1 criada: {nova_campana.nombre} [ID: {nova_campana.id}]")
            return nova_campana
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Erro ao criar campanha"
            )
    
    def obter_campana(self, campana_id: int) -> CampanaPresione1:
        """Obtém uma campanha por ID."""
        campana = self.db.query(CampanaPresione1).filter(
            CampanaPresione1.id == campana_id
        ).first()
        
        if not campana:
            raise HTTPException(
                status_code=404,
                detail=f"Campanha {campana_id} não encontrada"
            )
        
        return campana
    
    def listar_campanas(self, skip: int = 0, limit: int = 100, apenas_ativas: bool = False) -> List[CampanaPresione1]:
        """Lista campanhas."""
        query = self.db.query(CampanaPresione1)
        
        if apenas_ativas:
            query = query.filter(CampanaPresione1.activa == True)
        
        return query.order_by(CampanaPresione1.fecha_creacion.desc()).offset(skip).limit(limit).all()
    
    def atualizar_campana(self, campana_id: int, dados_atualizacao: CampanaPresione1Update) -> CampanaPresione1:
        """Atualiza uma campanha."""
        campana = self.obter_campana(campana_id)
        
        # Verificar se pode atualizar (não pode estar ativa)
        if campana.activa and not dados_atualizacao.activa is False:
            raise HTTPException(
                status_code=400,
                detail="Não é possível atualizar campanha ativa. Pare a campanha primeiro."
            )
        
        # Atualizar campos fornecidos
        for campo, valor in dados_atualizacao.dict(exclude_unset=True).items():
            setattr(campana, campo, valor)
        
        campana.fecha_actualizacion = func.now()
        self.db.commit()
        self.db.refresh(campana)
        
        logger.info(f"Campanha {campana_id} atualizada")
        return campana
    
    def obter_proximo_numero(self, campana_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém o próximo número para discagem de uma campanha.
        
        Args:
            campana_id: ID da campanha presione1
            
        Returns:
            Dict com informações do número ou None se não há números disponíveis
        """
        try:
            # Buscar campanha
            campana = self.obter_campana(campana_id)
            
            # Buscar números da campanha principal que ainda não foram discados nesta campanha presione1
            query = """
            SELECT c.phone_number, c.id as contact_id
            FROM contacts c
            WHERE c.campaign_id = :campaign_id
            AND c.phone_number IS NOT NULL 
            AND c.phone_number != ''
            AND NOT EXISTS (
                SELECT 1 FROM llamadas_presione1 ll 
                WHERE ll.campana_id = :campana_id 
                AND ll.numero_normalizado = c.phone_number
                AND ll.estado != 'error'
            )
            ORDER BY c.id
            LIMIT 1
            """
            
            resultado = self.db.execute(
                text(query), 
                {"campaign_id": campana.campaign_id, "campana_id": campana_id}
            ).fetchone()
            
            if not resultado:
                logger.info(f"Não há números disponíveis para campanha {campana_id}")
                return None
            
            phone_number = resultado[0]
            contact_id = resultado[1]
            
            # Normalizar número (remover caracteres especiais, etc.)
            numero_normalizado = self._normalizar_numero(phone_number)
            
            return {
                "numero_original": phone_number,
                "numero_normalizado": numero_normalizado,
                "contact_id": contact_id,
                "valido": True
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter próximo número para campanha {campana_id}: {str(e)}")
            return None
    
    def _normalizar_numero(self, numero: str) -> str:
        """
        Normaliza um número de telefone removendo caracteres especiais.
        
        Args:
            numero: Número original
            
        Returns:
            Número normalizado (apenas dígitos)
        """
        if not numero:
            return ""
        
        # Remover todos os caracteres exceto dígitos
        numero_limpo = ''.join(filter(str.isdigit, str(numero)))
        
        # Se começar com 0, assumir que é código de país e manter
        # Se não tiver código de país, pode adicionar lógica específica aqui
        
        return numero_limpo
    
    async def iniciar_campana(self, campana_id: int, usuario_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Inicia uma campanha de discado preditivo.
        
        Args:
            campana_id: ID da campanha
            usuario_id: ID do usuário que inicia
            
        Returns:
            Resultado do início da campanha
        """
        campana = self.obter_campana(campana_id)
        
        if campana.activa:
            raise HTTPException(
                status_code=400,
                detail="Campanha já está ativa"
            )
        
        # Verificar se há números disponíveis
        proximo = self.obter_proximo_numero(campana_id)
        if not proximo:
            raise HTTPException(
                status_code=400,
                detail="Não há números disponíveis para discado nesta campanha"
            )
        
        # Marcar campanha como ativa
        campana.activa = True
        campana.pausada = False
        self.db.commit()
        
        # Iniciar processo de discado em background
        self.campanhas_ativas[campana_id] = {
            "campana": campana,
            "ativa": True,
            "pausada": False,
            "usuario_id": usuario_id,
            "llamadas_activas": {}
        }
        
        # Criar task para gerenciar o discado
        asyncio.create_task(self._gerenciar_discado_campana(campana_id))
        
        logger.info(f"Campanha {campana_id} iniciada por usuário {usuario_id}")
        
        return {
            "mensaje": f"Campanha '{campana.nombre}' iniciada com sucesso",
            "campana_id": campana_id,
            "llamadas_simultaneas": campana.llamadas_simultaneas,
            "tiempo_entre_llamadas": campana.tiempo_entre_llamadas
        }
    
    async def pausar_campana(self, campana_id: int, pausar: bool, motivo: Optional[str] = None) -> Dict[str, Any]:
        """Pausa ou retoma uma campanha."""
        campana = self.obter_campana(campana_id)
        
        if not campana.activa:
            raise HTTPException(
                status_code=400,
                detail="Campanha não está ativa"
            )
        
        campana.pausada = pausar
        self.db.commit()
        
        # Atualizar estado em memória
        if campana_id in self.campanhas_ativas:
            self.campanhas_ativas[campana_id]["pausada"] = pausar
        
        action = "pausada" if pausar else "retomada"
        logger.info(f"Campanha {campana_id} {action}. Motivo: {motivo}")
        
        return {
            "mensaje": f"Campanha {action} com sucesso",
            "campana_id": campana_id,
            "pausada": pausar,
            "motivo": motivo
        }
    
    async def parar_campana(self, campana_id: int) -> Dict[str, Any]:
        """Para completamente uma campanha."""
        campana = self.obter_campana(campana_id)
        
        if not campana.activa:
            raise HTTPException(
                status_code=400,
                detail="Campanha não está ativa"
            )
        
        # Marcar como inativa
        campana.activa = False
        campana.pausada = False
        self.db.commit()
        
        # Remover de campanhas ativas
        if campana_id in self.campanhas_ativas:
            self.campanhas_ativas[campana_id]["ativa"] = False
            
            # Finalizar chamadas ativas
            for llamada_id in list(self.campanhas_ativas[campana_id]["llamadas_activas"].keys()):
                await self._finalizar_llamada(llamada_id, "campanha_parada")
            
            del self.campanhas_ativas[campana_id]
        
        logger.info(f"Campanha {campana_id} parada")
        
        return {
            "mensaje": "Campanha parada com sucesso",
            "campana_id": campana_id
        }
    
    async def _gerenciar_discado_campana(self, campana_id: int):
        """
        Processo principal que gerencia o discado de uma campanha.
        Executa em background e coordena as chamadas.
        """
        try:
            campana_info = self.campanhas_ativas[campana_id]
            campana = campana_info["campana"]
            
            logger.info(f"Iniciando gerenciamento de discado para campanha {campana_id}")
            
            while campana_info["ativa"]:
                # Verificar se está pausada
                if campana_info["pausada"]:
                    await asyncio.sleep(1)
                    continue
                
                # Verificar número de chamadas ativas
                llamadas_ativas = len(campana_info["llamadas_activas"])
                
                if llamadas_ativas < campana.llamadas_simultaneas:
                    # Pode iniciar mais chamadas
                    proximo = self.obter_proximo_numero(campana_id)
                    
                    if proximo:
                        # Iniciar nova chamada
                        await self._iniciar_llamada_campana(campana_id, proximo)
                    else:
                        # Não há mais números, aguardar chamadas ativas finalizarem
                        if llamadas_ativas == 0:
                            logger.info(f"Campanha {campana_id} finalizada - sem mais números")
                            await self.parar_campana(campana_id)
                            break
                
                # Aguardar antes da próxima iteração
                await asyncio.sleep(campana.tiempo_entre_llamadas)
        
        except Exception as e:
            logger.error(f"Erro no gerenciamento da campanha {campana_id}: {str(e)}")
            await self.parar_campana(campana_id)
    
    async def _iniciar_llamada_campana(self, campana_id: int, numero_info: Dict[str, Any]):
        """Inicia uma chamada individual na campanha."""
        try:
            campana = self.campanhas_ativas[campana_id]["campana"]
            
            # Gerar CLI aleatório
            try:
                cli_info = self.cli_service.generar_cli_aleatorio(solo_poco_usados=True)
                cli = cli_info.cli_seleccionado
            except Exception:
                cli = "+5491122334455"  # CLI de fallback
            
            # Criar registro da chamada
            nueva_llamada = LlamadaPresione1(
                campana_id=campana_id,
                numero_destino=numero_info["numero_original"],
                numero_normalizado=numero_info["numero_normalizado"],
                cli_utilizado=cli,
                estado="marcando",
                fecha_inicio=datetime.now()
            )
            
            self.db.add(nueva_llamada)
            self.db.commit()
            self.db.refresh(nueva_llamada)
            
            # Adicionar à lista de chamadas ativas
            self.campanhas_ativas[campana_id]["llamadas_activas"][nueva_llamada.id] = nueva_llamada
            
            # TODO: Iniciar chamada via Asterisk com suporte a voicemail (não implementado)
            # respuesta_asterisk = await asterisk_service.originar_llamada_presione1(
            #     numero_destino=numero_info["numero_normalizado"],
            #     cli=cli,
            #     audio_url=campana.mensaje_audio_url,
            #     timeout_dtmf=campana.timeout_presione1,
            #     llamada_id=nueva_llamada.id,
            #     detectar_voicemail=campana.detectar_voicemail,
            #     mensaje_voicemail_url=campana.mensaje_voicemail_url,
            #     duracion_maxima_voicemail=campana.duracion_maxima_voicemail
            # )
            
            # Simulação para teste
            respuesta_asterisk = {
                "UniqueID": f"sim_{nueva_llamada.id}_{int(datetime.now().timestamp())}",
                "Channel": f"SIP/teste-{nueva_llamada.id}"
            }
            
            # Atualizar dados técnicos
            nueva_llamada.unique_id_asterisk = respuesta_asterisk.get("UniqueID")
            nueva_llamada.channel = respuesta_asterisk.get("Channel")
            self.db.commit()
            
            logger.info(f"Chamada iniciada para {numero_info['numero_normalizado']} na campanha {campana_id}")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar chamada: {str(e)}")
            # Marcar chamada como erro se foi criada
            if 'nueva_llamada' in locals():
                nueva_llamada.estado = "error"
                nueva_llamada.motivo_finalizacion = str(e)
                nueva_llamada.fecha_fin = datetime.now()
                self.db.commit()
    
    async def processar_evento_asterisk(self, evento: Dict[str, Any]):
        """
        Processa eventos recebidos do Asterisk para atualizar estados das chamadas.
        
        Args:
            evento: Evento recebido do Asterisk
        """
        evento_tipo = evento.get("Event")
        llamada_id = evento.get("LlamadaID")
        
        if not llamada_id:
            return
        
        llamada = self.db.query(LlamadaPresione1).filter(
            LlamadaPresione1.id == llamada_id
        ).first()
        
        if not llamada:
            return
        
        if evento_tipo == "CallAnswered":
            answer_type = evento.get("AnswerType", "Unknown")
            if answer_type == "Human":
                llamada.estado = "contestada"
                llamada.fecha_contestada = datetime.now()
                llamada.voicemail_detectado = False
            
        elif evento_tipo == "VoicemailDetected":
            llamada.estado = "voicemail_detectado"
            llamada.voicemail_detectado = True
            llamada.fecha_voicemail_detectado = datetime.now()
            llamada.fecha_contestada = datetime.now()  # Considerar como atendida para estatísticas
            logger.info(f"Voicemail detectado na chamada {llamada_id}")
            
        elif evento_tipo == "VoicemailAudioStarted":
            llamada.estado = "voicemail_audio_reproducido"
            llamada.fecha_voicemail_audio_inicio = datetime.now()
            audio_url = evento.get("AudioURL")
            max_duration = evento.get("MaxDuration")
            logger.info(f"Reproduzindo áudio no voicemail da chamada {llamada_id}: {audio_url}")
            
        elif evento_tipo == "VoicemailAudioFinished":
            llamada.fecha_voicemail_audio_fin = datetime.now()
            audio_duration = evento.get("AudioDuration", 0)
            llamada.duracion_mensaje_voicemail = int(audio_duration)
            reason = evento.get("Reason", "Unknown")
            
            if reason == "Completed":
                llamada.estado = "voicemail_finalizado"
                await self._finalizar_llamada(llamada.id, "voicemail_mensaje_dejado")
            else:
                await self._finalizar_llamada(llamada.id, f"voicemail_error_{reason}")
                
            logger.info(f"Áudio do voicemail finalizado para chamada {llamada_id}. Duração: {audio_duration}s")
            
        elif evento_tipo == "AudioStarted":
            llamada.estado = "audio_reproducido"
            llamada.fecha_audio_inicio = datetime.now()
            
        elif evento_tipo == "WaitingDTMF":
            llamada.estado = "esperando_dtmf"
            
        elif evento_tipo == "DTMFReceived":
            dtmf = evento.get("DTMF")
            llamada.dtmf_recibido = dtmf
            llamada.fecha_dtmf_recibido = datetime.now()
            
            # Calcular tempo de resposta
            if llamada.fecha_audio_inicio:
                tiempo_respuesta = (datetime.now() - llamada.fecha_audio_inicio).total_seconds()
                llamada.tiempo_respuesta_dtmf = tiempo_respuesta
            
            if dtmf == "1":
                llamada.presiono_1 = True
                llamada.estado = "presiono_1"
                # Transferir chamada
                await self._transferir_llamada(llamada)
            else:
                llamada.presiono_1 = False
                llamada.estado = "no_presiono"
                await self._finalizar_llamada(llamada.id, "no_presiono_1")
                
        elif evento_tipo == "DTMFTimeout":
            llamada.estado = "no_presiono"
            llamada.presiono_1 = False
            await self._finalizar_llamada(llamada.id, "timeout_dtmf")
            
        elif evento_tipo == "CallHangup":
            # Determinar motivo baseado no estado atual
            if llamada.estado == "voicemail_detectado" and not evento.get("CauseTxt", "").find("Voicemail") >= 0:
                await self._finalizar_llamada(llamada.id, "voicemail_colgado_sem_mensagem")
            else:
                await self._finalizar_llamada(llamada.id, "colgado")
        
        self.db.commit()
    
    async def _transferir_llamada(self, llamada: LlamadaPresione1):
        """Transfere chamada que pressionou 1."""
        try:
            campana = llamada.campana
            
            if campana.extension_transferencia:
                # TODO: Transferir para extensão específica (não implementado)
                # await asterisk_service.transferir_llamada(
                #     channel=llamada.channel,
                #     destino=campana.extension_transferencia
                # )
                logger.info(f"Simulação: transferindo para extensão {campana.extension_transferencia}")
            elif campana.cola_transferencia:
                # TODO: Transferir para fila de agentes (não implementado)
                # await asterisk_service.transferir_a_cola(
                #     channel=llamada.channel,
                #     cola=campana.cola_transferencia
                # )
                logger.info(f"Simulação: transferindo para fila {campana.cola_transferencia}")
            
            llamada.estado = "transferida"
            llamada.fecha_transferencia = datetime.now()
            llamada.transferencia_exitosa = True
            llamada.motivo_finalizacion = "presiono_1_transferido"
            
            logger.info(f"Chamada {llamada.id} transferida com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao transferir chamada {llamada.id}: {str(e)}")
            llamada.transferencia_exitosa = False
            await self._finalizar_llamada(llamada.id, "erro_transferencia")
    
    async def _finalizar_llamada(self, llamada_id: int, motivo: str):
        """Finaliza uma chamada."""
        llamada = self.db.query(LlamadaPresione1).filter(
            LlamadaPresione1.id == llamada_id
        ).first()
        
        if not llamada:
            return
        
        llamada.estado = "finalizada"
        llamada.fecha_fin = datetime.now()
        llamada.motivo_finalizacion = motivo
        
        # Calcular duração total
        if llamada.fecha_inicio:
            duracao = (datetime.now() - llamada.fecha_inicio).total_seconds()
            llamada.duracion_total = int(duracao)
        
        # Calcular duração do áudio
        if llamada.fecha_audio_inicio and llamada.fecha_dtmf_recibido:
            duracao_audio = (llamada.fecha_dtmf_recibido - llamada.fecha_audio_inicio).total_seconds()
            llamada.duracion_audio = int(duracao_audio)
        
        self.db.commit()
        
        # Remover da lista de chamadas ativas
        campana_id = llamada.campana_id
        if campana_id in self.campanhas_ativas:
            if llamada_id in self.campanhas_ativas[campana_id]["llamadas_activas"]:
                del self.campanhas_ativas[campana_id]["llamadas_activas"][llamada_id]
        
        logger.info(f"Chamada {llamada_id} finalizada. Motivo: {motivo}")
    
    def obter_estadisticas_campana(self, campana_id: int) -> EstadisticasCampanaResponse:
        """Obtém estatísticas detalhadas de uma campanha."""
        campana = self.obter_campana(campana_id)
        
        # Contar números totais na lista
        total_numeros = self.db.query(NumeroLlamada).filter(
            NumeroLlamada.id_lista == campana.lista_llamadas_id,
            NumeroLlamada.valido == True
        ).count()
        
        # Contar chamadas realizadas
        llamadas_realizadas = self.db.query(LlamadaPresione1).filter(
            LlamadaPresione1.campana_id == campana_id
        ).count()
        
        # Estados das chamadas
        llamadas_contestadas = self.db.query(LlamadaPresione1).filter(
            LlamadaPresione1.campana_id == campana_id,
            LlamadaPresione1.fecha_contestada.isnot(None)
        ).count()
        
        llamadas_presiono_1 = self.db.query(LlamadaPresione1).filter(
            LlamadaPresione1.campana_id == campana_id,
            LlamadaPresione1.presiono_1 == True
        ).count()
        
        llamadas_no_presiono = self.db.query(LlamadaPresione1).filter(
            LlamadaPresione1.campana_id == campana_id,
            LlamadaPresione1.presiono_1 == False
        ).count()
        
        llamadas_transferidas = self.db.query(LlamadaPresione1).filter(
            LlamadaPresione1.campana_id == campana_id,
            LlamadaPresione1.transferencia_exitosa == True
        ).count()
        
        llamadas_error = self.db.query(LlamadaPresione1).filter(
            LlamadaPresione1.campana_id == campana_id,
            LlamadaPresione1.estado == "error"
        ).count()
        
        # Estatísticas de voicemail
        llamadas_voicemail = self.db.query(LlamadaPresione1).filter(
            LlamadaPresione1.campana_id == campana_id,
            LlamadaPresione1.voicemail_detectado == True
        ).count()
        
        llamadas_voicemail_mensaje_dejado = self.db.query(LlamadaPresione1).filter(
            LlamadaPresione1.campana_id == campana_id,
            LlamadaPresione1.motivo_finalizacion == "voicemail_mensaje_dejado"
        ).count()
        
        # Duração média das mensagens no voicemail
        duracion_media_mensaje_voicemail = self.db.query(func.avg(LlamadaPresione1.duracion_mensaje_voicemail)).filter(
            LlamadaPresione1.campana_id == campana_id,
            LlamadaPresione1.duracion_mensaje_voicemail.isnot(None)
        ).scalar()
        
        # Cálculos de percentuais
        tasa_contestacion = (llamadas_contestadas / llamadas_realizadas * 100) if llamadas_realizadas > 0 else 0
        tasa_presiono_1 = (llamadas_presiono_1 / llamadas_contestadas * 100) if llamadas_contestadas > 0 else 0
        tasa_transferencia = (llamadas_transferidas / llamadas_presiono_1 * 100) if llamadas_presiono_1 > 0 else 0
        
        # Percentuais de voicemail
        tasa_voicemail = (llamadas_voicemail / llamadas_realizadas * 100) if llamadas_realizadas > 0 else 0
        tasa_mensaje_voicemail = (llamadas_voicemail_mensaje_dejado / llamadas_voicemail * 100) if llamadas_voicemail > 0 else 0
        
        # Tempos médios
        tiempo_medio_respuesta = self.db.query(func.avg(LlamadaPresione1.tiempo_respuesta_dtmf)).filter(
            LlamadaPresione1.campana_id == campana_id,
            LlamadaPresione1.tiempo_respuesta_dtmf.isnot(None)
        ).scalar()
        
        duracion_media_llamada = self.db.query(func.avg(LlamadaPresione1.duracion_total)).filter(
            LlamadaPresione1.campana_id == campana_id,
            LlamadaPresione1.duracion_total.isnot(None)
        ).scalar()
        
        # Chamadas ativas
        llamadas_activas = 0
        if campana_id in self.campanhas_ativas:
            llamadas_activas = len(self.campanhas_ativas[campana_id]["llamadas_activas"])
        
        return EstadisticasCampanaResponse(
            campana_id=campana_id,
            nombre_campana=campana.nombre,
            total_numeros=total_numeros,
            llamadas_realizadas=llamadas_realizadas,
            llamadas_pendientes=total_numeros - llamadas_realizadas,
            llamadas_contestadas=llamadas_contestadas,
            llamadas_presiono_1=llamadas_presiono_1,
            llamadas_no_presiono=llamadas_no_presiono,
            llamadas_transferidas=llamadas_transferidas,
            llamadas_error=llamadas_error,
            # Estatísticas de voicemail
            llamadas_voicemail=llamadas_voicemail,
            llamadas_voicemail_mensaje_dejado=llamadas_voicemail_mensaje_dejado,
            tasa_voicemail=round(tasa_voicemail, 2),
            tasa_mensaje_voicemail=round(tasa_mensaje_voicemail, 2),
            duracion_media_mensaje_voicemail=round(duracion_media_mensaje_voicemail, 2) if duracion_media_mensaje_voicemail else None,
            # Percentuais existentes
            tasa_contestacion=round(tasa_contestacion, 2),
            tasa_presiono_1=round(tasa_presiono_1, 2),
            tasa_transferencia=round(tasa_transferencia, 2),
            tiempo_medio_respuesta=tiempo_medio_respuesta,
            duracion_media_llamada=duracion_media_llamada,
            activa=campana.activa,
            pausada=campana.pausada,
            llamadas_activas=llamadas_activas
        ) 