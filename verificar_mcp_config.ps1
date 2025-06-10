# Script para verificar configuracao MCP
Write-Host "Verificando configuracao MCP..." -ForegroundColor Yellow

$mcpPath = "C:\Users\EDevsHub\.cursor\mcp.json"

if (Test-Path $mcpPath) {
    Write-Host "Arquivo encontrado!" -ForegroundColor Green
    
    try {
        $content = Get-Content $mcpPath -Raw
        Write-Host "Conteudo:" -ForegroundColor Blue
        Write-Host $content
        
        # Verificar se e JSON valido
        $json = $content | ConvertFrom-Json
        Write-Host "JSON valido!" -ForegroundColor Green
        
        # Verificar configuracao do Supabase
        if ($json.mcpServers.supabase) {
            Write-Host "Configuracao Supabase encontrada" -ForegroundColor Green
            
            # Verificar se tem token
            $hasToken = $false
            foreach ($arg in $json.mcpServers.supabase.args) {
                if ($arg -like "sbp_*") {
                    $hasToken = $true
                    $tokenPreview = $arg.Substring(0, [Math]::Min(10, $arg.Length)) + "..."
                    Write-Host "Token encontrado: $tokenPreview" -ForegroundColor Green
                    break
                }
            }
            
            if (-not $hasToken) {
                Write-Host "Token nao encontrado!" -ForegroundColor Red
            }
        } else {
            Write-Host "Configuracao Supabase nao encontrada!" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "Erro ao processar JSON: $($_.Exception.Message)" -ForegroundColor Red
    }
    
} else {
    Write-Host "Arquivo nao encontrado em $mcpPath" -ForegroundColor Red
} 