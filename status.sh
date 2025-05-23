#!/bin/bash

# ===================================
# SCRIPT DE STATUS
# Sistema de Discador Preditivo
# ===================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configurações
PROJECT_DIR=$(dirname $(readlink -f $0))
ENV_FILE="$PROJECT_DIR/.env"
LOG_DIR="/var/log/discador"

# Carregar variáveis de ambiente se disponível
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

# Configurações padrão
API_PORT=${API_PORT:-8000}
DB_NAME=${DB_NAME:-discador_db}
DB_USER=${DB_USER:-discador}
ASTERISK_HOST=${ASTERISK_HOST:-127.0.0.1}
ASTERISK_PUERTO=${ASTERISK_PUERTO:-5038}

# Função para status colorido
status_ok() {
    echo -e "  ✅ $1: ${GREEN}$2${NC}"
}

status_warning() {
    echo -e "  ⚠️  $1: ${YELLOW}$2${NC}"
}

status_error() {
    echo -e "  ❌ $1: ${RED}$2${NC}"
}

status_info() {
    echo -e "  ℹ️  $1: ${BLUE}$2${NC}"
}

# Cabeçalho
show_header() {
    echo -e "${CYAN}"
    echo "=============================================="
    echo "🔍 STATUS DO SISTEMA DISCADOR PREDITIVO"
    echo "=============================================="
    echo -e "${NC}"
    echo "Data/Hora: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Servidor: $(hostname)"
    echo "Usuário: $(whoami)"
    echo ""
}

# Verificar serviços do sistema
check_system_services() {
    echo -e "${YELLOW}📋 SERVIÇOS DO SISTEMA${NC}"
    echo "----------------------------------------------"
    
    # PostgreSQL
    if systemctl is-active --quiet postgresql 2>/dev/null; then
        local pg_version=$(sudo -u postgres psql -c "SHOW server_version;" 2>/dev/null | grep -oP '\d+\.\d+' | head -1 || echo "N/A")
        status_ok "PostgreSQL" "RODANDO (v$pg_version)"
    else
        status_error "PostgreSQL" "PARADO"
    fi
    
    # Redis
    if systemctl is-active --quiet redis-server 2>/dev/null; then
        local redis_version=$(redis-cli --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1 || echo "N/A")
        status_ok "Redis" "RODANDO (v$redis_version)"
    else
        status_error "Redis" "PARADO"
    fi
    
    # Asterisk
    if systemctl is-active --quiet asterisk 2>/dev/null; then
        local ast_version=$(asterisk -V 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1 || echo "N/A")
        status_ok "Asterisk" "RODANDO (v$ast_version)"
    else
        status_error "Asterisk" "PARADO"
    fi
    
    echo ""
}

# Verificar aplicação
check_application() {
    echo -e "${YELLOW}🚀 APLICAÇÃO DISCADOR${NC}"
    echo "----------------------------------------------"
    
    # Verificar processo
    local uvicorn_pids=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null || echo "")
    
    if [ -n "$uvicorn_pids" ]; then
        local pid_count=$(echo "$uvicorn_pids" | wc -w)
        local main_pid=$(echo "$uvicorn_pids" | head -n1)
        
        # Informações do processo
        local cpu_usage=$(ps -p $main_pid -o %cpu --no-headers 2>/dev/null | xargs || echo "N/A")
        local mem_usage=$(ps -p $main_pid -o %mem --no-headers 2>/dev/null | xargs || echo "N/A")
        local start_time=$(ps -p $main_pid -o lstart --no-headers 2>/dev/null | xargs || echo "N/A")
        
        status_ok "Processo Principal" "RODANDO (PID: $main_pid)"
        status_info "Processos Ativos" "$pid_count"
        status_info "CPU" "${cpu_usage}%"
        status_info "Memória" "${mem_usage}%"
        status_info "Iniciado em" "$start_time"
        
        # Verificar PID file
        local pid_locations=(
            "/var/log/discador/app.pid"
            "$HOME/logs/app.pid"
            "$PROJECT_DIR/logs/app.pid"
            "$PROJECT_DIR/app.pid"
        )
        
        local pid_file_found=false
        for location in "${pid_locations[@]}"; do
            if [ -f "$location" ]; then
                local file_pid=$(cat "$location" 2>/dev/null || echo "")
                if [ "$file_pid" = "$main_pid" ]; then
                    status_ok "Arquivo PID" "$location"
                    pid_file_found=true
                    break
                fi
            fi
        done
        
        if [ "$pid_file_found" = false ]; then
            status_warning "Arquivo PID" "NÃO ENCONTRADO"
        fi
    else
        status_error "Aplicação" "PARADA"
    fi
    
    echo ""
}

