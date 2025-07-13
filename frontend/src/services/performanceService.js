import { makeApiRequest } from '../config/api.js';

/**
 * Serviço para gerenciar performance, testes de carga e CLI rotation
 */
class PerformanceService {
  constructor() {
    this.isProduction = !import.meta.env.DEV;
    this.mockData = {
      loadTest: {
        status: 'idle',
        progress: 0,
        results: null
      },
      cliLimits: {
        usa: { country: 'USA', daily_limit: 100, used: 45 },
        canada: { country: 'Canada', daily_limit: 100, used: 23 },
        mexico: { country: 'Mexico', daily_limit: 0, used: 156 },
        brasil: { country: 'Brasil', daily_limit: 0, used: 89 },
        colombia: { country: 'Colombia', daily_limit: 0, used: 67 }
      },
      cliUsage: {
        total_clis: 25000,
        active_clis: 2000,
        blocked_clis: 150,
        countries: ['usa', 'canada', 'mexico', 'brasil', 'colombia']
      },
      dtmfConfigs: {
        usa: { country: 'USA', connect_key: '1', disconnect_key: '9', instructions: 'Press 1 to connect' },
        canada: { country: 'Canada', connect_key: '1', disconnect_key: '9', instructions: 'Press 1 to connect' },
        mexico: { country: 'Mexico', connect_key: '3', disconnect_key: '9', instructions: 'Presione 3 para conectar' },
        brasil: { country: 'Brasil', connect_key: '1', disconnect_key: '9', instructions: 'Pressione 1 para conectar' },
        colombia: { country: 'Colombia', connect_key: '1', disconnect_key: '9', instructions: 'Presione 1 para conectar' }
      }
    };
  }

  // Helper para fallback quando endpoint não existe
  async apiRequestWithFallback(endpoint, method = 'GET', data = null, fallbackData = null) {
    try {
      const response = await makeApiRequest(endpoint, method, data);
      return response;
    } catch (error) {
      if (error.message.includes('Endpoint not implemented') || error.message.includes('404')) {
        console.warn(`🔄 Usando fallback para ${endpoint}`);
        return fallbackData || { status: 'fallback', message: 'Endpoint não implementado, usando mock' };
      }
      throw error;
    }
  }

  // ========== MÉTRICAS EM TEMPO REAL ==========
  /**
   * Obtém métricas em tempo real
   */
  async getRealtimeMetrics() {
    try {
      const response = await makeApiRequest('/performance/metrics/realtime', 'GET');
      return response;
    } catch (error) {
      console.error('❌ Error al obtener métricas en tiempo real:', error);
      throw error;
    }
  }

  /**
   * Obtém histórico de métricas
   */
  async getMetricsHistory(minutes = 60) {
    try {
      const response = await makeApiRequest(`/performance/metrics/history?minutes=${minutes}`, 'GET');
      return response;
    } catch (error) {
      console.error('❌ Error al obtener historial de métricas:', error);
      throw error;
    }
  }

