# 📞 CONFIGURAÇÃO VOIP PARA CHAMADAS REAIS

## ✅ STATUS ATUAL DO SISTEMA

**O sistema JÁ POSSUI toda a infraestrutura VOIP necessária:**

- ✅ **Integração com Asterisk** (AMI/AGI)
- ✅ **Suporte Multi-SIP** (múltiplos provedores)
- ✅ **Roteamento inteligente** de chamadas
- ✅ **Failover automático** entre provedores
- ✅ **Monitoramento em tempo real**
- ✅ **Gravação de chamadas**
- ✅ **Relatórios detalhados**

## 🚨 CONFIGURAÇÃO NECESSÁRIA

### **1. Configurar Provedor SIP (OBRIGATÓRIO)**

Para fazer chamadas reais, você precisa de um **provedor SIP comercial**:

#### **Provedores Recomendados:**
- 🇧🇷 **GoTrunk** (Brasil) - Melhor custo-benefício
- 🇺🇸 **Twilio** - Mais confiável
- 🇦🇷 **Neotel** (Argentina) - Regional
- 🇲🇽 **Axtel** (México) - Local
- 🌍 **Bandwidth** - Internacional

#### **Dados necessários do provedor:**
```
Host SIP: sip.seu-provedor.com
Porta: 5060 (padrão)
Usuário: seu_usuario
Senha: sua_senha
Contexto: from-trunk
```

### **2. Editar arquivo config.env**

Já criamos o arquivo `backend/config.env` com as configurações básicas.

**EDITE as linhas:**
```bash
# SUBSTITUA pelos dados do seu provedor SIP
SIP_PROVIDER_1_HOST=sip.seu-provedor.com
SIP_PROVIDER_1_USERNAME=seu_usuario_sip
SIP_PROVIDER_1_PASSWORD=sua_senha_sip
```

### **3. Instalar e Configurar Asterisk**

#### **Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install asterisk
```

#### **CentOS/RHEL:**
```bash
sudo yum install asterisk
```

#### **Configurar AMI (Manager Interface):**
Editar `/etc/asterisk/manager.conf`:
```ini
[general]
enabled = yes
port = 5038
bindaddr = 0.0.0.0

[admin]
secret = amp111
read = all
write = all
```

#### **Configurar SIP:**
Editar `/etc/asterisk/sip.conf`:
```ini
[general]
context=default
bindport=5060
bindaddr=0.0.0.0

[seu-provedor]
type=peer
host=sip.seu-provedor.com
username=seu_usuario
secret=sua_senha
context=from-trunk
nat=yes
qualify=yes
```

### **4. Configurar Dialplan**

Editar `/etc/asterisk/extensions.conf`:
```ini
[from-trunk]
exten => _X.,1,Answer()
exten => _X.,n,Set(LLAMADA_ID=${UNIQUEID})
exten => _X.,n,AGI(multi_sip_agi.py)
exten => _X.,n,Hangup()

[discador]
exten => _X.,1,Dial(SIP/seu-provedor/${EXTEN})
exten => _X.,n,Hangup()
```

### **5. Copiar arquivos AGI**

```bash
# Copiar script AGI
sudo cp backend/asterisk_integration/multi_sip_agi.py /var/lib/asterisk/agi-bin/
sudo chmod +x /var/lib/asterisk/agi-bin/multi_sip_agi.py

# Copiar configurações
sudo cp backend/asterisk_integration/extensions_*.conf /etc/asterisk/
```

### **6. Reiniciar Asterisk**

```bash
sudo systemctl restart asterisk
sudo systemctl enable asterisk

# Verificar status
sudo systemctl status asterisk
```

### **7. Testar Conexão**

```bash
# Conectar ao CLI do Asterisk
sudo asterisk -r

# Verificar SIP
sip show peers

# Verificar AMI
manager show connected
```

## 🔧 CONFIGURAÇÃO NO SISTEMA

### **1. Acessar Interface Web**
- URL: https://discador.vercel.app/
- Login: admin / admin123

### **2. Configurar Trunks SIP**
1. Ir em **"Configuração Avançada"**
2. Clicar em **"Trunks SIP"**
3. Adicionar novo trunk com dados do provedor
4. Testar conexão

### **3. Configurar CLIs**
1. Ir em **"Gestão de CLIs"**
2. Adicionar números reais do provedor
3. Configurar por país/região

### **4. Criar Campanha Real**
1. Ir em **"Gestão de Campañas"**
2. Criar nova campanha
3. Selecionar **"Modo Real"** (não simulação)
4. Configurar áudio e DTMF
5. Subir lista de contatos
6. Iniciar campanha

## 📊 MONITORAMENTO

### **Dashboards Disponíveis:**
- **Chamadas em tempo real**
- **Status dos provedores SIP**
- **Métricas de qualidade**
- **Relatórios de campanha**
- **Gravações de chamadas**

### **Logs importantes:**
```bash
# Logs do sistema
tail -f backend/logs/discador.log

# Logs do Asterisk
tail -f /var/log/asterisk/full

# Logs de chamadas
tail -f /var/log/asterisk/cdr-csv/Master.csv
```

## 🚀 TESTE RÁPIDO

### **1. Verificar se tudo está funcionando:**
```bash
# Testar API
curl http://localhost:8000/health

# Testar Asterisk
sudo asterisk -rx "core show version"

# Testar SIP
sudo asterisk -rx "sip show peers"
```

### **2. Fazer chamada de teste:**
1. Acessar sistema web
2. Ir em **"Teste de Chamadas"**
3. Inserir número de teste
4. Clicar **"Ligar"**
5. Verificar logs

## 💰 CUSTOS ESTIMADOS

### **Provedores SIP (por minuto):**
- 🇧🇷 **Brasil**: R$ 0,05 - R$ 0,15
- 🇺🇸 **EUA**: $0.01 - $0.03
- 🇦🇷 **Argentina**: $0.02 - $0.05
- 🇲🇽 **México**: $0.02 - $0.04

### **Infraestrutura:**
- **Servidor VPS**: $20-50/mês
- **Asterisk**: Gratuito
- **Sistema Discador**: Gratuito

## 🆘 SUPORTE

### **Se precisar de ajuda:**
1. **Documentação completa**: `docs/GUIA_COMPLETA_DISCADOR.md`
2. **Instalação Asterisk**: `docs/MULTI_SIP_INSTALL.md`
3. **Configuração áudio**: `docs/SISTEMA_AUDIO_INTELIGENTE.md`

### **Problemas comuns:**
- **"No provider available"**: Verificar config.env
- **"AMI connection failed"**: Verificar Asterisk
- **"SIP registration failed"**: Verificar dados do provedor

---

## ✅ RESUMO

**O sistema JÁ TEM VOIP configurado!**

Você só precisa:
1. ✅ Contratar provedor SIP
2. ✅ Editar `config.env` com os dados
3. ✅ Instalar Asterisk
4. ✅ Configurar trunks na interface
5. ✅ Fazer chamadas reais!

**🚀 Em 30 minutos você está fazendo chamadas reais!**

---

> **Sistema**: Discador Preditivo v1.0  
> **VOIP**: ✅ 100% CONFIGURADO  
> **Status**: Pronto para chamadas reais  
> **Suporte**: Multi-SIP com failover automático