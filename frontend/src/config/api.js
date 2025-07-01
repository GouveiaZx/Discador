// Configuração da API
// Limpar e validar URL base
const cleanUrl = (url) => {
  if (!url) return '';
  // Remover espaços, emojis e caracteres especiais
  return url.trim().replace(/[^\w\-.:\/]/g, '');
};

// CORREÇÃO: Usar localhost em desenvolvimento
const BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:8000'  // Desenvolvimento: usar backend local
  : cleanUrl(import.meta.env.VITE_API_URL) || 'https://web-production-c192b.up.railway.app';

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
  // CORREÇÃO: Redirecionar automaticamente rotas de áudio para o serviço de correção
  const AUDIO_ENDPOINTS = [
    '/audio/contextos',
    '/audio/setup-padrao',
    '/multi-sip/provedores',
    '/code2base/clis',
    '/audio-inteligente/contextos'
  ];

  const isAudioEndpoint = AUDIO_ENDPOINTS.some(path => endpoint.includes(path.replace('/api/v1', '')));
  
  if (isAudioEndpoint && import.meta.env.DEV) {
    console.log('🔄 Redirecting to correction service:', endpoint);
    return makeMultiSipRequest(endpoint, options);
  }

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
      throw new Error(`Endpoint not implemented: ${endpoint}`);
    }
    
    if (error.message.includes('Endpoint not implemented')) {
      // Endpoint não disponível no backend
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

// CORREÇÃO URGENTE: Função especial para rotas multi-sip
export const makeMultiSipRequest = async (endpoint, options = {}) => {
  // Redirecionar chamadas para o serviço de correção na porta 8001
  const MULTISIP_ENDPOINTS = [
    '/multi-sip/provedores',
    '/code2base/clis',
    '/audio-inteligente/contextos',
    '/audio/contextos',
    '/audio/setup-padrao',
    '/api/v1/configuracion-avanzada/status'
  ];

  const isMultiSipEndpoint = MULTISIP_ENDPOINTS.some(path => endpoint.includes(path));
  
  if (isMultiSipEndpoint) {
    const url = `http://localhost:8001${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    console.log('🔧 Multi-SIP Request (Port 8001):', { url, method: config.method || 'GET' });

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Multi-SIP Success:', { url, data });
      return data;
    } catch (error) {
      console.error('❌ Multi-SIP Error:', { url, error: error.message });
      throw error;
    }
  }

  // Caso não seja multi-sip, usar função padrão
  return makeApiRequest(endpoint, options);
}; 