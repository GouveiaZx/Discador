# 📋 GUIA COMPLETO DO SISTEMA DISCADOR

## 🎯 O QUE FOI CRIADO?

Este é um **Sistema de Discador Preditivo Completo** com múltiplas funcionalidades avançadas:

---

## 🏠 FRONTEND - Interface Web (React + Vite)

### 📍 Localização: `frontend/`
### 🌐 URL: https://discador-main.vercel.app

### 📱 Páginas Principais:

1. **🎯 Dashboard Principal** (`/dashboard`)
   - Métricas em tempo real
   - Gráficos de chamadas por hora
   - Status de campanhas ativas
   - KPIs: Llamadas Activas, Efectividad, etc.

2. **📞 Monitoramento** (`/monitoreo`)
   - Chamadas ativas em tempo real
   - WebSocket para updates automáticos
   - Status de operadores

3. **🎪 Campanhas** (`/campanas`)
   - Criação de campanhas
   - Gestão de listas de números
   - Configuração de CLIs

4. **📋 Listas** (`/listas`)
   - Upload de arquivos CSV/Excel
   - Gestão de leads
   - Validação de números

5. **🛡️ Blacklist** (`/blacklist`)
   - Números bloqueados
   - DNC (Do Not Call)
   - Proteções legais

6. **📊 Histórico** (`/historial`)
   - Relatórios de chamadas
   - Exportação de dados
   - Análises estatísticas

---

## 🚀 BACKEND - API Sistema (FastAPI + Python)

### 📍 Localização: `backend/`
### 🌐 URL: https://railway-url/docs (Swagger API)

### 🔧 MÓDULOS PRINCIPAIS:

## 1. 📡 **SISTEMA MULTI-SIP**
**Localização:** `backend/app/routes/multi_sip.py`

**O que faz:**
- Gerencia múltiplos provedores SIP
- Roteamento inteligente de chamadas
- Seleção automática do melhor provedor
- Tarifação por destino

**Endpoints principais:**
```
POST /multi-sip/provedores - Criar provedor
GET  /multi-sip/provedores - Listar provedores
POST /multi-sip/tarifas    - Criar tarifas
GET  /multi-sip/selecionar/{numero} - Selecionar melhor provedor
```

## 2. 🤖 **ÁUDIO INTELIGENTE**
**Localização:** `backend/app/routes/audio_inteligente.py`

**O que faz:**
- Sistema "Presione 1" automático
- IVR (Interactive Voice Response)
- Detecção de voicemail
- Máquina de estados para áudio

**Funcionalidades:**
- Detecta se atendeu pessoa ou máquina
- Reproduz áudios específicos
- Aguarda interação DTMF (teclas)
- Transfere para operador se pressionar 1

**Endpoints principais:**
```
POST /audio/contextos     - Criar contexto de áudio
GET  /audio/contextos     - Listar contextos
POST /audio/iniciar       - Iniciar sessão de áudio
POST /audio/evento        - Processar evento de áudio
```

## 3. 🎯 **CODE2BASE - SELEÇÃO CLI INTELIGENTE**
**Localização:** `backend/app/routes/code2base.py`

**O que faz:**
- Seleciona automaticamente o melhor CLI
- Algoritmo baseado em:
  - Geografia (proximidade)
  - Qualidade histórica
  - Taxa de sucesso
  - Uso recente

**Funcionalidades:**
- Regras personalizáveis
- Pesos configuráveis
- Estatísticas de performance
- Simulações de teste

**Endpoints principais:**
```
POST /code2base/seleccionar - Selecionar CLI inteligente
GET  /code2base/reglas      - Listar regras
POST /code2base/reglas      - Criar regra
GET  /code2base/estadisticas - Ver estatísticas
```

## 4. 🗳️ **CAMPANHAS POLÍTICAS**
**Localização:** `backend/app/routes/campanha_politica.py`

**O que faz:**
- Compliance com legislação eleitoral
- Logs imutáveis para auditoria
- Validação de horários legais
- Calendário eleitoral

**Funcionalidades:**
- Período eleitoral automático
- Silêncio eleitoral
- Logs criptografados
- Exportação para autoridades

**Endpoints principais:**
```
POST /campanha-politica/campanhas      - Criar campanha política
POST /campanha-politica/validar-horario - Validar horário legal
GET  /campanha-politica/logs-eleitorais - Logs de auditoria
```

## 5. 🛡️ **BLACKLIST & VALIDAÇÕES**
**Localização:** `backend/app/routes/blacklist.py`

**O que faz:**
- DNC (Do Not Call) automático
- Blacklist por número/prefixo
- Validações de números
- Proteções legais

**Funcionalidades:**
- Import/export de listas
- Validação automática antes de discar
- Diferentes tipos de bloqueio
- Histórico de bloqueios

