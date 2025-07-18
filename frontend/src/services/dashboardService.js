/**
 * Servicio para datos del dashboard
 */

import { makeApiRequest } from '../config/api.js';

/**
 * Obtiene métricas en tiempo real del dashboard
 * @returns {Promise} Promesa con los datos de las métricas
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
    
    // Retornar estructura vacía en caso de error
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
 * Obtiene datos para gráficos del dashboard
 * @returns {Promise} Promesa con los datos de los gráficos
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
    
    // Retornar estructura vacía en caso de error
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
 * Obtiene estadísticas de campañas activas
 * @returns {Promise} Promesa con los datos de las campañas
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
    
    // Retornar estructura vacía en caso de error
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
 * Obtiene estadísticas de operadores
 * @returns {Promise} Promesa con los datos de los operadores
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
    
    // Retornar estructura vacía en caso de error
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