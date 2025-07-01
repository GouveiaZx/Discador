# 🚀 Instalação do Sistema de Discador Preditivo

## 📋 Visão Geral

Este guia fornece instruções completas para instalar o sistema de discador preditivo "Presione 1" com detecção de voicemail em servidores Linux (Debian/Ubuntu).

## 🖥️ Requisitos do Sistema

### Especificações Mínimas
- **CPU**: 2 cores (4 recomendado)
- **RAM**: 4GB (8GB recomendado)
- **Disco**: 20GB livre (SSD recomendado)
- **Sistema**: Ubuntu 20.04+ ou Debian 11+
- **Rede**: Conectividade estável à internet

### Portas Necessárias
- **8000**: API Backend (FastAPI)
- **3000**: Frontend (se aplicável)
- **5432**: PostgreSQL
- **5038**: Asterisk AMI
- **5060**: SIP (Asterisk)
- **10000-20000**: RTP (Asterisk)

## 🔧 Instalação Passo a Passo

### 1. Preparação do Sistema

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar utilitários básicos
sudo apt install -y curl wget git unzip software-properties-common \
    build-essential pkg-config libssl-dev libffi-dev

# Configurar timezone
sudo timedatectl set-timezone America/Sao_Paulo

# Criar usuário do sistema
sudo useradd -m -s /bin/bash discador
sudo usermod -aG sudo discador
sudo su - discador
```

### 2. Instalação do Python 3.9+

```bash
# Instalar Python e pip
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verificar versão
python3 --version  # Deve ser 3.9+

# Instalar poetry (gerenciador de dependências)
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Instalação do PostgreSQL

```bash
# Instalar PostgreSQL
sudo apt install -y postgresql postgresql-contrib postgresql-client

# Iniciar e habilitar serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Configurar usuário e banco
sudo -u postgres psql << EOF
CREATE USER discador WITH PASSWORD 'discador_2024_secure';
CREATE DATABASE discador_db OWNER discador;
GRANT ALL PRIVILEGES ON DATABASE discador_db TO discador;
ALTER USER discador CREATEDB;
\q
EOF

# Configurar autenticação
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" \
    /etc/postgresql/*/main/postgresql.conf

echo "host    discador_db    discador    127.0.0.1/32    md5" | \
    sudo tee -a /etc/postgresql/*/main/pg_hba.conf

sudo systemctl restart postgresql
```

### 4. Instalação do Redis (Cache)

```bash
# Instalar Redis
sudo apt install -y redis-server

# Configurar Redis
sudo sed -i 's/# maxmemory 256mb/maxmemory 256mb/' /etc/redis/redis.conf
sudo sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf

# Reiniciar Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### 5. Instalação do Asterisk

```bash
# Instalar dependências do Asterisk
sudo apt install -y asterisk asterisk-dev asterisk-config \
    asterisk-modules asterisk-voicemail asterisk-sounds-core-en-wav

# Configurar grupos
sudo usermod -aG asterisk discador
sudo usermod -aG audio asterisk

# Configurar AMI
sudo tee /etc/asterisk/manager.conf << EOF
[general]
enabled = yes
port = 5038
bindaddr = 127.0.0.1

[discador_ami]
secret = discador_ami_2024
read = all
write = all
EOF

# Configurar SIP básico
sudo tee /etc/asterisk/sip.conf << EOF
[general]
context = default
allowoverlap = no
udpbindaddr = 0.0.0.0:5060
tcpenable = no
tcpbindaddr = 0.0.0.0:5060
transport = udp
srvlookup = yes
qualify = yes

[trunk_provider]
type = peer
host = seu.provedor.voip.com
username = seu_usuario
secret = sua_senha
fromuser = seu_usuario
fromdomain = seu.provedor.voip.com
insecure = port,invite
canreinvite = no
context = from-trunk
EOF

# Configurar dialplan
sudo tee /etc/asterisk/extensions.conf << EOF
[globals]

[general]
static = yes
writeprotect = no
clearglobalvars = no

[default]
exten => _X.,1,NoOp(Chamada padrão)
exten => _X.,n,Hangup()

