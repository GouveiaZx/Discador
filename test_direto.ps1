try {
    Write-Host "Testando endpoint hello-direto..."
    $response = Invoke-WebRequest -Uri "https://discador.onrender.com/api/v1/hello-direto" -Method GET -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Content: $($response.Content)"
    Write-Host ""
    
    Write-Host "Testando endpoint presione1/campanhas direto..."
    $response2 = Invoke-WebRequest -Uri "https://discador.onrender.com/api/v1/presione1/campanhas" -Method GET -UseBasicParsing
    Write-Host "Status: $($response2.StatusCode)"
    Write-Host "Content Length: $($response2.Content.Length)"
    if ($response2.Content.Length -lt 1000) {
        Write-Host "Content: $($response2.Content)"
    } else {
        Write-Host "Content: [LARGE DATA - $($response2.Content.Length) chars]"
    }
} catch {
    Write-Host "Erro: $($_.Exception.Message)"
} 