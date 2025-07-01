# 🚀 Sistema de Discador Preditivo com Detecção de Voicemail

## 📋 Visão Geral

Sistema completo de discador preditivo "Presione 1" com capacidade avançada de detecção de voicemail e reprodução automática de mensagens personalizadas.

### ✨ Características Principais

- **🎯 Discador Preditivo**: Campanhas automatizadas com detecção DTMF
- **🎙️ Detecção de Voicemail**: Algoritmos avançados para identificar correio de voz
- **📞 Integração Asterisk**: AMI completa para controle de chamadas
- **📊 Analytics em Tempo Real**: Estatísticas detalhadas e métricas
- **🔄 API RESTful**: Interface completa para gerenciamento
- **🗄️ Banco Robusto**: PostgreSQL com migrações automáticas

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Backend   │    │   Asterisk      │
│   (Opcional)    │◄──►│   FastAPI       │◄──►│   AMI/SIP       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                        ┌─────────────────┐    ┌─────────────────┐
                        │   PostgreSQL    │    │   Redis Cache   │
                        │   Database      │    │   Session       │
                        └─────────────────┘    └─────────────────┘
```

## 🚀 Instalação Rápida

### Opção 1: Instalação Automatizada (Recomendada)

```bash
# Baixar e executar instalador
chmod +x install.sh
./install.sh
```

### Opção 2: Instalação Manual

Consulte a [documentação completa de instalação](docs/INSTALACAO_SISTEMA.md).

## 📚 Documentação

### 📖 Navegação Rápida
- **[📋 ÍNDICE COMPLETO](docs/INDEX.md)** - 🎯 **COMECE AQUI** - Navegação organizada de toda a documentação
- **[📋 Instalação Completa](docs/INSTALACAO_SISTEMA.md)** - Guia passo a passo para Linux
- **[⚙️ Configuração Avançada](docs/VOICEMAIL_DETECTION.md)** - Detecção de voicemail

### 🔧 Scripts de Controle
- **`./start.sh`** - Iniciar o sistema
- **`./stop.sh`** - Parar o sistema  
- **`./status.sh`** - Verificar status
- **`./validate.sh`** - Validar instalação

### 🧪 Scripts de Teste
- **`python scripts/teste_voicemail.py`** - Teste completo do sistema
- **`python scripts/populate_sample_data.py`** - Popular dados de exemplo

## ⚡ Início Rápido

```bash
# 1. Clonar repositório
git clone https://github.com/seu-repo/discador-preditivo.git
cd discador-preditivo

# 2. Executar instalação automatizada
./install.sh

# 3. Iniciar sistema
./start.sh

# 4. Validar funcionamento
./validate.sh

# 5. Acessar documentação
open http://localhost:8000/docs
```

## 🔗 Enlaces Principais

| Componente | URL | Descrição |
|------------|-----|-----------|
| **API Docs** | http://localhost:8000/docs | Documentação interativa |
| **Health Check** | http://localhost:8000/health | Status da aplicação |
| **Métricas** | http://localhost:8000/metrics | Monitoramento |
| **Admin Panel** | http://localhost:8000/admin | Interface administrativa |

## 📊 Funcionalidades

### 🎯 Campanhas
- ✅ Criação e configuração de campanhas
- ✅ Listas de números com validação
- ✅ Agendamento e execução automática
- ✅ Pausar/retomar/parar campanhas
- ✅ Estatísticas em tempo real

### 🎙️ Detecção de Voicemail
- ✅ Algoritmos BeepDetection, SilenceDetection, TonePattern
- ✅ Reprodução automática de mensagem personalizada
- ✅ Configuração de durações mínimas/máximas
- ✅ Métricas específicas de voicemail

### 📞 Integração Asterisk
- ✅ Conexão AMI robusta com reconexão automática
- ✅ Controle completo de chamadas
- ✅ Eventos em tempo real
- ✅ Transferência para extensões/filas

### 📈 Analytics
- ✅ Dashboard em tempo real
- ✅ Estatísticas por campanha
- ✅ Métricas de conversão
- ✅ Relatórios de performance

## 🛠️ Requisitos do Sistema

### 🖥️ Hardware Mínimo
- **CPU**: 2 cores (4 recomendado)
- **RAM**: 4GB (8GB recomendado)  
- **Disco**: 20GB livre (SSD recomendado)

### 💻 Software
- **OS**: Ubuntu 20.04+ ou Debian 11+
- **Python**: 3.9+
- **PostgreSQL**: 12+
- **Redis**: 6+
- **Asterisk**: 18+

### 🌐 Rede
- **Portas**: 8000 (API), 5432 (PostgreSQL), 6379 (Redis), 5038 (AMI), 5060 (SIP)

## 📋 Variáveis de Ambiente

```bash
# Banco de Dados
DATABASE_URL=postgresql://discador:password@localhost:5432/discador_db

