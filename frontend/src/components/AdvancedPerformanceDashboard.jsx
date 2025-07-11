import React, { useState, useEffect, useRef } from 'react';
import { Line, Bar, Doughnut, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// Importar componentes especializados
import LoadTestManager from './LoadTestManager';
import CliLimitsManager from './CliLimitsManager';
import DTMFCountryConfig from './DTMFCountryConfig';
import CliRotationDashboard from './CliRotationDashboard';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
);

const AdvancedPerformanceDashboard = () => {
  const [selectedTab, setSelectedTab] = useState('realtime');
  const [metrics, setMetrics] = useState({
    cps: 0,
    concurrent_calls: 0,
    success_rate: 0,
    answered_calls: 0,
    total_calls: 0,
    active_clis: 0,
    blocked_clis: 0,
    avg_call_duration: 0,
    countries: {},
    timestamp: new Date().toISOString()
  });
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [testRunning, setTestRunning] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [cliStats, setCliStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);

  // Conectar WebSocket para métricas en tiempo real
  useEffect(() => {
    // Não tentar conectar WebSocket no Vercel (produção)
    if (window.location.hostname.includes('vercel.app')) {
      console.log('🚫 WebSocket desabilitado no Vercel');
      setLoading(false);
      return;
    }
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}`;
    wsRef.current = new WebSocket(`${wsUrl}/api/performance/ws/performance`);
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'metrics') {
          setMetrics(data.data);
          
          // Mantener historial en memoria
          setMetricsHistory(prev => {
            const newHistory = [...prev, {
              ...data.data,
              timestamp: new Date().toISOString()
            }];
            
            // Mantener solo los últimos 100 puntos
            return newHistory.slice(-100);
          });
        }
        
        if (data.type === 'test_status') {
          setTestRunning(data.running);
          if (data.results) {
            setTestResults(data.results);
          }
        }
        
        if (data.type === 'cli_stats') {
          setCliStats(data.data);
        }
        
      } catch (err) {
        console.error('Error al procesar WebSocket:', err);
      }
    };
    
    wsRef.current.onopen = () => {
      console.log('🔗 WebSocket conectado');
      setLoading(false);
    };
    
    wsRef.current.onerror = (error) => {
      console.error('❌ Error WebSocket:', error);
      setError('Error de conexión WebSocket');
      setLoading(false);
    };
    
    wsRef.current.onclose = () => {
      console.log('🔌 WebSocket desconectado');
      // Intentar reconectar después de 5 segundos
      setTimeout(() => {
        if (wsRef.current?.readyState === WebSocket.CLOSED) {
          // Reconectar
        }
      }, 5000);
    };
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Mantener historial en memoria
  useEffect(() => {
    if (metrics.timestamp) {
      setMetricsHistory(prev => {
        const newHistory = [...prev, metrics];
        return newHistory.slice(-100); // Mantener solo los últimos 100 puntos
      });
    }
  }, [metrics]);

  // Iniciar test de carga
  const startLoadTest = async () => {
    try {
      setTestRunning(true);
      const response = await fetch('/api/performance/load-test/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_cps: 25,
          duration: 300,
          country: 'all'
        })
      });

      if (!response.ok) {
        throw new Error('Error al iniciar test');
      }

      const result = await response.json();
      console.log('🧪 Test de carga iniciado:', result);
    } catch (error) {
      console.error('❌ Error al iniciar test:', error);
      setTestRunning(false);
    }
  };

  // Parar test de carga
  const stopLoadTest = async () => {
    try {
      const response = await fetch('/api/performance/load-test/stop', {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error('Error al parar test');
      }

      setTestRunning(false);
      console.log('🛑 Test de carga parado');
    } catch (error) {
      console.error('❌ Error al parar test:', error);
    }
  };

  // Configuraciones de gráficos
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'rgba(255, 255, 255, 0.9)',
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'minute',
          displayFormats: {
            minute: 'HH:mm'
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)'
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)'
        }
      }
    }
  };

  // Datos del gráfico CPS en tiempo real
  const cpsChartData = {
    labels: metricsHistory.map(m => new Date(m.timestamp)),
    datasets: [{
      label: 'CPS Actual',
      data: metricsHistory.map(m => m.cps),
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true,
      pointRadius: 2,
      pointHoverRadius: 4
    }]
  };

  // Datos del gráfico de llamadas concurrentes
  const concurrentCallsData = {
    labels: metricsHistory.map(m => new Date(m.timestamp)),
    datasets: [{
      label: 'Llamadas Concurrentes',
      data: metricsHistory.map(m => m.concurrent_calls),
      borderColor: '#10B981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      tension: 0.4,
      fill: true
    }]
  };

  // Datos del gráfico de tasa de éxito
  const successRateData = {
    labels: metricsHistory.map(m => new Date(m.timestamp)),
    datasets: [{
      label: 'Tasa de Éxito (%)',
      data: metricsHistory.map(m => m.success_rate),
      borderColor: '#F59E0B',
      backgroundColor: 'rgba(245, 158, 11, 0.1)',
      tension: 0.4,
      fill: true
    }]
  };

  // Datos del gráfico de distribución por país
  const countryDistributionData = {
    labels: Object.keys(metrics.countries || {}),
    datasets: [{
      label: 'Llamadas por País',
      data: Object.values(metrics.countries || {}),
      backgroundColor: [
        '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
        '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
      ],
      borderWidth: 2,
      borderColor: '#1F2937'
    }]
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num?.toString() || '0';
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0s';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return minutes > 0 ? `${minutes}m ${remainingSeconds}s` : `${remainingSeconds}s`;
  };

  const getStatusColor = (value, thresholds) => {
    if (value >= thresholds.good) return 'text-green-400';
    if (value >= thresholds.warning) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getProgressColor = (value, thresholds) => {
    if (value >= thresholds.good) return 'bg-green-500';
    if (value >= thresholds.warning) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  // Renderizar métricas en tiempo real
  const renderRealtimeMetrics = () => (
    <div className="space-y-6">
      {/* KPIs principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-4 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-secondary-400">CPS Actual</p>
              <p className={`text-2xl font-bold ${getStatusColor(metrics.cps, { good: 20, warning: 10 })}`}>
                {metrics.cps}
              </p>
            </div>
            <div className="text-3xl">📞</div>
          </div>
          <div className="mt-2">
            <div className="w-full bg-secondary-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${getProgressColor(metrics.cps, { good: 20, warning: 10 })}`}
                style={{ width: `${Math.min(metrics.cps * 3.33, 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-secondary-400 mt-1">Meta: 20-30 CPS</p>
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-secondary-400">Llamadas Concurrentes</p>
              <p className="text-2xl font-bold text-blue-400">{metrics.concurrent_calls}</p>
            </div>
            <div className="text-3xl">🔄</div>
          </div>
          <div className="mt-2">
            <div className="w-full bg-secondary-700 rounded-full h-2">
              <div 
                className="h-2 rounded-full bg-blue-500"
                style={{ width: `${Math.min(metrics.concurrent_calls * 2, 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-secondary-400 mt-1">Activas ahora</p>
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-secondary-400">Tasa de Éxito</p>
              <p className={`text-2xl font-bold ${getStatusColor(metrics.success_rate, { good: 80, warning: 60 })}`}>
                {metrics.success_rate}%
              </p>
            </div>
            <div className="text-3xl">✅</div>
          </div>
          <div className="mt-2">
            <div className="w-full bg-secondary-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${getProgressColor(metrics.success_rate, { good: 80, warning: 60 })}`}
                style={{ width: `${metrics.success_rate}%` }}
              ></div>
            </div>
            <p className="text-xs text-secondary-400 mt-1">Objetivo: &gt;80%</p>
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-secondary-400">CLIs Activos</p>
              <p className="text-2xl font-bold text-green-400">{metrics.active_clis}</p>
            </div>
            <div className="text-3xl">📱</div>
          </div>
          <div className="mt-2">
            <div className="flex justify-between text-xs text-secondary-400">
              <span>Bloqueados: {metrics.blocked_clis}</span>
              <span>Total: {metrics.active_clis + metrics.blocked_clis}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos en tiempo real */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de CPS en tiempo real */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold mb-4 text-white">
            Historial de CPS - Tiempo Real
          </h3>
          <div className="h-64">
            <Line data={cpsChartData} options={chartOptions} />
          </div>
        </div>

        {/* Gráfico de llamadas concurrentes */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold mb-4 text-white">
            Llamadas Concurrentes
          </h3>
          <div className="h-64">
            <Line data={concurrentCallsData} options={chartOptions} />
          </div>
        </div>

        {/* Gráfico de tasa de éxito */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold mb-4 text-white">
            Tasa de Éxito
          </h3>
          <div className="h-64">
            <Line data={successRateData} options={chartOptions} />
          </div>
        </div>

        {/* Gráfico de distribución por país */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold mb-4 text-white">
            Distribución por País
          </h3>
          <div className="h-64">
            <Doughnut data={countryDistributionData} options={chartOptions} />
          </div>
        </div>
      </div>
    </div>
  );

  // Renderizar sección de test de carga
  const renderLoadTestSection = () => (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold mb-4">Configuración del Test de Carga</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              CPS Objetivo
            </label>
            <input
              type="number"
              min="1"
              max="50"
              defaultValue="25"
              className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              Duración (minutos)
            </label>
            <input
              type="number"
              min="1"
              max="60"
              defaultValue="5"
              className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              País
            </label>
            <select className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none">
              <option value="all">Todos los países</option>
              <option value="usa">Estados Unidos</option>
              <option value="canada">Canadá</option>
              <option value="mexico">México</option>
              <option value="brasil">Brasil</option>
              <option value="colombia">Colombia</option>
              <option value="argentina">Argentina</option>
            </select>
          </div>
        </div>
        
        <div className="flex space-x-4 mt-6">
          <button
            onClick={startLoadTest}
            disabled={testRunning}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              testRunning 
                ? 'bg-secondary-600 cursor-not-allowed' 
                : 'bg-primary-600 hover:bg-primary-700 text-white'
            }`}
          >
            {testRunning ? 'Test en Curso...' : 'Iniciar Test'}
          </button>
          
          {testRunning && (
            <button
              onClick={stopLoadTest}
              className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-all"
            >
              Parar Test
            </button>
          )}
        </div>
      </div>

      {testResults && (
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold mb-4">Resultados del Test</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">{testResults.avg_cps}</div>
              <div className="text-sm text-secondary-400">CPS Promedio</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">{testResults.max_cps}</div>
              <div className="text-sm text-secondary-400">CPS Máximo</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">{testResults.success_rate}%</div>
              <div className="text-sm text-secondary-400">Tasa de Éxito</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">{formatDuration(testResults.duration)}</div>
              <div className="text-sm text-secondary-400">Duración</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // Renderizar estadísticas de CLIs
  const renderCliStatsSection = () => (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold mb-4">Estadísticas de CLIs</h3>
        {cliStats ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">{cliStats.total_clis}</div>
              <div className="text-sm text-secondary-400">Total CLIs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">{cliStats.active_clis}</div>
              <div className="text-sm text-secondary-400">Activos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">{cliStats.high_usage_clis}</div>
              <div className="text-sm text-secondary-400">Alto Uso</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-400">{cliStats.blocked_clis}</div>
              <div className="text-sm text-secondary-400">Bloqueados</div>
            </div>
          </div>
        ) : (
          <p className="text-gray-500">Cargando estadísticas...</p>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-secondary-400">Conectando al sistema de performance...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-xl">
        <h1 className="text-3xl font-bold text-gradient-primary mb-2">
          Dashboard de Performance
        </h1>
        <p className="text-secondary-400">
          Monitoreo avanzado, tests de carga y gestión de performance
        </p>
      </div>

      {/* Navegación por pestañas */}
      <div className="glass-panel p-4 rounded-xl">
        <div className="flex space-x-2 overflow-x-auto">
          {[
            { id: 'realtime', label: 'Tiempo Real', icon: '📊' },
            { id: 'loadtest', label: 'Tests de Carga', icon: '🧪' },
            { id: 'cli-limits', label: 'Límites CLI', icon: '🔢' },
            { id: 'cli-rotation', label: 'Rotación CLI', icon: '🔄' },
            { id: 'dtmf-config', label: 'Config DTMF', icon: '📞' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
                selectedTab === tab.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-secondary-700 text-secondary-300 hover:bg-secondary-600'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Contenido de las pestañas */}
      <div className="min-h-[500px]">
        {selectedTab === 'realtime' && renderRealtimeMetrics()}
        {selectedTab === 'loadtest' && <LoadTestManager />}
        {selectedTab === 'cli-limits' && <CliLimitsManager />}
        {selectedTab === 'cli-rotation' && <CliRotationDashboard />}
        {selectedTab === 'dtmf-config' && <DTMFCountryConfig />}
      </div>
    </div>
  );
};

export default AdvancedPerformanceDashboard; 