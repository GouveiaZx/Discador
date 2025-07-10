import { makeApiRequest } from '../config/api.js';

/**
 * Serviço para APIs de Performance Avançado
 * Inclui métricas em tempo real, CLI limits, DTMF config e load testing
 */
class PerformanceService {
  
  // ========== MÉTRICAS EM TEMPO REAL ==========
  
  /**
   * Obtém métricas em tempo real do sistema
   */
  async getRealtimeMetrics() {
    try {
      const response = await makeApiRequest('/performance/metrics/realtime', 'GET');
      return response;
    } catch (error) {
      console.error('❌ Erro ao obter métricas em tempo real:', error);
      throw error;
    }
  }

  /**
   * Obtém histórico de métricas
   * @param {number} minutes - Minutos de histórico (padrão 60)
   */
  async getMetricsHistory(minutes = 60) {
    try {
      const response = await makeApiRequest(`/performance/metrics/history?minutes=${minutes}`, 'GET');
      return response;
    } catch (error) {
      console.error('❌ Erro ao obter histórico de métricas:', error);
      throw error;
    }
  }

  /**
   * Cria conexão WebSocket para métricas em tempo real
   * @param {function} onMessage - Callback para receber mensagens
   * @param {function} onError - Callback para erros
   * @param {function} onClose - Callback para fechamento da conexão
   */
  createWebSocketConnection(onMessage, onError, onClose) {
    const wsUrl = import.meta.env.DEV 
      ? 'ws://localhost:8000/api/performance/ws/performance'
      : 'wss://discador.onrender.com/api/performance/ws/performance';
    
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('❌ Erro ao processar mensagem WebSocket:', error);
        onError(error);
      }
    };
    
    ws.onerror = (error) => {
      console.error('❌ Erro na conexão WebSocket:', error);
      onError(error);
    };
    
    ws.onclose = () => {
      console.log('🔌 Conexão WebSocket fechada');
      onClose();
    };
    
    ws.onopen = () => {
      console.log('✅ Conexão WebSocket estabelecida');
    };
    
    return ws;
  }

  // ========== SISTEMA DE DISCADO ==========

  /**
   * Inicia o sistema de discado de alta performance
   * @param {object} config - Configurações do dialer
   */
  async startDialer(config) {
    try {
      const response = await makeApiRequest('/performance/dialer/start', 'POST', config);
      return response;
    } catch (error) {
      console.error('❌ Erro ao iniciar dialer:', error);
      throw error;
    }
  }

  /**
   * Para o sistema de discado
   */
  async stopDialer() {
    try {
      const response = await makeApiRequest('/performance/dialer/stop', 'POST');
      return response;
    } catch (error) {
      console.error('❌ Erro ao parar dialer:', error);
      throw error;
    }
  }

  /**
   * Define manualmente o CPS do sistema
   * @param {number} cps - Chamadas por segundo
   */
  async setCPS(cps) {
    try {
      const response = await makeApiRequest(`/performance/dialer/cps/${cps}`, 'POST');
      return response;
    } catch (error) {
      console.error('❌ Erro ao definir CPS:', error);
      throw error;
    }
  }

  // ========== TESTE DE CARGA ==========

  /**
   * Inicia teste de carga
   * @param {object} config - Configurações do teste
   */
  async startLoadTest(config) {
    try {
      const response = await makeApiRequest('/performance/load-test/start', 'POST', config);
      return response;
    } catch (error) {
      console.error('❌ Erro ao iniciar teste de carga:', error);
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
      console.error('❌ Erro ao parar teste de carga:', error);
      throw error;
    }
  }

  /**
   * Obtém status do teste de carga
   */
  async getLoadTestStatus() {
    try {
      const response = await makeApiRequest('/performance/load-test/status', 'GET');
      return response;
    } catch (error) {
      console.error('❌ Erro ao obter status do teste:', error);
      throw error;
    }
  }

  /**
   * Obtém resultados do teste de carga
   * @param {string} format - Formato dos resultados (json, csv, excel)
   */
  async getLoadTestResults(format = 'json') {
    try {
      const response = await makeApiRequest(`/performance/load-test/results?format=${format}`, 'GET');
      return response;
    } catch (error) {
      console.error('❌ Erro ao obter resultados do teste:', error);
      throw error;
    }
  }

  // ========== CLI LIMITS (LIMITES DE CLI) ==========

  /**
   * Obtém limites de CLI por país
   */
  async getCliLimits() {
    try {
      const response = await makeApiRequest('/performance/cli/limits', 'GET');
      return response;
    } catch (error) {
      console.error('❌ Erro ao obter limites de CLI:', error);
      throw error;
    }
  }

  /**
   * Define limite de CLI para um país
   * @param {string} country - Código do país
   * @param {number} dailyLimit - Limite diário de uso
   */
  async setCliLimit(country, dailyLimit) {
    try {
      const response = await makeApiRequest(`/performance/cli/limits/${country}`, 'POST', {
        country,
        daily_limit: dailyLimit
      });
      return response;
    } catch (error) {
      console.error('❌ Erro ao definir limite de CLI:', error);
      throw error;
    }
  }

  /**
   * Obtém estatísticas de uso de CLI
   */
  async getCliUsage() {
    try {
      const response = await makeApiRequest('/performance/cli/usage', 'GET');
      return response;
    } catch (error) {
      console.error('❌ Erro ao obter uso de CLI:', error);
      throw error;
    }
  }

  /**
   * Reseta contadores de uso de CLI
   */
  async resetCliUsage() {
    try {
      const response = await makeApiRequest('/performance/cli/reset', 'POST');
      return response;
    } catch (error) {
      console.error('❌ Erro ao resetar uso de CLI:', error);
      throw error;
    }
  }

  // ========== DTMF CONFIG (CONFIGURAÇÃO DTMF) ==========

  /**
   * Obtém configurações DTMF por país
   */
  async getDTMFConfig() {
    try {
      const response = await makeApiRequest('/performance/dtmf/config', 'GET');
      return response;
    } catch (error) {
      console.error('❌ Erro ao obter configurações DTMF:', error);
      throw error;
    }
  }

  /**
   * Atualiza configuração DTMF para um país
   * @param {string} country - Código do país
   * @param {object} config - Configurações DTMF
   */
  async updateDTMFConfig(country, config) {
    try {
      const response = await makeApiRequest(`/performance/dtmf/config/${country}`, 'POST', config);
      return response;
    } catch (error) {
      console.error('❌ Erro ao atualizar configuração DTMF:', error);
      throw error;
    }
  }

  // ========== HEALTH CHECK ==========

  /**
   * Verifica saúde do sistema de performance
   */
  async healthCheck() {
    try {
      const response = await makeApiRequest('/performance/health', 'GET');
      return response;
    } catch (error) {
      console.error('❌ Erro no health check:', error);
      throw error;
    }
  }

  // ========== UTILITÁRIOS ==========

  /**
   * Formata dados de métricas para gráficos
   * @param {array} metricsHistory - Histórico de métricas
   */
  formatMetricsForChart(metricsHistory) {
    if (!metricsHistory || !Array.isArray(metricsHistory)) {
      return {
        labels: [],
        datasets: []
      };
    }

    return {
      labels: metricsHistory.map(m => new Date(m.timestamp).toLocaleTimeString()),
      datasets: [
        {
          label: 'CPS Atual',
          data: metricsHistory.map(m => m.current_cps),
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true
        },
        {
          label: 'Chamadas Simultâneas',
          data: metricsHistory.map(m => m.concurrent_calls),
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true
        },
        {
          label: 'Taxa de Sucesso (%)',
          data: metricsHistory.map(m => (m.success_rate * 100).toFixed(1)),
          borderColor: '#F59E0B',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true
        }
      ]
    };
  }

  /**
   * Obtém configurações padrão para países
   */
  getDefaultCountryConfigs() {
    return {
      usa: {
        cli_limit: 100,
        dtmf_config: {
          connect_key: "1",
          disconnect_key: "9",
          repeat_key: "0",
          menu_timeout: 10,
          instructions: "Press 1 to connect, 9 to disconnect, 0 to repeat"
        }
      },
      canada: {
        cli_limit: 100,
        dtmf_config: {
          connect_key: "1",
          disconnect_key: "9",
          repeat_key: "0",
          menu_timeout: 10,
          instructions: "Press 1 to connect, 9 to disconnect, 0 to repeat"
        }
      },
      mexico: {
        cli_limit: 0, // Ilimitado
        dtmf_config: {
          connect_key: "3", // Especial para México
          disconnect_key: "9",
          repeat_key: "0",
          menu_timeout: 15,
          instructions: "Presione 3 para conectar, 9 para desconectar, 0 para repetir"
        }
      },
      brasil: {
        cli_limit: 0, // Ilimitado
        dtmf_config: {
          connect_key: "1",
          disconnect_key: "9",
          repeat_key: "0",
          menu_timeout: 10,
          instructions: "Pressione 1 para conectar, 9 para desconectar, 0 para repetir"
        }
      },
      colombia: {
        cli_limit: 0, // Ilimitado
        dtmf_config: {
          connect_key: "1",
          disconnect_key: "9",
          repeat_key: "0",
          menu_timeout: 10,
          instructions: "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        }
      },
      argentina: {
        cli_limit: 0, // Ilimitado
        dtmf_config: {
          connect_key: "1",
          disconnect_key: "9",
          repeat_key: "0",
          menu_timeout: 10,
          instructions: "Presione 1 para conectar, 9 para desconectar, 0 para repetir"
        }
      }
    };
  }

  /**
   * Valida configurações de teste de carga
   * @param {object} config - Configurações a validar
   */
  validateLoadTestConfig(config) {
    const errors = [];

    if (!config.target_cps || config.target_cps < 1 || config.target_cps > 50) {
      errors.push('CPS deve estar entre 1 e 50');
    }

    if (!config.duration_minutes || config.duration_minutes < 1 || config.duration_minutes > 120) {
      errors.push('Duração deve estar entre 1 e 120 minutos');
    }

    if (!config.countries_to_test || config.countries_to_test.length === 0) {
      errors.push('Deve selecionar pelo menos um país para teste');
    }

    if (!config.number_of_clis || config.number_of_clis < 10 || config.number_of_clis > 50000) {
      errors.push('Número de CLIs deve estar entre 10 e 50000');
    }

    return errors;
  }
}

// Instância singleton
const performanceService = new PerformanceService();

export default performanceService; 