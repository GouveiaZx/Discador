#!/bin/bash

# ===================================
# SCRIPT DE VALIDAÇÃO
# Sistema de Discador Preditivo
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

# Configurações
PROJECT_DIR=$(dirname $(readlink -f $0))
ENV_FILE="$PROJECT_DIR/.env"
VALIDATION_LOG="$PROJECT_DIR/validation_$(date +%Y%m%d_%H%M%S).log"

# Variáveis de controle
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNINGS=0

# Carregar variáveis de ambiente
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

# Configurações padrão
API_PORT=${API_PORT:-8000}
API_HOST=${API_HOST:-localhost}
DATABASE_URL=${DATABASE_URL:-"postgresql://discador:discador_2024_secure@localhost:5432/discador_db"}
ASTERISK_HOST=${ASTERISK_HOST:-127.0.0.1}
ASTERISK_PUERTO=${ASTERISK_PUERTO:-5038}

# Funções de log
log_test_start() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "\n${BLUE}[TESTE $TOTAL_TESTS]${NC} $1"
    echo "[TESTE $TOTAL_TESTS] $1" >> "$VALIDATION_LOG"
}

log_success() {
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "  ✅ ${GREEN}$1${NC}"
    echo "  ✅ $1" >> "$VALIDATION_LOG"
}

log_failure() {
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo -e "  ❌ ${RED}$1${NC}"
    echo "  ❌ $1" >> "$VALIDATION_LOG"
}

log_warning() {
    WARNINGS=$((WARNINGS + 1))
    echo -e "  ⚠️  ${YELLOW}$1${NC}"
    echo "  ⚠️  $1" >> "$VALIDATION_LOG"
}

log_info() {
    echo -e "  ℹ️  ${BLUE}$1${NC}"
    echo "  ℹ️  $1" >> "$VALIDATION_LOG"
}

# Cabeçalho
show_header() {
    echo -e "${CYAN}"
    echo "=============================================="
    echo "🧪 VALIDAÇÃO DO SISTEMA DISCADOR PREDITIVO"
    echo "=============================================="
    echo -e "${NC}"
    echo "Data/Hora: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Log de validação: $VALIDATION_LOG"
    echo ""
    
    # Criar log
    echo "=== VALIDAÇÃO SISTEMA DISCADOR PREDITIVO ===" > "$VALIDATION_LOG"
    echo "Data: $(date)" >> "$VALIDATION_LOG"
    echo "Usuário: $(whoami)" >> "$VALIDATION_LOG"
    echo "Servidor: $(hostname)" >> "$VALIDATION_LOG"
    echo "" >> "$VALIDATION_LOG"
}

# Teste 1: Verificar arquivos essenciais
test_essential_files() {
    log_test_start "Verificando arquivos essenciais do projeto"
    
    local files=(
        "app/main.py:Arquivo principal da aplicação"
        "requirements.txt:Dependências Python"
        "migrations/create_presione1_tables.sql:Migração do banco"
        "scripts/teste_voicemail.py:Script de teste"
        "start.sh:Script de inicialização"
        "stop.sh:Script de parada"
        "status.sh:Script de status"
    )
    
    local all_files_ok=true
    
    for file_info in "${files[@]}"; do
        local file_path=$(echo "$file_info" | cut -d: -f1)
        local file_desc=$(echo "$file_info" | cut -d: -f2)
        
        if [ -f "$PROJECT_DIR/$file_path" ]; then
            log_info "$file_desc: ENCONTRADO"
        else
            log_failure "$file_desc: NÃO ENCONTRADO ($file_path)"
            all_files_ok=false
        fi
    done
    
    if [ "$all_files_ok" = true ]; then
        log_success "Todos os arquivos essenciais encontrados"
    else
        log_failure "Alguns arquivos essenciais estão faltando"
        return 1
    fi
}

# Teste 2: Verificar serviços do sistema
test_system_services() {
    log_test_start "Verificando serviços do sistema"
    
    local services=(
        "postgresql:PostgreSQL"
        "redis-server:Redis"
        "asterisk:Asterisk"
    )
    
    local all_services_ok=true
    
    for service_info in "${services[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local service_desc=$(echo "$service_info" | cut -d: -f2)
        
        if systemctl is-active --quiet "$service_name" 2>/dev/null; then
            log_info "$service_desc: RODANDO"
        else
            log_failure "$service_desc: NÃO RODANDO"
            all_services_ok=false
        fi
    done
    
    if [ "$all_services_ok" = true ]; then
        log_success "Todos os serviços estão rodando"
    else
        log_failure "Alguns serviços não estão rodando"
        return 1
    fi
}

