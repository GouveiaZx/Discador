# Script PowerShell simplificado para verificar implementacao

Write-Host "Verificando implementacao de Blacklist e Multiplas Listas de Chamadas"
Write-Host "==============================================================="

$arquivos = @(
    "app/schemas/blacklist.py",
    "app/services/blacklist_service.py", 
    "app/services/discado_service.py",
    "app/routes/blacklist.py",
    "app/routes/discado.py",
    "tests/test_blacklist.py",
    "migrations/update_blacklist_and_llamadas.sql",
    "docs/BLACKLIST_MULTIPLES_LISTAS.md",
    "test_funcionalidade.py",
    "RESUMO_IMPLEMENTACAO.md"
)

$existentes = 0
$total = $arquivos.Count

Write-Host "`nVerificando arquivos criados:"
foreach ($arquivo in $arquivos) {
    if (Test-Path $arquivo) {
        Write-Host "OK - $arquivo" -ForegroundColor Green
        $existentes++
    } else {
        Write-Host "FALTANDO - $arquivo" -ForegroundColor Red
    }
}

Write-Host "`nResumo:"
Write-Host "Arquivos existentes: $existentes de $total"
Write-Host "Taxa de sucesso: $([math]::Round(($existentes/$total)*100, 1))%"

if ($existentes -eq $total) {
    Write-Host "`nIMPLEMENTACAO COMPLETA!" -ForegroundColor Green
} else {
    Write-Host "`nImplementacao parcial - verifique arquivos faltantes" -ForegroundColor Yellow
}

Write-Host "`nProximos passos:"
Write-Host "1. Executar migracoes SQL"
Write-Host "2. Testar endpoints da API"
Write-Host "3. Verificar documentacao completa" 