// Configuração da API
// Limpar e validar URL base
const cleanUrl = (url) => {
  if (!url) return '';
  // Remover espaços, emojis e caracteres especiais
  return url.trim().replace(/[^\w\-.:\/]/g, '');
};

// CORREÇÃO: Forçar URL correta em produção
const BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:8000'  // Desenvolvimento: usar backend local
  : 'https://discador.onrender.com'; // Produção: forçar URL correta do Render.com

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
export const makeApiRequest = async (endpoint, methodOrOptions = {}, data = null) => {
  const url = buildApiUrl(endpoint);
  
  // Se o segundo parâmetro é uma string, é um método HTTP
  let config;
  if (typeof methodOrOptions === 'string') {
    config = {
      method: methodOrOptions,
      timeout: API_TIMEOUT,
      headers: {}
    };
    
    // Se há dados, adicionar ao body
    if (data && (methodOrOptions === 'POST' || methodOrOptions === 'PUT' || methodOrOptions === 'PATCH')) {
      // Se é FormData, não definir Content-Type (browser define automaticamente)
      if (data instanceof FormData) {
        config.body = data;
      } else {
        // Se não é FormData, definir Content-Type como JSON
        config.headers['Content-Type'] = 'application/json';
        config.body = JSON.stringify(data);
      }
    } else {
      // Para GET requests, definir Content-Type padrão
      config.headers = { ...DEFAULT_HEADERS };
    }
  } else {
    // Forma tradicional: segundo parâmetro é um objeto de opções
    config = {
      timeout: API_TIMEOUT,
      headers: {},
      ...methodOrOptions
    };
    
    // Se há body e não é FormData, definir Content-Type
    if (config.body && !(config.body instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
    }
    
    // Adicionar headers padrão apenas se não conflitarem
    if (!config.body || !(config.body instanceof FormData)) {
      config.headers = { ...DEFAULT_HEADERS, ...config.headers };
    }
  }

  console.log('🚀 Making API request:', { url, method: config.method || 'GET', hasBody: !!config.body });

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