# Asterisk
ASTERISK_HOST=127.0.0.1
ASTERISK_PUERTO=5038
ASTERISK_USUARIO=discador_ami
ASTERISK_PASSWORD=ami_password

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=sua_chave_secreta

# Redis
REDIS_URL=redis://localhost:6379/0

# Arquivos
SOUNDS_PATH=/var/lib/asterisk/sounds/custom
```

## 🧪 Executar Testes

```bash
# Teste completo do sistema
python scripts/teste_voicemail.py

# Teste específico
python scripts/teste_voicemail.py --teste 1

# Validação da instalação
./validate.sh

# Popular dados de exemplo
python scripts/populate_sample_data.py
```

## 📊 Exemplo de Uso via API

```bash
# Criar lista de números
curl -X POST http://localhost:8000/api/v1/listas-llamadas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Lista Vendas",
    "descripcion": "Números para campanha de vendas",
    "numeros": ["+5511999999999", "+5511888888888"]
  }'

# Criar campanha com voicemail
curl -X POST http://localhost:8000/api/v1/presione1/campanhas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Campanha Vendas Q1",
    "descripcion": "Campanha primeiro trimestre",
    "lista_llamadas_id": 1,
    "mensaje_audio_url": "/var/lib/asterisk/sounds/custom/vendas.wav",
    "detectar_voicemail": true,
    "mensaje_voicemail_url": "/var/lib/asterisk/sounds/custom/vendas_vm.wav",
    "extension_transferencia": "200",
    "timeout_presione1": 10
  }'

# Iniciar campanha
curl -X POST http://localhost:8000/api/v1/presione1/campanhas/1/iniciar

# Ver estatísticas
curl http://localhost:8000/api/v1/presione1/campanhas/1/estadisticas
```

## 🔧 Comandos Úteis

```bash
# Sistema
./start.sh                    # Iniciar sistema
./stop.sh                     # Parar sistema
./status.sh                   # Ver status
./validate.sh                 # Validar sistema

# Logs
tail -f /var/log/discador/app.log    # Ver logs em tempo real
grep ERROR /var/log/discador/app.log # Ver apenas erros

# Banco de Dados
psql $DATABASE_URL                   # Conectar ao banco
python scripts/populate_sample_data.py --verificar  # Verificar dados

# Asterisk
asterisk -r                          # Console Asterisk
asterisk -rx "manager show users"    # Ver usuários AMI
```

## 🐛 Troubleshooting

### ❌ Problemas Comuns

**API não inicia**
```bash
# Verificar logs
tail -f /var/log/discador/app.log

# Verificar dependências
source venv/bin/activate
pip install -r requirements.txt
```

**Erro de conexão com banco**
```bash
# Testar conexão
psql $DATABASE_URL

# Verificar serviço
sudo systemctl status postgresql
```

**Asterisk AMI não conecta**
```bash
# Verificar configuração
sudo asterisk -rx "manager show users"

# Testar porta
telnet localhost 5038
```

### 📋 Checklist de Verificação
- [ ] Todos os serviços rodando (`./status.sh`)
- [ ] Banco de dados configurado
- [ ] Arquivos de áudio em `/var/lib/asterisk/sounds/custom/`
- [ ] Configuração AMI no Asterisk
- [ ] Variáveis de ambiente no `.env`

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- **📧 Email**: suporte@empresa.com
- **📚 Documentação**: [docs/](docs/)
- **🐛 Issues**: [GitHub Issues](https://github.com/seu-repo/discador-preditivo/issues)
- **💬 Discord**: [Servidor Discord](https://discord.gg/seu-servidor)

## 🔄 Atualizações

Para atualizar o sistema:

```bash
git pull origin main
pip install -r requirements.txt
./stop.sh && ./start.sh
./validate.sh
```

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**

> **Versão**: 1.0.0  
> **Última atualização**: Janeiro 2024  
> **Compatibilidade**: Ubuntu 20.04+, Debian 11+ 