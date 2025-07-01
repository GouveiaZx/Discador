# 🚀 GUIA DE INÍCIO RÁPIDO - DISCADOR

## ⚡ ACESSO RÁPIDO

### 🌐 URLs Principais:
- **Frontend:** https://discador-main.vercel.app
- **API Swagger:** https://graceful-courtesy-production.up.railway.app/docs
- **Status Backend:** https://graceful-courtesy-production.up.railway.app/health

---

## 🎯 PRIMEIRO USO - 5 MINUTOS

### 1. **Acesse o Dashboard** (30 segundos)
```
1. Entre em: https://discador-main.vercel.app
2. Você verá o dashboard principal funcionando
3. Observe métricas em tempo real
```

### 2. **Teste a API** (1 minuto)
```
1. Acesse: https://graceful-courtesy-production.up.railway.app/docs
2. Clique em "Try it out" em qualquer endpoint
3. Execute GET /health para verificar status
```

### 3. **Teste Primeira Funcionalidade** (2 minutos)
```
1. Na API Swagger, vá para: /code2base/clis
2. Execute GET /code2base/clis para ver CLIs
3. Teste POST /code2base/seleccionar com um número
```

### 4. **Explore o Frontend** (1.5 minutos)
```
1. Navegue pelas abas: Monitoreo, Campanhas, Listas
2. Veja os gráficos em tempo real
3. Observe a interface responsiva
```

---

## 🛠️ CONFIGURAÇÃO BÁSICA

### 1. **Criar Primeiro CLI** 
```bash
curl -X POST "https://graceful-courtesy-production.up.railway.app/code2base/clis" \
-H "Content-Type: application/json" \
-d '{
  "numero": "+5491112345678",
  "nombre": "CLI Teste",
  "prefijo_codigo": "54911",
  "operadora": "CLARO",
  "activo": true
}'
```

### 2. **Testar Seleção Inteligente**
```bash
curl -X POST "https://graceful-courtesy-production.up.railway.app/code2base/seleccionar" \
-H "Content-Type: application/json" \
-d '{
  "numero_destino": "+5491187654321",
  "campaña_id": 1
}'
```

### 3. **Configurar Provedor SIP**
```bash
curl -X POST "https://graceful-courtesy-production.up.railway.app/multi-sip/provedores" \
-H "Content-Type: application/json" \
-d '{
  "nome": "Provedor Teste",
  "servidor_sip": "sip.provider.com",
  "porta": 5060,
  "usuario_sip": "user123",
  "senha_sip": "pass123",
  "status": "ativo"
}'
```

---

## 🎪 CRIAR PRIMEIRA CAMPANHA

### Via API (Recomendado):
```bash
# 1. Criar campanha
curl -X POST "https://graceful-courtesy-production.up.railway.app/campanas" \
-H "Content-Type: application/json" \
-d '{
  "nombre": "Campanha Teste",
  "descripcion": "Primeira campanha de teste",
  "cli_id": 1,
  "activo": true
}'

# 2. Verificar campanhas
curl -X GET "https://graceful-courtesy-production.up.railway.app/campanas"
```

### Via Frontend:
```
1. Acesse aba "Campanhas"
2. Clique "Nueva Campaña"
3. Preencha formulário
4. Salve e ative
```

---

## 🤖 CONFIGURAR ÁUDIO INTELIGENTE

### Setup Automático:
```bash
curl -X POST "https://graceful-courtesy-production.up.railway.app/audio/setup-padrao"
```

### Criar Contexto Manual:
```bash
curl -X POST "https://graceful-courtesy-production.up.railway.app/audio/contextos" \
-H "Content-Type: application/json" \
-d '{
  "nome": "Presione 1 Personalizado",
  "timeout_dtmf_padrao": 10,
  "detectar_voicemail": true,
  "audio_principal_url": "https://exemplo.com/audio.wav"
}'
```

---

## 📊 MONITORAMENTO EM TEMPO REAL

### 1. **Dashboard Web:**
- Acesse: https://discador-main.vercel.app
- Vá para aba "Monitoreo"
- Observe updates automáticos

### 2. **API Monitoramento:**
```bash
# Status geral
curl -X GET "https://graceful-courtesy-production.up.railway.app/monitoring/dashboard"

# Chamadas ativas
curl -X GET "https://graceful-courtesy-production.up.railway.app/monitoring/llamadas-activas"
```

### 3. **WebSocket (Avançado):**
```javascript
const ws = new WebSocket('wss://graceful-courtesy-production.up.railway.app/ws/monitoring');
ws.onmessage = (event) => {
  console.log('Update em tempo real:', JSON.parse(event.data));
};
```

---

## 🧪 TESTES RÁPIDOS

### 1. **Teste Sistema CODE2BASE:**
```bash
curl -X POST "https://graceful-courtesy-production.up.railway.app/code2base/testar" \
-H "Content-Type: application/json" \
-d '{
  "numero_destino": "+5491112345678",
  "campaña_id": 1,
  "simulaciones": 5
}'
```

### 2. **Teste Multi-SIP:**
```bash
curl -X GET "https://graceful-courtesy-production.up.railway.app/multi-sip/selecionar/+5491112345678"
```

### 3. **Verificar Blacklist:**
```bash
curl -X GET "https://graceful-courtesy-production.up.railway.app/blacklist/validar/+5491112345678"
```

---

## 📋 CHECKLIST DE VERIFICAÇÃO

### ✅ Sistema Básico Funcionando:
- [ ] Frontend carrega sem erros
- [ ] API responde em /health
- [ ] Dashboard mostra métricas
- [ ] Swagger funciona em /docs

### ✅ Funcionalidades Core:
- [ ] CODE2BASE seleciona CLIs
- [ ] Multi-SIP lista provedores
- [ ] Áudio Inteligente configurado
- [ ] Monitoramento em tempo real

### ✅ Módulos Avançados:
- [ ] Campanhas Políticas (se necessário)
- [ ] Blacklist configurada
- [ ] Relatórios funcionando
- [ ] WebSockets conectando

---

## 🚨 SOLUÇÃO DE PROBLEMAS

### ❌ Frontend não carrega:
```bash
# Verificar se API está online
curl https://graceful-courtesy-production.up.railway.app/health
```

### ❌ API retorna erro 500:
```bash
# Verificar logs no Railway dashboard
# Ou testar endpoint básico
curl https://graceful-courtesy-production.up.railway.app/
```

### ❌ Sem dados no dashboard:
```bash
# Criar dados de teste
curl -X POST "https://graceful-courtesy-production.up.railway.app/code2base/clis" \
-H "Content-Type: application/json" \
-d '{"numero": "+5491112345678", "nombre": "CLI Teste", "activo": true}'
```

---

## 🎓 PRÓXIMOS PASSOS

### 📚 **Aprender Mais:**
1. Leia `GUIA_COMPLETO_SISTEMA.md`
2. Explore `MAPA_ROTAS_API.md`
3. Teste todas as funcionalidades no Swagger

### 🔧 **Configurar Produção:**
1. Configurar provedores SIP reais
2. Upload de arquivos de áudio
3. Configurar Asterisk integration
4. Configurar alertas de monitoramento

### 🚀 **Escalar Sistema:**
1. Configurar múltiplos CLIs
2. Criar campanhas reais
3. Configurar blacklist completa
4. Treinar equipe de operação

---

**✨ Parabéns! Você tem um sistema completo funcionando!** 