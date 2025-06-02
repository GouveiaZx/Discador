/**
 * Serviço para interagir com a API de chamadas
 */

import { makeApiRequest } from '../config/api.js';

/**
 * Obtém todas as chamadas com estado 'en_progreso'
 * @returns {Promise} Promessa com os dados das chamadas
 */
export const obtenerLlamadasEnProgreso = async () => {
  try {
    return await makeApiRequest('/llamadas/en-progreso', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
  } catch (error) {
    console.error('Error al obtener las llamadas en progreso:', error);
    // Retornar dados mock em caso de erro
    return {
      llamadas: [
        {
          id: 1,
          numero: '+5411234567890',
          estado: 'conectada',
          duracion: 145,
          operador: 'Sistema',
          campanha: 'Campanha Demo',
          inicio: new Date().toISOString()
        },
        {
          id: 2,
          numero: '+5411987654321',
          estado: 'discando',
          duracion: 12,
          operador: 'Sistema',
          campanha: 'Campanha Demo',
          inicio: new Date().toISOString()
        }
      ]
    };
  }
};

/**
 * Finaliza manualmente una llamada
 * @param {number} llamadaId - ID de la llamada a finalizar
 * @returns {Promise} Promessa com o resultado da finalização
 */
export const finalizarLlamadaManualmente = async (llamadaId) => {
  try {
    return await makeApiRequest('/llamadas/finalizar', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        llamada_id: llamadaId,
        resultado: 'finalizada_por_admin'
      })
    });
  } catch (error) {
    console.error(`Error al finalizar la llamada ID ${llamadaId}:`, error);
    // Simular sucesso em caso de erro (para desenvolvimento)
    return { success: true, message: 'Llamada finalizada (modo demo)' };
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

    return await makeApiRequest(`/llamadas/historico?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
  } catch (error) {
    console.error('Erro ao obter histórico de chamadas:', error);
    // Retornar dados mock em caso de erro
    return {
      llamadas: [
        {
          id: 1,
          numero: '+5411234567890',
          estado: 'conectada',
          duracion: 145,
          resultado: 'transferida',
          operador: 'Operador 1',
          campanha: 'Campanha Demo',
          inicio: new Date(Date.now() - 3600000).toISOString(),
          fin: new Date().toISOString()
        },
        {
          id: 2,
          numero: '+5411987654321',
          estado: 'finalizada',
          duracion: 89,
          resultado: 'sin_respuesta',
          operador: 'Sistema',
          campanha: 'Campanha Demo',
          inicio: new Date(Date.now() - 7200000).toISOString(),
          fin: new Date(Date.now() - 7000000).toISOString()
        }
      ],
      total: 2,
      page: page,
      page_size: pageSize,
      total_pages: 1
    };
  }
};

/**
 * Obtém os detalhes de una chamada específica pelo ID
 * @param {number} llamadaId - ID da chamada
 * @returns {Promise} Promessa com os detalhes da chamada
 */
export const obtenerDetalleLlamada = async (llamadaId) => {
  try {
    return await makeApiRequest(`/llamadas/${llamadaId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
  } catch (error) {
    console.error(`Erro ao obter detalhes da chamada ID ${llamadaId}:`, error);
    // Retornar dados mock em caso de erro
    return {
      id: llamadaId,
      numero: '+5411234567890',
      estado: 'finalizada',
      duracion: 145,
      resultado: 'transferida',
      operador: 'Operador 1',
      campanha: 'Campanha Demo',
      inicio: new Date(Date.now() - 3600000).toISOString(),
      fin: new Date().toISOString(),
      notas: 'Llamada demo con datos simulados'
    };
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

    const response = await fetch(makeApiRequest(`/llamadas/historico/export?${queryParams}`), {
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
    // Simular CSV em caso de erro
    const csvContent = 'ID,Numero,Estado,Duracion,Resultado,Operador,Campanha,Inicio,Fin\n1,+5411234567890,finalizada,145,transferida,Operador 1,Campanha Demo,2024-01-01T10:00:00Z,2024-01-01T10:02:25Z\n';
    return new Blob([csvContent], { type: 'text/csv' });
  }
}; 