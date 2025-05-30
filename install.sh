#!/bin/bash

# ===================================
# SCRIPT DE INSTALAÇÃO AUTOMATIZADA
# Sistema de Discador Preditivo
# ===================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
PROJECT_NAME="discador-preditivo"
USER_NAME="discador"
DB_NAME="discador_db"
DB_USER="discador"
DB_PASSWORD="discador_2024_secure"
AMI_PASSWORD="discador_ami_2024"

# Funções auxiliares
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

log_header() {
    echo -e "\n${CYAN}=================================="
    echo -e "🔧 $1"
    echo -e "==================================${NC}"
}

check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "Este script não deve ser executado como root"
        log_info "Execute como usuário normal com sudo"
        exit 1
    fi
}

check_system() {
    log_header "VERIFICANDO SISTEMA"
    
    # Verificar distribuição
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        log_error "Não foi possível detectar a distribuição Linux"
        exit 1
    fi
    
    log_info "Sistema detectado: $OS $VER"
    
    # Verificar se é Ubuntu ou Debian
    if [[ "$OS" != *"Ubuntu"* ]] && [[ "$OS" != *"Debian"* ]]; then
        log_warning "Este script foi testado apenas em Ubuntu e Debian"
        log_info "Continuando mesmo assim..."
    fi
    
    # Verificar recursos mínimos
    MEMORY=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
    DISK=$(df -h / | awk 'NR==2{print $4}' | sed 's/G//')
    
    log_info "Memória disponível: ${MEMORY}GB"
    log_info "Espaço em disco: ${DISK}GB"
    
    if [ "$MEMORY" -lt 4 ]; then
        log_warning "Recomendado pelo menos 4GB de RAM"
    fi
    
    if [ "${DISK%.*}" -lt 20 ]; then
        log_warning "Recomendado pelo menos 20GB de espaço livre"
    fi
}

install_packages() {
    log_header "INSTALANDO PACOTES DO SISTEMA"
    
    log_info "Atualizando repositórios..."
    sudo apt update
    
    log_info "Instalando pacotes essenciais..."
    sudo apt install -y \
        curl wget git unzip software-properties-common \
        build-essential pkg-config libssl-dev libffi-dev \
        python3 python3-pip python3-venv python3-dev \
        postgresql postgresql-contrib postgresql-client \
        redis-server \
        asterisk asterisk-dev asterisk-config asterisk-modules \
        asterisk-voicemail asterisk-sounds-core-en-wav \
        jq net-tools
    
    log_success "Pacotes instalados com sucesso"
}

create_user() {
    log_header "CRIANDO USUÁRIO DO SISTEMA"
    
    if id "$USER_NAME" &>/dev/null; then
        log_warning "Usuário $USER_NAME já existe"
    else
        log_info "Criando usuário $USER_NAME..."
        sudo useradd -m -s /bin/bash "$USER_NAME"
        sudo usermod -aG sudo "$USER_NAME"
        log_success "Usuário $USER_NAME criado"
    fi
    
    # Adicionar aos grupos necessários
    sudo usermod -aG asterisk "$USER_NAME"
    sudo usermod -aG audio asterisk
}

setup_python() {
    log_header "CONFIGURANDO PYTHON"
    
    # Instalar Poetry
    if ! command -v poetry &> /dev/null; then
        log_info "Instalando Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        export PATH="$HOME/.local/bin:$PATH"
        log_success "Poetry instalado"
    else
        log_warning "Poetry já está instalado"
    fi
    
    # Verificar versão do Python
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    log_info "Python versão: $PYTHON_VERSION"
    
    if [ "$(echo "$PYTHON_VERSION >= 3.9" | bc -l)" -eq 0 ]; then
        log_warning "Recomendado Python 3.9+, mas continuando..."
    fi
}

