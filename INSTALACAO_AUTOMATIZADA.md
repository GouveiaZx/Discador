# 🚀 Instalação Automatizada - Sistema Discador Preditivo

Esta documentação descreve o processo de instalação automatizada completa do Sistema de Discador Preditivo em servidores cloud ou dedicados.

## 📋 Visão Geral

O sistema de instalação automatizada configura uma stack completa incluindo:

- **Backend FastAPI** com Python 3.9+
- **Frontend React** com TypeScript
- **PostgreSQL** como banco de dados
- **Redis** para cache e sessões
- **Asterisk** para telefonia
- **NGINX** como proxy reverso
- **PM2** para gerenciamento de processos
- **UFW** para firewall
- **SSL/HTTPS** com Let's Encrypt (opcional)

## 🛠️ Scripts Disponíveis

### 1. `install_complete.sh` - Instalação Principal
Script principal que configura todo o sistema do zero.

### 2. `setup_ssl.sh` - Configuração SSL
Script complementar para configurar SSL/HTTPS com Let's Encrypt.

## 🖥️ Requisitos do Servidor

### Hardware Mínimo
- **CPU**: 2 cores (4 recomendado)
- **RAM**: 4GB (8GB recomendado)
- **Disco**: 20GB livres (SSD preferível)
- **Rede**: Conexão estável com internet

### Software
- **OS**: Ubuntu 20.04+ ou Debian 11+
- **Acesso root** via sudo
- **Portas abertas**: 22 (SSH), 80 (HTTP), 443 (HTTPS)

### Para SSL (Opcional)
- **Domínio válido** apontando para o servidor
- **Email válido** para notificações Let's Encrypt

## 🚀 Instalação Rápida

### Passo 1: Preparação

```bash
# Fazer login no servidor como root ou usuário com sudo
ssh usuario@seu-servidor.com

# Baixar os scripts
wget https://raw.githubusercontent.com/seu-repo/discador-preditivo/main/install_complete.sh
wget https://raw.githubusercontent.com/seu-repo/discador-preditivo/main/setup_ssl.sh

# Dar permissões de execução
chmod +x install_complete.sh setup_ssl.sh
```

### Passo 2: Instalação Principal

```bash
# Instalação interativa (recomendada)
sudo ./install_complete.sh

# Ou instalação silenciosa (usando IP do servidor)
sudo ./install_complete.sh --silent
```

### Passo 3: Configuração SSL (Opcional)

```bash
# Apenas se você tem um domínio configurado
sudo ./setup_ssl.sh
```

## 📖 Instalação Detalhada

### Instalação Interativa

O script solicitará as seguintes informações:

1. **Domínio ou IP do servidor**
   - Ex: `discador.empresa.com` ou `192.168.1.100`
   - Usado para configurar NGINX e CORS

2. **Confirmação das configurações**
   - Usuário do sistema: `discador`
   - Diretório: `/opt/discador-preditivo`
   - Portas: API (8000), Frontend (3000)

### Instalação Silenciosa

Para automação ou CI/CD, use o modo silencioso:

```bash
sudo ./install_complete.sh --silent
```

Isso usará configurações padrão e o IP público do servidor.

## 🔧 Processo de Instalação

O script executa as seguintes etapas:

### 1. Verificações Iniciais
- Sistema operacional (Ubuntu/Debian)
- Privilégios de root
- Conectividade de rede

### 2. Atualização do Sistema
- Atualização de pacotes
- Instalação de utilitários básicos
- Configuração de repositórios

### 3. Criação do Usuário
- Usuário `discador` para o sistema
- Estrutura de diretórios em `/opt/discador-preditivo`
- Permissões apropriadas

### 4. Instalação de Serviços

#### PostgreSQL
- Instalação e configuração
- Criação de banco `discador_db`
- Usuário `discador` com senha segura
- Configuração de permissões

#### Redis
- Instalação do Redis Server
- Configuração de memória e política
- Otimização para produção

#### Node.js e PM2
- Node.js 18 via NodeSource
- PM2 para gerenciamento de processos
- Configuração de startup automático

#### Python
- Python 3.9+ com ambiente virtual
- Dependências para desenvolvimento
- Biblioteca para PostgreSQL

#### Asterisk
- Instalação completa com módulos
- Configuração AMI com usuário seguro
- Contextos básicos para discador
- Diretório de áudios personalizados

#### NGINX
- Instalação e configuração
- Proxy reverso para API e Frontend
- Compressão e cache
- Headers de segurança

### 5. Configuração das Aplicações

