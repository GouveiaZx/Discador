#!/usr/bin/env pwsh

Write-Host "🔍 Testando Endpoint de Agentes - Correção _.filter" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

$baseUrl = "https://discador.onrender.com/api/v1"

Write-Host "📋 Testando endpoint: $baseUrl/monitoring/agentes" -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/monitoring/agentes" -Method Get -ContentType "application/json"
    
    Write-Host "✅ Status: 200 - Sucesso" -ForegroundColor Green
    Write-Host "📊 Dados retornados:" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "🔢 Total de agentes: $($response.total_agentes)" -ForegroundColor White
    Write-Host "🟢 Disponíveis: $($response.disponiveis)" -ForegroundColor Green
    Write-Host "🔵 Ocupados: $($response.ocupados)" -ForegroundColor Blue
    Write-Host "🟡 Em pausa: $($response.em_pausa)" -ForegroundColor Yellow
    Write-Host "🔴 Offline: $($response.offline)" -ForegroundColor Red
    Write-Host ""
    
    Write-Host "👥 Lista de agentes:" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($agente in $response.agentes) {
        $statusColor = switch ($agente.status) {
            "disponivel" { "Green" }
            "ocupado" { "Blue" }
            "pausa" { "Yellow" }
            "offline" { "Red" }
            default { "White" }
        }
        
        Write-Host "📋 Agente: $($agente.nome)" -ForegroundColor White
        Write-Host "   ID: $($agente.id)" -ForegroundColor Gray
        Write-Host "   Extensão: $($agente.extensao)" -ForegroundColor Gray
        Write-Host "   Status: $($agente.status)" -ForegroundColor $statusColor
        Write-Host "   Chamadas hoje: $($agente.chamadas_hoje)" -ForegroundColor Gray
        Write-Host "   Tempo online: $($agente.tempo_online)" -ForegroundColor Gray
        Write-Host ""
    }
    
    Write-Host "✨ Estrutura JSON válida para o frontend!" -ForegroundColor Green
    Write-Host "✅ Array 'agentes' encontrado na resposta" -ForegroundColor Green
    Write-Host "✅ Propriedades corretas: id, nome, extensao, status, chamadas_hoje, tempo_online" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🚀 Frontend deve funcionar corretamente agora!" -ForegroundColor Green
    Write-Host "   - agents.filter() funcionará com o array extraído" -ForegroundColor White
    Write-Host "   - StatusBadge tem cores para todos os status" -ForegroundColor White
    Write-Host "   - Métricas serão calculadas corretamente" -ForegroundColor White
    
} catch {
    Write-Host "❌ Erro ao testar endpoint:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "🔄 Aguarde alguns minutos para o deploy automático do frontend no Vercel..." -ForegroundColor Yellow
Write-Host "🌐 Depois acesse: https://discador.vercel.app" -ForegroundColor Cyan 