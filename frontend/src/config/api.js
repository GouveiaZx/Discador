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

// Função helper para fazer requisições HTTP com tratamento de erro
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
      ok: response.ok 
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ API Success:', { url, dataKeys: Object.keys(data) });
    return data;
  } catch (error) {
    console.error('❌ API Error:', { url, error: error.message });
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