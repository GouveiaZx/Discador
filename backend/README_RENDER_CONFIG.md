# 🚀 CONFIGURAÇÃO DO RENDER.COM

## ⚠️ PROBLEMA IDENTIFICADO
O frontend não consegue acessar o backend devido a erro de CORS:
- **Erro**: `Access to fetch at 'https://discador.onrender.com/api/v1/campaigns' from origin 'https://discador.vercel.app' has been blocked by CORS policy`
- **Causa**: Variável `CORS_ORIGINS` não configurada no ambiente de produção do Render.com

## 🔧 CONFIGURAÇÃO NECESSÁRIA

### 1. Acessar Dashboard do Render
- Ir para https://dashboard.render.com
- Selecionar o serviço "discador" 

### 2. Configurar Environment Variables
Adicionar as seguintes variáveis na seção **Environment**:

**⚠️ IMPORTANTE: A variável CORS_ORIGINS é CRÍTICA para resolver o erro de CORS!**

```
SUPABASE_URL=https://orxxocptgaeoyrtlxwkv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjVzdbZcnlN_jiT1mNijqWEWylVrhdQ
CORS_ORIGINS=["https://discador.vercel.app","https://discador-frontend.vercel.app"]
DEBUG=false
HOST=0.0.0.0
PUERTO=8000
```

### 3. Trigger Manual Deploy
Após configurar as variáveis, fazer deploy manual para aplicar as mudanças.

## 📊 TESTE DE VERIFICAÇÃO
Após a configuração, testar:

### 1. Teste básico da API
```bash
curl https://discador.onrender.com/api/v1/campaigns
```
Deve retornar:
- **Status**: 200
- **Total**: 4 campanhas
- **Contatos**: 704.236 total

### 2. Teste específico de CORS (NOVO)
```bash
curl -X GET "https://discador.onrender.com/api/v1/cors-test" \
  -H "Origin: https://discador.vercel.app" \
  -H "Accept: application/json" \
  -v
```
Deve retornar status 200 e mostrar headers `Access-Control-Allow-Origin`.

### 3. Teste de OPTIONS para CORS
```bash
curl -X OPTIONS "https://discador.onrender.com/api/v1/campaigns" \
  -H "Origin: https://discador.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -v
```
Deve retornar headers CORS corretos.

## 🎯 RESULTADO ESPERADO
✅ Frontend no Vercel vai conectar ao backend corretamente
✅ Campanhas serão exibidas com contagens corretas
✅ Sistema totalmente funcional