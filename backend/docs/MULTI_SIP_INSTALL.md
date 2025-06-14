# 🔌 **SISTEMA MULTI-SIP - GUIA COMPLETO**

## 📋 **VISÃO GERAL**

O **Sistema Multi-SIP** é um módulo avançado para gestão de múltiplos provedores VoIP com seleção inteligente, roteamento dinâmico e monitoramento em tempo real.

## 🎯 **FUNCIONALIDADES PRINCIPAIS**

### 🔗 **Integração Multi-SIP**
- ✅ Suporte a múltiplos provedores (Twilio, GoTrunk, Asterisk, Custom)
- ✅ Autenticação SIP completa
- ✅ Teste automático de conectividade

### 📞 **Roteamento Dinâmico**
- ✅ Seleção baseada em prefixo geográfico
- ✅ Failover automático inteligente
- ✅ Balanceamento de carga

### 💸 **Gestão de Tarifas**
- ✅ Tarifas específicas por provedor e destino
- ✅ Cálculo de custo estimado em tempo real
- ✅ Suporte a múltiplas moedas

### 🧠 **Seleção Inteligente**
- ✅ **MENOR_CUSTO**: Otimização financeira
- ✅ **MELHOR_QUALIDADE**: Prioriza taxa de sucesso
- ✅ **INTELIGENTE**: Combina custo, qualidade e latência

## 🚀 **INSTALAÇÃO**

### 1️⃣ **Aplicar Migração do Banco**
```bash
cd backend
psql -U seu_usuario -d sua_base_dados -f migrations/create_multi_sip_tables.sql
```

### 2️⃣ **Configurar AGI no Asterisk**
```bash
# Copiar script AGI
sudo cp asterisk_integration/multi_sip_agi.py /var/lib/asterisk/agi-bin/
sudo chmod +x /var/lib/asterisk/agi-bin/multi_sip_agi.py
sudo chown asterisk:asterisk /var/lib/asterisk/agi-bin/multi_sip_agi.py
```

### 3️⃣ **Configurar Dialplan**
```ini
[multi-sip-outbound]
exten => _X.,1,Verbose(1,Iniciando seleção Multi-SIP para ${EXTEN})
exten => _X.,n,Set(CAMPANHA_ID=${CHANNEL(CAMPANHA_ID)})
exten => _X.,n,AGI(multi_sip_agi.py)
exten => _X.,n,GotoIf($["${MULTISIP_SUCCESS}" = "1"]?dial:error)
exten => _X.,n(dial),Dial(${MULTISIP_DIAL_STRING},30,tT)
exten => _X.,n,Goto(hangup)
exten => _X.,n(error),Playtone(congestion)
exten => _X.,n(hangup),Hangup()
```

## 🎛️ **USO BÁSICO**

### 1️⃣ **Cadastrar Provedor**
```bash
curl -X POST "http://localhost:8000/api/multi-sip/provedores" \
-H "Content-Type: application/json" \
-d '{
  "nome": "Provedor Twilio",
  "codigo": "TWILIO_PROD",
  "tipo_provedor": "twilio",
  "servidor_sip": "sip.twilio.com",
  "porta_sip": 5061,
  "usuario_sip": "seu_usuario",
  "senha_sip": "sua_senha",
  "prioridade": 1,
  "custo_base_por_minuto": 0.015
}'
```

### 2️⃣ **Configurar Tarifas**
```bash
curl -X POST "http://localhost:8000/api/multi-sip/provedores/1/tarifas" \
-H "Content-Type: application/json" \
-d '{
  "pais_codigo": "BR",
  "prefixo": "55",
  "descricao_destino": "Brasil - Nacional",
  "tipo_ligacao": "fixo",
  "custo_por_minuto": 0.008
}'
```

### 3️⃣ **Selecionar Provedor**
```bash
curl -X POST "http://localhost:8000/api/multi-sip/selecionar-provedor" \
-H "Content-Type: application/json" \
-d '{
  "numero_destino": "5511999887766",
  "metodo_selecao": "inteligente"
}'
```

## 📊 **MONITORAMENTO**

### Status dos Provedores
```bash
curl "http://localhost:8000/api/multi-sip/status-provedores"
```

### Logs de Seleção
```bash
curl "http://localhost:8000/api/multi-sip/logs-selecao?limit=100"
```

### Estatísticas Gerais
```bash
curl "http://localhost:8000/api/multi-sip/estatisticas/geral?periodo_dias=7"
```

## 🔧 **ALGORITMOS DE SELEÇÃO**

### MENOR_CUSTO
Prioriza sempre o menor custo por minuto.

### MELHOR_QUALIDADE  
Prioriza provedores com maior taxa de sucesso histórica.

### INTELIGENTE (Recomendado)
Combina múltiplos fatores:
- **40%** Custo
- **40%** Qualidade (taxa de sucesso)
- **20%** Latência

## 🚨 **TROUBLESHOOTING**

### Problema: "Nenhum provedor disponível"
```bash
# Verificar provedores ativos
curl "http://localhost:8000/api/multi-sip/provedores?activo=true"

# Ativar provedor
curl -X PUT "http://localhost:8000/api/multi-sip/provedores/1" \
-d '{"status": "ativo", "activo": true}'
```

### Problema: AGI não funciona
```bash
# Verificar logs
sudo tail -f /var/log/asterisk/multi_sip_agi.log

# Testar AGI
sudo -u asterisk python3 /var/lib/asterisk/agi-bin/multi_sip_agi.py
```

## 📈 **ENDPOINTS DA API**

### Provedores
- `POST /api/multi-sip/provedores` - Criar provedor
- `GET /api/multi-sip/provedores` - Listar provedores
- `GET /api/multi-sip/provedores/{id}` - Obter provedor
- `PUT /api/multi-sip/provedores/{id}` - Atualizar provedor

### Tarifas
- `POST /api/multi-sip/provedores/{id}/tarifas` - Criar tarifa
- `GET /api/multi-sip/provedores/{id}/tarifas` - Listar tarifas

### Seleção
- `POST /api/multi-sip/selecionar-provedor` - Selecionar provedor
- `POST /api/multi-sip/selecionar-provedor/resultado` - Registrar resultado

### Monitoramento
- `GET /api/multi-sip/status-provedores` - Status dos provedores
- `GET /api/multi-sip/logs-selecao` - Logs de seleção
- `GET /api/multi-sip/estatisticas/geral` - Estatísticas gerais

## 🔐 **SEGURANÇA**

- ✅ Senhas SIP criptografadas
- ✅ Logs imutáveis de auditoria
- ✅ Validação de entrada rigorosa
- ✅ Controle de acesso por IP

---

**© 2025 Sistema Multi-SIP - Seleção Inteligente de Provedores VoIP** 🚀
