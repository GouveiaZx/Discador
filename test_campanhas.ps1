try {
    Write-Host "Buscando campanhas via endpoint raiz modificado..."
    $response = Invoke-WebRequest -Uri "https://discador.onrender.com/?campanhas=presione1" -Method GET -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Content Length: $($response.Content.Length)"
    Write-Host "Content:"
    Write-Host $response.Content
} catch {
    Write-Host "Erro: $($_.Exception.Message)"
} 