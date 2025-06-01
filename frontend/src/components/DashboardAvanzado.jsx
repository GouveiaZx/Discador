import React, { useState, useEffect, useCallback } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

/**
 * Dashboard avançado com métricas em tempo real
 */
const DashboardAvanzado = () => {
  const [metrics, setMetrics] = useState({
    llamadasActivas: 0,
    llamadasHoy: 0,
    conectadas: 0,
    sinRespuesta: 0,
    transferidas: 0,
    efectividad: 0,
    tiempoPromedioLlamada: 0,
    campanasActivas: 0
  });

  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Dados para gráficos
  const [chartData, setChartData] = useState({
    llamadasPorHora: [],
    efectividadDiaria: [],
    estadoLlamadas: {}
  });

  /**
   * Carregar métricas do backend
   */
  const cargarMetricas = useCallback(async () => {
    setLoading(true);
    try {
      // Simular dados do backend (substituir por API real)
      const mockMetrics = {
        llamadasActivas: Math.floor(Math.random() * 50) + 10,
        llamadasHoy: Math.floor(Math.random() * 500) + 200,
        conectadas: Math.floor(Math.random() * 100) + 50,
        sinRespuesta: Math.floor(Math.random() * 80) + 30,
        transferidas: Math.floor(Math.random() * 60) + 20,
        efectividad: Math.floor(Math.random() * 40) + 25,
        tiempoPromedioLlamada: Math.floor(Math.random() * 180) + 60,
        campanasActivas: Math.floor(Math.random() * 8) + 3
      };

      // Dados para gráfico de linha (chamadas por hora)
      const horasHoy = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);
      const llamadasPorHora = horasHoy.map(() => Math.floor(Math.random() * 50));

      // Dados para gráfico de efetividade diária (últimos 7 dias)
      const ultimosDias = Array.from({ length: 7 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (6 - i));
        return date.toLocaleDateString('es-AR', { weekday: 'short' });
      });
      const efectividadDiaria = ultimosDias.map(() => Math.floor(Math.random() * 60) + 20);

      // Dados para gráfico de rosca (estado das chamadas)
      const estadoLlamadas = {
        conectadas: mockMetrics.conectadas,
        sinRespuesta: mockMetrics.sinRespuesta,
        transferidas: mockMetrics.transferidas,
        ocupado: Math.floor(Math.random() * 40) + 10
      };

      setMetrics(mockMetrics);
      setChartData({
        llamadasPorHora: { labels: horasHoy, data: llamadasPorHora },
        efectividadDiaria: { labels: ultimosDias, data: efectividadDiaria },
        estadoLlamadas
      });
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error al cargar métricas:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Atualização automática a cada 10 segundos
  useEffect(() => {
    cargarMetricas();
    const interval = setInterval(cargarMetricas, 10000);
    return () => clearInterval(interval);
  }, [cargarMetricas]);

  // Configurações dos gráficos
  const lineChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Llamadas por Hora (Hoy)', color: '#fff' }
    },
    scales: {
      y: { beginAtZero: true, ticks: { color: '#9CA3AF' } },
      x: { ticks: { color: '#9CA3AF' } }
    }
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Efectividad Diaria (%)', color: '#fff' }
    },
    scales: {
      y: { beginAtZero: true, max: 100, ticks: { color: '#9CA3AF' } },
      x: { ticks: { color: '#9CA3AF' } }
    }
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'right' },
      title: { display: true, text: 'Estado de Llamadas', color: '#fff' }
    }
  };

  const lineData = {
    labels: chartData.llamadasPorHora.labels || [],
    datasets: [{
      label: 'Llamadas',
      data: chartData.llamadasPorHora.data || [],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }]
  };

  const barData = {
    labels: chartData.efectividadDiaria.labels || [],
    datasets: [{
      label: 'Efectividad %',
      data: chartData.efectividadDiaria.data || [],
      backgroundColor: 'rgba(34, 197, 94, 0.8)',
      borderColor: 'rgb(34, 197, 94)',
      borderWidth: 1
    }]
  };

  const doughnutData = {
    labels: ['Conectadas', 'Sin Respuesta', 'Transferidas', 'Ocupado'],
    datasets: [{
      data: [
        chartData.estadoLlamadas.conectadas || 0,
        chartData.estadoLlamadas.sinRespuesta || 0,
        chartData.estadoLlamadas.transferidas || 0,
        chartData.estadoLlamadas.ocupado || 0
      ],
      backgroundColor: [
        'rgba(34, 197, 94, 0.8)',   // Verde - Conectadas
        'rgba(239, 68, 68, 0.8)',   // Vermelho - Sin Respuesta
        'rgba(59, 130, 246, 0.8)',  // Azul - Transferidas
        'rgba(245, 158, 11, 0.8)'   // Amarelo - Ocupado
      ],
      borderWidth: 2,
      borderColor: '#374151'
    }]
  };

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-white">Dashboard Avanzado</h1>
        <div className="flex items-center space-x-4">
          {loading && (
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
          )}
          {lastUpdated && (
            <span className="text-sm text-gray-400">
              Última actualización: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* KPIs Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {/* Llamadas Activas */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Llamadas Activas</p>
              <p className="text-2xl font-bold text-green-400">{metrics.llamadasActivas}</p>
            </div>
            <div className="bg-green-900 p-3 rounded-full">
              <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Llamadas Hoy */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Llamadas Hoy</p>
              <p className="text-2xl font-bold text-blue-400">{metrics.llamadasHoy}</p>
            </div>
            <div className="bg-blue-900 p-3 rounded-full">
              <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Efectividad */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Efectividad</p>
              <p className="text-2xl font-bold text-yellow-400">{metrics.efectividad}%</p>
            </div>
            <div className="bg-yellow-900 p-3 rounded-full">
              <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Campañas Activas */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Campañas Activas</p>
              <p className="text-2xl font-bold text-purple-400">{metrics.campanasActivas}</p>
            </div>
            <div className="bg-purple-900 p-3 rounded-full">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Gráfico de Línea - Llamadas por Hora */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <Line data={lineData} options={lineChartOptions} />
        </div>

        {/* Gráfico de Rosca - Estado de Llamadas */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <Doughnut data={doughnutData} options={doughnutOptions} />
        </div>
      </div>

      {/* Gráfico de Barras - Efectividad Diaria */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
        <Bar data={barData} options={barChartOptions} />
      </div>

      {/* Métricas Detalhadas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Estadísticas de Llamadas</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Conectadas:</span>
              <span className="text-green-400 font-semibold">{metrics.conectadas}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Sin respuesta:</span>
              <span className="text-red-400 font-semibold">{metrics.sinRespuesta}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Transferidas:</span>
              <span className="text-blue-400 font-semibold">{metrics.transferidas}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Rendimiento</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Tiempo promedio:</span>
              <span className="text-white font-semibold">{Math.floor(metrics.tiempoPromedioLlamada / 60)}:{(metrics.tiempoPromedioLlamada % 60).toString().padStart(2, '0')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Tasa de conexión:</span>
              <span className="text-green-400 font-semibold">{Math.round((metrics.conectadas / metrics.llamadasHoy) * 100)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Tasa de transferencia:</span>
              <span className="text-blue-400 font-semibold">{Math.round((metrics.transferidas / metrics.conectadas) * 100)}%</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Estado del Sistema</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Sistema:</span>
              <span className="flex items-center text-green-400">
                <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                Operativo
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Uptime:</span>
              <span className="text-white font-semibold">99.9%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Calidad de conexión:</span>
              <span className="text-green-400 font-semibold">Excelente</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardAvanzado; 