[presione1-campana]
exten => s,1,NoOp(Campanha Presione 1 - \${LLAMADA_ID})
exten => s,n,Set(CHANNEL(language)=pt_BR)
exten => s,n,Answer()
exten => s,n,Wait(1)
exten => s,n,GotoIf(\${DETECTAR_VOICEMAIL}?detect_vm:play_audio)

exten => s,n(detect_vm),BackgroundDetect(\${AUDIO_URL},\${TIMEOUT_DTMF},1)
exten => s,n,GotoIf(\${VMDETECTED}?voicemail_flow:dtmf_wait)

exten => s,n(voicemail_flow),NoOp(Voicemail detectado)
exten => s,n,UserEvent(VoicemailDetected,LlamadaID:\${LLAMADA_ID})
exten => s,n,GotoIf(\${LEN(\${VOICEMAIL_AUDIO_URL})}?play_vm_audio:hangup)

exten => s,n(play_vm_audio),Playback(\${VOICEMAIL_AUDIO_URL})
exten => s,n,UserEvent(VoicemailAudioFinished,LlamadaID:\${LLAMADA_ID})
exten => s,n,Hangup()

exten => s,n(play_audio),Playback(\${AUDIO_URL})
exten => s,n(dtmf_wait),Read(RESPONSE,silence/1,1,,,\${TIMEOUT_DTMF})
exten => s,n,GotoIf(\${RESPONSE}=1?transfer:no_response)

exten => s,n(transfer),UserEvent(DTMFReceived,LlamadaID:\${LLAMADA_ID},DTMF:1)
exten => s,n,Transfer(100)

exten => s,n(no_response),UserEvent(DTMFTimeout,LlamadaID:\${LLAMADA_ID})
exten => s,n,Hangup()

exten => _X.,1,Goto(s,1)
EOF

# Reiniciar Asterisk
sudo systemctl restart asterisk
sudo systemctl enable asterisk
```

### 6. Clonagem e Configuração do Projeto

```bash
# Ir para diretório home do usuário
cd /home/discador

# Clonar repositório (substitua pela URL real)
git clone https://github.com/seu-repositorio/discador-preditivo.git
cd discador-preditivo

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
pip install --upgrade pip
pip install -r requirements.txt

# Ou se usar Poetry
poetry install
```

### 7. Configuração de Variáveis de Ambiente

```bash
# Criar arquivo de configuração
tee .env << EOF
# ===================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ===================================
DATABASE_URL=postgresql://discador:discador_2024_secure@localhost:5432/discador_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=discador_db
DB_USER=discador
DB_PASSWORD=discador_2024_secure

# ===================================
# CONFIGURAÇÃO DO ASTERISK
# ===================================
ASTERISK_HOST=127.0.0.1
ASTERISK_PUERTO=5038
ASTERISK_USUARIO=discador_ami
ASTERISK_PASSWORD=discador_ami_2024

# ===================================
# CONFIGURAÇÃO DA API
# ===================================
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
SECRET_KEY=sua_chave_secreta_muito_segura_aqui_2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ===================================
# CONFIGURAÇÃO DO REDIS
# ===================================
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# ===================================
# CONFIGURAÇÃO DE LOGS
# ===================================
LOG_LEVEL=INFO
LOG_FILE=/var/log/discador/app.log

# ===================================
# CONFIGURAÇÃO DE ARQUIVOS
# ===================================
SOUNDS_PATH=/var/lib/asterisk/sounds/custom
RECORDINGS_PATH=/var/spool/asterisk/monitor

# ===================================
# CONFIGURAÇÃO DE EMAIL (OPCIONAL)
# ===================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
EMAIL_FROM=sistema@empresa.com

# ===================================
# CONFIGURAÇÃO DE MONITORAMENTO
# ===================================
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_URL=/health

# ===================================
# CONFIGURAÇÃO DE SEGURANÇA
# ===================================
ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com
CORS_ORIGINS=http://localhost:3000,https://seu-frontend.com
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
EOF

# Proteger arquivo de configuração
chmod 600 .env
```

### 8. Configuração do Banco de Dados

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar migrações
python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('✅ Banco de dados inicializado com sucesso!')
"

# Executar migrações SQL específicas
psql postgresql://discador:discador_2024_secure@localhost:5432/discador_db \
    -f migrations/create_presione1_tables.sql

# Inserir dados de exemplo
python scripts/populate_sample_data.py
```

