# Sistema de Áudio Inteligente

## Visão Geral

O **Sistema de Áudio Inteligente** é uma extensão avançada do discador preditivo que permite controle dinâmico e inteligente da reprodução de áudio durante as chamadas. O sistema utiliza uma máquina de estados combinada com um motor de regras configurável para determinar qual áudio reproduzir baseado no contexto atual da chamada.

## Características Principais

### ✅ Sistema de Contexto de Áudio
- Controla o que será reproduzido de acordo com o estado atual da chamada
- Flexível para múltiplos tipos de estados (espera, atendido, tecla pressionada, erro, etc.)
- Configurações específicas por contexto (timeout, detecção de voicemail, etc.)

### ✅ Motor de Regras para Reprodução Dinâmica
- Permite campanhas com regras configuráveis
- Considera horário, DTMF, tempo, status da chamada, etc.
- Sistema de prioridades para resolução de conflitos

### ✅ Máquina de Estados de Áudio
- Gerencia estados possíveis: "tocando", "aguardando DTMF", "erro", "conectado", etc.
- Transições validadas e auditadas
- Eventos que disparam mudanças de estado

### ✅ Sincronização com Estados da Chamada
- Reage aos eventos reais da chamada (cliente atendeu, apertou tecla, etc.)
- Integração com Asterisk via AMI
- Atualização automática dos estados das chamadas

## Arquitetura do Sistema

### Componentes Principais

1. **AudioStateMachine**: Máquina de estados que gerencia transições
2. **AudioRulesEngine**: Motor de regras que avalia condições e aplica ações
3. **AudioIntelligentSystem**: Sistema principal que coordena os componentes
4. **AudioContextManager**: Gerenciador de contextos e templates
5. **AudioIntegrationService**: Serviço de integração com o sistema existente

### Modelos de Dados

#### AudioContexto
```python
- id: Identificador único
- nome: Nome do contexto
- timeout_dtmf_padrao: Timeout padrão para DTMF
- detectar_voicemail: Se deve detectar voicemail
- audio_principal_url: URL do áudio principal
- audio_voicemail_url: URL do áudio para voicemail
- configuracoes_avancadas: Configurações em JSON
```

#### AudioRegra
```python
- id: Identificador único
- contexto_id: Referência ao contexto
- estado_origem: Estado que dispara a regra
- evento_disparador: Evento que ativa a regra
- condicoes: Condições adicionais (JSON)
- estado_destino: Estado resultante
- audio_url: URL do áudio a reproduzir
- prioridade: Prioridade da regra
```

#### AudioSessao
```python
- id: Identificador único
- llamada_id: Referência à chamada
- contexto_id: Contexto utilizado
- estado_atual: Estado atual da máquina
- dados_contexto: Dados específicos da sessão
- timeout_dtmf: Timeout específico desta sessão
```

## Estados da Máquina

### Estados Disponíveis

1. **INICIANDO**: Estado inicial da chamada
2. **TOCANDO**: Telefone está tocando
3. **AGUARDANDO_DTMF**: Aguardando entrada DTMF do usuário
4. **DETECTANDO_VOICEMAIL**: Analisando se é voicemail
5. **REPRODUZINDO_VOICEMAIL**: Reproduzindo mensagem no voicemail
6. **AGUARDANDO_HUMANO**: Aguardando confirmação de humano
7. **CONECTADO**: Usuário conectado (pressionou tecla 1)
8. **TRANSFERINDO**: Transferindo chamada
9. **ERRO**: Estado de erro
10. **FINALIZADO**: Estado terminal

### Transições Válidas

```
INICIANDO → [TOCANDO, ERRO, FINALIZADO]
TOCANDO → [AGUARDANDO_DTMF, DETECTANDO_VOICEMAIL, AGUARDANDO_HUMANO, ERRO, FINALIZADO]
AGUARDANDO_DTMF → [CONECTADO, DETECTANDO_VOICEMAIL, AGUARDANDO_HUMANO, ERRO, FINALIZADO]
DETECTANDO_VOICEMAIL → [REPRODUZINDO_VOICEMAIL, AGUARDANDO_HUMANO, ERRO, FINALIZADO]
REPRODUZINDO_VOICEMAIL → [FINALIZADO, ERRO]
AGUARDANDO_HUMANO → [CONECTADO, DETECTANDO_VOICEMAIL, ERRO, FINALIZADO]
CONECTADO → [TRANSFERINDO, FINALIZADO, ERRO]
TRANSFERINDO → [FINALIZADO, ERRO]
ERRO → [FINALIZADO]
FINALIZADO → [] (terminal)
```

## Eventos do Sistema

### Tipos de Eventos

