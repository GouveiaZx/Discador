# Script PowerShell para verificar a implementação de Blacklist e Múltiplas Listas
# Executa verificações dos arquivos e estrutura implementada

Write-Host "🚀 Verificando implementação de Blacklist e Múltiplas Listas de Chamadas" -ForegroundColor Green
Write-Host "=" * 70

# Função para verificar se arquivo existe
function Verificar-Arquivo {
    param($caminho, $descricao)
    if (Test-Path $caminho) {
        Write-Host "✅ $descricao" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $descricao" -ForegroundColor Red
        return $false
    }
}

# Função para verificar conteúdo específico em arquivo
function Verificar-Conteudo {
    param($caminho, $busca, $descricao)
    if (Test-Path $caminho) {
        $conteudo = Get-Content $caminho -Raw
        if ($conteudo -match $busca) {
            Write-Host "✅ $descricao" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $descricao" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ Arquivo não encontrado: $caminho" -ForegroundColor Red
        return $false
    }
}

$sucessos = 0
$total = 0

Write-Host "`n📁 VERIFICANDO NOVOS ARQUIVOS CRIADOS:" -ForegroundColor Yellow
Write-Host "-" * 50

# Verificar novos arquivos criados
$arquivos_novos = @(
    @("app/schemas/blacklist.py", "Schema de Blacklist"),
    @("app/services/blacklist_service.py", "Serviço de Blacklist"),
    @("app/services/discado_service.py", "Serviço de Discado Integrado"),
    @("app/routes/blacklist.py", "Rotas de Blacklist"),
    @("app/routes/discado.py", "Rotas de Discado"),
    @("tests/test_blacklist.py", "Testes de Blacklist"),
    @("migrations/update_blacklist_and_llamadas.sql", "Migração SQL"),
    @("docs/BLACKLIST_MULTIPLES_LISTAS.md", "Documentação Completa"),
    @("test_funcionalidade.py", "Script de Teste Funcional"),
    @("RESUMO_IMPLEMENTACAO.md", "Resumo da Implementação")
)

foreach ($arquivo in $arquivos_novos) {
    $total++
    if (Verificar-Arquivo $arquivo[0] $arquivo[1]) {
        $sucessos++
    }
}

Write-Host "`n📝 VERIFICANDO MODIFICAÇÕES EM ARQUIVOS EXISTENTES:" -ForegroundColor Yellow
Write-Host "-" * 50

# Verificar modificações em arquivos existentes
$modificacoes = @(
    @("app/models/lista_negra.py", "numero_normalizado", "Campo numero_normalizado em ListaNegra"),
    @("app/models/lista_negra.py", "veces_bloqueado", "Campo veces_bloqueado em ListaNegra"),
    @("app/models/llamada.py", "numero_normalizado", "Campo numero_normalizado em Llamada"),
    @("app/models/llamada.py", "id_lista_llamadas", "Campo id_lista_llamadas em Llamada"),
    @("app/models/llamada.py", "bloqueado_blacklist", "Campo bloqueado_blacklist em Llamada"),
    @("app/models/lista_llamadas.py", "llamadas.*relationship", "Relação com Llamadas em ListaLlamadas"),
    @("app/schemas/__init__.py", "BlacklistCreate", "Export de BlacklistCreate"),
    @("main.py", "blacklist.*router", "Router de Blacklist no main.py"),
    @("main.py", "discado.*router", "Router de Discado no main.py")
)

foreach ($mod in $modificacoes) {
    $total++
    if (Verificar-Conteudo $mod[0] $mod[1] $mod[2]) {
        $sucessos++
    }
}

Write-Host "`n🔍 VERIFICANDO FUNCIONALIDADES ESPECÍFICAS:" -ForegroundColor Yellow
Write-Host "-" * 50

# Verificar implementações específicas
$funcionalidades = @(
    @("app/services/blacklist_service.py", "verificar_numero_blacklist", "Método verificar_numero_blacklist"),
    @("app/services/blacklist_service.py", "agregar_numero_blacklist", "Método agregar_numero_blacklist"),
    @("app/services/blacklist_service.py", "agregar_numeros_bulk", "Método agregar_numeros_bulk"),
    @("app/services/discado_service.py", "iniciar_llamada", "Método iniciar_llamada"),
    @("app/services/discado_service.py", "BlacklistService", "Integração com BlacklistService"),
    @("app/routes/blacklist.py", "POST.*verificar", "Endpoint POST /verificar"),
    @("app/routes/blacklist.py", "POST.*agregar-bulk", "Endpoint POST /agregar-bulk"),
    @("app/routes/discado.py", "iniciar-llamada", "Endpoint POST /iniciar-llamada"),
    @("app/routes/discado.py", "llamar-siguiente-lista", "Endpoint POST /llamar-siguiente-lista"),
    @("migrations/update_blacklist_and_llamadas.sql", "ALTER TABLE lista_negra", "Alterações na tabla lista_negra"),
    @("migrations/update_blacklist_and_llamadas.sql", "ALTER TABLE llamadas", "Alterações na tabla llamadas")
)

foreach ($func in $funcionalidades) {
    $total++
    if (Verificar-Conteudo $func[0] $func[1] $func[2]) {
        $sucessos++
    }
}

Write-Host "`n📊 RESUMO DA VERIFICAÇÃO:" -ForegroundColor Cyan
Write-Host "=" * 50
Write-Host "Sucessos: $sucessos/$total" -ForegroundColor $(if ($sucessos -eq $total) { "Green" } else { "Yellow" })
Write-Host "Taxa de sucesso: $([math]::Round(($sucessos/$total)*100, 1))%" -ForegroundColor $(if ($sucessos -eq $total) { "Green" } else { "Yellow" })

if ($sucessos -eq $total) {
    Write-Host "`n🎉 IMPLEMENTAÇÃO COMPLETA!" -ForegroundColor Green
    Write-Host "Todos os arquivos e funcionalidades foram implementados com sucesso." -ForegroundColor Green
} elseif ($sucessos -ge ($total * 0.8)) {
    Write-Host "`n✅ IMPLEMENTAÇÃO QUASE COMPLETA!" -ForegroundColor Yellow
    Write-Host "A maioria dos componentes foi implementada com sucesso." -ForegroundColor Yellow
    Write-Host "Verifique os itens marcados como ❌ acima." -ForegroundColor Yellow
} else {
    Write-Host "`n⚠️ IMPLEMENTAÇÃO PARCIAL" -ForegroundColor Red
    Write-Host "Alguns componentes importantes podem estar faltando." -ForegroundColor Red
    Write-Host "Verifique os itens marcados como ❌ acima." -ForegroundColor Red
}

Write-Host "`n📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Executar as migrações SQL:" -ForegroundColor White
Write-Host "   psql -d discador -f migrations/create_listas_llamadas.sql" -ForegroundColor Gray
Write-Host "   psql -d discador -f migrations/update_blacklist_and_llamadas.sql" -ForegroundColor Gray
Write-Host "2. Testar os endpoints da API usando a documentação em:" -ForegroundColor White
Write-Host "   docs/BLACKLIST_MULTIPLES_LISTAS.md" -ForegroundColor Gray
Write-Host "3. Verificar logs da aplicação após iniciar o servidor:" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor Gray

Write-Host "`n📖 DOCUMENTAÇÃO COMPLETA DISPONÍVEL EM:" -ForegroundColor Cyan
Write-Host "- docs/BLACKLIST_MULTIPLES_LISTAS.md" -ForegroundColor White
Write-Host "- RESUMO_IMPLEMENTACAO.md" -ForegroundColor White

Write-Host "`n✨ Implementação de Blacklist e Múltiplas Listas concluída!" -ForegroundColor Green 