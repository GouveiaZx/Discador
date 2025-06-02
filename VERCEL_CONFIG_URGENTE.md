# 🚀 CONFIGURAÇÃO URGENTE VERCEL - CORRIGIR URLS

## 🎯 **AÇÃO IMEDIATA NECESSÁRIA**

### 📋 **PASSO 1: Acessar Vercel Dashboard**
1. Vá para: **https://vercel.com/dashboard**
2. Faça login se necessário
3. Localize o projeto **"discador"**
4. Clique no projeto

### ⚙️ **PASSO 2: Configurar Variáveis de Ambiente**
1. Clique em **"Settings"** (no menu lateral)
2. Clique em **"Environment Variables"**
3. Localize a variável **"VITE_API_URL"**

### 🔧 **PASSO 3: Corrigir a URL**
**VALOR ATUAL (INCORRETO):**
```
VITE_API_URL = https://web-production-c192b.up.railway.app/api/v1
```

**VALOR CORRETO:**
```
VITE_API_URL = https://web-production-c192b.up.railway.app
```
**(remover `/api/v1` do final)**

### 🚀 **PASSO 4: Redeploy**
1. Salvar a variável de ambiente
2. Ir para **"Deployments"**
3. Clicar nos **3 pontos** do último deploy
4. Selecionar **"Redeploy"**
5. **OU** fazer novo commit (push automático)

## ✅ **VERIFICAÇÃO**

Após 2-3 minutos, verificar no console do browser:
- ✅ Deve aparecer log: `🔧 API Configuration`
- ✅ URLs devem estar corretas (sem `/api/v1/api/v1/`)

## 🎯 **RESULTADO ESPERADO**

**ANTES (ERRO):**
```
❌ https://web-production-c192b.up.railway.app/api/v1/api/v1/campaigns
❌ https://web-production-c192b.up.railway.app/api/v1/api/v1/blacklist
```

**DEPOIS (CORRETO):**
```
✅ https://web-production-c192b.up.railway.app/api/v1/campaigns
✅ https://web-production-c192b.up.railway.app/api/v1/blacklist
```

## 📊 **STATUS ATUAL**

- ✅ **Correção implementada** no código
- ✅ **Push realizado** para repositório
- ⏳ **Aguardando** configuração Vercel
- 🎯 **5 minutos** para resolver completamente

## 🚨 **SE AINDA PERSISTIR**

Caso o erro continue:
1. Limpar cache do browser (Ctrl+Shift+R)
2. Verificar se a variável foi salva corretamente
3. Aguardar redeploy completo (2-3 min)
4. Verificar console para logs de debug

**ESTA CONFIGURAÇÃO RESOLVE 100% DOS ERROS 404!** 