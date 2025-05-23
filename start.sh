#!/bin/bash

# ===================================
# SCRIPT DE INICIALIZAÇÃO
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
PROJECT_DIR=$(dirname $(readlink -f $0))
ENV_FILE="$PROJECT_DIR/.env"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="/var/log/discador"
PID_FILE="$LOG_DIR/app.pid"

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

log_header() {
    echo -e "\n${CYAN}=================================="
    echo -e "🚀 $1"
    echo -e "==================================${NC}"
}

# Verificar se está rodando como usuário correto
check_user() {
    if [ "$USER" = "root" ]; then
        log_error "Este script não deve ser executado como root"
        log_info "Execute como usuário normal ou como 'discador'"
        exit 1
    fi
}

# Carregar variáveis de ambiente
load_env() {
    if [ -f "$ENV_FILE" ]; then
        source "$ENV_FILE"
        log_success "Variáveis de ambiente carregadas"
    else
        log_warning "Arquivo .env não encontrado em $ENV_FILE"
        log_info "Usando configurações padrão..."
        
        # Configurações padrão
        export DATABASE_URL="postgresql://discador:discador_2024_secure@localhost:5432/discador_db"
        export ASTERISK_HOST="127.0.0.1"
        export ASTERISK_PUERTO="5038"
        export API_HOST="0.0.0.0"
        export API_PORT="8000"
    fi
}

# Função para verificar serviços
check_service() {
    local service=$1
    if systemctl is-active --quiet $service 2>/dev/null; then
        log_success "$service está rodando"
        return 0
    else
        log_error "$service não está rodando"
        return 1
    fi
}

# Verificar dependências do sistema
check_dependencies() {
    log_header "VERIFICANDO DEPENDÊNCIAS"
    
    local all_ok=true
    
    # Verificar serviços principais
    if ! check_service postgresql; then
        log_warning "Tentando iniciar PostgreSQL..."
        sudo systemctl start postgresql || all_ok=false
    fi
    
    if ! check_service redis-server; then
        log_warning "Tentando iniciar Redis..."
        sudo systemctl start redis-server || all_ok=false
    fi
    
    if ! check_service asterisk; then
        log_warning "Tentando iniciar Asterisk..."
        sudo systemctl start asterisk || all_ok=false
    fi
    
    # Aguardar serviços inicializarem
    if [ "$all_ok" = false ]; then
        log_info "Aguardando serviços inicializarem..."
        sleep 5
    fi
    
    # Verificar conectividade do banco
    log_info "Verificando conectividade do banco de dados..."
    if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "Banco de dados acessível"
    else
        log_error "Não foi possível conectar ao banco de dados"
        log_info "URL: $DATABASE_URL"
        return 1
    fi
    
    # Verificar conectividade Asterisk AMI
    log_info "Verificando conectividade Asterisk AMI..."
    if timeout 3 bash -c "</dev/tcp/$ASTERISK_HOST/$ASTERISK_PUERTO" 2>/dev/null; then
        log_success "Asterisk AMI acessível"
    else
        log_error "Asterisk AMI não está acessível em $ASTERISK_HOST:$ASTERISK_PUERTO"
        return 1
    fi
    
    return 0
}

# Verificar e preparar ambiente Python
setup_python_env() {
    log_header "CONFIGURANDO AMBIENTE PYTHON"
    
    # Verificar se ambiente virtual existe
    if [ ! -d "$VENV_DIR" ]; then
        log_warning "Ambiente virtual não encontrado, criando..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Ativar ambiente virtual
    source "$VENV_DIR/bin/activate"
    log_success "Ambiente virtual ativado"
    
    # Verificar dependências Python
    log_info "Verificando dependências Python..."
    if python -c "import fastapi, sqlalchemy, asyncpg, uvicorn" 2>/dev/null; then
        log_success "Dependências Python OK"
    else
        log_warning "Instalando/atualizando dependências..."
        if [ -f "$PROJECT_DIR/requirements.txt" ]; then
            pip install --upgrade pip
            pip install -r "$PROJECT_DIR/requirements.txt"
            log_success "Dependências instaladas"
        else
            log_error "Arquivo requirements.txt não encontrado"
            return 1
        fi
    fi
}

# Verificar se aplicação já está rodando
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            log_warning "Aplicação já está rodando (PID: $pid)"
            log_info "Use './stop.sh' para parar antes de reiniciar"
            exit 1
        else
            log_info "Removendo PID file órfão..."
            rm "$PID_FILE"
        fi
    fi
    
    # Verificar por processos uvicorn
    if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
        log_warning "Processo uvicorn detectado. Parando..."
        pkill -f "uvicorn.*app.main:app" || true
        sleep 2
    fi
}

