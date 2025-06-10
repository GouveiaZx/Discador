from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.models.audio_sistema import (
    AudioContexto, AudioRegra, AudioTemplate,
    EstadoAudio, TipoEvento
)

logger = logging.getLogger(__name__)

class AudioContextManager:
    """
    Gerenciador de contextos de áudio e templates pré-configurados.
    Facilita a criação e gestão de configurações de áudio.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def criar_contexto_basico(
        self,
        nome: str,
        descricao: str,
        audio_principal_url: str,
        timeout_dtmf: int = 10,
        detectar_voicemail: bool = True,
        audio_voicemail_url: Optional[str] = None
    ) -> AudioContexto:
        """
        Cria um contexto básico de áudio.
        
        Args:
            nome: Nome do contexto
            descricao: Descrição do contexto
            audio_principal_url: URL do áudio principal
            timeout_dtmf: Timeout para DTMF em segundos
            detectar_voicemail: Se deve detectar voicemail
            audio_voicemail_url: URL do áudio para voicemail
            
        Returns:
            AudioContexto: Contexto criado
        """
        try:
            # Verificar se já existe contexto com esse nome
            contexto_existente = self.db.query(AudioContexto).filter(
                AudioContexto.nome == nome
            ).first()
            
            if contexto_existente:
                raise ValueError(f"Já existe um contexto com o nome '{nome}'")
            
            # Criar novo contexto
            novo_contexto = AudioContexto(
                nome=nome,
                descricao=descricao,
                timeout_dtmf_padrao=timeout_dtmf,
                detectar_voicemail=detectar_voicemail,
                audio_principal_url=audio_principal_url,
                audio_voicemail_url=audio_voicemail_url
            )
            
            self.db.add(novo_contexto)
            self.db.commit()
            self.db.refresh(novo_contexto)
            
            logger.info(f"Contexto básico criado: {nome} (ID: {novo_contexto.id})")
            return novo_contexto
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar contexto básico: {str(e)}")
            raise
    
    def criar_contexto_presione1(
        self,
        nome: str,
        audio_principal_url: str,
        audio_voicemail_url: str,
        timeout_dtmf: int = 10,
        detectar_voicemail: bool = True,
        tentativas_maximas: int = 3
    ) -> AudioContexto:
        """
        Cria um contexto pré-configurado para campanhas "Presione 1".
        
        Args:
            nome: Nome do contexto
            audio_principal_url: URL do áudio principal
            audio_voicemail_url: URL do áudio para voicemail
            timeout_dtmf: Timeout para aguardar DTMF
            detectar_voicemail: Se deve detectar voicemail
            tentativas_maximas: Número máximo de tentativas
            
        Returns:
            AudioContexto: Contexto criado com regras pré-configuradas
        """
        try:
            # Criar contexto base
            contexto = self.criar_contexto_basico(
                nome=nome,
                descricao="Contexto para campanhas Presione 1 com detecção de voicemail",
                audio_principal_url=audio_principal_url,
                timeout_dtmf=timeout_dtmf,
                detectar_voicemail=detectar_voicemail,
                audio_voicemail_url=audio_voicemail_url
            )
            
            contexto.tentativas_maximas = tentativas_maximas
            
            # Criar regras pré-configuradas para Presione 1
            regras_presione1 = [
                # Regra 1: Iniciar -> Tocando
                {
                    "nome": "Iniciar Chamada",
                    "descricao": "Transição inicial quando a chamada é iniciada",
                    "prioridade": 100,
                    "estado_origem": EstadoAudio.INICIANDO,
                    "evento_disparador": TipoEvento.CHAMADA_INICIADA,
                    "estado_destino": EstadoAudio.TOCANDO,
                    "condicoes": None
                },
                
                # Regra 2: Tocando -> Aguardando DTMF (quando atendeu)
                {
                    "nome": "Atendimento Detectado",
                    "descricao": "Quando a chamada é atendida, aguardar DTMF",
                    "prioridade": 90,
                    "estado_origem": EstadoAudio.TOCANDO,
                    "evento_disparador": TipoEvento.ATENDEU,
                    "estado_destino": EstadoAudio.AGUARDANDO_DTMF,
                    "condicoes": None
                },
                
                # Regra 3: Aguardando DTMF -> Conectado (tecla 1 pressionada)
                {
                    "nome": "Tecla 1 Pressionada",
                    "descricao": "Cliente pressionou tecla 1, conectar",
                    "prioridade": 95,
                    "estado_origem": EstadoAudio.AGUARDANDO_DTMF,
                    "evento_disparador": TipoEvento.DTMF_DETECTADO,
                    "estado_destino": EstadoAudio.CONECTADO,
                    "condicoes": [
                        {
                            "campo": "dtmf_tecla",
                            "operador": "igual",
                            "valor": "1"
                        }
                    ]
                },
                
                # Regra 4: Timeout DTMF -> Detectando Voicemail
                {
                    "nome": "Timeout DTMF",
                    "descricao": "Timeout aguardando DTMF, verificar se é voicemail",
                    "prioridade": 80,
                    "estado_origem": EstadoAudio.AGUARDANDO_DTMF,
                    "evento_disparador": TipoEvento.TIMEOUT_DTMF,
                    "estado_destino": EstadoAudio.DETECTANDO_VOICEMAIL,
                    "condicoes": None
                },
                
                # Regra 5: Voicemail detectado -> Reproduzir mensagem
                {
                    "nome": "Voicemail Detectado",
                    "descricao": "Voicemail detectado, reproduzir mensagem",
                    "prioridade": 85,
                    "estado_origem": EstadoAudio.DETECTANDO_VOICEMAIL,
                    "evento_disparador": TipoEvento.VOICEMAIL_DETECTADO,
                    "estado_destino": EstadoAudio.REPRODUZINDO_VOICEMAIL,
                    "audio_url": audio_voicemail_url,
                    "condicoes": None
                },
                
                # Regra 6: Humano confirmado após detecção de voicemail
                {
                    "nome": "Humano Após Voicemail",
                    "descricao": "Humano detectado após análise de voicemail",
                    "prioridade": 75,
                    "estado_origem": EstadoAudio.DETECTANDO_VOICEMAIL,
                    "evento_disparador": TipoEvento.HUMANO_CONFIRMADO,
                    "estado_destino": EstadoAudio.AGUARDANDO_DTMF,
                    "condicoes": None
                },
                
                # Regra 7: Finalizar após reproduzir voicemail
                {
                    "nome": "Finalizar Voicemail",
                    "descricao": "Finalizar chamada após reproduzir mensagem no voicemail",
                    "prioridade": 70,
                    "estado_origem": EstadoAudio.REPRODUZINDO_VOICEMAIL,
                    "evento_disparador": None,
                    "estado_destino": EstadoAudio.FINALIZADO,
                    "condicoes": [
                        {
                            "campo": "tempo_no_estado_atual",
                            "operador": "maior_que",
                            "valor": 30  # 30 segundos reproduzindo
                        }
                    ]
                },
                
                # Regra 8: Finalizar por timeout geral
                {
                    "nome": "Timeout Geral",
                    "descricao": "Finalizar por timeout geral da chamada",
                    "prioridade": 60,
                    "estado_origem": EstadoAudio.TOCANDO,
                    "evento_disparador": None,
                    "estado_destino": EstadoAudio.FINALIZADO,
                    "condicoes": [
                        {
                            "campo": "tempo_total_sessao",
                            "operador": "maior_que",
                            "valor": 60  # 60 segundos no total
                        }
                    ]
                }
            ]
            
            # Criar as regras no banco
            for regra_config in regras_presione1:
                regra = AudioRegra(
                    contexto_id=contexto.id,
                    nome=regra_config["nome"],
                    descricao=regra_config["descricao"],
                    prioridade=regra_config["prioridade"],
                    estado_origem=regra_config["estado_origem"],
                    evento_disparador=regra_config.get("evento_disparador"),
                    estado_destino=regra_config["estado_destino"],
                    audio_url=regra_config.get("audio_url"),
                    condicoes=regra_config.get("condicoes")
                )
                self.db.add(regra)
            
            self.db.commit()
            
            logger.info(f"Contexto Presione 1 criado: {nome} com {len(regras_presione1)} regras")
            return contexto
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar contexto Presione 1: {str(e)}")
            raise
    
    def criar_template_presione1(self) -> AudioTemplate:
        """
        Cria um template pré-configurado para campanhas "Presione 1".
        
        Returns:
            AudioTemplate: Template criado
        """
        try:
            # Verificar se já existe
            template_existente = self.db.query(AudioTemplate).filter(
                AudioTemplate.nome == "Presione 1 Padrão"
            ).first()
            
            if template_existente:
                logger.info("Template Presione 1 já existe")
                return template_existente
            
            # Configuração do contexto
            configuracao_contexto = {
                "timeout_dtmf_padrao": 10,
                "detectar_voicemail": True,
                "duracao_maxima_voicemail": 30,
                "tentativas_maximas": 3
            }
            
            # Regras do template
            regras_template = [
                {
                    "nome": "Iniciar Chamada",
                    "descricao": "Transição inicial quando a chamada é iniciada",
                    "prioridade": 100,
                    "estado_origem": "iniciando",
                    "evento_disparador": "chamada_iniciada",
                    "estado_destino": "tocando"
                },
                {
                    "nome": "Atendimento Detectado",
                    "descricao": "Quando a chamada é atendida, aguardar DTMF",
                    "prioridade": 90,
                    "estado_origem": "tocando",
                    "evento_disparador": "atendeu",
                    "estado_destino": "aguardando_dtmf"
                },
                {
                    "nome": "Tecla 1 Pressionada",
                    "descricao": "Cliente pressionou tecla 1, conectar",
                    "prioridade": 95,
                    "estado_origem": "aguardando_dtmf",
                    "evento_disparador": "dtmf_detectado",
                    "estado_destino": "conectado",
                    "condicoes": [
                        {
                            "campo": "dtmf_tecla",
                            "operador": "igual",
                            "valor": "1"
                        }
                    ]
                },
                {
                    "nome": "Timeout DTMF",
                    "descricao": "Timeout aguardando DTMF, verificar se é voicemail",
                    "prioridade": 80,
                    "estado_origem": "aguardando_dtmf",
                    "evento_disparador": "timeout_dtmf",
                    "estado_destino": "detectando_voicemail"
                },
                {
                    "nome": "Voicemail Detectado",
                    "descricao": "Voicemail detectado, reproduzir mensagem",
                    "prioridade": 85,
                    "estado_origem": "detectando_voicemail",
                    "evento_disparador": "voicemail_detectado",
                    "estado_destino": "reproduzindo_voicemail"
                },
                {
                    "nome": "Humano Após Voicemail",
                    "descricao": "Humano detectado após análise de voicemail",
                    "prioridade": 75,
                    "estado_origem": "detectando_voicemail",
                    "evento_disparador": "humano_confirmado",
                    "estado_destino": "aguardando_dtmf"
                }
            ]
            
            # Criar template
            template = AudioTemplate(
                nome="Presione 1 Padrão",
                descricao="Template padrão para campanhas Presione 1 com detecção de voicemail",
                categoria="presione1",
                configuracao_contexto=configuracao_contexto,
                regras_template=regras_template
            )
            
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            
            logger.info(f"Template Presione 1 criado (ID: {template.id})")
            return template
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar template Presione 1: {str(e)}")
            raise
    
    def criar_contexto_a_partir_template(
        self,
        template_id: int,
        nome_contexto: str,
        audio_principal_url: str,
        audio_voicemail_url: Optional[str] = None,
        configuracoes_personalizadas: Optional[Dict[str, Any]] = None
    ) -> AudioContexto:
        """
        Cria um contexto baseado em um template existente.
        
        Args:
            template_id: ID do template
            nome_contexto: Nome do novo contexto
            audio_principal_url: URL do áudio principal
            audio_voicemail_url: URL do áudio para voicemail
            configuracoes_personalizadas: Configurações específicas
            
        Returns:
            AudioContexto: Contexto criado
        """
        try:
            # Buscar template
            template = self.db.query(AudioTemplate).filter(
                AudioTemplate.id == template_id
            ).first()
            
            if not template:
                raise ValueError(f"Template {template_id} não encontrado")
            
            # Mesclar configurações
            config_final = template.configuracao_contexto.copy()
            if configuracoes_personalizadas:
                config_final.update(configuracoes_personalizadas)
            
            # Criar contexto
            contexto = AudioContexto(
                nome=nome_contexto,
                descricao=f"Contexto baseado no template '{template.nome}'",
                timeout_dtmf_padrao=config_final.get("timeout_dtmf_padrao", 10),
                detectar_voicemail=config_final.get("detectar_voicemail", True),
                duracao_maxima_voicemail=config_final.get("duracao_maxima_voicemail", 30),
                tentativas_maximas=config_final.get("tentativas_maximas", 3),
                audio_principal_url=audio_principal_url,
                audio_voicemail_url=audio_voicemail_url,
                configuracoes_avancadas=config_final
            )
            
            self.db.add(contexto)
            self.db.commit()
            self.db.refresh(contexto)
            
            # Criar regras baseadas no template
            for regra_template in template.regras_template:
                regra = AudioRegra(
                    contexto_id=contexto.id,
                    nome=regra_template.get("nome"),
                    descricao=regra_template.get("descricao"),
                    prioridade=regra_template.get("prioridade", 0),
                    estado_origem=EstadoAudio(regra_template.get("estado_origem")),
                    evento_disparador=TipoEvento(regra_template.get("evento_disparador")) if regra_template.get("evento_disparador") else None,
                    estado_destino=EstadoAudio(regra_template.get("estado_destino")),
                    audio_url=regra_template.get("audio_url"),
                    condicoes=regra_template.get("condicoes"),
                    parametros_acao=regra_template.get("parametros_acao")
                )
                self.db.add(regra)
            
            self.db.commit()
            
            logger.info(f"Contexto criado a partir do template: {nome_contexto}")
            return contexto
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar contexto a partir do template: {str(e)}")
            raise
    
    def listar_contextos(self, ativo_apenas: bool = True) -> List[AudioContexto]:
        """
        Lista todos os contextos de áudio.
        
        Args:
            ativo_apenas: Se deve listar apenas contextos ativos
            
        Returns:
            List[AudioContexto]: Lista de contextos
        """
        query = self.db.query(AudioContexto)
        
        if ativo_apenas:
            query = query.filter(AudioContexto.ativo == True)
        
        return query.order_by(AudioContexto.nome).all()
    
    def listar_templates(self, categoria: Optional[str] = None) -> List[AudioTemplate]:
        """
        Lista todos os templates disponíveis.
        
        Args:
            categoria: Filtrar por categoria específica
            
        Returns:
            List[AudioTemplate]: Lista de templates
        """
        query = self.db.query(AudioTemplate).filter(AudioTemplate.ativo == True)
        
        if categoria:
            query = query.filter(AudioTemplate.categoria == categoria)
        
        return query.order_by(AudioTemplate.categoria, AudioTemplate.nome).all()
    
    def obter_contexto_por_nome(self, nome: str) -> Optional[AudioContexto]:
        """
        Obtém um contexto pelo nome.
        
        Args:
            nome: Nome do contexto
            
        Returns:
            AudioContexto: Contexto encontrado ou None
        """
        return self.db.query(AudioContexto).filter(
            AudioContexto.nome == nome,
            AudioContexto.ativo == True
        ).first()
    
    def inicializar_templates_padrao(self) -> Dict[str, AudioTemplate]:
        """
        Inicializa os templates padrão do sistema.
        
        Returns:
            Dict: Templates criados
        """
        templates_criados = {}
        
        try:
            # Template Presione 1
            template_presione1 = self.criar_template_presione1()
            templates_criados["presione1"] = template_presione1
            
            logger.info(f"Templates padrão inicializados: {list(templates_criados.keys())}")
            return templates_criados
            
        except Exception as e:
            logger.error(f"Erro ao inicializar templates padrão: {str(e)}")
            raise 