1. **CHAMADA_INICIADA**: Chamada foi iniciada
2. **TELEFONE_TOCANDO**: Telefone está tocando
3. **ATENDEU**: Chamada foi atendida
4. **VOICEMAIL_DETECTADO**: Voicemail foi detectado
5. **DTMF_DETECTADO**: Tecla DTMF foi pressionada
6. **TIMEOUT_DTMF**: Timeout aguardando DTMF
7. **HUMANO_CONFIRMADO**: Humano foi confirmado
8. **CHAMADA_FINALIZADA**: Chamada foi finalizada
9. **ERRO_SISTEMA**: Erro no sistema
10. **TRANSFERENCIA_SOLICITADA**: Transferência foi solicitada

## Motor de Regras

### Estrutura de uma Regra

```json
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
    ],
    "audio_url": "https://example.com/conectado.wav",
    "parametros_acao": {
        "timeout_dtmf": 15
    }
}
```

### Operadores Disponíveis

- **igual**: Valor igual
- **diferente**: Valor diferente
- **maior_que**: Valor maior que
- **menor_que**: Valor menor que
- **contem**: String contém valor
- **nao_contem**: String não contém valor
- **entre**: Valor entre dois números
- **existe**: Campo existe

### Campos Contextuais Automáticos

- `tempo_no_estado_atual`: Tempo em segundos no estado atual
- `tempo_total_sessao`: Tempo total da sessão em segundos
- `tentativas_realizadas`: Número de tentativas realizadas
- `estado_atual`: Estado atual da máquina
- `evento_atual`: Evento atual sendo processado

## API Endpoints

### Iniciar Chamada com Áudio Inteligente
```http
POST /api/v1/audio-inteligente/iniciar-chamada
Content-Type: application/json

{
    "numero_destino": "+5511999999999",
    "campana_id": 1,
    "contexto_audio": "Presione 1 Padrão",
    "cli": "+5511888888888",
    "configuracoes_audio": {
        "timeout_dtmf": 15,
        "detectar_voicemail": true
    }
}
```

### Processar Evento do Asterisk
```http
POST /api/v1/audio-inteligente/evento-asterisk
Content-Type: application/json

{
    "llamada_id": 123,
    "tipo_evento": "DTMF",
    "dados_evento": {
        "Digit": "1",
        "Channel": "SIP/123-00000001"
    }
}
```

### Obter Status da Chamada
```http
GET /api/v1/audio-inteligente/status-llamada/123
```

### Listar Contextos Disponíveis
```http
GET /api/v1/audio-inteligente/contextos
```

### Criar Novo Contexto
```http
POST /api/v1/audio-inteligente/criar-contexto
Content-Type: application/json

{
    "nome": "Meu Contexto",
    "descricao": "Contexto personalizado",
    "audio_principal_url": "https://example.com/audio.wav",
    "timeout_dtmf": 10,
    "detectar_voicemail": true,
    "audio_voicemail_url": "https://example.com/voicemail.wav"
}
```

## Templates Pré-configurados

### Template "Presione 1 Padrão"

Template otimizado para campanhas "Presione 1" com:
- Detecção automática de voicemail
- Timeout configurável para DTMF
- Regras para diferentes cenários (atendimento humano, voicemail, timeout)
- Transições automáticas baseadas em eventos

### Criando Contexto a partir de Template
```http
POST /api/v1/audio-inteligente/criar-contexto-template
Content-Type: application/json

{
    "template_id": 1,
    "nome_contexto": "Minha Campanha Presione 1",
    "audio_principal_url": "https://example.com/audio.wav",
    "audio_voicemail_url": "https://example.com/voicemail.wav",
    "configuracoes_personalizadas": {
        "timeout_dtmf_padrao": 15
    }
}
```

## Integração com Asterisk

### Mapeamento de Eventos

| Evento Asterisk | Evento Sistema | Descrição |
|----------------|----------------|-----------|
| Dial | TELEFONE_TOCANDO | Telefone está tocando |
| DialEnd | ATENDEU | Chamada foi atendida |
| DTMF | DTMF_DETECTADO | Tecla DTMF pressionada |
| DTMFTimeout | TIMEOUT_DTMF | Timeout aguardando DTMF |
| VoicemailDetected | VOICEMAIL_DETECTADO | Voicemail detectado |
| HumanDetected | HUMANO_CONFIRMADO | Humano confirmado |
| Hangup | CHAMADA_FINALIZADA | Chamada finalizada |
| Error | ERRO_SISTEMA | Erro no sistema |

### Variáveis do Asterisk

O sistema define as seguintes variáveis para o Asterisk:

- `LLAMADA_ID`: ID da chamada
- `AUDIO_SESSAO_ID`: ID da sessão de áudio
- `CONTEXTO_AUDIO`: Nome do contexto
- `AUDIO_PRINCIPAL_URL`: URL do áudio principal
- `TIMEOUT_DTMF`: Timeout para DTMF
- `DETECTAR_VOICEMAIL`: Se deve detectar voicemail
- `AUDIO_VOICEMAIL_URL`: URL do áudio para voicemail
- `SISTEMA_AUDIO_INTELIGENTE`: Flag indicando uso do sistema

## Configuração Inicial

### Setup Automático
```http
POST /api/v1/audio-inteligente/setup-inicial
```