# Executar migrações se necessário
run_migrations() {
    log_header "VERIFICANDO MIGRAÇÕES"
    
    # Verificar se tabelas existem
    if psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM campanas_presione1;" > /dev/null 2>&1; then
        log_success "Banco de dados já configurado"
    else
        log_info "Executando migrações..."
        
        if [ -f "$PROJECT_DIR/migrations/create_presione1_tables.sql" ]; then
            psql "$DATABASE_URL" -f "$PROJECT_DIR/migrations/create_presione1_tables.sql"
            log_success "Migrações SQL executadas"
        else
            log_warning "Arquivo de migração não encontrado"
        fi
    fi
}

# Preparar diretórios
prepare_directories() {
    # Criar diretório de logs se não existir
    if [ ! -d "$LOG_DIR" ]; then
        sudo mkdir -p "$LOG_DIR" 2>/dev/null || mkdir -p "$HOME/logs"
        LOG_DIR="$HOME/logs"
        PID_FILE="$LOG_DIR/app.pid"
    fi
    
    # Ajustar permissões se possível
    if [ -w "$LOG_DIR" ]; then
        log_success "Diretório de logs preparado: $LOG_DIR"
    else
        log_warning "Sem permissão de escrita em $LOG_DIR"
        LOG_DIR="$PROJECT_DIR/logs"
        PID_FILE="$LOG_DIR/app.pid"
        mkdir -p "$LOG_DIR"
        log_info "Usando diretório local: $LOG_DIR"
    fi
}

# Iniciar aplicação
start_application() {
    log_header "INICIANDO APLICAÇÃO"
    
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Configurar variáveis de ambiente para a aplicação
    export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
    
    log_info "Iniciando servidor FastAPI..."
    log_info "Host: $API_HOST"
    log_info "Porta: $API_PORT"
    log_info "Logs: $LOG_DIR/app.log"
    
    # Iniciar em background
    nohup uvicorn app.main:app \
        --host "${API_HOST:-0.0.0.0}" \
        --port "${API_PORT:-8000}" \
        --workers 1 \
        --log-level info \
        > "$LOG_DIR/app.log" 2>&1 &
    
    local app_pid=$!
    echo $app_pid > "$PID_FILE"
    
    # Aguardar inicialização
    log_info "Aguardando inicialização da aplicação (PID: $app_pid)..."
    sleep 8
    
    # Verificar se está rodando
    if ps -p $app_pid > /dev/null; then
        # Testar endpoint de saúde
        local health_url="http://localhost:${API_PORT:-8000}/health"
        local max_attempts=10
        local attempt=0
        
        while [ $attempt -lt $max_attempts ]; do
            if curl -s "$health_url" > /dev/null 2>&1; then
                log_success "🎉 Sistema iniciado com sucesso!"
                log_info "🔗 API: http://localhost:${API_PORT:-8000}"
                log_info "📖 Docs: http://localhost:${API_PORT:-8000}/docs"
                log_info "📊 Health: $health_url"
                log_info "🆔 PID: $app_pid"
                log_info "📄 Logs: tail -f $LOG_DIR/app.log"
                log_info "🛑 Parar: $PROJECT_DIR/stop.sh"
                return 0
            fi
            
            attempt=$((attempt + 1))
            log_info "Tentativa $attempt/$max_attempts - aguardando resposta da API..."
            sleep 2
        done
        
        log_warning "Aplicação iniciou mas API não está respondendo"
        log_info "Verifique os logs: tail -f $LOG_DIR/app.log"
        return 1
    else
        log_error "Falha ao iniciar aplicação"
        log_info "Verifique os logs para mais detalhes:"
        if [ -f "$LOG_DIR/app.log" ]; then
            tail -n 10 "$LOG_DIR/app.log"
        fi
        return 1
    fi
}

# Função principal
main() {
    echo -e "${CYAN}"
    echo "=========================================="
    echo "🚀 INICIANDO DISCADOR PREDITIVO"
    echo "=========================================="
    echo -e "${NC}"
    
    check_user
    load_env
    prepare_directories
    
    if ! check_dependencies; then
        log_error "Dependências não atendidas. Verifique a instalação."
        exit 1
    fi
    
    check_running
    setup_python_env
    run_migrations
    
    if start_application; then
        exit 0
    else
        exit 1
    fi
}

# Tratamento de sinais
trap 'log_error "Processo interrompido"; exit 1' INT TERM

# Executar função principal
main "$@" 