# Teste 3: Verificar conectividade do banco
test_database_connectivity() {
    log_test_start "Verificando conectividade do banco de dados"
    
    if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
        log_info "Conexão com PostgreSQL: OK"
        
        # Verificar tabelas
        local table_count=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('campanas_presione1', 'llamadas_presione1', 'listas_llamadas', 'numeros_llamada');" 2>/dev/null | xargs || echo "0")
        
        if [ "$table_count" -ge 3 ]; then
            log_info "Tabelas principais: ENCONTRADAS ($table_count tabelas)"
            log_success "Banco de dados configurado corretamente"
        else
            log_warning "Apenas $table_count tabelas encontradas, esperado pelo menos 3"
            log_failure "Banco de dados incompleto"
            return 1
        fi
    else
        log_failure "Não foi possível conectar ao banco de dados"
        log_info "URL testada: $DATABASE_URL"
        return 1
    fi
}

# Teste 4: Verificar conectividade do Redis
test_redis_connectivity() {
    log_test_start "Verificando conectividade do Redis"
    
    if redis-cli ping > /dev/null 2>&1; then
        local redis_memory=$(redis-cli info memory | grep "used_memory_human" | cut -d: -f2 | tr -d '\r' || echo "N/A")
        log_info "Redis conectado, memória em uso: $redis_memory"
        log_success "Redis funcionando corretamente"
    else
        log_failure "Não foi possível conectar ao Redis"
        return 1
    fi
}

# Teste 5: Verificar Asterisk AMI
test_asterisk_ami() {
    log_test_start "Verificando Asterisk AMI"
    
    if timeout 3 bash -c "</dev/tcp/$ASTERISK_HOST/$ASTERISK_PUERTO" 2>/dev/null; then
        log_info "AMI acessível em $ASTERISK_HOST:$ASTERISK_PUERTO"
        log_success "Asterisk AMI funcionando"
    else
        log_failure "Asterisk AMI não acessível em $ASTERISK_HOST:$ASTERISK_PUERTO"
        return 1
    fi
}

# Teste 6: Verificar ambiente Python
test_python_environment() {
    log_test_start "Verificando ambiente Python"
    
    if [ -d "$PROJECT_DIR/venv" ]; then
        log_info "Ambiente virtual: ENCONTRADO"
        
        # Ativar ambiente e testar dependências
        source "$PROJECT_DIR/venv/bin/activate"
        
        local dependencies=(
            "fastapi:FastAPI"
            "sqlalchemy:SQLAlchemy"
            "uvicorn:Uvicorn"
            "asyncpg:AsyncPG"
            "redis:Redis Python"
        )
        
        local deps_ok=true
        for dep_info in "${dependencies[@]}"; do
            local dep_name=$(echo "$dep_info" | cut -d: -f1)
            local dep_desc=$(echo "$dep_info" | cut -d: -f2)
            
            if python -c "import $dep_name" 2>/dev/null; then
                log_info "$dep_desc: INSTALADO"
            else
                log_failure "$dep_desc: NÃO INSTALADO"
                deps_ok=false
            fi
        done
        
        if [ "$deps_ok" = true ]; then
            log_success "Ambiente Python configurado corretamente"
        else
            log_failure "Algumas dependências Python estão faltando"
            return 1
        fi
    else
        log_failure "Ambiente virtual não encontrado"
        return 1
    fi
}

# Teste 7: Verificar se aplicação está rodando
test_application_running() {
    log_test_start "Verificando se aplicação está rodando"
    
    local uvicorn_pids=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null || echo "")
    
    if [ -n "$uvicorn_pids" ]; then
        local main_pid=$(echo "$uvicorn_pids" | head -n1)
        log_info "Aplicação rodando (PID: $main_pid)"
        log_success "Aplicação está ativa"
    else
        log_warning "Aplicação não está rodando"
        log_info "Tentando iniciar aplicação para testes..."
        
        # Tentar iniciar para testes
        cd "$PROJECT_DIR"
        if [ -f "start.sh" ]; then
            timeout 30 ./start.sh > /dev/null 2>&1 &
            sleep 10
            
            # Verificar novamente
            uvicorn_pids=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null || echo "")
            if [ -n "$uvicorn_pids" ]; then
                log_info "Aplicação iniciada com sucesso para testes"
            else
                log_failure "Não foi possível iniciar a aplicação"
                return 1
            fi
        else
            log_failure "Script start.sh não encontrado"
            return 1
        fi
    fi
}