#### Backend FastAPI
- Estrutura básica se não existir
- Ambiente virtual Python
- Instalação de dependências
- Arquivo `.env` com configurações
- Execução de migrações

#### Frontend React
- Criação de aplicação TypeScript
- Dependências básicas (axios, react-router)
- Estrutura de diretórios
- Build para produção

#### PM2
- Configuração de processos
- Scripts de backend e frontend
- Logs centralizados
- Restart automático

### 6. Configuração do Sistema

#### Firewall (UFW)
- Políticas restritivas por padrão
- Portas essenciais abertas
- Serviços locais protegidos

#### Serviços Systemd
- Serviço para PM2
- Backup automático
- Inicialização automática

#### Scripts de Gerenciamento
- `backup.sh` - Backup automático
- `deploy.sh` - Deploy de atualizações
- `status.sh` - Status do sistema

#### Logs e Rotação
- Logrotate configurado
- Logs centralizados
- Retenção apropriada

### 7. Inicialização e Validação
- Inicialização das aplicações
- Testes de conectividade
- Validação de serviços
- Relatório final

## 🔒 Configuração SSL

### Pré-requisitos para SSL

1. **Domínio configurado** apontando para o servidor
2. **DNS propagado** (verificar com `dig seu-dominio.com`)
3. **Firewall** permitindo portas 80 e 443
4. **NGINX** funcionando corretamente

### Processo SSL

```bash
sudo ./setup_ssl.sh
```

O script de SSL executará:

1. **Verificação de DNS** - Confirma se domínio aponta para o servidor
2. **Instalação do Certbot** - Via snap para melhor compatibilidade
3. **Configuração temporária** - NGINX para validação Let's Encrypt
4. **Obtenção do certificado** - Automaticamente via webroot
5. **Configuração NGINX SSL** - Com configurações de segurança
6. **Renovação automática** - Cron job para renovação
7. **Atualização do backend** - CORS e configurações SSL
8. **Validação final** - Testes de conectividade HTTPS

## 📊 Estrutura Final

Após a instalação, você terá:

```
/opt/discador-preditivo/
├── backend/
│   ├── app/              # Aplicação FastAPI
│   ├── venv/             # Ambiente virtual Python
│   ├── migrations/       # Migrações do banco
│   ├── scripts/          # Scripts auxiliares
│   └── .env              # Configurações
├── frontend/
│   ├── src/              # Código fonte React
│   ├── build/            # Build de produção
│   └── node_modules/     # Dependências Node.js
├── logs/                 # Logs das aplicações
├── backups/              # Backups automáticos
├── scripts/              # Scripts de gerenciamento
└── ecosystem.config.js   # Configuração PM2
```

## 🔗 URLs de Acesso

Após a instalação:

### HTTP (Instalação básica)
- **Frontend**: `http://seu-servidor/`
- **API Docs**: `http://seu-servidor/docs`
- **Health Check**: `http://seu-servidor/health`

### HTTPS (Com SSL configurado)
- **Frontend**: `https://seu-dominio.com/`
- **API Docs**: `https://seu-dominio.com/docs`
- **Health Check**: `https://seu-dominio.com/health`

## 🔑 Credenciais Geradas

O sistema gera automaticamente:

### Banco de Dados
- **Host**: `localhost:5432`
- **Banco**: `discador_db`
- **Usuário**: `discador`
- **Senha**: `discador_2024_secure_[timestamp]`

### Asterisk AMI
- **Host**: `127.0.0.1:5038`
- **Usuário**: `discador_ami`
- **Senha**: `ami_[timestamp]_secure`

### Backend
- **Secret Key**: Gerada automaticamente (32 bytes hex)

> **⚠️ Importante**: Anote essas credenciais! Elas são exibidas no final da instalação e salvas nos logs.

## ⚡ Comandos de Gerenciamento

### PM2 (Aplicações)
```bash
# Status das aplicações
sudo -u discador pm2 status

# Logs em tempo real
sudo -u discador pm2 logs

# Reiniciar aplicações
sudo -u discador pm2 restart all

# Parar aplicações
sudo -u discador pm2 stop all
```

### Scripts de Sistema
```bash
# Status completo do sistema
/opt/discador-preditivo/scripts/status.sh

# Backup manual
/opt/discador-preditivo/scripts/backup.sh

# Deploy de atualizações
/opt/discador-preditivo/scripts/deploy.sh
```

### Serviços
```bash
# Status dos serviços
systemctl status postgresql redis-server asterisk nginx

# Restart de serviços
sudo systemctl restart postgresql
sudo systemctl restart redis-server
sudo systemctl restart asterisk
sudo systemctl restart nginx
```

