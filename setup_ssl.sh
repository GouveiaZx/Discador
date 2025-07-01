#!/bin/bash

# ===================================
# CONFIGURAÇÃO SSL/HTTPS AUTOMATIZADA
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
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
LOG_FILE="/var/log/ssl_setup_discador.log"

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
    echo -e "🔒 $1"
    echo -e "==================================${NC}"
    echo "=== $1 ===" >> "$LOG_FILE"
}

# Verificar se está rodando como root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Este script deve ser executado como root (sudo)"
        exit 1
    fi
}

# Verificar se NGINX está instalado
check_nginx() {
    if ! command -v nginx &> /dev/null; then
        log_error "NGINX não está instalado. Execute primeiro o script de instalação principal."
        exit 1
    fi
    
    if ! systemctl is-active --quiet nginx; then
        log_error "NGINX não está rodando. Inicie o serviço primeiro."
        exit 1
    fi
    
    log_success "NGINX está instalado e rodando"
}

# Coletar informações do usuário
collect_ssl_info() {
    log_header "CONFIGURAÇÃO SSL"
    
    echo -e "${YELLOW}Configuração SSL/HTTPS com Let's Encrypt${NC}"
    echo ""
    
    read -p "Domínio para SSL (ex: discador.empresa.com): " DOMAIN_NAME
    
    if [ -z "$DOMAIN_NAME" ]; then
        log_error "Domínio é obrigatório para configuração SSL"
        exit 1
    fi
    
    read -p "Email para notificações do Let's Encrypt: " EMAIL
    
    if [ -z "$EMAIL" ]; then
        log_error "Email é obrigatório para o Let's Encrypt"
        exit 1
    fi
    
    echo ""
    echo -e "${CYAN}Configurações SSL:${NC}"
    echo "- Domínio: $DOMAIN_NAME"
    echo "- Email: $EMAIL"
    echo ""
    
    read -p "Continuar com a configuração SSL? (y/N): " confirm
    if [[ "$confirm" != "y" ]] && [[ "$confirm" != "Y" ]]; then
        log_info "Configuração SSL cancelada"
        exit 0
    fi
}

# Verificar DNS
verify_dns() {
    log_header "VERIFICANDO DNS"
    
    local server_ip=$(curl -s ifconfig.me)
    local domain_ip=$(dig +short "$DOMAIN_NAME" | tail -n1)
    
    log_info "IP do servidor: $server_ip"
    log_info "IP do domínio: $domain_ip"
    
    if [ "$server_ip" = "$domain_ip" ]; then
        log_success "DNS configurado corretamente"
    else
        log_warning "DNS pode não estar apontando para este servidor"
        log_warning "Verifique se o domínio $DOMAIN_NAME aponta para $server_ip"
        
        read -p "Continuar mesmo assim? (y/N): " continue_anyway
        if [[ "$continue_anyway" != "y" ]] && [[ "$continue_anyway" != "Y" ]]; then
            log_info "Configure o DNS primeiro e execute novamente"
            exit 1
        fi
    fi
}

# Instalar Certbot
install_certbot() {
    log_header "INSTALANDO CERTBOT"
    
    # Atualizar repositórios
    apt-get update -qq
    
    # Instalar snapd se não estiver instalado
    if ! command -v snap &> /dev/null; then
        apt-get install -y -qq snapd
        systemctl enable --now snapd.socket
        sleep 5
    fi
    
    # Instalar certbot via snap
    snap install core; snap refresh core
    snap install --classic certbot
    
    # Criar link simbólico
    ln -sf /snap/bin/certbot /usr/bin/certbot
    
    log_success "Certbot instalado"
}

# Configurar NGINX para HTTP temporário
setup_temp_nginx() {
    log_header "CONFIGURANDO NGINX TEMPORÁRIO"
    
    # Backup da configuração atual
    cp "$NGINX_AVAILABLE/$PROJECT_NAME" "$NGINX_AVAILABLE/$PROJECT_NAME.backup"
    
    # Criar configuração temporária para validação do Let's Encrypt
    cat > "$NGINX_AVAILABLE/$PROJECT_NAME.temp" << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect para HTTPS (será ativado depois)
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF
    
    # Substituir configuração temporariamente
    mv "$NGINX_AVAILABLE/$PROJECT_NAME.temp" "$NGINX_AVAILABLE/$PROJECT_NAME"
    
    # Recarregar NGINX
    nginx -t
    systemctl reload nginx
    
    log_success "NGINX configurado para validação SSL"
}