  // ========== WEBSOCKET ==========
  /**
   * Cria conexão WebSocket para métricas em tempo real
   */
  createWebSocketConnection(onMessage, onError, onClose) {
    // Não conectar WebSocket no Vercel ou em produção
    if (window.location.hostname.includes('vercel.app') || this.isProduction) {
      console.log('🚫 WebSocket desabilitado em produção');
      return null;
    }

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/performance/ws/performance`;
      
      const ws = new WebSocket(wsUrl);
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (err) {
          console.error('❌ Error al parsear mensaje WebSocket:', err);
        }
      };
      
      ws.onerror = (error) => {
        console.error('❌ Error WebSocket:', error);
        if (onError) onError(error);
      };
      
      ws.onclose = () => {
        console.log('🔌 WebSocket desconectado');
        if (onClose) onClose();
      };
      
      return ws;
    } catch (error) {
      console.error('❌ Error al crear WebSocket:', error);
      if (onError) onError(error);
      return null;
    }
  }

  // ========== CONTROLE DO DIALER ==========
  /**
   * Inicia o dialer de alta performance
   */
  async startDialer(config) {
    try {
      const response = await makeApiRequest('/performance/dialer/start', 'POST', config);
      return response;
    } catch (error) {
      console.error('❌ Error al iniciar dialer:', error);
      throw error;
    }
  }

  /**
   * Para o dialer
   */
  async stopDialer() {
    try {
      const response = await makeApiRequest('/performance/dialer/stop', 'POST');
      return response;
    } catch (error) {
      console.error('❌ Error al parar dialer:', error);
      throw error;
    }
  }

  /**
   * Define CPS manualmente
   */
  async setCPS(cps) {
    try {
      if (!cps || isNaN(cps) || cps < 1 || cps > 100) {
        throw new Error('CPS deve estar entre 1 e 100');
      }
      
      const response = await makeApiRequest(`/performance/dialer/cps/${cps}`, 'POST');
      return response;
    } catch (error) {
      console.error('❌ Error al definir CPS:', error);
      throw error;
    }
  }

  // ========== TESTES DE CARGA ==========
  /**
   * Inicia teste de carga
   */
  async startLoadTest(config) {
    try {
      const response = await makeApiRequest('/performance/load-test/start', 'POST', config);
      return response;
    } catch (error) {
      console.error('❌ Error al iniciar test de carga:', error);
      throw error;
    }
  }

  /**
   * Para teste de carga
   */
  async stopLoadTest() {
    try {
      const response = await makeApiRequest('/performance/load-test/stop', 'POST');
      return response;
    } catch (error) {
      console.error('❌ Error al parar test de carga:', error);
      throw error;
    }
  }

  /**
   * Obtém status do teste atual
   */
  async getLoadTestStatus() {
    try {
      const response = await this.apiRequestWithFallback('/performance/load-test/status', 'GET', null, {
        status: 'success',
        test_status: this.mockData.loadTest.status,
        progress: this.mockData.loadTest.progress,
        message: 'Mock data - backend em deploy'
      });
      return response;
    } catch (error) {
      console.error('❌ Error al obtener status del test:', error);
      throw error;
    }
  }

  /**
   * Obtém resultados do teste
   */
  async getLoadTestResults(format = 'json') {
    try {
      const response = await this.apiRequestWithFallback(`/performance/load-test/results?format=${format}`, 'GET', null, {
        status: 'success',
        results: this.mockData.loadTest.results,
        message: 'Mock data - backend em deploy'
      });
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener resultados del test:', error);
      throw error;
    }
  }

  // ========== CLI LIMITS ==========
  /**
   * Obtém limites de CLI por país
   */
  async getCliLimits() {
    try {
      const response = await this.apiRequestWithFallback('/performance/cli/limits', 'GET', null, {
        status: 'success',
        limits: this.mockData.cliLimits,
        message: 'Mock data - backend em deploy'
      });
      return response;
    } catch (error) {
      console.error('❌ Error al obtener límites de CLI:', error);
      throw error;
    }
  }

  /**
   * Define limite de CLI para um país
   */
  async updateCliLimits(country, limit) {
    try {
      const requestData = {
        country: country,
        daily_limit: limit
      };
      
      const response = await this.apiRequestWithFallback(`/performance/cli/limits/${country}`, 'POST', requestData, {
        status: 'success',
        country: country,
        new_limit: limit,
        message: `Mock: Limite atualizado para ${country}`
      });
      return response;
    } catch (error) {
      console.error('❌ Error al actualizar límites de CLI:', error);
      throw error;
    }
  }

  /**
   * Obtém estatísticas de uso de CLI
   */
  async getCliUsage() {
    try {
      const response = await this.apiRequestWithFallback('/performance/cli/usage', 'GET', null, {
        status: 'success',
        statistics: this.mockData.cliUsage,
        message: 'Mock data - backend em deploy'
      });
      return response;
    } catch (error) {
      console.error('❌ Error al obtener uso de CLIs:', error);
      throw error;
    }
  }

  /**
   * Reseta uso diário de CLI
   */
  async resetCliUsage(country = null) {
    try {
      const url = country ? `/performance/cli/reset?country=${country}` : '/performance/cli/reset';
      const response = await this.apiRequestWithFallback(url, 'POST', null, {
        status: 'success',
        message: `Mock: Uso resetado${country ? ` para ${country}` : ''}`
      });
      return response;
    } catch (error) {
      console.error('❌ Error al resetear uso de CLI:', error);
      throw error;
    }
  }

  // ========== CLI ROTATION ==========
  /**
   * Obtém dados de rotação de CLI
   */
  async getCliRotationData() {
    try {
      const response = await makeApiRequest('/performance/cli/rotation', 'GET');
      return response;
    } catch (error) {
      console.error('❌ Error al obtener datos de rotación:', error);
      throw error;
    }
  }

  /**
   * Obtém lista de CLIs com filtros
   */
  async getCliList(filters = {}) {
    try {
      const queryParams = new URLSearchParams(filters).toString();
      const response = await makeApiRequest(`/performance/cli/list?${queryParams}`, 'GET');
      return response;
    } catch (error) {
      console.error('❌ Error al obtener lista de CLIs:', error);
      throw error;
    }
  }

  /**
   * Atualiza configuração de rotação de CLI
   */
  async updateCliRotationConfig(config) {
    try {
      const response = await makeApiRequest('/performance/cli/rotation/config', 'POST', config);
      return response;
    } catch (error) {
      console.error('❌ Error al actualizar configuración de rotación:', error);
      throw error;
    }
  }

  // ========== CONFIGURAÇÕES DTMF ==========
  /**
   * Obtém configurações DTMF por país
   */
  async getDTMFConfigs() {
    try {
      const response = await this.apiRequestWithFallback('/performance/dtmf/configs', 'GET', null, {
        status: 'success',
        configurations: this.mockData.dtmfConfigs,
        message: 'Mock data - backend em deploy'
      });
      return response;
    } catch (error) {
      console.error('❌ Error al obtener configuraciones DTMF:', error);
      throw error;
    }
  }

  /**
   * Salva configuração DTMF para um país
   */
  async saveDTMFConfig(config) {
    try {
      const response = await this.apiRequestWithFallback(`/performance/dtmf/config/${config.country}`, 'POST', config, {
        status: 'success',
        country: config.country,
        new_config: config,
        message: `Mock: Configuração DTMF salva para ${config.country}`
      });
      return response;
    } catch (error) {
      console.error('❌ Error al guardar configuración DTMF:', error);
      throw error;
    }
  }

  /**
   * Reseta configuração DTMF para um país
   */
  async resetDTMFConfig(country) {
    try {
      const response = await this.apiRequestWithFallback(`/performance/dtmf/config/reset?country=${country}`, 'POST', null, {
        status: 'success',
        country: country,
        message: `Mock: Configuração DTMF resetada para ${country}`
      });
      return response;
    } catch (error) {
      console.error('❌ Error al resetear configuración DTMF:', error);
      throw error;
    }
  }

  // ========== EXPORTAÇÃO DE DADOS ==========
  /**
   * Exporta dados de performance
   * @param {string} type - Tipo de dados (metrics|cli-usage|test-results)
   * @param {string} format - Formato (json|csv|excel)
   * @param {object} filters - Filtros de exportação
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

  // ========== VALIDAÇÕES E UTILIDADES ==========
  /**
   * Valida configuração de CPS
   * @param {number} cps - CPS a validar
   */
  validateCPS(cps) {
    if (!cps || isNaN(cps) || cps < 1 || cps > 100) {
      throw new Error('CPS debe estar entre 1 y 100');
    }
    return true;
  }

  /**
   * Valida configuração de país
   * @param {string} country - Código del país
   */
  validateCountry(country) {
    const validCountries = [
      // América do Norte
      'usa', 'canada',
      
      // América Latina
      'mexico', 'brasil', 'argentina', 'colombia', 'chile', 'peru', 'venezuela', 'ecuador', 
      'bolivia', 'uruguay', 'paraguay', 'costa_rica', 'panama', 'guatemala', 'honduras', 
      'el_salvador', 'nicaragua', 'republica_dominicana', 'porto_rico',
      
      // Europa
      'espanha', 'portugal', 'franca', 'alemanha', 'italia', 'reino_unido', 'holanda', 
      'belgica', 'suica', 'austria',
      
      // Ásia
      'india', 'filipinas', 'malasia', 'singapura', 'tailandia', 'indonesia',
      
      // Oceania
      'australia', 'nova_zelandia',
      
      // África
      'africa_do_sul',
      
      // Oriente Médio
      'israel'
    ];
    
    if (!validCountries.includes(country)) {
      throw new Error(`País no válido: ${country}`);
    }
    return true;
  }

  /**
   * Obtém configurações por defecto por país
   */
  getDefaultCountryConfigs() {
    return {
      // América do Norte
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
      
      // América Latina
      mexico: {
        name: 'México',
        flag: '🇲🇽',
        cli_limit: 0,
        dtmf_key: '3',
        timezone: 'America/Mexico_City'
      },
      brasil: {
        name: 'Brasil',
        flag: '🇧🇷',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Sao_Paulo'
      },
      argentina: {
        name: 'Argentina',
        flag: '🇦🇷',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Argentina/Buenos_Aires'
      },
      colombia: {
        name: 'Colombia',
        flag: '🇨🇴',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Bogota'
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
      },
      venezuela: {
        name: 'Venezuela',
        flag: '🇻🇪',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Caracas'
      },
      ecuador: {
        name: 'Ecuador',
        flag: '🇪🇨',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Guayaquil'
      },
      bolivia: {
        name: 'Bolivia',
        flag: '🇧🇴',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/La_Paz'
      },
      uruguay: {
        name: 'Uruguay',
        flag: '🇺🇾',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Montevideo'
      },
      paraguay: {
        name: 'Paraguay',
        flag: '🇵🇾',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Asuncion'
      },
      costa_rica: {
        name: 'Costa Rica',
        flag: '🇨🇷',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Costa_Rica'
      },
      panama: {
        name: 'Panamá',
        flag: '🇵🇦',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Panama'
      },
      guatemala: {
        name: 'Guatemala',
        flag: '🇬🇹',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Guatemala'
      },
      honduras: {
        name: 'Honduras',
        flag: '🇭🇳',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Tegucigalpa'
      },
      el_salvador: {
        name: 'El Salvador',
        flag: '🇸🇻',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/El_Salvador'
      },
      nicaragua: {
        name: 'Nicaragua',
        flag: '🇳🇮',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Managua'
      },
      republica_dominicana: {
        name: 'República Dominicana',
        flag: '🇩🇴',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Santo_Domingo'
      },
      porto_rico: {
        name: 'Porto Rico',
        flag: '🇵🇷',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'America/Puerto_Rico'
      },
      
      // Europa
      espanha: {
        name: 'España',
        flag: '🇪🇸',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Europe/Madrid'
      },
      portugal: {
        name: 'Portugal',
        flag: '🇵🇹',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Europe/Lisbon'
      },
      franca: {
        name: 'França',
        flag: '🇫🇷',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Europe/Paris'
      },
      alemanha: {
        name: 'Alemanha',
        flag: '🇩🇪',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Europe/Berlin'
      },
      italia: {
        name: 'Itália',
        flag: '🇮🇹',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Europe/Rome'
      },
      reino_unido: {
        name: 'Reino Unido',
        flag: '🇬🇧',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Europe/London'
      },
      holanda: {
        name: 'Holanda',
        flag: '🇳🇱',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Europe/Amsterdam'
      },
      belgica: {
        name: 'Bélgica',
        flag: '🇧🇪',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Europe/Brussels'
      },
      suica: {
        name: 'Suíça',
        flag: '🇨🇭',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Europe/Zurich'
      },
      austria: {
        name: 'Áustria',
        flag: '🇦🇹',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Europe/Vienna'
      },
      
      // Ásia
      india: {
        name: 'Índia',
        flag: '🇮🇳',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Asia/Kolkata'
      },
      filipinas: {
        name: 'Filipinas',
        flag: '🇵🇭',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Asia/Manila'
      },
      malasia: {
        name: 'Malásia',
        flag: '🇲🇾',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Asia/Kuala_Lumpur'
      },
      singapura: {
        name: 'Singapura',
        flag: '🇸🇬',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Asia/Singapore'
      },
      tailandia: {
        name: 'Tailândia',
        flag: '🇹🇭',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Asia/Bangkok'
      },
      indonesia: {
        name: 'Indonésia',
        flag: '🇮🇩',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Asia/Jakarta'
      },
      
      // Oceania
      australia: {
        name: 'Austrália',
        flag: '🇦🇺',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Australia/Sydney'
      },
      nova_zelandia: {
        name: 'Nova Zelândia',
        flag: '🇳🇿',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Pacific/Auckland'
      },
      
      // África
      africa_do_sul: {
        name: 'África do Sul',
        flag: '🇿🇦',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Africa/Johannesburg'
      },
      
      // Oriente Médio
      israel: {
        name: 'Israel',
        flag: '🇮🇱',
        cli_limit: 0,
        dtmf_key: '1',
        timezone: 'Asia/Jerusalem'
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

// Instancia del servicio
const performanceService = new PerformanceService();

export default performanceService; 