setup_postgresql() {
    log_header "CONFIGURANDO POSTGRESQL"
    
    # Iniciar serviços
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Verificar se banco já existe
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log_warning "Banco $DB_NAME já existe"
    else
        log_info "Criando banco de dados..."
        sudo -u postgres psql << EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
\q
EOF
        log_success "Banco de dados configurado"
    fi
    
    # Configurar autenticação
    PG_VERSION=$(sudo -u postgres psql -c "SHOW server_version;" | grep -oP '\d+\.\d+' | head -1)
    PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
    PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
    
    if [ -f "$PG_CONF" ]; then
        sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"
        
        if ! grep -q "host.*$DB_NAME.*$DB_USER" "$PG_HBA"; then
            echo "host    $DB_NAME    $DB_USER    127.0.0.1/32    md5" | sudo tee -a "$PG_HBA"
        fi
        
        sudo systemctl restart postgresql
        log_success "PostgreSQL configurado"
    else
        log_warning "Arquivo de configuração do PostgreSQL não encontrado"
    fi
}

setup_redis() {
    log_header "CONFIGURANDO REDIS"
    
    # Configurar Redis
    sudo sed -i 's/# maxmemory 256mb/maxmemory 256mb/' /etc/redis/redis.conf
    sudo sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
    
    # Iniciar serviços
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    log_success "Redis configurado"
}

setup_asterisk() {
    log_header "CONFIGURANDO ASTERISK"
    
    # Backup das configurações originais
    sudo cp /etc/asterisk/manager.conf /etc/asterisk/manager.conf.backup 2>/dev/null || true
    sudo cp /etc/asterisk/sip.conf /etc/asterisk/sip.conf.backup 2>/dev/null || true
    sudo cp /etc/asterisk/extensions.conf /etc/asterisk/extensions.conf.backup 2>/dev/null || true
    
    # Configurar AMI
    sudo tee /etc/asterisk/manager.conf << EOF
[general]
enabled = yes
port = 5038
bindaddr = 127.0.0.1

[discador_ami]
secret = $AMI_PASSWORD
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

; Configure seus trunks SIP aqui
[trunk_provider]
type = peer
; host = seu.provedor.voip.com
; username = seu_usuario
; secret = sua_senha
; fromuser = seu_usuario
; fromdomain = seu.provedor.voip.com
; insecure = port,invite
; canreinvite = no
; context = from-trunk
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

; Contexto para extensões internas
[internal]
exten => 100,1,NoOp(Transferência para extensão 100)
exten => 100,n,Dial(SIP/100,30)
exten => 100,n,Hangup()
EOF
    
    # Reiniciar Asterisk
    sudo systemctl restart asterisk
    sudo systemctl enable asterisk
    
    log_success "Asterisk configurado"
}

clone_project() {
    log_header "CLONANDO PROJETO"
    
    PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
    
    if [ -d "$PROJECT_DIR" ]; then
        log_warning "Diretório do projeto já existe: $PROJECT_DIR"
        log_info "Pulando clonagem..."
    else
        log_info "Criando diretório do projeto..."
        sudo -u "$USER_NAME" mkdir -p "$PROJECT_DIR"
        
        # Copiar arquivos atuais se estivermos no diretório do projeto
        if [ -f "app/main.py" ]; then
            log_info "Copiando arquivos do projeto atual..."
            sudo -u "$USER_NAME" cp -r . "$PROJECT_DIR/"
        else
            log_warning "Arquivos do projeto não encontrados no diretório atual"
            log_info "Você precisará copiar os arquivos manualmente para: $PROJECT_DIR"
        fi
    fi
    
    log_success "Projeto preparado em: $PROJECT_DIR"
}

setup_python_env() {
    log_header "CONFIGURANDO AMBIENTE PYTHON"
    
    PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
    
    # Mudar para usuário discador
    sudo -u "$USER_NAME" bash << EOF
cd "$PROJECT_DIR"

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

# Ativar ambiente e instalar dependências
source venv/bin/activate

# Instalar dependências
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependências instaladas"
else
    echo "⚠️  Arquivo requirements.txt não encontrado"
fi
EOF
    
    log_success "Ambiente Python configurado"
}

create_env_file() {
    log_header "CRIANDO ARQUIVO DE CONFIGURAÇÃO"
    
    PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
    ENV_FILE="$PROJECT_DIR/.env"
    
    sudo -u "$USER_NAME" tee "$ENV_FILE" << EOF
# ===================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ===================================
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# ===================================
# CONFIGURAÇÃO DO ASTERISK
# ===================================
ASTERISK_HOST=127.0.0.1
ASTERISK_PUERTO=5038
ASTERISK_USUARIO=discador_ami
ASTERISK_PASSWORD=$AMI_PASSWORD

# ===================================
# CONFIGURAÇÃO DA API
# ===================================
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
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
# CONFIGURAÇÃO DE MONITORAMENTO
# ===================================
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_URL=/health

# ===================================
# CONFIGURAÇÃO DE SEGURANÇA
# ===================================
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
EOF
    
    sudo -u "$USER_NAME" chmod 600 "$ENV_FILE"
    log_success "Arquivo .env criado"
}

