Write-Host "🎵 TESTANDO NOVOS ENDPOINTS - ÁUDIO, GRAVAÇÕES E AGENTES" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Yellow

$baseUrl = "https://discador.onrender.com/api/v1"

# Aguardar deploy
Write-Host "⏰ Aguardando 30 segundos para o deploy..." -ForegroundColor Yellow
Start-Sleep 30

Write-Host "`n🎯 TESTANDO ENDPOINTS DE ÁUDIO:" -ForegroundColor Magenta

# Teste 1: Listar Áudios
Write-Host "📡 Testando: Listar Áudios" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/audios" -Method GET
    Write-Host "✅ Listar Áudios - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Listar Áudios - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 2: Detalhes de Áudio
Write-Host "📡 Testando: Detalhes de Áudio" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/audios/1" -Method GET
    Write-Host "✅ Detalhes de Áudio - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Detalhes de Áudio - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 3: Reproduzir Áudio
Write-Host "📡 Testando: Reproduzir Áudio" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/audios/1/play" -Method GET
    Write-Host "✅ Reproduzir Áudio - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Reproduzir Áudio - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 4: Upload de Áudio
Write-Host "📡 Testando: Upload de Áudio" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/audios/upload" -Method POST -Body '{}' -ContentType "application/json"
    Write-Host "✅ Upload de Áudio - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Upload de Áudio - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎙️ TESTANDO ENDPOINTS DE GRAVAÇÕES:" -ForegroundColor Magenta

# Teste 5: Listar Gravações
Write-Host "📡 Testando: Listar Gravações" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/gravacoes" -Method GET
    Write-Host "✅ Listar Gravações - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Listar Gravações - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 6: Detalhes de Gravação
Write-Host "📡 Testando: Detalhes de Gravação" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/gravacoes/2000" -Method GET
    Write-Host "✅ Detalhes de Gravação - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Detalhes de Gravação - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 7: Reproduzir Gravação
Write-Host "📡 Testando: Reproduzir Gravação" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/gravacoes/2000/play" -Method GET
    Write-Host "✅ Reproduzir Gravação - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Reproduzir Gravação - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 8: Download de Gravação
Write-Host "📡 Testando: Download de Gravação" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/gravacoes/2000/download" -Method GET
    Write-Host "✅ Download de Gravação - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Download de Gravação - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n👥 TESTANDO ENDPOINTS DE AGENTES:" -ForegroundColor Magenta

# Teste 9: Listar Agentes Detalhado
Write-Host "📡 Testando: Listar Agentes Detalhado" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/agentes" -Method GET
    Write-Host "✅ Listar Agentes Detalhado - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Listar Agentes Detalhado - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 10: Detalhes de Agente
Write-Host "📡 Testando: Detalhes de Agente" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/agentes/1" -Method GET
    Write-Host "✅ Detalhes de Agente - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Detalhes de Agente - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 11: Alterar Status do Agente
Write-Host "📡 Testando: Alterar Status do Agente" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/agentes/1/status" -Method POST -Body '{"status": "pausa", "motivo": "teste"}' -ContentType "application/json"
    Write-Host "✅ Alterar Status do Agente - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Alterar Status do Agente - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 12: Corrigir Endpoint Faltando
Write-Host "📡 Testando: Endpoint Corrigido /presione1/campanhas/2" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/campanhas/2" -Method GET
    Write-Host "✅ Endpoint Corrigido - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Endpoint Corrigido - ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Yellow
Write-Host "🎉 TESTE COMPLETO DOS NOVOS ENDPOINTS FINALIZADO!" -ForegroundColor Green
Write-Host "`n🔗 Links úteis:" -ForegroundColor Cyan
Write-Host "Frontend: https://discador.vercel.app/" -ForegroundColor Blue
Write-Host "Backend: https://discador.onrender.com/" -ForegroundColor Blue
Write-Host "Documentação: https://discador.onrender.com/docs" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Yellow 