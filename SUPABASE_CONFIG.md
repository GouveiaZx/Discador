# 🚀 Configuração do Supabase - Sistema Discador Preditivo

## 📋 Resumo da Configuração

O sistema foi configurado para usar o Supabase como backend principal, com as seguintes configurações:

### 🔧 Frontend (https://discador.vercel.app/)
- **URL da API**: `https://discador.onrender.com`
- **Supabase URL**: `https://orxxocptgaeoyrtlxwkv.supabase.co`
- **Supabase Anon Key**: Configurada no `.env.local`

### 🔧 Backend (https://discador.onrender.com/)
- **Supabase URL**: `https://orxxocptgaeoyrtlxwkv.supabase.co`
- **Supabase Anon Key**: Configurada no `.env`
- **Database URL**: Conexão direta com PostgreSQL do Supabase

## 📁 Arquivos Configurados

### Frontend
1. **`.env.local`** - Variáveis de ambiente para produção
2. **`src/config/api.js`** - Configuração da API atualizada
3. **`src/config/supabase.js`** - Cliente Supabase configurado
4. **`src/contexts/SupabaseAuthContext.jsx`** - Contexto de autenticação com Supabase
5. **`package.json`** - Dependência `@supabase/supabase-js` adicionada

### Backend
1. **`.env`** - Variáveis de ambiente do Supabase
2. **`app/config.py`** - Configuração principal do sistema
3. **Múltiplas rotas** - Já configuradas para usar Supabase

## 🔑 Variáveis de Ambiente

### Frontend (.env.local)
```env
# CONFIGURAÇÃO PARA PRODUÇÃO
VITE_API_URL=https://discador.onrender.com

# CONFIGURAÇÃO DO SUPABASE
VITE_SUPABASE_URL=https://orxxocptgaeoyrtlxwkv.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjVzdbZcnlN_jiT1mNijqWEWylVrhdQ

# Para desenvolvimento local, descomente a linha abaixo:
# VITE_API_URL=http://localhost:8000
```

### Backend (.env)
```env
# Configurações do Supabase
SUPABASE_URL=https://orxxocptgaeoyrtlxwkv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjVzdbZcnlN_jiT1mNijqWEWylVrhdQ

# Configurações do Banco de Dados
DATABASE_URL=postgresql://postgres.orxxocptgaeoyrtlxwkv:%21Gouveia1@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

## 🛠️ Como Usar o Supabase

### No Frontend

#### 1. Importar o cliente Supabase
```javascript
import { supabase, auth, database, storage, realtime } from '../config/supabase';
```

#### 2. Autenticação
```javascript
// Login
const { data, error } = await auth.signIn('email@example.com', 'password');

// Registro
const { data, error } = await auth.signUp('email@example.com', 'password', {
  name: 'Nome do Usuário',
  role: 'operator'
});

// Logout
const { error } = await auth.signOut();
```

#### 3. Banco de Dados
```javascript
// Inserir dados
const { data, error } = await database.insert('campanhas', {
  nome: 'Nova Campanha',
  status: 'ativa'
});

// Buscar dados
const { data, error } = await database.select('campanhas', '*', {
  status: 'ativa'
});

// Atualizar dados
const { data, error } = await database.update('campanhas', 
  { status: 'pausada' }, 
  { id: 1 }
);
```

#### 4. Realtime
```javascript
// Escutar mudanças em tempo real
const channel = realtime.subscribe('campanhas', (payload) => {
  console.log('Mudança detectada:', payload);
});

// Cancelar inscrição
realtime.unsubscribe(channel);
```

### No Backend

O backend já está configurado para usar o Supabase através das rotas existentes:

- **Campanhas**: `/api/v1/campaigns`
- **Caller ID**: `/api/v1/caller-id`
- **Trunks**: `/api/v1/trunks`
- **DNC**: `/api/v1/dnc`
- **Timing**: `/api/v1/timing`

## 🔄 Migração de Contextos

Para usar o novo contexto de autenticação do Supabase:

### Antes (AuthContext)
```javascript
import { useAuth } from '../contexts/AuthContext';
const { user, login, logout } = useAuth();
```

### Depois (SupabaseAuthContext)
```javascript
import { useSupabaseAuth } from '../contexts/SupabaseAuthContext';
const { user, signIn, signOut } = useSupabaseAuth();
```

## 🚀 Deploy

### Frontend (Vercel)
1. As variáveis de ambiente já estão configuradas no `.env.local`
2. O build irá usar automaticamente `https://discador.onrender.com` como API

### Backend (Render)
1. As variáveis de ambiente já estão configuradas no `.env`
2. O Supabase está configurado e funcionando

## ✅ Status da Configuração

- ✅ Frontend configurado para produção
- ✅ Backend configurado com Supabase
- ✅ Variáveis de ambiente definidas
- ✅ Cliente Supabase criado
- ✅ Contexto de autenticação com Supabase
- ✅ Dependências instaladas
- ✅ URLs de produção configuradas

## 🔧 Próximos Passos

1. **Testar a aplicação** em produção
2. **Configurar tabelas** no Supabase se necessário
3. **Implementar RLS** (Row Level Security) para segurança
4. **Migrar componentes** para usar o novo contexto Supabase
5. **Configurar backups** automáticos

## 📞 Suporte

Para dúvidas sobre a configuração do Supabase:
- Documentação: https://supabase.com/docs
- Dashboard: https://supabase.com/dashboard/project/orxxocptgaeoyrtlxwkv