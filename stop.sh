#!/bin/bash

# ===================================
# SCRIPT DE PARADA
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
    echo -e "🛑 $1"
    echo -e "==================================${NC}"
}

# Verificar diretórios alternativos para PID
check_pid_locations() {
    local locations=(
        "/var/log/discador/app.pid"
        "$HOME/logs/app.pid"
        "$PROJECT_DIR/logs/app.pid"
        "$PROJECT_DIR/app.pid"
    )
    
    for location in "${locations[@]}"; do
        if [ -f "$location" ]; then
            PID_FILE="$location"
            LOG_DIR=$(dirname "$location")
            return 0
        fi
    done
    
    return 1
}

# Parar aplicação usando PID file
stop_by_pid() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        
        if ps -p $pid > /dev/null 2>&1; then
            log_info "Parando aplicação (PID: $pid)..."
            
            # Tentar parada suave
            kill $pid
            
            # Aguardar até 15 segundos
            local count=0
            while [ $count -lt 15 ] && ps -p $pid > /dev/null 2>&1; do
                sleep 1
                count=$((count + 1))
                echo -n "."
            done
            echo ""
            
            # Verificar se parou
            if ps -p $pid > /dev/null 2>&1; then
                log_warning "Processo não parou, forçando parada..."
                kill -9 $pid || true
                sleep 2
            fi
            
            # Verificar novamente
            if ps -p $pid > /dev/null 2>&1; then
                log_error "Não foi possível parar o processo $pid"
                return 1
            else
                log_success "Processo $pid parado com sucesso"
            fi
        else
            log_warning "Processo $pid não está rodando"
        fi
        
        # Remover PID file
        rm "$PID_FILE"
        log_info "Arquivo PID removido"
    else
        log_warning "Arquivo PID não encontrado: $PID_FILE"
        return 1
    fi
}

# Parar todos os processos relacionados
stop_all_processes() {
    log_info "Procurando processos relacionados..."
    
    # Processos uvicorn
    local uvicorn_pids=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null || true)
    if [ -n "$uvicorn_pids" ]; then
        log_info "Parando processos uvicorn..."
        echo "$uvicorn_pids" | while read pid; do
            if [ -n "$pid" ]; then
                log_info "Parando uvicorn PID: $pid"
                kill $pid || true
            fi
        done
        
        sleep 3
        
        # Force kill se necessário
        uvicorn_pids=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null || true)
        if [ -n "$uvicorn_pids" ]; then
            log_warning "Forçando parada de processos uvicorn..."
            pkill -9 -f "uvicorn.*app.main:app" || true
        fi
    fi
    
    # Processos Python relacionados ao discador
    local python_pids=$(pgrep -f "python.*discador" 2>/dev/null || true)
    if [ -n "$python_pids" ]; then
        log_info "Parando processos Python relacionados..."
        echo "$python_pids" | while read pid; do
            if [ -n "$pid" ]; then
                log_info "Parando Python PID: $pid"
                kill $pid || true
            fi
        done
    fi
    
    sleep 2
}

# Limpar recursos
cleanup_resources() {
    log_header "LIMPANDO RECURSOS"
    
    # Remover arquivos PID órfãos
    local pid_locations=(
        "/var/log/discador/app.pid"
        "$HOME/logs/app.pid"
        "$PROJECT_DIR/logs/app.pid"
        "$PROJECT_DIR/app.pid"
    )
    
    for location in "${pid_locations[@]}"; do
        if [ -f "$location" ]; then
            local pid=$(cat "$location" 2>/dev/null || echo "")
            if [ -n "$pid" ] && ! ps -p $pid > /dev/null 2>&1; then
                log_info "Removendo PID file órfão: $location"
                rm "$location"
            fi
        fi
    done
    
    # Limpar arquivos temporários
    if [ -d "$PROJECT_DIR/tmp" ]; then
        log_info "Limpando arquivos temporários..."
        rm -rf "$PROJECT_DIR/tmp/*" 2>/dev/null || true
    fi
    
    log_success "Limpeza concluída"
}

# Verificar status após parada
verify_stopped() {
    log_header "VERIFICANDO STATUS"
    
    # Verificar processos relacionados
    local uvicorn_count=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null | wc -l)
    local python_count=$(pgrep -f "python.*discador" 2>/dev/null | wc -l)
    
    if [ "$uvicorn_count" -eq 0 ] && [ "$python_count" -eq 0 ]; then
        log_success "✅ Todos os processos foram parados"
        
        # Verificar se API ainda responde
        local api_port=$(grep "API_PORT" "$PROJECT_DIR/.env" 2>/dev/null | cut -d'=' -f2 || echo "8000")
        if ! curl -s "http://localhost:$api_port/health" > /dev/null 2>&1; then
            log_success "✅ API não está mais respondendo"
        else
            log_warning "⚠️  API ainda está respondendo"
        fi
        
        return 0
    else
        log_warning "⚠️  Ainda existem processos rodando:"
        log_info "  Uvicorn: $uvicorn_count processos"
        log_info "  Python: $python_count processos"
        return 1
    fi
}

# Mostrar logs recentes se disponível
show_recent_logs() {
    if [ -f "$LOG_DIR/app.log" ]; then
        log_info "Últimas linhas do log:"
        echo "----------------------------------------"
        tail -n 5 "$LOG_DIR/app.log" 2>/dev/null || true
        echo "----------------------------------------"
    fi
}

# Função principal
main() {
    echo -e "${CYAN}"
    echo "=========================================="
    echo "🛑 PARANDO DISCADOR PREDITIVO"
    echo "=========================================="
    echo -e "${NC}"
    
    # Verificar se há algo para parar
    local has_processes=false
    
    if pgrep -f "uvicorn.*app.main:app" > /dev/null 2>&1; then
        has_processes=true
    fi
    
    if check_pid_locations; then
        has_processes=true
    fi
    
    if [ "$has_processes" = false ]; then
        log_info "Nenhum processo do discador preditivo encontrado"
        log_success "✅ Sistema já está parado"
        exit 0
    fi
    
    # Parar aplicação
    log_header "PARANDO APLICAÇÃO"
    
    # Tentar parar usando PID file primeiro
    if check_pid_locations && ! stop_by_pid; then
        log_warning "Falha ao parar usando PID file, tentando método alternativo..."
    fi
    
    # Parar todos os processos relacionados
    stop_all_processes
    
    # Limpar recursos
    cleanup_resources
    
    # Verificar se parou completamente
    if verify_stopped; then
        log_success "🎉 Sistema parado com sucesso!"
        show_recent_logs
        exit 0
    else
        log_error "❌ Alguns processos podem ainda estar rodando"
        log_info "Execute novamente ou use: sudo pkill -9 -f 'uvicorn.*app.main:app'"
        exit 1
    fi
}

# Tratamento de sinais
trap 'log_error "Processo interrompido"; exit 1' INT TERM

# Executar função principal
main "$@" 