try {
    Write-Host "Testando endpoint de roteamento..."
    $response = Invoke-WebRequest -Uri "https://discador.onrender.com/api/v1/test-roteamento/campanhas" -Method GET -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Content Length: $($response.Content.Length)"
    Write-Host "Content: $($response.Content)"
} catch {
    Write-Host "Erro: $($_.Exception.Message)"
} 