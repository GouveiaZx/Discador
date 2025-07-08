# Sistema de Discado Preditivo "Presione 1" 🔢📞

## Visão Geral

O sistema **Presione 1** é uma funcionalidade avançada do discador preditivo que automatiza campanhas onde:

1. 🤖 **Sistema liga automaticamente** para números de uma lista
2. 🎵 **Reproduz mensagem de áudio** quando a chamada é atendida  
3. ⌨️ **Aguarda tecla 1** para demonstrar interesse
4. 📞 **Transfere automaticamente** para agente/fila se pressionou 1
5. ❌ **Encerra chamada** caso contrário

## 🚀 Início Rápido

### 1. Executar Migração
```bash
# Aplicar migração do banco de dados
psql -d discador -f migrations/create_presione1_tables.sql
```

### 2. Iniciar Servidor
```bash
cd backend
python main.py
```

### 3. Testar Sistema
```bash
# Teste completo automatizado
python scripts/teste_presione1.py

# Teste específico
python scripts/teste_presione1.py --test 1
```

### 4. Documentação da API
Acesse: `http://localhost:8000/documentacao`

## 📋 Exemplo de Uso

### Criar Campanha via API

```bash
curl -X POST "http://localhost:8000/api/v1/presione1/campanhas" \
     -H "Content-Type: application/json" \
     -d '{
       "nombre": "Campanha Vendas",
       "descripcion": "Campanha automatizada de vendas",
       "lista_llamadas_id": 1,
       "mensaje_audio_url": "/sounds/vendas.wav",
       "timeout_presione1": 15,
       "extension_transferencia": "100",
       "llamadas_simultaneas": 2,
       "tiempo_entre_llamadas": 5
     }'
```

### Iniciar Campanha

```bash
curl -X POST "http://localhost:8000/api/v1/presione1/campanhas/1/iniciar" \
     -H "Content-Type: application/json" \
     -d '{
       "campana_id": 1,
       "usuario_id": "operador_01"
     }'
```

### Monitorar Progresso

```bash
# Estatísticas em tempo real
curl "http://localhost:8000/api/v1/presione1/campanhas/1/estadisticas"

# Monitoramento completo
curl "http://localhost:8000/api/v1/presione1/campanhas/1/monitor"
```

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA PRESIONE 1                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Routes    │    │   Service   │    │   Models    │    │
│  │ presione1.py│───▶│presione1_   │───▶│campana_     │    │
│  │             │    │service.py   │    │presione1.py │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                   │         │
│         ▼                   ▼                   ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Schemas   │    │  Asterisk   │    │ PostgreSQL  │    │
│  │presione1.py │    │ Service     │    │  Database   │    │
│  │             │    │             │    │             │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

```
📱 API Request ──▶ 🛣️ Routes ──▶ 🔧 Service ──▶ 🗄️ Database
      │                │              │             │
      │                ▼              ▼             │
      │         📋 Validation   🤖 Business     ┌─────▼──────┐
      │                │         Logic         │            │
      │                │              │        │ PostgreSQL │
      ▼                │              ▼        │  Tables:   │
📤 Response ◀──────────┼──────── 📞 Asterisk   │ • campanhas│
                       │           AMI         │ • llamadas │
                       ▼                       │            │
                🎵 Audio Playback              └────────────┘
                ⌨️ DTMF Detection
                📞 Call Transfer
```

## 📊 Base de Dados

### Tabelas Principais

#### `campanas_presione1`
```sql
CREATE TABLE campanas_presione1 (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    lista_llamadas_id INTEGER REFERENCES listas_llamadas(id),
    mensaje_audio_url VARCHAR(500) NOT NULL,
    timeout_presione1 INTEGER DEFAULT 10,
    extension_transferencia VARCHAR(20),
    cola_transferencia VARCHAR(50),
    activa BOOLEAN DEFAULT FALSE,
    pausada BOOLEAN DEFAULT FALSE,
    llamadas_simultaneas INTEGER DEFAULT 1,
    tiempo_entre_llamadas INTEGER DEFAULT 5,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);
```

#### `llamadas_presione1`
```sql
CREATE TABLE llamadas_presione1 (
    id SERIAL PRIMARY KEY,
    campana_id INTEGER REFERENCES campanas_presione1(id),
    numero_destino VARCHAR(20) NOT NULL,
    numero_normalizado VARCHAR(20) NOT NULL,
    cli_utilizado VARCHAR(20),
    estado VARCHAR(30) DEFAULT 'pendiente',
    fecha_inicio TIMESTAMP,
    fecha_contestada TIMESTAMP,
    fecha_audio_inicio TIMESTAMP,
    fecha_dtmf_recibido TIMESTAMP,
    fecha_transferencia TIMESTAMP,
    fecha_fin TIMESTAMP,
    presiono_1 BOOLEAN,
    dtmf_recibido VARCHAR(10),
    tiempo_respuesta_dtmf REAL,
    transferencia_exitosa BOOLEAN,
    unique_id_asterisk VARCHAR(50),
    channel VARCHAR(100),
    duracion_total INTEGER,
    duracion_audio INTEGER,
    motivo_finalizacion VARCHAR(100)
);
```

