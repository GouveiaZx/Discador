// Configuração da API
// Forçar URL correta sem duplicação
const BASE_URL = import.meta.env.VITE_API_URL || 'https://web-production-c192b.up.railway.app';

// Garantir que não há /api/v1 duplicado
export const API_BASE_URL = BASE_URL.replace(/\/api\/v1$/, '');

// Headers padrão para requisições
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

// Configurações de timeout
export const API_TIMEOUT = 30000; // 30 segundos

// Função helper para construir URLs corretas
export const buildApiUrl = (endpoint) => {
  // Garantir que endpoint começa com /api/v1
  const cleanEndpoint = endpoint.startsWith('/api/v1') ? endpoint : `/api/v1${endpoint}`;
  const finalUrl = `${API_BASE_URL}${cleanEndpoint}`;
  console.log('🔗 Building API URL:', { endpoint, cleanEndpoint, finalUrl });
  return finalUrl;
};

// Função helper para fazer requisições HTTP com tratamento de erro melhorado
export const makeApiRequest = async (endpoint, options = {}) => {
  const url = buildApiUrl(endpoint);
  
  const config = {
    timeout: API_TIMEOUT,
    headers: {
      ...DEFAULT_HEADERS,
      ...options.headers
    },
    ...options
  };

  console.log('🚀 Making API request:', { url, method: config.method || 'GET' });

  try {
    const response = await fetch(url, config);
    
    console.log('📡 API Response:', { 
      url, 
      status: response.status, 
      ok: response.ok,
      contentType: response.headers.get('content-type')
    });

    if (!response.ok) {
      // Verificar se é uma página 404 ou erro do servidor
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('text/html')) {
        console.warn('⚠️ API returned HTML instead of JSON - endpoint may not exist:', url);
        throw new Error(`Endpoint not implemented: ${endpoint} (HTTP ${response.status})`);
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // Verificar se a resposta é JSON válido
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      console.warn('⚠️ API returned non-JSON response:', { url, contentType });
      throw new Error(`Invalid response format from ${endpoint} - expected JSON`);
    }

    const data = await response.json();
    console.log('✅ API Success:', { url, dataKeys: Object.keys(data) });
    return data;
  } catch (error) {
    // Melhor logging de erros
    if (error.name === 'SyntaxError' && error.message.includes('JSON')) {
      console.error('❌ API returned invalid JSON (probably HTML error page):', { url, error: error.message });
      throw new Error(`Endpoint not available: ${endpoint}`);
    }
    
    console.error('❌ API Error:', { url, error: error.message, type: error.name });
    throw error;
  }
};

// Debug: Log da configuração atual
console.log('🔧 API Configuration:', {
  BASE_URL,
  API_BASE_URL,
  VITE_API_URL: import.meta.env.VITE_API_URL,
  NODE_ENV: import.meta.env.NODE_ENV
}); 