/**
 * Serviço para dados do dashboard
 */

import { makeApiRequest } from '../config/api.js';

/**
 * Obtém métricas em tempo real do dashboard
 * @returns {Promise} Promessa com os dados das métricas
 */
export const obtenerMetricasDashboard = async () => {
  try {
    return await makeApiRequest('/dashboard/metrics', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
  } catch (error) {
      console.error('Error al obtener métricas del dashboard:', error.message);
    
    // Retornar estrutura vazia em caso de erro
    return {
      llamadasActivas: 0,
      llamadasHoy: 0,
      conectadas: 0,
      sinRespuesta: 0,
      transferidas: 0,
      efectividad: 0,
      tiempoPromedioLlamada: 0,
      campanasActivas: 0,
      operadoresOnline: 0,
      tiempoEsperaPromedio: 0,
      llamadasEnCola: 0,
      error: true,
      message: 'Error al conectar con el backend: ' + error.message
    };
  }
};

/**
 * Obtém dados para gráficos do dashboard
 * @returns {Promise} Promessa com os dados dos gráficos
 */
export const obtenerDatosGraficos = async () => {
  try {
    return await makeApiRequest('/dashboard/charts', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
  } catch (error) {
      console.error('Error al obtener datos de gráficos:', error.message);
    
    // Retornar estrutura vazia em caso de erro
    return {
      llamadasPorHora: {
        labels: [],
        data: []
      },
      efectividadDiaria: {
        labels: [],
        data: []
      },
      estadoLlamadas: {
        conectadas: 0,
        sinRespuesta: 0,
        transferidas: 0,
        ocupado: 0
      },
      tendenciaSemanal: {
        labels: [],
        llamadas: [],
        efectividad: []
      },
      error: true,
      message: 'Error al conectar con el backend: ' + error.message
    };
  }
};

/**
 * Obtém estatísticas de campanhas ativas
 * @returns {Promise} Promessa com os dados das campanhas
 */
export const obtenerEstatisticasCampanhas = async () => {
  try {
    return await makeApiRequest('/dashboard/campaigns', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
  } catch (error) {
      console.error('Error al obtener estadísticas de campañas:', error.message);
    
    // Retornar estrutura vazia em caso de erro
    return {
      campanhas: [],
      resumen: {
        totalCampanhas: 0,
        campanhasActivas: 0,
        totalContactos: 0,
        contactosRestantes: 0,
        efectividadPromedio: 0
      },
      error: true,
      message: 'Error al conectar con el backend: ' + error.message
    };
  }
};

/**
 * Obtém estatísticas de operadores
 * @returns {Promise} Promessa com os dados dos operadores
 */
export const obtenerEstatisticasOperadores = async () => {
  try {
    return await makeApiRequest('/dashboard/operators', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
  } catch (error) {
      console.error('Error al obtener estadísticas de operadores:', error.message);
    
    // Retornar estrutura vazia em caso de erro
    return {
      operadores: [],
      resumen: {
        totalOperadores: 0,
        operadoresOnline: 0,
        operadoresEnPausa: 0,
        tiempoPromedioSesion: 0,
        efectividadPromedio: 0
      },
      error: true,
      message: 'Error al conectar con el backend: ' + error.message
    };
  }
}; 