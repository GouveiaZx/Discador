# Sistema de Discado Preditivo "Presione 1"

## Visão Geral

O sistema de discado preditivo "Presione 1" é uma funcionalidade avançada do discador que permite campanhas automatizadas onde:

1. **Sistema liga automaticamente** para números de uma lista
2. **Reproduz mensagem de áudio** quando a chamada é atendida
3. **Aguarda usuário pressionar tecla 1** para demonstrar interesse
4. **Transfere automaticamente** para agente/fila se pressionou 1
5. **Encerra chamada** se não pressionou ou pressionou outra tecla

## Fluxo de Funcionamento

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ligar para    │───▶│    Atendida?    │───▶│  Reproduzir     │
│ próximo número  │    │                 │    │     áudio       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   Não atendida  │    │ Aguardar DTMF   │
         │              │   (finalizar)   │    │   (timeout)     │
         │              └─────────────────┘    └─────────────────┘
         │                                              │
         │              ┌─────────────────┐            ▼
         │              │ Pressionou 1?   │◄───────────────────
         │              └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │──────────────│ Sim: Transferir │    │ Não: Finalizar  │
                        │   para agente   │    │    chamada      │
                        └─────────────────┘    └─────────────────┘
```

## Componentes Principais

### 1. Campanhas Presione 1

**Características**:
- Nome e descrição da campanha
- Lista de números para discar
- URL do arquivo de áudio a reproduzir
- Timeout para aguardar DTMF (3-60 segundos)
- Configuração de transferência (extensão ou fila)
- Controle de chamadas simultâneas (1-10)
- Tempo entre chamadas (1-60 segundos)

### 2. Estados das Chamadas

| Estado | Descrição |
|--------|-----------|
| `pendiente` | Chamada aguardando para ser realizada |
| `marcando` | Sistema tentando conectar a chamada |
| `contestada` | Chamada foi atendida |
| `audio_reproducido` | Áudio iniciou reprodução |
| `esperando_dtmf` | Aguardando usuário pressionar tecla |
| `presiono_1` | Usuário pressionou tecla 1 |
| `no_presiono` | Não pressionou 1 ou pressionou outra tecla |
| `transferida` | Chamada transferida para agente |
| `finalizada` | Chamada encerrada |
| `error` | Erro durante o processo |

## API Endpoints

### Campanhas

#### Criar Campanha
```http
POST /api/v1/presione1/campanhas
```

**Body:**
```json
{
  "nombre": "Campanha Vendas Q1",
  "descripcion": "Campanha de vendas para primeiro trimestre",
  "lista_llamadas_id": 1,
  "mensaje_audio_url": "/sounds/vendas_q1.wav",
  "timeout_presione1": 15,
  "extension_transferencia": "100",
  "llamadas_simultaneas": 3,
  "tiempo_entre_llamadas": 5,
  "notas": "Campanha prioritária"
}
```

**Resposta:**
```json
{
  "id": 1,
  "nombre": "Campanha Vendas Q1",
  "descripcion": "Campanha de vendas para primeiro trimestre",
  "lista_llamadas_id": 1,
  "mensaje_audio_url": "/sounds/vendas_q1.wav",
  "timeout_presione1": 15,
  "extension_transferencia": "100",
  "cola_transferencia": null,
  "activa": false,
  "pausada": false,
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "fecha_actualizacion": "2024-01-15T10:30:00Z",
  "llamadas_simultaneas": 3,
  "tiempo_entre_llamadas": 5,
  "notas": "Campanha prioritária"
}
```

#### Listar Campanhas
```http
GET /api/v1/presione1/campanhas?apenas_ativas=true&skip=0&limit=20
```

#### Obter Campanha
```http
GET /api/v1/presione1/campanhas/{campana_id}
```

#### Atualizar Campanha
```http
PUT /api/v1/presione1/campanhas/{campana_id}
```

**Nota**: Campanhas ativas não podem ser editadas. Pare primeiro.

### Controle de Execução

#### Iniciar Campanha
```http
POST /api/v1/presione1/campanhas/{campana_id}/iniciar
```

**Body:**
```json
{
  "campana_id": 1,
  "usuario_id": "operador_01"
}
```

**O que acontece**:
1. Valida se há números disponíveis
2. Marca campanha como ativa
3. Inicia discado automático em background
4. Respeita limites de chamadas simultâneas

#### Pausar/Retomar Campanha
```http
POST /api/v1/presione1/campanhas/{campana_id}/pausar
```

**Body:**
```json
{
  "campana_id": 1,
  "pausar": true,
  "motivo": "Pausa para almoço"
}
```

**Pausar** (`pausar: true`):
- Para discado de novos números
- Chamadas em andamento continuam
- Pode ser retomada a qualquer momento

**Retomar** (`pausar: false`):
- Retoma discado automático
- Continua de onde parou

#### Parar Campanha
```http
POST /api/v1/presione1/campanhas/{campana_id}/parar
```

**Ação**:
- Marca campanha como inativa
- Finaliza todas as chamadas ativas
- Para discado automático
- Remove da lista de campanhas ativas

### Monitoramento

#### Estatísticas da Campanha
```http
GET /api/v1/presione1/campanhas/{campana_id}/estadisticas
```

**Resposta:**
```json
{
  "campana_id": 1,
  "nombre_campana": "Campanha Vendas Q1",
  "total_numeros": 1000,
  "llamadas_realizadas": 250,
  "llamadas_pendientes": 750,
  "llamadas_contestadas": 175,
  "llamadas_presiono_1": 87,
  "llamadas_no_presiono": 88,
  "llamadas_transferidas": 82,
  "llamadas_error": 5,
  "tasa_contestacion": 70.0,
  "tasa_presiono_1": 49.7,
  "tasa_transferencia": 94.3,
  "tiempo_medio_respuesta": 5.2,
  "duracion_media_llamada": 45.5,
  "activa": true,
  "pausada": false,
  "llamadas_activas": 3
}
```

#### Monitoramento em Tempo Real
```http
GET /api/v1/presione1/campanhas/{campana_id}/monitor
```

Inclui:
- Estado atual da campanha
- Chamadas ativas no momento
- Últimas chamadas finalizadas
- Estatísticas atualizadas

#### Listar Chamadas da Campanha
```http
GET /api/v1/presione1/campanhas/{campana_id}/llamadas?estado=presiono_1&presiono_1=true
```

Filtros disponíveis:
- `estado`: Filtrar por estado específico
- `presiono_1`: true/false/null
- `skip` e `limit` para paginação

#### Próximo Número
```http
GET /api/v1/presione1/campanhas/{campana_id}/proximo-numero
```

Útil para:
- Verificar progresso
- Debug e monitoramento
- Validar disponibilidade

## Configuração de Áudio

### Formatos Suportados
- **WAV** (recomendado): `.wav`
- **GSM**: `.gsm` 
- **uLaw**: `.ulaw`
- **aLaw**: `.alaw`
- **MP3**: `.mp3`

### Exemplo de Áudio
Conteúdo sugerido para o arquivo de áudio:

> "Olá! Esta é uma chamada da [Empresa]. Se você tem interesse em nossos produtos e gostaria de falar com um de nossos consultores, pressione a tecla 1 agora. Caso contrário, a chamada será encerrada. Pressione 1 para continuar."

### Configuração de Transferência

**Para Extensão Específica:**
```json
{
  "extension_transferencia": "100",
  "cola_transferencia": null
}
```

**Para Fila de Agentes:**
```json
{
  "extension_transferencia": null,
  "cola_transferencia": "vendas"
}
```

## Integração com Asterisk

### Eventos Processados

| Evento | Descrição | Ação |
|--------|-----------|------|
| `CallAnswered` | Chamada atendida | Marca como contestada |
| `AudioStarted` | Áudio iniciou | Inicia cronômetro DTMF |
| `WaitingDTMF` | Aguardando tecla | Marca estado |
| `DTMFReceived` | Tecla pressionada | Processa resposta |
| `DTMFTimeout` | Timeout DTMF | Finaliza chamada |
| `TransferStarted` | Transferência iniciada | Marca como transferida |
| `CallHangup` | Chamada desligada | Finaliza registro |

### Variables do Dialplan

```
LLAMADA_ID: ID da chamada na base de dados
AUDIO_URL: URL do arquivo de áudio
TIMEOUT_DTMF: Timeout em segundos
MODO: "PRESIONE1"
```

## Base de Dados

### Tabela `campanas_presione1`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | SERIAL | ID único |
| `nombre` | VARCHAR(100) | Nome da campanha |
| `descripcion` | VARCHAR(255) | Descrição |
| `lista_llamadas_id` | INTEGER | ID da lista de números |
| `mensaje_audio_url` | VARCHAR(500) | URL do áudio |
| `timeout_presione1` | INTEGER | Timeout DTMF (3-60s) |
| `extension_transferencia` | VARCHAR(20) | Extensão de destino |
| `cola_transferencia` | VARCHAR(50) | Fila de agentes |
| `activa` | BOOLEAN | Se está executando |
| `pausada` | BOOLEAN | Se está pausada |
| `llamadas_simultaneas` | INTEGER | Máximo simultâneo (1-10) |
| `tiempo_entre_llamadas` | INTEGER | Segundos entre calls (1-60) |

### Tabela `llamadas_presione1`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | SERIAL | ID único |
| `campana_id` | INTEGER | ID da campanha |
| `numero_destino` | VARCHAR(20) | Número discado |
| `numero_normalizado` | VARCHAR(20) | Número normalizado |
| `cli_utilizado` | VARCHAR(20) | CLI usado |
| `estado` | VARCHAR(30) | Estado atual |
| `fecha_inicio` | TIMESTAMP | Início da tentativa |
| `fecha_contestada` | TIMESTAMP | Momento atendida |
| `fecha_audio_inicio` | TIMESTAMP | Início do áudio |
| `fecha_dtmf_recibido` | TIMESTAMP | Recebimento DTMF |
| `fecha_transferencia` | TIMESTAMP | Início transferência |
| `fecha_fin` | TIMESTAMP | Fim da chamada |
| `presiono_1` | BOOLEAN | Se pressionou 1 |
| `dtmf_recibido` | VARCHAR(10) | Tecla pressionada |
| `tiempo_respuesta_dtmf` | REAL | Tempo de resposta |
| `transferencia_exitosa` | BOOLEAN | Transferência OK |
| `duracion_total` | INTEGER | Duração total (s) |
| `duracion_audio` | INTEGER | Duração áudio (s) |
| `motivo_finalizacion` | VARCHAR(100) | Motivo fim |

### View de Estatísticas

```sql
SELECT * FROM vista_estadisticas_presione1 WHERE campana_id = 1;
```

Retorna estatísticas resumidas por campanha com:
- Contadores de llamadas por estado
- Taxas de conversão
- Tempos médios
- Estado atual

## Exemplo de Uso Completo

### 1. Criar Lista de Números
```http
POST /api/v1/listas-llamadas
Content-Type: application/json