### 9. Configuração de Diretórios e Permissões

```bash
# Criar diretórios necessários
sudo mkdir -p /var/log/discador
sudo mkdir -p /var/lib/asterisk/sounds/custom
sudo mkdir -p /var/spool/asterisk/monitor
sudo mkdir -p /etc/discador

# Configurar permissões
sudo chown -R discador:discador /var/log/discador
sudo chown -R asterisk:asterisk /var/lib/asterisk/sounds/custom
sudo chown -R asterisk:asterisk /var/spool/asterisk/monitor
sudo chmod -R 755 /var/lib/asterisk/sounds/custom

# Adicionar discador ao grupo asterisk
sudo usermod -aG asterisk discador
```

### 10. Configuração de Arquivos de Áudio

```bash
# Criar diretório para áudios customizados
sudo mkdir -p /var/lib/asterisk/sounds/custom

# Baixar arquivos de áudio de exemplo (substitua pelas URLs reais)
cd /var/lib/asterisk/sounds/custom

# Áudio principal para "Presione 1"
sudo wget -O presione1_demo.wav \
    "https://exemplo.com/audios/presione1_demo.wav"

# Áudio para voicemail
sudo wget -O voicemail_demo.wav \
    "https://exemplo.com/audios/voicemail_demo.wav"

# Configurar permissões
sudo chown asterisk:asterisk *.wav
sudo chmod 644 *.wav

# Verificar arquivos
ls -la /var/lib/asterisk/sounds/custom/
```

## 🔄 Scripts de Inicialização

### 1. Script Principal de Start

```bash
# Criar script de inicialização
tee /home/discador/discador-preditivo/start.sh << 'EOF'
#!/bin/bash

# Script de inicialização do Sistema de Discador Preditivo
# Autor: Sistema Discador
# Data: $(date)

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configurações
PROJECT_DIR="/home/discador/discador-preditivo"
ENV_FILE="$PROJECT_DIR/.env"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="/var/log/discador"

# Verificar se está rodando como usuário correto
if [ "$USER" != "discador" ]; then
    log_error "Este script deve ser executado como usuário 'discador'"
    exit 1
fi

# Carregar variáveis de ambiente
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
    log_success "Variáveis de ambiente carregadas"
else
    log_error "Arquivo .env não encontrado em $ENV_FILE"
    exit 1
fi

# Função para verificar serviços
check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        log_success "$service está rodando"
        return 0
    else
        log_error "$service não está rodando"
        return 1
    fi
}

# Verificar dependências
log_info "Verificando dependências do sistema..."

check_service postgresql || exit 1
check_service redis-server || exit 1
check_service asterisk || exit 1

# Verificar conectividade do banco
log_info "Verificando conectividade do banco de dados..."
if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
    log_success "Banco de dados acessível"
else
    log_error "Não foi possível conectar ao banco de dados"
    exit 1
fi

# Verificar conectividade Asterisk AMI
log_info "Verificando conectividade Asterisk AMI..."
if timeout 5 bash -c "</dev/tcp/$ASTERISK_HOST/$ASTERISK_PUERTO" 2>/dev/null; then
    log_success "Asterisk AMI acessível"
else
    log_error "Asterisk AMI não está acessível"
    exit 1
fi

# Ativar ambiente virtual
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    log_success "Ambiente virtual ativado"
else
    log_error "Ambiente virtual não encontrado em $VENV_DIR"
    exit 1
fi

# Verificar dependências Python
log_info "Verificando dependências Python..."
if python -c "import fastapi, sqlalchemy, asyncpg" 2>/dev/null; then
    log_success "Dependências Python OK"
else
    log_warning "Instalando/atualizando dependências..."
    pip install -r requirements.txt
fi

# Executar migrações se necessário
log_info "Verificando migrações do banco..."
python -c "
from app.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM campanas_presione1'))
        print('Banco de dados OK')
except Exception as e:
    print(f'Erro no banco: {e}')
    exit(1)
"

# Criar diretórios de log se não existirem
mkdir -p "$LOG_DIR"

# Iniciar aplicação
log_info "Iniciando aplicação..."
cd "$PROJECT_DIR"

# Verificar se já está rodando
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    log_warning "Aplicação já está rodando. Parando processo anterior..."
    pkill -f "uvicorn.*app.main:app"
    sleep 2
fi

# Iniciar em background
nohup uvicorn app.main:app \
    --host $API_HOST \
    --port $API_PORT \
    --reload \
    > "$LOG_DIR/app.log" 2>&1 &

APP_PID=$!
echo $APP_PID > "$LOG_DIR/app.pid"

# Aguardar inicialização
log_info "Aguardando inicialização da aplicação..."
sleep 5

# Verificar se está rodando
if ps -p $APP_PID > /dev/null; then
    log_success "🚀 Sistema iniciado com sucesso!"
    log_info "PID: $APP_PID"
    log_info "URL: http://localhost:$API_PORT"
    log_info "Logs: $LOG_DIR/app.log"
    log_info "Para parar: $PROJECT_DIR/stop.sh"
else
    log_error "Falha ao iniciar aplicação"
    cat "$LOG_DIR/app.log"
    exit 1
fi
EOF

chmod +x /home/discador/discador-preditivo/start.sh
```

