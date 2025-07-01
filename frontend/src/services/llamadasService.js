/**
 * Serviço para interagir com a API de chamadas
 */

import { makeApiRequest, buildApiUrl } from '../config/api.js';

/**
 * Obtém todas as chamadas com estado 'en_progreso'
 * @returns {Promise} Promessa com os dados das chamadas
 */
export const obtenerLlamadasEnProgreso = async () => {
  try {
    const data = await makeApiRequest('/api/v1/llamadas/en-progreso', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    // Unificar formato de resposta - mapear diferentes formatos de API
    if (data.calls && Array.isArray(data.calls)) {
      data.llamadas = data.calls.map(llamada => ({
        id: llamada.id || Math.random(),
        numero_destino: llamada.phone_number || llamada.numero_destino || llamada.telefono || 'N/A',
        telefono: llamada.phone_number || llamada.numero_destino || llamada.telefono || 'N/A',
        usuario: llamada.usuario || llamada.usuario_email || 'Sistema',
        usuario_email: llamada.usuario || llamada.usuario_email || 'Sistema',
        fecha_asignacion: llamada.start_time || llamada.fecha_asignacion || llamada.startTime || new Date().toISOString(),
        fecha_inicio: llamada.start_time || llamada.startTime || llamada.fecha_asignacion || new Date().toISOString(),
        startTime: llamada.start_time || llamada.startTime || llamada.fecha_asignacion || new Date().toISOString(),
        estado: llamada.status || 'en_progreso',
        campaign_id: llamada.campaign_id || null,
        duration: llamada.duration || '00:00:00'
      }));
    } else if (data.llamadas && Array.isArray(data.llamadas)) {
      data.llamadas = data.llamadas.map(llamada => ({
        ...llamada,
        id: llamada.id || Math.random(),
        telefono: llamada.telefono || llamada.numero_destino || llamada.phone_number || 'N/A',
        numero_destino: llamada.numero_destino || llamada.telefono || llamada.phone_number || 'N/A',
        usuario: llamada.usuario || llamada.usuario_email || 'Sistema',
        usuario_email: llamada.usuario_email || llamada.usuario || 'Sistema',
        startTime: llamada.startTime || llamada.fecha_asignacion || llamada.start_time || new Date().toISOString(),
        fecha_asignacion: llamada.fecha_asignacion || llamada.startTime || llamada.start_time || new Date().toISOString(),
        fecha_inicio: llamada.fecha_inicio || llamada.startTime || llamada.fecha_asignacion || llamada.start_time || new Date().toISOString(),
        estado: llamada.estado || llamada.status || 'en_progreso',
        duration: llamada.duration || '00:00:00'
      }));
    }

    return data;
  } catch (error) {
      console.error('Error al obtener las llamadas en progreso:', error.message);
    
    // Retornar estructura vacía en caso de error
    return {
      llamadas: [],
      total: 0,
      message: 'Error al conectar con el backend: ' + error.message
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
    return await makeApiRequest('/api/v1/llamadas/finalizar', {
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
      console.error(`Error al finalizar la llamada ID ${llamadaId}:`, error.message);
    
    // Retornar erro real
    return { 
      success: false, 
      message: 'Error al finalizar llamada: ' + error.message 
    };
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

    const data = await makeApiRequest(`/api/v1/llamadas/historico?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    // Mapear dados do backend real para formato esperado pelo frontend
    if (data.llamadas && Array.isArray(data.llamadas)) {
      data.llamadas = data.llamadas.map(llamada => ({
        ...llamada,
        numero_destino: llamada.telefono || llamada.numero_destino,
        usuario_email: llamada.usuario || llamada.usuario_email || '',
        fecha_asignacion: llamada.fecha_inicio || llamada.fecha_asignacion,
        fecha_finalizacion: llamada.fecha_fin || llamada.fecha_finalizacion,
        estado: llamada.estado || 'finalizada',
        resultado: llamada.resultado || 'sin_respuesta'
      }));
    }

    return data;
  } catch (error) {
      console.error('Erro ao obter histórico de chamadas:', error.message);
    
    // Retornar estrutura vazia em caso de erro
    return {
      llamadas: [],
      total: 0,
      page: page,
      page_size: pageSize,
      total_pages: 0,
      message: 'Error al conectar con el backend: ' + error.message
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
    return await makeApiRequest(`/api/v1/llamadas/${llamadaId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
  } catch (error) {
      console.error(`Erro ao obter detalhes da chamada ID ${llamadaId}:`, error.message);
    
    // Retornar erro em caso de falha
    return {
      error: true,
      message: 'Error al obtener detalles de la llamada: ' + error.message
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

    const response = await fetch(buildApiUrl(`/api/v1/llamadas/historico/export?${queryParams}`), {
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
    console.error('Error al exportar histórico CSV:', error.message);
    
    // Retornar erro em caso de falha
    throw new Error('Error al exportar histórico: ' + error.message);
  }
}; 