{
  "nombre": "Prospects Q1 2024",
  "descripcion": "Lista de prospects para primeiro trimestre"
}
```

### 2. Upload de Números
```http
POST /api/v1/listas-llamadas/1/upload
Content-Type: multipart/form-data

archivo: prospects_q1.csv
```

### 3. Criar Campanha Presione 1
```http
POST /api/v1/presione1/campanhas
Content-Type: application/json

{
  "nombre": "Campanha Prospects Q1",
  "descripcion": "Campanha automatizada para prospects",
  "lista_llamadas_id": 1,
  "mensaje_audio_url": "/sounds/prospects_q1.wav",
  "timeout_presione1": 12,
  "extension_transferencia": "200",
  "llamadas_simultaneas": 2,
  "tiempo_entre_llamadas": 3
}
```

### 4. Iniciar Campanha
```http
POST /api/v1/presione1/campanhas/1/iniciar
Content-Type: application/json

{
  "campana_id": 1,
  "usuario_id": "operador_vendas"
}
```

### 5. Monitorar Progresso
```http
GET /api/v1/presione1/campanhas/1/estadisticas
```

### 6. Pausar se Necessário
```http
POST /api/v1/presione1/campanhas/1/pausar
Content-Type: application/json

{
  "campana_id": 1,
  "pausar": true,
  "motivo": "Pausa para almoço"
}
```

### 7. Retomar
```http
POST /api/v1/presione1/campanhas/1/pausar
Content-Type: application/json

