#!/bin/bash

# ===================================
# INSTALAÇÃO AUTOMATIZADA COMPLETA
# Sistema de Discador Preditivo
# Backend FastAPI + Frontend React + Asterisk
# ===================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configurações globais
SCRIPT_DIR=$(dirname $(readlink -f $0))
PROJECT_NAME="discador-preditivo"
SYSTEM_USER="discador"
INSTALL_DIR="/opt/$PROJECT_NAME"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
LOG_FILE="/var/log/install_discador.log"

# Versões das dependências
NODE_VERSION="18"
PYTHON_VERSION="3.9"
NGINX_VERSION="latest"
PM2_VERSION="latest"

# Configurações do sistema
DB_NAME="discador_db"
DB_USER="discador"
DB_PASSWORD="discador_2024_secure_$(date +%s)"
AMI_USER="discador_ami"
AMI_PASSWORD="ami_$(date +%s)_secure"
API_PORT="8000"
FRONTEND_PORT="3000"
DOMAIN_NAME=""

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log_header() {
    echo -e "\n${CYAN}=================================="
    echo -e "🚀 $1"
    echo -e "==================================${NC}"
    echo "=== $1 ===" >> "$LOG_FILE"
}

# Função para verificar se comando foi executado com sucesso
check_command() {
    if [ $? -eq 0 ]; then
        log_success "$1"
    else
        log_error "Falha em: $1"
        exit 1
    fi
}

# Verificar se está rodando como root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Este script deve ser executado como root (sudo)"
        exit 1
    fi
}

