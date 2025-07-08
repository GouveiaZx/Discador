# ============================================================================
# TESTE COMPLETO DOS ENDPOINTS PRESIONE1
# ============================================================================

Write-Host "🚀 TESTANDO TODOS OS ENDPOINTS PRESIONE1..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Yellow

$baseUrl = "https://discador.onrender.com/api/v1"
$campanhaId = 2
$llamadaId = 1001

# Função para testar endpoint
function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Url,
        [string]$Description,
        [string]$Body = $null
    )
    
    try {
        Write-Host "📡 Testando: $Description" -ForegroundColor Cyan
        
        $params = @{
            Uri = $Url
            Method = $Method
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $Description - Status: $($response.StatusCode)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️ $Description - Status: $($response.StatusCode)" -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Host "❌ $Description - ERRO: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# ============================================================================
# ENDPOINTS DE CAMPANHAS
# ============================================================================

Write-Host "`n🎯 ENDPOINTS DE CAMPANHAS:" -ForegroundColor Magenta

$tests = @(
    @{
        Method = "GET"
        Url = "$baseUrl/presione1/campanhas"
        Description = "Listar Campanhas"
    },
    @{
        Method = "GET"
        Url = "$baseUrl/presione1/campanhas/$campanhaId/estadisticas"
        Description = "Estatísticas da Campanha"
    },
    @{
        Method = "GET"
        Url = "$baseUrl/presione1/campanhas/$campanhaId/monitor"
        Description = "Monitor da Campanha"
    },
    @{
        Method = "GET"
        Url = "$baseUrl/presione1/campanhas/$campanhaId/llamadas"
        Description = "Chamadas da Campanha"
    }
)

$successCount = 0
$totalTests = $tests.Count

foreach ($test in $tests) {
    if (Test-Endpoint -Method $test.Method -Url $test.Url -Description $test.Description) {
        $successCount++
    }
}

# ============================================================================
# ENDPOINTS DE CONTROLE
# ============================================================================

Write-Host "`n🎛️ ENDPOINTS DE CONTROLE:" -ForegroundColor Magenta

$controlTests = @(
    @{
        Method = "POST"
        Url = "$baseUrl/presione1/campanhas/$campanhaId/iniciar"
        Description = "Iniciar Campanha"
        Body = '{"usuario_id": "teste"}'
    },
    @{
        Method = "POST"
        Url = "$baseUrl/presione1/campanhas/$campanhaId/pausar"
        Description = "Pausar Campanha"
        Body = '{"pausar": true}'
    },
    @{
        Method = "POST"
        Url = "$baseUrl/presione1/campanhas/$campanhaId/parar"
        Description = "Parar Campanha"
        Body = '{}'
    }
)

foreach ($test in $controlTests) {
    if (Test-Endpoint -Method $test.Method -Url $test.Url -Description $test.Description -Body $test.Body) {
        $successCount++
    }
    $totalTests++
}

# ============================================================================
# ENDPOINTS DE CHAMADAS
# ============================================================================

Write-Host "`n📞 ENDPOINTS DE CHAMADAS:" -ForegroundColor Magenta

$callTests = @(
    @{
        Method = "POST"
        Url = "$baseUrl/presione1/llamadas/$llamadaId/transferir"
        Description = "Transferir Chamada"
        Body = '{"destino": "100"}'
    },
    @{
        Method = "POST"
        Url = "$baseUrl/presione1/llamadas/$llamadaId/finalizar"
        Description = "Finalizar Chamada"
        Body = '{"motivo": "teste"}'
    }
)

foreach ($test in $callTests) {
    if (Test-Endpoint -Method $test.Method -Url $test.Url -Description $test.Description -Body $test.Body) {
        $successCount++
    }
    $totalTests++
}

# ============================================================================
# ENDPOINTS DE MONITORAMENTO
# ============================================================================

Write-Host "`n📊 ENDPOINTS DE MONITORAMENTO:" -ForegroundColor Magenta

$monitorTests = @(
    @{
        Method = "GET"
        Url = "$baseUrl/monitoring/agentes"
        Description = "Listar Agentes"
    },
    @{
        Method = "GET"
        Url = "$baseUrl/audio-inteligente/campanhas/$campanhaId/sessoes"
        Description = "Sessões Áudio Inteligente"
    }
)

foreach ($test in $monitorTests) {
    if (Test-Endpoint -Method $test.Method -Url $test.Url -Description $test.Description) {
        $successCount++
    }
    $totalTests++
}

# ============================================================================
# RELATÓRIO FINAL
# ============================================================================

Write-Host "`n============================================================" -ForegroundColor Yellow
Write-Host "🏆 RELATÓRIO FINAL:" -ForegroundColor Green
Write-Host "✅ Sucessos: $successCount/$totalTests" -ForegroundColor Green

if ($successCount -eq $totalTests) {
    Write-Host "🎉 TODOS OS ENDPOINTS ESTÃO FUNCIONANDO!" -ForegroundColor Green
    Write-Host "✅ Frontend agora deve funcionar completamente!" -ForegroundColor Green
} else {
    $failures = $totalTests - $successCount
    Write-Host "⚠️ Alguns endpoints falharam: $failures" -ForegroundColor Yellow
}

Write-Host "`n🔗 Links úteis:" -ForegroundColor Cyan
Write-Host "Frontend: https://discador.vercel.app/" -ForegroundColor Blue
Write-Host "Backend: https://discador.onrender.com/" -ForegroundColor Blue
Write-Host "Documentação: https://discador.onrender.com/docs" -ForegroundColor Blue

Write-Host "`n============================================================" -ForegroundColor Yellow 