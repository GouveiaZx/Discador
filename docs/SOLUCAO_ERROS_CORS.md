# Solução para Erros CORS

## Problema Identificado

Os erros que você encontrou são relacionados à política CORS (Cross-Origin Resource Sharing) entre o frontend hospedado no Vercel (`discador.vercel.app`) e o backend no Render (`discador.onrender.com`).

## Erros Encontrados

### 1. Erro CORS Principal
```
Access to fetch at 'https://discador.onrender.com/api/v1/presione1/campanhas' 
from origin 'https://discador.vercel.app' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Causa**: O backend não estava configurado para aceitar requisições do domínio `discador.vercel.app`.

### 2. Erro de Carregamento de Recurso
```
discador.onrender.com/api/v1/presione1/campanhas:1 Failed to load resource: net::ERR_FAILED
```

**Causa**: Falha na conexão com o backend, possivelmente devido ao erro CORS ou problemas de rede.

### 3. Erro de API no Frontend
```
❌ API Error: Object
❌ [CampaignContext] Erro ao buscar campanhas: TypeError: Failed to fetch
```

**Causa**: O frontend não conseguiu completar a requisição devido aos erros anteriores.

## Solução Implementada

### 1. Atualização do arquivo `.env`
Adicionamos `https://discador.vercel.app` às origens permitidas:
```env
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","https://discador-frontend.vercel.app","https://discador.vercel.app"]
```

### 2. Modificação do `main.py`
O código agora carrega as configurações CORS do arquivo `.env` dinamicamente:
```python
# Carregar origens permitidas do arquivo .env
import ast
cors_origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:5173","https://discador.vercel.app"]')
try:
    cors_origins = ast.literal_eval(cors_origins_str)
except:
    cors_origins = ["http://localhost:3000", "http://localhost:5173", "https://discador.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)
```

## Para Futuros Deploys

### 1. Configuração no Render
Certifique-se de que as variáveis de ambiente estão configuradas corretamente:
- `CORS_ORIGINS`: Lista dos domínios permitidos
- Outras variáveis necessárias do arquivo `.env`

### 2. Configuração no Vercel
Verifique se o frontend está apontando para a URL correta do backend:
- URL da API: `https://discador.onrender.com/api/v1`

### 3. Teste de CORS
Para testar se o CORS está funcionando:
```bash
curl -H "Origin: https://discador.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://discador.onrender.com/api/v1/presione1/campanhas
```

### 4. Monitoramento
Verifique os logs do Render para confirmar que:
- O servidor está iniciando corretamente
- As configurações CORS estão sendo carregadas
- Não há erros de dependências

## Configurações Recomendadas

### Para Produção
```env
CORS_ORIGINS=["https://discador.vercel.app","https://seu-dominio-personalizado.com"]
DEBUG=false
```

### Para Desenvolvimento
```env
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","https://discador.vercel.app"]
DEBUG=true
```

## Verificação Final

Após o deploy, verifique:
1. ✅ Backend responde corretamente
2. ✅ Headers CORS estão presentes
3. ✅ Frontend consegue fazer requisições
4. ✅ Dados são carregados corretamente

## Comandos Úteis

### Verificar Headers CORS
```bash
curl -I https://discador.onrender.com/api/v1/presione1/campanhas
```

### Testar Endpoint
```bash
curl https://discador.onrender.com/api/v1/presione1/campanhas
```

Com essas configurações, o erro CORS deve ser resolvido e o frontend poderá se comunicar corretamente com o backend.