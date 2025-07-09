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
      wsRef.current = new WebSocket(`${wsUrl}/ws/performance`);
      
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
      
      const response = await fetch('/api/load-test/start', {
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
      const response = await fetch('/api/load-test/stop', {
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
        }
      },
      y: {
        beginAtZero: true
      }
    },
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
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
    <div className="flex items-center space-x-2 mb-4">
      <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
      <span className={`text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
        {isConnected ? 'Conectado' : 'Desconectado'}
      </span>
    </div>
  );

  // Renderizar métricas em tempo real
  const renderRealtimeMetrics = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Cards de métricas */}
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
          <h3 className="text-sm font-medium text-gray-500">CPS Atual</h3>
          <p className="text-2xl font-bold text-blue-600">
            {metrics.realtime?.current_cps?.toFixed(1) || '0.0'}
          </p>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
          <h3 className="text-sm font-medium text-gray-500">Taxa de Sucesso</h3>
          <p className="text-2xl font-bold text-green-600">
            {metrics.realtime?.success_rate ? `${(metrics.realtime.success_rate * 100).toFixed(1)}%` : '0.0%'}
          </p>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-purple-500">
          <h3 className="text-sm font-medium text-gray-500">Chamadas Concorrentes</h3>
          <p className="text-2xl font-bold text-purple-600">
            {metrics.realtime?.concurrent_calls || '0'}
          </p>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-orange-500">
          <h3 className="text-sm font-medium text-gray-500">Carga do Sistema</h3>
          <p className="text-2xl font-bold text-orange-600">
            {metrics.realtime?.system_load?.toFixed(1) || '0.0'}%
          </p>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">CPS em Tempo Real</h3>
          <div className="h-64">
            <Line data={cpsChartData} options={chartOptions} />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Chamadas Concorrentes</h3>
          <div className="h-64">
            <Line data={concurrentCallsData} options={chartOptions} />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Taxa de Sucesso</h3>
          <div className="h-64">
            <Line data={successRateData} options={chartOptions} />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Distribuição por País</h3>
          <div className="h-64">
            <Doughnut data={countryDistributionData} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>
      </div>
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
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Cabeçalho */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dashboard de Performance Avançado
          </h1>
          <p className="text-gray-600">
            Monitoramento em tempo real, testes de carga e análise de performance
          </p>
          {renderConnectionStatus()}
        </div>

        {/* Navegação por abas */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            {[
              { id: 'realtime', label: 'Tempo Real' },
              { id: 'loadtest', label: 'Teste de Carga' },
              { id: 'cli', label: 'CLIs' },
              { id: 'countries', label: 'Países' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  selectedTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Conteúdo das abas */}
        <div className="tab-content">
          {selectedTab === 'realtime' && renderRealtimeMetrics()}
          {selectedTab === 'loadtest' && renderLoadTestSection()}
          {selectedTab === 'cli' && renderCliStats()}
          {selectedTab === 'countries' && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Estatísticas por País</h3>
              <p className="text-gray-500">Implementação em progresso...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedPerformanceDashboard; 