# 🎯 SISTEMA DISCADOR PREDITIVO - DOCUMENTAÇÃO COMPLETA

## 🌍 IDIOMAS / LANGUAGES / IDIOMAS

- 🇧🇷 **Português**: [README_SISTEMA_COMPLETO.md](README_SISTEMA_COMPLETO.md) (este arquivo)
- 🇦🇷 **Español Argentino**: [README_SISTEMA_COMPLETO-ES.md](README_SISTEMA_COMPLETO-ES.md)

## 📋 VISÃO GERAL

Sistema completo de discado preditivo com interface web moderna, backend robusto e integração com Asterisk. Desenvolvido para operações de telemarketing, cobrança e pesquisas telefônicas.

## 🌐 LINKS DO SISTEMA

- **Frontend**: https://discador.vercel.app/
- **Backend API**: https://discador.onrender.com/
- **Documentação API**: https://discador.onrender.com/documentacion
- **Banco de Dados**: Supabase (projeto: orxxocptgaeoyrtlxwkv)

## 🏗️ ARQUITETURA

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FRONTEND      │    │     BACKEND     │    │   SUPABASE      │
│   (Vercel)      │◄──►│   (Render.com)  │◄──►│   (Database)    │
│   React + Vite  │    │   FastAPI       │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────►│    ASTERISK     │◄─────────────┘
                        │   (PBX/AGI)     │
                        └─────────────────┘
```

## 🚀 FUNCIONALIDADES PRINCIPAIS

### 📊 Dashboard Profissional
- Monitoramento em tempo real
- Estatísticas de campanhas
- Gráficos e métricas
- Alertas e notificações

### 📞 Discado Preditivo
- Algoritmo de predição inteligente
- Balanceamento de carga automático
- Detecção de voicemail (AMD)
- Sistema "Presione 1"

### 👥 Gestão de Campanhas
- Criação e edição de campanhas
- Upload de listas de contatos
- Configuração de horários
- Controle de tentativas

### 🔊 Sistema de Áudio Inteligente
- Reprodução de áudios personalizados
- Detecção de DTMF
- Transferência automática
- Gravação de chamadas

### ⛔ Blacklist e DNC
- Lista de números bloqueados
- Integração com DNC nacional
- Importação/exportação
- Validação automática

### 📈 Relatórios e Logs
- Histórico completo de chamadas
- Relatórios de performance
- Logs detalhados
- Exportação para CSV

## 👤 USUÁRIOS E PERMISSÕES

### 🔑 Credenciais de Acesso

| Usuário     | Senha        | Permissões                    |
|-------------|--------------|-------------------------------|
| admin       | admin123     | Acesso total ao sistema       |
| supervisor  | supervisor123| Campanhas, monitoramento      |
| operador    | operador123  | Apenas monitoramento          |

### 🛡️ Níveis de Acesso

- **Admin**: Configuração completa, usuários, sistema
- **Supervisor**: Campanhas, listas, relatórios
- **Operador**: Visualização de dados, monitoramento

## 🔧 CONFIGURAÇÃO TÉCNICA

### 📋 Variáveis de Ambiente

```bash
# BANCO DE DADOS
DATABASE_URL=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://orxxocptgaeoyrtlxwkv.supabase.co
SUPABASE_KEY=your_supabase_key

# AUTENTICAÇÃO
JWT_SECRET_KEY=sua-chave-secreta-muito-segura-aqui-2024
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=https://discador.vercel.app