### 2. Script de Parada

```bash
# Criar script de parada
tee /home/discador/discador-preditivo/stop.sh << 'EOF'
#!/bin/bash

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Configurações
PROJECT_DIR="/home/discador/discador-preditivo"
LOG_DIR="/var/log/discador"
PID_FILE="$LOG_DIR/app.pid"

log_info "Parando sistema de discador preditivo..."

# Parar aplicação usando PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        log_info "Parando processo PID: $PID"
        kill $PID
        sleep 3
        
        # Force kill se necessário
        if ps -p $PID > /dev/null; then
            log_info "Forçando parada do processo..."
            kill -9 $PID
        fi
        
        rm "$PID_FILE"
        log_success "Aplicação parada"
    else
        log_info "Processo não está rodando"
        rm "$PID_FILE"
    fi
else
    log_info "PID file não encontrado"
fi

# Matar qualquer processo restante
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    log_info "Matando processos restantes..."
    pkill -f "uvicorn.*app.main:app"
fi

log_success "🛑 Sistema parado com sucesso!"
EOF

chmod +x /home/discador/discador-preditivo/stop.sh
```

### 3. Script de Status

```bash
# Criar script de status
tee /home/discador/discador-preditivo/status.sh << 'EOF'
#!/bin/bash

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
PROJECT_DIR="/home/discador/discador-preditivo"
LOG_DIR="/var/log/discador"

echo -e "${BLUE}======================================"
echo -e "🔍 STATUS DO SISTEMA DISCADOR PREDITIVO"
echo -e "======================================${NC}"

# Verificar serviços do sistema
echo -e "\n${YELLOW}📋 Serviços do Sistema:${NC}"

check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo -e "  ✅ $service: ${GREEN}RODANDO${NC}"
    else
        echo -e "  ❌ $service: ${RED}PARADO${NC}"
    fi
}

check_service postgresql
check_service redis-server
check_service asterisk

# Verificar aplicação
echo -e "\n${YELLOW}🚀 Aplicação:${NC}"
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    PID=$(pgrep -f "uvicorn.*app.main:app")
    echo -e "  ✅ Discador API: ${GREEN}RODANDO${NC} (PID: $PID)"
    
    # Testar endpoint
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "  ✅ Health Check: ${GREEN}OK${NC}"
    else
        echo -e "  ⚠️  Health Check: ${YELLOW}FALHOU${NC}"
    fi
else
    echo -e "  ❌ Discador API: ${RED}PARADO${NC}"
fi

# Verificar conectividade
echo -e "\n${YELLOW}🔗 Conectividade:${NC}"

# Banco de dados
if psql postgresql://discador:discador_2024_secure@localhost:5432/discador_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "  ✅ PostgreSQL: ${GREEN}CONECTADO${NC}"
else
    echo -e "  ❌ PostgreSQL: ${RED}ERRO${NC}"
fi

# Redis
if redis-cli ping > /dev/null 2>&1; then
    echo -e "  ✅ Redis: ${GREEN}CONECTADO${NC}"
else
    echo -e "  ❌ Redis: ${RED}ERRO${NC}"
fi

# Asterisk AMI
if timeout 2 bash -c "</dev/tcp/127.0.0.1/5038" 2>/dev/null; then
    echo -e "  ✅ Asterisk AMI: ${GREEN}ACESSÍVEL${NC}"
else
    echo -e "  ❌ Asterisk AMI: ${RED}INACESSÍVEL${NC}"
fi

# Recursos do sistema
echo -e "\n${YELLOW}💻 Recursos do Sistema:${NC}"
echo -e "  💾 Uso de Memória: $(free -h | awk '/^Mem:/ {print $3"/"$2}')"
echo -e "  💿 Uso de Disco: $(df -h / | awk 'NR==2 {print $3"/"$2" ("$5")"}')"
echo -e "  ⚡ Load Average: $(uptime | awk -F'load average:' '{print $2}')"

# Logs recentes
echo -e "\n${YELLOW}📄 Logs Recentes:${NC}"
if [ -f "$LOG_DIR/app.log" ]; then
    echo -e "  📝 Últimas 3 linhas do log:"
    tail -n 3 "$LOG_DIR/app.log" | sed 's/^/    /'
else
    echo -e "  ⚠️  Arquivo de log não encontrado"
fi

echo -e "\n${BLUE}======================================${NC}"
EOF

chmod +x /home/discador/discador-preditivo/status.sh
```

