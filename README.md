# 🎯 SISTEMA DISCADOR PREDITIVO

> Sistema completo de discado preditivo com interface web moderna, backend robusto e integração com Asterisk.

## 🌍 IDIOMAS / LANGUAGES / IDIOMAS

- 🇧🇷 **Português**: [README.md](README.md) (este arquivo)
- 🇦🇷 **Español Argentino**: [README-ES.md](README-ES.md)
- 🇺🇸 **English**: [README-EN.md](README-EN.md) *(em breve)*

## 🌟 CARACTERÍSTICAS PRINCIPAIS

- **Frontend Moderno**: Interface React com design profissional
- **Backend Robusto**: API FastAPI com autenticação JWT
- **Banco de Dados**: PostgreSQL/Supabase com RLS
- **Integração Asterisk**: Dialplan completo e scripts AGI
- **Monitoramento**: Dashboard em tempo real
- **Gestão Completa**: Campanhas, listas, blacklist, DNC

## 🌐 LINKS DO SISTEMA

- **🖥️ Frontend**: https://discador.vercel.app/
- **🔧 Backend**: https://discador.onrender.com/
- **📚 Documentação**: https://discador.onrender.com/documentacion

## 🔑 USUÁRIOS DE TESTE

| Usuário     | Senha         | Permissões                    |
|-------------|---------------|-------------------------------|
| admin       | admin123      | Acesso completo               |
| supervisor  | supervisor123 | Campanhas e relatórios        |
| operador    | operador123   | Monitoramento                 |

## 📁 ESTRUTURA DO PROJETO

```
Discador-main/
├── 🎨 frontend/              # Interface React + Vite
├── ⚙️ backend/               # API FastAPI + Pydantic v2
├── 📞 asterisk_integration/  # Configurações Asterisk + AGI
├── 📚 docs/                  # Documentação específica
├── 🗄️ database/              # Scripts de banco
├── 🔄 migrations/            # Migrações SQL
├── 📋 README_SISTEMA_COMPLETO.md  # Documentação completa
└── 🚀 INICIO_RAPIDO.md       # Guia de início rápido
```

## ⚡ INÍCIO RÁPIDO

### 1. Acesso Imediato
```
🌐 https://discador.vercel.app/
👤 admin / admin123
```

### 2. Primeiro Uso (5 minutos)
1. **Login** → Dashboard principal
2. **Campanhas** → Visualizar campanha de teste
3. **Contatos** → 8 contatos incluídos
4. **Monitor** → Estatísticas em tempo real

📖 **Guia completo**: `INICIO_RAPIDO.md`

## 🛠️ INSTALAÇÃO COMPLETA

### Frontend (Vercel)
```bash
cd frontend
npm install
npm run build
# Deploy automático via GitHub
```

### Backend (Render.com)
```bash
cd backend
pip install -r requirements.txt
python main.py
# Deploy automático via GitHub
```

### Asterisk (Opcional)
```bash
cp asterisk_integration/* /etc/asterisk/
asterisk -rx "dialplan reload"
```

## 🚀 FUNCIONALIDADES

### 📊 Dashboard Profissional
- Estatísticas em tempo real
- Gráficos de performance
- Alertas e notificações
- Monitoramento de chamadas

### 📞 Discado Preditivo
- Algoritmo inteligente de predição
- Detecção automática de voicemail (AMD)
- Sistema "Presione 1" completo
- Rotação inteligente de CLIs
- Balanceamento de carga

### 👥 Gestão de Campanhas
- Criação e edição de campanhas
- Upload de listas CSV (até 1000 contatos)
- Configuração de horários de funcionamento
- Controle de tentativas e intervalos
- Relatórios detalhados de performance

### ⛔ Blacklist e DNC
- Lista de números bloqueados
- Integração com DNC nacional
- Importação/exportação de listas
- Validação automática em tempo real

### 🔊 Sistema de Áudio
- Reprodução de áudios personalizados
- Detecção de DTMF
- Transferência automática
- Gravação de chamadas

## 💻 TECNOLOGIAS

### Frontend
- **React 18** + **Vite** + **TailwindCSS**
- **Axios** para API calls
- **React Router** para navegação
- **Lucide React** para ícones

### Backend
- **FastAPI** + **Pydantic v2**
- **SQLAlchemy** + **PostgreSQL**
- **JWT** para autenticação
- **CORS** configurado

### Infraestrutura
- **Vercel** (Frontend)
- **Render.com** (Backend)
- **Supabase** (Banco de dados)
- **Asterisk** (PBX/AGI)

## 📊 DADOS INCLUÍDOS

O sistema já vem configurado com:
- ✅ **3 usuários** pré-configurados
- ✅ **1 campanha** de teste ativa
- ✅ **8 contatos** de exemplo
- ✅ **5 números** na blacklist
- ✅ **Configurações** padrão otimizadas

## 📚 DOCUMENTAÇÃO

| Arquivo | Descrição |
|---------|-----------|
| `README_SISTEMA_COMPLETO.md` | Documentação técnica completa |
| `INICIO_RAPIDO.md` | Guia de início rápido (5 min) |
| `backend/config.env.example` | Variáveis de ambiente |
| `docs/` | Documentação específica por módulo |

## 🆘 SUPORTE

### Problemas Comuns
- **Login falha**: Aguarde 1-2 min (backend reiniciando)
- **Dados não carregam**: Verifique conexão internet
- **Upload falha**: Formato CSV correto (phone_number, name)

### Contato
- 📧 Issues no GitHub
- 📋 Logs no sistema de monitoramento
- 📖 Documentação completa nos arquivos MD

## ✅ STATUS DO SISTEMA

**🎉 Sistema 100% funcional e pronto para produção**

- ✅ Frontend sem erros
- ✅ Backend com todos endpoints funcionando
- ✅ Banco de dados configurado
- ✅ Autenticação JWT implementada
- ✅ Integração Asterisk pronta
- ✅ CORS configurado
- ✅ Dados de teste incluídos

---

**🎯 Sistema Discador Preditivo v1.0.0**  
*Desenvolvido com ❤️ para operações telefônicas eficientes* 