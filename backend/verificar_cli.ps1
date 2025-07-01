# Script PowerShell para verificar implementacao CLI

Write-Host "🎯 Verificando implementação de CLI Aleatorio" -ForegroundColor Green
Write-Host "=" * 50

$arquivos_cli = @(
    "app/models/cli.py",
    "app/schemas/cli.py", 
    "app/services/cli_service.py",
    "app/routes/cli.py",
    "migrations/create_cli_table.sql",
    "tests/test_cli.py",
    "docs/CLI_ALEATORIO.md",
    "test_funcionalidade_cli.py"
)

$existentes = 0
$total = $arquivos_cli.Count

Write-Host "`n📁 Verificando arquivos CLI:"
foreach ($arquivo in $arquivos_cli) {
    if (Test-Path $arquivo) {
        Write-Host "✅ $arquivo" -ForegroundColor Green
        $existentes++
    } else {
        Write-Host "❌ $arquivo" -ForegroundColor Red
    }
}

Write-Host "`n🔍 Verificando conteúdo dos arquivos:"

# Verificar modelo CLI
if (Test-Path "app/models/cli.py") {
    $conteudo_modelo = Get-Content "app/models/cli.py" -Raw
    if ($conteudo_modelo -match "class Cli" -and $conteudo_modelo -match "veces_usado") {
        Write-Host "✅ Modelo Cli com campos corretos" -ForegroundColor Green
    } else {
        Write-Host "❌ Modelo Cli incompleto" -ForegroundColor Red
    }
}

# Verificar serviço CLI
if (Test-Path "app/services/cli_service.py") {
    $conteudo_servico = Get-Content "app/services/cli_service.py" -Raw
    if ($conteudo_servico -match "generar_cli_aleatorio" -and $conteudo_servico -match "agregar_cli") {
        Write-Host "✅ CliService com métodos principais" -ForegroundColor Green
    } else {
        Write-Host "❌ CliService incompleto" -ForegroundColor Red
    }
}

# Verificar integração com discado
if (Test-Path "app/services/discado_service.py") {
    $conteudo_discado = Get-Content "app/services/discado_service.py" -Raw
    if ($conteudo_discado -match "CliService" -and $conteudo_discado -match "cli_personalizado") {
        Write-Host "✅ Integração CLI-Discado implementada" -ForegroundColor Green
    } else {
        Write-Host "❌ Integração CLI-Discado faltando" -ForegroundColor Red
    }
}

# Verificar rotas no main.py
if (Test-Path "main.py") {
    $conteudo_main = Get-Content "main.py" -Raw
    if ($conteudo_main -match "cli\.router") {
        Write-Host "✅ Rotas CLI incluídas no main.py" -ForegroundColor Green
    } else {
        Write-Host "❌ Rotas CLI não incluídas no main.py" -ForegroundColor Red
    }
}

# Verificar schemas init
if (Test-Path "app/schemas/__init__.py") {
    $conteudo_init = Get-Content "app/schemas/__init__.py" -Raw
    if ($conteudo_init -match "CliCreate" -and $conteudo_init -match "CliRandomResponse") {
        Write-Host "✅ Schemas CLI exportados corretamente" -ForegroundColor Green
    } else {
        Write-Host "❌ Schemas CLI não exportados" -ForegroundColor Red
    }
}

Write-Host "`n📊 Resumo da verificação:"
Write-Host "Arquivos CLI: $existentes de $total" -ForegroundColor $(if ($existentes -eq $total) { "Green" } else { "Yellow" })
Write-Host "Taxa de sucesso: $([math]::Round(($existentes/$total)*100, 1))%" -ForegroundColor $(if ($existentes -eq $total) { "Green" } else { "Yellow" })

if ($existentes -eq $total) {
    Write-Host "`n🎉 IMPLEMENTAÇÃO CLI COMPLETA!" -ForegroundColor Green
    Write-Host "Todos os arquivos necessários foram criados." -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Implementação parcial" -ForegroundColor Yellow
    Write-Host "Alguns arquivos podem estar faltando." -ForegroundColor Yellow
}

Write-Host "`n📋 Próximos passos:"
Write-Host "1. Executar migração SQL: psql -d discador -f migrations/create_cli_table.sql"
Write-Host "2. Adicionar CLIs iniciais via API"
Write-Host "3. Testar geração de CLI aleatorio"
Write-Host "4. Verificar integração com discado"

Write-Host "`n📖 Documentação disponível em: docs/CLI_ALEATORIO.md" -ForegroundColor Cyan 