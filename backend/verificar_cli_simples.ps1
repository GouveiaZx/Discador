# Verificacao CLI simples

Write-Host "Verificando implementacao CLI Aleatorio"
Write-Host "========================================"

$arquivos = @(
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
foreach ($arquivo in $arquivos) {
    if (Test-Path $arquivo) {
        Write-Host "OK - $arquivo" -ForegroundColor Green
        $existentes++
    } else {
        Write-Host "FALTANDO - $arquivo" -ForegroundColor Red
    }
}

Write-Host "`nVerificando integracoes:"

# Verificar discado service
if (Test-Path "app/services/discado_service.py") {
    $conteudo = Get-Content "app/services/discado_service.py" -Raw
    if ($conteudo -match "CliService") {
        Write-Host "OK - DiscadoService integrado com CLI" -ForegroundColor Green
    } else {
        Write-Host "FALTANDO - Integracao CLI em DiscadoService" -ForegroundColor Red
    }
}

# Verificar main.py
if (Test-Path "main.py") {
    $conteudo = Get-Content "main.py" -Raw
    if ($conteudo -match "cli\.router") {
        Write-Host "OK - Rotas CLI incluidas no main.py" -ForegroundColor Green
    } else {
        Write-Host "FALTANDO - Rotas CLI no main.py" -ForegroundColor Red
    }
}

Write-Host "`nResumo:"
Write-Host "Arquivos CLI: $existentes de $($arquivos.Count)"
$percentual = [math]::Round(($existentes/$arquivos.Count)*100, 1)
Write-Host "Taxa de sucesso: $percentual%"

if ($existentes -eq $arquivos.Count) {
    Write-Host "`nIMPLEMENTACAO CLI COMPLETA!" -ForegroundColor Green
} else {
    Write-Host "`nImplementacao parcial - verificar arquivos faltantes" -ForegroundColor Yellow
}

Write-Host "`nProximos passos:"
Write-Host "1. Executar migracao SQL"
Write-Host "2. Adicionar CLIs iniciais"
Write-Host "3. Testar endpoints da API" 