# Obter certificado SSL
obtain_ssl_certificate() {
    log_header "OBTENDO CERTIFICADO SSL"
    
    # Criar diretório para validação
    mkdir -p /var/www/html/.well-known/acme-challenge/
    
    # Obter certificado
    certbot certonly \
        --webroot \
        --webroot-path=/var/www/html \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --domains "$DOMAIN_NAME"
    
    if [ $? -eq 0 ]; then
        log_success "Certificado SSL obtido com sucesso"
    else
        log_error "Falha ao obter certificado SSL"
        # Restaurar configuração original
        mv "$NGINX_AVAILABLE/$PROJECT_NAME.backup" "$NGINX_AVAILABLE/$PROJECT_NAME"
        systemctl reload nginx
        exit 1
    fi
}

# Configurar NGINX com SSL
configure_nginx_ssl() {
    log_header "CONFIGURANDO NGINX COM SSL"
    
    # Criar configuração completa com SSL
    cat > "$NGINX_AVAILABLE/$PROJECT_NAME" << EOF
# Configuração NGINX com SSL para Discador Preditivo
upstream backend_api {
    server 127.0.0.1:8000;
}

upstream frontend_app {
    server 127.0.0.1:3000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name $DOMAIN_NAME;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name $DOMAIN_NAME;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1h;
    ssl_session_tickets off;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN_NAME/chain.pem;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # Logs
    access_log /var/log/nginx/discador_ssl_access.log;
    error_log /var/log/nginx/discador_ssl_error.log;
    
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
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        # WebSocket support
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
    }
    
    # Assets estáticos com cache longo
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
        proxy_pass http://frontend_app;
        proxy_set_header Host \$host;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' https: data: blob: 'unsafe-inline'" always;
    add_header X-Robots-Tag "noindex, nofollow" always;
}
EOF
    
    # Testar configuração
    nginx -t
    if [ $? -eq 0 ]; then
        log_success "Configuração NGINX SSL válida"
        systemctl reload nginx
        log_success "NGINX recarregado com SSL"
    else
        log_error "Configuração NGINX SSL inválida"
        # Restaurar backup
        mv "$NGINX_AVAILABLE/$PROJECT_NAME.backup" "$NGINX_AVAILABLE/$PROJECT_NAME"
        systemctl reload nginx
        exit 1
    fi
}

# Configurar renovação automática
setup_auto_renewal() {
    log_header "CONFIGURANDO RENOVAÇÃO AUTOMÁTICA"
    
    # Criar script de renovação personalizado
    cat > /etc/cron.d/certbot-discador << EOF
# Renovação automática do certificado SSL do Discador Preditivo
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Tentar renovar às 2:30 AM todos os dias
30 2 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF
    
    # Configurar permissões
    chmod 644 /etc/cron.d/certbot-discador
    
    # Testar renovação
    log_info "Testando renovação automática..."
    certbot renew --dry-run
    
    if [ $? -eq 0 ]; then
        log_success "Renovação automática configurada e testada"
    else
        log_warning "Teste de renovação falhou, mas configuração foi aplicada"
    fi
}

# Configurar firewall para HTTPS
update_firewall() {
    log_header "ATUALIZANDO FIREWALL"
    
    # Permitir HTTPS
    ufw allow 443/tcp comment "HTTPS"
    
    log_success "Firewall atualizado para HTTPS"
}

# Atualizar configuração do backend
update_backend_config() {
    log_header "ATUALIZANDO CONFIGURAÇÃO DO BACKEND"
    
    local backend_env="/opt/discador-preditivo/backend/.env"
    
    if [ -f "$backend_env" ]; then
        # Atualizar CORS_ORIGINS para incluir HTTPS
        sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=https://$DOMAIN_NAME,http://localhost:3000|" "$backend_env"
        
        # Adicionar configuração de SSL se não existir
        if ! grep -q "SSL_ENABLED" "$backend_env"; then
            echo "" >> "$backend_env"
            echo "# SSL Configuration" >> "$backend_env"
            echo "SSL_ENABLED=true" >> "$backend_env"
            echo "DOMAIN_NAME=$DOMAIN_NAME" >> "$backend_env"
        fi
        
        log_success "Configuração do backend atualizada para SSL"
        
        # Reiniciar backend se estiver rodando
        if systemctl is-active --quiet discador-pm2; then
            log_info "Reiniciando aplicações..."
            sudo -u discador pm2 restart all
            log_success "Aplicações reiniciadas"
        fi
    else
        log_warning "Arquivo de configuração do backend não encontrado"
    fi
}

