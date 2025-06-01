# 🚀 TUTORIAL COMPLETO - CONFIGURAÇÃO SUPABASE

## Configuração do banco de dados em produção para o Discador Preditivo

---

## 📋 ETAPA 1: CRIAR PROJETO SUPABASE

### 1.1 Acessar o Dashboard
1. Visite: **https://app.supabase.com/**
2. Faça login ou crie uma conta
3. Clique em **"New Project"**

### 1.2 Configurar Projeto
```
Nome: Discador Preditivo
Organização: [Sua organização]
Região: South America (São Paulo) 
Senha do BD: [ANOTE ESTA SENHA!]
```

⚠️ **IMPORTANTE**: Guarde a senha do banco de dados em local seguro!

---

## 📋 ETAPA 2: EXECUTAR MIGRAÇÃO SQL

### 2.1 Abrir SQL Editor
1. No dashboard do Supabase, vá em **"SQL Editor"**
2. Clique em **"New query"**

### 2.2 Executar Migração
1. Copie o conteúdo completo do arquivo `supabase_migration.sql`
2. Cole no editor SQL
3. Clique em **"Run"**

### 2.3 Verificar Tabelas Criadas
Você deve ver as seguintes tabelas criadas:
- ✅ `users` (usuários do sistema)
- ✅ `campaigns` (campanhas de discagem)
- ✅ `contacts` (lista de contatos)
- ✅ `blacklist` (números bloqueados)
- ✅ `call_logs` (logs de chamadas)

---

## 📋 ETAPA 3: CONFIGURAR AUTENTICAÇÃO

### 3.1 URLs de Configuração
1. Vá em **Authentication > URL Configuration**
2. Configure:

```
Site URL: https://discador.vercel.app
Redirect URLs:
- https://discador.vercel.app/auth/callback
- http://localhost:3000/auth/callback
```

### 3.2 Habilitar Providers (Opcional)
- Email/Password: ✅ (já habilitado)
- Google OAuth: Configure se necessário

---

## 📋 ETAPA 4: OBTER CHAVES DA API

### 4.1 Acessar Configurações
1. Vá em **Project Settings > API**
2. Anote as seguintes informações:

```
Project URL: https://[PROJECT_ID].supabase.co
anon (public): eyJhbGci...
service_role (secret): eyJhbGci...
```

⚠️ **NUNCA** exponha a `service_role` key no frontend!

---

## 📋 ETAPA 5: CONFIGURAR VARIÁVEIS DE AMBIENTE

### 5.1 Executar Configuração Automática
```bash
python configurar_supabase.py configure \
  "https://[PROJECT_ID].supabase.co" \
  "eyJhbGci...[ANON_KEY]" \
  "eyJhbGci...[SERVICE_ROLE_KEY]"
```

### 5.2 Atualizar Senha do Banco
Edite o arquivo `config.production.env`:
```env
DATABASE_URL=postgresql://postgres:[SUA_SENHA]@db.[PROJECT_ID].supabase.co:5432/postgres
```

---

## 📋 ETAPA 6: DEPLOY E TESTES

### 6.1 Testar Conexão Local
```bash
python configurar_supabase.py test
```

### 6.2 Atualizar Railway (Backend)
1. Vá no dashboard do Railway
2. Atualize as variáveis de ambiente:
```env
DATABASE_URL=postgresql://postgres:[SENHA]@db.[PROJECT_ID].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT_ID].supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
```

### 6.3 Atualizar Vercel (Frontend) 
1. Vá no dashboard do Vercel
2. Atualize as variáveis de ambiente:
```env
REACT_APP_SUPABASE_URL=https://[PROJECT_ID].supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGci...
```

---

## 📋 ETAPA 7: VERIFICAR FUNCIONAMENTO

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

### 7.3 Verificar Dashboard
- ✅ Dados reais do PostgreSQL
- ✅ Campanhas funcionando
- ✅ Upload de listas operacional
- ✅ Blacklist integrada

---

## 🔧 COMANDOS ÚTEIS

### Verificar Status
```bash
# Testar conexão
python configurar_supabase.py test

# Ver logs do Railway
railway logs

# Ver status do Vercel  
vercel logs
```

### SQL Úteis no Supabase
```sql
-- Ver usuários
SELECT * FROM users;

-- Ver campanhas
SELECT * FROM campaigns;

-- Ver estatísticas
SELECT * FROM campaign_stats;

-- Verificar RLS
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public';
```

---

## 🎯 CHECKLIST DE VERIFICAÇÃO

- [ ] Projeto Supabase criado
- [ ] Migração SQL executada (5 tabelas)
- [ ] Autenticação configurada
- [ ] Chaves API obtidas
- [ ] Variáveis de ambiente configuradas
- [ ] Backend Railway atualizado
- [ ] Frontend Vercel atualizado
- [ ] Conexão testada
- [ ] Login funcionando
- [ ] Dashboard com dados reais

---

## 🚨 RESOLUÇÃO DE PROBLEMAS

### Erro de Conexão
```bash
# Verificar configuração
cat config.production.env

# Testar conexão manual
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:[SENHA]@db.[PROJECT_ID].supabase.co:5432/postgres')
print('✅ Conexão OK')
"
```

### Erro de Autenticação
1. Verificar URLs de redirect no Supabase
2. Conferir chaves de API
3. Verificar CORS no backend

### Dados não Aparecem
1. Verificar RLS policies
2. Conferir permissões de usuário
3. Ver logs do backend

---

## 🎉 RESULTADO FINAL

Após seguir este tutorial, você terá:

✅ **Sistema 100% funcional** com banco PostgreSQL  
✅ **5 tabelas** com dados reais  
✅ **Autenticação** segura e funcional  
✅ **Dashboard** alimentado por dados reais  
✅ **Deploy completo** em produção  
✅ **84% do MVP** concluído  

**Próxima etapa**: Integração VoIP para chamadas reais! 📞 