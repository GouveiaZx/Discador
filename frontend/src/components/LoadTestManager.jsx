import React, { useState, useEffect, useRef } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
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
import performanceService from '../services/performanceService';

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

const LoadTestManager = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [testStatus, setTestStatus] = useState(null);
  const [testResults, setTestResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [realTimeData, setRealTimeData] = useState([]);
  
  const [testConfig, setTestConfig] = useState({
    target_cps: 25,
    duration_minutes: 10,
    countries_to_test: ['usa', 'mexico', 'brasil', 'colombia'],
    number_of_clis: 1000
  });

  const pollIntervalRef = useRef(null);
  const maxDataPoints = 100;

  const countries = {
    usa: { name: 'Estados Unidos', flag: '🇺🇸' },
    canada: { name: 'Canadá', flag: '🇨🇦' },
    mexico: { name: 'México', flag: '🇲🇽' },
    brasil: { name: 'Brasil', flag: '🇧🇷' },
    colombia: { name: 'Colômbia', flag: '🇨🇴' },
    argentina: { name: 'Argentina', flag: '🇦🇷' },
    chile: { name: 'Chile', flag: '🇨🇱' },
    peru: { name: 'Peru', flag: '🇵🇪' }
  };

  useEffect(() => {
    checkTestStatus();
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const checkTestStatus = async () => {
    try {
      const status = await performanceService.getLoadTestStatus();
      setTestStatus(status);
      setIsRunning(status.is_running || false);
      
      if (status.is_running) {
        startPolling();
      }
    } catch (err) {
      console.error('❌ Erro ao verificar status do teste:', err);
    }
  };

  const startPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }
    
    pollIntervalRef.current = setInterval(async () => {
      try {
        const status = await performanceService.getLoadTestStatus();
        setTestStatus(status);
        
        if (status.is_running) {
          // Adicionar dados em tempo real
          const newDataPoint = {
            timestamp: new Date(),
            cps: status.current_cps || 0,
            concurrent_calls: status.concurrent_calls || 0,
            success_rate: status.success_rate || 0,
            errors: status.errors || 0
          };
          
          setRealTimeData(prev => {
            const updated = [...prev, newDataPoint];
            return updated.slice(-maxDataPoints);
          });
        } else {
          setIsRunning(false);
          clearInterval(pollIntervalRef.current);
          loadTestResults();
        }
      } catch (err) {
        console.error('❌ Erro ao obter status:', err);
      }
    }, 2000);
  };

  const loadTestResults = async () => {
    try {
      const results = await performanceService.getLoadTestResults();
      setTestResults(results);
    } catch (err) {
      console.error('❌ Erro ao carregar resultados:', err);
    }
  };

  const handleStartTest = async () => {
    // Validar configuração
    const validationErrors = performanceService.validateLoadTestConfig(testConfig);
    if (validationErrors.length > 0) {
      setError(validationErrors.join(', '));
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setRealTimeData([]);
      
      await performanceService.startLoadTest(testConfig);
      setSuccessMessage('Teste de carga iniciado com sucesso!');
      setIsRunning(true);
      startPolling();
      
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('❌ Erro ao iniciar teste:', err);
      setError('Erro ao iniciar teste de carga. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleStopTest = async () => {
    try {
      setLoading(true);
      await performanceService.stopLoadTest();
      setIsRunning(false);
      setSuccessMessage('Teste de carga interrompido!');
      
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
      
      setTimeout(() => {
        setSuccessMessage('');
        loadTestResults();
      }, 2000);
    } catch (err) {
      console.error('❌ Erro ao parar teste:', err);
      setError('Erro ao parar teste de carga.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportResults = async (format) => {
    try {
      const results = await performanceService.getLoadTestResults(format);
      
      if (format === 'json') {
        const dataStr = JSON.stringify(results, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        const exportFileDefaultName = `load_test_results_${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
      } else {
        // Para CSV/Excel, assumir que o backend retorna o arquivo
        const blob = new Blob([results], { type: 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `load_test_results_${new Date().toISOString().split('T')[0]}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
      
      setSuccessMessage(`Resultados exportados em ${format.toUpperCase()}`);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('❌ Erro ao exportar resultados:', err);
      setError('Erro ao exportar resultados.');
    }
  };

  const getChartData = () => {
    if (!realTimeData.length) return { labels: [], datasets: [] };

    return {
      labels: realTimeData.map(d => d.timestamp.toLocaleTimeString()),
      datasets: [
        {
          label: 'CPS Atual',
          data: realTimeData.map(d => d.cps),
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true
        },
        {
          label: 'Chamadas Simultâneas',
          data: realTimeData.map(d => d.concurrent_calls),
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true
        }
      ]
    };
  };

  const getSuccessRateData = () => {
    if (!realTimeData.length) return { labels: [], datasets: [] };

    return {
      labels: realTimeData.map(d => d.timestamp.toLocaleTimeString()),
      datasets: [
        {
          label: 'Taxa de Sucesso (%)',
          data: realTimeData.map(d => d.success_rate * 100),
          borderColor: '#F59E0B',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { color: 'rgba(255, 255, 255, 0.7)' }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { color: 'rgba(255, 255, 255, 0.7)' }
      }
    },
    plugins: {
      legend: {
        labels: { color: 'rgba(255, 255, 255, 0.9)' }
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-2">
          🧪 Teste de Carga - Alta Performance
        </h2>
        <p className="text-green-100">
          Teste o sistema com 20-30 CPS para validar comportamento sob alta carga
        </p>
      </div>

      {/* Mensagens de Status */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z"/>
            </svg>
            <span className="text-red-400">{error}</span>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span className="text-green-400">{successMessage}</span>
          </div>
        </div>
      )}

      {/* Status do Teste */}
      {testStatus && (
        <div className="glass-panel rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Status do Teste</h3>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              isRunning ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
            }`}>
              {isRunning ? '🟢 Executando' : '🔴 Parado'}
            </div>
          </div>
          
          {isRunning && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">
                  {testStatus.current_cps || 0}
                </div>
                <div className="text-sm text-secondary-400">CPS Atual</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">
                  {testStatus.concurrent_calls || 0}
                </div>
                <div className="text-sm text-secondary-400">Chamadas Ativas</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-400">
                  {((testStatus.success_rate || 0) * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-secondary-400">Taxa de Sucesso</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-400">
                  {testStatus.errors || 0}
                </div>
                <div className="text-sm text-secondary-400">Erros</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Configuração do Teste */}
      <div className="glass-panel rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          ⚙️ Configuração do Teste
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              CPS Alvo
            </label>
            <input
              type="number"
              value={testConfig.target_cps}
              onChange={(e) => setTestConfig({...testConfig, target_cps: parseFloat(e.target.value)})}
              min="1"
              max="50"
              step="0.1"
              disabled={isRunning}
              className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              Duração (minutos)
            </label>
            <input
              type="number"
              value={testConfig.duration_minutes}
              onChange={(e) => setTestConfig({...testConfig, duration_minutes: parseInt(e.target.value)})}
              min="1"
              max="120"
              disabled={isRunning}
              className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              Número de CLIs
            </label>
            <input
              type="number"
              value={testConfig.number_of_clis}
              onChange={(e) => setTestConfig({...testConfig, number_of_clis: parseInt(e.target.value)})}
              min="10"
              max="50000"
              step="10"
              disabled={isRunning}
              className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
            />
          </div>

          <div className="flex items-end">
            {!isRunning ? (
              <button
                onClick={handleStartTest}
                disabled={loading}
                className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              >
                {loading ? 'Iniciando...' : '▶️ Iniciar Teste'}
              </button>
            ) : (
              <button
                onClick={handleStopTest}
                disabled={loading}
                className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              >
                {loading ? 'Parando...' : '⏹️ Parar Teste'}
              </button>
            )}
          </div>
        </div>

        {/* Seleção de Países */}
        <div>
          <label className="block text-sm font-medium text-secondary-300 mb-2">
            Países para Teste
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {Object.entries(countries).map(([code, country]) => (
              <label key={code} className="flex items-center space-x-2 p-2 bg-secondary-700 rounded-lg">
                <input
                  type="checkbox"
                  checked={testConfig.countries_to_test.includes(code)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setTestConfig({
                        ...testConfig,
                        countries_to_test: [...testConfig.countries_to_test, code]
                      });
                    } else {
                      setTestConfig({
                        ...testConfig,
                        countries_to_test: testConfig.countries_to_test.filter(c => c !== code)
                      });
                    }
                  }}
                  disabled={isRunning}
                  className="form-checkbox h-4 w-4 text-primary-500 focus:ring-primary-500 border-secondary-600 rounded"
                />
                <span className="text-sm text-white">
                  {country.flag} {country.name}
                </span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Gráficos em Tempo Real */}
      {isRunning && realTimeData.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-panel rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              📊 CPS e Chamadas Simultâneas
            </h3>
            <div className="h-64">
              <Line data={getChartData()} options={chartOptions} />
            </div>
          </div>

          <div className="glass-panel rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              📈 Taxa de Sucesso
            </h3>
            <div className="h-64">
              <Line data={getSuccessRateData()} options={chartOptions} />
            </div>
          </div>
        </div>
      )}

      {/* Resultados do Teste */}
      {testResults && (
        <div className="glass-panel rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">
              📋 Resultados do Último Teste
            </h3>
            <div className="flex space-x-2">
              <button
                onClick={() => handleExportResults('json')}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
              >
                📄 JSON
              </button>
              <button
                onClick={() => handleExportResults('csv')}
                className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm transition-colors"
              >
                📊 CSV
              </button>
              <button
                onClick={() => handleExportResults('excel')}
                className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white rounded text-sm transition-colors"
              >
                📈 Excel
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">
                {testResults.avg_cps || 0}
              </div>
              <div className="text-sm text-secondary-400">CPS Médio</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">
                {testResults.max_concurrent || 0}
              </div>
              <div className="text-sm text-secondary-400">Pico Simultâneas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">
                {((testResults.overall_success_rate || 0) * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-secondary-400">Taxa Geral</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-400">
                {testResults.total_errors || 0}
              </div>
              <div className="text-sm text-secondary-400">Total Erros</div>
            </div>
          </div>
        </div>
      )}

      {/* Informações Importantes */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <h4 className="font-medium text-blue-400 mb-2">ℹ️ Informações sobre Testes de Carga</h4>
        <ul className="text-sm text-blue-300 space-y-1">
          <li>• <strong>CPS Recomendado:</strong> 20-30 CPS para teste de alta performance</li>
          <li>• <strong>Duração:</strong> 10-60 minutos para testes completos</li>
          <li>• <strong>CLIs:</strong> Use 1000+ CLIs para testes realistas</li>
          <li>• <strong>Países:</strong> Teste com mix de países para validar comportamento</li>
          <li>• <strong>Monitoramento:</strong> Acompanhe taxa de sucesso e erros em tempo real</li>
        </ul>
      </div>
    </div>
  );
};

export default LoadTestManager; 