# Teste 8: Verificar API Health Check
test_api_health() {
    log_test_start "Verificando API Health Check"
    
    local health_url="http://$API_HOST:$API_PORT/health"
    local max_attempts=5
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$health_url" > /dev/null 2>&1; then
            local response=$(curl -s "$health_url" 2>/dev/null || echo "")
            if echo "$response" | grep -q "healthy"; then
                log_info "Health check respondeu: OK"
                log_success "API Health funcionando"
                return 0
            else
                log_warning "Health check retornou resposta inesperada: $response"
            fi
        fi
        
        attempt=$((attempt + 1))
        log_info "Tentativa $attempt/$max_attempts falhada, aguardando..."
        sleep 3
    done
    
    log_failure "API Health não está respondendo após $max_attempts tentativas"
    log_info "URL testada: $health_url"
    return 1
}

# Teste 9: Verificar documentação da API
test_api_documentation() {
    log_test_start "Verificando documentação da API"
    
    local docs_url="http://$API_HOST:$API_PORT/docs"
    
    if curl -s "$docs_url" > /dev/null 2>&1; then
        log_info "Documentação acessível em: $docs_url"
        log_success "Documentação da API funcionando"
    else
        log_failure "Documentação da API não acessível"
        log_info "URL testada: $docs_url"
        return 1
    fi
}

# Teste 10: Testar criação de lista via API
test_api_list_creation() {
    log_test_start "Testando criação de lista via API"
    
    local api_url="http://$API_HOST:$API_PORT/api/v1/listas-llamadas"
    local test_data='{
        "nombre": "Lista Teste Validação",
        "descripcion": "Lista criada durante validação do sistema",
        "numeros": ["+5511999999999", "+5511888888888"]
    }'
    
    local response=$(curl -s -X POST "$api_url" \
        -H "Content-Type: application/json" \
        -d "$test_data" 2>/dev/null || echo "")
    
    if echo "$response" | grep -q '"id"'; then
        local lista_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
        log_info "Lista criada com ID: $lista_id"
        log_success "Criação de lista via API funcionando"
        
        # Guardar ID para limpeza posterior
        echo "$lista_id" > "$PROJECT_DIR/test_lista_id.tmp"
    else
        log_failure "Erro ao criar lista via API"
        log_info "Resposta: $response"
        return 1
    fi
}

# Teste 11: Testar criação de campanha via API
test_api_campaign_creation() {
    log_test_start "Testando criação de campanha via API"
    
    # Verificar se temos ID da lista
    local lista_id=""
    if [ -f "$PROJECT_DIR/test_lista_id.tmp" ]; then
        lista_id=$(cat "$PROJECT_DIR/test_lista_id.tmp")
    fi
    
    if [ -z "$lista_id" ]; then
        log_warning "ID da lista não disponível, usando ID 1"
        lista_id=1
    fi
    
    local api_url="http://$API_HOST:$API_PORT/api/v1/presione1/campanhas"
    local test_data="{
        \"nombre\": \"Campanha Teste Validação\",
        \"descripcion\": \"Campanha criada durante validação\",
        \"lista_llamadas_id\": $lista_id,
        \"mensaje_audio_url\": \"/var/lib/asterisk/sounds/custom/presione1_demo.wav\",
        \"detectar_voicemail\": true,
        \"mensaje_voicemail_url\": \"/var/lib/asterisk/sounds/custom/voicemail_demo.wav\",
        \"extension_transferencia\": \"100\",
        \"timeout_presione1\": 10,
        \"llamadas_simultaneas\": 1,
        \"tiempo_entre_llamadas\": 5
    }"
    
    local response=$(curl -s -X POST "$api_url" \
        -H "Content-Type: application/json" \
        -d "$test_data" 2>/dev/null || echo "")
    
    if echo "$response" | grep -q '"id"'; then
        local campana_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
        log_info "Campanha criada com ID: $campana_id"
        log_success "Criação de campanha via API funcionando"
        
        # Guardar ID para limpeza posterior
        echo "$campana_id" > "$PROJECT_DIR/test_campana_id.tmp"
    else
        log_failure "Erro ao criar campanha via API"
        log_info "Resposta: $response"
        return 1
    fi
}

