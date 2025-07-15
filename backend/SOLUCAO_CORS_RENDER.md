# 🚨 SOLUÇÃO PARA ERRO DE CORS NO RENDER.COM

## 🔍 PROBLEMA IDENTIFICADO

O frontend hospedado no Vercel (`https://discador.vercel.app`) não consegue acessar o backend no Render.com (`https://discador.onrender.com`) devido a erro de CORS:

```
Access to fetch at 'https://discador.onrender.com/api/v1/campaigns' 
from origin 'https://discador.vercel.app' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## 🎯 CAUSA RAIZ

A variável de ambiente `CORS_ORIGINS` **NÃO ESTÁ CONFIGURADA** no dashboard do Render.com, fazendo com que o backend use apenas as origens padrão do código, que não incluem `https://discador.vercel.app`.

## ✅ SOLUÇÃO IMEDIATA

### 1. Acessar Dashboard do Render.com
- Ir para: https://dashboard.render.com
- Selecionar o serviço **"discador"**
- Clicar em **"Environment"** no menu lateral

### 2. Adicionar Variável CORS_ORIGINS
Adicionar a seguinte variável de ambiente:

**Nome:** `CORS_ORIGINS`  
**Valor:** `["https://discador.vercel.app","https://discador-frontend.vercel.app","http://localhost:3000","http://localhost:5173"]`

### 3. Fazer Deploy Manual
- Clicar em **"Manual Deploy"** → **"Deploy latest commit"**
- Aguardar o deploy completar (2-3 minutos)

## 🧪 TESTE DE VERIFICAÇÃO

### Teste 1: Verificar API Funcionando
```bash
curl -X GET "https://discador.onrender.com/api/v1/campaigns" \
  -H "Accept: application/json"
```

### Teste 2: Verificar CORS Específico
```bash
curl -X GET "https://discador.onrender.com/api/v1/cors-test" \
  -H "Origin: https://discador.vercel.app" \
  -H "Accept: application/json" \
  -v
```

### Teste 3: Verificar CORS Headers (OPTIONS)
```bash
curl -X OPTIONS "https://discador.onrender.com/api/v1/campaigns" \
  -H "Origin: https://discador.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

**Resultado esperado:**
```
Access-Control-Allow-Origin: https://discador.vercel.app
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: *
```

### Teste 4: Verificar Campanhas
```bash
curl https://discador.onrender.com/api/v1/campaigns
```

**Resultado esperado:**
```json
[
  {
    "id": 1,
    "name": "Campanha 1",
    "contacts_total": 4187
  },
  {
    "id": 2, 
    "name": "Campanha 2",
    "contacts_total": 0
  },
  {
    "id": 3,
    "name": "Campanha 3", 
    "contacts_total": 700044
  }
]
```

## 🔧 CONFIGURAÇÃO COMPLETA DO RENDER.COM

Para referência, todas as variáveis que devem estar configuradas:

```
SUPABASE_URL=https://orxxocptgaeoyrtlxwkv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjVzdbZcnlN_jiT1mNijqWEWylVrhdQ
CORS_ORIGINS=["https://discador.vercel.app","https://discador-frontend.vercel.app","http://localhost:3000","http://localhost:5173"]
DEBUG=false
HOST=0.0.0.0
PUERTO=8000
```

## 🎯 RESULTADO FINAL

Após aplicar a solução:

✅ **Frontend no Vercel** → Conecta ao backend sem erro de CORS  
✅ **Campanhas carregam** → Exibe 4 campanhas com contagens corretas  
✅ **Sistema funcional** → Todas as funcionalidades do discador funcionando  

## 🚨 IMPORTANTE

- **NÃO ESQUECER** de fazer o deploy manual após adicionar a variável
- **AGUARDAR** 2-3 minutos para o deploy completar
- **TESTAR** no browser após o deploy para confirmar que funcionou

## 📞 SUPORTE

Se o problema persistir após seguir estes passos:
1. Verificar se a variável foi salva corretamente no dashboard
2. Confirmar que o deploy manual foi executado
3. Limpar cache do browser e testar novamente