Write-Host "Testando novos endpoints..." -ForegroundColor Green

$baseUrl = "https://discador.onrender.com/api/v1"

Write-Host "Aguardando deploy (30s)..." -ForegroundColor Yellow
Start-Sleep 30

Write-Host "Testando audios..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/audios" -Method GET
    Write-Host "OK - Audios: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "ERRO - Audios: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Testando gravacoes..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/gravacoes" -Method GET
    Write-Host "OK - Gravacoes: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "ERRO - Gravacoes: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Testando agentes..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/agentes" -Method GET
    Write-Host "OK - Agentes: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "ERRO - Agentes: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Testando endpoint corrigido..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/campanhas/2" -Method GET
    Write-Host "OK - Endpoint corrigido: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "ERRO - Endpoint corrigido: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Teste concluido!" -ForegroundColor Green 