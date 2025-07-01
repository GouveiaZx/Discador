import React, { useState, useEffect, useCallback } from 'react';
import { 
  PhoneIcon, 
  UserGroupIcon, 
  ChartBarIcon, 
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlayIcon,
  PauseIcon,
  StopIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

// ============================================================================
// COMPONENTE PRINCIPAL DO DASHBOARD
// ============================================================================

const MonitoringDashboard = () => {
  // Estados do dashboard
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  // WebSocket para atualizações em tempo real
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  // Configurações
  const REFRESH_INTERVAL = 3000; // 3 segundos
  const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api/v1' 
    : '/api/v1';

  // ============================================================================
  // FUNÇÕES DE API
  // ============================================================================

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/monitoring/dashboard/resumo`);
      if (!response.ok) throw new Error('Error al buscar datos');
      
      const data = await response.json();
      setDashboardData(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error al buscar dashboard:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Função para conectar WebSocket
  const connectWebSocket = useCallback(() => {
    if (ws) {
      ws.close();
    }

    const websocket = new WebSocket(`ws://localhost:8000/api/v1/monitoring/ws/1`);
    
    websocket.onopen = () => {
      console.log('WebSocket conectado');
      setIsConnected(true);
      // Solicitar dados iniciais
      websocket.send(JSON.stringify({ tipo: 'solicitar_dashboard' }));
    };

    websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.tipo === 'dashboard_update') {
          setDashboardData(message.datos);
          setLastUpdate(new Date());
        }
      } catch (err) {
        console.error('Error al procesar mensaje WebSocket:', err);
      }
    };

    websocket.onclose = () => {
      console.log('WebSocket desconectado');
      setIsConnected(false);
      
      // Intentar reconectar después de 5 segundos
      setTimeout(() => {
        if (autoRefresh) {
          connectWebSocket();
        }
      }, 5000);
    };

    websocket.onerror = (error) => {
      console.error('Error en WebSocket:', error);
      setIsConnected(false);
    };

    setWs(websocket);
  }, [autoRefresh, ws]);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    // Buscar dados iniciais
    fetchDashboardData();

    // Conectar WebSocket se auto-refresh estiver ativo
    if (autoRefresh) {
      connectWebSocket();
    }

    // Cleanup
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [autoRefresh]);

  // ============================================================================
  // COMPONENTES DE CARTÕES
  // ============================================================================

  const StatusCard = ({ title, value, icon, color = 'blue', subtitle }) => (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 border-l-4 border-${color}-500`}>
      <div className="flex items-center">
        <div className={`text-${color}-500 text-2xl mr-4`}>
          {icon}
        </div>
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              {title}
          </p>
          <p className="text-2xl font-semibold text-gray-900 dark:text-white">
              {value}
          </p>
          {subtitle && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {subtitle}
            </p>
            )}
        </div>
      </div>
    </div>
  );

  // ============================================================================
  // COMPONENTE DE AGENTES
  // ============================================================================

  const AgentCard = ({ agent }) => {
    const statusColors = {
      livre: 'green',
      em_chamada: 'yellow',
      ausente: 'red',
      pausado: 'gray',
      offline: 'red'
    };

    const statusIcons = {
      livre: CheckCircleIcon,
      em_chamada: PhoneIcon,
      ausente: XCircleIcon,
      pausado: PauseIcon,
      offline: StopIcon
    };

    const color = statusColors[agent.status_atual] || 'gray';
    const Icon = statusIcons[agent.status_atual] || XCircleIcon;

    return (
      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white">
                {agent.nome_agente}
            </h4>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              ID: {agent.codigo_agente}
              </p>
          </div>
          <div className="text-right">
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              agent.status_atual === 'disponible'
                ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                : agent.status_atual === 'ocupado'
                ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
            }`}>
              {agent.status_atual}
            </span>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Llamadas: {agent.chamadas_atendidas}
            </p>
          </div>
        </div>
      </div>
    );
  };

  // ============================================================================
  // COMPONENTE DE CAMPANHAS
  // ============================================================================

  const CampaignCard = ({ campaign }) => (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium text-gray-900 dark:text-white">
          {campaign.nome_campanha}
        </h4>
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
          campaign.status_campanha === 'ativa' 
            ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
            : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100'
        }`}>
          {campaign.status_campanha}
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-500 dark:text-gray-400">Llamadas Hoy</p>
          <p className="font-semibold text-gray-900 dark:text-white">
            {campaign.chamadas_ativas}
          </p>
        </div>
        <div>
          <p className="text-gray-500 dark:text-gray-400">Agentes</p>
          <p className="font-semibold text-gray-900 dark:text-white">
            {campaign.agentes_asignados}
          </p>
        </div>
        <div>
          <p className="text-gray-500 dark:text-gray-400">Tasa Atend.</p>
          <p className="font-semibold text-gray-900 dark:text-white">
            {campaign.taxa_atendimento}%
          </p>
        </div>
        <div>
          <p className="text-gray-500 dark:text-gray-400">Éxito</p>
          <p className="font-semibold text-gray-900 dark:text-white">
            {campaign.taxa_sucesso}%
          </p>
        </div>
      </div>
    </div>
  );

  // ============================================================================
  // COMPONENTE DE PROVEDORES
  // ============================================================================

  const ProviderCard = ({ provider }) => {
    const statusColor = provider.status_conexao === 'conectado' ? 'green' : 'red';
    
    return (
      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white">
            {provider.nome_provedor}
            </h4>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {provider.tipo_provedor}
            </p>
          </div>
          <div className="text-right">
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              provider.status_conexao === 'conectado'
                ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
            }`}>
              {provider.status_conexao}
            </span>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Calidad: {provider.calidad_conexion}/5
            </p>
          </div>
        </div>
      </div>
    );
  };

  // ============================================================================
  // RENDER PRINCIPAL
  // ============================================================================

  if (loading && !dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
              Error en el Dashboard
            </h3>
            <p className="mt-2 text-red-600">Error: {error}</p>
          <button 
            onClick={fetchDashboardData}
              className="mt-2 text-sm bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded"
          >
              Reintentar
          </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      darkMode ? 'dark bg-gray-900' : 'bg-gray-50'
    }`}>
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <ChartBarIcon className="h-8 w-8 text-blue-600" />
              <h1 className="ml-3 text-xl font-semibold text-gray-900 dark:text-white">
                Painel de Monitoramento
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Status da conexão */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {isConnected ? 'Conectado' : 'Desconectado'}
                </span>
              </div>

              {/* Última atualização */}
              {lastUpdate && (
                <div className="flex items-center space-x-1 text-sm text-gray-600 dark:text-gray-400">
                  <ClockIcon className="h-4 w-4" />
                  <span>{lastUpdate.toLocaleTimeString()}</span>
                </div>
              )}

              {/* Controles */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className={`p-2 rounded-lg ${
                    autoRefresh 
                      ? 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-300' 
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  }`}
                  title={autoRefresh ? 'Pausar atualizações' : 'Iniciar atualizações'}
                >
                  {autoRefresh ? <PauseIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
                </button>

                <button
                  onClick={fetchDashboardData}
                  className="p-2 rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-800"
                  title="Atualizar agora"
                >
                  <ArrowPathIcon className="h-4 w-4" />
                </button>

                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className="p-2 rounded-lg bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400"
                  title="Alternar tema"
                >
                  {darkMode ? '☀️' : '🌙'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Conteúdo principal */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {dashboardData && (
          <div className="space-y-6">
            {/* Cards de estatísticas principais */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatusCard
                title="Campañas Activas"
                value={dashboardData.total_campanas_activas}
                icon="📊"
                color="blue"
              />
              <StatusCard
                title="Llamadas Activas"
                value={dashboardData.total_llamadas_activas}
                icon="📞"
                color="green"
              />
              <StatusCard
                title="Agentes Online"
                value={dashboardData.total_agentes_online}
                icon="👥"
                color="indigo"
              />
              <StatusCard
                title="Tasa Atención"
                value={`${dashboardData.tasa_atencion_general}%`}
                icon="📈"
                color="purple"
              />
            </div>

            {/* Alertas se houver */}
            {(dashboardData.alertas_criticos > 0 || dashboardData.alertas_warning > 0) && (
              <div className="bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                    {dashboardData.alertas_criticos} alertas críticos, {dashboardData.alertas_warning} avisos
                    </h3>
                  </div>
                </div>
              </div>
            )}

            {/* Grid de seções */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Campanhas */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Campañas Activas
                </h3>
                <div className="space-y-4">
                  {dashboardData.campanas?.length > 0 ? (
                    dashboardData.campanas.slice(0, 5).map((campaign, index) => (
                      <CampaignCard key={index} campaign={campaign} />
                    ))
                  ) : (
                    <p className="text-gray-500 dark:text-gray-400">
                      Ninguna campaña activa
                    </p>
                  )}
                </div>
              </div>

              {/* Agentes */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Agentes Online
                </h3>
                <div className="space-y-4">
                  {dashboardData.agentes?.length > 0 ? (
                    dashboardData.agentes.slice(0, 5).map((agent, index) => (
                      <AgentCard key={index} agent={agent} />
                    ))
                  ) : (
                    <p className="text-gray-500 dark:text-gray-400">
                      Ningún agente online
                    </p>
                  )}
                </div>
              </div>

              {/* Provedores SIP */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Estado Proveedores
                </h3>
                <div className="space-y-4">
                  {dashboardData.estado_proveedores?.length > 0 ? (
                    dashboardData.estado_proveedores.map((provider, index) => (
                      <ProviderCard key={index} provider={provider} />
                    ))
                  ) : (
                    <p className="text-gray-500 dark:text-gray-400">
                      Sin información de proveedores
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default MonitoringDashboard; 