import { makeApiRequest } from '../config/api.js';

/**
 * Servicio para APIs de Performance Avanzado
 * Gestiona todas las operaciones de performance, tests de carga y gestión de CLIs
 */
class PerformanceService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
  }

  // ========== MÉTRICAS EN TIEMPO REAL ==========
  /**
   * Obtiene métricas en tiempo real del sistema
   */
  async getRealtimeMetrics() {
    try {
      const response = await makeApiRequest('/performance/metrics/realtime', 'GET');
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener métricas en tiempo real:', error);
      throw error;
    }
  }

  /**
   * Obtiene historial de métricas
   * @param {number} minutes - Minutos de historial
   */
  async getMetricsHistory(minutes = 60) {
    try {
      const response = await makeApiRequest(`/performance/metrics/history?minutes=${minutes}`, 'GET');
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener historial de métricas:', error);
      throw error;
    }
  }

  /**
   * Crea conexión WebSocket para métricas en tiempo real
   * @param {function} onMessage - Callback para mensajes
   * @param {function} onError - Callback para errores
   * @param {function} onClose - Callback para cierre
   */
  createWebSocketConnection(onMessage, onError, onClose) {
    const wsUrl = process.env.NODE_ENV === 'development' 
      ? 'ws://localhost:8000/api/performance/ws/performance'
      : 'wss://discador.onrender.com/api/performance/ws/performance';
    
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('❌ Error al procesar mensaje WebSocket:', error);
        onError(error);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ Error en conexión WebSocket:', error);
      onError(error);
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket desconectado');
      if (onClose) onClose();
    };

    return ws;
  }

  // ========== SISTEMA DE DISCADO ==========
  /**
   * Inicia el sistema de discado de alta performance
   * @param {object} config - Configuraciones del discado
   */
  async startDialer(config) {
    try {
      const response = await makeApiRequest('/performance/dialer/start', 'POST', config);
      return response.data;
    } catch (error) {
      console.error('❌ Error al iniciar dialer:', error);
      throw error;
    }
  }

  /**
   * Para el sistema de discado
   */
  async stopDialer() {
    try {
      const response = await makeApiRequest('/performance/dialer/stop', 'POST');
      return response.data;
    } catch (error) {
      console.error('❌ Error al parar dialer:', error);
      throw error;
    }
  }

  /**
   * Define manualmente el CPS del sistema
   * @param {number} cps - CPS objetivo
   */
  async setCPS(cps) {
    try {
      const response = await makeApiRequest(`/performance/dialer/cps/${cps}`, 'POST');
      return response.data;
    } catch (error) {
      console.error('❌ Error al definir CPS:', error);
      throw error;
    }
  }

  // ========== TEST DE CARGA ==========
  /**
   * Inicia test de carga
   * @param {object} config - Configuraciones del test
   */
  async startLoadTest(config) {
    try {
      const response = await makeApiRequest('/performance/load-test/start', 'POST', config);
      return response.data;
    } catch (error) {
      console.error('❌ Error al iniciar test de carga:', error);
      throw error;
    }
  }

  /**
   * Para test de carga
   */
  async stopLoadTest() {
    try {
      const response = await makeApiRequest('/performance/load-test/stop', 'POST');
      return response.data;
    } catch (error) {
      console.error('❌ Error al parar test de carga:', error);
      throw error;
    }
  }

  /**
   * Obtiene status del test de carga
   */
  async getLoadTestStatus() {
    try {
      const response = await makeApiRequest('/performance/load-test/status', 'GET');
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener status del test:', error);
      throw error;
    }
  }

  /**
   * Obtiene resultados del test de carga
   * @param {string} format - Formato de exportación (json|csv|excel)
   */
  async getLoadTestResults(format = 'json') {
    try {
      const response = await makeApiRequest(`/performance/load-test/results?format=${format}`, 'GET');
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener resultados del test:', error);
      throw error;
    }
  }

  // ========== CLI LIMITS (LÍMITES DE CLI) ==========
  /**
   * Obtiene límites de CLI por país
   */
  async getCliLimits() {
    try {
      const response = await makeApiRequest('/performance/cli/limits', 'GET');
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener límites de CLI:', error);
      throw error;
    }
  }

  /**
   * Actualiza límites de CLI por país
   * @param {string} country - Código del país
   * @param {number} limit - Límite diario
   */
  async updateCliLimits(country, limit) {
    try {
      const response = await makeApiRequest('/performance/cli/limits', 'POST', {
        country,
        daily_limit: limit
      });
      return response.data;
    } catch (error) {
      console.error('❌ Error al actualizar límites de CLI:', error);
      throw error;
    }
  }

  /**
   * Obtiene uso actual de CLIs
   */
  async getCliUsage() {
    try {
      const response = await makeApiRequest('/performance/cli/usage', 'GET');
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener uso de CLIs:', error);
      throw error;
    }
  }

  /**
   * Resetea contadores de uso de CLIs
   * @param {string} country - País específico (opcional)
   */
  async resetCliUsage(country = null) {
    try {
      const url = country ? `/performance/cli/usage/reset?country=${country}` : '/performance/cli/usage/reset';
      const response = await makeApiRequest(url, 'POST');
      return response.data;
    } catch (error) {
      console.error('❌ Error al resetear uso de CLIs:', error);
      throw error;
    }
  }

  // ========== ROTACIÓN DE CLIS ==========
  /**
   * Obtiene datos de rotación de CLIs
   */
  async getCliRotationData() {
    try {
      const response = await makeApiRequest('/performance/cli/rotation', 'GET');
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener datos de rotación:', error);
      throw error;
    }
  }

  /**
   * Obtiene lista de CLIs con filtros
   * @param {object} filters - Filtros de búsqueda
   */
  async getCliList(filters = {}) {
    try {
      const queryParams = new URLSearchParams(filters).toString();
      const response = await makeApiRequest(`/performance/cli/list?${queryParams}`, 'GET');
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener lista de CLIs:', error);
      throw error;
    }
  }

  /**
   * Actualiza configuración de rotación de CLIs
   * @param {object} config - Configuración de rotación
   */
  async updateCliRotationConfig(config) {
    try {
      const response = await makeApiRequest('/performance/cli/rotation/config', 'POST', config);
      return response.data;
    } catch (error) {
      console.error('❌ Error al actualizar configuración de rotación:', error);
      throw error;
    }
  }

  // ========== CONFIGURACIÓN DTMF ==========
  /**
   * Obtiene configuraciones DTMF por país
   */
  async getDTMFConfigs() {
    try {
      const response = await makeApiRequest('/performance/dtmf/configs', 'GET');
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener configuraciones DTMF:', error);
      throw error;
    }
  }

  /**
   * Guarda configuración DTMF para un país
   * @param {object} config - Configuración DTMF
   */
  async saveDTMFConfig(config) {
    try {
      const response = await makeApiRequest('/performance/dtmf/config', 'POST', config);
      return response.data;
    } catch (error) {
      console.error('❌ Error al guardar configuración DTMF:', error);
      throw error;
    }
  }

  /**
   * Resetea configuración DTMF a valores por defecto
   * @param {string} country - Código del país
   */
  async resetDTMFConfig(country) {
    try {
      const response = await makeApiRequest(`/performance/dtmf/config/reset?country=${country}`, 'POST');
      return response.data;
    } catch (error) {
      console.error('❌ Error al resetear configuración DTMF:', error);
      throw error;
    }
  }

  // ========== EXPORTACIÓN DE DATOS ==========
  /**
   * Exporta datos de performance
   * @param {string} type - Tipo de datos (metrics|cli-usage|test-results)
   * @param {string} format - Formato (json|csv|excel)
   * @param {object} filters - Filtros de exportación
   */
  async exportData(type, format = 'json', filters = {}) {
    try {
      const queryParams = new URLSearchParams({ format, ...filters }).toString();
      const response = await makeApiRequest(`/performance/export/${type}?${queryParams}`, 'GET');
      return response.data;
    } catch (error) {
      console.error('❌ Error al exportar datos:', error);
      throw error;
    }
  }

  // ========== VALIDACIONES Y UTILIDADES ==========
  /**
   * Valida configuración de CPS
   * @param {number} cps - CPS a validar
   */
  validateCPS(cps) {
    if (!cps || isNaN(cps) || cps < 1 || cps > 100) {
      throw new Error('CPS debe estar entre 1 y 100');
    }
    return true;
  }

  /**
   * Valida configuración de país
   * @param {string} country - Código del país
   */
  validateCountry(country) {
    const validCountries = ['usa', 'canada', 'mexico', 'brasil', 'colombia', 'argentina', 'chile', 'peru'];
    if (!validCountries.includes(country)) {
      throw new Error(`País no válido: ${country}`);
    }
    return true;
  }

  /**
   * Obtiene configuraciones por defecto por país
   */
  getDefaultCountryConfigs() {
    return {
      usa: {
        name: 'Estados Unidos',
        flag: '🇺🇸',
        cli_limit: 100,
        dtmf_key: '1',
        timezone: 'America/New_York'
      },
      canada: {
        name: 'Canadá',
        flag: '🇨🇦',
        cli_limit: 100,
        dtmf_key: '1',
        timezone: 'America/Toronto'
      },
      mexico: {
        name: 'México',
        flag: '🇲🇽',
        cli_limit: 0, // Sin límite
        dtmf_key: '3', // Especial para México
        timezone: 'America/Mexico_City'
      },
      brasil: {
        name: 'Brasil',
        flag: '🇧🇷',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Sao_Paulo'
      },
      colombia: {
        name: 'Colombia',
        flag: '🇨🇴',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Bogota'
      },
      argentina: {
        name: 'Argentina',
        flag: '🇦🇷',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Argentina/Buenos_Aires'
      },
      chile: {
        name: 'Chile',
        flag: '🇨🇱',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Santiago'
      },
      peru: {
        name: 'Perú',
        flag: '🇵🇪',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Lima'
      }
    };
  }

  /**
   * Formatea números para mostrar
   * @param {number} num - Número a formatear
   */
  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num?.toString() || '0';
  }

  /**
   * Formatea duración en segundos
   * @param {number} seconds - Segundos a formatear
   */
  formatDuration(seconds) {
    if (!seconds) return '0s';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${remainingSeconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    } else {
      return `${remainingSeconds}s`;
    }
  }

  /**
   * Calcula porcentaje de uso
   * @param {number} used - Cantidad usada
   * @param {number} limit - Límite total
   */
  calculateUsagePercentage(used, limit) {
    if (!limit || limit === 0) return 0;
    return Math.min(Math.round((used / limit) * 100), 100);
  }

  /**
   * Obtiene color de status según porcentaje
   * @param {number} percentage - Porcentaje
   */
  getStatusColor(percentage) {
    if (percentage >= 90) return 'danger';
    if (percentage >= 70) return 'warning';
    return 'success';
  }
}

// Función auxiliar para hacer requests HTTP
async function makeApiRequest(endpoint, method = 'GET', data = null) {
  const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
  const url = `${baseURL}${endpoint}`;
  
  const config = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
    }
  };

  if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
    config.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Error HTTP: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`❌ Error en API ${method} ${endpoint}:`, error);
    throw error;
  }
}

// Instancia del servicio
const performanceService = new PerformanceService();

export default performanceService; 