# Verificar conectividade
check_connectivity() {
    echo -e "${YELLOW}🔗 CONECTIVIDADE${NC}"
    echo "----------------------------------------------"
    
    # API Health Check
    local health_url="http://localhost:$API_PORT/health"
    if curl -s "$health_url" > /dev/null 2>&1; then
        local response=$(curl -s "$health_url" 2>/dev/null || echo "")
        if echo "$response" | grep -q "healthy"; then
            status_ok "API Health" "SAUDÁVEL"
        else
            status_warning "API Health" "RESPOSTA INVÁLIDA"
        fi
    else
        status_error "API Health" "SEM RESPOSTA"
    fi
    
    # API Documentation
    local docs_url="http://localhost:$API_PORT/docs"
    if curl -s "$docs_url" > /dev/null 2>&1; then
        status_ok "Documentação API" "ACESSÍVEL"
    else
        status_error "Documentação API" "INACESSÍVEL"
    fi
    
    # Banco de dados
    if [ -n "$DATABASE_URL" ]; then
        if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
            # Verificar tabelas principais
            local table_count=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('campanas_presione1', 'llamadas_presione1');" 2>/dev/null | xargs || echo "0")
            if [ "$table_count" -eq 2 ]; then
                status_ok "PostgreSQL" "CONECTADO E CONFIGURADO"
            else
                status_warning "PostgreSQL" "CONECTADO MAS INCOMPLETO"
            fi
        else
            status_error "PostgreSQL" "ERRO DE CONEXÃO"
        fi
    else
        status_warning "PostgreSQL" "URL NÃO CONFIGURADA"
    fi
    
    # Redis
    if redis-cli ping > /dev/null 2>&1; then
        local redis_memory=$(redis-cli info memory | grep "used_memory_human" | cut -d: -f2 | tr -d '\r' || echo "N/A")
        status_ok "Redis" "CONECTADO ($redis_memory)"
    else
        status_error "Redis" "ERRO DE CONEXÃO"
    fi
    
    # Asterisk AMI
    if timeout 3 bash -c "</dev/tcp/$ASTERISK_HOST/$ASTERISK_PUERTO" 2>/dev/null; then
        status_ok "Asterisk AMI" "ACESSÍVEL"
    else
        status_error "Asterisk AMI" "INACESSÍVEL"
    fi
    
    echo ""
}

# Verificar recursos do sistema
check_system_resources() {
    echo -e "${YELLOW}💻 RECURSOS DO SISTEMA${NC}"
    echo "----------------------------------------------"
    
    # Memória
    local mem_info=$(free -h | awk '/^Mem:/ {print $3"/"$2" ("int($3/$2*100)"%)")' )
    status_info "Memória" "$mem_info"
    
    # Disco
    local disk_info=$(df -h / | awk 'NR==2 {print $3"/"$2" ("$5")"}')
    status_info "Disco (/)" "$disk_info"
    
    # Load Average
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | xargs)
    status_info "Load Average" "$load_avg"
    
    # CPU Cores
    local cpu_cores=$(nproc)
    status_info "CPU Cores" "$cpu_cores"
    
    # Uptime
    local uptime_info=$(uptime -p 2>/dev/null || uptime | awk '{print $3,$4}')
    status_info "Uptime" "$uptime_info"
    
    echo ""
}

# Verificar configuração
check_configuration() {
    echo -e "${YELLOW}⚙️  CONFIGURAÇÃO${NC}"
    echo "----------------------------------------------"
    
    # Arquivo .env
    if [ -f "$ENV_FILE" ]; then
        local env_size=$(stat -c%s "$ENV_FILE" 2>/dev/null || echo "0")
        status_ok "Arquivo .env" "ENCONTRADO (${env_size} bytes)"
    else
        status_warning "Arquivo .env" "NÃO ENCONTRADO"
    fi
    
    # Ambiente virtual Python
    if [ -d "$PROJECT_DIR/venv" ]; then
        local python_version=$("$PROJECT_DIR/venv/bin/python" --version 2>/dev/null | cut -d' ' -f2 || echo "N/A")
        status_ok "Virtual Env" "CONFIGURADO (Python $python_version)"
    else
        status_warning "Virtual Env" "NÃO ENCONTRADO"
    fi
    
    # Requirements.txt
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        local req_count=$(grep -c "^[^#]" "$PROJECT_DIR/requirements.txt" 2>/dev/null || echo "0")
        status_ok "Requirements" "ENCONTRADO ($req_count dependências)"
    else
        status_warning "Requirements" "NÃO ENCONTRADO"
    fi
    
    # Diretórios importantes
    local directories=(
        "/var/lib/asterisk/sounds/custom:Áudios Asterisk"
        "/var/log/discador:Logs Sistema"
        "$PROJECT_DIR/migrations:Migrações"
        "$PROJECT_DIR/scripts:Scripts"
    )
    
    for dir_info in "${directories[@]}"; do
        local dir_path=$(echo "$dir_info" | cut -d: -f1)
        local dir_name=$(echo "$dir_info" | cut -d: -f2)
        
        if [ -d "$dir_path" ]; then
            local file_count=$(find "$dir_path" -type f 2>/dev/null | wc -l || echo "0")
            status_ok "$dir_name" "EXISTE ($file_count arquivos)"
        else
            status_warning "$dir_name" "NÃO EXISTE"
        fi
    done
    
    echo ""
}

