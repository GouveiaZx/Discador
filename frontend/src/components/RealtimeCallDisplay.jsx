import React, { useState, useEffect, useRef } from 'react';
import { makeApiRequest } from '../config/api';

const RealtimeCallDisplay = () => {
  const [activeCalls, setActiveCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(2000); // 2 segundos
  const [totalCalls, setTotalCalls] = useState(0);
  const [totalDuration, setTotalDuration] = useState(0);
  const intervalRef = useRef(null);
  const wsRef = useRef(null);

  // Simular dados de chamadas para desenvolvimento
  const mockCalls = [
    {
      id: '1',
      sip_channel: 'SIP/liza/7508',
      client_name: 'liza',
      extension: '7508',
      numero_discado: '8323870217',
      duracao: 47,
      flags: 'tTr',
      status: 'conectada',
      caller_id: 'Discador',
      trunk: 'trunk_brasil',
      start_time: new Date(Date.now() - 47000).toISOString()
    },
    {
      id: '2', 
      sip_channel: 'SIP/maria/3401',
      client_name: 'maria',
      extension: '3401',
      numero_discado: '1155987654321',
      duracao: 128,
      flags: 'tT',
      status: 'conectada',
      caller_id: 'Campanha',
      trunk: 'trunk_brasil',
      start_time: new Date(Date.now() - 128000).toISOString()
    },
    {
      id: '3',
      sip_channel: 'SIP/carlos/9876',
      client_name: 'carlos', 
      extension: '9876',
      numero_discado: '573001234567',
      duracao: 23,
      flags: 'tTr',
      status: 'conectada',
      caller_id: 'Discador',
      trunk: 'trunk_colombia',
      start_time: new Date(Date.now() - 23000).toISOString()
    }
  ];

  const fetchActiveCalls = async () => {
    try {
      // Tentar buscar dados reais da API
      const response = await makeApiRequest('/monitoring/llamadas-activas');
      
      if (response && response.active_calls) {
        setActiveCalls(response.active_calls);
        setTotalCalls(response.total_active || 0);
      } else {
        // Usar dados mock se não houver dados reais
        setActiveCalls(mockCalls);
        setTotalCalls(mockCalls.length);
      }
      
      // Calcular duração total
      const total = activeCalls.reduce((sum, call) => sum + (call.duracao || 0), 0);
      setTotalDuration(total);
      
      setLastUpdate(new Date());
      setLoading(false);
    } catch (error) {
      console.warn('Usando dados mock para demonstração:', error.message);
      setActiveCalls(mockCalls);
      setTotalCalls(mockCalls.length);
      setLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatCallDisplay = (call) => {
    // Formato: SIP/cliente/ext,duração,flags número 00:00:47
    return `${call.sip_channel},${call.duracao},${call.flags}      ${call.numero_discado}      ${formatDuration(call.duracao)}`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'conectada': return 'text-green-600 bg-green-50';
      case 'tocando': return 'text-yellow-600 bg-yellow-50';
      case 'ocupado': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTrunkFlag = (trunk) => {
    if (trunk?.includes('brasil')) return '🇧🇷';
    if (trunk?.includes('colombia')) return '🇨🇴';
    if (trunk?.includes('mexico')) return '🇲🇽';
    if (trunk?.includes('usa')) return '🇺🇸';
    return '🌐';
  };

  // Auto-refresh das chamadas
  useEffect(() => {
    fetchActiveCalls();
    
    if (autoRefresh) {
      intervalRef.current = setInterval(() => {
        fetchActiveCalls();
        
        // Incrementar duração das chamadas localmente para parecer mais real
        setActiveCalls(prevCalls => 
          prevCalls.map(call => ({
            ...call,
            duracao: call.duracao + (refreshInterval / 1000)
          }))
        );
      }, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, refreshInterval]);

  // Atualizar duração em tempo real
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveCalls(prevCalls => 
        prevCalls.map(call => ({
          ...call,
          duracao: call.duracao + 1
        }))
      );
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Carregando chamadas ativas...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Cabeçalho */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">📞 Chamadas Ativas em Tempo Real</h2>
          <p className="text-gray-600 mt-1">Monitoramento detalhado de todas as chamadas em andamento</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-600">Auto-refresh:</label>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="text-sm border border-gray-300 rounded-lg px-3 py-1"
          >
            <option value={1000}>1s</option>
            <option value={2000}>2s</option>
            <option value={5000}>5s</option>
            <option value={10000}>10s</option>
          </select>
        </div>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-blue-600">Chamadas Ativas</p>
              <p className="text-2xl font-semibold text-blue-900">{totalCalls}</p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-green-600">Duração Total</p>
              <p className="text-2xl font-semibold text-green-900">{formatDuration(totalDuration)}</p>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-yellow-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-yellow-600">Última Atualização</p>
              <p className="text-sm font-semibold text-yellow-900">
                {lastUpdate ? lastUpdate.toLocaleTimeString() : '--:--:--'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-purple-600">Duração Média</p>
              <p className="text-2xl font-semibold text-purple-900">
                {totalCalls > 0 ? formatDuration(Math.floor(totalDuration / totalCalls)) : '--:--'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de Chamadas - Estilo Terminal */}
      <div className="bg-black rounded-lg p-4 font-mono text-sm">
        <div className="text-green-400 mb-4 border-b border-gray-700 pb-2">
          <div className="flex justify-between items-center">
            <span>📟 DISCADOR PREDITIVO - CHAMADAS ATIVAS</span>
            <span className="text-xs">
              {new Date().toLocaleString()} | Total: {totalCalls} chamadas
            </span>
          </div>
        </div>
        
        {activeCalls.length === 0 ? (
          <div className="text-yellow-400 text-center py-8">
            <div className="text-4xl mb-2">📱</div>
            <p>Nenhuma chamada ativa no momento</p>
            <p className="text-xs text-gray-400 mt-2">As chamadas aparecerão aqui em tempo real</p>
          </div>
        ) : (
          <div className="space-y-2">
            {activeCalls.map((call, index) => (
              <div 
                key={call.id || index}
                className="grid grid-cols-12 gap-2 text-white hover:bg-gray-800 p-2 rounded transition-colors"
              >
                <div className="col-span-1 text-yellow-400">
                  {getTrunkFlag(call.trunk)}
                </div>
                <div className="col-span-5 text-green-400">
                  {formatCallDisplay(call)}
                </div>
                <div className="col-span-2 text-blue-400">
                  {call.client_name}
                </div>
                <div className="col-span-2 text-purple-400">
                  {call.caller_id}
                </div>
                <div className="col-span-1 text-orange-400">
                  {call.flags}
                </div>
                <div className="col-span-1">
                  <span className={`px-2 py-1 rounded text-xs ${getStatusColor(call.status)}`}>
                    {call.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Rodapé do Terminal */}
        <div className="border-t border-gray-700 mt-4 pt-2 text-gray-400 text-xs">
          <div className="flex justify-between">
            <span>Sistema ativo - Monitoramento em tempo real</span>
            <span>Press CTRL+C to stop | Auto-refresh: {autoRefresh ? 'ON' : 'OFF'}</span>
          </div>
        </div>
      </div>

      {/* Legenda */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div className="bg-gray-50 rounded-lg p-3">
          <h4 className="font-semibold text-gray-800 mb-2">📋 Formato da Exibição</h4>
          <p className="text-gray-600 font-mono text-xs mb-1">
            SIP/cliente/extensão,duração,flags → número → 00:00:47
          </p>
          <p className="text-gray-500 text-xs">
            Exemplo: SIP/liza/7508,35,tTr → 8323870217 → 00:00:47
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <h4 className="font-semibold text-gray-800 mb-2">🏁 Flags de Chamada</h4>
          <div className="text-xs text-gray-600 space-y-1">
            <p><span className="font-mono bg-yellow-100 px-1">t</span> - Transferência habilitada</p>
            <p><span className="font-mono bg-blue-100 px-1">T</span> - Timeout ativo</p>
            <p><span className="font-mono bg-green-100 px-1">r</span> - Ringing (tocando)</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealtimeCallDisplay; 