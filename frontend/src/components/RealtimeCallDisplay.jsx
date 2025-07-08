import React, { useState, useEffect, useRef } from 'react';
import { makeApiRequest } from '../config/api';

const RealtimeCallDisplay = () => {
  const [activeCalls, setActiveCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(2000); // 2 segundos
  const [totalCalls, setTotalCalls] = useState(0);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  // Flags de países para exibir no display
  const countryFlags = {
    '1': '🇺🇸', // EUA
    '55': '🇧🇷', // Brasil
    '52': '🇲🇽', // México
    '57': '🇨🇴', // Colômbia
    '51': '🇵🇪', // Peru
    '34': '🇪🇸', // Espanha
    '33': '🇫🇷', // França
    '44': '🇬🇧', // Reino Unido
  };

  const fetchActiveCalls = async () => {
    try {
      setError(null);
      
      // Buscar dados reais da API
      const response = await makeApiRequest('/monitoring/llamadas-activas');
      
      if (response.active_calls) {
        setActiveCalls(response.active_calls);
        setTotalCalls(response.total_active);
        setLastUpdate(new Date(response.last_update));
      } else {
        setActiveCalls([]);
        setTotalCalls(0);
      }
      
    } catch (err) {
      console.error('Erro ao buscar chamadas ativas:', err);
      setError('Erro ao conectar com o servidor');
      setActiveCalls([]);
      setTotalCalls(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveCalls();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchActiveCalls, refreshInterval);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, refreshInterval]);

  const formatCallDisplay = (call) => {
    const flag = countryFlags[call.codigo_pais] || '🌐';
    // Formato exato: SIP/cliente/ext,duração,flags → número → 00:00:47
    return `${call.canal},${call.duracao_segundos},${call.flags}      ${call.numero}      ${call.duracao_formatada}`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'atendida':
        return 'text-green-400';
      case 'tocando':
        return 'text-yellow-400';
      case 'iniciando':
        return 'text-blue-400';
      case 'transferindo':
        return 'text-purple-400';
      case 'ocupado':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'atendida':
        return 'CONECTADA';
      case 'tocando':
        return 'TOCANDO';
      case 'iniciando':
        return 'LLAMANDO';
      case 'transferindo':
        return 'TRANSFIRIENDO';
      case 'ocupado':
        return 'OCUPADO';
      default:
        return 'DESCONOCIDO';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gradient-primary">
            📞 Llamadas en Tiempo Real
          </h1>
          <p className="text-secondary-400 mt-1">
            Monitoreo en vivo de todas las llamadas activas
          </p>
        </div>
        
        {/* Controls */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-secondary-300">Auto-refresh:</span>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                autoRefresh 
                  ? 'bg-green-600 text-white' 
                  : 'bg-secondary-700 text-secondary-300 hover:bg-secondary-600'
              }`}
            >
              {autoRefresh ? 'ON' : 'OFF'}
            </button>
          </div>
          
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="bg-secondary-700 border border-secondary-600 text-white text-sm rounded px-3 py-1 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value={1000}>1s</option>
            <option value={2000}>2s</option>
            <option value={5000}>5s</option>
            <option value={10000}>10s</option>
          </select>
          
          <button
            onClick={fetchActiveCalls}
            disabled={loading}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? '🔄' : '⟳'} Actualizar
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-600/20 rounded-lg">
              <span className="text-2xl">📞</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-secondary-400">Llamadas Activas</p>
              <p className="text-2xl font-bold text-white">{totalCalls}</p>
            </div>
          </div>
        </div>
        
        <div className="glass-panel p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-600/20 rounded-lg">
              <span className="text-2xl">⏱️</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-secondary-400">Última Actualización</p>
              <p className="text-sm font-medium text-white">
                {lastUpdate ? lastUpdate.toLocaleTimeString() : '--:--:--'}
              </p>
            </div>
          </div>
        </div>
        
        <div className="glass-panel p-4">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-600/20 rounded-lg">
              <span className="text-2xl">🔄</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-secondary-400">Auto-refresh</p>
              <p className="text-sm font-medium text-white">
                {autoRefresh ? `${refreshInterval/1000}s` : 'Desactivado'}
              </p>
            </div>
          </div>
        </div>
        
        <div className="glass-panel p-4">
          <div className="flex items-center">
            <div className="p-2 bg-purple-600/20 rounded-lg">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-secondary-400">Estado</p>
              <p className="text-sm font-medium text-white">
                {error ? 'Error' : 'Conectado'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="glass-panel border-red-500/20 bg-red-900/10 p-4">
          <div className="flex items-center">
            <span className="text-red-400 text-xl mr-3">⚠️</span>
            <div>
              <h3 className="text-red-400 font-medium">Error de Conexión</h3>
              <p className="text-red-300 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Terminal Display */}
      <div className="glass-panel">
        <div className="border-b border-secondary-700 p-4">
          <h2 className="text-lg font-semibold text-white flex items-center">
            <span className="text-green-400 mr-2">●</span>
            Monitor de Llamadas - Terminal
            <span className="ml-auto text-sm text-secondary-400">
              Formato: SIP/cliente/ext,duración,flags → número → 00:00:47
            </span>
          </h2>
        </div>
        
        <div className="p-4">
          {loading && activeCalls.length === 0 ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-secondary-400">Cargando llamadas activas...</p>
            </div>
          ) : activeCalls.length === 0 ? (
            <div className="text-center py-12">
              <span className="text-6xl mb-4 block">📵</span>
              <h3 className="text-xl font-semibold text-white mb-2">Sin Llamadas Activas</h3>
              <p className="text-secondary-400">No hay llamadas en progreso en este momento</p>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="font-mono text-sm bg-black/30 p-4 rounded-lg border border-secondary-700">
                <div className="text-green-400 mb-3 border-b border-secondary-700 pb-2">
                  === TERMINAL DE MONITOREO DE LLAMADAS ===
                </div>
                {activeCalls.map((call, index) => {
                  const flag = countryFlags[call.codigo_pais] || '🌐';
                  return (
                    <div key={call.id || index} className="mb-2 group hover:bg-secondary-800/30 p-2 rounded transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className="text-lg">{flag}</span>
                          <span className="text-green-400 font-mono text-sm">
                            {formatCallDisplay(call)}
                          </span>
                        </div>
                        <div className="flex items-center space-x-4 text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                          <span className={`px-2 py-1 rounded ${getStatusColor(call.status)} bg-black/20`}>
                            {getStatusText(call.status)}
                          </span>
                          {call.agente && (
                            <span className="text-blue-400">👤 {call.agente}</span>
                          )}
                          {call.campanha && (
                            <span className="text-purple-400">📋 {call.campanha}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="text-center text-sm text-secondary-400">
        <p>
          🔄 Actualización automática cada {refreshInterval/1000} segundos 
          {lastUpdate && ` • Última actualización: ${lastUpdate.toLocaleString()}`}
        </p>
      </div>
    </div>
  );
};

export default RealtimeCallDisplay; 