# Verificar logs
check_logs() {
    echo -e "${YELLOW}📄 LOGS E MONITORAMENTO${NC}"
    echo "----------------------------------------------"
    
    # Localizar logs
    local log_locations=(
        "/var/log/discador/app.log"
        "$HOME/logs/app.log"
        "$PROJECT_DIR/logs/app.log"
    )
    
    local main_log=""
    for location in "${log_locations[@]}"; do
        if [ -f "$location" ]; then
            main_log="$location"
            break
        fi
    done
    
    if [ -n "$main_log" ]; then
        local log_size=$(stat -c%s "$main_log" 2>/dev/null || echo "0")
        local log_lines=$(wc -l < "$main_log" 2>/dev/null || echo "0")
        local log_modified=$(stat -c%y "$main_log" 2>/dev/null | cut -d. -f1 || echo "N/A")
        
        status_ok "Log Principal" "$main_log"
        status_info "Tamanho" "$(numfmt --to=iec $log_size 2>/dev/null || echo "${log_size} bytes")"
        status_info "Linhas" "$log_lines"
        status_info "Modificado" "$log_modified"
        
        # Mostrar últimas linhas (apenas erros/warnings)
        echo ""
        echo -e "${PURPLE}📖 Últimas entradas relevantes:${NC}"
        echo "----------------------------------------------"
        if grep -E "(ERROR|WARNING|CRITICAL)" "$main_log" 2>/dev/null | tail -n 3 | while read line; do
            echo "  $line"
        done; then
            :
        else
            echo "  Nenhum erro ou warning recente encontrado"
        fi
    else
        status_warning "Log Principal" "NÃO ENCONTRADO"
    fi
    
    echo ""
}

# Verificar campanhas ativas (se API estiver respondendo)
check_campaigns() {
    echo -e "${YELLOW}🎯 CAMPANHAS ATIVAS${NC}"
    echo "----------------------------------------------"
    
    local api_url="http://localhost:$API_PORT/api/v1/presione1/campanhas"
    
    if curl -s "$api_url" > /dev/null 2>&1; then
        local campaigns=$(curl -s "$api_url" 2>/dev/null || echo "[]")
        
        if echo "$campaigns" | jq . > /dev/null 2>&1; then
            local total_campaigns=$(echo "$campaigns" | jq length 2>/dev/null || echo "0")
            local active_campaigns=$(echo "$campaigns" | jq '[.[] | select(.activa == true)] | length' 2>/dev/null || echo "0")
            local running_campaigns=$(echo "$campaigns" | jq '[.[] | select(.activa == true and .pausada == false)] | length' 2>/dev/null || echo "0")
            
            status_info "Total" "$total_campaigns campanhas"
            status_info "Ativas" "$active_campaigns campanhas"
            
            if [ "$running_campaigns" -gt 0 ]; then
                status_ok "Em Execução" "$running_campaigns campanhas"
            else
                status_info "Em Execução" "0 campanhas"
            fi
        else
            status_warning "Campanhas" "RESPOSTA INVÁLIDA DA API"
        fi
    else
        status_error "Campanhas" "API INACESSÍVEL"
    fi
    
    echo ""
}

# Mostrar URLs úteis
show_useful_urls() {
    echo -e "${YELLOW}🔗 LINKS ÚTEIS${NC}"
    echo "----------------------------------------------"
    echo "  📖 Documentação API: http://localhost:$API_PORT/docs"
    echo "  🔍 Health Check: http://localhost:$API_PORT/health"
    echo "  📊 Métricas: http://localhost:$API_PORT/metrics"
    echo "  🎯 Campanhas: http://localhost:$API_PORT/api/v1/presione1/campanhas"
    echo ""
}

# Mostrar comandos úteis
show_useful_commands() {
    echo -e "${YELLOW}⚡ COMANDOS ÚTEIS${NC}"
    echo "----------------------------------------------"
    echo "  🚀 Iniciar: $PROJECT_DIR/start.sh"
    echo "  🛑 Parar: $PROJECT_DIR/stop.sh"
    echo "  🔄 Reiniciar: $PROJECT_DIR/stop.sh && $PROJECT_DIR/start.sh"
    echo "  🧪 Validar: $PROJECT_DIR/validate.sh"
    echo "  📄 Logs: tail -f ${main_log:-/var/log/discador/app.log}"
    
    if [ -f "$PROJECT_DIR/scripts/teste_voicemail.py" ]; then
        echo "  🎙️  Teste Voicemail: python $PROJECT_DIR/scripts/teste_voicemail.py"
    fi
    
    echo ""
}

# Função principal
main() {
    show_header
    check_system_services
    check_application
    check_connectivity
    check_system_resources
    check_configuration
    check_logs
    check_campaigns
    show_useful_urls
    show_useful_commands
    
    echo -e "${CYAN}=============================================="
    echo "Status verificado em $(date '+%H:%M:%S')"
    echo -e "===============================================${NC}"
}

# Executar verificação
main "$@" 