# Teste 12: Testar listagem via API
test_api_listing() {
    log_test_start "Testando listagem via API"
    
    # Testar listagem de campanhas
    local campanhas_url="http://$API_HOST:$API_PORT/api/v1/presione1/campanhas"
    
    if curl -s "$campanhas_url" > /dev/null 2>&1; then
        local campanhas=$(curl -s "$campanhas_url" 2>/dev/null || echo "[]")
        
        if echo "$campanhas" | python3 -c "import sys, json; json.load(sys.stdin)" > /dev/null 2>&1; then
            local count=$(echo "$campanhas" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
            log_info "Campanhas encontradas: $count"
            log_success "Listagem via API funcionando"
        else
            log_failure "Resposta inválida da API de listagem"
            return 1
        fi
    else
        log_failure "Erro ao acessar listagem de campanhas"
        return 1
    fi
}

# Limpeza de dados de teste
cleanup_test_data() {
    log_test_start "Limpando dados de teste"
    
    # Remover campanha de teste
    if [ -f "$PROJECT_DIR/test_campana_id.tmp" ]; then
        local campana_id=$(cat "$PROJECT_DIR/test_campana_id.tmp")
        local delete_url="http://$API_HOST:$API_PORT/api/v1/presione1/campanhas/$campana_id"
        
        if curl -s -X DELETE "$delete_url" > /dev/null 2>&1; then
            log_info "Campanha de teste removida (ID: $campana_id)"
        else
            log_warning "Não foi possível remover campanha de teste"
        fi
        
        rm "$PROJECT_DIR/test_campana_id.tmp"
    fi
    
    # Remover lista de teste
    if [ -f "$PROJECT_DIR/test_lista_id.tmp" ]; then
        local lista_id=$(cat "$PROJECT_DIR/test_lista_id.tmp")
        local delete_url="http://$API_HOST:$API_PORT/api/v1/listas-llamadas/$lista_id"
        
        if curl -s -X DELETE "$delete_url" > /dev/null 2>&1; then
            log_info "Lista de teste removida (ID: $lista_id)"
        else
            log_warning "Não foi possível remover lista de teste"
        fi
        
        rm "$PROJECT_DIR/test_lista_id.tmp"
    fi
    
    log_success "Limpeza concluída"
}

# Mostrar resumo final
show_summary() {
    echo ""
    echo -e "${CYAN}=============================================="
    echo "📊 RESUMO DA VALIDAÇÃO"
    echo -e "===============================================${NC}"
    echo ""
    
    echo -e "Total de testes: ${BLUE}$TOTAL_TESTS${NC}"
    echo -e "Testes aprovados: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Testes falhados: ${RED}$FAILED_TESTS${NC}"
    echo -e "Avisos: ${YELLOW}$WARNINGS${NC}"
    
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}🎉 VALIDAÇÃO APROVADA!${NC}"
        echo -e "Sistema está funcionando corretamente."
        
        if [ $WARNINGS -gt 0 ]; then
            echo -e "${YELLOW}⚠️  Existem $WARNINGS avisos para revisar.${NC}"
        fi
    else
        echo -e "${RED}❌ VALIDAÇÃO FALHADA!${NC}"
        echo -e "$FAILED_TESTS teste(s) falharam."
        echo -e "Verifique o log para detalhes: $VALIDATION_LOG"
    fi
    
    echo ""
    echo -e "${CYAN}📄 Log completo salvo em: $VALIDATION_LOG${NC}"
    echo ""
    
    # Salvar resumo no log
    echo "" >> "$VALIDATION_LOG"
    echo "=== RESUMO ===" >> "$VALIDATION_LOG"
    echo "Total: $TOTAL_TESTS | Aprovados: $PASSED_TESTS | Falhados: $FAILED_TESTS | Avisos: $WARNINGS" >> "$VALIDATION_LOG"
    echo "Data final: $(date)" >> "$VALIDATION_LOG"
}

# Função principal
main() {
    show_header
    
    # Executar todos os testes
    test_essential_files || true
    test_system_services || true
    test_database_connectivity || true
    test_redis_connectivity || true
    test_asterisk_ami || true
    test_python_environment || true
    test_application_running || true
    test_api_health || true
    test_api_documentation || true
    test_api_list_creation || true
    test_api_campaign_creation || true
    test_api_listing || true
    cleanup_test_data || true
    
    show_summary
    
    # Retornar código apropriado
    if [ $FAILED_TESTS -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Tratamento de sinais
trap 'echo ""; echo "Validação interrompida"; exit 1' INT TERM

# Executar validação
main "$@" 