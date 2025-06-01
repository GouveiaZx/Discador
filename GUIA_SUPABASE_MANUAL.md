# 🚀 GUIA MANUAL - CONFIGURAÇÃO SUPABASE

## Configuração completa do banco PostgreSQL para o Discador Preditivo

---

## 📋 ETAPA 1: CRIAR PROJETO SUPABASE

### 1.1 Acessar Supabase
1. Vá para: **https://app.supabase.com/**
2. Faça login ou crie uma conta
3. Clique em **"New Project"**

### 1.2 Configurar Projeto
```
- Nome: Discador Preditivo
- Organização: [Sua organização]  
- Região: South America (São Paulo)
- Senha do BD: [ANOTE ESTA SENHA!]
```

⚠️ **IMPORTANTE**: Guarde a senha do banco de dados!

---

## 📋 ETAPA 2: EXECUTAR MIGRAÇÃO SQL

### 2.1 Abrir SQL Editor
1. No dashboard do Supabase, vá em **"SQL Editor"** 
2. Clique em **"New query"**

### 2.2 Executar Migração
1. Copie TODO o conteúdo do arquivo `supabase_migration.sql`
2. Cole no editor SQL do Supabase
3. Clique em **"Run"**

### 2.3 Verificar Tabelas
Após executar, você deve ver 5 tabelas criadas:
- ✅ `users` (usuários)
- ✅ `campaigns` (campanhas)
- ✅ `contacts` (contatos)  
- ✅ `blacklist` (bloqueados)
- ✅ `call_logs` (logs de chamadas)

---

## 📋 ETAPA 3: OBTER CONFIGURAÇÕES

### 3.1 Ir para Project Settings > API
No dashboard do Supabase:
1. Clique em **"Settings"** (engrenagem)
2. Vá em **"API"**
3. Anote as informações:

```
Project URL: https://[PROJECT_ID].supabase.co
anon key: eyJhbGci...
service_role key: eyJhbGci...
```

---

## 📋 ETAPA 4: CONFIGURAR AMBIENTE LOCAL

### 4.1 Criar arquivo config.production.env

Crie o arquivo `config.production.env` com o conteúdo:

```env
# CONFIGURAÇÃO SUPABASE - PRODUÇÃO
SUPABASE_URL=https://[PROJECT_ID].supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# Database URL (substitua [SENHA] e [PROJECT_ID])
DATABASE_URL=postgresql://postgres:[SENHA]@db.[PROJECT_ID].supabase.co:5432/postgres

# Configurações FastAPI
DEBUG=false
HOST=0.0.0.0
PUERTO=8000
SECRET_KEY=sua_chave_secreta_super_segura_aqui_123456789
```

### 4.2 Testar Conexão Local

```bash
# Instalar dependência (se necessário)
pip install psycopg2-binary

# Testar conexão
python -c "
import os
import psycopg2
from urllib.parse import urlparse

# Carregar do arquivo
with open('config.production.env') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

db_url = os.getenv('DATABASE_URL')
result = urlparse(db_url)
connection = psycopg2.connect(
    database=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)
cursor = connection.cursor()
cursor.execute('SELECT version();')
version = cursor.fetchone()
print('✅ Conexão PostgreSQL bem-sucedida!')
print(f'📊 Versão: {version[0][:50]}...')
connection.close()
"
```

---

## 📋 ETAPA 5: ATUALIZAR DEPLOYS

### 5.1 Railway (Backend)
1. Vá para: **https://railway.app/dashboard**
2. Selecione seu projeto backend
3. Vá em **"Variables"**
4. Atualize/adicione:

```env
DATABASE_URL=postgresql://postgres:[SENHA]@db.[PROJECT_ID].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT_ID].supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
```

### 5.2 Vercel (Frontend)
1. Vá para: **https://vercel.com/dashboard**
2. Selecione seu projeto frontend
3. Vá em **"Settings > Environment Variables"**
4. Atualize/adicione:

```env
REACT_APP_SUPABASE_URL=https://[PROJECT_ID].supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGci...
```

---

## 📋 ETAPA 6: CONFIGURAR AUTENTICAÇÃO

### 6.1 URLs de Configuração
No Supabase, vá em **Authentication > URL Configuration**:

```
Site URL: https://discador.vercel.app
Redirect URLs:
- https://discador.vercel.app/auth/callback
- http://localhost:3000/auth/callback
```

---

## 📋 ETAPA 7: TESTAR SISTEMA COMPLETO

### 7.1 Testar Backend
```bash
curl https://web-production-c192b.up.railway.app/api/v1/campaigns
```

### 7.2 Testar Frontend
1. Acesse: **https://discador.vercel.app**
2. Faça login com:
   - `admin / admin123`
   - `supervisor / super123`
   - `operador / oper123`

### 7.3 Testar Discador
```bash
# Testar endpoints do discador
curl https://web-production-c192b.up.railway.app/api/v1/discador/status
curl https://web-production-c192b.up.railway.app/api/v1/dashboard/real-stats
```

---

## 🎯 RESULTADO FINAL

Após seguir este guia, você terá:

✅ **Banco PostgreSQL** funcionando no Supabase  
✅ **5 tabelas** com dados reais  
✅ **Backend** conectado ao Supabase  
✅ **Frontend** configurado para dados reais  
✅ **Discador** integrado com banco PostgreSQL  
✅ **Deploy completo** em produção  

---

## 🚨 RESOLUÇÃO DE PROBLEMAS

### Erro de Conexão
```bash
# Verificar configuração
cat config.production.env

# Testar conexão manual
python -c "import psycopg2; conn = psycopg2.connect('postgresql://postgres:[SENHA]@db.[PROJECT_ID].supabase.co:5432/postgres'); print('✅ OK')"
```

### Erro 404 na API
- Verificar se Railway redeploy após mudança de variáveis
- Verificar logs do Railway: `railway logs`

### Dados não aparecem
- Verificar RLS policies no Supabase
- Verificar permissões de usuário
- Ver logs do backend

---

## ✅ CHECKLIST DE VERIFICAÇÃO

- [ ] Projeto Supabase criado
- [ ] Migração SQL executada (5 tabelas)
- [ ] Configurações de API copiadas
- [ ] Arquivo config.production.env criado
- [ ] Conexão local testada
- [ ] Railway atualizado
- [ ] Vercel atualizado
- [ ] URLs de autenticação configuradas
- [ ] Sistema testado end-to-end

---

## 🎉 PRÓXIMOS PASSOS

Com o Supabase configurado, você pode:

1. **Executar o discador real**: APIs prontas
2. **Monitorar chamadas**: Dashboard com dados reais  
3. **Gerenciar campanhas**: Interface completa
4. **Integrar VoIP**: Próxima etapa principal

**Sistema agora 90% completo! 🚀** 