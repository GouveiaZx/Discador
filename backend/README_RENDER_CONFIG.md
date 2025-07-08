# 🚀 CONFIGURAÇÃO DO RENDER.COM

## ⚠️ PROBLEMA IDENTIFICADO
O backend em produção está retornando 0 campanhas porque as variáveis do Supabase não estão configuradas.

## 🔧 CONFIGURAÇÃO NECESSÁRIA

### 1. Acessar Dashboard do Render
- Ir para https://dashboard.render.com
- Selecionar o serviço "discador" 

### 2. Configurar Environment Variables
Adicionar as seguintes variáveis na seção **Environment**:

```
SUPABASE_URL=https://orxxocptgaeoyrtlxwkv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjVzdbZcnlN_jiT1mNijqWEWylVrhdQ
DEBUG=false
HOST=0.0.0.0
PUERTO=8000
```

### 3. Trigger Manual Deploy
Após configurar as variáveis, fazer deploy manual para aplicar as mudanças.

## 📊 TESTE DE VERIFICAÇÃO
Após a configuração, testar:
```bash
curl https://discador.onrender.com/api/v1/campaigns
```

Deve retornar:
- **Status**: 200
- **Total**: 4 campanhas
- **Contatos**: 704.236 total

## 🎯 RESULTADO ESPERADO
✅ Frontend no Vercel vai conectar ao backend corretamente
✅ Campanhas serão exibidas com contagens corretas
✅ Sistema totalmente funcional 