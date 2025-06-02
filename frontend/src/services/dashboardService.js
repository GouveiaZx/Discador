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
    if (error.message.includes('Endpoint not implemented')) {
      console.info('ℹ️ Using mock data for dashboard metrics (backend not available)');
    } else {
      console.error('Error al obtener métricas del dashboard:', error.message);
    }
    
    // Retornar dados mock realísticos em caso de erro
    const now = new Date();
    const horaAtual = now.getHours();
    
    // Simular padrões realísticos baseados na hora
    const isBusinessHour = horaAtual >= 8 && horaAtual <= 18;
    const baseMultiplier = isBusinessHour ? 1.5 : 0.5;
    
    return {
      llamadasActivas: Math.floor((Math.random() * 30 + 10) * baseMultiplier),
      llamadasHoy: Math.floor((Math.random() * 300 + 200) * baseMultiplier),
      conectadas: Math.floor((Math.random() * 80 + 40) * baseMultiplier),
      sinRespuesta: Math.floor((Math.random() * 60 + 30) * baseMultiplier),
      transferidas: Math.floor((Math.random() * 40 + 20) * baseMultiplier),
      efectividad: Math.floor(Math.random() * 30) + 35, // 35-65%
      tiempoPromedioLlamada: Math.floor(Math.random() * 120) + 90, // 1.5-3.5 min
      campanasActivas: Math.floor(Math.random() * 5) + 2,
      operadoresOnline: Math.floor((Math.random() * 10 + 5) * baseMultiplier),
      tiempoEsperaPromedio: Math.floor(Math.random() * 30) + 15,
      llamadasEnCola: Math.floor((Math.random() * 15 + 5) * baseMultiplier)
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
    if (error.message.includes('Endpoint not implemented')) {
      console.info('ℹ️ Using mock chart data (backend not available)');
    } else {
      console.error('Error al obtener datos de gráficos:', error.message);
    }
    
    // Gerar dados mock para gráficos
    const horasHoy = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);
    const llamadasPorHora = horasHoy.map((_, i) => {
      // Simular padrão realístico: menos chamadas de madrugada, pico durante o dia
      if (i >= 0 && i <= 6) return Math.floor(Math.random() * 10); // Madrugada
      if (i >= 7 && i <= 18) return Math.floor(Math.random() * 60) + 30; // Horário comercial
      return Math.floor(Math.random() * 25) + 5; // Noite
    });

    // Dados para efetividade diária (últimos 7 dias)
    const ultimosDias = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date.toLocaleDateString('pt-BR', { weekday: 'short' });
    });
    const efectividadDiaria = ultimosDias.map(() => Math.floor(Math.random() * 35) + 30); // 30-65%

    // Dados para distribuição de resultados
    const totalLlamadas = Math.floor(Math.random() * 400) + 200;
    const conectadas = Math.floor(totalLlamadas * (Math.random() * 0.25 + 0.25)); // 25-50%
    const sinRespuesta = Math.floor(totalLlamadas * (Math.random() * 0.25 + 0.30)); // 30-55%
    const transferidas = Math.floor(totalLlamadas * (Math.random() * 0.15 + 0.10)); // 10-25%
    const ocupado = Math.max(0, totalLlamadas - conectadas - sinRespuesta - transferidas);

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
        ocupado
      },
      tendenciaSemanal: {
        labels: ultimosDias,
        llamadas: ultimosDias.map(() => Math.floor(Math.random() * 150) + 100),
        efectividad: ultimosDias.map(() => Math.floor(Math.random() * 25) + 40)
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
    if (error.message.includes('Endpoint not implemented')) {
      console.info('ℹ️ Using mock campaign data (backend not available)');
    } else {
      console.error('Error al obtener estadísticas de campañas:', error.message);
    }
    
    // Dados mock de campanhas com variação
    const campanhas = [
      {
        id: 1,
        nome: 'Campanha Vendas Q1',
        estado: 'activa',
        contactosTotal: 1500,
        contactosLlamados: Math.floor(Math.random() * 500) + 400,
        conectadas: Math.floor(Math.random() * 150) + 120,
        transferidas: Math.floor(Math.random() * 80) + 60,
        efectividad: Math.floor(Math.random() * 20) + 35,
        operadoresAsignados: 8
      },
      {
        id: 2,
        nome: 'Seguimiento Clientes',
        estado: 'activa',
        contactosTotal: 800,
        contactosLlamados: Math.floor(Math.random() * 300) + 250,
        conectadas: Math.floor(Math.random() * 100) + 80,
        transferidas: Math.floor(Math.random() * 60) + 40,
        efectividad: Math.floor(Math.random() * 25) + 45,
        operadoresAsignados: 5
      },
      {
        id: 3,
        nome: 'Promoción Especial',
        estado: Math.random() > 0.5 ? 'activa' : 'pausada',
        contactosTotal: 2000,
        contactosLlamados: Math.floor(Math.random() * 800) + 600,
        conectadas: Math.floor(Math.random() * 200) + 150,
        transferidas: Math.floor(Math.random() * 100) + 70,
        efectividad: Math.floor(Math.random() * 15) + 25,
        operadoresAsignados: Math.random() > 0.5 ? 6 : 0
      }
    ];

    const totalContactos = campanhas.reduce((sum, c) => sum + c.contactosTotal, 0);
    const contactosLlamados = campanhas.reduce((sum, c) => sum + c.contactosLlamados, 0);
    const efectividadPromedio = campanhas.reduce((sum, c) => sum + c.efectividad, 0) / campanhas.length;

    return {
      campanhas,
      resumen: {
        totalCampanhas: campanhas.length,
        campanhasActivas: campanhas.filter(c => c.estado === 'activa').length,
        totalContactos,
        contactosRestantes: totalContactos - contactosLlamados,
        efectividadPromedio: Math.round(efectividadPromedio * 10) / 10
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
    if (error.message.includes('Endpoint not implemented')) {
      console.info('ℹ️ Using mock operator data (backend not available)');
    } else {
      console.error('Error al obtener estadísticas de operadores:', error.message);
    }
    
    // Dados mock de operadores com variação
    const estados = ['online', 'pausa', 'offline'];
    const nombres = ['María González', 'Carlos Ruiz', 'Ana Martínez', 'Luis Hernández', 'Sofia Ramirez', 'Pedro López'];
    
    const operadores = nombres.map((nome, index) => {
      const estado = estados[Math.floor(Math.random() * estados.length)];
      const llamadasHoy = estado === 'offline' ? Math.floor(Math.random() * 20) + 10 : Math.floor(Math.random() * 30) + 25;
      const conectadas = Math.floor(llamadasHoy * (Math.random() * 0.4 + 0.4)); // 40-80%
      const transferidas = Math.floor(conectadas * (Math.random() * 0.4 + 0.3)); // 30-70% das conectadas
      
      return {
        id: index + 1,
        nome,
        estado,
        llamadasHoy,
        conectadas,
        transferidas,
        tiempoSesion: estado === 'offline' ? Math.floor(Math.random() * 300) + 200 : Math.floor(Math.random() * 300) + 300,
        efectividad: Math.round((conectadas / llamadasHoy) * 100 * 10) / 10
      };
    });

    const operadoresOnline = operadores.filter(o => o.estado === 'online').length;
    const operadoresEnPausa = operadores.filter(o => o.estado === 'pausa').length;
    const tiempoPromedioSesion = Math.round(operadores.reduce((sum, o) => sum + o.tiempoSesion, 0) / operadores.length);
    const efectividadPromedio = Math.round(operadores.reduce((sum, o) => sum + o.efectividad, 0) / operadores.length * 10) / 10;

    return {
      operadores,
      resumen: {
        totalOperadores: operadores.length,
        operadoresOnline,
        operadoresEnPausa,
        tiempoPromedioSesion,
        efectividadPromedio
      }
    };
  }
}; 