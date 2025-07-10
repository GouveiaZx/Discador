import React, { useState, useEffect } from 'react';
import { Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import performanceService from '../services/performanceService';

ChartJS.register(
  CategoryScale,
  LinearScale,
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
  const [filters, setFilters] = useState({
    country: '',
    status: '',
    provider: ''
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    itemsPerPage: 50,
    total: 0
  });
  const [sortConfig, setSortConfig] = useState({
    key: 'usage_count',
    direction: 'desc'
  });

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

  const providers = {
    'provider-1': 'Proveedor A',
    'provider-2': 'Proveedor B',
    'provider-3': 'Proveedor C',
    'provider-4': 'Proveedor D'
  };

  const statusLabels = {
    'active': 'Activo',
    'high_usage': 'Uso Alto',
    'limit_reached': 'Límite Alcanzado',
    'blocked': 'Bloqueado',
    'inactive': 'Inactivo'
  };

  // Cargar datos de CLI
  useEffect(() => {
    loadCliData();
  }, [filters, pagination.currentPage, sortConfig]);

  const loadCliData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simular carga de datos de CLI
      const mockData = generateMockCliData();
      
      // Aplicar filtros
      let filteredData = mockData;
      if (filters.country) {
        filteredData = filteredData.filter(cli => cli.country === filters.country);
      }
      if (filters.status) {
        filteredData = filteredData.filter(cli => cli.status === filters.status);
      }
      if (filters.provider) {
        filteredData = filteredData.filter(cli => cli.provider === filters.provider);
      }

      // Aplicar ordenamiento
      filteredData.sort((a, b) => {
        if (sortConfig.direction === 'asc') {
          return a[sortConfig.key] > b[sortConfig.key] ? 1 : -1;
        }
        return a[sortConfig.key] < b[sortConfig.key] ? 1 : -1;
      });

      // Aplicar paginación
      const startIndex = (pagination.currentPage - 1) * pagination.itemsPerPage;
      const paginatedData = filteredData.slice(startIndex, startIndex + pagination.itemsPerPage);

      setCliData(paginatedData);
      setPagination(prev => ({ ...prev, total: filteredData.length }));

    } catch (err) {
      console.error('❌ Error al cargar CLIs:', err);
      setError('Error al cargar datos de CLI. Verificá la conexión.');
      // Fallback con datos simulados
      const fallbackData = generateMockCliData().slice(0, 10);
      setCliData(fallbackData);
      setPagination(prev => ({ ...prev, total: fallbackData.length }));
    } finally {
      setLoading(false);
    }
  };

  const generateMockCliData = () => {
    const mockClis = [];
    const countryKeys = Object.keys(countries);
    const providerKeys = Object.keys(providers);
    const statusKeys = Object.keys(statusLabels);

    for (let i = 0; i < 2000; i++) {
      const country = countryKeys[Math.floor(Math.random() * countryKeys.length)];
      const provider = providerKeys[Math.floor(Math.random() * providerKeys.length)];
      const usageCount = Math.floor(Math.random() * 150);
      const lastUsed = new Date(Date.now() - Math.floor(Math.random() * 86400000 * 7)).toISOString();
      
      mockClis.push({
        id: `cli-${i + 1}`,
        phone_number: `+1${Math.floor(Math.random() * 9000000000) + 1000000000}`,
        country,
        provider,
        usage_count: usageCount,
        last_used: lastUsed,
        success_rate: Math.floor(Math.random() * 40) + 60,
        status: usageCount > 90 ? 'limit_reached' : usageCount > 50 ? 'high_usage' : 'active',
        created_at: new Date(Date.now() - Math.floor(Math.random() * 86400000 * 30)).toISOString()
      });
    }

    return mockClis;
  };

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  const handlePageChange = (page) => {
    setPagination(prev => ({ ...prev, currentPage: page }));
  };

  const clearFilters = () => {
    setFilters({
      country: '',
      status: '',
      provider: ''
    });
    setPagination(prev => ({ ...prev, currentPage: 1 }));
  };

  // Datos para gráficos
  const getCountryDistribution = () => {
    const distribution = {};
    cliData.forEach(cli => {
      distribution[cli.country] = (distribution[cli.country] || 0) + 1;
    });

    return {
      labels: Object.keys(distribution).map(code => countries[code]?.name || code),
      datasets: [{
        label: 'CLIs por País',
        data: Object.values(distribution),
        backgroundColor: [
          '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
          '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
        ],
        borderWidth: 2,
        borderColor: '#1F2937'
      }]
    };
  };

  const getStatusDistribution = () => {
    const distribution = {};
    cliData.forEach(cli => {
      distribution[cli.status] = (distribution[cli.status] || 0) + 1;
    });

    return {
      labels: Object.keys(distribution).map(status => statusLabels[status] || status),
      datasets: [{
        label: 'CLIs por Estado',
        data: Object.values(distribution),
        backgroundColor: ['#10B981', '#F59E0B', '#EF4444', '#6B7280', '#8B5CF6'],
        borderWidth: 2,
        borderColor: '#1F2937'
      }]
    };
  };

  const getUsageChart = () => {
    const usageRanges = { '0-25': 0, '26-50': 0, '51-75': 0, '76-100': 0, '100+': 0 };
    
    cliData.forEach(cli => {
      const usage = cli.usage_count;
      if (usage <= 25) usageRanges['0-25']++;
      else if (usage <= 50) usageRanges['26-50']++;
      else if (usage <= 75) usageRanges['51-75']++;
      else if (usage <= 100) usageRanges['76-100']++;
      else usageRanges['100+']++;
    });

    return {
      labels: Object.keys(usageRanges),
      datasets: [{
        label: 'Distribución de Uso',
        data: Object.values(usageRanges),
        backgroundColor: '#3B82F6',
        borderColor: '#1E40AF',
        borderWidth: 1
      }]
    };
  };

  const getStatusColor = (status) => {
    const colors = {
      active: 'text-green-400',
      high_usage: 'text-yellow-400',
      limit_reached: 'text-red-400',
      blocked: 'text-red-600',
      inactive: 'text-gray-400'
    };
    return colors[status] || colors.inactive;
  };

  const getStatusBadge = (status) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      high_usage: 'bg-yellow-100 text-yellow-800',
      limit_reached: 'bg-red-100 text-red-800',
      blocked: 'bg-red-200 text-red-900',
      inactive: 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || colors.inactive}`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: { size: 12 }
        }
      }
    }
  };

  if (loading && cliData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-secondary-400">Cargando datos de CLI...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-xl">
        <h2 className="text-2xl font-bold text-gradient-primary mb-2">
          🔄 Dashboard de Rotación de DIDs/CLIs
        </h2>
        <p className="text-secondary-400">
          Monitoreo de uso, rotación y rendimiento de {pagination.total.toLocaleString()} CLIs
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-4 rounded-xl text-center">
          <div className="text-2xl font-bold text-primary-400">{pagination.total.toLocaleString()}</div>
          <div className="text-sm text-secondary-400">Total de CLIs</div>
        </div>
        <div className="glass-panel p-4 rounded-xl text-center">
          <div className="text-2xl font-bold text-success-400">
            {cliData.filter(cli => cli.status === 'active').length}
          </div>
          <div className="text-sm text-secondary-400">CLIs Activos</div>
        </div>
        <div className="glass-panel p-4 rounded-xl text-center">
          <div className="text-2xl font-bold text-warning-400">
            {cliData.filter(cli => cli.status === 'high_usage').length}
          </div>
          <div className="text-sm text-secondary-400">Uso Alto</div>
        </div>
        <div className="glass-panel p-4 rounded-xl text-center">
          <div className="text-2xl font-bold text-error-400">
            {cliData.filter(cli => cli.status === 'limit_reached').length}
          </div>
          <div className="text-sm text-secondary-400">Límite Alcanzado</div>
        </div>
      </div>

      {/* Filtros */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">🔍 Filtros</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">País</label>
            <select
              value={filters.country}
              onChange={(e) => setFilters({...filters, country: e.target.value})}
              className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
            >
              <option value="">Todos los países</option>
              {Object.entries(countries).map(([code, country]) => (
                <option key={code} value={code}>
                  {country.flag} {country.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">Proveedor</label>
            <select
              value={filters.provider}
              onChange={(e) => setFilters({...filters, provider: e.target.value})}
              className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
            >
              <option value="">Todos los proveedores</option>
              {Object.entries(providers).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">Estado</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
            >
              <option value="">Todos los estados</option>
              {Object.entries(statusLabels).map(([code, label]) => (
                <option key={code} value={code}>{label}</option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={clearFilters}
              className="w-full px-4 py-2 bg-secondary-600 hover:bg-secondary-700 text-white rounded-lg transition-colors"
            >
              Limpiar Filtros
            </button>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">🌍 CLIs por País</h3>
          <div className="h-64">
            <Doughnut data={getCountryDistribution()} options={chartOptions} />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">📊 CLIs por Estado</h3>
          <div className="h-64">
            <Doughnut data={getStatusDistribution()} options={chartOptions} />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">📈 Distribución de Uso</h3>
          <div className="h-64">
            <Bar data={getUsageChart()} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Tabla de CLIs */}
      <div className="glass-panel p-6 rounded-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">📋 Lista de CLIs</h3>
          <div className="text-sm text-secondary-400">
            Mostrando {((pagination.currentPage - 1) * pagination.itemsPerPage) + 1} - {Math.min(pagination.currentPage * pagination.itemsPerPage, pagination.total)} de {pagination.total.toLocaleString()} CLIs
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-secondary-600">
                <th className="text-left py-3 px-4 text-secondary-300 font-medium">
                  <button onClick={() => handleSort('phone_number')} className="flex items-center space-x-1 hover:text-white">
                    <span>Teléfono</span>
                    {sortConfig.key === 'phone_number' && (
                      <span>{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </button>
                </th>
                <th className="text-left py-3 px-4 text-secondary-300 font-medium">
                  <button onClick={() => handleSort('country')} className="flex items-center space-x-1 hover:text-white">
                    <span>País</span>
                    {sortConfig.key === 'country' && (
                      <span>{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </button>
                </th>
                <th className="text-left py-3 px-4 text-secondary-300 font-medium">
                  <button onClick={() => handleSort('usage_count')} className="flex items-center space-x-1 hover:text-white">
                    <span>Uso</span>
                    {sortConfig.key === 'usage_count' && (
                      <span>{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </button>
                </th>
                <th className="text-left py-3 px-4 text-secondary-300 font-medium">
                  <button onClick={() => handleSort('success_rate')} className="flex items-center space-x-1 hover:text-white">
                    <span>Tasa Éxito</span>
                    {sortConfig.key === 'success_rate' && (
                      <span>{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </button>
                </th>
                <th className="text-left py-3 px-4 text-secondary-300 font-medium">
                  <button onClick={() => handleSort('status')} className="flex items-center space-x-1 hover:text-white">
                    <span>Estado</span>
                    {sortConfig.key === 'status' && (
                      <span>{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </button>
                </th>
                <th className="text-left py-3 px-4 text-secondary-300 font-medium">
                  Último Uso
                </th>
              </tr>
            </thead>
            <tbody>
              {cliData.map((cli, index) => (
                <tr key={cli.id} className="border-b border-secondary-700/50 hover:bg-secondary-800/30">
                  <td className="py-3 px-4 text-white font-mono text-sm">{cli.phone_number}</td>
                  <td className="py-3 px-4 text-white">
                    <div className="flex items-center space-x-2">
                      <span>{countries[cli.country]?.flag}</span>
                      <span className="text-sm">{countries[cli.country]?.name}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-white">{cli.usage_count}</td>
                  <td className="py-3 px-4 text-white">{cli.success_rate}%</td>
                  <td className="py-3 px-4">
                    {getStatusBadge(cli.status)}
                  </td>
                  <td className="py-3 px-4 text-secondary-300 text-sm">
                    {new Date(cli.last_used).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Paginación */}
        <div className="flex items-center justify-between mt-6">
          <div className="text-sm text-secondary-400">
            Mostrando {((pagination.currentPage - 1) * pagination.itemsPerPage) + 1} - {Math.min(pagination.currentPage * pagination.itemsPerPage, pagination.total)} de {pagination.total.toLocaleString()} CLIs
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handlePageChange(pagination.currentPage - 1)}
              disabled={pagination.currentPage === 1}
              className="px-3 py-1 bg-secondary-600 hover:bg-secondary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              Anterior
            </button>
            
            <span className="text-white px-3 py-1">
              {pagination.currentPage} de {Math.ceil(pagination.total / pagination.itemsPerPage)}
            </span>
            
            <button
              onClick={() => handlePageChange(pagination.currentPage + 1)}
              disabled={pagination.currentPage >= Math.ceil(pagination.total / pagination.itemsPerPage)}
              className="px-3 py-1 bg-secondary-600 hover:bg-secondary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              Siguiente
            </button>
          </div>
        </div>
      </div>

      {/* Información Importante */}
      <div className="glass-panel p-6 rounded-xl">
        <h4 className="font-medium text-blue-400 mb-2">ℹ️ Información sobre Rotación de CLIs</h4>
        <ul className="text-sm text-secondary-300 space-y-1">
          <li>• <strong>Rotación Inteligente:</strong> CLIs son seleccionados basándose en el menor uso reciente</li>
          <li>• <strong>Límites por País:</strong> USA/Canadá limitados a 100 usos/día</li>
          <li>• <strong>Distribución:</strong> El sistema balancea uso entre proveedores y regiones</li>
          <li>• <strong>Auto-recuperación:</strong> CLIs bloqueados son automáticamente pausados</li>
          <li>• <strong>Monitoreo:</strong> Tasa de éxito y rendimiento son monitoreados en tiempo real</li>
        </ul>
      </div>
    </div>
  );
};

export default CliRotationDashboard; 