### Estados das Chamadas

| Estado | Descrição | Próximo Estado |
|--------|-----------|----------------|
| `pendiente` | Aguardando discado | `marcando` |
| `marcando` | Conectando chamada | `contestada` / `error` |
| `contestada` | Chamada atendida | `audio_reproducido` |
| `audio_reproducido` | Áudio reproduzindo | `esperando_dtmf` |
| `esperando_dtmf` | Aguardando tecla | `presiono_1` / `no_presiono` |
| `presiono_1` | Pressionou tecla 1 | `transferida` |
| `no_presiono` | Não pressionou 1 | `finalizada` |
| `transferida` | Transferido para agente | `finalizada` |
| `finalizada` | Chamada encerrada | - |
| `error` | Erro no processo | - |

## 🔧 API Endpoints

### Campanhas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/presione1/campanhas` | Criar campanha |
| `GET` | `/presione1/campanhas` | Listar campanhas |
| `GET` | `/presione1/campanhas/{id}` | Obter campanha |
| `PUT` | `/presione1/campanhas/{id}` | Atualizar campanha |

### Controle

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/presione1/campanhas/{id}/iniciar` | Iniciar campanha |
| `POST` | `/presione1/campanhas/{id}/pausar` | Pausar/retomar |
| `POST` | `/presione1/campanhas/{id}/parar` | Parar campanha |

### Monitoramento

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/presione1/campanhas/{id}/estadisticas` | Estatísticas |
| `GET` | `/presione1/campanhas/{id}/monitor` | Monitor tempo real |
| `GET` | `/presione1/campanhas/{id}/llamadas` | Lista chamadas |
| `GET` | `/presione1/campanhas/{id}/proximo-numero` | Próximo número |

## 🧪 Testes

### Executar Testes Unitários
```bash
cd backend
python -m pytest tests/test_presione1.py -v
```

### Executar Teste Funcional Completo
```bash
python scripts/teste_presione1.py
```

### Executar Teste Específico
```bash
# Teste 1: Criar lista
python scripts/teste_presione1.py --test 1

# Teste 5: Iniciar campanha
python scripts/teste_presione1.py --test 5
```

### Cobertura de Testes

- ✅ **Testes Unitários**: Service, Models, Schemas
- ✅ **Testes de Integração**: API endpoints, Asterisk
- ✅ **Testes End-to-End**: Fluxo completo
- ✅ **Testes Funcionais**: Script automatizado

## 📈 Métricas e KPIs

### Métricas Principais

```python
# Taxa de Atendimento
tasa_contestacion = (llamadas_contestadas / llamadas_realizadas) * 100

# Taxa de Interesse
tasa_presione_1 = (presionaron_1 / llamadas_contestadas) * 100  

# Taxa de Transferência
tasa_transferencia = (transferencias_exitosas / presionaron_1) * 100
```

### Dashboard de Exemplo

```
┌─────────────────────────────────────────────────────────────┐
│              📊 CAMPANHA: Vendas Q1 2024                  │
├─────────────────────────────────────────────────────────────┤
│ Status: 🟢 ATIVA    │ Pausada: ❌ NÃO   │ Canais: 3/5    │
├─────────────────────────────────────────────────────────────┤
│ 📞 Total: 1,500     │ 📱 Feitas: 875    │ ⏳ Pendentes: 625│
│ ✅ Atendidas: 612   │ 1️⃣ Press 1: 287   │ ❌ Não Press: 325│
│ 🔄 Transfer: 271    │ 💥 Erros: 8       │               │
├─────────────────────────────────────────────────────────────┤
│ 📈 Taxa Atend: 69.9%     │ 🎯 Taxa Interest: 46.9%     │
│ ⏱️ Tempo Resp: 4.8s       │ 🔄 Taxa Transfer: 94.4%     │
└─────────────────────────────────────────────────────────────┘
```

## 🎵 Configuração de Áudio

### Formatos Suportados
- **WAV** (recomendado): `8kHz, 16-bit, mono`
- **GSM**: Formato comprimido
- **uLaw/aLaw**: Codecs telefônicos
- **MP3**: Para compatibilidade

