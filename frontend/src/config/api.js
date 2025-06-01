// Configuração da API
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://web-production-c192b.up.railway.app';

// Headers padrão para requisições
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

// Configurações de timeout
export const API_TIMEOUT = 30000; // 30 segundos 