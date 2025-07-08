# 🚀 INÍCIO RÁPIDO - SISTEMA DISCADOR PREDITIVO

> Comece a usar o sistema em 5 minutos! Guia passo a passo para sua primeira experiência.

## 🌍 IDIOMAS

- 🇧🇷 **Português**: [INICIO_RAPIDO.md](INICIO_RAPIDO.md) (este arquivo)
- 🇦🇷 **Español Argentino**: [INICIO_RAPIDO-ES.md](INICIO_RAPIDO-ES.md)

## ⚡ ACESSO IMEDIATO

### 🌐 Links Diretos
- **Sistema**: https://discador.vercel.app/
- **API**: https://discador.onrender.com/
- **Documentação**: https://discador.onrender.com/documentacion

### 🔑 Login Rápido
```
Usuário: admin
Senha: admin123
```

## 📋 PRIMEIROS PASSOS (5 minutos)

### 1️⃣ Fazer Login
1. Acesse https://discador.vercel.app/
2. Digite: `admin` / `admin123`
3. Clique em "Entrar"

### 2️⃣ Explorar Dashboard
- 📊 **Dashboard**: Visão geral do sistema
- 📞 **Campanhas**: Gerenciar campanhas ativas
- 👥 **Contatos**: Visualizar listas de contatos
- ⛔ **Blacklist**: Números bloqueados

### 3️⃣ Primeira Campanha
1. Vá em **"Gestão de Campanhas"**
2. A campanha "Campanha Principal" já está criada
3. Visualize os **8 contatos** de teste incluídos
4. Configure horários se necessário

### 4️⃣ Monitoramento
1. Acesse **"Monitor de Chamadas"**
2. Visualize estatísticas em tempo real
3. Acompanhe status das chamadas

## 🎯 FUNCIONALIDADES PRINCIPAIS

### 📊 Dashboard Profissional
- Estatísticas em tempo real
- Gráficos de performance
- Alertas e notificações

### 📞 Sistema de Discado
- Discado preditivo automático
- Detecção de voicemail
- Sistema "Presione 1"
- Rotação de CLIs

### 👥 Gestão de Listas
- Upload de contatos CSV
- Validação automática
- Controle de tentativas

### ⛔ Controle de Bloqueios
- Blacklist personalizada
- Integração DNC
- Validação em tempo real

## 🛠️ CONFIGURAÇÕES BÁSICAS

### ⚙️ Configuração Avançada
1. Acesse **"Configuração Avançada"**
2. Configure **Provedores SIP**
3. Ajuste **CLIs disponíveis**
4. Configure **Contextos de áudio**

### 📁 Upload de Listas
1. Vá em **"Upload de Listas"**
2. Prepare arquivo CSV com colunas:
   ```
   phone_number,name
   +5511999887766,João Silva
   +5511888776655,Maria Santos
   ```
3. Faça upload e aguarde processamento

## 📞 USUÁRIOS DISPONÍVEIS

| Usuário    | Senha         | Acesso                    |
|------------|---------------|---------------------------|
| admin      | admin123      | Completo (recomendado)    |
| supervisor | supervisor123 | Campanhas e relatórios    |
| operador   | operador123   | Apenas monitoramento      |

## 🔧 CONFIGURAÇÃO ASTERISK (Opcional)

Se você tem Asterisk instalado:

### 1. Copiar Arquivos
```bash
cp asterisk_integration/extensions_discador.conf /etc/asterisk/
cp asterisk_integration/cli_rotation_agi.py /var/lib/asterisk/agi-bin/
chmod +x /var/lib/asterisk/agi-bin/cli_rotation_agi.py
```

### 2. Incluir no Dialplan
```
# No arquivo /etc/asterisk/extensions.conf
#include "extensions_discador.conf"
```

### 3. Recarregar
```bash
asterisk -rx "dialplan reload"
```

## 📊 DADOS DE TESTE INCLUÍDOS

O sistema já vem com:
- ✅ **3 usuários** configurados
- ✅ **1 campanha** ativa
- ✅ **8 contatos** de teste
- ✅ **5 números** na blacklist
- ✅ **Configurações** padrão

## 🚨 DICAS IMPORTANTES

### ✅ DO
- Use o usuário **admin** para configuração inicial
- Teste com os contatos incluídos primeiro
- Configure horários de funcionamento
- Monitore performance regularmente

### ❌ NÃO FAÇA
- Não delete a campanha principal inicialmente
- Não altere configurações sem backup
- Não use em produção sem testes
- Não compartilhe credenciais de admin

## 🆘 RESOLUÇÃO DE PROBLEMAS

### 🔧 Problemas Comuns

**Login não funciona:**
- Verifique usuário/senha
- Aguarde alguns segundos
- Recarregue a página

**Dados não carregam:**
- Verifique conexão internet
- Backend pode estar reiniciando (aguarde 1-2 min)

**Upload falha:**
- Verifique formato CSV
- Máximo 1000 contatos por vez
- Colunas obrigatórias: phone_number, name

## 📞 PRÓXIMOS PASSOS

1. **Familiarize-se** com a interface
2. **Teste** com dados incluídos
3. **Configure** seus provedores SIP
4. **Importe** suas listas reais
5. **Inicie** sua primeira campanha

## 🎉 PRONTO PARA USAR!

O sistema está **100% configurado** e pronto para uso imediato. Comece explorando o dashboard e teste as funcionalidades com os dados incluídos.

---

**💡 Dica**: Mantenha este guia aberto durante os primeiros usos para referência rápida. 