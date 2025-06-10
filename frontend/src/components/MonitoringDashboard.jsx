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
  const API_BASE = 'http://localhost:8000/api/v1';

  // ============================================================================
  // FUNÇÕES DE API
  // ============================================================================

  const fetchDashboardData = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/monitoring/dashboard/resumo`);
      if (!response.ok) throw new Error('Erro ao buscar dados');
      
      const data = await response.json();
      setDashboardData(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Erro ao buscar dashboard:', err);
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
          setDashboardData(message.dados);
          setLastUpdate(new Date());
        }
      } catch (err) {
        console.error('Erro ao processar mensagem WebSocket:', err);
      }
    };

    websocket.onclose = () => {
      console.log('WebSocket desconectado');
      setIsConnected(false);
      
      // Tentar reconectar após 5 segundos
      setTimeout(() => {
        if (autoRefresh) {
          connectWebSocket();
        }
      }, 5000);
    };

    websocket.onerror = (error) => {
      console.error('Erro no WebSocket:', error);
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

  const StatCard = ({ title, value, icon: Icon, color = 'blue', change = null }) => (
    <div className={`bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border-l-4 border-${color}-500`}>
      <div className="flex items-center">
        <div className={`p-3 rounded-full bg-${color}-100 dark:bg-${color}-900`}>
          <Icon className={`h-6 w-6 text-${color}-600 dark:text-${color}-300`} />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
              {title}
            </dt>
            <dd className={`text-2xl font-bold text-gray-900 dark:text-white`}>
              {value}
            </dd>
            {change && (
              <dd className={`text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {change >= 0 ? '+' : ''}{change}%
              </dd>
            )}
          </dl>
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
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className={`p-2 rounded-full bg-${color}-100 dark:bg-${color}-900`}>
              <Icon className={`h-4 w-4 text-${color}-600 dark:text-${color}-300`} />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {agent.nome_agente}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {agent.codigo_agente}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className={`text-xs font-medium text-${color}-600 dark:text-${color}-300`}>
              {agent.status_atual.replace('_', ' ').toUpperCase()}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {agent.chamadas_atendidas} chamadas
            </p>
          </div>
        </div>
        
        {agent.chamada_atual && (
          <div className="mt-2 text-xs text-gray-600 dark:text-gray-300">
            Em chamada: {agent.chamada_atual}
          </div>
        )}
      </div>
    );
  };

  // ============================================================================
  // COMPONENTE DE CAMPANHAS
  // ============================================================================

  const CampaignCard = ({ campaign }) => (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-900 dark:text-white">
          {campaign.nome_campanha}
        </h3>
        <span className={`px-2 py-1 text-xs rounded-full ${
          campaign.status_campanha === 'ativa' 
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
            : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
        }`}>
          {campaign.status_campanha}
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-500 dark:text-gray-400">Ativas</p>
          <p className="font-medium text-gray-900 dark:text-white">
            {campaign.chamadas_ativas}
          </p>
        </div>
        <div>
          <p className="text-gray-500 dark:text-gray-400">Realizadas</p>
          <p className="font-medium text-gray-900 dark:text-white">
            {campaign.chamadas_realizadas}
          </p>
        </div>
        <div>
          <p className="text-gray-500 dark:text-gray-400">Taxa Atend.</p>
          <p className="font-medium text-gray-900 dark:text-white">
            {campaign.taxa_atendimento}%
          </p>
        </div>
        <div>
          <p className="text-gray-500 dark:text-gray-400">Sucesso</p>
          <p className="font-medium text-gray-900 dark:text-white">
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
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            {provider.nome_provedor}
          </h3>
          <div className={`w-3 h-3 rounded-full bg-${statusColor}-500`}></div>
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500 dark:text-gray-400">Chamadas hoje:</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {provider.chamadas_hoje}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500 dark:text-gray-400">Taxa sucesso:</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {provider.taxa_sucesso}%
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500 dark:text-gray-400">Latência:</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {provider.latencia_media ? `${Math.round(provider.latencia_media)}ms` : '-'}
            </span>
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
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <ArrowPathIcon className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="mt-2 text-gray-600 dark:text-gray-400">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="h-8 w-8 text-red-600 mx-auto" />
          <p className="mt-2 text-red-600">Erro: {error}</p>
          <button 
            onClick={fetchDashboardData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Tentar novamente
          </button>
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
              <StatCard
                title="Campanhas Ativas"
                value={dashboardData.total_campanhas_ativas}
                icon={ChartBarIcon}
                color="blue"
              />
              <StatCard
                title="Chamadas Ativas"
                value={dashboardData.total_chamadas_ativas}
                icon={PhoneIcon}
                color="green"
              />
              <StatCard
                title="Agentes Online"
                value={dashboardData.total_agentes_online}
                icon={UserGroupIcon}
                color="purple"
              />
              <StatCard
                title="Taxa Atendimento"
                value={`${dashboardData.taxa_atendimento_geral}%`}
                icon={CheckCircleIcon}
                color="yellow"
              />
            </div>

            {/* Alertas se houver */}
            {(dashboardData.alertas_criticos > 0 || dashboardData.alertas_warning > 0) && (
              <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4">
                <div className="flex items-center">
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-600 dark:text-red-300" />
                  <span className="ml-2 text-red-800 dark:text-red-200 font-medium">
                    {dashboardData.alertas_criticos} alertas críticos, {dashboardData.alertas_warning} avisos
                  </span>
                </div>
              </div>
            )}

            {/* Grid de seções */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Campanhas */}
              <div className="lg:col-span-1">
                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Campanhas Ativas
                </h2>
                <div className="space-y-3">
                  {dashboardData.campanhas?.length > 0 ? (
                    dashboardData.campanhas.slice(0, 5).map((campaign, index) => (
                      <CampaignCard key={index} campaign={campaign} />
                    ))
                  ) : (
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                      Nenhuma campanha ativa
                    </p>
                  )}
                </div>
              </div>

              {/* Agentes */}
              <div className="lg:col-span-1">
                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Status dos Agentes
                </h2>
                <div className="space-y-3">
                  {dashboardData.agentes?.length > 0 ? (
                    dashboardData.agentes.slice(0, 5).map((agent, index) => (
                      <AgentCard key={index} agent={agent} />
                    ))
                  ) : (
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                      Nenhum agente configurado
                    </p>
                  )}
                </div>
              </div>

              {/* Provedores SIP */}
              <div className="lg:col-span-1">
                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Provedores SIP
                </h2>
                <div className="space-y-3">
                  {dashboardData.status_provedores?.length > 0 ? (
                    dashboardData.status_provedores.map((provider, index) => (
                      <ProviderCard key={index} provider={provider} />
                    ))
                  ) : (
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                      Nenhum provedor configurado
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