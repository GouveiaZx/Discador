# 🛡️ SOLUÇÃO PARA ERRO DE CSP NO VERCEL

## 📋 PROBLEMA IDENTIFICADO

### Erro Reportado:
```
Refused to load the script '<URL>' because it violates the following Content Security Policy directive: "script-src 'self' 'wasm-unsafe-eval' 'inline-speculation-rules' <URL>". Note that 'script-src-elem' was not explicitly set, so 'script-src' is used as a fallback.
```

### 🔍 Análise do Problema:
- **Causa**: O Vercel aplica uma política de Content Security Policy (CSP) restritiva por padrão
- **Impacto**: Scripts necessários para o funcionamento da aplicação React/Vite são bloqueados
- **Sintoma**: Aplicação não carrega corretamente em produção no Vercel

## 🔧 SOLUÇÃO IMPLEMENTADA

### 1. Configuração de Headers CSP no vercel.json

Adicionamos uma configuração específica de CSP no arquivo `vercel.json` que permite:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://vercel.live https://*.vercel.app; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://discador.onrender.com https://*.supabase.co wss://*.supabase.co; frame-src 'self'; object-src 'none'; base-uri 'self';"
        }
      ]
    }
  ]
}
```

### 2. Explicação das Diretivas CSP:

- **`default-src 'self'`**: Permite recursos apenas do mesmo domínio por padrão
- **`script-src 'self' 'unsafe-inline' 'unsafe-eval'`**: Permite scripts do próprio domínio, inline e eval (necessário para Vite/React)
- **`style-src 'self' 'unsafe-inline'`**: Permite estilos do próprio domínio e inline
- **`connect-src`**: Permite conexões com:
  - `'self'`: Próprio domínio
  - `https://discador.onrender.com`: Backend da aplicação
  - `https://*.supabase.co`: Banco de dados Supabase
  - `wss://*.supabase.co`: WebSocket do Supabase
- **`img-src 'self' data: https:`**: Permite imagens do próprio domínio, data URLs e HTTPS
- **`font-src 'self' data:`**: Permite fontes do próprio domínio e data URLs

### 3. Headers de Segurança Adicionais:

```json
{
  "key": "X-Frame-Options",
  "value": "DENY"
},
{
  "key": "X-Content-Type-Options",
  "value": "nosniff"
},
{
  "key": "Referrer-Policy",
  "value": "strict-origin-when-cross-origin"
}
```

## ✅ RESULTADO ESPERADO

Após a implementação desta solução:

1. **Scripts carregam corretamente**: Não há mais bloqueios de CSP
2. **Aplicação funciona**: React/Vite executa normalmente
3. **APIs funcionam**: Conexões com backend e Supabase permitidas
4. **Segurança mantida**: CSP ainda protege contra ataques XSS

## 🚀 DEPLOY

Para aplicar as mudanças:

1. **Commit das alterações**:
   ```bash
   git add frontend/vercel.json
   git commit -m "fix: Adicionar configuração CSP para resolver erro de carregamento de scripts"
   git push
   ```

2. **Deploy automático**: O Vercel detectará as mudanças e fará o deploy automaticamente

3. **Verificação**: Acessar a aplicação e verificar se não há mais erros de CSP no console

## 🔍 MONITORAMENTO

### Como verificar se a solução funcionou:

1. **Console do navegador**: Não deve haver mais erros de CSP
2. **Network tab**: Scripts devem carregar com status 200
3. **Aplicação**: Deve funcionar normalmente

### Logs esperados após correção:
```
✅ Scripts carregados com sucesso
✅ Conexão com backend estabelecida
✅ Dashboard carregando dados corretamente
```

## 📚 REFERÊNCIAS

- [Vercel Headers Configuration](https://vercel.com/docs/projects/project-configuration#headers)
- [Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [Vite Security Considerations](https://vitejs.dev/guide/build.html#browser-compatibility)

---

**Nota**: Esta configuração balanceia segurança e funcionalidade, permitindo que a aplicação React/Vite funcione corretamente enquanto mantém proteções essenciais contra ataques XSS e outros vetores de segurança.