Write-Host "Testando Endpoint de Agentes" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

$baseUrl = "https://discador.onrender.com/api/v1"

Write-Host "Testando: $baseUrl/monitoring/agentes" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/monitoring/agentes" -Method Get -ContentType "application/json"
    
    Write-Host "Status: 200 - Sucesso" -ForegroundColor Green
    Write-Host "Total de agentes: $($response.total_agentes)" -ForegroundColor White
    Write-Host "Disponiveis: $($response.disponiveis)" -ForegroundColor Green
    Write-Host "Ocupados: $($response.ocupados)" -ForegroundColor Blue
    Write-Host "Em pausa: $($response.em_pausa)" -ForegroundColor Yellow
    Write-Host "Offline: $($response.offline)" -ForegroundColor Red
    Write-Host ""
    
    Write-Host "Lista de agentes:" -ForegroundColor Cyan
    foreach ($agente in $response.agentes) {
        Write-Host "- $($agente.nome) (ID: $($agente.id), Ext: $($agente.extensao), Status: $($agente.status))" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Frontend deve funcionar corretamente agora!" -ForegroundColor Green
    Write-Host "Array 'agentes' encontrado na resposta" -ForegroundColor Green
    
} catch {
    Write-Host "Erro ao testar endpoint:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "Aguarde alguns minutos para o deploy do frontend no Vercel..." -ForegroundColor Yellow
Write-Host "Depois acesse: https://discador.vercel.app" -ForegroundColor Cyan 