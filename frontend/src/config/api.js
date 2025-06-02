// Configuração da API
// Limpar e validar URL base
const cleanUrl = (url) => {
  if (!url) return '';
  // Remover espaços, emojis e caracteres especiais
  return url.trim().replace(/[^\w\-.:\/]/g, '');
};

const BASE_URL = cleanUrl(import.meta.env.VITE_API_URL) || 'https://web-production-c192b.up.railway.app';

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

    // Verificar se é erro 404 (endpoint não implementado)
    if (response.status === 404) {
      console.warn('⚠️ Server returned 404 - endpoint not implemented');
      throw new Error(`Endpoint not implemented: ${endpoint}`);
    }

    // Verificar se a resposta é HTML (endpoint não existe)
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('text/html')) {
      console.warn('⚠️ Server returned HTML page - endpoint probably does not exist');
      throw new Error(`Endpoint not implemented: ${endpoint}`);
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // Verificar se a resposta é JSON válido
    if (!contentType || !contentType.includes('application/json')) {
      console.warn('⚠️ API returned non-JSON response:', { url, contentType });
      throw new Error(`Endpoint not implemented: ${endpoint}`);
    }

    const data = await response.json();
    console.log('✅ API Success:', { url, dataKeys: Object.keys(data) });
    return data;
  } catch (error) {
    // Melhor logging de erros
    if (error.name === 'SyntaxError' && error.message.includes('JSON')) {
      console.info('ℹ️ Server endpoint not available, using fallback data');
      throw new Error(`Endpoint not implemented: ${endpoint}`);
    }
    
    if (error.message.includes('Endpoint not implemented')) {
      console.info(`ℹ️ Using mock data for ${endpoint} (backend not available)`);
      throw error;
    }
    
    console.error('❌ API Error:', { url, error: error.message, type: error.name });
    throw error;
  }
};

// Debug: Log da configuração atual (apenas em desenvolvimento)
if (import.meta.env.DEV) {
  console.log('🔧 API Configuration:', {
    'Raw VITE_API_URL': import.meta.env.VITE_API_URL,
    'Cleaned BASE_URL': BASE_URL,
    'Final API_BASE_URL': API_BASE_URL,
    'NODE_ENV': import.meta.env.NODE_ENV
  });
} 