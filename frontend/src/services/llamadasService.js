/**
 * Servicio para interactuar con la API de llamadas
 */

import { makeApiRequest, buildApiUrl } from '../config/api.js';

/**
 * Obtiene todas las llamadas con estado 'en_progreso'
 * @returns {Promise} Promesa con los datos de las llamadas
 */
export const obtenerLlamadasEnProgreso = async () => {
  try {
    const data = await makeApiRequest('/api/v1/llamadas/en-progreso', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    // Unificar formato de respuesta - mapear diferentes formatos de API
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
 * @returns {Promise} Promesa con el resultado de la finalización
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
    
    // Retornar error real
    return { 
      success: false, 
      message: 'Error al finalizar llamada: ' + error.message 
    };
  }
};

/**
 * Obtiene el historial de llamadas con filtros y paginación
 * @param {Object} filters - Objeto con los filtros a aplicar
 * @param {number} page - Número de la página actual
 * @param {number} pageSize - Tamaño de la página
 * @returns {Promise} Promesa con los datos de las llamadas
 */
export const obtenerHistoricoLlamadas = async (filters = {}, page = 1, pageSize = 10) => {
  try {
    // Construir parámetros de query
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

    // Mapear datos del backend real para formato esperado por el frontend
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
    
    // Retornar estructura vacía en caso de error
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
 * Obtiene los detalles de una llamada específica por ID
 * @param {number} llamadaId - ID de la llamada
 * @returns {Promise} Promesa con los detalles de la llamada
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
    
    // Retornar error en caso de falla
    return {
      error: true,
      message: 'Error al obtener detalles de la llamada: ' + error.message
    };
  }
};

/**
 * Exporta historial de llamadas filtrado para CSV
 * @param {Object} filters - Objeto con los filtros a aplicar
 * @returns {Promise} Promesa con los datos en formato blob para descarga
 */
export const exportarHistoricoCSV = async (filters = {}) => {
  try {
    // Construir parámetros de query
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
      throw new Error('Error al exportar historial de llamadas');
    }

    return await response.blob();
  } catch (error) {
    
    // Retornar error en caso de falla
    throw new Error('Error al exportar histórico: ' + error.message);
  }
};