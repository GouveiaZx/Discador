import React, { useState, useEffect, useCallback, useRef } from 'react';
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
import { makeApiRequest } from '../config/api';
import { useCampaigns } from '../contexts/CampaignContext';

// ============================================================================
// COMPONENTE PRINCIPAL DO DASHBOARD
// ============================================================================

const MonitoringDashboard = () => {
  // Usar contexto de campanhas
  const { 
    campaigns, 
    activeCampaigns, 
    loading: campaignsLoading, 
    error: campaignsError,
    lastUpdate,
    activeCampaignsCount,
    refreshCampaigns
  } = useCampaigns();

  // Estados do dashboard
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  // WebSocket para atualizações em tempo real
  const websocketRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const intervalRef = useRef(null);

  // Configurações
  const REFRESH_INTERVAL = 3000; // 3 segundos

  // ============================================================================
  // FUNÇÕES DE API
  // ============================================================================

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Usar campanhas ativas do contexto
      console.log('📊 [MonitoringDashboard] Usando campanhas do contexto:', activeCampaigns.length);
      
      // Buscar estatísticas agregadas para campanhas ativas
      const statsPromises = activeCampaigns.map(campaign => 
        makeApiRequest(`/presione1/campanhas/${campaign.id}/estadisticas`)
      );
      
      const statsResults = await Promise.allSettled(statsPromises);
      const campaignStats = statsResults.map((result, index) => ({
        ...activeCampaigns[index],
        stats: result.status === 'fulfilled' ? result.value : null
      }));
      
      // Calcular métricas agregadas
      const totalCalls = campaignStats.reduce((sum, campaign) => 
        sum + (campaign.stats?.llamadas_realizadas || 0), 0);
      const totalContacted = campaignStats.reduce((sum, campaign) => 
        sum + (campaign.stats?.llamadas_contestadas || 0), 0);
      const totalPressed1 = campaignStats.reduce((sum, campaign) => 
        sum + (campaign.stats?.llamadas_presiono_1 || 0), 0);
      const totalTransferred = campaignStats.reduce((sum, campaign) => 
        sum + (campaign.stats?.llamadas_transferidas || 0), 0);
      
      const aggregatedData = {
        campanhas_ativas: activeCampaigns.length,
        llamadas_realizadas: totalCalls,
        llamadas_contestadas: totalContacted,
        llamadas_presiono_1: totalPressed1,
        llamadas_transferidas: totalTransferred,
        tasa_contestacion: totalCalls > 0 ? (totalContacted / totalCalls * 100).toFixed(1) : 0,
        tasa_presiono_1: totalContacted > 0 ? (totalPressed1 / totalContacted * 100).toFixed(1) : 0,
        tasa_transferencia: totalPressed1 > 0 ? (totalTransferred / totalPressed1 * 100).toFixed(1) : 0,
        campaign_details: campaignStats
      };
      
      setDashboardData(aggregatedData);
      console.log('✅ [MonitoringDashboard] Dados agregados:', aggregatedData);
      
    } catch (err) {
      console.error('❌ [MonitoringDashboard] Erro ao carregar dashboard:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [activeCampaigns]);

  // Função para conectar WebSocket (placeholder para futuro)
  const connectWebSocket = useCallback(() => {
    // TODO: Implementar WebSocket específico para presione1
    console.log('WebSocket para presione1 não implementado ainda');
  }, []);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    // Buscar dados iniciais quando campanhas estiverem carregadas
    if (!campaignsLoading && activeCampaigns) {
      fetchDashboardData();
    }
  }, [campaignsLoading, activeCampaigns, fetchDashboardData]);

  useEffect(() => {
    // Configurar auto-refresh
    if (autoRefresh && !campaignsLoading) {
      intervalRef.current = setInterval(fetchDashboardData, REFRESH_INTERVAL);
    }

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, [autoRefresh, campaignsLoading, fetchDashboardData]);

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

  const CampaignCard = ({ campaign }) => {
    const getStatusColor = (status) => {
      if (campaign.activa && !campaign.pausada) return 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100';
      if (campaign.activa && campaign.pausada) return 'bg-amber-100 text-amber-800 dark:bg-amber-800 dark:text-amber-100';
      return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100';
    };

    const getStatusText = () => {
      if (campaign.activa && !campaign.pausada) return 'Activa';
      if (campaign.activa && campaign.pausada) return 'Pausada';
      return 'Inactiva';
    };

    const stats = campaign.stats || {};
    
    return (
      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-gray-900 dark:text-white truncate">
            {campaign.nombre || 'Campaña sin nombre'}
          </h4>
          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>
        
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500 dark:text-gray-400">Llamadas Realizadas</p>
            <p className="font-semibold text-gray-900 dark:text-white">
              {stats.llamadas_realizadas || 0}
            </p>
          </div>
          <div>
            <p className="text-gray-500 dark:text-gray-400">Contestadas</p>
            <p className="font-semibold text-gray-900 dark:text-white">
              {stats.llamadas_contestadas || 0}
            </p>
          </div>
          <div>
            <p className="text-gray-500 dark:text-gray-400">Presionaron 1</p>
            <p className="font-semibold text-blue-600 dark:text-blue-400">
              {stats.llamadas_presiono_1 || 0}
            </p>
          </div>
          <div>
            <p className="text-gray-500 dark:text-gray-400">Transferidas</p>
            <p className="font-semibold text-green-600 dark:text-green-400">
              {stats.llamadas_transferidas || 0}
            </p>
          </div>
        </div>
        
        {/* Métricas de performance */}
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>Taxa Atendimento: {stats.tasa_contestacion || 0}%</span>
            <span>Taxa Interesse: {stats.tasa_presiono_1 || 0}%</span>
          </div>
          <div className="mt-1 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(stats.tasa_contestacion || 0, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>
    );
  };

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
                  title={autoRefresh ? 'Pausar actualizaciones' : 'Iniciar actualizaciones'}
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
                value={dashboardData.campanhas_ativas}
                icon="📊"
                color="blue"
              />
              <StatusCard
                title="Llamadas Activas"
                value={dashboardData.llamadas_realizadas}
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
                value={`${dashboardData.tasa_contestacion}%`}
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
              <div className="col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <ChartBarIcon className="w-5 h-5 mr-2 text-blue-500" />
                    Campanhas "Presione 1" Ativas
                  </h3>
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {isConnected ? 'Conectado' : 'Desconectado'}
                    </span>
                  </div>
                </div>
                
                <div className="space-y-4">
                  {activeCampaigns.length > 0 ? (
                    activeCampaigns.map((campaign, index) => (
                      <CampaignCard key={campaign.id || index} campaign={campaign} />
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <ExclamationTriangleIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500 dark:text-gray-400">
                        Nenhuma campanha ativa encontrada
                      </p>
                      <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                        Inicie uma campanha para ver o monitoramento em tempo real
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Seção de Métricas Agregadas */}
              <div className="col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center mb-4">
                  <PhoneIcon className="w-5 h-5 mr-2 text-green-500" />
                  Métricas Agregadas - Hoje
                </h3>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {dashboardData?.llamadas_realizadas || 0}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Total Llamadas</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                      {dashboardData?.llamadas_contestadas || 0}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Contestadas</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                      {dashboardData?.llamadas_presiono_1 || 0}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Presionaron 1</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                      {dashboardData?.llamadas_transferidas || 0}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Transferidas</p>
                  </div>
                </div>
                
                {/* Barras de progresso para taxas */}
                <div className="mt-6 space-y-3">
                  <div>
                    <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                      <span>Taxa de Atendimento</span>
                      <span>{dashboardData?.tasa_contestacion || 0}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(dashboardData?.tasa_contestacion || 0, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                      <span>Taxa de Interesse (Presione 1)</span>
                      <span>{dashboardData?.tasa_presiono_1 || 0}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-purple-500 to-purple-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(dashboardData?.tasa_presiono_1 || 0, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                      <span>Taxa de Transferência</span>
                      <span>{dashboardData?.tasa_transferencia || 0}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(dashboardData?.tasa_transferencia || 0, 100)}%` }}
                      ></div>
                    </div>
                  </div>
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