### Exemplo de Mensagem
```
"Olá! Esta é uma chamada da [SUA EMPRESA]. 
Se você tem interesse em nossos produtos e 
gostaria de falar com um consultor, 
pressione a tecla 1 agora. 
Caso contrário, a chamada será encerrada. 
Pressione 1 para continuar."
```

### Boas Práticas
- ⏱️ **Duração**: 15-30 segundos máximo
- 🔊 **Qualidade**: 8kHz telefônica
- 📝 **Clareza**: Instruções claras e diretas
- ⚡ **Timeout**: 10-15 segundos recomendado

## 🔧 Configuração e Deploy

### Variáveis de Ambiente
```bash
# Asterisk
ASTERISK_HOST=localhost
ASTERISK_PUERTO=5038
ASTERISK_USUARIO=admin
ASTERISK_PASSWORD=secret

# Base de dados
DB_HOST=localhost
DB_PUERTO=5432
DB_NOMBRE=discador
DB_USUARIO=postgres
DB_PASSWORD=password
```

### Estrutura de Arquivos
```
backend/
├── app/
│   ├── models/
│   │   └── campana_presione1.py      # 📋 Models
│   ├── schemas/
│   │   └── presione1.py              # 📝 Schemas
│   ├── services/
│   │   ├── presione1_service.py      # 🔧 Service
│   │   └── asterisk.py               # 📞 Asterisk
│   └── routes/
│       └── presione1.py              # 🛣️ Routes
├── migrations/
│   └── create_presione1_tables.sql   # 🗄️ Migration
├── scripts/
│   └── teste_presione1.py            # 🧪 Test Script
├── tests/
│   └── test_presione1.py             # ✅ Tests
└── docs/
    └── DISCADO_PREDITIVO_PRESIONE1.md # 📚 Docs
```

## 🔍 Troubleshooting

### Problemas Comuns

**❌ Campanha não inicia**
```bash
# Verificar números disponíveis
curl "http://localhost:8000/api/v1/presione1/campanhas/1/proximo-numero"

# Verificar estado da campanha
curl "http://localhost:8000/api/v1/presione1/campanhas/1"
```

**❌ Baixa taxa de atendimento**
- Verificar horários de discado
- Analisar qualidade da lista
- Conferir blacklist

**❌ Baixa taxa de presione 1**
- Revisar conteúdo do áudio
- Ajustar timeout DTMF
- Testar qualidade do som

**❌ Transferências falhando**
```bash
# Verificar logs do Asterisk
tail -f /var/log/asterisk/messages

# Testar extensão manualmente
asterisk -x "originate SIP/100 extension s@test"
```

### Logs Importantes

```bash
# Logs da aplicação
tail -f logs/discador.log | grep "Presione1"

# Logs do PostgreSQL
tail -f /var/log/postgresql/postgresql.log

# Logs do Asterisk
tail -f /var/log/asterisk/messages
```

## 🔐 Segurança e Compliance

### Considerações Legais
- 📅 Respeitar horários de discado (8h-20h)
- 🚫 Implementar opt-out automático
- 📋 Manter registros de consentimento
- ⚖️ Compliance com LGPD

### Auditoria
- 📊 Logs completos de campanhas
- 🔍 Rastreamento de resultados
- 👤 Registro de ações de usuários
- 📞 Histórico de transferências

## 🚀 Próximos Passos

### Funcionalidades Planejadas
- [ ] 📊 Dashboard web em tempo real
- [ ] 📧 Relatórios por email automáticos
- [ ] 🎵 Upload de áudio via interface
- [ ] 📱 Integração com WhatsApp
- [ ] 🤖 IA para otimização de horários
- [ ] 📈 Analytics avançados

### Melhorias Técnicas
- [ ] 🔄 Cache Redis para performance
- [ ] 📦 Containerização Docker
- [ ] ☁️ Deploy em Kubernetes
- [ ] 📈 Métricas Prometheus
- [ ] 🔍 Logs estruturados ELK

## 📞 Suporte

### Contatos
- 📧 **Email**: suporte@discador.com
- 💬 **Slack**: #discador-presione1
- 📚 **Wiki**: [docs.discador.com](https://docs.discador.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/empresa/discador/issues)

### FAQ

**Q: Posso usar arquivos MP3?**
A: Sim, mas WAV 8kHz é recomendado para melhor qualidade.

**Q: Qual o limite de chamadas simultâneas?**
A: Configurável de 1-10, dependendo da capacidade do Asterisk.

**Q: Como integrar com meu CRM?**
A: Use os webhooks ou consulte a API REST para integração.

**Q: É possível personalizar a mensagem por campanha?**
A: Sim, cada campanha tem sua própria URL de áudio.

---

**✨ Sistema Presione 1 - Discado Preditivo Inteligente**

*Documentação atualizada em: Janeiro 2024* 