## 🧪 Validação da Instalação

### 1. Teste Básico de Conectividade

```bash
# Criar script de validação
tee /home/discador/discador-preditivo/validate.sh << 'EOF'
#!/bin/bash

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 VALIDANDO INSTALAÇÃO DO SISTEMA${NC}"
echo "=========================================="

# Teste 1: Verificar API
echo -e "\n${YELLOW}Teste 1: API Health Check${NC}"
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "✅ ${GREEN}API respondendo corretamente${NC}"
else
    echo -e "❌ ${RED}API não está respondendo${NC}"
    exit 1
fi

# Teste 2: Verificar documentação
echo -e "\n${YELLOW}Teste 2: Documentação da API${NC}"
if curl -s http://localhost:8000/docs | grep -q "FastAPI"; then
    echo -e "✅ ${GREEN}Documentação acessível em http://localhost:8000/docs${NC}"
else
    echo -e "❌ ${RED}Documentação não acessível${NC}"
fi

# Teste 3: Teste do banco
echo -e "\n${YELLOW}Teste 3: Conectividade do Banco${NC}"
if python3 -c "
import os, sys
sys.path.append('/home/discador/discador-preditivo')
from app.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM campanas_presione1'))
        print('✅ Banco de dados OK')
except Exception as e:
    print(f'❌ Erro no banco: {e}')
    exit(1)
"; then
    echo -e "✅ ${GREEN}Banco de dados funcionando${NC}"
else
    echo -e "❌ ${RED}Erro no banco de dados${NC}"
    exit 1
fi

# Teste 4: Criar campanha de teste
echo -e "\n${YELLOW}Teste 4: Criação de Campanha de Teste${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/presione1/campanhas \
    -H "Content-Type: application/json" \
    -d '{
        "nombre": "Teste Validação",
        "descripcion": "Campanha para validar instalação",
        "lista_llamadas_id": 1,
        "mensaje_audio_url": "/var/lib/asterisk/sounds/custom/presione1_demo.wav",
        "detectar_voicemail": true,
        "mensaje_voicemail_url": "/var/lib/asterisk/sounds/custom/voicemail_demo.wav",
        "extension_transferencia": "100"
    }')

if echo "$RESPONSE" | grep -q '"id"'; then
    CAMPANA_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    echo -e "✅ ${GREEN}Campanha criada com ID: $CAMPANA_ID${NC}"
else
    echo -e "❌ ${RED}Erro ao criar campanha${NC}"
    echo "Resposta: $RESPONSE"
    exit 1
fi

# Teste 5: Listar campanhas
echo -e "\n${YELLOW}Teste 5: Listagem de Campanhas${NC}"
if curl -s http://localhost:8000/api/v1/presione1/campanhas | grep -q "Teste Validação"; then
    echo -e "✅ ${GREEN}Listagem funcionando${NC}"
else
    echo -e "❌ ${RED}Erro na listagem${NC}"
    exit 1
fi

# Teste 6: Asterisk AMI
echo -e "\n${YELLOW}Teste 6: Asterisk AMI${NC}"
if python3 -c "
import asyncio, sys
sys.path.append('/home/discador/discador-preditivo')
from app.services.asterisk import asterisk_service

async def test_ami():
    try:
        connected = await asterisk_service.conectar()
        if connected:
            print('✅ Asterisk AMI conectou com sucesso')
            await asterisk_service.desconectar()
        else:
            print('❌ Erro ao conectar Asterisk AMI')
            exit(1)
    except Exception as e:
        print(f'❌ Erro AMI: {e}')
        exit(1)

asyncio.run(test_ami())
"; then
    echo -e "✅ ${GREEN}Asterisk AMI funcionando${NC}"
else
    echo -e "❌ ${RED}Erro no Asterisk AMI${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}"
echo -e "${GREEN}✅ Sistema instalado e funcionando corretamente${NC}"
echo ""
echo "🔗 Links úteis:"
echo "  📖 API: http://localhost:8000/docs"
echo "  🔍 Health: http://localhost:8000/health"
echo "  📊 Métricas: http://localhost:8000/metrics"
echo ""
echo "📁 Comandos úteis:"
echo "  🚀 Iniciar: ./start.sh"
echo "  🛑 Parar: ./stop.sh"
echo "  📊 Status: ./status.sh"
echo "  🧪 Testar voicemail: python scripts/teste_voicemail.py"
EOF

chmod +x /home/discador/discador-preditivo/validate.sh
```

