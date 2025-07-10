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
  TimeScale
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
  TimeScale
);

const AdvancedPerformanceDashboard = () => {
  const [metrics, setMetrics] = useState({
    realtime: null,
    history: [],
    loadTest: null,
    cliStats: null,
    countryStats: null
  });
  
  const [isConnected, setIsConnected] = useState(false);
  const [selectedTab, setSelectedTab] = useState('realtime');
  const [testRunning, setTestRunning] = useState(false);
  const [testConfig, setTestConfig] = useState({
    target_cps: 25,
    duration_minutes: 10,
    countries: ['usa', 'mexico', 'brasil', 'colombia']
  });
  
  const wsRef = useRef(null);
  const metricsHistoryRef = useRef([]);

  // Conectar WebSocket para métricas em tempo real
  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
      wsRef.current = new WebSocket(`${wsUrl}/api/performance/ws/performance`);
      
      wsRef.current.onopen = () => {
        setIsConnected(true);
        console.log('✅ WebSocket conectado');
      };
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMetricsUpdate(data);
      };
      
      wsRef.current.onclose = () => {
        setIsConnected(false);
        console.log('🔌 WebSocket desconectado');
        // Reconectar após 3 segundos
        setTimeout(connectWebSocket, 3000);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('❌ Erro no WebSocket:', error);
      };
    };
    
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Atualizar métricas recebidas via WebSocket
  const handleMetricsUpdate = (data) => {
    setMetrics(prev => ({
      ...prev,
      realtime: data.realtime,
      history: data.history || prev.history,
      cliStats: data.cli_stats || prev.cliStats,
      countryStats: data.country_stats || prev.countryStats
    }));
    
    // Manter histórico em memória
    if (data.realtime) {
      metricsHistoryRef.current.push({
        ...data.realtime,
        timestamp: new Date()
      });
      
      // Manter apenas últimos 1000 pontos
      if (metricsHistoryRef.current.length > 1000) {
        metricsHistoryRef.current.shift();
      }
    }
  };

  // Iniciar teste de carga
  const startLoadTest = async () => {
    try {
      setTestRunning(true);
      
      const response = await fetch('/api/performance/load-test/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testConfig)
      });
      
      if (!response.ok) {
        throw new Error('Erro ao iniciar teste');
      }
      
      const result = await response.json();
      console.log('🧪 Teste de carga iniciado:', result);
      
    } catch (error) {
      console.error('❌ Erro ao iniciar teste:', error);
      setTestRunning(false);
    }
  };

  // Parar teste de carga
  const stopLoadTest = async () => {
    try {
      const response = await fetch('/api/performance/load-test/stop', {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Erro ao parar teste');
      }
      
      setTestRunning(false);
      console.log('🛑 Teste de carga parado');
      
    } catch (error) {
      console.error('❌ Erro ao parar teste:', error);
    }
  };

  // Configurações de gráficos
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
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
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'rgba(255, 255, 255, 0.8)'
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1
      }
    }
  };

  // Dados do gráfico CPS em tempo real
  const cpsChartData = {
    labels: metricsHistoryRef.current.map(m => m.timestamp),
    datasets: [
      {
        label: 'CPS Atual',
        data: metricsHistoryRef.current.map(m => m.current_cps),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      },
      {
        label: 'CPS Alvo',
        data: metricsHistoryRef.current.map(m => m.target_cps),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderDash: [5, 5]
      }
    ]
  };

  // Dados do gráfico de chamadas concorrentes
  const concurrentCallsData = {
    labels: metricsHistoryRef.current.map(m => m.timestamp),
    datasets: [
      {
        label: 'Chamadas Concorrentes',
        data: metricsHistoryRef.current.map(m => m.concurrent_calls),
        borderColor: 'rgb(153, 102, 255)',
        backgroundColor: 'rgba(153, 102, 255, 0.2)',
        tension: 0.1
      }
    ]
  };

  // Dados do gráfico de taxa de sucesso
  const successRateData = {
    labels: metricsHistoryRef.current.map(m => m.timestamp),
    datasets: [
      {
        label: 'Taxa de Sucesso (%)',
        data: metricsHistoryRef.current.map(m => m.success_rate * 100),
        borderColor: 'rgb(255, 206, 86)',
        backgroundColor: 'rgba(255, 206, 86, 0.2)',
        tension: 0.1
      }
    ]
  };

  // Dados do gráfico de distribuição por país
  const countryDistributionData = {
    labels: metrics.countryStats ? Object.keys(metrics.countryStats) : [],
    datasets: [
      {
        label: 'Chamadas por País',
        data: metrics.countryStats ? Object.values(metrics.countryStats).map(c => c.calls_attempted) : [],
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)'
        ],
        borderWidth: 1
      }
    ]
  };

  // Renderizar status de conexão
  const renderConnectionStatus = () => (
    <div className="mb-4">
      <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
        isConnected 
          ? 'bg-green-100 text-green-800' 
          : 'bg-red-100 text-red-800'
      }`}>
        <div className={`w-2 h-2 rounded-full mr-2 ${
          isConnected ? 'bg-green-600' : 'bg-red-600'
        }`} />
        {isConnected ? 'Conectado' : 'Desconectado'}
      </div>
    </div>
  );

  // Renderizar métricas em tempo real
  const renderRealtimeMetrics = () => (
    <div className="space-y-6">
      {/* KPIs principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-panel p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-secondary-400">CPS Atual</p>
              <p className="text-2xl font-bold text-gradient-primary">
                {metrics.realtime?.current_cps?.toFixed(1) || '0.0'}
              </p>
            </div>
            <div className="w-12 h-12 bg-primary-500/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-secondary-400">Chamadas Ativas</p>
              <p className="text-2xl font-bold text-gradient-primary">
                {metrics.realtime?.active_calls || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-accent-500/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-secondary-400">Taxa de Sucesso</p>
              <p className="text-2xl font-bold text-gradient-primary">
                {metrics.realtime?.success_rate?.toFixed(1) || '0.0'}%
              </p>
            </div>
            <div className="w-12 h-12 bg-success-500/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-secondary-400">CLIs Ativos</p>
              <p className="text-2xl font-bold text-gradient-primary">
                {metrics.realtime?.active_clis || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-warning-500/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-warning-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Gráfico de CPS em tempo real */}
      {metricsHistoryRef.current.length > 0 && (
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">
            Histórico de CPS - Tempo Real
          </h3>
          <div className="h-80">
            <Line
              data={{
                labels: metricsHistoryRef.current.map(m => m.timestamp),
                datasets: [
                  {
                    label: 'CPS Atual',
                    data: metricsHistoryRef.current.map(m => m.current_cps),
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    tension: 0.4,
                    fill: true
                  },
                  {
                    label: 'CPS Alvo',
                    data: metricsHistoryRef.current.map(m => m.target_cps),
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    borderDash: [5, 5]
                  }
                ]
              }}
              options={chartOptions}
            />
          </div>
        </div>
      )}
    </div>
  );

  // Renderizar seção de teste de carga
  const renderLoadTestSection = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Configuração do Teste de Carga</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">CPS Alvo</label>
            <input
              type="number"
              value={testConfig.target_cps}
              onChange={(e) => setTestConfig(prev => ({ ...prev, target_cps: parseInt(e.target.value) }))}
              className="w-full p-2 border border-gray-300 rounded-md"
              min="1"
              max="50"
              disabled={testRunning}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Duração (minutos)</label>
            <input
              type="number"
              value={testConfig.duration_minutes}
              onChange={(e) => setTestConfig(prev => ({ ...prev, duration_minutes: parseInt(e.target.value) }))}
              className="w-full p-2 border border-gray-300 rounded-md"
              min="1"
              max="60"
              disabled={testRunning}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Países</label>
            <select
              multiple
              value={testConfig.countries}
              onChange={(e) => setTestConfig(prev => ({ 
                ...prev, 
                countries: Array.from(e.target.selectedOptions, option => option.value)
              }))}
              className="w-full p-2 border border-gray-300 rounded-md"
              disabled={testRunning}
            >
              <option value="usa">USA</option>
              <option value="canada">Canadá</option>
              <option value="mexico">México</option>
              <option value="brasil">Brasil</option>
              <option value="colombia">Colômbia</option>
              <option value="argentina">Argentina</option>
            </select>
          </div>
        </div>
        
        <div className="flex space-x-4">
          <button
            onClick={startLoadTest}
            disabled={testRunning}
            className={`px-4 py-2 rounded-md font-medium ${
              testRunning 
                ? 'bg-gray-300 cursor-not-allowed' 
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {testRunning ? 'Teste em Andamento...' : 'Iniciar Teste'}
          </button>
          
          <button
            onClick={stopLoadTest}
            disabled={!testRunning}
            className={`px-4 py-2 rounded-md font-medium ${
              !testRunning 
                ? 'bg-gray-300 cursor-not-allowed' 
                : 'bg-red-500 hover:bg-red-600 text-white'
            }`}
          >
            Parar Teste
          </button>
        </div>
      </div>
      
      {metrics.loadTest && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Resultados do Teste</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {metrics.loadTest.total_calls_attempted || 0}
              </p>
              <p className="text-sm text-gray-500">Chamadas Tentadas</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {metrics.loadTest.total_calls_successful || 0}
              </p>
              <p className="text-sm text-gray-500">Bem-sucedidas</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {metrics.loadTest.total_calls_failed || 0}
              </p>
              <p className="text-sm text-gray-500">Falhadas</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {metrics.loadTest.actual_cps?.toFixed(1) || '0.0'}
              </p>
              <p className="text-sm text-gray-500">CPS Alcançado</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // Renderizar estatísticas de CLIs
  const renderCliStats = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Estatísticas de CLIs</h3>
        
        {metrics.cliStats ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">
                  {metrics.cliStats.total_clis || 0}
                </p>
                <p className="text-sm text-gray-500">CLIs Disponíveis</p>
              </div>
              
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {metrics.cliStats.active_clis || 0}
                </p>
                <p className="text-sm text-gray-500">CLIs Ativos</p>
              </div>
              
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-600">
                  {metrics.cliStats.average_usage?.toFixed(1) || '0.0'}
                </p>
                <p className="text-sm text-gray-500">Uso Médio</p>
              </div>
            </div>
            
            {metrics.cliStats.top_used && (
              <div>
                <h4 className="font-semibold mb-2">CLIs Mais Usados</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          CLI
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Uso Hoje
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Limite
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {metrics.cliStats.top_used.map((cli, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {cli.cli}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {cli.usage}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {cli.limit === 0 ? 'Ilimitado' : cli.limit}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              cli.status === 'available' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {cli.status === 'available' ? 'Disponível' : 'Bloqueado'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500">Carregando estatísticas...</p>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-100 to-secondary-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Cabeçalho */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gradient-primary mb-2">
                Performance Dashboard
              </h1>
              <p className="text-secondary-400 text-lg">
                Monitoramento avançado, testes de carga e gestão de performance
              </p>
            </div>
            {renderConnectionStatus()}
          </div>
        </div>

        {/* Navegação por abas */}
        <div className="mb-8">
          <nav className="flex space-x-1 glass-panel rounded-xl p-1">
            {[
              { id: 'realtime', label: 'Tempo Real', icon: '📊' },
              { id: 'loadtest', label: 'Testes de Carga', icon: '🧪' },
              { id: 'cli-limits', label: 'Limites CLI', icon: '🔢' },
              { id: 'cli-rotation', label: 'Rotação CLI', icon: '🔄' },
              { id: 'dtmf-config', label: 'Config DTMF', icon: '⌨️' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                  selectedTab === tab.id
                    ? 'bg-primary-500 text-white shadow-lg'
                    : 'text-secondary-400 hover:text-white hover:bg-white/10'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Conteúdo das abas */}
        <div className="tab-content">
          {selectedTab === 'realtime' && renderRealtimeMetrics()}
          {selectedTab === 'loadtest' && <LoadTestManager />}
          {selectedTab === 'cli-limits' && <CliLimitsManager />}
          {selectedTab === 'cli-rotation' && <CliRotationDashboard />}
          {selectedTab === 'dtmf-config' && <DTMFCountryConfig />}
        </div>
      </div>
    </div>
  );
};

export default AdvancedPerformanceDashboard; 