{
  "campana_id": 1,
  "pausar": false,
  "motivo": "Retomando após pausa"
}
```

### 8. Parar Campanha
```http
POST /api/v1/presione1/campanhas/1/parar
```

## Métricas e KPIs

### Taxas de Conversão

**Taxa de Atendimento:**
```
(Chamadas Atendidas / Chamadas Realizadas) × 100
```

**Taxa de Interesse (Presione 1):**
```
(Pressionaram 1 / Chamadas Atendidas) × 100
```

**Taxa de Transferência:**
```
(Transferências Exitosas / Pressionaram 1) × 100
```

### Tempos Médios

- **Tempo de Resposta DTMF**: Segundos entre início do áudio e pressionar tecla
- **Duração Média**: Tempo total das chamadas
- **Duração do Áudio**: Tempo que o áudio ficou tocando

### Exemplo de Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                    Campanha: Prospects Q1                  │
├─────────────────────────────────────────────────────────────┤
│ Estado: ● ATIVA      Pausada: ○ NÃO      Activas: 2/2     │
├─────────────────────────────────────────────────────────────┤
│ Total Números: 1,000    │ Realizadas: 250   │ Pendentes: 750│
│ Atendidas: 175 (70%)    │ Presione 1: 87    │ Não Pres: 88 │
│ Transferidas: 82 (94%)  │ Erros: 5          │              │
├─────────────────────────────────────────────────────────────┤
│ Tempo Médio Resposta: 5.2s     │ Duração Média: 45.5s    │
│ Taxa Interesse: 49.7%          │ Taxa Transfer: 94.3%     │
└─────────────────────────────────────────────────────────────┘
```

## Boas Práticas

### 1. Configuração de Áudio
- Use arquivos WAV com qualidade telefônica (8kHz, mono)
- Mantenha mensagem clara e objetiva (15-30 segundos)
- Instrua claramente para pressionar 1
- Teste áudio antes de usar em produção

### 2. Configuração de Timeout
- **Timeout muito baixo** (< 5s): Usuários podem não ter tempo
- **Timeout muito alto** (> 20s): Desperdício de recursos
- **Recomendado**: 10-15 segundos

### 3. Chamadas Simultâneas
- Inicie com poucos canais (1-2)
- Monitore taxa de atendimento
- Aumente gradualmente conforme capacidade
- Considere capacidade dos agentes para transferência

### 4. Gestão de Listas
- Use listas atualizadas e segmentadas
- Remova números problemáticos
- Considere horários adequados para cada público
- Integre com blacklist para compliance

### 5. Monitoramento
- Acompanhe métricas em tempo real
- Ajuste timeout conforme resultados
- Pause campanhas com alta taxa de erro
- Analise horários com melhor conversão

## Troubleshooting

### Problemas Comuns

**Campanha não inicia:**
- Verificar se há números disponíveis na lista
- Confirmar que campanha não está já ativa
- Validar configuração de transferência

**Baixa taxa de atendimento:**
- Verificar horários de discado
- Analisar qualidade da lista
- Considerar números em blacklist

**Baixa taxa de presione 1:**
- Revisar conteúdo do áudio
- Ajustar timeout DTMF
- Testar qualidade do áudio

**Transferências falhando:**
- Verificar configuração da extensão/fila
- Confirmar disponibilidade de agentes
- Validar dialplan do Asterisk

### Logs e Debug

Logs importantes para análise:
- Eventos de início/fim de campanhas
- Resultados DTMF por chamada
- Tempos de resposta por horário
- Erros de transferência

## Segurança e Compliance

### Considerações Legais
- Respeitar horários permitidos para discado
- Implementar opt-out automático
- Manter registros de consentimento
- Compliance com LGPD/regulamentações locais

### Integração com Blacklist
O sistema integra automaticamente com a blacklist existente:
- Números em blacklist são excluídos automaticamente
- Atualizações de blacklist afetam campanhas ativas
- Registro de tentativas para números bloqueados

### Auditoria
Todos os eventos são registrados para auditoria:
- Início/fim de campanhas
- Resultados de cada chamada
- Ações de usuários (pausar/parar)
- Transferências e seus resultados 