### Logs
```bash
# Logs da aplicação
tail -f /opt/discador-preditivo/logs/backend.log
tail -f /opt/discador-preditivo/logs/frontend.log

# Logs do sistema
tail -f /var/log/discador/app.log
tail -f /var/log/nginx/discador_access.log
```

## 🔧 Configuração Pós-Instalação

### 1. Arquivos de Áudio

Adicione seus arquivos de áudio em `/var/lib/asterisk/sounds/custom/`:

```bash
# Formato recomendado: WAV 8kHz, 16-bit, mono
sudo cp seu_arquivo.wav /var/lib/asterisk/sounds/custom/
sudo chown asterisk:asterisk /var/lib/asterisk/sounds/custom/seu_arquivo.wav
```

### 2. Configuração de Extensões SIP

Edite `/etc/asterisk/pjsip.conf` ou `/etc/asterisk/sip.conf` para configurar extensões.

### 3. Configuração de Campanhas

Acesse a interface web e configure suas primeiras campanhas.

### 4. Monitoramento

Configure alertas para:
- Uso de disco
- Memória
- Status dos serviços
- Renovação SSL

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Falha na Instalação de Dependências
```bash
# Limpar cache e tentar novamente
sudo apt-get clean
sudo apt-get update
sudo apt-get upgrade
```

#### 2. Erro de Conexão com Banco
```bash
# Verificar status do PostgreSQL
sudo systemctl status postgresql

# Testar conexão
sudo -u postgres psql -c "SELECT version();"
```

#### 3. NGINX Não Inicia
```bash
# Verificar configuração
sudo nginx -t

# Ver logs de erro
sudo tail -f /var/log/nginx/error.log
```

#### 4. PM2 Não Gerencia Processos
```bash
# Reinicializar PM2
sudo -u discador pm2 kill
sudo -u discador pm2 start /opt/discador-preditivo/ecosystem.config.js
```

#### 5. SSL Não Funciona
```bash
# Verificar DNS
dig seu-dominio.com

# Verificar certificado
sudo certbot certificates

# Testar renovação
sudo certbot renew --dry-run
```

### Logs de Diagnóstico

Todos os scripts geram logs detalhados:

- **Instalação principal**: `/var/log/install_discador.log`
- **Configuração SSL**: `/var/log/ssl_setup_discador.log`
- **Aplicação**: `/opt/discador-preditivo/logs/`
- **Sistema**: `/var/log/discador/`

## 🔄 Atualizações

### Atualização Manual
```bash
# Usar script de deploy
/opt/discador-preditivo/scripts/deploy.sh
```

### Atualização via Git
```bash
cd /opt/discador-preditivo
git pull origin main
sudo -u discador pm2 restart all
```

## 💾 Backup e Restauração

### Backup Automático
- Configurado para executar diariamente às 2:30 AM
- Backup do banco de dados
- Backup das configurações
- Retenção de 7 dias

### Backup Manual
```bash
/opt/discador-preditivo/scripts/backup.sh
```

### Restauração
```bash
# Restaurar banco de dados
gunzip -c /opt/discador-preditivo/backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | \
  sudo -u discador psql discador_db

# Restaurar configurações
sudo tar -xzf /opt/discador-preditivo/backups/config_backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

## 🛡️ Segurança

### Medidas Implementadas

1. **Firewall restritivo** com UFW
2. **Usuário dedicado** sem privilégios desnecessários
3. **Senhas seguras** geradas automaticamente
4. **Headers de segurança** no NGINX
5. **SSL/TLS** com configurações modernas
6. **Isolamento de serviços** via localhost
7. **Logs auditáveis** para todas as operações

### Recomendações Adicionais

1. **Trocar senhas padrão** após instalação
2. **Configurar fail2ban** para SSH
3. **Atualizar regularmente** o sistema
4. **Monitorar logs** de segurança
5. **Backup regular** dos dados

## 📞 Suporte

Para problemas com a instalação:

1. **Verificar logs** de instalação
2. **Consultar troubleshooting** nesta documentação
3. **Executar script de validação** existente
4. **Reportar issues** no repositório

## 🎯 Próximos Passos

Após a instalação bem-sucedida:

1. **Configurar extensões SIP** no Asterisk
2. **Adicionar arquivos de áudio** personalizados
3. **Criar primeira campanha** de teste
4. **Configurar monitoramento** e alertas
5. **Treinar equipe** no uso do sistema
6. **Implementar backup offsite** se necessário

---

**🎉 Parabéns! Seu Sistema de Discador Preditivo está pronto para uso!** 