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
  return `${API_BASE_URL}${cleanEndpoint}`;
};

// Debug: Log da configuração atual
console.log('🔧 API Configuration:', {
  BASE_URL,
  API_BASE_URL,
  VITE_API_URL: import.meta.env.VITE_API_URL
}); 