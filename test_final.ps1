try {
    Write-Host "Testando endpoint /api/v1/presione1/campanhas..."
    $response = Invoke-WebRequest -Uri "https://discador.onrender.com/api/v1/presione1/campanhas" -Method GET -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Content Length: $($response.Content.Length)"
    Write-Host "Content:"
    Write-Host $response.Content
} catch {
    Write-Host "Erro: $($_.Exception.Message)"
} 