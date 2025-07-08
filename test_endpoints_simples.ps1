Write-Host "🚀 TESTANDO ENDPOINTS PRESIONE1..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Yellow

$baseUrl = "https://discador.onrender.com/api/v1"
$campanhaId = 2

Write-Host "`n🎯 TESTANDO ENDPOINTS DE CAMPANHAS:" -ForegroundColor Magenta

# Teste 1: Listar Campanhas
Write-Host "📡 Testando: Listar Campanhas" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/campanhas" -Method GET
    Write-Host "✅ Listar Campanhas - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Listar Campanhas - ERRO" -ForegroundColor Red
}

# Teste 2: Estatísticas da Campanha
Write-Host "📡 Testando: Estatísticas da Campanha" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/campanhas/$campanhaId/estadisticas" -Method GET
    Write-Host "✅ Estatísticas da Campanha - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Estatísticas da Campanha - ERRO" -ForegroundColor Red
}

# Teste 3: Monitor da Campanha
Write-Host "📡 Testando: Monitor da Campanha" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/campanhas/$campanhaId/monitor" -Method GET
    Write-Host "✅ Monitor da Campanha - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Monitor da Campanha - ERRO" -ForegroundColor Red
}

# Teste 4: Chamadas da Campanha
Write-Host "📡 Testando: Chamadas da Campanha" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/campanhas/$campanhaId/llamadas" -Method GET
    Write-Host "✅ Chamadas da Campanha - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Chamadas da Campanha - ERRO" -ForegroundColor Red
}

Write-Host "`n🎛️ TESTANDO ENDPOINTS DE CONTROLE:" -ForegroundColor Magenta

# Teste 5: Iniciar Campanha
Write-Host "📡 Testando: Iniciar Campanha" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/campanhas/$campanhaId/iniciar" -Method POST -Body '{"usuario_id": "teste"}' -ContentType "application/json"
    Write-Host "✅ Iniciar Campanha - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Iniciar Campanha - ERRO" -ForegroundColor Red
}

# Teste 6: Pausar Campanha
Write-Host "📡 Testando: Pausar Campanha" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/campanhas/$campanhaId/pausar" -Method POST -Body '{"pausar": true}' -ContentType "application/json"
    Write-Host "✅ Pausar Campanha - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Pausar Campanha - ERRO" -ForegroundColor Red
}

# Teste 7: Parar Campanha
Write-Host "📡 Testando: Parar Campanha" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/campanhas/$campanhaId/parar" -Method POST -Body '{}' -ContentType "application/json"
    Write-Host "✅ Parar Campanha - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Parar Campanha - ERRO" -ForegroundColor Red
}

Write-Host "`n📞 TESTANDO ENDPOINTS DE CHAMADAS:" -ForegroundColor Magenta

# Teste 8: Transferir Chamada
Write-Host "📡 Testando: Transferir Chamada" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/llamadas/1001/transferir" -Method POST -Body '{"destino": "100"}' -ContentType "application/json"
    Write-Host "✅ Transferir Chamada - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Transferir Chamada - ERRO" -ForegroundColor Red
}

# Teste 9: Finalizar Chamada
Write-Host "📡 Testando: Finalizar Chamada" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/presione1/llamadas/1001/finalizar" -Method POST -Body '{"motivo": "teste"}' -ContentType "application/json"
    Write-Host "✅ Finalizar Chamada - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Finalizar Chamada - ERRO" -ForegroundColor Red
}

Write-Host "`n📊 TESTANDO ENDPOINTS DE MONITORAMENTO:" -ForegroundColor Magenta

# Teste 10: Listar Agentes
Write-Host "📡 Testando: Listar Agentes" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/monitoring/agentes" -Method GET
    Write-Host "✅ Listar Agentes - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Listar Agentes - ERRO" -ForegroundColor Red
}

# Teste 11: Sessões Áudio Inteligente
Write-Host "📡 Testando: Sessões Áudio Inteligente" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/audio-inteligente/campanhas/$campanhaId/sessoes" -Method GET
    Write-Host "✅ Sessões Áudio Inteligente - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Sessões Áudio Inteligente - ERRO" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Yellow
Write-Host "🏆 TESTE COMPLETO FINALIZADO!" -ForegroundColor Green
Write-Host "`n🔗 Links úteis:" -ForegroundColor Cyan
Write-Host "Frontend: https://discador.vercel.app/" -ForegroundColor Blue
Write-Host "Backend: https://discador.onrender.com/" -ForegroundColor Blue
Write-Host "Documentação: https://discador.onrender.com/docs" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Yellow 