# 🚀 GUIA COMPLETO: COMO USAR O SISTEMA DE DISCADO

## 📋 **VISÃO GERAL:**
Sistema completo para discado preditivo com gravações, monitoramento em tempo real e relatórios avançados.

---

## **1. 📂 UPLOAD DE LISTAS (✅ FUNCIONANDO)**

### **Passo 1:** Acessar Upload
```
🔗 URL: https://discador.vercel.app/
📱 Selecionar: "Subida de Listas"
```

### **Passo 2:** Fazer Upload
```
📁 Selecionar arquivo: Slackall.txt ou qualquer lista
🎯 Escolher campanha: Selecionar da lista
⚡ Upload automático: Chunks de 500 números
📊 Monitoramento: Logs no console do browser
```

---

## **2. 🎯 CRIAR CAMPANHAS**

### **Endpoint para Criar Campanha:**
```http
POST https://discador.onrender.com/api/v1/campaigns
Content-Type: application/json

{
  "name": "Campanha Vendas 2025",
  "description": "Campanha de vendas para Q1",
  "cli_number": "+5511999999999",
  "audio_url": "/sounds/presione1.wav",
  "start_time": "09:00",
  "end_time": "18:00",
  "timezone": "America/Sao_Paulo",
  "max_attempts": 3,
  "retry_interval": 30,
  "max_concurrent_calls": 5
}
```

### **No Frontend:**
1. **Acessar:** Gestión → Campanhas
2. **Criar:** Nova Campanha
3. **Configurar:**
   - Nome e descrição
   - CLI (número origem)
   - Áudio "Presione 1"
   - Horários de funcionamento
   - Tentativas máximas
   - Chamadas simultâneas

---

## **3. 🎵 CONFIGURAR ÁUDIOS**

### **Áudios Necessários:**

#### **📢 Áudio Principal (Presione 1):**
```
"Olá! Esta é uma chamada da [Empresa]. 
Se você tem interesse em nossos produtos e 
gostaria de falar com um consultor, 
pressione a tecla 1 agora. 
Caso contrário, a chamada será encerrada."
```

#### **📱 Áudio para Voicemail:**
```
"Esta é uma mensagem da [Empresa]. 
Temos uma proposta especial para você. 
Entre em contato conosco através do 
telefone [NÚMERO] ou visite nosso site."
```

### **Formatos Suportados:**
- **WAV** (recomendado)
- **GSM**
- **MP3**
- **uLaw/aLaw**

---

## **4. 📞 INICIAR LIGAÇÕES**

### **Método 1: Via API**
```http
POST https://discador.onrender.com/api/v1/presione1/campanhas/{id}/iniciar
Content-Type: application/json

{
  "usuario_id": 1
}
```

### **Método 2: Via Frontend**
1. **Acessar:** Dashboard → Campanhas
2. **Selecionar:** Campanha criada
3. **Clicar:** "Iniciar Campanha"
4. **Configurar:**
   - Chamadas simultâneas
   - Tempo entre chamadas
   - Horários de funcionamento

### **O que Acontece:**
```
🔄 Sistema inicia discado automático
📞 Liga para números da lista
🎵 Reproduz áudio "Presione 1"
⌨️ Aguarda usuário pressionar 1
📞 Se pressionar 1: transfere para agente
❌ Se não: encerra chamada
```

---

## **5. 📊 MONITORAMENTO EM TEMPO REAL**

### **Dashboard Principal:**
```
🔗 URL: https://discador.vercel.app/dashboard
```

### **Informações Disponíveis:**
- **📞 Chamadas Ativas:** Lista em tempo real
- **📈 Estatísticas:** Taxa de sucesso, duração média
- **👥 Agentes:** Status online/offline
- **🔄 Campanhas:** Estado ativo/pausado
- **📊 Gráficos:** Performance em tempo real

### **WebSocket para Tempo Real:**
```javascript
// Frontend conecta automaticamente ao WebSocket
wss://discador.onrender.com/api/v1/asterisk-monitoring/ws/monitoring
```

### **Monitorar Campanha Específica:**
```http
GET https://discador.onrender.com/api/v1/presione1/campanhas/{id}/monitor
```

---

## **6. 🎙️ GRAVAÇÕES DAS CHAMADAS**