setup_directories() {
    log_header "CONFIGURANDO DIRETÓRIOS"
    
    # Criar diretórios necessários
    sudo mkdir -p /var/log/discador
    sudo mkdir -p /var/lib/asterisk/sounds/custom
    sudo mkdir -p /var/spool/asterisk/monitor
    sudo mkdir -p /etc/discador
    
    # Configurar permissões
    sudo chown -R "$USER_NAME:$USER_NAME" /var/log/discador
    sudo chown -R asterisk:asterisk /var/lib/asterisk/sounds/custom
    sudo chown -R asterisk:asterisk /var/spool/asterisk/monitor
    sudo chmod -R 755 /var/lib/asterisk/sounds/custom
    
    # Adicionar usuário ao grupo asterisk
    sudo usermod -aG asterisk "$USER_NAME"
    
    log_success "Diretórios configurados"
}

setup_database() {
    log_header "CONFIGURANDO BANCO DE DADOS"
    
    PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
    
    sudo -u "$USER_NAME" bash << EOF
cd "$PROJECT_DIR"
source venv/bin/activate

# Executar migrações se o arquivo existir
if [ -f "migrations/create_presione1_tables.sql" ]; then
    psql postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME -f migrations/create_presione1_tables.sql
    echo "✅ Migrações SQL executadas"
fi

# Popular dados de exemplo se o script existir
if [ -f "scripts/populate_sample_data.py" ]; then
    python scripts/populate_sample_data.py
    echo "✅ Dados de exemplo criados"
fi
EOF
    
    log_success "Banco de dados configurado"
}

create_audio_files() {
    log_header "CONFIGURANDO ARQUIVOS DE ÁUDIO"
    
    # Criar arquivos de áudio de exemplo (texto para fala)
    SOUNDS_DIR="/var/lib/asterisk/sounds/custom"
    
    # Criar arquivo de áudio simples (beep)
    sudo -u asterisk bash << EOF
cd "$SOUNDS_DIR"

# Criar áudio simples para presione1
echo "Criando arquivo de áudio para Presione 1..."
# Este é um placeholder - substitua por arquivos reais
touch presione1_demo.wav
touch voicemail_demo.wav

echo "⚠️  IMPORTANTE: Substitua estes arquivos por gravações reais:"
echo "  - presione1_demo.wav: Mensagem principal"
echo "  - voicemail_demo.wav: Mensagem para voicemail"
EOF
    
    log_warning "Arquivos de áudio de exemplo criados"
    log_info "IMPORTANTE: Substitua por gravações reais em $SOUNDS_DIR"
}

create_scripts() {
    log_header "CRIANDO SCRIPTS DE CONTROLE"
    
    PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
    
    # Os scripts já devem estar no projeto, apenas tornar executáveis
    sudo -u "$USER_NAME" bash << EOF
cd "$PROJECT_DIR"

# Tornar scripts executáveis
chmod +x start.sh stop.sh status.sh validate.sh 2>/dev/null || true

echo "✅ Scripts de controle preparados"
EOF
    
    log_success "Scripts criados"
}

create_systemd_service() {
    log_header "CONFIGURANDO SERVIÇO SYSTEMD"
    
    sudo tee /etc/systemd/system/discador-preditivo.service << EOF
[Unit]
Description=Sistema de Discador Preditivo
After=network.target postgresql.service redis-server.service asterisk.service
Requires=postgresql.service redis-server.service asterisk.service

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=/home/$USER_NAME/$PROJECT_NAME
Environment=PATH=/home/$USER_NAME/$PROJECT_NAME/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/$USER_NAME/$PROJECT_NAME/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable discador-preditivo
    
    log_success "Serviço systemd configurado"
}