# ASTERISK
ASTERISK_HOST=localhost
ASTERISK_PORT=5038
ASTERISK_USERNAME=admin
ASTERISK_PASSWORD=amp111
```

### 🗂️ Estrutura do Banco de Dados

```sql
-- Tabelas Principais
users           -- Usuários do sistema
campaigns       -- Campanhas de discado
contacts        -- Contatos das campanhas
call_logs       -- Logs de chamadas
blacklist       -- Números bloqueados
audios          -- Arquivos de áudio
trunks          -- Trunks SIP
dnc_lists       -- Listas DNC
dnc_numbers     -- Números DNC
roles           -- Roles do sistema
user_roles      -- Associação usuário-role
```

## 📞 INTEGRAÇÃO ASTERISK

### 📁 Arquivos de Configuração

1. **extensions_discador.conf** - Dialplan principal
2. **cli_rotation_agi.py** - Script AGI para rotação de CLIs
3. **Configurações SIP** - Trunks e provedores

### 🔄 Contextos do Dialplan

- `discador-outbound` - Chamadas de saída
- `discador-presione1` - Sistema Presione 1
- `discador-voicemail-detection` - Detecção de voicemail
- `discador-monitoring` - Monitoramento
- `discador-cli-rotation` - Rotação de CLIs

## 🛠️ INSTALAÇÃO E DEPLOY

### 1. Frontend (Vercel)
```bash
cd frontend
npm install
npm run build
# Deploy automático via GitHub
```

### 2. Backend (Render.com)
```bash
cd backend
pip install -r requirements.txt
python main.py
# Deploy automático via GitHub
```

### 3. Banco de Dados (Supabase)
```sql
-- Executar scripts SQL fornecidos
-- Configurar RLS (Row Level Security)
-- Configurar webhooks se necessário
```

### 4. Asterisk (Servidor Local)
```bash
# Copiar arquivos de configuração
cp asterisk_integration/* /etc/asterisk/
# Recarregar configurações
asterisk -rx "dialplan reload"
asterisk -rx "sip reload"
```

## 📊 DADOS INICIAIS

O sistema vem com dados de exemplo:

- **3 usuários** configurados
- **1 campanha** de teste
- **8 contatos** de exemplo
- **5 números** na blacklist
- **Configurações** pré-definidas

## 🔍 MONITORAMENTO

### 📈 Métricas Disponíveis

- Chamadas por minuto
- Taxa de conexão
- Tempo médio de chamada
- Distribuição por status
- Performance dos operadores

### 🚨 Alertas

- Falhas de conexão
- Limites de chamadas
- Números bloqueados
- Erros do sistema

## 🔒 SEGURANÇA

### 🛡️ Medidas Implementadas

- Autenticação JWT
- Senhas hasheadas
- CORS configurado
- Rate limiting
- Validação de dados
- Logs de auditoria

## 📚 API ENDPOINTS

### 🔑 Autenticação
- `POST /api/v1/auth/login` - Login do usuário
- `GET /api/v1/auth/me` - Dados do usuário atual

### 📊 Dashboard
- `GET /api/v1/stats` - Estatísticas gerais
- `GET /api/v1/monitoring/dashboard` - Dashboard

### 📞 Campanhas
- `GET /api/v1/campaigns` - Listar campanhas
- `POST /api/v1/campaigns` - Criar campanha
- `PUT /api/v1/campaigns/{id}` - Atualizar campanha

### 👥 Contatos
- `GET /api/v1/contacts` - Listar contatos
- `POST /api/v1/contacts/upload` - Upload de lista

### ⛔ Blacklist
- `GET /api/v1/blacklist` - Listar bloqueados
- `POST /api/v1/blacklist` - Adicionar número

## 🚀 PRÓXIMOS PASSOS

1. **Configurar Asterisk** com arquivos fornecidos
2. **Importar listas** de contatos reais
3. **Configurar provedores SIP** reais
4. **Ajustar parâmetros** de discado
5. **Treinar equipe** no uso do sistema

## 📞 SUPORTE

Para suporte técnico:
- Documentação: `/docs` no projeto
- Issues: GitHub do projeto
- Logs: Sistema de monitoramento

## 📄 LICENÇA

Sistema desenvolvido para uso comercial.
Todos os direitos reservados.

---

**🎉 Sistema Discador Preditivo - Versão 1.0.0**
*Desenvolvido com ❤️ para operações telefônicas eficientes* 