Este endpoint:
1. Cria templates padrão
2. Configura contexto "Presione 1 Padrão"
3. Inicializa estruturas necessárias

### Demonstração
```http
POST /api/v1/audio-inteligente/teste-demo
```

Executa uma demonstração completa:
1. Configura sistema inicial
2. Inicia chamada de teste
3. Simula eventos (atendimento, DTMF)
4. Retorna status final

## Monitoramento e Auditoria

### Eventos Registrados

Todos os eventos são registrados na tabela `audio_eventos` com:
- Timestamp preciso
- Estado origem e destino
- Dados do evento
- Regra aplicada
- Status de sucesso/erro

### Métricas Disponíveis

- Tempo médio por estado
- Taxa de conversão por contexto
- Eficácia das regras
- Distribuição de eventos

## Casos de Uso

### 1. Campanha Presione 1 Básica
```python
# Criar contexto
contexto = context_manager.criar_contexto_presione1(
    nome="Campanha Produto X",
    audio_principal_url="https://cdn.empresa.com/produto_x.wav",
    audio_voicemail_url="https://cdn.empresa.com/produto_x_voicemail.wav"
)

# Iniciar chamada
resultado = await integration_service.iniciar_chamada_com_audio_inteligente(
    numero_destino="+5511999999999",
    campana_id=1,
    contexto_audio_nome="Campanha Produto X"
)
```

### 2. Campanha com Regras Personalizadas
```python
# Criar contexto básico
contexto = context_manager.criar_contexto_basico(
    nome="Pesquisa Satisfação",
    audio_principal_url="https://cdn.empresa.com/pesquisa.wav"
)

# Adicionar regras personalizadas
regra_horario = AudioRegra(
    contexto_id=contexto.id,
    nome="Horário Comercial",
    estado_origem=EstadoAudio.INICIANDO,
    estado_destino=EstadoAudio.TOCANDO,
    condicoes=[
        {
            "campo": "hora_atual",
            "operador": "entre",
            "valor": [9, 18]
        }
    ]
)
```

### 3. Integração com Sistema Existente
```python
# Processar evento do Asterisk
resultado = integration_service.processar_evento_asterisk(
    llamada_id=123,
    tipo_evento="DTMF",
    dados_evento={"Digit": "1"}
)

# Verificar se houve mudança de estado
if resultado.get("sucesso"):
    novo_estado = resultado.get("novo_estado")
    print(f"Estado alterado para: {novo_estado}")
```

## Considerações de Performance

### Otimizações Implementadas

1. **Índices de Banco**: Índices otimizados para consultas frequentes
2. **Cache de Regras**: Regras carregadas em memória por contexto
3. **Processamento Assíncrono**: Eventos processados de forma assíncrona
4. **Validação de Transições**: Validação rápida de transições válidas

### Recomendações

- Manter número de regras por contexto abaixo de 50
- Usar prioridades para otimizar ordem de avaliação
- Monitorar performance das consultas de regras
- Implementar cache para contextos frequentemente usados

## Troubleshooting

### Problemas Comuns

1. **Regra não aplicada**: Verificar condições e prioridades
2. **Transição inválida**: Verificar estados origem/destino válidos
3. **Evento não processado**: Verificar mapeamento de eventos do Asterisk
4. **Timeout de DTMF**: Ajustar configurações de timeout

### Logs e Debugging

O sistema registra logs detalhados em:
- Aplicação de regras
- Mudanças de estado
- Processamento de eventos
- Erros de validação

### Monitoramento

Endpoints para monitoramento:
- Status de sessões ativas
- Estatísticas de contextos
- Performance de regras
- Eventos recentes

## Roadmap Futuro

### Funcionalidades Planejadas

1. **Editor Visual**: Interface gráfica para criar regras
2. **Machine Learning**: Otimização automática de regras
3. **A/B Testing**: Testes de diferentes contextos
4. **Analytics Avançado**: Dashboards de performance
5. **Integração CRM**: Sincronização com sistemas CRM
6. **Multi-idioma**: Suporte a múltiplos idiomas
7. **Síntese de Voz**: Geração dinâmica de áudio

### Melhorias Técnicas

1. **Cache Distribuído**: Redis para cache de regras
2. **Processamento em Lote**: Otimização para alto volume
3. **Webhooks**: Notificações em tempo real
4. **API GraphQL**: API mais flexível
5. **Microserviços**: Separação em serviços independentes

---

## Conclusão

O Sistema de Áudio Inteligente representa uma evolução significativa do discador preditivo, oferecendo controle granular e inteligente sobre a reprodução de áudio durante as chamadas. Com sua arquitetura modular e extensível, o sistema pode ser facilmente adaptado para diferentes tipos de campanhas e necessidades específicas.

A combinação de máquina de estados, motor de regras e integração com Asterisk proporciona uma solução robusta e flexível para campanhas de telemarketing modernas, permitindo maior personalização e eficácia nas comunicações com clientes. 