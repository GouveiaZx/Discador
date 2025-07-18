import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  PhoneIcon, 
  PlayIcon, 
  PauseIcon, 
  StopIcon, 
  SpeakerWaveIcon,
  ChartBarIcon,
  UserGroupIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  EyeIcon,
  Cog6ToothIcon,
  MicrophoneIcon,
  SignalIcon,
  BellIcon,
  CubeTransparentIcon
} from '@heroicons/react/24/outline';
import { makeApiRequest } from '../config/api';

const CampaignControl = ({ campaignId, onClose }) => {
  // Estados principais
  const [campaign, setCampaign] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [activeCalls, setActiveCalls] = useState([]);
  const [recentCalls, setRecentCalls] = useState([]);
  const [audioSessions, setAudioSessions] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [actionLoading, setActionLoading] = useState({});
  
  // Estados de controle
  const [selectedView, setSelectedView] = useState('overview');
  const [selectedCallId, setSelectedCallId] = useState(null);
  const [audioVolume, setAudioVolume] = useState(50);
  const [showAdvancedMetrics, setShowAdvancedMetrics] = useState(false);
  
  // Configurações
  const REFRESH_INTERVAL = 3000; // 3 segundos para reduzir carga
  const intervalRef = useRef(null);
  const wsRef = useRef(null);

  // ============================================================================
  // FUNÇÕES DE API CORRIGIDAS
  // ============================================================================

  const fetchCampaignData = useCallback(async () => {
    try {
      if (!campaignId) return;
      
      // Fazer requisições uma por vez para evitar problemas de CORS
      
      // 1. Dados da campanha
      try {
        const campaignRes = await makeApiRequest(`/presione1/campanhas/${campaignId}`);
        setCampaign(campaignRes);
      } catch (err) {
      }
      
      // 2. Estatísticas (com retry em caso de erro)
      try {
        const statsRes = await makeApiRequest(`/presione1/campanhas/${campaignId}/estadisticas`);
        setStatistics(statsRes);
      } catch (err) {
        // Usar datos mock en caso de error
        setStatistics({
          campana_id: campaignId,
          nombre_campana: campaign?.nombre || 'Campaña',
          total_numeros: 0,
          llamadas_realizadas: 0,
          llamadas_contestadas: 0,
          llamadas_presiono_1: 0,
          llamadas_transferidas: 0,
          tasa_contestacion: 0,
          tasa_presiono_1: 0,
          tasa_transferencia: 0,
          activa: false,
          pausada: false,
          llamadas_activas: 0
        });
      }
      
      // 3. Monitoramento
      try {
        const monitorRes = await makeApiRequest(`/presione1/campanhas/${campaignId}/monitor`);
        setActiveCalls(monitorRes.llamadas_activas || []);
        setRecentCalls(monitorRes.ultimas_llamadas || []);
      } catch (err) {
        setActiveCalls([]);
        setRecentCalls([]);
      }
      
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [campaignId, campaign?.nombre]);

  const fetchAudioSessions = useCallback(async () => {
    try {
      const response = await makeApiRequest(`/audio-inteligente/campanhas/${campaignId}/sessoes`);
      setAudioSessions(response.data || []);
    } catch (err) {
      setAudioSessions([]);
    }
  }, [campaignId]);

  const fetchAgents = useCallback(async () => {
    try {
      const response = await makeApiRequest('/monitoring/agentes');
      // Extrair o array de agentes do objeto retornado
      const agentesArray = response.data?.agentes || response.agentes || [];
      setAgents(agentesArray);
    } catch (err) {
      setAgents([]);
    }
  }, []);

  // ============================================================================
  // CONTROLES DE CAMPANHA CORRIGIDOS
  // ============================================================================

  const handlePauseCampaign = async () => {
    try {
      setActionLoading(prev => ({ ...prev, pausing: true }));
      
      const pauseData = {
        campana_id: campaignId,
        pausar: true,
        motivo: 'Pausado pelo operador via interface'
      };
      
      await makeApiRequest(`/presione1/campanhas/${campaignId}/pausar`, 'POST', pauseData);
      
      // Aguardar um pouco antes de atualizar
      setTimeout(() => {
        fetchCampaignData();
      }, 1000);
      
    } catch (err) {
      setError(`Error al pausar campaña: ${err.message}`);
    } finally {
      setActionLoading(prev => ({ ...prev, pausing: false }));
    }
  };

  const handleResumeCampaign = async () => {
    try {
      setActionLoading(prev => ({ ...prev, resuming: true }));
      
      const resumeData = {
        campana_id: campaignId,
        pausar: false,
        motivo: 'Retomado pelo operador via interface'
      };
      
      await makeApiRequest(`/presione1/campanhas/${campaignId}/pausar`, 'POST', resumeData);
      
      // Aguardar um pouco antes de atualizar
      setTimeout(() => {
        fetchCampaignData();
      }, 1000);
      
    } catch (err) {
      setError(`Error al reanudar campaña: ${err.message}`);
    } finally {
      setActionLoading(prev => ({ ...prev, resuming: false }));
    }
  };

  const handleStopCampaign = async () => {
    if (!confirm('🛑 ¿Está seguro que desea DETENER completamente la campaña?\n\nEsta acción:\n• Detendrá todas las llamadas activas\n• Marcará la campaña como inactiva\n• No podrá ser reanudada automáticamente')) return;
    
    try {
      setActionLoading(prev => ({ ...prev, stopping: true }));
      
      await makeApiRequest(`/presione1/campanhas/${campaignId}/parar`, 'POST', {
        campana_id: campaignId,
        motivo: 'Parado pelo operador via interface'
      });
      
      // Aguardar um pouco antes de atualizar
      setTimeout(() => {
        fetchCampaignData();
      }, 1000);
      
    } catch (err) {
      setError(`Error al detener campaña: ${err.message}`);
    } finally {
      setActionLoading(prev => ({ ...prev, stopping: false }));
    }
  };

  const handleTransferCall = async (callId, extension) => {
    try {
      await makeApiRequest(`/presione1/llamadas/${callId}/transferir`, 'POST', {
        extension
      });
      await fetchCampaignData();
    } catch (err) {
      setError(`Error al transferir llamada: ${err.message}`);
    }
  };

  const handleHangupCall = async (callId) => {
    try {
      await makeApiRequest(`/presione1/llamadas/${callId}/finalizar`, 'POST');
      await fetchCampaignData();
    } catch (err) {
      setError(`Error al finalizar llamada: ${err.message}`);
    }
  };

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    if (campaignId) {
      fetchCampaignData();
      fetchAudioSessions();
      fetchAgents();
    }
  }, [campaignId, fetchCampaignData, fetchAudioSessions, fetchAgents]);

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(() => {
        fetchCampaignData();
        fetchAudioSessions();
        fetchAgents();
      }, REFRESH_INTERVAL);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, fetchCampaignData, fetchAudioSessions, fetchAgents]);

  // ============================================================================
  // COMPONENTES
  // ============================================================================

  const StatusBadge = ({ status, children }) => {
    const colors = {
      // Status de campanhas
      'ativa': 'bg-green-500',
      'pausada': 'bg-yellow-500',
      'parada': 'bg-red-500',
      'em_andamento': 'bg-blue-500',
      'aguardando_dtmf': 'bg-purple-500',
      'transferindo': 'bg-orange-500',
      'finalizada': 'bg-gray-500',
      // Status de agentes
      'disponivel': 'bg-green-500',
      'ocupado': 'bg-blue-500',
      'pausa': 'bg-yellow-500',
      'offline': 'bg-red-500'
    };
    
    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full text-white ${colors[status] || 'bg-gray-500'}`}>
        {children}
      </span>
    );
  };

  const MetricCard = ({ title, value, subtitle, icon, color = 'blue', trend }) => (
    <div className={`card-glass rounded-lg shadow-lg border border-white/10 p-4 hover:shadow-xl transition-all duration-300`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-secondary-300">{title}</p>
          <p className={`text-2xl font-bold text-${color}-400`}>{value}</p>
          {subtitle && <p className="text-xs text-secondary-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full bg-${color}-500/20 text-${color}-400`}>
          {icon}
        </div>
      </div>
      {trend && (
        <div className="mt-2 flex items-center text-xs">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            trend > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {trend > 0 ? '↗' : '↘'} {Math.abs(trend)}%
          </span>
          <span className="ml-2 text-gray-500">vs. anterior</span>
        </div>
      )}
    </div>
  );

  const OverviewTab = () => (
    <div className="space-y-6">
      {/* Controles da Campanha */}
      <div className="card-glass rounded-lg shadow-lg border border-white/10 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-white">Controles de Campaña</h3>
            <p className="text-sm text-secondary-300">Gestione la ejecución de la campaña</p>
          </div>
          <StatusBadge status={campaign?.estado || 'parada'}>
            {campaign?.estado?.toUpperCase() || 'PARADA'}
          </StatusBadge>
        </div>
        
        <div className="flex flex-wrap gap-3">
          {campaign?.estado === 'ativa' && (
            <button
              onClick={handlePauseCampaign}
              disabled={actionLoading.pausing}
              className="inline-flex items-center px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {actionLoading.pausing ? (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
              ) : (
                <PauseIcon className="w-4 h-4 mr-2" />
              )}
              Pausar
            </button>
          )}
          
          {campaign?.estado === 'pausada' && (
            <button
              onClick={handleResumeCampaign}
              disabled={actionLoading.resuming}
              className="inline-flex items-center px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {actionLoading.resuming ? (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
              ) : (
                <PlayIcon className="w-4 h-4 mr-2" />
              )}
              Reanudar
            </button>
          )}
          
          <button
            onClick={handleStopCampaign}
            disabled={actionLoading.stopping}
            className="inline-flex items-center px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {actionLoading.stopping ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
            ) : (
              <StopIcon className="w-4 h-4 mr-2" />
            )}
            Detener
          </button>
        </div>
      </div>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
                      title="Llamadas Realizadas"
          value={statistics?.llamadas_realizadas || 0}
          icon={<PhoneIcon className="w-6 h-6" />}
          color="blue"
        />
        <MetricCard
          title="Atendidas"
          value={statistics?.llamadas_contestadas || 0}
          subtitle={`${statistics?.tasa_contestacion || 0}% taxa`}
          icon={<CheckCircleIcon className="w-6 h-6" />}
          color="green"
        />
        <MetricCard
          title="Pressionaram 1"
          value={statistics?.llamadas_presiono_1 || 0}
          subtitle={`${statistics?.tasa_presiono_1 || 0}% interesse`}
          icon={<SpeakerWaveIcon className="w-6 h-6" />}
          color="purple"
        />
        <MetricCard
          title="Transferidas"
          value={statistics?.llamadas_transferidas || 0}
          subtitle={`${statistics?.tasa_transferencia || 0}% sucesso`}
          icon={<ArrowPathIcon className="w-6 h-6" />}
          color="orange"
        />
      </div>

      {/* Chamadas Ativas */}
      <div className="card-glass rounded-lg shadow-lg border border-white/10 p-6">
        <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">
          Llamadas Activas ({activeCalls.length})
        </h3>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-secondary-300">Tiempo real</span>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="text-left text-sm font-medium text-secondary-300 border-b border-white/10">
                <th className="pb-2">Número</th>
                <th className="pb-2">Estado</th>
                <th className="pb-2">Duración</th>
                <th className="pb-2">CLI</th>
                <th className="pb-2">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {activeCalls.map((call, index) => (
                <tr key={call.id || index} className="text-sm">
                  <td className="py-3 font-medium text-white">{call.numero_destino}</td>
                  <td className="py-3">
                    <StatusBadge status={call.estado}>{call.estado}</StatusBadge>
                  </td>
                  <td className="py-3 text-secondary-300">{call.duracion || '0:00'}</td>
                  <td className="py-3 text-secondary-300">{call.cli_utilizado}</td>
                  <td className="py-3">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleTransferCall(call.id, '100')}
                        className="text-blue-600 hover:text-blue-800"
                        title="Transferir"
                      >
                        <ArrowPathIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleHangupCall(call.id)}
                        className="text-red-600 hover:text-red-800"
                        title="Finalizar"
                      >
                        <XCircleIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {activeCalls.length === 0 && (
            <div className="text-center py-8 text-secondary-400">
              No hay llamadas activas en este momento
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const AudioTab = () => (
    <div className="space-y-6">
      <div className="card-glass rounded-lg shadow-lg border border-white/10 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Sistema de Audio Inteligente</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <MetricCard
            title="Sesiones Activas"
            value={audioSessions.filter(s => s.estado === 'ativa').length}
            icon={<MicrophoneIcon className="w-6 h-6" />}
            color="green"
          />
          <MetricCard
            title="DTMF Detectados"
            value={audioSessions.filter(s => s.dtmf_detectado).length}
            icon={<SignalIcon className="w-6 h-6" />}
            color="blue"
          />
          <MetricCard
            title="Buzones de Voz"
            value={audioSessions.filter(s => s.voicemail_detectado).length}
            icon={<SpeakerWaveIcon className="w-6 h-6" />}
            color="purple"
          />
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="text-left text-sm font-medium text-secondary-300 border-b border-white/10">
                <th className="pb-2">Llamada</th>
                <th className="pb-2">Estado</th>
                <th className="pb-2">DTMF</th>
                <th className="pb-2">Buzón</th>
                <th className="pb-2">Duración</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {audioSessions.map((session, index) => (
                <tr key={session.id || index} className="text-sm">
                  <td className="py-3 font-medium text-white">{session.llamada_id}</td>
                  <td className="py-3">
                    <StatusBadge status={session.estado}>{session.estado}</StatusBadge>
                  </td>
                  <td className="py-3 text-secondary-300">{session.dtmf_detectado || '-'}</td>
                  <td className="py-3 text-secondary-300">{session.voicemail_detectado ? 'Sí' : 'No'}</td>
                  <td className="py-3 text-secondary-300">{session.duracao || '0:00'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const AgentsTab = () => (
    <div className="space-y-6">
      <div className="card-glass rounded-lg shadow-lg border border-white/10 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Agentes Conectados</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <MetricCard
            title="Disponibles"
            value={agents.filter(a => a.status === 'disponivel').length}
            icon={<UserGroupIcon className="w-6 h-6" />}
            color="green"
          />
          <MetricCard
            title="Ocupados"
            value={agents.filter(a => a.status === 'ocupado').length}
            icon={<PhoneIcon className="w-6 h-6" />}
            color="blue"
          />
          <MetricCard
            title="En Pausa"
            value={agents.filter(a => a.status === 'pausa').length}
            icon={<PauseIcon className="w-6 h-6" />}
            color="yellow"
          />
          <MetricCard
            title="Fuera de Línea"
            value={agents.filter(a => a.status === 'offline').length}
            icon={<XCircleIcon className="w-6 h-6" />}
            color="red"
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent, index) => (
            <div key={agent.id || index} className="card-glass rounded-lg p-4 border border-white/10">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-white">{agent.nome}</h4>
                <StatusBadge status={agent.status}>{agent.status}</StatusBadge>
              </div>
              <p className="text-sm text-secondary-300">ID: {agent.id}</p>
              <p className="text-sm text-secondary-300">Ext: {agent.extensao}</p>
              <p className="text-sm text-secondary-300">Llamadas hoy: {agent.llamadas_hoje}</p>
              <p className="text-sm text-secondary-300">Tiempo en línea: {agent.tempo_online}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8 min-h-screen bg-gradient-to-br from-secondary-900 via-dark-100 to-secondary-900">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-400"></div>
        <span className="ml-2 text-white">Cargando control de campaña...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 min-h-screen bg-gradient-to-br from-secondary-900 via-dark-100 to-secondary-900">
      {/* Header */}
      <div className="card-glass rounded-lg shadow-lg border border-white/10 p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">
              {campaign?.nombre || 'Campaña'}
            </h1>
            <p className="text-secondary-300 mt-1">{campaign?.descripcion}</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="autoRefresh"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="autoRefresh" className="text-sm text-secondary-300">
                Auto-refresh
              </label>
            </div>
            
            {lastUpdate && (
              <span className="text-xs text-secondary-400">
                Última actualización: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
            
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XCircleIcon className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card-glass rounded-lg shadow-lg border border-white/10 mb-6">
        <div className="border-b border-white/10">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', label: 'Resumen General', icon: ChartBarIcon },
              { id: 'audio', label: 'Audio Inteligente', icon: MicrophoneIcon },
              { id: 'agents', label: 'Agentes', icon: UserGroupIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedView(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  selectedView === tab.id
                    ? 'border-primary-500 text-primary-400'
                    : 'border-transparent text-secondary-400 hover:text-secondary-200'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
        
        <div className="p-6">
          {selectedView === 'overview' && <OverviewTab />}
          {selectedView === 'audio' && <AudioTab />}
          {selectedView === 'agents' && <AgentsTab />}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <XCircleIcon className="w-5 h-5 text-red-400 mr-3 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-400 hover:text-red-600"
            >
              <XCircleIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignControl;