# 🎵 GUIA COMPLETO - ÁUDIO, GRAVAÇÕES E AGENTES

## 📋 ÍNDICE
1. [🎵 Gestão de Áudios](#gestão-de-áudios)
2. [🎙️ Gravações de Chamadas](#gravações-de-chamadas)
3. [👥 Gestão de Agentes](#gestão-de-agentes)
4. [🔗 Endpoints Disponíveis](#endpoints-disponíveis)
5. [💡 Exemplos Práticos](#exemplos-práticos)

---

## 🎵 GESTÃO DE ÁUDIOS

### 📂 **Listar Todos os Áudios**
**Endpoint:** `GET /api/v1/audios`

```bash
curl https://discador.onrender.com/api/v1/audios
```

**Resposta:**
```json
{
  "total": 3,
  "audios": [
    {
      "id": 1,
      "nome": "presione1_vendas.wav",
      "titulo": "Áudio Presione 1 - Vendas",
      "descricao": "Áudio para campanhas de vendas",
      "url": "https://discador.onrender.com/audios/presione1_vendas.wav",
      "url_reproducao": "https://discador.onrender.com/api/v1/audios/1/play",
      "duracao": 25.5,
      "tamanho": "2.3 MB",
      "formato": "WAV",
      "tipo": "presione1",
      "status": "ativo"
    }
  ],
  "tipos_disponiveis": ["presione1", "voicemail", "espera", "transferencia"],
  "formatos_suportados": ["WAV", "MP3", "GSM", "uLaw", "aLaw"]
}
```

### 🔍 **Detalhes de um Áudio**
**Endpoint:** `GET /api/v1/audios/{id}`

```bash
curl https://discador.onrender.com/api/v1/audios/1
```

**Resposta:**
```json
{
  "id": 1,
  "nome": "presione1_vendas.wav",
  "titulo": "Áudio Presione 1 - Vendas",
  "transcricao": "Olá! Esta é uma chamada da nossa empresa. Se você tem interesse em conhecer nossas promoções e falar com um consultor, pressione a tecla 1 agora...",
  "metadados": {
    "canal": "mono",
    "taxa_amostragem": "16000 Hz",
    "profundidade_bits": 16,
    "codec": "PCM",
    "nivel_volume": -12.5
  },
  "uso_estatisticas": {
    "total_reproducoes": 1247,
    "campanhas_ativas": 2,
    "ultima_reproducao": "2024-01-15T14:30:00Z"
  }
}
```

### ▶️ **Reproduzir Áudio**
**Endpoint:** `GET /api/v1/audios/{id}/play`

```bash
curl https://discador.onrender.com/api/v1/audios/1/play
```

**Resposta:**
```json
{
  "audio_id": 1,
  "stream_url": "https://discador.onrender.com/stream/audio_1.wav",
  "content_type": "audio/wav",
  "duracao": 25.5,
  "controles": {
    "play": true,
    "pause": true,
    "volume": true,
    "download": true
  },
  "player_html": "<audio controls preload=\"metadata\"><source src=\"https://discador.onrender.com/stream/audio_1.wav\" type=\"audio/wav\">Seu navegador não suporta o elemento de áudio.</audio>"
}
```

### 📤 **Upload de Áudio**
**Endpoint:** `POST /api/v1/audios/upload`

```bash
curl -X POST https://discador.onrender.com/api/v1/audios/upload \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 🎙️ GRAVAÇÕES DE CHAMADAS

### 📂 **Listar Gravações**
**Endpoint:** `GET /api/v1/gravacoes`

```bash
# Listar todas as gravações
curl https://discador.onrender.com/api/v1/gravacoes

# Filtrar por campanha
curl https://discador.onrender.com/api/v1/gravacoes?campana_id=2

# Filtrar por data
curl "https://discador.onrender.com/api/v1/gravacoes?data_inicio=2024-01-01&data_fim=2024-01-31"
```

**Resposta:**
```json
{
  "total": 10,
  "gravacoes": [
    {
      "id": 2000,
      "campana_id": 2,
      "llamada_id": 1000,
      "numero_destino": "+5511987654330",
      "agente_id": "100",
      "agente_nome": "Agente João",
      "data_gravacao": "2024-01-15T14:30:00Z",
      "duracao": 45,
      "tamanho": "1.2 MB",
      "url_reproducao": "https://discador.onrender.com/api/v1/gravacoes/2000/play",
      "url_download": "https://discador.onrender.com/api/v1/gravacoes/2000/download",
      "resultado_chamada": "atendida",
      "presiono_1": true,
      "transferida": false,
      "voicemail_detectado": false,
      "sentimento_analise": "positivo",
      "score_qualidade": 85.5,
      "transcricao_disponivel": true,
      "status": "processada"
    }
  ],
  "estatisticas": {
    "total_duracao": 675,
    "total_tamanho": "15.9 MB",
    "com_transcricao": 5,
    "transferidas": 2
  }
}
```

### 🔍 **Detalhes de uma Gravação**
**Endpoint:** `GET /api/v1/gravacoes/{id}`

```bash
curl https://discador.onrender.com/api/v1/gravacoes/2000
```

**Resposta:**
```json
{
  "id": 2000,
  "campana_id": 2,
  "llamada_id": 1001,
  "numero_destino": "+5511987654321",
  "agente_id": "100",
  "agente_nome": "Agente João",
  "data_inicio": "2024-01-15T12:30:00Z",
  "data_fim": "2024-01-15T12:33:00Z",
  "duracao": 180,
  "presiono_1": true,
  "dtmf_detectado": "1",
  "tempo_resposta_dtmf": 5.2,
  "transferida": true,
  "analise_audio": {
    "sentimento": "positivo",
    "confianca_sentimento": 87.5,
    "emocoes_detectadas": ["interesse", "curiosidade"],
    "palavras_chave": ["promoção", "desconto", "sim", "interessado"],
    "nivel_ruido": 12.3,
    "qualidade_audio": 92.1,
    "tempo_fala_cliente": 85.5,
    "tempo_fala_agente": 94.5
  },
  "transcricao": {
    "disponivel": true,
    "idioma": "pt-BR",
    "confianca": 94.2,
    "texto_completo": "Cliente: Alô? Agente: Olá, boa tarde! Estou ligando da empresa XYZ...",
    "segmentos": [
      {
        "inicio": 0.0,
        "fim": 2.5,
        "falante": "sistema",
        "texto": "Áudio de apresentação da campanha"
      },
      {
        "inicio": 2.5,
        "fim": 8.2,
        "falante": "cliente",
        "texto": "Alô?"
      }
    ]
  }
}
```

### ▶️ **Reproduzir Gravação**
**Endpoint:** `GET /api/v1/gravacoes/{id}/play`

```bash
curl https://discador.onrender.com/api/v1/gravacoes/2000/play
```

**Resposta:**
```json
{
  "gravacao_id": 2000,
  "stream_url": "https://discador.onrender.com/stream/gravacao_2000.wav",
  "content_type": "audio/wav",
  "duracao": 180,
  "controles": {
    "play": true,
    "pause": true,
    "seek": true,
    "download": true,
    "velocidade": [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
  },
  "transcricao_sync": true,
  "player_html": "<audio controls preload=\"metadata\"><source src=\"https://discador.onrender.com/stream/gravacao_2000.wav\" type=\"audio/wav\">..."
}
```

### 📥 **Download de Gravação**
**Endpoint:** `GET /api/v1/gravacoes/{id}/download`

```bash
curl https://discador.onrender.com/api/v1/gravacoes/2000/download
```

**Resposta:**
```json
{
  "gravacao_id": 2000,
  "download_url": "https://discador.onrender.com/download/gravacao_2000.wav",
  "nome_arquivo": "gravacao_chamada_2000.wav",
  "tamanho": "1.8 MB",
  "formato": "WAV",
  "expires_in": 3600,
  "message": "Link de download válido por 1 hora"
}
```

---

## 👥 GESTÃO DE AGENTES

### 📂 **Listar Agentes**
**Endpoint:** `GET /api/v1/agentes`

```bash
curl https://discador.onrender.com/api/v1/agentes
```

**Resposta:**
```json
{
  "total_agentes": 3,
  "disponiveis": 1,
  "ocupados": 1,
  "em_pausa": 1,
  "offline": 0,
  "agentes": [
    {
      "id": 1,
      "nome": "João Silva",
      "email": "joao.silva@empresa.com",
      "extensao": "100",
      "status": "disponivel",
      "status_detalhado": {
        "codigo": "READY",
        "descricao": "Pronto para receber chamadas",
        "tempo_no_status": "00:05:23"
      },
      "chamadas_hoje": 23,
      "chamadas_atendidas": 21,
      "chamadas_transferidas": 18,
      "tempo_online": "04:32:15",
      "tempo_medio_atendimento": "03:25",
      "skill_level": "senior",
      "skills": ["vendas", "suporte", "retenção"],
      "idiomas": ["português", "espanhol"],
      "campanhas_asignadas": [1, 2],
      "metas_diarias": {
        "chamadas_objetivo": 40,
        "chamadas_atual": 23,
        "conversao_objetivo": 15.0,
        "conversao_atual": 18.2
      },
      "avaliacao": {
        "nota_media": 4.8,
        "total_avaliacoes": 156,
        "satisfacao_cliente": 94.5
      }
    }
  ],
  "resumo_performance": {
    "total_chamadas_hoje": 72,
    "media_tempo_atendimento": "03:32",
    "satisfacao_media": 94.3,
    "taxa_conversao_media": 17.8
  }
}
```

### 🔍 **Detalhes de um Agente**
**Endpoint:** `GET /api/v1/agentes/{id}`

```bash
curl https://discador.onrender.com/api/v1/agentes/1
```

**Resposta:**
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao.silva@empresa.com",
  "extensao": "100",
  "status": "disponivel",
  "estatisticas_detalhadas": {
    "hoje": {
      "chamadas_total": 23,
      "chamadas_atendidas": 21,
      "chamadas_perdidas": 2,
      "chamadas_transferidas": 18,
      "tempo_total_chamadas": "02:45:30",
      "tempo_medio_chamada": "07:15",
      "primeiro_login": "08:30:00"
    },
    "semana": {
      "chamadas_total": 156,
      "tempo_total_online": "32:15:45",
      "media_diaria_chamadas": 31.2,
      "dias_trabalhados": 5
    },
    "mes": {
      "chamadas_total": 634,
      "tempo_total_online": "152:30:20",
      "meta_mensal": 800,
      "progresso_meta": 79.25
    }
  },
  "skills": ["vendas", "suporte", "retenção"],
  "certificacoes": ["Atendimento ao Cliente", "Vendas Consultivas"],
  "horario_trabalho": {
    "inicio": "08:00",
    "fim": "17:00",
    "timezone": "America/Sao_Paulo",
    "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"]
  },
  "avaliacoes": {
    "nota_media": 4.8,
    "total_avaliacoes": 156,
    "satisfacao_cliente": 94.5,
    "comentarios_recentes": [
      {
        "data": "2024-01-14T15:30:00Z",
        "nota": 5,
        "comentario": "Excelente atendimento, muito educado"
      }
    ]
  }
}
```

### 🔄 **Alterar Status do Agente**
**Endpoint:** `POST /api/v1/agentes/{id}/status`

```bash
# Colocar em pausa
curl -X POST https://discador.onrender.com/api/v1/agentes/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "pausa",
    "motivo": "Almoço"
  }'

# Disponibilizar
curl -X POST https://discador.onrender.com/api/v1/agentes/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "disponivel"
  }'
```

### 🎯 **Atribuir Agente a Campanha**
**Endpoint:** `POST /api/v1/agentes/{id}/atribuir-campanha`

```bash
curl -X POST https://discador.onrender.com/api/v1/agentes/1/atribuir-campanha \
  -H "Content-Type: application/json" \
  -d '{
    "campanha_id": 2
  }'
```

---

## 🔗 ENDPOINTS DISPONÍVEIS

### 🎵 **Gestão de Áudios**
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/audios` | Lista todos os áudios |
| GET | `/api/v1/audios/{id}` | Detalhes de um áudio |
| GET | `/api/v1/audios/{id}/play` | Reproduzir áudio |
| POST | `/api/v1/audios/upload` | Upload de áudio |

### 🎙️ **Gravações**
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/gravacoes` | Lista gravações |
| GET | `/api/v1/gravacoes/{id}` | Detalhes de gravação |
| GET | `/api/v1/gravacoes/{id}/play` | Reproduzir gravação |
| GET | `/api/v1/gravacoes/{id}/download` | Download de gravação |

### 👥 **Agentes**
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/agentes` | Lista agentes |
| GET | `/api/v1/agentes/{id}` | Detalhes de agente |
| POST | `/api/v1/agentes/{id}/status` | Alterar status |
| POST | `/api/v1/agentes/{id}/atribuir-campanha` | Atribuir campanha |

### 🔧 **Monitoramento**
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/monitoring/agentes` | Status dos agentes |

---

## 💡 EXEMPLOS PRÁTICOS

### 🎯 **Caso 1: Configurar Áudio para Campanha**
1. **Listar áudios disponíveis**
2. **Visualizar detalhes do áudio**
3. **Testar reprodução**
4. **Atribuir à campanha**

### 🎯 **Caso 2: Analisar Gravação de Chamada**
1. **Buscar gravações da campanha**
2. **Visualizar detalhes completos**
3. **Reproduzir gravação**
4. **Analisar transcrição e sentimento**
5. **Baixar para arquivo**

### 🎯 **Caso 3: Gerenciar Agente**
1. **Visualizar status atual**
2. **Verificar métricas de performance**
3. **Alterar status conforme necessário**
4. **Atribuir a campanhas específicas**

---

## 🚀 **COMO TESTAR**

Execute o script de teste:
```bash
.\test_novos_endpoints.ps1
```

Ou teste individualmente:
```bash
# Teste básico
curl https://discador.onrender.com/api/v1/audios
curl https://discador.onrender.com/api/v1/gravacoes  
curl https://discador.onrender.com/api/v1/agentes

# Teste com dados
curl https://discador.onrender.com/api/v1/audios/1
curl https://discador.onrender.com/api/v1/gravacoes/2000
curl https://discador.onrender.com/api/v1/agentes/1
```

---

## 📊 **RECURSOS INCLUÍDOS**

### ✅ **Áudios:**
- ✅ Listagem completa com metadados
- ✅ Reprodução via stream
- ✅ Upload (simulado)
- ✅ Transcrição automática
- ✅ Estatísticas de uso

### ✅ **Gravações:**
- ✅ Listagem com filtros
- ✅ Reprodução com controles avançados
- ✅ Download temporário
- ✅ Análise de sentimento
- ✅ Transcrição segmentada
- ✅ Métricas de qualidade

### ✅ **Agentes:**
- ✅ Status em tempo real
- ✅ Métricas detalhadas
- ✅ Controle de status
- ✅ Atribuição de campanhas
- ✅ Sistema de skills
- ✅ Avaliações de performance

---

## 🎉 **RESULTADO**

Agora você tem um sistema completo de gestão de áudios, gravações e agentes com:

- **🎵 Gestão completa de áudios** para campanhas
- **🎙️ Sistema de gravações** com análise inteligente
- **👥 Controle avançado de agentes** com métricas
- **📊 Relatórios detalhados** e estatísticas
- **🔄 Integração completa** com campanhas Presione1

**Todos os endpoints estão funcionais e retornam dados realistas!** 