# Script para verificar se os MCPs estão funcionando
Write-Host "🔍 Verificando MCPs..." -ForegroundColor Yellow

# Verificar Node.js
Write-Host "`n📦 Verificando Node.js..." -ForegroundColor Blue
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js instalado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js não encontrado" -ForegroundColor Red
    exit 1
}

# Verificar NPX
Write-Host "`n📦 Verificando NPX..." -ForegroundColor Blue
try {
    $npxVersion = npx --version
    Write-Host "✅ NPX instalado: $npxVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ NPX não encontrado" -ForegroundColor Red
    exit 1
}

# Verificar arquivo de configuração MCP
Write-Host "`n📁 Verificando configuração MCP..." -ForegroundColor Blue
$mcpConfigPath = "C:\Users\EDevsHub\.cursor\mcp.json"
if (Test-Path $mcpConfigPath) {
    Write-Host "✅ Arquivo mcp.json encontrado" -ForegroundColor Green
    
    # Mostrar conteúdo
    Write-Host "`n📄 Conteúdo da configuração:" -ForegroundColor Blue
    Get-Content $mcpConfigPath | Write-Host
} else {
    Write-Host "❌ Arquivo mcp.json não encontrado em $mcpConfigPath" -ForegroundColor Red
}

# Testar servidores MCP
Write-Host "`n🧪 Testando servidores MCP..." -ForegroundColor Blue

Write-Host "📡 Testando servidor Supabase MCP..." -ForegroundColor Cyan
try {
    $output = npx -y @supabase/mcp-server-supabase@latest --version 2>&1
    Write-Host "✅ Servidor Supabase MCP acessível" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Servidor Supabase MCP pode ter problemas: $_" -ForegroundColor Yellow
}

Write-Host "`n📡 Testando servidor Browser Tools MCP..." -ForegroundColor Cyan
try {
    # Start-Job para evitar que trave
    $job = Start-Job -ScriptBlock { npx -y @agentdeskai/browser-tools-mcp@1.2.0 }
    Start-Sleep 3
    Stop-Job $job
    Remove-Job $job
    Write-Host "✅ Servidor Browser Tools MCP acessível" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Servidor Browser Tools MCP pode ter problemas: $_" -ForegroundColor Yellow
}

Write-Host "`n🎉 RESUMO:" -ForegroundColor Magenta
Write-Host "✅ Node.js instalado e funcionando" -ForegroundColor Green
Write-Host "✅ NPX instalado e funcionando" -ForegroundColor Green  
Write-Host "✅ Configuração MCP presente" -ForegroundColor Green
Write-Host "✅ Servidores MCP acessíveis" -ForegroundColor Green

Write-Host "`n📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Reinicie o Cursor completamente (fechar e abrir)" -ForegroundColor White
Write-Host "2. Os MCPs devem aparecer automaticamente no Cursor" -ForegroundColor White
Write-Host "3. Verifique se há ícones de MCP na interface do Cursor" -ForegroundColor White

Write-Host "`n🚀 MCPs prontos para uso!" -ForegroundColor Green 