// Teste simples para verificar a conexão com o backend
const API_BASE_URL = 'http://localhost:8000';

async function testPauseEndpoint() {
    try {
        console.log('🔍 Testando conexão com o backend...');
        
        // Primeiro, testar se o servidor está rodando
        const healthResponse = await fetch(`${API_BASE_URL}/health`);
        console.log('✅ Servidor está rodando:', healthResponse.status);
        
        // Testar o endpoint de pausar
        const pauseUrl = `${API_BASE_URL}/api/v1/presione1/campanhas/1/pausar`;
        console.log('🔗 URL de teste:', pauseUrl);
        
        const response = await fetch(pauseUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                campana_id: 1,
                pausar: true,
                usuario_id: 'frontend_user',
                motivo: 'Teste via JavaScript'
            })
        });
        
        console.log('📡 Status da resposta:', response.status);
        console.log('📡 Headers da resposta:', Object.fromEntries(response.headers.entries()));
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Resposta de sucesso:', data);
        } else {
            const errorText = await response.text();
            console.log('❌ Erro na resposta:', errorText);
        }
        
    } catch (error) {
        console.error('❌ Erro na requisição:', error.message);
        console.error('Stack trace:', error.stack);
    }
}

// Executar o teste
testPauseEndpoint();