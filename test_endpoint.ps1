try {
    Write-Host "Testando endpoint de debug..."
    $response = Invoke-WebRequest -Uri "https://discador.onrender.com/api/v1/presione1-debug/campanhas" -Method GET -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Content: $($response.Content)"
    Write-Host ""
    
    Write-Host "Testando endpoint principal..."
    $response2 = Invoke-WebRequest -Uri "https://discador.onrender.com/api/v1/presione1/campanhas" -Method GET -UseBasicParsing
    Write-Host "Status: $($response2.StatusCode)"
    Write-Host "Content: $($response2.Content)"
} catch {
    Write-Host "Erro: $($_.Exception.Message)"
} 