"""
Serviço para gerenciar campanhas de discado preditivo com modo "Presione 1".
"""

import asyncio
import random
import time
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
from app.services.asterisk import asterisk_service  # Integração com Asterisk ativada
from app.utils.logger import logger


class PresionE1Service:
    """Serviço para campanhas de discado preditivo con modo 'Presione 1' - 100% Supabase."""
    
    def __init__(self, db: Session = None):
        # db mantido para compatibilidade, mas não usado para presione1
        self.cli_service = CliService(db) if db else None
        self.blacklist_service = BlacklistService(db) if db else None
        self.campanhas_ativas = {}  # Armazena campanhas em execução
        self._supabase_config = self._init_supabase()
        # Cache para otimização de performance
        self._cache = {}
        self._cache_ttl = {}
        self._query_times = {}  # Para monitorar tempos de consulta
    
    def _init_supabase(self) -> Dict[str, str]:
        """Inicializa configuração do Supabase."""
        import os
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("Configuração do Supabase não encontrada")
            raise Exception("SUPABASE_URL e SUPABASE_ANON_KEY são obrigatórios")
        
        return {
            "url": supabase_url,
            "key": supabase_key,
            "headers": {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            }
        }
    
    def _supabase_request(self, method: str, table: str, data=None, filters=None, select=None, use_count=False) -> Dict[str, Any]:
        """Método centralizado para requests ao Supabase com monitoramento de performance."""
        import requests
        
        start_time = time.time()
        query_key = f"{method}_{table}"
        
        url = f"{self._supabase_config['url']}/rest/v1/{table}"
        headers = self._supabase_config['headers'].copy()
        
        # Adicionar filtros na URL
        if filters:
            filter_params = []
            for key, value in filters.items():
                if "=" in str(key):
                    # Filtro já formatado (ex: "id=eq.1")
                    filter_params.append(f"{key}")
                else:
                    # Filtro simples (ex: {"id": 1} -> "id=eq.1")
                    filter_params.append(f"{key}=eq.{value}")
            if filter_params:
                url += "?" + "&".join(filter_params)
        
        # Adicionar select ou count
        separator = "?" if "?" not in url else "&"
        if use_count:
            url += f"{separator}select=count"
            headers["Prefer"] = "count=exact"
        elif select:
            url += f"{separator}select={select}"
        
        # Configurar headers específicos por método
        if method.upper() in ["PATCH", "PUT", "POST"]:
            headers["Prefer"] = "return=representation"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            # Monitorar tempo de consulta
            query_time = time.time() - start_time
            if query_key not in self._query_times:
                self._query_times[query_key] = []
            self._query_times[query_key].append(query_time)
            
            # Log consultas lentas
            if query_time > 1.0:
                logger.warning(f"⚠️ Consulta lenta detectada: {method} {table} - {query_time:.2f}s")
            elif query_time > 0.5:
                logger.info(f"📊 Consulta moderada: {method} {table} - {query_time:.2f}s")
            
            if response.status_code not in [200, 201, 204, 206]:
                logger.error(f"Erro Supabase {method} {table}: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erro do Supabase: {response.text}"
                )
            
            if response.status_code == 204:
                return {"success": True}
            
            # Para count, retornar o número do header
            if use_count and "content-range" in response.headers:
                count_info = response.headers["content-range"]
                if "/" in count_info:
                    total = count_info.split("/")[1]
                    return {"count": int(total) if total != "*" else 0}
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Erro de conexão Supabase: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro de conexão com Supabase: {str(e)}"
            )
    
    def crear_campana(self, campana_data: CampanaPresione1Create) -> Dict[str, Any]:
        """
        Cria uma nova campanha Presione 1 no Supabase.
        
        Args:
            campana_data: Dados da campanha a criar
            
        Returns:
            Dict com dados da campanha criada
        """
        # Verificar se a campanha principal existe no Supabase
        campanhas_principais = self._supabase_request(
            "GET", 
            "campaigns", 
            filters={"id": campana_data.campaign_id},
            select="id,name"
        )
        
        if not campanhas_principais:
            raise HTTPException(
                status_code=404,
                detail=f"Campanha principal {campana_data.campaign_id} não encontrada"
            )
        
        # Verificar se já existe uma campanha presione1 ativa para esta campanha principal
        campanhas_existentes = self._supabase_request(
            "GET",
            "campanas_presione1",
            filters={
                "campaign_id": campana_data.campaign_id,
                "activa": "eq.true"
            }
        )
        
        if campanhas_existentes:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe uma campanha presione1 ativa para a campanha {campana_data.campaign_id}"
            )
        
        # Preparar dados para inserção
        nova_campana_data = {
            "nombre": campana_data.nombre,
            "descripcion": campana_data.descripcion,
            "campaign_id": campana_data.campaign_id,
            "mensaje_audio_url": campana_data.mensaje_audio_url,
            "timeout_presione1": campana_data.timeout_presione1,
            "detectar_voicemail": campana_data.detectar_voicemail,
            "mensaje_voicemail_url": campana_data.mensaje_voicemail_url,
            "duracion_minima_voicemail": campana_data.duracion_minima_voicemail,
            "duracion_maxima_voicemail": campana_data.duracion_maxima_voicemail,
            "extension_transferencia": campana_data.extension_transferencia,
            "cola_transferencia": campana_data.cola_transferencia,
            "llamadas_simultaneas": campana_data.llamadas_simultaneas,
            "tiempo_entre_llamadas": campana_data.tiempo_entre_llamadas,
            "notas": campana_data.notas,
            "activa": False,
            "pausada": False,
            "fecha_creacion": datetime.utcnow().isoformat(),
            "fecha_actualizacion": datetime.utcnow().isoformat()
        }
        
        # Criar campanha no Supabase
        nova_campana = self._supabase_request(
            "POST",
            "campanas_presione1",
            data=nova_campana_data
        )
        
        if not nova_campana:
            raise HTTPException(
                status_code=400,
                detail="Erro ao criar campanha no Supabase"
            )
        
        # Como pode retornar uma lista, pegar o primeiro elemento
        if isinstance(nova_campana, list):
            nova_campana = nova_campana[0]
        
        logger.info(f"Campanha Presione 1 criada: {nova_campana.get('nombre')} [ID: {nova_campana.get('id')}]")
        return nova_campana
    
    def obter_campana(self, campana_id: int) -> Dict[str, Any]:
        """Obtém uma campanha por ID, considerando estado em memória se ativa."""
        try:
            # Buscar dados base do Supabase
            campanhas = self._supabase_request(
                "GET",
                "campanas_presione1",
                filters={"id": campana_id}
            )
            
            if not campanhas:
                raise HTTPException(
                    status_code=404,
                    detail=f"Campanha {campana_id} não encontrada"
                )
            
            campana = campanhas[0]
            
            # Se a campanha está ativa em memória, usar estado em memória
            if campana_id in self.campanhas_ativas:
                estado_memoria = self.campanhas_ativas[campana_id]
                campana["activa"] = estado_memoria.get("ativa", campana.get("activa"))
                campana["pausada"] = estado_memoria.get("pausada", campana.get("pausada"))
                logger.debug(f"Campanha {campana_id} - usando estado em memória: ativa={campana['activa']}, pausada={campana['pausada']}")
            
            return campana
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao obter campanha {campana_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao buscar campanha: {str(e)}"
            )
    
    def listar_campanas(self, skip: int = 0, limit: int = 100, apenas_ativas: bool = False) -> List[Dict[str, Any]]:
        """Lista campanhas do Supabase."""
        try:
            filters = {}
            if apenas_ativas:
                filters["activa"] = "eq.true"
                
            # Supabase não suporta offset diretamente, usamos range
            range_header = None
            if skip > 0 or limit < 100:
                end = skip + limit - 1
                range_header = f"{skip}-{end}"
            
            # Para agora vou simplificar sem range, implementar depois se necessário
            campanhas = self._supabase_request(
                "GET",
                "campanas_presione1",
                filters=filters,
                select="*"
            )
            
            # Ordenar por fecha_creacion desc (mais recentes primeiro)
            if campanhas:
                campanhas.sort(key=lambda x: x.get('fecha_creacion', ''), reverse=True)
            
            # Aplicar skip e limit manualmente se necessário
            if skip > 0 or limit < 100:
                campanhas = campanhas[skip:skip+limit]
            
            return campanhas or []
            
        except Exception as e:
            logger.error(f"Erro ao listar campanhas: {str(e)}")
            return []
    
    def atualizar_campana(self, campana_id: int, dados_atualizacao: CampanaPresione1Update) -> Dict[str, Any]:
        """Atualiza uma campanha no Supabase."""
        campana = self.obter_campana(campana_id)
        
        # Verificar se pode atualizar (não pode estar ativa)
        if campana.get("activa") and not dados_atualizacao.activa is False:
            raise HTTPException(
                status_code=400,
                detail="Não é possível atualizar campanha ativa. Pare a campanha primeiro."
            )
        
        # Preparar dados para atualização
        dados_para_atualizar = dados_atualizacao.dict(exclude_unset=True)
        dados_para_atualizar["fecha_actualizacion"] = datetime.utcnow().isoformat()
        
        # Atualizar no Supabase
        campanhas_atualizadas = self._supabase_request(
            "PATCH",
            "campanas_presione1",
            data=dados_para_atualizar,
            filters={"id": campana_id}
        )
        
        if not campanhas_atualizadas:
            raise HTTPException(
                status_code=500,
                detail="Erro ao atualizar campanha no Supabase"
            )
        
        # Pegar primeiro resultado se for lista
        campanha_atualizada = campanhas_atualizadas[0] if isinstance(campanhas_atualizadas, list) else campanhas_atualizadas
        
        logger.info(f"Campanha {campana_id} atualizada no Supabase")
        return campanha_atualizada
    
    def obter_proximo_numero(self, campana_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém o próximo número para discagem de uma campanha via Supabase.
        
        Args:
            campana_id: ID da campanha presione1
            
        Returns:
            Dict com informações do número ou None se não há números disponíveis
        """
        try:
            logger.info(f"🔍 Buscando próximo número para campanha {campana_id}")
            
            # Buscar campanha
            campana = self.obter_campana(campana_id)
            campaign_id = campana.get("campaign_id")
            
            logger.info(f"📋 Campanha presione1 {campana_id} vinculada à campanha principal {campaign_id}")
            
            if not campaign_id:
                logger.error(f"❌ Campanha {campana_id} não tem campaign_id associado")
                return None
            
            # Buscar contatos da campanha principal
            logger.info(f"🔎 Buscando contatos para campaign_id {campaign_id}...")
            contatos = self._supabase_request(
                "GET",
                "contacts",
                filters={"campaign_id": campaign_id},
                select="id,phone_number,name"
            )
            
            if not contatos:
                logger.warning(f"⚠️ Não há contatos para campaign_id {campaign_id}")
                return None
            
            logger.info(f"📞 Encontrados {len(contatos)} contatos para campaign_id {campaign_id}")
            
            # Buscar chamadas já realizadas para esta campanha presione1
            logger.info(f"🔍 Verificando chamadas já realizadas para campanha presione1 {campana_id}...")
            llamadas_existentes = self._supabase_request(
                "GET",
                "llamadas_presione1",
                filters={"campana_id": campana_id},
                select="numero_normalizado,estado"
            )
            
            # Criar set dos números já discados para busca rápida
            numeros_discados = set()
            if llamadas_existentes:
                for llamada in llamadas_existentes:
                    # Filtrar apenas estados válidos (ignorar errors)
                    estado = llamada.get("estado")
                    if estado and estado != "error":
                        numero = llamada.get("numero_normalizado")
                        if numero:
                            numeros_discados.add(numero)
                logger.info(f"📊 {len(numeros_discados)} números já foram discados nesta campanha (excluindo errors)")
            else:
                logger.info(f"✅ Nenhuma chamada realizada ainda nesta campanha")
            
            # Buscar primeiro contato não discado
            logger.info(f"🎯 Procurando primeiro contato não discado...")
            for i, contato in enumerate(contatos):
                phone_number = contato.get("phone_number")
                if not phone_number or phone_number.strip() == "":
                    logger.debug(f"⚠️ Contato {i+1} tem phone_number vazio: {contato}")
                    continue
                
                numero_normalizado = self._normalizar_numero(phone_number)
                logger.debug(f"🔢 Contato {i+1}: {phone_number} -> {numero_normalizado}")
                
                # Verificar se já foi discado
                if numero_normalizado not in numeros_discados:
                    logger.info(f"✅ Próximo número encontrado: {phone_number} (normalizado: {numero_normalizado})")
                    return {
                        "numero_original": phone_number,
                        "numero_normalizado": numero_normalizado,
                        "contact_id": contato.get("id"),
                        "valido": True
                    }
                else:
                    logger.debug(f"⏭️ Contato {i+1} já foi discado: {numero_normalizado}")
            
            logger.warning(f"⚠️ Todos os {len(contatos)} contatos já foram discados para campanha {campana_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter próximo número para campanha {campana_id}: {str(e)}")
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
    
    def _atualizar_campana_supabase(self, campana_id: int, dados: Dict[str, Any]) -> bool:
        """Atualiza uma campanha no Supabase usando método centralizado."""
        try:
            # Adicionar timestamp de atualização
            dados_com_timestamp = dados.copy()
            dados_com_timestamp["fecha_actualizacion"] = datetime.utcnow().isoformat()
            
            logger.info(f"🔄 Atualizando campanha {campana_id} no Supabase com dados: {dados_com_timestamp}")
            
            resultado = self._supabase_request(
                "PATCH",
                "campanas_presione1",
                data=dados_com_timestamp,
                filters={"id": campana_id}
            )
            
            if resultado:
                logger.info(f"✅ Campanha {campana_id} atualizada no Supabase com sucesso: {dados_com_timestamp}")
                
                # Verificar se a atualização foi persistida
                campana_verificacao = self._supabase_request(
                    "GET",
                    "campanas_presione1",
                    filters={"id": campana_id},
                    select="id,activa,pausada,fecha_actualizacion"
                )
                
                if campana_verificacao:
                    logger.info(f"🔍 Verificação pós-atualização campanha {campana_id}: {campana_verificacao[0]}")
                
                return True
            else:
                logger.error(f"❌ Erro ao atualizar campanha {campana_id} - resultado vazio")
                return False
                
        except Exception as e:
            logger.error(f"💥 Erro ao atualizar campanha {campana_id}: {str(e)}")
            return False
    
    def _atualizar_campanha_principal(self, campaign_id: int, status: str) -> bool:
        """Atualiza o status da campanha principal na tabela campaigns."""
        if not campaign_id:
            logger.warning("ID da campanha principal não fornecido")
            return False
            
        try:
            resultado = self._supabase_request(
                "PATCH",
                "campaigns",
                data={"status": status},
                filters={"id": campaign_id}
            )
            
            if resultado:
                logger.info(f"Campanha principal {campaign_id} atualizada para status '{status}'")
                return True
            else:
                logger.warning(f"Falha ao atualizar campanha principal {campaign_id}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao atualizar campanha principal {campaign_id}: {str(e)}")
            return False
    
    async def iniciar_campana(self, campana_id: int, usuario_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Inicia uma campanha de discado preditivo.
        
        Args:
            campana_id: ID da campanha
            usuario_id: ID do usuário que inicia
            
        Returns:
            Resultado do início da campanha
        """
        logger.info(f"🚀 Iniciando campanha {campana_id} por usuário {usuario_id}")
        
        # Buscar campanha
        campana = self.obter_campana(campana_id)
        logger.info(f"📋 Campanha encontrada: {campana.get('nombre')} (campaign_id: {campana.get('campaign_id')})")
        
        if campana.get("activa"):
            logger.warning(f"❌ Campanha {campana_id} já está ativa")
            raise HTTPException(
                status_code=400,
                detail="Campanha já está ativa"
            )
        
        # Verificar se há números disponíveis com detalhes melhorados
        logger.info(f"🔍 Verificando números disponíveis para campanha {campana_id}...")
        proximo = self.obter_proximo_numero(campana_id)
        
        if not proximo:
            campaign_id = campana.get("campaign_id")
            
            # Diagnóstico detalhado do problema
            if not campaign_id:
                logger.error(f"❌ Campanha {campana_id} não tem campaign_id associado")
                raise HTTPException(
                    status_code=400,
                    detail=f"Campanha não tem uma campanha principal (campaign_id) associada. Configure uma campanha principal primeiro."
                )
            
            # Verificar se existem contatos para a campanha principal
            try:
                contatos = self._supabase_request(
                    "GET",
                    "contacts",
                    filters={"campaign_id": campaign_id},
                    select="id,phone_number"
                )
                
                if not contatos:
                    logger.warning(f"⚠️ Nenhum contato encontrado para campaign_id {campaign_id}. Criando contatos de teste...")
                    
                    # Criar contatos de teste automaticamente
                    try:
                        resultado_contatos = await self.popular_contatos_teste(campana_id)
                        logger.info(f"✅ Contatos de teste criados: {resultado_contatos.get('contatos_criados', 0)}")
                        
                        # Tentar novamente obter próximo número
                        proximo = self.obter_proximo_numero(campana_id)
                        if not proximo:
                            raise HTTPException(
                                status_code=500,
                                detail="Erro interno: Não foi possível criar contatos de teste válidos"
                            )
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao criar contatos de teste: {str(e)}")
                        raise HTTPException(
                            status_code=400,
                            detail=f"Não há contatos cadastrados para esta campanha. "
                                   f"Tentativa de criar contatos de teste falhou: {str(e)}. "
                                   f"Adicione contatos à campanha principal (ID: {campaign_id}) manualmente."
                        )
                else:
                    # Há contatos, mas todos já foram discados
                    total_contatos = len(contatos)
                    logger.error(f"❌ Todos os {total_contatos} contatos já foram discados para campanha {campana_id}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Todos os {total_contatos} contatos desta campanha já foram discados. "
                               f"Adicione mais contatos ou reinicie a campanha para rediscar."
                    )
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"❌ Erro ao verificar contatos para campaign_id {campaign_id}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro interno ao verificar contatos da campanha: {str(e)}"
                )
        
        logger.info(f"✅ Número disponível encontrado: {proximo.get('numero_original')}")
        
        # Marcar campanha como ativa no Supabase
        logger.info(f"🔄 Marcando campanha {campana_id} como ativa...")
        self._atualizar_campana_supabase(campana_id, {"activa": True, "pausada": False})
        
        # Atualizar status da campanha principal
        self._atualizar_campanha_principal(campana.get("campaign_id"), "active")
        
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
        
        logger.info(f"🎯 Campanha {campana_id} iniciada com sucesso por usuário {usuario_id}")
        
        return {
            "mensaje": f"Campanha '{campana.get('nombre', 'Sem nome')}' iniciada com sucesso",
            "campana_id": campana_id,
            "llamadas_simultaneas": campana.get("llamadas_simultaneas", 5),
            "tiempo_entre_llamadas": campana.get("tiempo_entre_llamadas", 1.0),
            "proximo_numero": proximo.get("numero_original")
        }
    
    async def pausar_campana(self, campana_id: int, pausar: bool, motivo: Optional[str] = None) -> Dict[str, Any]:
        """Pausa ou retoma uma campanha."""
        acao = "pausar" if pausar else "retomar"
        logger.info(f"🎯 Iniciando {acao} da campanha {campana_id}")
        
        campana = self.obter_campana(campana_id)
        logger.info(f"📊 Dados da campanha obtidos: activa={campana.get('activa')}, pausada={campana.get('pausada')}")
        
        if not campana.get("activa"):
            logger.error(f"❌ Campanha {campana_id} não está ativa")
            raise HTTPException(
                status_code=400,
                detail="Campanha não está ativa"
            )
        
        # Verificar estado atual na memória
        if campana_id in self.campanhas_ativas:
            estado_memoria = self.campanhas_ativas[campana_id]
            logger.info(f"🧠 Estado atual na memória: {estado_memoria}")
        else:
            logger.warning(f"⚠️ Campanha {campana_id} não encontrada na memória")
        
        # Atualizar no Supabase
        logger.info(f"💾 Atualizando no Supabase: pausada={pausar}")
        sucesso_supabase = self._atualizar_campana_supabase(campana_id, {"pausada": pausar})
        
        if not sucesso_supabase:
            logger.error(f"❌ Falha ao atualizar no Supabase")
            raise HTTPException(
                status_code=500,
                detail="Erro ao atualizar campanha no banco de dados"
            )
        
        # Atualizar status da campanha principal
        status_principal = "paused" if pausar else "active"
        logger.info(f"📝 Atualizando campanha principal (ID: {campana.get('campaign_id')}) para status: {status_principal}")
        self._atualizar_campanha_principal(campana.get("campaign_id"), status_principal)
        
        # Atualizar estado em memória
        if campana_id in self.campanhas_ativas:
            estado_anterior = self.campanhas_ativas[campana_id]["pausada"]
            self.campanhas_ativas[campana_id]["pausada"] = pausar
            logger.info(f"🔄 Estado na memória atualizado: {estado_anterior} -> {pausar}")
        else:
            logger.warning(f"⚠️ Campanha {campana_id} não está na memória para atualizar")
        
        action = "pausada" if pausar else "retomada"
        logger.info(f"✅ Campanha {campana_id} {action} com sucesso. Motivo: {motivo}")
        
        return {
            "mensaje": f"Campanha {action} com sucesso",
            "campana_id": campana_id,
            "pausada": pausar,
            "motivo": motivo
        }
    
    async def parar_campana(self, campana_id: int) -> Dict[str, Any]:
        """Para completamente uma campanha."""
        campana = self.obter_campana(campana_id)
        
        if not campana.get("activa"):
            raise HTTPException(
                status_code=400,
                detail="Campanha não está ativa"
            )
        
        # Marcar como inativa no Supabase
        self._atualizar_campana_supabase(campana_id, {"activa": False, "pausada": False})
        
        # Atualizar status da campanha principal para draft
        self._atualizar_campanha_principal(campana.get("campaign_id"), "draft")
        
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
                
                if llamadas_ativas < campana.get("llamadas_simultaneas", 5):
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
                await asyncio.sleep(campana.get("tiempo_entre_llamadas", 10))
        
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
            
            # Criar registro da chamada no Supabase
            llamada_data = {
                "campana_id": campana_id,
                "numero_destino": numero_info["numero_original"],
                "numero_normalizado": numero_info["numero_normalizado"],
                "cli_utilizado": cli,
                "estado": "marcando",
                "fecha_inicio": datetime.now().isoformat(),
                "voicemail_detectado": False,
                "presiono_1": False,
                "transferencia_exitosa": False
            }
            
            nueva_llamada_response = self._supabase_request(
                "POST",
                "llamadas_presione1",
                data=llamada_data
            )
            
            if not nueva_llamada_response:
                raise Exception("Erro ao criar chamada no Supabase")
            
            # Pegar dados da chamada criada
            nueva_llamada = nueva_llamada_response[0] if isinstance(nueva_llamada_response, list) else nueva_llamada_response
            llamada_id = nueva_llamada.get("id")
            
            # Adicionar à lista de chamadas ativas
            self.campanhas_ativas[campana_id]["llamadas_activas"][llamada_id] = nueva_llamada
            
            # Iniciar chamada via Asterisk com suporte a voicemail
            respuesta_asterisk = await asterisk_service.originar_llamada_presione1(
                numero_destino=numero_info["numero_normalizado"],
                cli=cli,
                audio_url=campana.get("mensaje_audio_url"),
                timeout_dtmf=campana.get("timeout_presione1", 15),
                llamada_id=nueva_llamada.get("id"),
                detectar_voicemail=campana.get("detectar_voicemail", True),
                mensaje_voicemail_url=campana.get("mensaje_voicemail_url"),
                duracion_maxima_voicemail=campana.get("duracion_maxima_voicemail", 30)
            )
            
            # Simulação desativada - usando Asterisk real
            # respuesta_asterisk = {
            #     "UniqueID": f"sim_{llamada_id}_{int(datetime.now().timestamp())}",
            #     "Channel": f"SIP/teste-{llamada_id}"
            # }
            
            # Atualizar dados técnicos no Supabase
            self._supabase_request(
                "PATCH",
                "llamadas_presione1",
                data={
                    "unique_id_asterisk": respuesta_asterisk.get("UniqueID"),
                    "channel": respuesta_asterisk.get("Channel")
                },
                filters={"id": llamada_id}
            )
            
            logger.info(f"Chamada iniciada para {numero_info['numero_normalizado']} na campanha {campana_id}")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar chamada: {str(e)}")
            # Marcar chamada como erro se foi criada
            if 'llamada_id' in locals() and llamada_id:
                self._supabase_request(
                    "PATCH",
                    "llamadas_presione1",
                    data={
                        "estado": "error",
                        "motivo_finalizacion": str(e),
                        "fecha_fin": datetime.now().isoformat()
                    },
                    filters={"id": llamada_id}
                )
    
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
        
        llamadas = self._supabase_request(
            "GET",
            "llamadas_presione1",
            filters={"id": llamada_id}
        )
        
        if not llamadas:
            return
        
        llamada = llamadas[0]
        
        # Preparar dados para atualização
        updates = {}
        
        if evento_tipo == "CallAnswered":
            answer_type = evento.get("AnswerType", "Unknown")
            if answer_type == "Human":
                updates.update({
                    "estado": "contestada",
                    "fecha_contestada": datetime.now().isoformat(),
                    "voicemail_detectado": False
                })
            
        elif evento_tipo == "VoicemailDetected":
            updates.update({
                "estado": "voicemail_detectado",
                "voicemail_detectado": True,
                "fecha_voicemail_detectado": datetime.now().isoformat(),
                "fecha_contestada": datetime.now().isoformat()  # Considerar como atendida para estatísticas
            })
            logger.info(f"Voicemail detectado na chamada {llamada_id}")
            
        elif evento_tipo == "VoicemailAudioStarted":
            updates.update({
                "estado": "voicemail_audio_reproducido",
                "fecha_voicemail_audio_inicio": datetime.now().isoformat()
            })
            audio_url = evento.get("AudioURL")
            max_duration = evento.get("MaxDuration")
            logger.info(f"Reproduzindo áudio no voicemail da chamada {llamada_id}: {audio_url}")
            
        elif evento_tipo == "VoicemailAudioFinished":
            audio_duration = evento.get("AudioDuration", 0)
            reason = evento.get("Reason", "Unknown")
            
            updates.update({
                "fecha_voicemail_audio_fin": datetime.now().isoformat(),
                "duracion_mensaje_voicemail": int(audio_duration)
            })
            
            if reason == "Completed":
                updates["estado"] = "voicemail_finalizado"
                await self._finalizar_llamada(llamada_id, "voicemail_mensaje_dejado")
            else:
                await self._finalizar_llamada(llamada_id, f"voicemail_error_{reason}")
                
            logger.info(f"Áudio do voicemail finalizado para chamada {llamada_id}. Duração: {audio_duration}s")
            
        elif evento_tipo == "AudioStarted":
            updates.update({
                "estado": "audio_reproducido",
                "fecha_audio_inicio": datetime.now().isoformat()
            })
            
        elif evento_tipo == "WaitingDTMF":
            updates["estado"] = "esperando_dtmf"
            
        elif evento_tipo == "DTMFReceived":
            dtmf = evento.get("DTMF")
            fecha_dtmf = datetime.now()
            
            updates.update({
                "dtmf_recibido": dtmf,
                "fecha_dtmf_recibido": fecha_dtmf.isoformat()
            })
            
            # Calcular tempo de resposta
            fecha_audio_inicio = llamada.get("fecha_audio_inicio")
            if fecha_audio_inicio:
                try:
                    # Parse da data ISO
                    inicio = datetime.fromisoformat(fecha_audio_inicio.replace('Z', '+00:00'))
                    tiempo_respuesta = (fecha_dtmf - inicio).total_seconds()
                    updates["tiempo_respuesta_dtmf"] = tiempo_respuesta
                except:
                    pass
            
            if dtmf == "1":
                updates.update({
                    "presiono_1": True,
                    "estado": "presiono_1"
                })
                # Atualizar primeiro, depois transferir
                if updates:
                    self._supabase_request("PATCH", "llamadas_presione1", data=updates, filters={"id": llamada_id})
                await self._transferir_llamada(llamada_id)
                return  # Já atualizou
            else:
                updates.update({
                    "presiono_1": False,
                    "estado": "no_presiono"
                })
                # Atualizar primeiro, depois finalizar
                if updates:
                    self._supabase_request("PATCH", "llamadas_presione1", data=updates, filters={"id": llamada_id})
                await self._finalizar_llamada(llamada_id, "no_presiono_1")
                return  # Já atualizou
                
        elif evento_tipo == "DTMFTimeout":
            updates.update({
                "estado": "no_presiono",
                "presiono_1": False
            })
            # Atualizar primeiro, depois finalizar
            if updates:
                self._supabase_request("PATCH", "llamadas_presione1", data=updates, filters={"id": llamada_id})
            await self._finalizar_llamada(llamada_id, "timeout_dtmf")
            return  # Já atualizou
            
        elif evento_tipo == "CallHangup":
            # Determinar motivo baseado no estado atual
            estado_atual = llamada.get("estado")
            if estado_atual == "voicemail_detectado" and not evento.get("CauseTxt", "").find("Voicemail") >= 0:
                await self._finalizar_llamada(llamada_id, "voicemail_colgado_sem_mensagem")
            else:
                await self._finalizar_llamada(llamada_id, "colgado")
            return  # Já atualizou
        
        # Aplicar atualizações se houver
        if updates:
            self._supabase_request(
                "PATCH",
                "llamadas_presione1",
                data=updates,
                filters={"id": llamada_id}
            )
    
    async def _transferir_llamada(self, llamada_id: int):
        """Transfere chamada que pressionou 1."""
        try:
            # Buscar dados da chamada
            llamadas = self._supabase_request("GET", "llamadas_presione1", filters={"id": llamada_id})
            if not llamadas:
                logger.error(f"Chamada {llamada_id} não encontrada para transferência")
                return
            
            llamada = llamadas[0]
            campana = self.obter_campana(llamada.get("campana_id"))
            
            extension_transferencia = campana.get("extension_transferencia")
            cola_transferencia = campana.get("cola_transferencia")
            
            if extension_transferencia:
                # Transferir para extensão específica
                await asterisk_service.transferir_llamada(
                    channel=llamada.get("channel"),
                    destino=extension_transferencia
                )
                logger.info(f"Transferindo para extensão {extension_transferencia}")
            elif cola_transferencia:
                # Transferir para fila de agentes
                await asterisk_service.transferir_a_cola(
                    channel=llamada.get("channel"),
                    cola=cola_transferencia
                )
                logger.info(f"Transferindo para fila {cola_transferencia}")
            
            # Atualizar estado no Supabase
            self._supabase_request(
                "PATCH",
                "llamadas_presione1",
                data={
                    "estado": "transferida",
                    "fecha_transferencia": datetime.now().isoformat(),
                    "transferencia_exitosa": True,
                    "motivo_finalizacion": "presiono_1_transferido"
                },
                filters={"id": llamada_id}
            )
            
            logger.info(f"Chamada {llamada_id} transferida com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao transferir chamada {llamada_id}: {str(e)}")
            # Marcar transferência como falhada
            self._supabase_request(
                "PATCH",
                "llamadas_presione1",
                data={"transferencia_exitosa": False},
                filters={"id": llamada_id}
            )
            await self._finalizar_llamada(llamada_id, "erro_transferencia")
    
    async def _finalizar_llamada(self, llamada_id: int, motivo: str):
        """Finaliza uma chamada."""
        try:
            # Buscar dados da chamada
            llamadas = self._supabase_request("GET", "llamadas_presione1", filters={"id": llamada_id})
            if not llamadas:
                logger.error(f"Chamada {llamada_id} não encontrada para finalização")
                return
            
            llamada = llamadas[0]
            agora = datetime.now()
            
            # Preparar dados para atualização
            updates = {
                "estado": "finalizada",
                "fecha_fin": agora.isoformat(),
                "motivo_finalizacion": motivo
            }
            
            # Calcular duração total
            fecha_inicio = llamada.get("fecha_inicio")
            if fecha_inicio:
                try:
                    inicio = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
                    duracao = (agora - inicio).total_seconds()
                    updates["duracion_total"] = int(duracao)
                except:
                    pass
            
            # Calcular duração do áudio
            fecha_audio_inicio = llamada.get("fecha_audio_inicio")
            fecha_dtmf_recibido = llamada.get("fecha_dtmf_recibido")
            if fecha_audio_inicio and fecha_dtmf_recibido:
                try:
                    inicio_audio = datetime.fromisoformat(fecha_audio_inicio.replace('Z', '+00:00'))
                    fin_audio = datetime.fromisoformat(fecha_dtmf_recibido.replace('Z', '+00:00'))
                    duracao_audio = (fin_audio - inicio_audio).total_seconds()
                    updates["duracion_audio"] = int(duracao_audio)
                except:
                    pass
            
            # Atualizar no Supabase
            self._supabase_request(
                "PATCH", 
                "llamadas_presione1", 
                data=updates, 
                filters={"id": llamada_id}
            )
            
            # Remover da lista de chamadas ativas
            campana_id = llamada.get("campana_id")
            if campana_id and campana_id in self.campanhas_ativas:
                if llamada_id in self.campanhas_ativas[campana_id]["llamadas_activas"]:
                    del self.campanhas_ativas[campana_id]["llamadas_activas"][llamada_id]
            
            logger.info(f"Chamada {llamada_id} finalizada: {motivo}")
            
        except Exception as e:
            logger.error(f"Erro ao finalizar chamada {llamada_id}: {str(e)}")
    
    def _get_cached_result(self, cache_key: str, ttl: int = 30) -> Optional[Any]:
        """Obtém resultado do cache se ainda válido."""
        if cache_key in self._cache:
            cache_time = self._cache_ttl.get(cache_key, 0)
            if time.time() - cache_time < ttl:
                logger.debug(f"Cache hit para {cache_key}")
                return self._cache[cache_key]
        return None
    
    def _set_cache_result(self, cache_key: str, result: Any):
        """Armazena resultado no cache."""
        self._cache[cache_key] = result
        self._cache_ttl[cache_key] = time.time()
        logger.debug(f"Resultado cacheado para {cache_key}")
    
    def _calculate_statistics_optimized(self, llamadas: List[Dict]) -> Dict[str, Any]:
        """Calcula estatísticas de forma otimizada usando uma única passada."""
        stats = {
            "llamadas_realizadas": len(llamadas),
            "llamadas_contestadas": 0,
            "llamadas_presiono_1": 0,
            "llamadas_no_presiono": 0,
            "llamadas_transferidas": 0,
            "llamadas_error": 0,
            "llamadas_voicemail": 0,
            "llamadas_voicemail_mensaje_dejado": 0,
            "tasa_contestacion": 0.0,
            "tasa_presiono_1": 0.0,
            "tasa_transferencia": 0.0,
            "tasa_voicemail": 0.0,
            "tasa_mensaje_voicemail": 0.0,
            "tiempo_medio_respuesta": None,
            "duracion_media_llamada": None,
            "duracion_media_mensaje_voicemail": None
        }
        
        if not llamadas:
            return stats
        
        # Listas para cálculos de média
        tiempos_respuesta = []
        duraciones_llamada = []
        duraciones_voicemail = []
        
        # Uma única passada pelos dados
        for llamada in llamadas:
            # Contestadas
            if llamada.get("fecha_contestada"):
                stats["llamadas_contestadas"] += 1
                
                # Presiono 1
                if llamada.get("presiono_1") is True:
                    stats["llamadas_presiono_1"] += 1
                elif llamada.get("presiono_1") is False:
                    stats["llamadas_no_presiono"] += 1
            
            # Transferidas
            if llamada.get("transferencia_exitosa") is True:
                stats["llamadas_transferidas"] += 1
            
            # Erro
            if llamada.get("estado") == "error":
                stats["llamadas_error"] += 1
            
            # Voicemail
            if llamada.get("voicemail_detectado") is True:
                stats["llamadas_voicemail"] += 1
                
                if llamada.get("motivo_finalizacion") == "voicemail_mensaje_dejado":
                    stats["llamadas_voicemail_mensaje_dejado"] += 1
                
                # Duração voicemail
                duracion_vm = llamada.get("duracion_mensaje_voicemail")
                if duracion_vm:
                    duraciones_voicemail.append(duracion_vm)
            
            # Tempos de resposta
            tiempo_resp = llamada.get("tiempo_respuesta_dtmf")
            if tiempo_resp:
                tiempos_respuesta.append(tiempo_resp)
            
            # Duração da chamada
            duracion = llamada.get("duracion_total")
            if duracion:
                duraciones_llamada.append(duracion)
        
        # Calcular percentuais
        if stats["llamadas_realizadas"] > 0:
            stats["tasa_contestacion"] = round((stats["llamadas_contestadas"] / stats["llamadas_realizadas"]) * 100, 2)
            stats["tasa_voicemail"] = round((stats["llamadas_voicemail"] / stats["llamadas_realizadas"]) * 100, 2)
        
        if stats["llamadas_contestadas"] > 0:
            stats["tasa_presiono_1"] = round((stats["llamadas_presiono_1"] / stats["llamadas_contestadas"]) * 100, 2)
        
        if stats["llamadas_presiono_1"] > 0:
            stats["tasa_transferencia"] = round((stats["llamadas_transferidas"] / stats["llamadas_presiono_1"]) * 100, 2)
        
        if stats["llamadas_voicemail"] > 0:
            stats["tasa_mensaje_voicemail"] = round((stats["llamadas_voicemail_mensaje_dejado"] / stats["llamadas_voicemail"]) * 100, 2)
        
        # Calcular médias
        if tiempos_respuesta:
            stats["tiempo_medio_respuesta"] = round(sum(tiempos_respuesta) / len(tiempos_respuesta), 2)
        
        if duraciones_llamada:
            stats["duracion_media_llamada"] = round(sum(duraciones_llamada) / len(duraciones_llamada), 2)
        
        if duraciones_voicemail:
            stats["duracion_media_mensaje_voicemail"] = round(sum(duraciones_voicemail) / len(duraciones_voicemail), 2)
        
        return stats
    
    def obter_estadisticas_campana(self, campana_id: int) -> EstadisticasCampanaResponse:
        """Obtém estatísticas detalhadas de uma campanha usando Supabase com cache."""
        try:
            # Verificar cache (30 segundos)
            cache_key = f"stats_campana_{campana_id}"
            cached_result = self._get_cached_result(cache_key, 30)
            if cached_result:
                return cached_result
            
            # Buscar dados da campanha (cache por 5 minutos)
            campana_cache_key = f"campana_{campana_id}"
            campana = self._get_cached_result(campana_cache_key, 300)
            if not campana:
                campana = self.obter_campana(campana_id)
                self._set_cache_result(campana_cache_key, campana)
            
            campaign_id = campana.get("campaign_id")
            
            # Buscar contatos totais usando count otimizado
            total_numeros = 0
            if campaign_id:
                try:
                    count_result = self._supabase_request(
                        "GET",
                        "contacts",
                        filters={"campaign_id": campaign_id},
                        use_count=True
                    )
                    total_numeros = count_result.get("count", 0) if count_result else 0
                except Exception as e:
                    logger.warning(f"Erro ao buscar contatos da campanha {campaign_id}: {str(e)}")
            
            # Buscar llamadas com select otimizado
            try:
                llamadas = self._supabase_request(
                    "GET",
                    "llamadas_presione1",
                    filters={"campana_id": campana_id},
                    select="estado,fecha_contestada,presiono_1,transferencia_exitosa,voicemail_detectado,motivo_finalizacion,duracion_mensaje_voicemail,tiempo_respuesta_dtmf,duracion_total"
                )
                
                if not llamadas:
                    llamadas = []
                    
            except Exception as e:
                logger.warning(f"Erro ao buscar llamadas da campanha {campana_id}: {str(e)}")
                llamadas = []
            
            # Calcular estatísticas usando método otimizado
            stats = self._calculate_statistics_optimized(llamadas)
            
            # Chamadas ativas
            llamadas_activas = 0
            if campana_id in self.campanhas_ativas:
                llamadas_activas = len(self.campanhas_ativas[campana_id].get("llamadas_activas", []))
            
            response = EstadisticasCampanaResponse(
                campana_id=campana_id,
                nombre_campana=campana.get("nombre", "Campanha"),
                total_numeros=total_numeros,
                llamadas_realizadas=stats["llamadas_realizadas"],
                llamadas_pendientes=total_numeros - stats["llamadas_realizadas"],
                llamadas_contestadas=stats["llamadas_contestadas"],
                llamadas_presiono_1=stats["llamadas_presiono_1"],
                llamadas_no_presiono=stats["llamadas_no_presiono"],
                llamadas_transferidas=stats["llamadas_transferidas"],
                llamadas_error=stats["llamadas_error"],
                # Estatísticas de voicemail
                llamadas_voicemail=stats["llamadas_voicemail"],
                llamadas_voicemail_mensaje_dejado=stats["llamadas_voicemail_mensaje_dejado"],
                tasa_voicemail=stats["tasa_voicemail"],
                tasa_mensaje_voicemail=stats["tasa_mensaje_voicemail"],
                duracion_media_mensaje_voicemail=stats["duracion_media_mensaje_voicemail"],
                # Percentuais existentes
                tasa_contestacion=stats["tasa_contestacion"],
                tasa_presiono_1=stats["tasa_presiono_1"],
                tasa_transferencia=stats["tasa_transferencia"],
                tiempo_medio_respuesta=stats["tiempo_medio_respuesta"],
                duracion_media_llamada=stats["duracion_media_llamada"],
                activa=campana.get("activa", False),
                pausada=campana.get("pausada", False),
                llamadas_activas=llamadas_activas
            )
            
            # Armazenar no cache
            self._set_cache_result(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas da campanha {campana_id}: {str(e)}")
            # Retornar dados zerados em caso de erro
            return EstadisticasCampanaResponse(
                campana_id=campana_id,
                nombre_campana="Campanha",
                total_numeros=0,
                llamadas_realizadas=0,
                llamadas_pendientes=0,
                llamadas_contestadas=0,
                llamadas_presiono_1=0,
                llamadas_no_presiono=0,
                llamadas_transferidas=0,
                llamadas_error=0,
                llamadas_voicemail=0,
                llamadas_voicemail_mensaje_dejado=0,
                tasa_voicemail=0.0,
                tasa_mensaje_voicemail=0.0,
                duracion_media_mensaje_voicemail=None,
                tasa_contestacion=0.0,
                tasa_presiono_1=0.0,
                tasa_transferencia=0.0,
                tiempo_medio_respuesta=None,
                duracion_media_llamada=None,
                activa=False,
                pausada=False,
                llamadas_activas=0
            )

    async def popular_contatos_teste(self, campana_id: int) -> Dict[str, Any]:
        """
        Popula contatos de teste para uma campanha presione1.
        
        Args:
            campana_id: ID da campanha presione1
            
        Returns:
            Resultado da operação
        """
        logger.info(f"📝 Populando contatos de teste para campanha {campana_id}")
        
        # Verificar se a campanha existe
        campana = self.obter_campana(campana_id)
        campaign_id = campana.get("campaign_id")
        
        if not campaign_id:
            raise HTTPException(
                status_code=400,
                detail="Campanha não tem campaign_id associado. Configure uma campanha principal primeiro."
            )
        
        # Números de teste para criar
        contatos_teste = [
            {"phone_number": "+5511999000001", "name": "Contato Teste 1"},
            {"phone_number": "+5511999000002", "name": "Contato Teste 2"},
            {"phone_number": "+5511999000003", "name": "Contato Teste 3"},
            {"phone_number": "+5511999000004", "name": "Contato Teste 4"},
            {"phone_number": "+5511999000005", "name": "Contato Teste 5"},
            {"phone_number": "+5511999000006", "name": "Contato Teste 6"},
            {"phone_number": "+5511999000007", "name": "Contato Teste 7"},
            {"phone_number": "+5511999000008", "name": "Contato Teste 8"},
            {"phone_number": "+5511999000009", "name": "Contato Teste 9"},
            {"phone_number": "+5511999000010", "name": "Contato Teste 10"}
        ]
        
        contatos_criados = 0
        contatos_existentes = 0
        
        for contato_info in contatos_teste:
            phone_number = contato_info["phone_number"]
            name = contato_info["name"]
            
            # Verificar se já existe
            contatos_existentes_check = self._supabase_request(
                "GET",
                "contacts",
                filters={
                    "campaign_id": campaign_id,
                    "phone_number": f"eq.{phone_number}"
                },
                select="id"
            )
            
            if contatos_existentes_check:
                contatos_existentes += 1
                logger.debug(f"⏭️ Contato já existe: {phone_number}")
                continue
            
            # Criar contato
            contato_data = {
                "campaign_id": campaign_id,
                "phone_number": phone_number,
                "name": name,
                "status": "not_started",
                "attempts": 0,
                "created_at": datetime.utcnow().isoformat()
            }
            
            try:
                novo_contato = self._supabase_request(
                    "POST",
                    "contacts",
                    data=contato_data
                )
                
                if novo_contato:
                    contatos_criados += 1
                    logger.info(f"✅ Contato criado: {name} ({phone_number})")
                else:
                    logger.warning(f"⚠️ Falha ao criar contato: {phone_number}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao criar contato {phone_number}: {str(e)}")
                continue
        
        logger.info(f"🎯 Operação concluída: {contatos_criados} criados, {contatos_existentes} já existiam")
        
        return {
            "mensaje": f"Contatos de teste populados com sucesso",
            "campana_id": campana_id,
            "campaign_id": campaign_id,
            "contatos_criados": contatos_criados,
            "contatos_existentes": contatos_existentes,
            "total_contatos": contatos_criados + contatos_existentes,
            "numeros_teste": [c["phone_number"] for c in contatos_teste]
        }

    async def debug_campana(self, campana_id: int) -> Dict[str, Any]:
        """
        Faz diagnóstico completo de uma campanha presione1.
        
        Args:
            campana_id: ID da campanha presione1
            
        Returns:
            Diagnóstico completo da campanha
        """
        logger.info(f"🔍 Iniciando debug da campanha {campana_id}")
        
        debug_info = {
            "campana_id": campana_id,
            "timestamp": datetime.utcnow().isoformat(),
            "campanha_presione1": None,
            "campanha_principal": None,
            "contatos": {
                "total": 0,
                "amostra": []
            },
            "llamadas_realizadas": {
                "total": 0,
                "amostra": []
            },
            "problemas": [],
            "pode_iniciar": False,
            "proxima_acao": ""
        }
        
        try:
            # 1. Verificar campanha presione1
            try:
                campana = self.obter_campana(campana_id)
                debug_info["campanha_presione1"] = campana
                logger.info(f"✅ Campanha presione1 encontrada: {campana.get('nombre')}")
            except Exception as e:
                debug_info["problemas"].append(f"Campanha presione1 não encontrada: {str(e)}")
                debug_info["proxima_acao"] = "Criar campanha presione1 primeiro"
                return debug_info
            
            # 2. Verificar campaign_id
            campaign_id = campana.get("campaign_id")
            debug_info["campanha_principal"] = campaign_id
            debug_info["logs_passos"].append(f"🔍 Passo 2: Campaign_id = {campaign_id}")
            
            if not campaign_id:
                debug_info["problemas"].append("Passo 2 FALHOU: campaign_id é None")
                return debug_info
            
            logger.info(f"📋 Campaign_id associado: {campaign_id}")
            
            # 3. Verificar campanha principal
            try:
                campanhas_principais = self._supabase_request(
                    "GET", 
                    "campaigns", 
                    filters={"id": campaign_id},
                    select="*"
                )
                
                if campanhas_principais:
                    debug_info["campanha_principal"] = campanhas_principais[0]
                    logger.info(f"✅ Campanha principal encontrada: {campanhas_principais[0].get('name')}")
                else:
                    debug_info["problemas"].append(f"Campanha principal {campaign_id} não encontrada")
                    debug_info["proxima_acao"] = f"Criar campanha principal com ID {campaign_id}"
                    return debug_info
                    
            except Exception as e:
                debug_info["problemas"].append(f"Erro ao buscar campanha principal: {str(e)}")
                return debug_info
            
            # 4. Verificar contatos
            try:
                contatos = self._supabase_request(
                    "GET",
                    "contacts",
                    filters={"campaign_id": campaign_id},
                    select="id,phone_number,name,status"
                )
                
                if contatos:
                    debug_info["contatos"]["total"] = len(contatos)
                    debug_info["contatos"]["amostra"] = contatos[:5]  # Primeiros 5
                    logger.info(f"📞 {len(contatos)} contatos encontrados")
                else:
                    debug_info["problemas"].append("Nenhum contato encontrado na campanha principal")
                    debug_info["proxima_acao"] = f"Adicionar contatos à campanha principal {campaign_id} ou usar /popular-contatos-teste"
                    
            except Exception as e:
                debug_info["problemas"].append(f"Erro ao buscar contatos: {str(e)}")
            
            # 5. Verificar chamadas realizadas
            try:
                llamadas = self._supabase_request(
                    "GET",
                    "llamadas_presione1",
                    filters={"campana_id": campana_id},
                    select="id,numero_destino,estado,fecha_inicio"
                )
                
                if llamadas:
                    debug_info["llamadas_realizadas"]["total"] = len(llamadas)
                    debug_info["llamadas_realizadas"]["amostra"] = llamadas[:5]  # Primeiras 5
                    logger.info(f"📊 {len(llamadas)} chamadas já realizadas")
                else:
                    logger.info(f"✅ Nenhuma chamada realizada ainda")
                    
            except Exception as e:
                debug_info["problemas"].append(f"Erro ao buscar chamadas: {str(e)}")
            
            # 6. Determinar se pode iniciar
            if (debug_info["campanha_presione1"] and 
                debug_info["campanha_principal"] and 
                debug_info["contatos"]["total"] > 0 and
                not campana.get("activa")):
                
                debug_info["pode_iniciar"] = True
                debug_info["proxima_acao"] = "Campanha pronta para iniciar!"
                
                # Verificar se há números ainda não discados
                contatos_totais = debug_info["contatos"]["total"]
                llamadas_realizadas = debug_info["llamadas_realizadas"]["total"]
                numeros_restantes = contatos_totais - llamadas_realizadas
                
                if numeros_restantes > 0:
                    debug_info["proxima_acao"] += f" ({numeros_restantes} números ainda não discados)"
                else:
                    debug_info["problemas"].append("Todos os contatos já foram discados")
                    debug_info["proxima_acao"] = "Adicionar mais contatos ou usar /popular-contatos-teste"
                    debug_info["pode_iniciar"] = False
                    
            elif campana.get("activa"):
                debug_info["problemas"].append("Campanha já está ativa")
                debug_info["proxima_acao"] = "Parar campanha primeiro para reiniciar"
                
            logger.info(f"🎯 Debug concluído. Pode iniciar: {debug_info['pode_iniciar']}")
            return debug_info
            
        except Exception as e:
            logger.error(f"❌ Erro durante debug: {str(e)}")
            debug_info["problemas"].append(f"Erro geral durante debug: {str(e)}")
            return debug_info

    async def debug_detalhado_campana(self, campana_id: int) -> Dict[str, Any]:
        """
        Debug detalhado passo a passo para identificar problemas específicos.
        """
        debug_detalhado = {
            "campana_id": campana_id,
            "timestamp": datetime.utcnow().isoformat(),
            "passo_1_campanha_presione1": None,
            "passo_2_campaign_id": None,
            "passo_3_contatos_raw": None,
            "passo_4_contatos_validos": None,
            "passo_5_llamadas_raw": None,
            "passo_6_numeros_discados": None,
            "passo_7_primeiro_disponivel": None,
            "problemas_identificados": [],
            "logs_passos": []
        }
        
        try:
            # Passo 1: Verificar campanha presione1
            debug_detalhado["logs_passos"].append("🔍 Passo 1: Verificando campanha presione1...")
            try:
                campana = self.obter_campana(campana_id)
                debug_detalhado["passo_1_campanha_presione1"] = campana
                debug_detalhado["logs_passos"].append(f"✅ Passo 1: Campanha encontrada - {campana.get('nombre')}")
            except Exception as e:
                debug_detalhado["problemas_identificados"].append(f"Passo 1 FALHOU: {str(e)}")
                return debug_detalhado
            
            # Passo 2: Verificar campaign_id
            campaign_id = campana.get("campaign_id")
            debug_detalhado["passo_2_campaign_id"] = campaign_id
            debug_detalhado["logs_passos"].append(f"🔍 Passo 2: Campaign_id = {campaign_id}")
            
            if not campaign_id:
                debug_detalhado["problemas_identificados"].append("Passo 2 FALHOU: campaign_id é None")
                return debug_detalhado
            
            # Passo 3: Buscar contatos RAW (exatamente como o código faz)
            debug_detalhado["logs_passos"].append("🔍 Passo 3: Buscando contatos RAW...")
            try:
                contatos_raw = self._supabase_request(
                    "GET",
                    "contacts",
                    filters={
                        "campaign_id": campaign_id,
                        "phone_number": "not.is.null"
                    },
                    select="id,phone_number,name"
                )
                debug_detalhado["passo_3_contatos_raw"] = {
                    "tipo": type(contatos_raw).__name__,
                    "count": len(contatos_raw) if contatos_raw else 0,
                    "amostra": contatos_raw[:3] if contatos_raw else []
                }
                debug_detalhado["logs_passos"].append(f"✅ Passo 3: {len(contatos_raw) if contatos_raw else 0} contatos encontrados")
            except Exception as e:
                debug_detalhado["problemas_identificados"].append(f"Passo 3 FALHOU: {str(e)}")
                return debug_detalhado
            
            # Passo 4: Filtrar contatos válidos
            debug_detalhado["logs_passos"].append("🔍 Passo 4: Filtrando contatos válidos...")
            contatos_validos = []
            if contatos_raw:
                for contato in contatos_raw:
                    phone_number = contato.get("phone_number")
                    if phone_number and phone_number.strip() != "":
                        contatos_validos.append({
                            "id": contato.get("id"),
                            "phone_number": phone_number,
                            "normalizado": self._normalizar_numero(phone_number)
                        })
            
            debug_detalhado["passo_4_contatos_validos"] = {
                "count": len(contatos_validos),
                "amostra": contatos_validos[:3]
            }
            debug_detalhado["logs_passos"].append(f"✅ Passo 4: {len(contatos_validos)} contatos válidos")
            
            # Passo 5: Buscar llamadas RAW
            debug_detalhado["logs_passos"].append("🔍 Passo 5: Buscando llamadas RAW...")
            try:
                llamadas_raw = self._supabase_request(
                    "GET",
                    "llamadas_presione1",
                    filters={
                        "campana_id": campana_id,
                        "estado": "not.eq.error"
                    },
                    select="numero_normalizado,estado"
                )
                debug_detalhado["passo_5_llamadas_raw"] = {
                    "tipo": type(llamadas_raw).__name__,
                    "count": len(llamadas_raw) if llamadas_raw else 0,
                    "amostra": llamadas_raw[:3] if llamadas_raw else []
                }
                debug_detalhado["logs_passos"].append(f"✅ Passo 5: {len(llamadas_raw) if llamadas_raw else 0} llamadas encontradas")
            except Exception as e:
                debug_detalhado["problemas_identificados"].append(f"Passo 5 FALHOU: {str(e)}")
                return debug_detalhado
            
            # Passo 6: Criar set de números discados
            debug_detalhado["logs_passos"].append("🔍 Passo 6: Criando set de números discados...")
            numeros_discados = set()
            if llamadas_raw:
                for llamada in llamadas_raw:
                    numero = llamada.get("numero_normalizado")
                    if numero:
                        numeros_discados.add(numero)
            
            debug_detalhado["passo_6_numeros_discados"] = {
                "count": len(numeros_discados),
                "amostra": list(numeros_discados)[:5]
            }
            debug_detalhado["logs_passos"].append(f"✅ Passo 6: {len(numeros_discados)} números únicos discados")
            
            # Passo 7: Procurar primeiro disponível
            debug_detalhado["logs_passos"].append("🔍 Passo 7: Procurando primeiro contato disponível...")
            primeiro_disponivel = None
            
            for i, contato in enumerate(contatos_validos):
                numero_normalizado = contato["normalizado"]
                if numero_normalizado not in numeros_discados:
                    primeiro_disponivel = {
                        "posicao": i,
                        "contato": contato,
                        "disponivel": True
                    }
                    break
            
            debug_detalhado["passo_7_primeiro_disponivel"] = primeiro_disponivel
            
            if primeiro_disponivel:
                debug_detalhado["logs_passos"].append(f"✅ Passo 7: Primeiro disponível na posição {primeiro_disponivel['posicao']}")
            else:
                debug_detalhado["logs_passos"].append("❌ Passo 7: Nenhum contato disponível encontrado")
                debug_detalhado["problemas_identificados"].append("Todos os contatos já foram discados")
            
            # Análise final
            if len(contatos_validos) == 0:
                debug_detalhado["problemas_identificados"].append("PROBLEMA: Nenhum contato válido encontrado")
            elif primeiro_disponivel is None:
                debug_detalhado["problemas_identificados"].append("PROBLEMA: Todos os contatos já foram discados")
            else:
                debug_detalhado["logs_passos"].append("🎯 SUCESSO: Contato disponível encontrado!")
            
            return debug_detalhado
            
        except Exception as e:
            debug_detalhado["problemas_identificados"].append(f"ERRO GERAL: {str(e)}")
            return debug_detalhado

    async def resetar_llamadas_campana(self, campana_id: int) -> Dict[str, Any]:
        """
        Reseta/limpa todas as llamadas de uma campanha presione1.
        
        Args:
            campana_id: ID da campanha presione1
            
        Returns:
            Resultado da operação
        """
        logger.info(f"🗑️ Resetando llamadas da campanha {campana_id}")
        
        # Verificar se a campanha existe
        campana = self.obter_campana(campana_id)
        
        if campana.get("activa"):
            raise HTTPException(
                status_code=400,
                detail="Não é possível resetar llamadas de uma campanha ativa. Pare a campanha primeiro."
            )
        
        try:
            # Buscar llamadas existentes
            llamadas_existentes = self._supabase_request(
                "GET",
                "llamadas_presione1", 
                filters={"campana_id": campana_id},
                select="id"
            )
            
            total_llamadas = len(llamadas_existentes) if llamadas_existentes else 0
            logger.info(f"📊 Encontradas {total_llamadas} llamadas para deletar")
            
            if total_llamadas > 0:
                # Deletar todas as llamadas desta campanha
                self._supabase_request(
                    "DELETE",
                    "llamadas_presione1",
                    filters={"campana_id": campana_id}
                )
                
                logger.info(f"✅ {total_llamadas} llamadas deletadas da campanha {campana_id}")
            else:
                logger.info(f"✅ Nenhuma llamada encontrada para campanha {campana_id}")
            
            return {
                "mensaje": f"Llamadas da campanha resetadas com sucesso",
                "campana_id": campana_id,
                "llamadas_deletadas": total_llamadas,
                "status": "sucesso"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao resetar llamadas da campanha {campana_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao resetar llamadas: {str(e)}"
            )

    async def investigar_llamadas_detalhado(self, campana_id: int) -> Dict[str, Any]:
        """
        Investigação detalhada das llamadas para debug do problema.
        """
        investigacao = {
            "campana_id": campana_id,
            "timestamp": datetime.utcnow().isoformat(),
            "llamadas_todas": {
                "total": 0,
                "amostra": [],
                "estados": {}
            },
            "llamadas_sem_error": {
                "total": 0,
                "numeros_unicos": 0,
                "numeros_set": []
            },
            "contatos_campanha": {
                "total": 0,
                "primeiros_5": []
            },
            "comparacao_metodos": {
                "debug_campana_conta": None,
                "obter_proximo_numero_ve": None
            }
        }
        
        try:
            # Verificar campanha
            campana = self.obter_campana(campana_id)
            campaign_id = campana.get("campaign_id")
            
            # 1. TODAS as llamadas
            logger.info(f"🔍 Investigando TODAS as llamadas para campana_id {campana_id}")
            
            llamadas_todas = self._supabase_request(
                "GET",
                "llamadas_presione1",
                filters={"campana_id": campana_id},
                select="*"
            )
            
            investigacao["llamadas_todas"]["total"] = len(llamadas_todas) if llamadas_todas else 0
            
            if llamadas_todas:
                # Amostra dos primeiros 5
                investigacao["llamadas_todas"]["amostra"] = llamadas_todas[:5]
                
                # Contar por estado
                estados = {}
                for llamada in llamadas_todas:
                    estado = llamada.get("estado", "unknown")
                    estados[estado] = estados.get(estado, 0) + 1
                
                investigacao["llamadas_todas"]["estados"] = estados
            
            # 2. Llamadas SEM error (como fazia antes)
            logger.info(f"🔍 Investigando llamadas SEM error")
            
            llamadas_sem_error = self._supabase_request(
                "GET",
                "llamadas_presione1",
                filters={
                    "campana_id": campana_id,
                    "estado": "not.eq.error"
                },
                select="numero_normalizado,estado"
            )
            
            investigacao["llamadas_sem_error"]["total"] = len(llamadas_sem_error) if llamadas_sem_error else 0
            
            if llamadas_sem_error:
                # Números únicos normalizados
                numeros_unicos = set()
                for llamada in llamadas_sem_error:
                    numero = llamada.get("numero_normalizado")
                    if numero:
                        numeros_unicos.add(numero)
                
                investigacao["llamadas_sem_error"]["numeros_unicos"] = len(numeros_unicos)
                investigacao["llamadas_sem_error"]["numeros_set"] = list(numeros_unicos)[:10]  # Primeiros 10
            
            # 3. Contatos da campanha
            logger.info(f"🔍 Investigando contatos da campanha principal {campaign_id}")
            
            contatos = self._supabase_request(
                "GET",
                "contacts",
                filters={"campaign_id": campaign_id},
                select="id,phone_number,name"
            )
            
            investigacao["contatos_campanha"]["total"] = len(contatos) if contatos else 0
            
            if contatos:
                investigacao["contatos_campanha"]["primeiros_5"] = contatos[:5]
            
            # 4. Comparação de métodos
            # Simular debug_campana (conta apenas llamadas existentes)
            llamadas_debug = self._supabase_request(
                "GET",
                "llamadas_presione1",
                filters={"campana_id": campana_id},
                select="id"
            )
            investigacao["comparacao_metodos"]["debug_campana_conta"] = len(llamadas_debug) if llamadas_debug else 0
            
            # Simular obter_proximo_numero (usa filtro not.eq.error)
            llamadas_sem_error_check = self._supabase_request(
                "GET",
                "llamadas_presione1",
                filters={
                    "campana_id": campana_id,
                    "estado": "not.eq.error"
                },
                select="numero_normalizado"
            )
            
            numeros_discados_metodo_antigo = set()
            if llamadas_sem_error_check:
                for llamada in llamadas_sem_error_check:
                    numero = llamada.get("numero_normalizado")
                    if numero:
                        numeros_discados_metodo_antigo.add(numero)
            
            investigacao["comparacao_metodos"]["obter_proximo_numero_ve"] = len(numeros_discados_metodo_antigo)
            
            return investigacao
            
        except Exception as e:
            logger.error(f"❌ Erro durante investigação: {str(e)}")
            investigacao["erro"] = str(e)
            return investigacao