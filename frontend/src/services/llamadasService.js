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
    const data = await makeApiRequest('/llamadas/en-progreso', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    // Mapear dados do backend real para formato esperado pelo frontend
    if (data.llamadas && Array.isArray(data.llamadas)) {
      data.llamadas = data.llamadas.map(llamada => ({
        ...llamada,
        numero_destino: llamada.telefono || llamada.numero_destino, // Converter telefono para numero_destino
        usuario_email: llamada.usuario || llamada.usuario_email || '',
        fecha_asignacion: llamada.fecha_inicio || llamada.fecha_asignacion,
        fecha_finalizacion: llamada.fecha_fin || llamada.fecha_finalizacion,
        operador: llamada.operador || 'Sistema',
        campanha: llamada.campanha || 'Default'
      }));
    }

    return data;
  } catch (error) {
    // Log apenas uma vez que estamos usando dados mock
    if (error.message.includes('Endpoint not implemented')) {
      console.info('ℹ️ Using mock data for llamadas en progreso (backend not available)');
    } else {
      console.error('Error al obtener las llamadas en progreso:', error.message);
    }
    
    // Retornar dados mock em caso de erro
    return {
      llamadas: [
        {
          id: 1,
          numero_destino: '+5411234567890',
          estado: 'conectada',
          duracion: Math.floor(Math.random() * 300) + 60,
          operador: 'Sistema',
          campanha: 'Campanha Demo',
          fecha_asignacion: new Date(Date.now() - Math.random() * 300000).toISOString(),
          usuario_email: 'operador1@discador.com'
        },
        {
          id: 2,
          numero_destino: '+5411987654321',
          estado: 'discando',
          duracion: Math.floor(Math.random() * 30) + 5,
          operador: 'Sistema',
          campanha: 'Campanha Demo',
          fecha_asignacion: new Date(Date.now() - Math.random() * 30000).toISOString(),
          usuario_email: 'operador2@discador.com'
        },
        {
          id: 3,
          numero_destino: '+5411555123456',
          estado: 'en_cola',
          duracion: 0,
          operador: 'Sistema',
          campanha: 'Campanha Test',
          fecha_asignacion: new Date().toISOString(),
          usuario_email: 'sistema@discador.com'
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
    if (error.message.includes('Endpoint not implemented')) {
      console.info(`ℹ️ Mock finalization for llamada ${llamadaId} (backend not available)`);
    } else {
      console.error(`Error al finalizar la llamada ID ${llamadaId}:`, error.message);
    }
    
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

    const data = await makeApiRequest(`/llamadas/historico?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    // Mapear dados do backend real para formato esperado pelo frontend
    if (data.llamadas && Array.isArray(data.llamadas)) {
      data.llamadas = data.llamadas.map(llamada => ({
        ...llamada,
        numero_destino: llamada.telefono || llamada.numero_destino, // Converter telefono para numero_destino
        usuario_email: llamada.usuario || llamada.usuario_email || '',
        fecha_asignacion: llamada.fecha_inicio || llamada.fecha_asignacion,
        fecha_finalizacion: llamada.fecha_fin || llamada.fecha_finalizacion,
        estado: llamada.estado || 'finalizada',
        resultado: llamada.resultado || 'sin_respuesta'
      }));
    }

    return data;
  } catch (error) {
    if (error.message.includes('Endpoint not implemented')) {
      console.info('ℹ️ Using mock data for histórico llamadas (backend not available)');
    } else {
      console.error('Erro ao obter histórico de chamadas:', error.message);
    }
    
    // Retornar dados mock em caso de erro
    const mockHistorico = [];
    for (let i = 0; i < pageSize; i++) {
      const id = (page - 1) * pageSize + i + 1;
      mockHistorico.push({
        id: id,
        numero_destino: `+5411${Math.floor(Math.random() * 900000000) + 100000000}`,
        estado: 'finalizada',
        resultado: ['transferida', 'sin_respuesta', 'ocupado', 'conectada'][Math.floor(Math.random() * 4)],
        usuario_email: ['operador1@discador.com', 'operador2@discador.com', 'sistema@discador.com'][Math.floor(Math.random() * 3)],
        operador: ['Operador 1', 'Operador 2', 'Sistema'][Math.floor(Math.random() * 3)],
        campanha: ['Campanha Demo', 'Campanha Test', 'Seguimiento'][Math.floor(Math.random() * 3)],
        fecha_asignacion: new Date(Date.now() - Math.random() * 86400000).toISOString(),
        fecha_finalizacion: new Date(Date.now() - Math.random() * 43200000).toISOString()
      });
    }

    return {
      llamadas: mockHistorico,
      total: 150, // Simular total para paginação
      page: page,
      page_size: pageSize,
      total_pages: Math.ceil(150 / pageSize)
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
    if (error.message.includes('Endpoint not implemented')) {
      console.info(`ℹ️ Using mock data for llamada ${llamadaId} (backend not available)`);
    } else {
      console.error(`Erro ao obter detalhes da chamada ID ${llamadaId}:`, error.message);
    }
    
    // Retornar dados mock em caso de erro
    return {
      id: llamadaId,
      numero_destino: '+5411234567890',
      estado: 'finalizada',
      duracion: Math.floor(Math.random() * 300) + 60,
      resultado: 'transferida',
      operador: 'Operador 1',
      campanha: 'Campanha Demo',
      fecha_asignacion: new Date(Date.now() - 3600000).toISOString(),
      fecha_finalizacion: new Date().toISOString(),
      usuario_email: 'operador1@discador.com',
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

    const response = await fetch(buildApiUrl(`/llamadas/historico/export?${queryParams}`), {
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
    console.info('ℹ️ Generating mock CSV export (backend not available)');
    
    // Simular CSV em caso de erro
    const csvContent = 'ID,Numero,Estado,Duracion,Resultado,Operador,Campanha,Inicio,Fin\n1,+5411234567890,finalizada,145,transferida,Operador 1,Campanha Demo,2024-01-01T10:00:00Z,2024-01-01T10:02:25Z\n2,+5411987654321,finalizada,89,sin_respuesta,Sistema,Campanha Demo,2024-01-01T11:00:00Z,2024-01-01T11:01:29Z\n';
    return new Blob([csvContent], { type: 'text/csv' });
  }
}; 