### 2. Executar Validação

```bash
# Ir para diretório do projeto
cd /home/discador/discador-preditivo

# Iniciar sistema
./start.sh

# Aguardar 10 segundos para inicialização completa
sleep 10

# Executar validação
./validate.sh
```

## 🔧 Configuração de Serviços Systemd

### 1. Criar Service para Auto-start

```bash
# Criar service do systemd
sudo tee /etc/systemd/system/discador-preditivo.service << EOF
[Unit]
Description=Sistema de Discador Preditivo
After=network.target postgresql.service redis-server.service asterisk.service
Requires=postgresql.service redis-server.service asterisk.service

[Service]
Type=forking
User=discador
Group=discador
WorkingDirectory=/home/discador/discador-preditivo
Environment=PATH=/home/discador/discador-preditivo/venv/bin
ExecStart=/home/discador/discador-preditivo/start.sh
ExecStop=/home/discador/discador-preditivo/stop.sh
Restart=always
RestartSec=10
PIDFile=/var/log/discador/app.pid

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviço
sudo systemctl enable discador-preditivo

# Iniciar serviço
sudo systemctl start discador-preditivo

# Verificar status
sudo systemctl status discador-preditivo
```

## 📊 Monitoramento e Logs

### 1. Configuração de Logrotate

```bash
# Configurar rotação de logs
sudo tee /etc/logrotate.d/discador << EOF
/var/log/discador/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su discador discador
}
EOF
```

### 2. Script de Monitoramento

```bash
# Criar script de monitoramento
tee /home/discador/discador-preditivo/monitor.sh << 'EOF'
#!/bin/bash

# Script de monitoramento contínuo
# Verifica saúde do sistema a cada 30 segundos

LOGFILE="/var/log/discador/monitor.log"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Verificar API
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "[$TIMESTAMP] API: OK" >> $LOGFILE
    else
        echo "[$TIMESTAMP] API: FALHOU - Reiniciando..." >> $LOGFILE
        systemctl restart discador-preditivo
    fi
    
    # Verificar uso de memória
    MEM_USAGE=$(free | awk '/^Mem:/ {printf "%.1f", $3/$2 * 100.0}')
    echo "[$TIMESTAMP] Memória: ${MEM_USAGE}%" >> $LOGFILE
    
    # Verificar campanhas ativas
    CAMPANHAS=$(curl -s http://localhost:8000/api/v1/presione1/campanhas | jq '. | length' 2>/dev/null || echo "0")
    echo "[$TIMESTAMP] Campanhas: $CAMPANHAS" >> $LOGFILE
    
    sleep 30
done
EOF

chmod +x /home/discador/discador-preditivo/monitor.sh
```

## 🧪 Exemplos de Teste

### 1. Teste Manual com cURL

