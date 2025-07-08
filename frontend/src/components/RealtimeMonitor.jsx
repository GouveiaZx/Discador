import React, { useState, useEffect, useRef } from 'react';
import { makeApiRequest } from '../config/api';

const RealtimeMonitor = () => {
  const [metrics, setMetrics] = useState({
    chamadas_ativas: 0,
    chamadas_completadas: 0,
    chamadas_falhadas: 0,
    taxa_sucesso: 0,
    tempo_medio_chamada: 0,
    campanhas_ativas: 0,
    provedores_online: 0,
    uso_cpu: 0,
    uso_memoria: 0
  });
  
  const [activeCalls, setActiveCalls] = useState([]);
  const [recentCalls, setRecentCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);
  const [filters, setFilters] = useState({
    campaign: '',
    status: '',
    trunk: '',
    dateRange: 'today'
  });
  
  const [expandedSections, setExpandedSections] = useState({
    metrics: true,
    activeCalls: true,
    recentCalls: true,
    systemHealth: true
  });

  const intervalRef = useRef(null);

  const loadMonitoringData = async () => {
    try {
      const [metricsRes, activeCallsRes, recentCallsRes] = await Promise.all([
        makeApiRequest('/monitoring/metrics'),
        makeApiRequest('/monitoring/active-calls'),
        makeApiRequest('/monitoring/recent-calls')
      ]);
      
      setMetrics(metricsRes.data || {});
      setActiveCalls(activeCallsRes.data || []);
      setRecentCalls(recentCallsRes.data || []);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar dados de monitoramento:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMonitoringData();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(loadMonitoringData, refreshInterval);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, refreshInterval]);

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('es-AR');
  };

  const getStatusColor = (status) => {
    const colors = {
      'ativo': 'bg-green-100 text-green-800',
      'conectado': 'bg-green-100 text-green-800',
      'ringing': 'bg-yellow-100 text-yellow-800',
      'em_andamento': 'bg-blue-100 text-blue-800',
      'finalizada': 'bg-gray-100 text-gray-800',
      'falhada': 'bg-red-100 text-red-800',
      'ocupado': 'bg-orange-100 text-orange-800',
      'offline': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const MetricCard = ({ title, value, subtitle, icon, trend, color = 'blue' }) => (
    <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full bg-${color}-100`}>
          {icon}
        </div>
      </div>
      {trend && (
        <div className="mt-3 flex items-center text-xs">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            trend > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {trend > 0 ? '↗' : '↘'} {Math.abs(trend)}%
          </span>
          <span className="ml-2 text-gray-500">vs. hora anterior</span>
        </div>
      )}
    </div>
  );

  const CollapsibleSection = ({ title, expanded, onToggle, children, count }) => (
    <div className="bg-white rounded-lg border">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
          {count !== undefined && (
            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
              {count}
            </span>
          )}
        </div>
        <svg
          className={`w-5 h-5 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {expanded && <div className="px-4 pb-4">{children}</div>}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-gray-600">Cargando monitoreo...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Monitoramento em Tempo Real</h1>
            <p className="text-gray-600 mt-1">
              Acompanhe métricas e status do sistema em tempo real
            </p>
          </div>
          
          <div className="mt-4 lg:mt-0 flex flex-wrap items-center space-x-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="autoRefresh"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="autoRefresh" className="text-sm text-gray-700">
                Auto-refresh
              </label>
            </div>
            
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="text-sm border border-gray-300 rounded px-2 py-1"
              disabled={!autoRefresh}
            >
              <option value={3000}>3s</option>
              <option value={5000}>5s</option>
              <option value={10000}>10s</option>
              <option value={30000}>30s</option>
            </select>
            
            <button
              onClick={loadMonitoringData}
              className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors"
            >
              Atualizar
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <CollapsibleSection
        title="Métricas Principais"
        expanded={expandedSections.metrics}
        onToggle={() => toggleSection('metrics')}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Chamadas Ativas"
            value={metrics.chamadas_ativas || 0}
            icon={
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
            }
            color="blue"
            trend={5}
          />
          
          <MetricCard
            title="Taxa de Sucesso"
            value={`${metrics.taxa_sucesso || 0}%`}
            subtitle={`${metrics.chamadas_completadas || 0} de ${(metrics.chamadas_completadas || 0) + (metrics.chamadas_falhadas || 0)} chamadas`}
            icon={
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            color="green"
            trend={-2}
          />
          
          <MetricCard
            title="Tempo Médio"
            value={formatDuration(metrics.tempo_medio_chamada || 0)}
            subtitle="Por chamada"
            icon={
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            color="purple"
          />
          
          <MetricCard
            title="Campanhas Ativas"
            value={metrics.campanhas_ativas || 0}
            subtitle={`${metrics.provedores_online || 0} provedores online`}
            icon={
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            }
            color="orange"
          />
        </div>
      </CollapsibleSection>

      {/* Active Calls */}
      <CollapsibleSection
        title="Chamadas Ativas"
        expanded={expandedSections.activeCalls}
        onToggle={() => toggleSection('activeCalls')}
        count={activeCalls.length}
      >
        {activeCalls.length === 0 ? (
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma chamada ativa</h3>
            <p className="mt-1 text-sm text-gray-500">As chamadas aparecerão aqui quando iniciadas.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Número
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Campanha
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duração
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trunk
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {activeCalls.map((call, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {call.number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {call.campaign}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(call.status)}`}>
                        {call.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDuration(call.duration || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {call.trunk}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-red-600 hover:text-red-900 mr-2">
                        Finalizar
                      </button>
                      <button className="text-blue-600 hover:text-blue-900">
                        Transferir
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CollapsibleSection>

      {/* Recent Calls */}
      <CollapsibleSection
        title="Chamadas Recentes"
        expanded={expandedSections.recentCalls}
        onToggle={() => toggleSection('recentCalls')}
        count={recentCalls.length}
      >
        {recentCalls.length === 0 ? (
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma chamada recente</h3>
            <p className="mt-1 text-sm text-gray-500">O histórico de chamadas aparecerá aqui.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recentCalls.slice(0, 10).map((call, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-gray-900">{call.number}</span>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(call.status)}`}>
                      {call.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">
                    {call.campaign} • {formatTime(call.timestamp)} • {formatDuration(call.duration || 0)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">{call.trunk}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      {/* System Health */}
      <CollapsibleSection
        title="Status do Sistema"
        expanded={expandedSections.systemHealth}
        onToggle={() => toggleSection('systemHealth')}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-700">CPU</h4>
              <span className="text-sm font-semibold text-gray-900">{metrics.uso_cpu || 0}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${
                  (metrics.uso_cpu || 0) > 80 ? 'bg-red-500' : 
                  (metrics.uso_cpu || 0) > 60 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${metrics.uso_cpu || 0}%` }}
              ></div>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-700">Memória</h4>
              <span className="text-sm font-semibold text-gray-900">{metrics.uso_memoria || 0}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${
                  (metrics.uso_memoria || 0) > 80 ? 'bg-red-500' : 
                  (metrics.uso_memoria || 0) > 60 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${metrics.uso_memoria || 0}%` }}
              ></div>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-700">Uptime</h4>
              <span className="text-sm font-semibold text-gray-900">24h 15m</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="h-2 bg-green-500 rounded-full" style={{ width: '98%' }}></div>
            </div>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  );
};

export default RealtimeMonitor; 