# Verificar sistema operacional
check_os() {
    log_header "VERIFICANDO SISTEMA OPERACIONAL"
    
    if [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        VER=$DISTRIB_RELEASE
    elif [ -f /etc/debian_version ]; then
        OS=Debian
        VER=$(cat /etc/debian_version)
    else
        log_error "Sistema operacional não suportado"
        exit 1
    fi
    
    log_info "Sistema detectado: $OS $VER"
    
    if [[ "$OS" != "Ubuntu" ]] && [[ "$OS" != "Debian" ]]; then
        log_error "Este script suporta apenas Ubuntu e Debian"
        exit 1
    fi
    
    log_success "Sistema operacional suportado"
}

# Função para input interativo
prompt_input() {
    local prompt="$1"
    local default="$2"
    local result
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " result
        echo "${result:-$default}"
    else
        read -p "$prompt: " result
        echo "$result"
    fi
}

# Coletar informações do usuário
collect_user_input() {
    log_header "CONFIGURAÇÃO INICIAL"
    
    echo -e "${YELLOW}Por favor, forneça as seguintes informações:${NC}"
    
    DOMAIN_NAME=$(prompt_input "Domínio ou IP do servidor (ex: discador.empresa.com)" "")
    
    if [ -z "$DOMAIN_NAME" ]; then
        DOMAIN_NAME=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
        log_info "Usando IP público/local: $DOMAIN_NAME"
    fi
    
    # Confirmar configurações
    echo -e "\n${CYAN}Configurações a serem aplicadas:${NC}"
    echo "- Domínio/IP: $DOMAIN_NAME"
    echo "- Usuário do sistema: $SYSTEM_USER"
    echo "- Diretório de instalação: $INSTALL_DIR"
    echo "- Banco de dados: $DB_NAME"
    echo "- Porta API: $API_PORT"
    echo "- Porta Frontend: $FRONTEND_PORT"
    
    echo ""
    read -p "Continuar com a instalação? (y/N): " confirm
    if [[ "$confirm" != "y" ]] && [[ "$confirm" != "Y" ]]; then
        log_info "Instalação cancelada pelo usuário"
        exit 0
    fi
}

# Atualizar sistema
update_system() {
    log_header "ATUALIZANDO SISTEMA"
    
    export DEBIAN_FRONTEND=noninteractive
    
    apt-get update -qq
    check_command "Atualização da lista de pacotes"
    
    apt-get upgrade -y -qq
    check_command "Atualização do sistema"
    
    apt-get install -y -qq \
        curl \
        wget \
        gnupg \
        lsb-release \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        unzip \
        git \
        htop \
        vim \
        ufw \
        fail2ban \
        logrotate
    check_command "Instalação de pacotes básicos"
}

# Criar usuário do sistema
create_system_user() {
    log_header "CRIANDO USUÁRIO DO SISTEMA"
    
    if id "$SYSTEM_USER" &>/dev/null; then
        log_warning "Usuário $SYSTEM_USER já existe"
    else
        useradd -r -s /bin/bash -d "$INSTALL_DIR" -m "$SYSTEM_USER"
        check_command "Criação do usuário $SYSTEM_USER"
        
        # Adicionar ao grupo sudo para operações administrativas específicas
        usermod -aG sudo "$SYSTEM_USER"
        check_command "Adição do usuário ao grupo sudo"
    fi
    
    # Criar diretórios principais
    mkdir -p "$INSTALL_DIR"/{backend,frontend,logs,backups,scripts}
    chown -R "$SYSTEM_USER:$SYSTEM_USER" "$INSTALL_DIR"
    check_command "Criação da estrutura de diretórios"
}

# Instalar PostgreSQL
install_postgresql() {
    log_header "INSTALANDO POSTGRESQL"
    
    apt-get install -y -qq postgresql postgresql-contrib postgresql-client
    check_command "Instalação do PostgreSQL"
    
    systemctl enable postgresql
    systemctl start postgresql
    check_command "Inicialização do PostgreSQL"
    
    # Configurar banco de dados
    log_info "Configurando banco de dados..."
    
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
    sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;"
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"
    check_command "Configuração do banco de dados"
    
    # Configurar PostgreSQL para conexões locais
    PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+\.\d+' | head -1)
    PG_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"
    
    # Backup das configurações originais
    cp "$PG_CONFIG_DIR/postgresql.conf" "$PG_CONFIG_DIR/postgresql.conf.backup"
    cp "$PG_CONFIG_DIR/pg_hba.conf" "$PG_CONFIG_DIR/pg_hba.conf.backup"
    
    # Configurar postgresql.conf
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" "$PG_CONFIG_DIR/postgresql.conf"
    sed -i "s/#port = 5432/port = 5432/" "$PG_CONFIG_DIR/postgresql.conf"
    
    # Configurar pg_hba.conf
    echo "local   $DB_NAME    $DB_USER                                md5" >> "$PG_CONFIG_DIR/pg_hba.conf"
    
    systemctl restart postgresql
    check_command "Restart do PostgreSQL"
    
    log_success "PostgreSQL instalado e configurado"
}

# Instalar Redis
install_redis() {
    log_header "INSTALANDO REDIS"
    
    apt-get install -y -qq redis-server
    check_command "Instalação do Redis"
    
    # Configurar Redis
    sed -i 's/^supervised no/supervised systemd/' /etc/redis/redis.conf
    sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
    sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
    
    systemctl enable redis-server
    systemctl start redis-server
    check_command "Configuração e inicialização do Redis"
    
    log_success "Redis instalado e configurado"
}

# Instalar Node.js e npm
install_nodejs() {
    log_header "INSTALANDO NODE.JS"
    
    # Instalar Node.js via NodeSource
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
    check_command "Adição do repositório NodeSource"
    
    apt-get install -y -qq nodejs
    check_command "Instalação do Node.js"
    
    # Verificar versões
    NODE_VER=$(node --version)
    NPM_VER=$(npm --version)
    log_info "Node.js instalado: $NODE_VER"
    log_info "npm instalado: $NPM_VER"
    
    # Instalar PM2 globalmente
    npm install -g pm2@$PM2_VERSION
    check_command "Instalação do PM2"
    
    # Configurar PM2 para iniciar com o sistema
    pm2 startup systemd -u "$SYSTEM_USER" --hp "$INSTALL_DIR"
    check_command "Configuração do PM2 startup"
    
    log_success "Node.js e PM2 instalados"
}

# Instalar Python e dependências
install_python() {
    log_header "INSTALANDO PYTHON E DEPENDÊNCIAS"
    
    apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libpq-dev \
        libffi-dev \
        libssl-dev
    check_command "Instalação do Python e dependências"
    
    # Criar ambiente virtual no diretório do backend
    sudo -u "$SYSTEM_USER" python3 -m venv "$INSTALL_DIR/backend/venv"
    check_command "Criação do ambiente virtual Python"
    
    log_success "Python instalado e configurado"
}

# Instalar e configurar Asterisk
install_asterisk() {
    log_header "INSTALANDO ASTERISK"
    
    # Instalar dependências do Asterisk
    apt-get install -y -qq \
        asterisk \
        asterisk-config \
        asterisk-modules \
        asterisk-dahdi \
        sox \
        libsox-fmt-all
    check_command "Instalação do Asterisk"
    
    # Parar Asterisk para configuração
    systemctl stop asterisk
    
    # Backup das configurações originais
    cp /etc/asterisk/manager.conf /etc/asterisk/manager.conf.backup
    cp /etc/asterisk/extensions.conf /etc/asterisk/extensions.conf.backup
    cp /etc/asterisk/sip.conf /etc/asterisk/sip.conf.backup 2>/dev/null || true
    cp /etc/asterisk/pjsip.conf /etc/asterisk/pjsip.conf.backup 2>/dev/null || true
    
    # Configurar AMI (Asterisk Manager Interface)
    cat > /etc/asterisk/manager.conf << EOF
[general]
enabled = yes
port = 5038
bindaddr = 127.0.0.1

[$AMI_USER]
secret = $AMI_PASSWORD
permit = 127.0.0.1/255.255.255.0
read = all
write = all
EOF
    
    # Configurar extensões básicas
    cat > /etc/asterisk/extensions.conf << EOF
[general]
static=yes
writeprotect=no
clearglobalvars=no

[globals]

[default]

[presione1-context]
exten => _X.,1,NoOp(Llamada entrante: \${CALLERID(num)} -> \${EXTEN})
same => n,Answer()
same => n,Wait(1)
same => n,Set(TIMEOUT(digit)=10)
same => n,Set(TIMEOUT(response)=15)
same => n,Background(\${MENSAJE_AUDIO})
same => n,WaitExten(10)

exten => 1,1,NoOp(Cliente presionó 1)
same => n,Set(PRESIONE1=true)
same => n,Transfer(\${EXTENSION_TRANSFERENCIA})

exten => t,1,NoOp(Timeout - Sin respuesta)
same => n,Set(PRESIONE1=false)
same => n,Hangup()

exten => i,1,NoOp(Entrada inválida)
same => n,Set(PRESIONE1=false)
same => n,Hangup()

[transferencia]
exten => 100,1,NoOp(Transferencia a operador)
same => n,Dial(SIP/operador,30)
same => n,Hangup()

exten => 200,1,NoOp(Transferencia a vendas)
same => n,Dial(SIP/vendas,30)
same => n,Hangup()
EOF
    
    # Criar diretório para áudios customizados
    mkdir -p /var/lib/asterisk/sounds/custom
    chown -R asterisk:asterisk /var/lib/asterisk/sounds/custom
    chmod 755 /var/lib/asterisk/sounds/custom
    
    # Criar arquivos de áudio de exemplo (placeholder)
    cat > /var/lib/asterisk/sounds/custom/README.txt << EOF
Diretório para arquivos de áudio personalizados

Formatos suportados:
- WAV (recomendado): 8kHz, 16-bit, mono
- GSM: Compressão padrão Asterisk
- ALAW/ULAW: Formatos de telefonia

Arquivos necessários:
- presione1_demo.wav: Mensagem principal
- voicemail_demo.wav: Mensagem para voicemail
- transferencia.wav: Mensagem de transferência

Para converter arquivos:
sox arquivo_original.wav -r 8000 -c 1 -t wav arquivo_convertido.wav
EOF
    
    # Configurar permissões
    chown asterisk:asterisk /etc/asterisk/manager.conf
    chown asterisk:asterisk /etc/asterisk/extensions.conf
    chmod 640 /etc/asterisk/manager.conf
    
    # Configurar firewall para Asterisk (apenas localmente)
    ufw allow from 127.0.0.1 to any port 5038 comment "Asterisk AMI local"
    
    # Iniciar e habilitar Asterisk
    systemctl enable asterisk
    systemctl start asterisk
    check_command "Inicialização do Asterisk"
    
    # Aguardar Asterisk inicializar
    sleep 5
    
    # Verificar se AMI está funcionando
    if timeout 5 bash -c "</dev/tcp/127.0.0.1/5038" 2>/dev/null; then
        log_success "Asterisk AMI funcionando"
    else
        log_warning "Asterisk AMI pode não estar respondendo"
    fi
    
    log_success "Asterisk instalado e configurado"
}

# Instalar NGINX
install_nginx() {
    log_header "INSTALANDO NGINX"
    
    apt-get install -y -qq nginx
    check_command "Instalação do NGINX"
    
    # Remover configuração padrão
    rm -f "$NGINX_ENABLED/default"
    
    # Criar configuração para o discador preditivo
    cat > "$NGINX_AVAILABLE/$PROJECT_NAME" << EOF
# Configuração NGINX para Discador Preditivo
upstream backend_api {
    server 127.0.0.1:$API_PORT;
}

upstream frontend_app {
    server 127.0.0.1:$FRONTEND_PORT;
}

server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    # Logs
    access_log /var/log/nginx/discador_access.log;
    error_log /var/log/nginx/discador_error.log;
    
    # Timeouts
    client_max_body_size 100M;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    send_timeout 300;
    
    # Compressão
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # API Backend
    location /api/ {
        proxy_pass http://backend_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support para eventos em tempo real
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Documentação da API
    location /docs {
        proxy_pass http://backend_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check
    location /health {
        proxy_pass http://backend_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Métricas (protegidas)
    location /metrics {
        allow 127.0.0.1;
        deny all;
        proxy_pass http://backend_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Frontend React
    location / {
        proxy_pass http://frontend_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Para React Router
        try_files \$uri \$uri/ @fallback;
    }
    
    # Fallback para React Router
    location @fallback {
        proxy_pass http://frontend_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Assets estáticos com cache longo
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
        proxy_pass http://frontend_app;
        proxy_set_header Host \$host;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}

# Redirect HTTP to HTTPS (quando SSL estiver configurado)
# server {
#     listen 80;
#     server_name $DOMAIN_NAME;
#     return 301 https://\$server_name\$request_uri;
# }
EOF
    
    # Habilitar site
    ln -sf "$NGINX_AVAILABLE/$PROJECT_NAME" "$NGINX_ENABLED/$PROJECT_NAME"
    check_command "Habilitação do site no NGINX"
    
    # Testar configuração
    nginx -t
    check_command "Teste da configuração do NGINX"
    
    # Iniciar NGINX
    systemctl enable nginx
    systemctl start nginx
    check_command "Inicialização do NGINX"
    
    log_success "NGINX instalado e configurado"
}

# Configurar backend FastAPI
setup_backend() {
    log_header "CONFIGURANDO BACKEND FASTAPI"
    
    # Copiar arquivos do backend para o diretório de instalação
    if [ -d "$SCRIPT_DIR/app" ]; then
        cp -r "$SCRIPT_DIR/app" "$INSTALL_DIR/backend/"
        cp -r "$SCRIPT_DIR/migrations" "$INSTALL_DIR/backend/" 2>/dev/null || true
        cp -r "$SCRIPT_DIR/scripts" "$INSTALL_DIR/backend/" 2>/dev/null || true
        cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/backend/" 2>/dev/null || true
    else
        log_warning "Diretório 'app' não encontrado. Criando estrutura básica..."
        
        # Criar estrutura básica se não existir
        mkdir -p "$INSTALL_DIR/backend/app"
        cat > "$INSTALL_DIR/backend/requirements.txt" << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
redis==5.0.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-decouple==3.8
alembic==1.12.1
psycopg2-binary==2.9.9
requests==2.31.0
aiofiles==23.2.1
websockets==11.0.3
prometheus-client==0.19.0
structlog==23.2.0
EOF
        
        # Criar app básica
        cat > "$INSTALL_DIR/backend/app/main.py" << EOF
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Discador Preditivo API",
    description="Sistema de discador preditivo com detecção de voicemail",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API funcionando"}

@app.get("/")
async def root():
    return {"message": "Discador Preditivo API v1.0.0"}
EOF
    fi
    
    # Ajustar permissões
    chown -R "$SYSTEM_USER:$SYSTEM_USER" "$INSTALL_DIR/backend"
    
    # Instalar dependências Python
    log_info "Instalando dependências Python..."
    sudo -u "$SYSTEM_USER" bash -c "
        cd '$INSTALL_DIR/backend' && 
        source venv/bin/activate && 
        pip install --upgrade pip && 
        pip install -r requirements.txt
    "
    check_command "Instalação das dependências Python"
    
    # Criar arquivo de configuração .env
    cat > "$INSTALL_DIR/backend/.env" << EOF
# Configuração do Backend FastAPI
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
REDIS_URL=redis://localhost:6379/0

# Asterisk
ASTERISK_HOST=127.0.0.1
ASTERISK_PUERTO=5038
ASTERISK_USUARIO=$AMI_USER
ASTERISK_PASSWORD=$AMI_PASSWORD

# API
API_HOST=0.0.0.0
API_PORT=$API_PORT
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Arquivos
SOUNDS_PATH=/var/lib/asterisk/sounds/custom

# Logs
LOG_LEVEL=INFO
LOG_FILE=/var/log/discador/app.log

# CORS
CORS_ORIGINS=http://localhost:3000,http://$DOMAIN_NAME,https://$DOMAIN_NAME
EOF
    
    chown "$SYSTEM_USER:$SYSTEM_USER" "$INSTALL_DIR/backend/.env"
    chmod 600 "$INSTALL_DIR/backend/.env"
    
    # Executar migrações se existirem
    if [ -f "$INSTALL_DIR/backend/migrations/create_presione1_tables.sql" ]; then
        log_info "Executando migrações do banco de dados..."
        sudo -u "$SYSTEM_USER" psql "postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME" -f "$INSTALL_DIR/backend/migrations/create_presione1_tables.sql"
        check_command "Execução das migrações"
    fi
    
    log_success "Backend FastAPI configurado"
}

# Configurar frontend React
setup_frontend() {
    log_header "CONFIGURANDO FRONTEND REACT"
    
    # Criar aplicação React se não existir
    if [ ! -d "$INSTALL_DIR/frontend/src" ]; then
        log_info "Criando aplicação React..."
        
        sudo -u "$SYSTEM_USER" bash -c "
            cd '$INSTALL_DIR' && 
            npx create-react-app frontend --template typescript
        "
        check_command "Criação da aplicação React"
        
        # Instalar dependências adicionais
        sudo -u "$SYSTEM_USER" bash -c "
            cd '$INSTALL_DIR/frontend' && 
            npm install axios react-router-dom @types/react-router-dom
        "
        check_command "Instalação de dependências adicionais"
        
        # Criar estrutura básica
        sudo -u "$SYSTEM_USER" mkdir -p "$INSTALL_DIR/frontend/src/components"
        sudo -u "$SYSTEM_USER" mkdir -p "$INSTALL_DIR/frontend/src/pages"
        sudo -u "$SYSTEM_USER" mkdir -p "$INSTALL_DIR/frontend/src/services"
        sudo -u "$SYSTEM_USER" mkdir -p "$INSTALL_DIR/frontend/src/utils"
        
        # Criar serviço de API
        cat > "$INSTALL_DIR/frontend/src/services/api.ts" << EOF
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Serviços de campanhas
export const campaignService = {
  getCampaigns: () => api.get('/presione1/campanhas'),
  getCampaign: (id: number) => api.get(\`/presione1/campanhas/\${id}\`),
  createCampaign: (data: any) => api.post('/presione1/campanhas', data),
  updateCampaign: (id: number, data: any) => api.put(\`/presione1/campanhas/\${id}\`, data),
  deleteCampaign: (id: number) => api.delete(\`/presione1/campanhas/\${id}\`),
  startCampaign: (id: number) => api.post(\`/presione1/campanhas/\${id}/iniciar\`),
  stopCampaign: (id: number) => api.post(\`/presione1/campanhas/\${id}/parar\`),
  getStatistics: (id: number) => api.get(\`/presione1/campanhas/\${id}/estadisticas\`),
};

// Serviços de listas
export const listService = {
  getLists: () => api.get('/listas-llamadas'),
  getList: (id: number) => api.get(\`/listas-llamadas/\${id}\`),
  createList: (data: any) => api.post('/listas-llamadas', data),
  updateList: (id: number, data: any) => api.put(\`/listas-llamadas/\${id}\`, data),
  deleteList: (id: number) => api.delete(\`/listas-llamadas/\${id}\`),
};

export default api;
EOF
        
        # Criar página principal
        cat > "$INSTALL_DIR/frontend/src/App.tsx" << EOF
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

function Dashboard() {
  return (
    <div className="dashboard">
      <h1>Discador Preditivo</h1>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Campanhas Ativas</h3>
          <p>0</p>
        </div>
        <div className="stat-card">
          <h3>Chamadas Hoje</h3>
          <p>0</p>
        </div>
        <div className="stat-card">
          <h3>Taxa de Sucesso</h3>
          <p>0%</p>
        </div>
      </div>
    </div>
  );
}

function Campaigns() {
  return (
    <div>
      <h1>Campanhas</h1>
      <p>Lista de campanhas será implementada aqui.</p>
    </div>
  );
}

function Lists() {
  return (
    <div>
      <h1>Listas de Chamadas</h1>
      <p>Gerenciamento de listas será implementado aqui.</p>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">
            <Link to="/">Discador Preditivo</Link>
          </div>
          <div className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/campaigns">Campanhas</Link>
            <Link to="/lists">Listas</Link>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/lists" element={<Lists />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
EOF
        
        # Criar CSS básico
        cat > "$INSTALL_DIR/frontend/src/App.css" << EOF
.App {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: #2c3e50;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand a {
  color: white;
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background 0.3s;
}

.nav-links a:hover {
  background: rgba(255, 255, 255, 0.1);
}

.main-content {
  flex: 1;
  padding: 2rem;
  background: #ecf0f1;
}

.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1rem;
}

.stat-card p {
  margin: 0;
  font-size: 2rem;
  font-weight: bold;
  color: #3498db;
}
EOF
        
        # Criar arquivo de ambiente
        cat > "$INSTALL_DIR/frontend/.env" << EOF
REACT_APP_API_URL=/api/v1
REACT_APP_APP_NAME=Discador Preditivo
PORT=$FRONTEND_PORT
EOF
        
    else
        log_info "Frontend React já existe, configurando..."
        
        # Atualizar dependências
        sudo -u "$SYSTEM_USER" bash -c "
            cd '$INSTALL_DIR/frontend' && 
            npm install
        "
        check_command "Atualização das dependências do frontend"
    fi
    
    # Build da aplicação
    log_info "Compilando aplicação React..."
    sudo -u "$SYSTEM_USER" bash -c "
        cd '$INSTALL_DIR/frontend' && 
        npm run build
    "
    check_command "Build da aplicação React"
    
    # Ajustar permissões
    chown -R "$SYSTEM_USER:$SYSTEM_USER" "$INSTALL_DIR/frontend"
    
    log_success "Frontend React configurado"
}

# Configurar PM2
setup_pm2() {
    log_header "CONFIGURANDO PM2"
    
    # Criar arquivo de configuração do PM2
    cat > "$INSTALL_DIR/ecosystem.config.js" << EOF
module.exports = {
  apps: [
    {
      name: 'discador-backend',
      cwd: '$INSTALL_DIR/backend',
      script: 'venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port $API_PORT --workers 1',
      env: {
        PYTHONPATH: '$INSTALL_DIR/backend',
      },
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: '$INSTALL_DIR/logs/backend-error.log',
      out_file: '$INSTALL_DIR/logs/backend-out.log',
      log_file: '$INSTALL_DIR/logs/backend.log',
      time: true
    },
    {
      name: 'discador-frontend',
      cwd: '$INSTALL_DIR/frontend',
      script: 'npx',
      args: 'serve -s build -l $FRONTEND_PORT',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      error_file: '$INSTALL_DIR/logs/frontend-error.log',
      out_file: '$INSTALL_DIR/logs/frontend-out.log',
      log_file: '$INSTALL_DIR/logs/frontend.log',
      time: true
    }
  ]
};
EOF
    
    chown "$SYSTEM_USER:$SYSTEM_USER" "$INSTALL_DIR/ecosystem.config.js"
    
    # Instalar serve globalmente para servir o React build
    npm install -g serve
    check_command "Instalação do serve"
    
    # Criar diretório de logs
    mkdir -p "$INSTALL_DIR/logs"
    chown "$SYSTEM_USER:$SYSTEM_USER" "$INSTALL_DIR/logs"
    
    log_success "PM2 configurado"
}

# Configurar firewall
setup_firewall() {
    log_header "CONFIGURANDO FIREWALL"
    
    # Resetar UFW
    ufw --force reset
    
    # Políticas padrão
    ufw default deny incoming
    ufw default allow outgoing
    
    # SSH (assumindo porta 22, ajustar se necessário)
    ufw allow ssh comment "SSH access"
    
    # HTTP e HTTPS
    ufw allow 80/tcp comment "HTTP"
    ufw allow 443/tcp comment "HTTPS"
    
    # PostgreSQL (apenas local)
    ufw allow from 127.0.0.1 to any port 5432 comment "PostgreSQL local"
    
    # Redis (apenas local)
    ufw allow from 127.0.0.1 to any port 6379 comment "Redis local"
    
    # Asterisk AMI (apenas local)
    ufw allow from 127.0.0.1 to any port 5038 comment "Asterisk AMI local"
    
    # Asterisk SIP (se necessário para conectividade externa)
    # ufw allow 5060/udp comment "Asterisk SIP"
    # ufw allow 5060/tcp comment "Asterisk SIP"
    
    # Habilitar firewall
    ufw --force enable
    check_command "Configuração do firewall"
    
    log_success "Firewall configurado"
}

# Configurar serviços systemd
setup_systemd_services() {
    log_header "CONFIGURANDO SERVIÇOS SYSTEMD"
    
    # Serviço para gerenciar PM2
    cat > /etc/systemd/system/discador-pm2.service << EOF
[Unit]
Description=PM2 process manager for Discador Preditivo
Documentation=https://pm2.keymetrics.io/
After=network.target
Wants=network.target

[Service]
Type=forking
User=$SYSTEM_USER
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:$INSTALL_DIR/backend/venv/bin
Environment=PM2_HOME=$INSTALL_DIR/.pm2
PIDFile=$INSTALL_DIR/.pm2/pm2.pid
Restart=on-failure

ExecStart=/usr/bin/pm2 resurrect
ExecReload=/usr/bin/pm2 reload all
ExecStop=/usr/bin/pm2 kill

[Install]
WantedBy=multi-user.target
EOF
    
    # Serviço de backup automático
    cat > /etc/systemd/system/discador-backup.service << EOF
[Unit]
Description=Backup automático do Discador Preditivo
After=network.target

[Service]
Type=oneshot
User=$SYSTEM_USER
ExecStart=$INSTALL_DIR/scripts/backup.sh
EOF
    
    # Timer para backup diário
    cat > /etc/systemd/system/discador-backup.timer << EOF
[Unit]
Description=Execução diária do backup
Requires=discador-backup.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    # Recarregar systemd
    systemctl daemon-reload
    check_command "Reload do systemd"
    
    # Habilitar serviços
    systemctl enable discador-pm2.service
    systemctl enable discador-backup.timer
    check_command "Habilitação dos serviços"
    
    log_success "Serviços systemd configurados"
}

# Criar scripts de gerenciamento
create_management_scripts() {
    log_header "CRIANDO SCRIPTS DE GERENCIAMENTO"
    
    # Script de backup
    cat > "$INSTALL_DIR/scripts/backup.sh" << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/discador-preditivo/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="discador_db"
DB_USER="discador"

mkdir -p "$BACKUP_DIR"

# Backup do banco de dados
pg_dump -U "$DB_USER" -h localhost "$DB_NAME" | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Backup dos arquivos de configuração
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" \
    /opt/discador-preditivo/backend/.env \
    /etc/nginx/sites-available/discador-preditivo \
    /etc/asterisk/manager.conf \
    /etc/asterisk/extensions.conf

# Manter apenas os últimos 7 backups
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup concluído: $DATE"
EOF
    
    # Script de deploy
    cat > "$INSTALL_DIR/scripts/deploy.sh" << 'EOF'
#!/bin/bash
set -e

echo "Iniciando deploy..."

# Parar aplicações
pm2 stop all

# Atualizar código (se usando Git)
if [ -d "/opt/discador-preditivo/.git" ]; then
    cd /opt/discador-preditivo
    git pull origin main
fi

# Atualizar dependências do backend
cd /opt/discador-preditivo/backend
source venv/bin/activate
pip install -r requirements.txt

# Atualizar dependências do frontend
cd /opt/discador-preditivo/frontend
npm install
npm run build

# Reiniciar aplicações
pm2 restart all

echo "Deploy concluído!"
EOF
    
    # Script de status
    cat > "$INSTALL_DIR/scripts/status.sh" << 'EOF'
#!/bin/bash

echo "=== STATUS DO SISTEMA DISCADOR PREDITIVO ==="
echo ""

echo "PM2 Processes:"
pm2 list

echo ""
echo "System Services:"
systemctl status postgresql --no-pager -l
systemctl status redis-server --no-pager -l
systemctl status asterisk --no-pager -l
systemctl status nginx --no-pager -l

echo ""
echo "Disk Usage:"
df -h /opt/discador-preditivo

echo ""
echo "Memory Usage:"
free -h

echo ""
echo "Recent Logs:"
tail -n 5 /opt/discador-preditivo/logs/backend.log
EOF
    
    # Tornar scripts executáveis
    chmod +x "$INSTALL_DIR/scripts/"*.sh
    chown -R "$SYSTEM_USER:$SYSTEM_USER" "$INSTALL_DIR/scripts"
    
    log_success "Scripts de gerenciamento criados"
}

# Configurar logs e rotação
setup_logging() {
    log_header "CONFIGURANDO LOGS E ROTAÇÃO"
    
    # Criar diretório de logs do sistema
    mkdir -p /var/log/discador
    chown "$SYSTEM_USER:$SYSTEM_USER" /var/log/discador
    
    # Configurar logrotate
    cat > /etc/logrotate.d/discador << EOF
/var/log/discador/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su $SYSTEM_USER $SYSTEM_USER
}

$INSTALL_DIR/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    copytruncate
    su $SYSTEM_USER $SYSTEM_USER
}

/var/log/nginx/discador_*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    postrotate
        systemctl reload nginx
    endscript
}
EOF
    
    log_success "Logs e rotação configurados"
}

# Iniciar aplicações
start_applications() {
    log_header "INICIANDO APLICAÇÕES"
    
    # Iniciar aplicações via PM2 como usuário do sistema
    sudo -u "$SYSTEM_USER" bash -c "
        cd '$INSTALL_DIR' && 
        pm2 start ecosystem.config.js
    "
    check_command "Inicialização das aplicações PM2"
    
    # Salvar configuração PM2
    sudo -u "$SYSTEM_USER" pm2 save
    check_command "Salvamento da configuração PM2"
    
    # Aguardar inicialização
    sleep 10
    
    log_success "Aplicações iniciadas"
}

# Validação final
validate_installation() {
    log_header "VALIDANDO INSTALAÇÃO"
    
    local errors=0
    
    # Verificar serviços
    services=("postgresql" "redis-server" "asterisk" "nginx")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            log_success "Serviço $service: ATIVO"
        else
            log_error "Serviço $service: INATIVO"
            ((errors++))
        fi
    done
    
    # Verificar PM2
    if sudo -u "$SYSTEM_USER" pm2 list | grep -q "online"; then
        log_success "Aplicações PM2: ATIVAS"
    else
        log_error "Aplicações PM2: INATIVAS"
        ((errors++))
    fi
    
    # Verificar conectividade da API
    if curl -s "http://localhost:$API_PORT/health" > /dev/null; then
        log_success "API Backend: RESPONDENDO"
    else
        log_error "API Backend: SEM RESPOSTA"
        ((errors++))
    fi
    
    # Verificar frontend
    if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null; then
        log_success "Frontend React: RESPONDENDO"
    else
        log_error "Frontend React: SEM RESPOSTA"
        ((errors++))
    fi
    
    # Verificar NGINX
    if curl -s "http://localhost/health" > /dev/null; then
        log_success "NGINX Proxy: FUNCIONANDO"
    else
        log_error "NGINX Proxy: COM PROBLEMAS"
        ((errors++))
    fi
    
    # Verificar banco de dados
    if sudo -u "$SYSTEM_USER" psql "postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "PostgreSQL: CONECTADO"
    else
        log_error "PostgreSQL: ERRO DE CONEXÃO"
        ((errors++))
    fi
    
    # Verificar Asterisk AMI
    if timeout 3 bash -c "</dev/tcp/127.0.0.1/5038" 2>/dev/null; then
        log_success "Asterisk AMI: ACESSÍVEL"
    else
        log_error "Asterisk AMI: INACESSÍVEL"
        ((errors++))
    fi
    
    return $errors
}

# Mostrar informações finais
show_final_info() {
    log_header "INSTALAÇÃO CONCLUÍDA"
    
    echo -e "${GREEN}🎉 Sistema Discador Preditivo instalado com sucesso!${NC}"
    echo ""
    echo -e "${CYAN}📋 INFORMAÇÕES DO SISTEMA:${NC}"
    echo "  🌐 Domínio/IP: $DOMAIN_NAME"
    echo "  👤 Usuário do sistema: $SYSTEM_USER"
    echo "  📁 Diretório de instalação: $INSTALL_DIR"
    echo ""
    echo -e "${CYAN}🔗 URLs DE ACESSO:${NC}"
    echo "  🌍 Frontend: http://$DOMAIN_NAME"
    echo "  📚 API Docs: http://$DOMAIN_NAME/docs"
    echo "  ❤️  Health Check: http://$DOMAIN_NAME/health"
    echo ""
    echo -e "${CYAN}🔑 CREDENCIAIS DO BANCO:${NC}"
    echo "  📊 Banco: $DB_NAME"
    echo "  👤 Usuário: $DB_USER"
    echo "  🔐 Senha: $DB_PASSWORD"
    echo ""
    echo -e "${CYAN}📞 CONFIGURAÇÃO ASTERISK:${NC}"
    echo "  👤 Usuário AMI: $AMI_USER"
    echo "  🔐 Senha AMI: $AMI_PASSWORD"
    echo "  🔌 Host:Porta: 127.0.0.1:5038"
    echo ""
    echo -e "${CYAN}⚡ COMANDOS ÚTEIS:${NC}"
    echo "  📊 Status: $INSTALL_DIR/scripts/status.sh"
    echo "  💾 Backup: $INSTALL_DIR/scripts/backup.sh"
    echo "  🚀 Deploy: $INSTALL_DIR/scripts/deploy.sh"
    echo "  📋 PM2 Status: sudo -u $SYSTEM_USER pm2 status"
    echo "  📄 Logs: sudo -u $SYSTEM_USER pm2 logs"
    echo ""
    echo -e "${CYAN}📁 ARQUIVOS DE CONFIGURAÇÃO:${NC}"
    echo "  🔧 Backend: $INSTALL_DIR/backend/.env"
    echo "  🌐 NGINX: $NGINX_AVAILABLE/$PROJECT_NAME"
    echo "  📞 Asterisk: /etc/asterisk/manager.conf"
    echo "  ⚙️  PM2: $INSTALL_DIR/ecosystem.config.js"
    echo ""
    echo -e "${YELLOW}📝 PRÓXIMOS PASSOS:${NC}"
    echo "  1. Configure SSL/HTTPS se necessário"
    echo "  2. Adicione arquivos de áudio em /var/lib/asterisk/sounds/custom/"
    echo "  3. Configure extensões SIP no Asterisk"
    echo "  4. Teste o sistema criando uma campanha"
    echo "  5. Configure backup automático"
    echo ""
    echo -e "${CYAN}📄 Logs da instalação salvos em: $LOG_FILE${NC}"
}

# Função principal
main() {
    # Cabeçalho
    echo -e "${CYAN}"
    echo "=============================================="
    echo "🚀 INSTALAÇÃO AUTOMATIZADA"
    echo "   SISTEMA DISCADOR PREDITIVO COMPLETO"
    echo "=============================================="
    echo -e "${NC}"
    echo "Data/Hora: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # Criar log de instalação
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    chmod 644 "$LOG_FILE"
    
    # Verificações iniciais
    check_root
    check_os
    collect_user_input
    
    # Instalação das dependências
    update_system
    create_system_user
    
    # Instalação dos serviços
    install_postgresql
    install_redis
    install_nodejs
    install_python
    install_asterisk
    install_nginx
    
    # Configuração das aplicações
    setup_backend
    setup_frontend
    setup_pm2
    
    # Configuração do sistema
    setup_firewall
    setup_systemd_services
    create_management_scripts
    setup_logging
    
    # Inicialização
    start_applications
    
    # Validação e finalização
    if validate_installation; then
        show_final_info
        log_success "Instalação concluída com sucesso!"
        exit 0
    else
        log_error "Instalação concluída com alguns problemas. Verifique os logs."
        exit 1
    fi
}

# Tratamento de sinais
trap 'log_error "Instalação interrompida"; exit 1' INT TERM

# Verificar se há argumentos para instalação silenciosa
if [[ "$1" == "--silent" ]]; then
    DOMAIN_NAME=$(hostname -I | awk '{print $1}')
    log_info "Modo silencioso ativado. Usando IP: $DOMAIN_NAME"
fi

# Executar instalação
main "$@" 