## 6. 📈 **MONITORAMENTO REAL-TIME**
**Localização:** `backend/app/routes/monitoring.py`

**O que faz:**
- WebSocket para updates em tempo real
- Métricas de sistema
- Alertas automáticos
- Dashboard em tempo real

**Funcionalidades:**
- Status de chamadas ativas
- Performance de operadores
- Alertas de problemas
- Métricas de qualidade

---

## 🗄️ BANCO DE DADOS

### 📍 Modelos Principais:

1. **Llamada** - Registro de chamadas
2. **Campana** - Campanhas de discagem
3. **CLI** - CLIs disponíveis
4. **ProvedorSIP** - Provedores VoIP
5. **ListaLlamadas** - Listas de números
6. **BlacklistNumero** - Números bloqueados
7. **CampanhaPolitica** - Campanhas eleitorais
8. **AudioContexto** - Contextos de áudio

---

## ⚙️ CONFIGURAÇÕES E VARIÁVEIS

### 📁 Arquivo: `backend/.env`
```env
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
ASTERISK_HOST=...
```

### 📁 Arquivo: `frontend/.env`
```env
VITE_API_URL=https://your-railway-url
```

---

## 🚀 COMO USAR O SISTEMA?

### 1. **Acessar Dashboard**
- Entre em: https://discador-main.vercel.app
- Faça login como admin

### 2. **Criar uma Campanha**
```
1. Ir em "Campanhas" > "Nueva Campaña"
2. Configurar nome, CLI, etc.
3. Upload da lista de números (CSV/Excel)
4. Configurar áudio inteligente (opcional)
5. Iniciar campanha
```

### 3. **Monitorar Chamadas**
```
1. Ir em "Monitoreo" > "Dashboard"
2. Ver chamadas ativas em tempo real
3. Acompanhar métricas e KPIs
```

### 4. **Configurar Áudio Inteligente**
```
1. API: POST /audio/contextos
2. Configurar "Presione 1"
3. Upload dos arquivos de áudio
4. Testar o fluxo
```

### 5. **Configurar Multi-SIP**
```
1. API: POST /multi-sip/provedores
2. Adicionar múltiplos provedores
3. Configurar tarifas por destino
4. Sistema seleciona automaticamente
```

---

## 🔧 COMO FUNCIONA A INTEGRAÇÃO?

### Frontend ⟷ Backend
```
Frontend (React) → API REST → Backend (FastAPI) → PostgreSQL
                              ↓
                           WebSocket → Updates em tempo real
```

### Backend ⟷ Asterisk
```
Backend → AGI Script → Asterisk → Chamada telefônica
Backend ← Eventos ← Asterisk ← Status da chamada
```

### Fluxo de uma Chamada:
```
1. 📋 Lista de números → Sistema
2. 🎯 CODE2BASE seleciona melhor CLI
3. 📡 Multi-SIP seleciona melhor provedor
4. 📞 Asterisk faz a ligação
5. 🤖 Áudio Inteligente detecta atendimento
6. 👤 Transfere para operador se necessário
7. 📊 Registra resultados e estatísticas
```

---

## 📚 DOCUMENTAÇÃO TÉCNICA

### APIs Disponíveis:
- **Swagger UI:** `http://backend-url/docs`
- **ReDoc:** `http://backend-url/redoc`

### Logs do Sistema:
- **Localização:** `backend/logs/`
- **Níveis:** DEBUG, INFO, WARNING, ERROR

### Testes:
- **Localização:** `backend/tests/`
- **Executar:** `pytest backend/tests/`

---

## 🎛️ FUNCIONALIDADES AVANÇADAS

### 1. **Algoritmo de Seleção CLI (CODE2BASE)**
- Aprende com histórico de chamadas
- Melhora automaticamente a taxa de sucesso
- Considera geografia, operadora, qualidade

### 2. **Sistema Multi-SIP**
- Failover automático entre provedores
- Balanceamento de carga
- Seleção por menor custo

### 3. **Áudio Inteligente**
- Detecção de voicemail vs. pessoa
- Fluxo "Presione 1" automático
- Transferência inteligente

### 4. **Compliance Político**
- Horários eleitorais automáticos
- Logs imutáveis para auditoria
- Exportação para autoridades

### 5. **Monitoramento Real-time**
- WebSocket para updates instantâneos
- Alertas automáticos
- Métricas de performance

---

## 🚨 PRÓXIMOS PASSOS RECOMENDADOS

1. **✅ Testar todas as funcionalidades**
2. **📚 Ler documentação da API (Swagger)**
3. **🎯 Criar primeira campanha de teste**
4. **🔧 Configurar provedores SIP reais**
5. **🎵 Upload de arquivos de áudio reais**
6. **👥 Treinar equipe no sistema**

---

**🎉 PARABÉNS! Você tem um sistema completo e profissional de discador preditivo!** 