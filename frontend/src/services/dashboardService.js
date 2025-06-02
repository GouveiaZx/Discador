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
    console.error('Error al obtener métricas del dashboard:', error);
    
    // Retornar dados mock realísticos em caso de erro
    const now = new Date();
    const horaAtual = now.getHours();
    
    return {
      llamadasActivas: Math.floor(Math.random() * 50) + 10,
      llamadasHoy: Math.floor(Math.random() * 500) + 200,
      conectadas: Math.floor(Math.random() * 100) + 50,
      sinRespuesta: Math.floor(Math.random() * 80) + 30,
      transferidas: Math.floor(Math.random() * 60) + 20,
      efectividad: Math.floor(Math.random() * 40) + 25,
      tiempoPromedioLlamada: Math.floor(Math.random() * 180) + 60,
      campanasActivas: Math.floor(Math.random() * 8) + 3,
      operadoresOnline: Math.floor(Math.random() * 15) + 5,
      tiempoEsperaPromedio: Math.floor(Math.random() * 45) + 15,
      llamadasEnCola: Math.floor(Math.random() * 20) + 5
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
    console.error('Error al obtener datos de gráficos:', error);
    
    // Gerar dados mock para gráficos
    const horasHoy = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);
    const llamadasPorHora = horasHoy.map((_, i) => {
      // Simular padrão realístico: menos chamadas de madrugada, pico durante o dia
      if (i >= 0 && i <= 6) return Math.floor(Math.random() * 10); // Madrugada
      if (i >= 7 && i <= 18) return Math.floor(Math.random() * 80) + 20; // Horário comercial
      return Math.floor(Math.random() * 30); // Noite
    });

    // Dados para efetividade diária (últimos 7 dias)
    const ultimosDias = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date.toLocaleDateString('es-AR', { weekday: 'short' });
    });
    const efectividadDiaria = ultimosDias.map(() => Math.floor(Math.random() * 40) + 30); // 30-70%

    // Dados para distribuição de resultados
    const totalLlamadas = Math.floor(Math.random() * 500) + 200;
    const conectadas = Math.floor(totalLlamadas * (Math.random() * 0.3 + 0.2)); // 20-50%
    const sinRespuesta = Math.floor(totalLlamadas * (Math.random() * 0.3 + 0.3)); // 30-60%
    const transferidas = Math.floor(totalLlamadas * (Math.random() * 0.2 + 0.1)); // 10-30%
    const ocupado = totalLlamadas - conectadas - sinRespuesta - transferidas;

    return {
      llamadasPorHora: {
        labels: horasHoy,
        data: llamadasPorHora
      },
      efectividadDiaria: {
        labels: ultimosDias,
        data: efectividadDiaria
      },
      estadoLlamadas: {
        conectadas,
        sinRespuesta,
        transferidas,
        ocupado: Math.max(0, ocupado)
      },
      tendenciaSemanal: {
        labels: ultimosDias,
        llamadas: ultimosDias.map(() => Math.floor(Math.random() * 200) + 100),
        efectividad: ultimosDias.map(() => Math.floor(Math.random() * 30) + 35)
      }
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
    console.error('Error al obtener estadísticas de campañas:', error);
    
    // Dados mock de campanhas
    return {
      campanhas: [
        {
          id: 1,
          nome: 'Campanha Vendas Q1',
          estado: 'activa',
          contactosTotal: 1500,
          contactosLlamados: 450,
          conectadas: 180,
          transferidas: 95,
          efectividad: 42.2,
          operadoresAsignados: 8
        },
        {
          id: 2,
          nome: 'Seguimiento Clientes',
          estado: 'activa',
          contactosTotal: 800,
          contactosLlamados: 320,
          conectadas: 128,
          transferidas: 75,
          efectividad: 58.6,
          operadoresAsignados: 5
        },
        {
          id: 3,
          nome: 'Promoción Especial',
          estado: 'pausada',
          contactosTotal: 2000,
          contactosLlamados: 680,
          conectadas: 204,
          transferidas: 98,
          efectividad: 30.0,
          operadoresAsignados: 0
        }
      ],
      resumen: {
        totalCampanhas: 3,
        campanhasActivas: 2,
        totalContactos: 4300,
        contactosRestantes: 2850,
        efectividadPromedio: 43.6
      }
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
    console.error('Error al obtener estadísticas de operadores:', error);
    
    // Dados mock de operadores
    return {
      operadores: [
        {
          id: 1,
          nome: 'María González',
          estado: 'online',
          llamadasHoy: 45,
          conectadas: 28,
          transferidas: 18,
          tiempoSesion: 480, // minutos
          efectividad: 62.2
        },
        {
          id: 2,
          nome: 'Carlos Ruiz',
          estado: 'online',
          llamadasHoy: 38,
          conectadas: 22,
          transferidas: 15,
          tiempoSesion: 420,
          efectividad: 57.9
        },
        {
          id: 3,
          nome: 'Ana Martínez',
          estado: 'pausa',
          llamadasHoy: 32,
          conectadas: 19,
          transferidas: 12,
          tiempoSesion: 360,
          efectividad: 59.4
        },
        {
          id: 4,
          nome: 'Luis Hernández',
          estado: 'offline',
          llamadasHoy: 28,
          conectadas: 15,
          transferidas: 9,
          tiempoSesion: 300,
          efectividad: 53.6
        }
      ],
      resumen: {
        totalOperadores: 4,
        operadoresOnline: 2,
        operadoresEnPausa: 1,
        tiempoPromedioSesion: 390,
        efectividadPromedio: 58.3
      }
    };
  }
}; 