```bash
# Teste 1: Health Check
curl http://localhost:8000/health

# Teste 2: Listar campanhas
curl http://localhost:8000/api/v1/presione1/campanhas

# Teste 3: Criar lista de números
curl -X POST http://localhost:8000/api/v1/listas-llamadas \
    -H "Content-Type: application/json" \
    -d '{
        "nombre": "Lista Teste Manual",
        "descripcion": "Lista para testes manuais",
        "numeros": ["+5511999999999", "+5511888888888"]
    }'

# Teste 4: Criar campanha
curl -X POST http://localhost:8000/api/v1/presione1/campanhas \
    -H "Content-Type: application/json" \
    -d '{
        "nombre": "Campanha Teste Manual",
        "descripcion": "Teste manual da API",
        "lista_llamadas_id": 1,
        "mensaje_audio_url": "/var/lib/asterisk/sounds/custom/presione1_demo.wav",
        "timeout_presione1": 10,
        "detectar_voicemail": true,
        "mensaje_voicemail_url": "/var/lib/asterisk/sounds/custom/voicemail_demo.wav",
        "extension_transferencia": "100"
    }'

# Teste 5: Iniciar campanha (substitua ID)
curl -X POST http://localhost:8000/api/v1/presione1/campanhas/1/iniciar

# Teste 6: Ver estatísticas
curl http://localhost:8000/api/v1/presione1/campanhas/1/estadisticas

# Teste 7: Parar campanha
curl -X POST http://localhost:8000/api/v1/presione1/campanhas/1/parar
```

### 2. Teste Automatizado de Voicemail

```bash
# Executar teste completo de voicemail
cd /home/discador/discador-preditivo
python scripts/teste_voicemail.py
```

## ⚠️ Troubleshooting

### Problemas Comuns e Soluções

#### 1. API não inicia
```bash
# Verificar logs
tail -f /var/log/discador/app.log

# Verificar processo
ps aux | grep uvicorn

# Verificar porta
netstat -tlnp | grep 8000
```

#### 2. Erro de conexão com banco
```bash
# Testar conexão manual
psql postgresql://discador:discador_2024_secure@localhost:5432/discador_db

# Verificar serviço PostgreSQL
sudo systemctl status postgresql

# Ver logs do PostgreSQL
sudo journalctl -u postgresql
```

#### 3. Asterisk AMI não conecta
```bash
# Verificar configuração AMI
sudo asterisk -rx "manager show users"

# Testar porta AMI
telnet localhost 5038

# Verificar logs Asterisk
sudo tail -f /var/log/asterisk/messages
```

#### 4. Permissões de arquivo
```bash
# Corrigir permissões
sudo chown -R discador:discador /home/discador/discador-preditivo
sudo chown -R asterisk:asterisk /var/lib/asterisk/sounds/custom
sudo chmod -R 755 /var/lib/asterisk/sounds/custom
```

#### 5. Dependências Python
```bash
# Reinstalar dependências
cd /home/discador/discador-preditivo
source venv/bin/activate
pip install --upgrade --force-reinstall -r requirements.txt
```

## 📚 Próximos Passos

### Após Instalação Bem-sucedida

1. **Configurar Certificados SSL** (para produção)
2. **Configurar Backup Automático** do banco de dados
3. **Implementar Monitoring** com Prometheus/Grafana
4. **Configurar Firewall** para segurança
5. **Documentar Procedimentos** específicos da sua empresa
6. **Treinar Usuários** no sistema

### Comandos de Manutenção

```bash
# Verificar status geral
./status.sh

# Ver logs em tempo real
tail -f /var/log/discador/app.log

# Backup do banco
pg_dump discador_db > backup_$(date +%Y%m%d).sql

# Atualizar sistema
git pull
pip install -r requirements.txt
./stop.sh && ./start.sh
```

---

## 📞 Suporte

Para dúvidas ou problemas:

1. **Logs**: Sempre verifique `/var/log/discador/app.log`
2. **Status**: Execute `./status.sh` para diagnóstico
3. **Validação**: Execute `./validate.sh` após mudanças
4. **Documentação**: Consulte `/docs/` para detalhes específicos

**Versão**: 1.0  
**Data**: Janeiro 2024  
**Compatibilidade**: Ubuntu 20.04+, Debian 11+ 