# Validação final
validate_ssl() {
    log_header "VALIDANDO CONFIGURAÇÃO SSL"
    
    local errors=0
    
    # Verificar se certificado existe
    if [ -f "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" ]; then
        log_success "Certificado SSL: ENCONTRADO"
        
        # Verificar data de expiração
        local expiry_date=$(openssl x509 -enddate -noout -in "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" | cut -d= -f2)
        log_info "Certificado expira em: $expiry_date"
    else
        log_error "Certificado SSL: NÃO ENCONTRADO"
        ((errors++))
    fi
    
    # Verificar NGINX
    if nginx -t > /dev/null 2>&1; then
        log_success "Configuração NGINX: VÁLIDA"
    else
        log_error "Configuração NGINX: INVÁLIDA"
        ((errors++))
    fi
    
    # Testar conectividade HTTPS
    local max_attempts=5
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -k "https://$DOMAIN_NAME/health" > /dev/null 2>&1; then
            log_success "HTTPS: FUNCIONANDO"
            break
        fi
        
        attempt=$((attempt + 1))
        if [ $attempt -eq $max_attempts ]; then
            log_error "HTTPS: NÃO RESPONDENDO"
            ((errors++))
        else
            log_info "Tentativa $attempt/$max_attempts - aguardando..."
            sleep 5
        fi
    done
    
    # Verificar redirect HTTP para HTTPS
    local redirect_check=$(curl -s -I "http://$DOMAIN_NAME" | grep "301\|302")
    if [ -n "$redirect_check" ]; then
        log_success "Redirect HTTP->HTTPS: FUNCIONANDO"
    else
        log_warning "Redirect HTTP->HTTPS: PODE NÃO ESTAR FUNCIONANDO"
    fi
    
    return $errors
}

# Mostrar informações finais
show_ssl_info() {
    log_header "CONFIGURAÇÃO SSL CONCLUÍDA"
    
    echo -e "${GREEN}🔒 SSL/HTTPS configurado com sucesso!${NC}"
    echo ""
    echo -e "${CYAN}📋 INFORMAÇÕES SSL:${NC}"
    echo "  🌐 Domínio: $DOMAIN_NAME"
    echo "  📧 Email: $EMAIL"
    echo "  📜 Certificado: /etc/letsencrypt/live/$DOMAIN_NAME/"
    echo ""
    echo -e "${CYAN}🔗 URLs SEGURAS:${NC}"
    echo "  🌍 Frontend: https://$DOMAIN_NAME"
    echo "  📚 API Docs: https://$DOMAIN_NAME/docs"
    echo "  ❤️  Health Check: https://$DOMAIN_NAME/health"
    echo ""
    echo -e "${CYAN}🔄 RENOVAÇÃO AUTOMÁTICA:${NC}"
    echo "  ⏰ Agendada para: 2:30 AM diariamente"
    echo "  📁 Configuração: /etc/cron.d/certbot-discador"
    echo "  🧪 Teste: certbot renew --dry-run"
    echo ""
    echo -e "${CYAN}⚡ COMANDOS ÚTEIS:${NC}"
    echo "  🔍 Status certificado: certbot certificates"
    echo "  🔄 Renovar manualmente: certbot renew"
    echo "  🧪 Teste renovação: certbot renew --dry-run"
    echo "  📋 Logs NGINX: tail -f /var/log/nginx/discador_ssl_*.log"
    echo ""
    echo -e "${YELLOW}📝 IMPORTANTE:${NC}"
    echo "  - Certificados Let's Encrypt expiram em 90 dias"
    echo "  - Renovação automática está configurada"
    echo "  - Verifique regularmente os logs de renovação"
    echo "  - Mantenha o domínio apontando para este servidor"
    echo ""
    echo -e "${CYAN}📄 Logs da configuração SSL salvos em: $LOG_FILE${NC}"
}

# Função principal
main() {
    # Cabeçalho
    echo -e "${CYAN}"
    echo "=============================================="
    echo "🔒 CONFIGURAÇÃO SSL/HTTPS AUTOMATIZADA"
    echo "   SISTEMA DISCADOR PREDITIVO"
    echo "=============================================="
    echo -e "${NC}"
    echo "Data/Hora: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # Criar log
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    chmod 644 "$LOG_FILE"
    
    # Verificações iniciais
    check_root
    check_nginx
    collect_ssl_info
    verify_dns
    
    # Configuração SSL
    install_certbot
    setup_temp_nginx
    obtain_ssl_certificate
    configure_nginx_ssl
    setup_auto_renewal
    update_firewall
    update_backend_config
    
    # Validação e finalização
    if validate_ssl; then
        show_ssl_info
        log_success "Configuração SSL concluída com sucesso!"
        exit 0
    else
        log_error "Configuração SSL concluída com alguns problemas. Verifique os logs."
        exit 1
    fi
}

# Tratamento de sinais
trap 'log_error "Configuração SSL interrompida"; exit 1' INT TERM

# Executar configuração
main "$@" 