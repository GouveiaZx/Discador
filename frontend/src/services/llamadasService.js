/**
 * Serviço para interagir com a API de chamadas
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Obtém todas as chamadas com estado 'en_progreso'
 * @returns {Promise} Promessa com os dados das chamadas
 */
export const obtenerLlamadasEnProgreso = async () => {
  try {
    const response = await fetch(`${API_URL}/llamadas/en-progreso`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Error al obtener llamadas en progreso');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al obtener las llamadas en progreso:', error);
    throw error;
  }
};

/**
 * Finaliza manualmente una llamada
 * @param {number} llamadaId - ID de la llamada a finalizar
 * @returns {Promise} Promessa com o resultado da finalização
 */
export const finalizarLlamadaManualmente = async (llamadaId) => {
  try {
    const response = await fetch(`${API_URL}/llamadas/finalizar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        llamada_id: llamadaId,
        resultado: 'finalizada_por_admin'
      })
    });

    if (!response.ok) {
      throw new Error('Error al finalizar llamada');
    }

    return await response.json();
  } catch (error) {
    console.error(`Error al finalizar la llamada ID ${llamadaId}:`, error);
    throw error;
  }
};

/**
 * Obtém o histórico de chamadas com filtros e paginação
 * @param {Object} filters - Objeto com os filtros a aplicar
 * @param {number} page - Número da página atual
 * @param {number} pageSize - Tamanho da página
 * @returns {Promise} Promessa com os dados das chamadas
 */
export const obtenerHistoricoLlamadas = async (filters = {}, page = 1, pageSize = 10) => {
  try {
    // Construir parâmetros de query
    const queryParams = new URLSearchParams({
      page,
      page_size: pageSize,
      ...filters
    });

    const response = await fetch(`${API_URL}/llamadas/historico?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Erro ao obter histórico de chamadas');
    }

    return await response.json();
  } catch (error) {
    console.error('Erro ao obter histórico de chamadas:', error);
    throw error;
  }
};

/**
 * Obtém os detalhes de una chamada específica pelo ID
 * @param {number} llamadaId - ID da chamada
 * @returns {Promise} Promessa com os detalhes da chamada
 */
export const obtenerDetalleLlamada = async (llamadaId) => {
  try {
    const response = await fetch(`${API_URL}/llamadas/${llamadaId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Erro ao obter detalhes da chamada');
    }

    return await response.json();
  } catch (error) {
    console.error(`Erro ao obter detalhes da chamada ID ${llamadaId}:`, error);
    throw error;
  }
};

/**
 * Exporta histórico de chamadas filtrado para CSV
 * @param {Object} filters - Objeto com os filtros a aplicar
 * @returns {Promise} Promessa com os dados em formato blob para download
 */
export const exportarHistoricoCSV = async (filters = {}) => {
  try {
    // Construir parâmetros de query
    const queryParams = new URLSearchParams({
      ...filters,
      export: 'csv'
    });

    const response = await fetch(`${API_URL}/llamadas/historico/export?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Erro ao exportar histórico de chamadas');
    }

    return await response.blob();
  } catch (error) {
    console.error('Erro ao exportar histórico para CSV:', error);
    throw error;
  }
}; 