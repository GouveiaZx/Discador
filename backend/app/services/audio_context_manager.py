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
    Gerenciador de contextos de audio e templates pre-configurados.
    Facilita a criacao e gestao de configuracoes de audio.
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
        Cria um contexto basico de audio.
        
        Args:
            nome: Nome do contexto
            descricao: Descricao do contexto
            audio_principal_url: URL do audio principal
            timeout_dtmf: Timeout para DTMF em segundos
            detectar_voicemail: Se deve detectar voicemail
            audio_voicemail_url: URL do audio para voicemail
            
        Returns:
            AudioContexto: Contexto criado
        """
        try:
            # Verificar se ja existe contexto com esse nome
            contexto_existente = self.db.query(AudioContexto).filter(
                AudioContexto.nome == nome
            ).first()
            
            if contexto_existente:
                raise ValueError(f"Ja existe um contexto com o nome '{nome}'")
            
            # Criar novo contexto
            novo_contexto = AudioContexto(
                nome=nome,
                descricao=descricao,
                configuracoes={
                    "timeout_dtmf_padrao": timeout_dtmf,
                    "detectar_voicemail": detectar_voicemail,
                    "audio_principal_url": audio_principal_url,
                    "audio_voicemail_url": audio_voicemail_url
                }
            )
            
            self.db.add(novo_contexto)
            self.db.commit()
            self.db.refresh(novo_contexto)
            
            logger.info(f"Contexto basico criado: {nome} (ID: {novo_contexto.id})")
            return novo_contexto
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar contexto basico: {str(e)}")
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
        Cria um contexto pre-configurado para campanhas "Presione 1".
        
        Args:
            nome: Nome do contexto
            audio_principal_url: URL do audio principal
            audio_voicemail_url: URL do audio para voicemail
            timeout_dtmf: Timeout para aguardar DTMF
            detectar_voicemail: Se deve detectar voicemail
            tentativas_maximas: Numero maximo de tentativas
            
        Returns:
            AudioContexto: Contexto criado com regras pre-configuradas
        """
        try:
            # Criar contexto base
            contexto = self.criar_contexto_basico(
                nome=nome,
                descricao="Contexto para campanhas Presione 1 com deteccao de voicemail",
                audio_principal_url=audio_principal_url,
                timeout_dtmf=timeout_dtmf,
                detectar_voicemail=detectar_voicemail,
                audio_voicemail_url=audio_voicemail_url
            )
            
            # Adicionar configuração de tentativas máximas
            contexto.configuracoes["tentativas_maximas"] = tentativas_maximas
            
            # Criar regras pre-configuradas para Presione 1
            regras_presione1 = [
                # Regra 1: Iniciar -> Tocando
                {
                    "nome": "Iniciar Chamada",
                    "descricao": "Transicao inicial quando a chamada e iniciada",
                    "prioridade": 100,
                    "estado_origem": EstadoAudio.INICIANDO,
                    "evento_disparador": TipoEvento.CHAMADA_INICIADA,
                    "estado_destino": EstadoAudio.TOCANDO,
                    "condicoes": None
                },
                
                # Regra 2: Tocando -> Aguardando DTMF (quando atendeu)
                {
                    "nome": "Atendimento Detectado",
                    "descricao": "Quando a chamada e atendida, aguardar DTMF",
                    "prioridade": 90,
                    "estado_origem": EstadoAudio.TOCANDO,
                    "evento_disparador": TipoEvento.CONEXAO_ESTABELECIDA,
                    "estado_destino": EstadoAudio.AGUARDANDO_DTMF,
                    "condicoes": None
                },
                
                # Regra 3: Aguardando DTMF -> Conectado (tecla 1 pressionada)
                {
                    "nome": "Tecla 1 Pressionada",
                    "descricao": "Cliente pressionou tecla 1, conectar",
                    "prioridade": 95,
                    "estado_origem": EstadoAudio.AGUARDANDO_DTMF,
                    "evento_disparador": TipoEvento.DTMF_RECEBIDO,
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
                    "descricao": "Timeout aguardando DTMF, verificar se e voicemail",
                    "prioridade": 80,
                    "estado_origem": EstadoAudio.AGUARDANDO_DTMF,
                    "evento_disparador": TipoEvento.TIMEOUT_ATINGIDO,
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
                
                # Regra 6: Humano confirmado apos deteccao de voicemail
                {
                    "nome": "Humano Apos Voicemail",
                    "descricao": "Humano detectado apos analise de voicemail",
                    "prioridade": 75,
                    "estado_origem": EstadoAudio.DETECTANDO_VOICEMAIL,
                    "evento_disparador": TipoEvento.HUMANO_DETECTADO,
                    "estado_destino": EstadoAudio.AGUARDANDO_DTMF,
                    "condicoes": None
                },
                
                # Regra 7: Finalizar apos reproduzir voicemail
                {
                    "nome": "Finalizar Voicemail",
                    "descricao": "Finalizar chamada apos reproduzir mensagem no voicemail",
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
                }
            ]
            
            # Criar regras no banco de dados
            for regra_config in regras_presione1:
                regra = AudioRegra(
                    contexto_id=contexto.id,
                    nome=regra_config["nome"],
                    descricao=regra_config["descricao"],
                    ordem=regra_config["prioridade"],
                    condicoes=regra_config.get("condicoes", []),
                    acoes=[
                        {
                            "tipo": "alterar_estado",
                            "estado_destino": regra_config["estado_destino"].value
                        }
                    ],
                    configuracoes={
                        "estado_origem": regra_config["estado_origem"].value,
                        "evento_disparador": regra_config.get("evento_disparador", {}).value if regra_config.get("evento_disparador") else None,
                        "audio_url": regra_config.get("audio_url")
                    }
                )
                self.db.add(regra)
            
            self.db.commit()
            
            logger.info(f"Contexto Presione 1 criado: {nome} (ID: {contexto.id})")
            return contexto
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar contexto Presione 1: {str(e)}")
            raise
    
    def criar_template_presione1(self) -> AudioTemplate:
        """
        Cria um template para audioss de campanha "Presione 1".
        
        Returns:
            AudioTemplate: Template criado
        """
        try:
            template = AudioTemplate(
                nome="Presione 1 - Padrão",
                descricao="Template padrão para campanhas Presione 1",
                texto_tts="Você tem uma oportunidade especial esperando. Pressione 1 para falar com um consultor ou pressione 2 para não receber mais ligações.",
                idioma="pt-BR",
                voz="pt-BR-Neural2-A",
                volume=1.0,
                velocidade=1.0,
                aguardar_dtmf=True,
                timeout_dtmf=10,
                max_repeticoes=2
            )
            
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            
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
        Cria um contexto a partir de um template existente.
        
        Args:
            template_id: ID do template
            nome_contexto: Nome do novo contexto
            audio_principal_url: URL do audio principal
            audio_voicemail_url: URL do audio para voicemail
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
                raise ValueError(f"Template com ID {template_id} não encontrado")
            
            # Configurações padrão baseadas no template
            configuracoes = {
                "audio_principal_url": audio_principal_url,
                "audio_voicemail_url": audio_voicemail_url,
                "timeout_dtmf": template.timeout_dtmf,
                "max_repeticoes": template.max_repeticoes,
                "template_id": template_id,
                "aguardar_dtmf": template.aguardar_dtmf,
                "volume": template.volume,
                "velocidade": template.velocidade,
                "idioma": template.idioma,
                "voz": template.voz
            }
            
            # Aplicar configurações personalizadas
            if configuracoes_personalizadas:
                configuracoes.update(configuracoes_personalizadas)
            
            # Criar contexto
            contexto = AudioContexto(
                nome=nome_contexto,
                descricao=f"Contexto criado a partir do template: {template.nome}",
                configuracoes=configuracoes
            )
            
            self.db.add(contexto)
            self.db.commit()
            self.db.refresh(contexto)
            
            logger.info(f"Contexto criado a partir do template: {nome_contexto} (ID: {contexto.id})")
            return contexto
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar contexto a partir do template: {str(e)}")
            raise
    
    def listar_contextos(self, ativo_apenas: bool = True) -> List[AudioContexto]:
        """
        Lista todos os contextos de audio disponíveis.
        
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
        Lista todos os templates de audio disponíveis.
        
        Args:
            categoria: Categoria específica para filtrar
            
        Returns:
            List[AudioTemplate]: Lista de templates
        """
        query = self.db.query(AudioTemplate)
        
        if categoria:
            query = query.filter(AudioTemplate.categoria == categoria)
        
        return query.order_by(AudioTemplate.nome).all()
    
    def obter_contexto_por_nome(self, nome: str) -> Optional[AudioContexto]:
        """
        Busca um contexto pelo nome.
        
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
        Inicializa templates padrão do sistema.
        
        Returns:
            Dict[str, AudioTemplate]: Templates criados
        """
        templates = {}
        
        try:
            # Template Presione 1
            presione1_template = self.criar_template_presione1()
            templates["presione1"] = presione1_template
            
            logger.info("Templates padrão inicializados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar templates padrão: {str(e)}")
        
        return templates 