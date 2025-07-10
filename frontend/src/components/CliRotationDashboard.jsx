import React, { useState, useEffect } from 'react';
import { Bar, Line, Doughnut, Scatter } from 'react-chartjs-2';
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
  Legend
} from 'chart.js';
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
  Legend
);

const CliRotationDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cliData, setCliData] = useState([]);
  const [usage, setUsage] = useState({});
  const [filters, setFilters] = useState({
    country: '',
    provider: '',
    status: '',
    sortBy: 'usage_count',
    sortOrder: 'desc'
  });
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 50,
    total: 0
  });
  const [refreshInterval, setRefreshInterval] = useState(null);

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

  const providers = {
    twilio: { name: 'Twilio', color: '#F22F46' },
    vonage: { name: 'Vonage', color: '#1E40AF' },
    telnyx: { name: 'Telnyx', color: '#059669' },
    local: { name: 'Local Provider', color: '#7C3AED' }
  };

  useEffect(() => {
    loadCliData();
    loadUsageData();
    
    // Auto-refresh a cada 30 segundos
    const interval = setInterval(() => {
      loadCliData();
      loadUsageData();
    }, 30000);
    
    setRefreshInterval(interval);
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [filters, pagination.page]);

  const loadCliData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simular carregamento de dados de CLI
      // Em produção, seria uma API real: /api/cli/list
      const response = await fetch('/api/cli/list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filters,
          pagination: {
            skip: (pagination.page - 1) * pagination.pageSize,
            limit: pagination.pageSize
          }
        })
      });

      if (!response.ok) {
        throw new Error('Erro ao carregar dados de CLI');
      }

      const data = await response.json();
      setCliData(data.clis || []);
      setPagination(prev => ({
        ...prev,
        total: data.total || 0
      }));

    } catch (err) {
      console.error('❌ Erro ao carregar CLIs:', err);
      
      // Fallback com dados simulados
      const simulatedData = generateSimulatedCliData();
      setCliData(simulatedData);
      setPagination(prev => ({
        ...prev,
        total: simulatedData.length
      }));
    } finally {
      setLoading(false);
    }
  };

  const loadUsageData = async () => {
    try {
      const usageResponse = await performanceService.getCliUsage();
      setUsage(usageResponse.usage || {});
    } catch (err) {
      console.error('❌ Erro ao carregar dados de uso:', err);
    }
  };

  const generateSimulatedCliData = () => {
    const simulatedClis = [];
    const countryCodes = Object.keys(countries);
    const providerCodes = Object.keys(providers);
    
    for (let i = 0; i < 100; i++) {
      const country = countryCodes[Math.floor(Math.random() * countryCodes.length)];
      const provider = providerCodes[Math.floor(Math.random() * providerCodes.length)];
      const usageCount = Math.floor(Math.random() * 150);
      const lastUsed = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000);
      
      simulatedClis.push({
        id: i + 1,
        number: `+${Math.floor(Math.random() * 9000000000) + 1000000000}`,
        country,
        provider,
        usage_count: usageCount,
        last_used: lastUsed.toISOString(),
        status: usageCount > 90 ? 'limit_reached' : usageCount > 50 ? 'high_usage' : 'active',
        success_rate: (Math.random() * 0.3 + 0.7).toFixed(3), // 70-100%
        avg_duration: Math.floor(Math.random() * 120 + 30), // 30-150 seconds
        created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
      });
    }
    
    return simulatedClis;
  };

  const getUsageDistributionData = () => {
    const distribution = cliData.reduce((acc, cli) => {
      const range = cli.usage_count === 0 ? 'Não usado' :
                    cli.usage_count <= 25 ? '1-25' :
                    cli.usage_count <= 50 ? '26-50' :
                    cli.usage_count <= 75 ? '51-75' :
                    cli.usage_count <= 100 ? '76-100' : '100+';
      acc[range] = (acc[range] || 0) + 1;
      return acc;
    }, {});

    return {
      labels: Object.keys(distribution),
      datasets: [{
        data: Object.values(distribution),
        backgroundColor: [
          '#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'
        ],
        borderWidth: 2,
        borderColor: '#1F2937'
      }]
    };
  };

  const getCountryDistributionData = () => {
    const distribution = cliData.reduce((acc, cli) => {
      const country = countries[cli.country]?.name || cli.country;
      acc[country] = (acc[country] || 0) + 1;
      return acc;
    }, {});

    return {
      labels: Object.keys(distribution),
      datasets: [{
        label: 'CLIs por País',
        data: Object.values(distribution),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: '#3B82F6',
        borderWidth: 1
      }]
    };
  };

  const getUsageOverTimeData = () => {
    const usageByDay = cliData.reduce((acc, cli) => {
      const date = new Date(cli.last_used).toLocaleDateString();
      acc[date] = (acc[date] || 0) + cli.usage_count;
      return acc;
    }, {});

    const sortedDates = Object.keys(usageByDay).sort();
    
    return {
      labels: sortedDates,
      datasets: [{
        label: 'Uso Acumulado',
        data: sortedDates.map(date => usageByDay[date]),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
      }]
    };
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-400';
      case 'high_usage': return 'text-yellow-400';
      case 'limit_reached': return 'text-red-400';
      case 'inactive': return 'text-gray-400';
      default: return 'text-white';
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      active: 'bg-green-500/20 text-green-400',
      high_usage: 'bg-yellow-500/20 text-yellow-400',
      limit_reached: 'bg-red-500/20 text-red-400',
      inactive: 'bg-gray-500/20 text-gray-400'
    };
    
    const labels = {
      active: 'Ativo',
      high_usage: 'Uso Alto',
      limit_reached: 'Limite Atingido',
      inactive: 'Inativo'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || colors.inactive}`}>
        {labels[status] || status}
      </span>
    );
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

  const totalPages = Math.ceil(pagination.total / pagination.pageSize);

  if (loading && cliData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-secondary-400">Carregando dados de CLI...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-2">
          🔄 Dashboard de Rotação de DIDs/CLIs
        </h2>
        <p className="text-purple-100">
          Monitoramento de uso, rotação e performance de {pagination.total.toLocaleString()} CLIs
        </p>
      </div>

      {/* Estatísticas Gerais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-primary-400">
            {pagination.total.toLocaleString()}
          </div>
          <div className="text-sm text-secondary-400">Total de CLIs</div>
        </div>
        
        <div className="glass-panel rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-green-400">
            {cliData.filter(cli => cli.status === 'active').length}
          </div>
          <div className="text-sm text-secondary-400">CLIs Ativos</div>
        </div>
        
        <div className="glass-panel rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-yellow-400">
            {cliData.filter(cli => cli.status === 'high_usage').length}
          </div>
          <div className="text-sm text-secondary-400">Alto Uso</div>
        </div>
        
        <div className="glass-panel rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-red-400">
            {cliData.filter(cli => cli.status === 'limit_reached').length}
          </div>
          <div className="text-sm text-secondary-400">Limite Atingido</div>
        </div>
      </div>

      {/* Filtros */}
      <div className="glass-panel rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">🔍 Filtros</h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">País</label>
            <select
              value={filters.country}
              onChange={(e) => setFilters({...filters, country: e.target.value})}
              className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos os países</option>
              {Object.entries(countries).map(([code, country]) => (
                <option key={code} value={code}>{country.flag} {country.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">Provedor</label>
            <select
              value={filters.provider}
              onChange={(e) => setFilters({...filters, provider: e.target.value})}
              className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos os provedores</option>
              {Object.entries(providers).map(([code, provider]) => (
                <option key={code} value={code}>{provider.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos os status</option>
              <option value="active">Ativo</option>
              <option value="high_usage">Alto Uso</option>
              <option value="limit_reached">Limite Atingido</option>
              <option value="inactive">Inativo</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">Ordenar por</label>
            <select
              value={filters.sortBy}
              onChange={(e) => setFilters({...filters, sortBy: e.target.value})}
              className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="usage_count">Uso</option>
              <option value="last_used">Último Uso</option>
              <option value="success_rate">Taxa de Sucesso</option>
              <option value="created_at">Data de Criação</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => {
                setFilters({
                  country: '',
                  provider: '',
                  status: '',
                  sortBy: 'usage_count',
                  sortOrder: 'desc'
                });
                setPagination(prev => ({...prev, page: 1}));
              }}
              className="w-full px-4 py-2 bg-secondary-600 hover:bg-secondary-700 text-white rounded-lg transition-colors"
            >
              Limpar Filtros
            </button>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <div className="glass-panel rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">📊 Distribuição por Uso</h3>
          <div className="h-64">
            <Doughnut data={getUsageDistributionData()} options={chartOptions} />
          </div>
        </div>

        <div className="glass-panel rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">🌍 CLIs por País</h3>
          <div className="h-64">
            <Bar data={getCountryDistributionData()} options={chartOptions} />
          </div>
        </div>

        <div className="glass-panel rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">📈 Uso ao Longo do Tempo</h3>
          <div className="h-64">
            <Line data={getUsageOverTimeData()} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Tabela de CLIs */}
      <div className="glass-panel rounded-lg overflow-hidden">
        <div className="p-6 border-b border-secondary-700">
          <h3 className="text-lg font-semibold text-white">📋 Lista de CLIs</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-secondary-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-300 uppercase tracking-wider">
                  Número
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-300 uppercase tracking-wider">
                  País
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-300 uppercase tracking-wider">
                  Provedor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-300 uppercase tracking-wider">
                  Uso
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-300 uppercase tracking-wider">
                  Taxa Sucesso
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-300 uppercase tracking-wider">
                  Último Uso
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-300 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-secondary-700">
              {cliData.map((cli) => (
                <tr key={cli.id} className="hover:bg-secondary-800 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    {cli.number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    {countries[cli.country]?.flag} {countries[cli.country]?.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    <span 
                      className="px-2 py-1 rounded-full text-xs font-medium"
                      style={{ 
                        backgroundColor: `${providers[cli.provider]?.color}20`,
                        color: providers[cli.provider]?.color
                      }}
                    >
                      {providers[cli.provider]?.name}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center">
                      <div className="text-white mr-2">{cli.usage_count}</div>
                      <div className="w-16 bg-secondary-700 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-green-500 to-red-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(cli.usage_count, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    {(cli.success_rate * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-300">
                    {new Date(cli.last_used).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(cli.status)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Paginação */}
        <div className="px-6 py-4 border-t border-secondary-700 flex items-center justify-between">
          <div className="text-sm text-secondary-400">
            Mostrando {(pagination.page - 1) * pagination.pageSize + 1} a {Math.min(pagination.page * pagination.pageSize, pagination.total)} de {pagination.total.toLocaleString()} CLIs
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPagination(prev => ({...prev, page: Math.max(1, prev.page - 1)}))}
              disabled={pagination.page === 1}
              className="px-3 py-1 bg-secondary-600 hover:bg-secondary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded transition-colors"
            >
              Anterior
            </button>
            
            <span className="text-sm text-secondary-300">
              Página {pagination.page} de {totalPages}
            </span>
            
            <button
              onClick={() => setPagination(prev => ({...prev, page: Math.min(totalPages, prev.page + 1)}))}
              disabled={pagination.page === totalPages}
              className="px-3 py-1 bg-secondary-600 hover:bg-secondary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded transition-colors"
            >
              Próxima
            </button>
          </div>
        </div>
      </div>

      {/* Informações Técnicas */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <h4 className="font-medium text-blue-400 mb-2">ℹ️ Informações sobre Rotação de CLIs</h4>
        <ul className="text-sm text-blue-300 space-y-1">
          <li>• <strong>Rotação Inteligente:</strong> CLIs são selecionados com base no menor uso recente</li>
          <li>• <strong>Limites por País:</strong> USA/Canadá limitados a 100 usos/dia</li>
          <li>• <strong>Distribuição:</strong> Sistema balanceia uso entre provedores e regiões</li>
          <li>• <strong>Auto-recuperação:</strong> CLIs bloqueados são automaticamente pausados</li>
          <li>• <strong>Monitoramento:</strong> Taxa de sucesso e performance são monitoradas em tempo real</li>
        </ul>
      </div>
    </div>
  );
};

export default CliRotationDashboard; 