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
    colombia: { name: 'Colombia', flag: '🇨🇴' },
    argentina: { name: 'Argentina', flag: '🇦🇷' },
    chile: { name: 'Chile', flag: '🇨🇱' },
    peru: { name: 'Perú', flag: '🇵🇪' }
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
      console.error('❌ Error al verificar estado del test:', err);
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
          // Agregar datos en tiempo real
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
        console.error('❌ Error al obtener estado:', err);
      }
    }, 2000);
  };

  const loadTestResults = async () => {
    try {
      const results = await performanceService.getLoadTestResults();
      setTestResults(results);
    } catch (err) {
      console.error('❌ Error al cargar resultados:', err);
    }
  };

  const handleStartTest = async () => {
    // Validar configuración
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
      setSuccessMessage('¡Test de carga iniciado con éxito!');
      setIsRunning(true);
      startPolling();
      
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('❌ Error al iniciar test:', err);
      setError('Error al iniciar test de carga. Intentá nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleStopTest = async () => {
    try {
      setLoading(true);
      await performanceService.stopLoadTest();
      setIsRunning(false);
      setSuccessMessage('¡Test de carga detenido!');
      
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
      
      setTimeout(() => {
        setSuccessMessage('');
        loadTestResults();
      }, 2000);
    } catch (err) {
      console.error('❌ Error al detener test:', err);
      setError('Error al detener test de carga.');
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
        const exportFileDefaultName = `resultados_test_carga_${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
      } else {
        // Para CSV/Excel, asumir que el backend devuelve el archivo
        const blob = new Blob([results], { type: 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `resultados_test_carga_${new Date().toISOString().split('T')[0]}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('❌ Error al exportar resultados:', err);
      setError('Error al exportar resultados.');
    }
  };

  const handleCountryChange = (countryCode, checked) => {
    setTestConfig(prev => ({
      ...prev,
      countries_to_test: checked 
        ? [...prev.countries_to_test, countryCode]
        : prev.countries_to_test.filter(c => c !== countryCode)
    }));
  };

  const getChartData = () => {
    return {
      labels: realTimeData.map(d => d.timestamp.toLocaleTimeString()),
      datasets: [
        {
          label: 'CPS Actual',
          data: realTimeData.map(d => d.cps),
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Llamadas Simultáneas',
          data: realTimeData.map(d => d.concurrent_calls),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          yAxisID: 'y1'
        }
      ]
    };
  };

  const getSuccessRateData = () => {
    return {
      labels: realTimeData.map(d => d.timestamp.toLocaleTimeString()),
      datasets: [
        {
          label: 'Tasa de Éxito (%)',
          data: realTimeData.map(d => d.success_rate * 100),
          borderColor: 'rgb(168, 85, 247)',
          backgroundColor: 'rgba(168, 85, 247, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { color: 'rgba(255, 255, 255, 0.7)' }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        beginAtZero: true,
        grid: { drawOnChartArea: false },
        ticks: { color: 'rgba(255, 255, 255, 0.7)' }
      },
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { color: 'rgba(255, 255, 255, 0.7)' }
      }
    },
    plugins: {
      legend: {
        labels: { color: 'rgba(255, 255, 255, 0.8)' }
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Encabezado */}
      <div className="glass-panel p-6 rounded-xl">
        <h2 className="text-2xl font-bold text-gradient-primary mb-2">
          🧪 Test de Carga - Alto Rendimiento
        </h2>
        <p className="text-secondary-400">
          Probá el sistema con 20-30 CPS para validar comportamiento bajo alta carga
        </p>
      </div>

      {/* Alertas */}
      {error && (
        <div className="glass-panel p-4 rounded-xl border border-error-500/30">
          <div className="flex items-center space-x-2">
            <span className="text-error-400">❌</span>
            <span className="text-error-300">{error}</span>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="glass-panel p-4 rounded-xl border border-success-500/30">
          <div className="flex items-center space-x-2">
            <span className="text-success-400">✅</span>
            <span className="text-success-300">{successMessage}</span>
          </div>
        </div>
      )}

      {/* Estado del Test */}
      {testStatus && (
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white">Estado del Test</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-400">
                {testStatus.current_cps || 0}
              </div>
              <div className="text-sm text-secondary-400">CPS Actual</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-accent-400">
                {testStatus.concurrent_calls || 0}
              </div>
              <div className="text-sm text-secondary-400">Llamadas Simultáneas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success-400">
                {((testStatus.success_rate || 0) * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-secondary-400">Tasa de Éxito</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-error-400">
                {testStatus.errors || 0}
              </div>
              <div className="text-sm text-secondary-400">Errores</div>
            </div>
          </div>
        </div>
      )}

      {/* Configuración del Test */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">
          ⚙️ Configuración del Test
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              CPS Objetivo
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={testConfig.target_cps}
              onChange={(e) => setTestConfig({...testConfig, target_cps: parseFloat(e.target.value)})}
              className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
              disabled={isRunning}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              Duración (minutos)
            </label>
            <input
              type="number"
              min="1"
              max="180"
              value={testConfig.duration_minutes}
              onChange={(e) => setTestConfig({...testConfig, duration_minutes: parseInt(e.target.value)})}
              className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
              disabled={isRunning}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              Número de CLIs
            </label>
            <input
              type="number"
              min="100"
              max="10000"
              value={testConfig.number_of_clis}
              onChange={(e) => setTestConfig({...testConfig, number_of_clis: parseInt(e.target.value)})}
              className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
              disabled={isRunning}
            />
          </div>
        </div>

        <div className="flex space-x-4 mb-6">
          <button
            onClick={handleStartTest}
            disabled={loading || isRunning}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              loading || isRunning
                ? 'bg-secondary-600 cursor-not-allowed'
                : 'bg-success-600 hover:bg-success-700 text-white'
            }`}
          >
            {loading ? 'Iniciando...' : '▶️ Iniciar Test'}
          </button>
          
          <button
            onClick={handleStopTest}
            disabled={!isRunning || loading}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              !isRunning || loading
                ? 'bg-secondary-600 cursor-not-allowed'
                : 'bg-error-600 hover:bg-error-700 text-white'
            }`}
          >
            {loading ? 'Deteniendo...' : '⏹️ Detener Test'}
          </button>
        </div>

        {/* Selección de Países */}
        <div>
          <label className="block text-sm font-medium text-secondary-300 mb-3">
            Países para Testear
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(countries).map(([code, country]) => (
              <label key={code} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={testConfig.countries_to_test.includes(code)}
                  onChange={(e) => handleCountryChange(code, e.target.checked)}
                  disabled={isRunning}
                  className="w-4 h-4 text-primary-600 bg-secondary-800 border-secondary-600 rounded focus:ring-primary-500"
                />
                <span className="text-sm text-white">
                  {country.flag} {country.name}
                </span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Gráficos en Tiempo Real */}
      {realTimeData.length > 0 && (
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">
            📊 CPS y Llamadas Simultáneas
          </h3>
          <div className="h-80">
            <Line data={getChartData()} options={chartOptions} />
          </div>
        </div>
      )}

      {realTimeData.length > 0 && (
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">
            📈 Tasa de Éxito
          </h3>
          <div className="h-80">
            <Line data={getSuccessRateData()} options={chartOptions} />
          </div>
        </div>
      )}

      {/* Resultados del Test */}
      {testResults && (
        <div className="glass-panel p-6 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">
              📋 Resultados del Último Test
            </h3>
            <div className="flex space-x-2">
              <button
                onClick={() => handleExportResults('json')}
                className="px-3 py-1 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm"
              >
                📄 JSON
              </button>
              <button
                onClick={() => handleExportResults('csv')}
                className="px-3 py-1 bg-accent-600 hover:bg-accent-700 text-white rounded-lg text-sm"
              >
                📊 CSV
              </button>
              <button
                onClick={() => handleExportResults('excel')}
                className="px-3 py-1 bg-success-600 hover:bg-success-700 text-white rounded-lg text-sm"
              >
                📗 Excel
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-400">
                {testResults.avg_cps || 0}
              </div>
              <div className="text-sm text-secondary-400">CPS Promedio</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success-400">
                {testResults.total_calls || 0}
              </div>
              <div className="text-sm text-secondary-400">Total Llamadas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-accent-400">
                {((testResults.success_rate || 0) * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-secondary-400">Tasa de Éxito</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-warning-400">
                {testResults.duration_minutes || 0}
              </div>
              <div className="text-sm text-secondary-400">Duración (min)</div>
            </div>
          </div>
        </div>
      )}

      {/* Información Importante */}
      <div className="glass-panel p-6 rounded-xl">
        <h4 className="font-medium text-blue-400 mb-2">ℹ️ Información sobre Tests de Carga</h4>
        <ul className="text-sm text-secondary-300 space-y-1">
          <li>• <strong>CPS Recomendado:</strong> 20-30 CPS para test de alto rendimiento</li>
          <li>• <strong>Duración:</strong> 10-60 minutos para tests completos</li>
          <li>• <strong>CLIs:</strong> Usá 1000+ CLIs para tests realistas</li>
          <li>• <strong>Países:</strong> Probá con mix de países para validar comportamiento</li>
          <li>• <strong>Monitoreo:</strong> Observá métricas en tiempo real durante el test</li>
        </ul>
      </div>
    </div>
  );
};

export default LoadTestManager; 