### **Onde Ficam as Gravações:**
```
📁 Diretório: /var/spool/asterisk/monitor/
📝 Formato: discador-{CHAMADA_ID}.wav
🔄 Auto-geradas: Para todas as chamadas
```

### **Configuração no Asterisk:**
```
# Habilitado automaticamente no extensions.conf
[discador-monitoring]
exten => _X.,1,Monitor(wav,/var/spool/asterisk/monitor/discador-${CHAMADA_ID},m)
```

### **Acessar Gravações via API:**
```http
GET https://discador.onrender.com/api/v1/monitoring/gravacoes/{chamada_id}
```

### **Listar Todas as Gravações:**
```http
GET https://discador.onrender.com/api/v1/monitoring/gravacoes?data=2025-01-01
```

---

## **7. 📈 RELATÓRIOS E ESTATÍSTICAS**

### **Relatório de Campanha:**
```http
GET https://discador.onrender.com/api/v1/presione1/campanhas/{id}/estadisticas
```

**Retorna:**
```json
{
  "total_llamadas": 1000,
  "llamadas_contestadas": 450,
  "presionaron_1": 89,
  "transferidas_exitosas": 75,
  "tasa_conversion": 7.5,
  "duracion_promedio": 35,
  "llamadas_voicemail": 120,
  "eficiencia_campana": 8.9
}
```

### **Relatório Histórico:**
```http
GET https://discador.onrender.com/api/v1/llamadas/historico?fecha_inicio=2025-01-01&fecha_fin=2025-01-31
```

### **Exportar para CSV:**
```http
GET https://discador.onrender.com/api/v1/reportes/exportar-csv?campanha_id=1&formato=detallado
```

---

## **8. 🎮 CONTROLES DA CAMPANHA**

### **⏸️ Pausar Campanha:**
```http
POST https://discador.onrender.com/api/v1/presione1/campanhas/{id}/pausar
```

### **▶️ Retomar Campanha:**
```http
POST https://discador.onrender.com/api/v1/presione1/campanhas/{id}/retomar
```

### **⏹️ Parar Campanha:**
```http
POST https://discador.onrender.com/api/v1/presione1/campanhas/{id}/parar
```

### **📊 Status da Campanha:**
```http
GET https://discador.onrender.com/api/v1/presione1/campanhas/{id}
```

---

## **9. 🔧 CONFIGURAÇÕES AVANÇADAS**

### **Detecção de Voicemail:**
```json
{
  "detectar_voicemail": true,
  "mensaje_voicemail_url": "/sounds/voicemail.wav",
  "duracion_maxima_voicemail": 30
}
```

### **Horários de Funcionamento:**
```json
{
  "start_time": "09:00",
  "end_time": "18:00",
  "timezone": "America/Sao_Paulo",
  "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"]
}
```

### **Limites e Performance:**
```json
{
  "max_concurrent_calls": 10,
  "cps": 5,
  "sleep_time": 1,
  "wait_time": 0.5,
  "max_attempts": 3,
  "retry_interval": 30
}
```

---

## **10. 📱 FLUXO COMPLETO DE USO**

### **Passo a Passo:**
```
1. 📂 Upload da lista de números ✅
2. 🎯 Criar campanha com configurações
3. 🎵 Configurar áudios (principal + voicemail)
4. ⚙️ Definir horários e limites
5. 🚀 Iniciar campanha
6. 📊 Monitorar em tempo real
7. 🎙️ Acessar gravações
8. 📈 Gerar relatórios
9. 🎮 Controlar execução (pausar/retomar)
10. 📋 Exportar resultados
```

---

## **🔗 LINKS ÚTEIS:**

- **🌐 Frontend:** https://discador.vercel.app/
- **🔧 API Backend:** https://discador.onrender.com/
- **📚 Documentação:** https://discador.onrender.com/docs
- **📊 Swagger UI:** https://discador.onrender.com/redoc

---

## **🎯 PRÓXIMOS PASSOS:**

1. **✅ Upload funcionando** (Slackall.txt pronto)
2. **🎯 Criar primeira campanha**
3. **🎵 Configurar áudios**
4. **🚀 Iniciar ligações**
5. **📊 Monitorar resultados**

**Sistema 100% operacional e pronto para uso!** 🚀 