run_tests() {
    log_header "EXECUTANDO TESTES DE VALIDAÇÃO"
    
    PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
    
    # Iniciar serviços
    sudo systemctl start postgresql redis-server asterisk
    
    # Aguardar inicialização
    sleep 5
    
    # Iniciar aplicação
    sudo systemctl start discador-preditivo
    
    # Aguardar aplicação inicializar
    sleep 10
    
    # Executar testes básicos
    sudo -u "$USER_NAME" bash << EOF
cd "$PROJECT_DIR"

# Teste de conectividade
echo "🔍 Testando conectividade..."

# Teste API
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ API: OK"
else
    echo "❌ API: ERRO"
fi

# Teste banco
if psql postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ PostgreSQL: OK"
else
    echo "❌ PostgreSQL: ERRO"
fi

# Teste Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: OK"
else
    echo "❌ Redis: ERRO"
fi

# Teste Asterisk AMI
if timeout 2 bash -c "</dev/tcp/127.0.0.1/5038" 2>/dev/null; then
    echo "✅ Asterisk AMI: OK"
else
    echo "❌ Asterisk AMI: ERRO"
fi
EOF
    
    log_success "Testes básicos executados"
}

show_summary() {
    log_header "INSTALAÇÃO CONCLUÍDA"
    
    echo -e "${GREEN}🎉 Sistema de Discador Preditivo instalado com sucesso!${NC}"
    echo ""
    echo -e "${YELLOW}📋 RESUMO DA INSTALAÇÃO:${NC}"
    echo "  👤 Usuário: $USER_NAME"
    echo "  📁 Diretório: /home/$USER_NAME/$PROJECT_NAME"
    echo "  🗄️  Banco: $DB_NAME"
    echo "  🔗 API: http://localhost:8000"
    echo ""
    echo -e "${YELLOW}🔧 COMANDOS ÚTEIS:${NC}"
    echo "  sudo systemctl status discador-preditivo  # Status do serviço"
    echo "  sudo systemctl restart discador-preditivo # Reiniciar serviço"
    echo "  sudo -u $USER_NAME /home/$USER_NAME/$PROJECT_NAME/status.sh     # Status detalhado"
    echo "  sudo -u $USER_NAME /home/$USER_NAME/$PROJECT_NAME/validate.sh   # Validar instalação"
    echo ""
    echo -e "${YELLOW}📖 PRÓXIMOS PASSOS:${NC}"
    echo "  1. Acessar documentação: http://localhost:8000/docs"
    echo "  2. Configurar arquivos de áudio em: /var/lib/asterisk/sounds/custom/"
    echo "  3. Configurar trunk SIP em: /etc/asterisk/sip.conf"
    echo "  4. Executar testes: sudo -u $USER_NAME python /home/$USER_NAME/$PROJECT_NAME/scripts/teste_voicemail.py"
    echo ""
    echo -e "${CYAN}📞 SUPORTE:${NC}"
    echo "  📄 Logs: /var/log/discador/app.log"
    echo "  📚 Docs: /home/$USER_NAME/$PROJECT_NAME/docs/"
    echo ""
}

main() {
    echo -e "${CYAN}"
    echo "=========================================="
    echo "🚀 INSTALADOR DO DISCADOR PREDITIVO"
    echo "=========================================="
    echo -e "${NC}"
    
    check_root
    check_system
    
    echo ""
    log_info "Esta instalação irá:"
    log_info "• Instalar PostgreSQL, Redis, Asterisk, Python"
    log_info "• Criar usuário '$USER_NAME'"
    log_info "• Configurar banco de dados '$DB_NAME'"
    log_info "• Configurar serviços automaticamente"
    log_info "• Criar ambiente completo do sistema"
    echo ""
    
    read -p "Deseja continuar? (s/N): " confirm
    if [[ ! "$confirm" =~ ^[Ss]$ ]]; then
        log_info "Instalação cancelada"
        exit 0
    fi
    
    # Executar instalação
    install_packages
    create_user
    setup_python
    setup_postgresql
    setup_redis
    setup_asterisk
    clone_project
    setup_python_env
    create_env_file
    setup_directories
    setup_database
    create_audio_files
    create_scripts
    create_systemd_service
    run_tests
    show_summary
    
    log_success "🎯 Instalação concluída com sucesso!"
}

# Executar instalação
main "$@" 