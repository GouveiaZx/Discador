import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api.js';

/**
 * Componente de Métrica de Campanha Profissional
 */
const CampaignMetricCard = ({ title, value, subtitle, icon, color = 'primary', loading = false }) => {
  const colorClasses = {
    primary: 'border-primary-500/30 bg-primary-500/10',
    success: 'border-success-500/30 bg-success-500/10',
    warning: 'border-warning-500/30 bg-warning-500/10',
    info: 'border-info-500/30 bg-info-500/10'
  };

  return (
    <div className={`card-glass p-6 border ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-4">
        <span className="text-2xl">{icon}</span>
        {loading && (
          <div className="animate-spin rounded-full h-5 w-5 border-2 border-primary-500 border-t-transparent"></div>
        )}
      </div>
      <div className="space-y-2">
        <h3 className="text-2xl font-bold text-white">
          {loading ? '--' : value}
        </h3>
        <div className="space-y-1">
          <p className="font-medium text-white">{title}</p>
          <p className="text-xs text-secondary-400">{subtitle}</p>
        </div>
      </div>
    </div>
  );
};

// Função de debug para testar no console do navegador
window.testCreateCampaign = async () => {
  try {
    console.log('🧪 Testando criação de campanha...');
    const testData = {
      name: 'Test Campaign Debug',
      description: 'Teste de debug',
      cli_number: '1155512345',
      max_concurrent_calls: 5,
      max_attempts: 3,
      retry_interval: 300
    };
    
    console.log('📤 Enviando dados:', testData);
    
    // Importar a função makeApiRequest do config
    const { makeApiRequest } = await import('../config/api.js');
    const response = await makeApiRequest('/campaigns', 'POST', testData);
    
    console.log('📥 Resposta recebida:', response);
    console.log('🔍 Tipo da resposta:', typeof response);
    console.log('🔍 Chaves da resposta:', Object.keys(response || {}));
    console.log('🔍 Tem ID?', !!(response && response.id));
    console.log('🔍 Valor do ID:', response?.id);
    
    return response;
  } catch (error) {
    console.error('❌ Erro no teste:', error);
    return null;
  }
};

/**
 * Componente para gestão de campanhas profissional
 */
function GestionCampanhas({ onOpenCampaignControl }) {
  const [campanhas, setCampanhas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCampanha, setEditingCampanha] = useState(null);
  const [actionLoading, setActionLoading] = useState({
    creating: false,
    updating: false,
    deleting: false
  });
  const [metrics, setMetrics] = useState({
    total: 0,
    active: 0,
    paused: 0,
    completed: 0
  });
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    cli_number: '',
    max_concurrent_calls: 5,
    max_attempts: 3,
    retry_interval: 300
  });

  useEffect(() => {
    fetchCampanhas();
  }, []);

  const fetchCampanhas = async () => {
    try {
      setLoading(true);
      setError(''); // Limpar erro anterior
      console.log('📋 Buscando lista de campanhas presione1...');
      const response = await makeApiRequest('/presione1/campanhas');
      console.log('📋 Resposta da listagem de campanhas presione1:', response);
      
      if (response && Array.isArray(response)) {
        // Buscar dados das campanhas principais para cada campanha presione1
        console.log('🔗 Buscando dados das campanhas principais...');
        const campanhasWithMainData = await Promise.all(
          response.map(async (campanha) => {
            try {
              // Buscar dados da campanha principal
              const mainCampaignResponse = await makeApiRequest('/campaigns');
              const mainCampaigns = mainCampaignResponse?.campaigns || [];
              const mainCampaign = mainCampaigns.find(c => c.id === campanha.campaign_id);
              
              return {
                id: campanha.id,
                name: campanha.nombre,
                description: campanha.descripcion,
                status: campanha.activa ? 'active' : (campanha.pausada ? 'paused' : 'draft'),
                // Dados da campanha principal (contatos e CLI)
                cli_number: mainCampaign?.cli_number || 'N/A',
                contacts_total: mainCampaign?.contacts_total || 0,
                created_at: campanha.fecha_creacion,
                updated_at: campanha.fecha_actualizacion,
                // Dados específicos presione1
                campaign_id: campanha.campaign_id,
                activa: campanha.activa,
                pausada: campanha.pausada,
                llamadas_simultaneas: campanha.llamadas_simultaneas,
                tiempo_entre_llamadas: campanha.tiempo_entre_llamadas
              };
            } catch (err) {
              console.error(`Erro ao buscar dados da campanha principal ${campanha.campaign_id}:`, err);
              // Retornar dados básicos em caso de erro
              return {
                id: campanha.id,
                name: campanha.nombre,
                description: campanha.descripcion,
                status: campanha.activa ? 'active' : (campanha.pausada ? 'paused' : 'draft'),
                cli_number: 'N/A',
                contacts_total: 0,
                created_at: campanha.fecha_creacion,
                updated_at: campanha.fecha_actualizacion,
                campaign_id: campanha.campaign_id,
                activa: campanha.activa,
                pausada: campanha.pausada,
                llamadas_simultaneas: campanha.llamadas_simultaneas,
                tiempo_entre_llamadas: campanha.tiempo_entre_llamadas
              };
            }
          })
        );
        
        console.log('✅ Campanhas com dados principais:', campanhasWithMainData);
        setCampanhas(campanhasWithMainData);
        updateMetrics(campanhasWithMainData);
        setError(''); // Limpar qualquer erro anterior
      } else {
        setError('Error al cargar campañas: respuesta inválida');
        console.error('Resposta inválida:', response);
      }
    } catch (err) {
      console.error('Erro ao carregar campanhas:', err);
      setError('Error de conexión con el servidor');
    } finally {
      setLoading(false);
    }
  };

  const updateMetrics = (campaigns) => {
    const total = campaigns.length;
    const active = campaigns.filter(c => c.status === 'active').length;
    const paused = campaigns.filter(c => c.status === 'paused').length;
    const completed = campaigns.filter(c => c.status === 'completed').length;
    setMetrics({ total, active, paused, completed });
  };

  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    try {
      setActionLoading({ ...actionLoading, creating: true });
      setError('');
      setSuccess('');
      
      // Validar campos obrigatórios
      if (!formData.name.trim()) {
        setError('El nombre de la campaña es obligatorio');
        return;
      }
      
      console.log('🚀 Dados para criar campanha:', formData);
      const createResponse = await makeApiRequest('/campaigns', 'POST', formData);
      console.log('✅ Resposta da API de criação:', createResponse);
      
      // A API retorna um objeto com id, name, message etc. quando cria com sucesso
      console.log('🔍 Verificando resposta:', {
        hasResponse: !!createResponse,
        hasId: !!(createResponse && createResponse.id),
        id: createResponse?.id,
        responseType: typeof createResponse,
        responseKeys: createResponse ? Object.keys(createResponse) : 'N/A'
      });
      
      // TESTE: Verificar especificamente se o ID existe e é válido
      if (createResponse && typeof createResponse === 'object' && createResponse.id) {
        console.log('✅ Condição atendida! ID encontrado:', createResponse.id);
        setSuccess('Campaña creada con éxito');
        
        // Recarregar a lista após a criação
        console.log('🔄 Recarregando lista de campanhas...');
        await fetchCampanhas();
        handleCloseModal();
        
        // Limpar mensagem de sucesso após 5 segundos
        setTimeout(() => setSuccess(''), 5000);
      } else {
        console.error('❌ Condição NÃO atendida!');
        console.error('- createResponse:', createResponse);
        console.error('- typeof createResponse:', typeof createResponse);
        console.error('- createResponse.id:', createResponse?.id);
        console.error('- !!createResponse:', !!createResponse);
        console.error('- !!createResponse.id:', !!(createResponse && createResponse.id));
        setError('Error al crear campaña: respuesta inválida del servidor');
      }
    } catch (err) {
      console.error('Erro ao criar campanha:', err);
      setError(`Error al crear campaña: ${err.message || 'Error desconocido'}`);
    } finally {
      setActionLoading({ ...actionLoading, creating: false });
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingCampanha(null);
    setError('');
    setSuccess('');
    setFormData({
      name: '',
      description: '',
      cli_number: '',
      max_concurrent_calls: 5,
      max_attempts: 3,
      retry_interval: 300
    });
  };

  const handleEditCampaign = (campanha) => {
    setEditingCampanha(campanha);
    setFormData({
      name: campanha.name || '',
      description: campanha.description || '',
      cli_number: campanha.cli_number || '',
      max_concurrent_calls: campanha.max_concurrent_calls || 5,
      max_attempts: campanha.max_attempts || 3,
      retry_interval: campanha.retry_interval || 300
    });
    setShowModal(true);
  };

  const handleUpdateCampaign = async (e) => {
    e.preventDefault();
    if (!editingCampanha) return;

    try {
      setActionLoading({ ...actionLoading, updating: true });
      setError('');
      setSuccess('');
      
      console.log('🔄 Dados para atualizar campanha:', formData);
      const updateResponse = await makeApiRequest(`/campaigns/${editingCampanha.id}`, 'PUT', formData);
      console.log('🔄 Resposta da atualização:', updateResponse);
      
      // A API retorna um objeto com id, name, message etc. quando atualiza com sucesso
      if (updateResponse && updateResponse.id) {
        setSuccess('Campaña actualizada con éxito');
        await fetchCampanhas();
        handleCloseModal();
        
        // Limpar mensagem de sucesso após 5 segundos
        setTimeout(() => setSuccess(''), 5000);
      } else {
        setError('Error al actualizar campaña');
      }
    } catch (err) {
      console.error('Erro ao atualizar campanha:', err);
      setError(`Error al actualizar campaña: ${err.message || 'Error desconocido'}`);
    } finally {
      setActionLoading({ ...actionLoading, updating: false });
    }
  };

  const handleDeleteCampaign = async (campaignId) => {
    if (!confirm('¿Estás seguro de que deseas eliminar esta campaña?')) {
      return;
    }

    try {
      setActionLoading({ ...actionLoading, [`deleting_${campaignId}`]: true });
      setError('');
      setSuccess('');
      
      const deleteResponse = await makeApiRequest(`/campaigns/${campaignId}`, 'DELETE');
      console.log('🗑️ Resposta da exclusão:', deleteResponse);
      
      // A API retorna um objeto com message quando deleta com sucesso
      if (deleteResponse && (deleteResponse.mensaje || deleteResponse.message)) {
        setSuccess(deleteResponse.mensaje || 'Campaña eliminada con éxito');
        await fetchCampanhas();
        
        // Limpar mensagem de sucesso após 5 segundos
        setTimeout(() => setSuccess(''), 5000);
      } else {
        setError('Error al eliminar campaña');
      }
    } catch (err) {
      console.error('Erro ao deletar campanha:', err);
      setError(`Error al eliminar campaña: ${err.message || 'Error desconocido'}`);
    } finally {
      setActionLoading({ ...actionLoading, [`deleting_${campaignId}`]: false });
    }
  };

  const handleStartCampaign = async (campaignId) => {
    try {
      setError('');
      setSuccess('');
      setActionLoading({ ...actionLoading, [`starting_${campaignId}`]: true });
      
      console.log('🚀 Iniciando campanha:', campaignId);
      
      // Endpoint para iniciar campanha Presione 1 - FIX: usuario_id como string
      const startResponse = await makeApiRequest(`/presione1/campanhas/${campaignId}/iniciar`, 'POST', {
        usuario_id: "1" // FIX: Mudado de número para string
      });
      
      console.log('✅ Resposta de iniciar:', startResponse);
      
      if (startResponse && (startResponse.mensaje || startResponse.message || startResponse.success)) {
        setSuccess(startResponse.mensaje || 'Campaña iniciada con éxito');
        await fetchCampanhas();
        
        // Limpar mensagem de sucesso após 5 segundos
        setTimeout(() => setSuccess(''), 5000);
      } else {
        setError('Error al iniciar campaña');
      }
    } catch (err) {
      console.error('Erro ao iniciar campanha:', err);
      setError(`Error al iniciar campaña: ${err.message || 'Error desconocido'}`);
    } finally {
      setActionLoading({ ...actionLoading, [`starting_${campaignId}`]: false });
    }
  };

  const handlePauseCampaign = async (campaignId) => {
    try {
      setActionLoading(prev => ({ ...prev, [`pausing_${campaignId}`]: true }));
      
      const pauseResponse = await makeApiRequest(`/presione1/campanhas/${campaignId}/pausar`, 'POST', {
        campana_id: campaignId,
        pausar: true,
        usuario_id: 'frontend_user',
        motivo: 'Pausado via interface'
      });
      
      console.log('✅ Resposta de pausar:', pauseResponse);
      
      if (pauseResponse && (pauseResponse.mensaje || pauseResponse.message)) {
        setSuccess(pauseResponse.mensaje || pauseResponse.message || 'Campaña pausada con éxito');
        fetchCampanhas();
      } else {
        setError('Error al pausar campaña');
      }
    } catch (err) {
      console.error('Erro ao pausar campanha:', err);
      setError(`Error al pausar campaña: ${err.message || 'Error desconocido'}`);
    } finally {
      setActionLoading(prev => ({ ...prev, [`pausing_${campaignId}`]: false }));
    }
  };

  const handleResumeCampaign = async (campaignId) => {
    try {
      setActionLoading(prev => ({ ...prev, [`resuming_${campaignId}`]: true }));
      
      const resumeResponse = await makeApiRequest(`/presione1/campanhas/${campaignId}/pausar`, 'POST', {
        campana_id: campaignId,
        pausar: false,
        usuario_id: 'frontend_user',
        motivo: 'Retomado via interface'
      });
      
      console.log('✅ Resposta de retomar:', resumeResponse);
      
      if (resumeResponse && (resumeResponse.mensaje || resumeResponse.message)) {
        setSuccess(resumeResponse.mensaje || resumeResponse.message || 'Campaña retomada con éxito');
        fetchCampanhas();
      } else {
        setError('Error al retomar campaña');
      }
    } catch (err) {
      console.error('Erro ao retomar campanha:', err);
      setError(`Error al retomar campaña: ${err.message || 'Error desconocido'}`);
    } finally {
      setActionLoading(prev => ({ ...prev, [`resuming_${campaignId}`]: false }));
    }
  };

  const handleStopCampaign = async (campaignId) => {
    try {
      setActionLoading(prev => ({ ...prev, [`stopping_${campaignId}`]: true }));
      
      const stopResponse = await makeApiRequest(`/presione1/campanhas/${campaignId}/parar`, 'POST', {
        campana_id: campaignId,
        usuario_id: 'frontend_user',
        motivo: 'Parado via interface'
      });
      
      console.log('✅ Resposta de parar:', stopResponse);
      
      if (stopResponse && (stopResponse.mensaje || stopResponse.message)) {
        setSuccess(stopResponse.mensaje || stopResponse.message || 'Campaña parada con éxito');
        fetchCampanhas();
      } else {
        setError('Error al parar campaña');
      }
    } catch (err) {
      console.error('Erro ao parar campanha:', err);
      setError(`Error al parar campaña: ${err.message || 'Error desconocido'}`);
    } finally {
      setActionLoading(prev => ({ ...prev, [`stopping_${campaignId}`]: false }));
    }
  };

  const renderStatusBadge = (status) => {
    const statusConfig = {
      active: { color: 'text-emerald-400', bg: 'bg-emerald-500/20', label: 'Activa' },
      paused: { color: 'text-amber-400', bg: 'bg-amber-500/20', label: 'Pausada' },
      draft: { color: 'text-slate-400', bg: 'bg-slate-500/20', label: 'Borrador' },
      completed: { color: 'text-blue-400', bg: 'bg-blue-500/20', label: 'Completada' }
    };

    const config = statusConfig[status] || statusConfig.draft;

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('es-AR');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-primary-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header Principal */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center space-y-4 lg:space-y-0">
          <div className="space-y-2">
            <h1 className="text-3xl lg:text-4xl font-bold text-gradient-primary">
              Gestión de Campañas
            </h1>
            <p className="text-secondary-400 text-sm lg:text-base">
              Administra tus campañas de llamadas con control total
            </p>
          </div>
          
          <button
            onClick={() => setShowModal(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
            </svg>
            <span>Nueva Campaña</span>
          </button>
        </div>

        {/* Métricas das Campanhas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <CampaignMetricCard
            title="Total"
            value={metrics.total}
            subtitle="Campañas registradas"
            icon="📊"
            color="primary"
            loading={loading}
          />
          
          <CampaignMetricCard
            title="Activas"
            value={metrics.active}
            subtitle="En ejecución"
            icon="🚀"
            color="success"
            loading={loading}
          />
          
          <CampaignMetricCard
            title="Pausadas"
            value={metrics.paused}
            subtitle="Temporalmente detenidas"
            icon="⏸️"
            color="warning"
            loading={loading}
          />
          
          <CampaignMetricCard
            title="Completadas"
            value={metrics.completed}
            subtitle="Campañas finalizadas"
            icon="✅"
            color="info"
            loading={loading}
          />
        </div>

        {/* Mensajes de éxito/error */}
        {success && (
          <div className="bg-success-500/20 border border-success-500/50 text-success-200 px-6 py-4 rounded-xl text-sm backdrop-blur-sm animate-fade-in">
            <div className="flex items-center space-x-3">
              <svg className="w-5 h-5 text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span className="font-medium">{success}</span>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-error-500/20 border border-error-500/50 text-error-200 px-6 py-4 rounded-xl text-sm backdrop-blur-sm animate-fade-in">
            <div className="flex items-center space-x-3">
              <svg className="w-5 h-5 text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Lista de campanhas */}
        <div className="card-glass p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Listado de Campañas</h3>
            <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-primary-500/20 border border-primary-500/30">
              <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse"></div>
              <span className="text-xs text-primary-400 font-medium">LIVE</span>
            </div>
          </div>
          
          {campanhas.length === 0 ? (
            <div className="text-center py-16">
              <div className="text-6xl mb-4 opacity-50">📋</div>
              <h3 className="text-lg font-medium text-white mb-2">No hay campañas creadas</h3>
              <p className="text-secondary-400 mb-6">Crea tu primera campaña para comenzar a gestionar llamadas</p>
              <button
                onClick={() => setShowModal(true)}
                className="btn-primary"
              >
                Crear Primera Campaña
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto custom-scrollbar">
              <table className="table-modern">
                <thead>
                  <tr>
                    <th>Campaña</th>
                    <th>Estado</th>
                    <th>CLI</th>
                    <th>Contactos</th>
                    <th>Creada</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {campanhas.map((campanha) => (
                    <tr key={campanha.id} className="group">
                      <td>
                        <div className="space-y-1">
                          <div className="font-medium text-white group-hover:text-primary-300 transition-colors">
                            {campanha.name}
                          </div>
                          {campanha.description && (
                            <div className="text-xs text-secondary-400 max-w-xs truncate">
                              {campanha.description}
                            </div>
                          )}
                        </div>
                      </td>
                      <td>
                        {renderStatusBadge(campanha.status)}
                      </td>
                      <td>
                        <span className="font-mono text-sm text-secondary-300">
                          {campanha.cli_number || 'N/A'}
                        </span>
                      </td>
                      <td>
                        <div className="text-white font-medium">
                          {campanha.contacts_total || 0}
                        </div>
                      </td>
                      <td>
                        <span className="text-xs text-secondary-400">
                          {formatDate(campanha.created_at)}
                        </span>
                      </td>
                      <td>
                        <div className="flex items-center space-x-2">
                          {/* Botões de ação */}
                          {campanha.status === 'draft' && (
                            <button 
                              onClick={() => handleStartCampaign(campanha.id)}
                              className="relative inline-flex items-center justify-center px-4 py-2 text-xs font-medium text-white bg-emerald-500 hover:bg-emerald-600 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-emerald-500/25 overflow-hidden"
                              disabled={actionLoading[`starting_${campanha.id}`]}
                              title="Iniciar campanha"
                            >
                              <div className="flex items-center space-x-2">
                                {actionLoading[`starting_${campanha.id}`] ? (
                                  <>
                                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                                      <span className="text-sm font-semibold">Iniciando...</span>
                                  </>
                                ) : (
                                  <>
                                    <div className="relative">
                                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4"/>
                                      </svg>
                                    </div>
                                    <span className="text-sm font-semibold">Iniciar</span>
                                  </>
                                )}
                              </div>
                              
                              {/* Animação de pulse no estado loading */}
                              {actionLoading[`starting_${campanha.id}`] && (
                                <div className="absolute inset-0 rounded-lg bg-emerald-400/30 animate-pulse"></div>
                              )}
                            </button>
                          )}
                          
                          {/* Botões para campanha ativa */}
                          {campanha.status === 'active' && (
                            <>
                              <button 
                                onClick={() => handlePauseCampaign(campanha.id)}
                                className="relative inline-flex items-center justify-center px-4 py-2 text-xs font-medium text-white bg-amber-500 hover:bg-amber-600 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-amber-500/25"
                                disabled={actionLoading[`pausing_${campanha.id}`]}
                                title="Pausar campanha"
                              >
                                <div className="flex items-center space-x-2">
                                  {actionLoading[`pausing_${campanha.id}`] ? (
                                    <>
                                      <div className="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent"></div>
                                      <span className="text-xs font-semibold">Pausando...</span>
                                    </>
                                  ) : (
                                    <>
                                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                                      </svg>
                                      <span className="text-xs font-semibold">Pausar</span>
                                    </>
                                  )}
                                </div>
                                
                                {/* Animação de pulse no estado loading */}
                                {actionLoading[`pausing_${campanha.id}`] && (
                                  <div className="absolute inset-0 rounded-lg bg-amber-400/30 animate-pulse"></div>
                                )}
                              </button>
                              
                              <button 
                                onClick={() => onOpenCampaignControl && onOpenCampaignControl(campanha.id)}
                                className="relative inline-flex items-center justify-center px-4 py-2 text-xs font-medium text-white bg-purple-500 hover:bg-purple-600 rounded-lg transition-all duration-200 shadow-lg hover:shadow-purple-500/25"
                                title="Controlar campanha"
                              >
                                <div className="flex items-center space-x-2">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                                  </svg>
                                  <span className="text-xs font-semibold">Controlar</span>
                                </div>
                              </button>
                              
                              <button 
                                onClick={() => handleStopCampaign(campanha.id)}
                                className="relative inline-flex items-center justify-center px-4 py-2 text-xs font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-red-500/25"
                                disabled={actionLoading[`stopping_${campanha.id}`]}
                                title="Parar campanha"
                              >
                                <div className="flex items-center space-x-2">
                                  {actionLoading[`stopping_${campanha.id}`] ? (
                                    <>
                                      <div className="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent"></div>
                                      <span className="text-xs font-semibold">Parando...</span>
                                    </>
                                  ) : (
                                    <>
                                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M6 6h12v12H6z"/>
                                      </svg>
                                      <span className="text-xs font-semibold">Parar</span>
                                    </>
                                  )}
                                </div>
                                
                                {/* Animação de pulse no estado loading */}
                                {actionLoading[`stopping_${campanha.id}`] && (
                                  <div className="absolute inset-0 rounded-lg bg-red-400/30 animate-pulse"></div>
                                )}
                              </button>
                            </>
                          )}
                          
                          {/* Botão para campanha pausada */}
                          {campanha.status === 'paused' && (
                            <button 
                              onClick={() => handleResumeCampaign(campanha.id)}
                              className="relative inline-flex items-center justify-center px-4 py-2 text-xs font-medium text-white bg-emerald-500 hover:bg-emerald-600 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-emerald-500/25"
                              disabled={actionLoading[`resuming_${campanha.id}`]}
                              title="Retomar campanha"
                            >
                              <div className="flex items-center space-x-2">
                                {actionLoading[`resuming_${campanha.id}`] ? (
                                  <>
                                    <div className="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent"></div>
                                    <span className="text-xs font-semibold">Retomando...</span>
                                  </>
                                ) : (
                                  <>
                                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                      <path d="M8 5v14l11-7z"/>
                                    </svg>
                                    <span className="text-xs font-semibold">Retomar</span>
                                  </>
                                )}
                              </div>
                              
                              {/* Animação de pulse no estado loading */}
                              {actionLoading[`resuming_${campanha.id}`] && (
                                <div className="absolute inset-0 rounded-lg bg-emerald-400/30 animate-pulse"></div>
                              )}
                            </button>
                          )}
                          
                          <button 
                            onClick={() => handleEditCampaign(campanha)}
                            className="relative inline-flex items-center justify-center px-3 py-2 text-xs font-medium text-white bg-blue-500 hover:bg-blue-600 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-blue-500/25"
                            disabled={actionLoading.updating}
                            title="Editar campanha"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                            </svg>
                          </button>
                          
                          <button 
                            onClick={() => handleDeleteCampaign(campanha.id)}
                            className="relative inline-flex items-center justify-center px-3 py-2 text-xs font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-red-500/25"
                            disabled={actionLoading[`deleting_${campanha.id}`]}
                            title="Eliminar campanha"
                          >
                            {actionLoading[`deleting_${campanha.id}`] ? (
                              <div className="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent"></div>
                            ) : (
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                              </svg>
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal para criar campaña */}
        {showModal && (
          <div className="modal-backdrop flex items-center justify-center p-4 z-50">
            <div className="card-glass max-w-md w-full p-6 animate-fade-in-up">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">
                  {editingCampanha ? 'Editar Campaña' : 'Nueva Campaña'}
                </h3>
                <button
                  onClick={handleCloseModal}
                  className="text-secondary-400 hover:text-white transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>

              <form onSubmit={editingCampanha ? handleUpdateCampaign : handleCreateCampaign} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-300 mb-2">
                    Nombre de la Campaña
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="input-modern"
                    placeholder="Ingresa el nombre de la campaña"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-300 mb-2">
                    Descripción
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="input-modern resize-none"
                    rows="3"
                    placeholder="Descripción de la campaña (opcional)"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-300 mb-2">
                    Número CLI (Origen)
                  </label>
                  <input
                    type="text"
                    value={formData.cli_number}
                    onChange={(e) => setFormData({ ...formData, cli_number: e.target.value })}
                    className="input-modern"
                    placeholder="+5511999999999"
                    required
                  />
                  <p className="text-xs text-secondary-400 mt-1">
                    Número que aparecerá como origen de las llamadas
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary-300 mb-2">
                      Llamadas Simultáneas
                    </label>
                    <input
                      type="number"
                      value={formData.max_concurrent_calls}
                      onChange={(e) => setFormData({ ...formData, max_concurrent_calls: parseInt(e.target.value) })}
                      className="input-modern"
                      min="1"
                      max="100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-secondary-300 mb-2">
                      Intentos Máximos
                    </label>
                    <input
                      type="number"
                      value={formData.max_attempts}
                      onChange={(e) => setFormData({ ...formData, max_attempts: parseInt(e.target.value) })}
                      className="input-modern"
                      min="1"
                      max="10"
                    />
                  </div>
                </div>

                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="btn-secondary flex-1"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={editingCampanha ? actionLoading.updating : actionLoading.creating}
                    className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {editingCampanha ? (
                      actionLoading.updating ? (
                        <div className="flex items-center space-x-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                          <span>Actualizando...</span>
                        </div>
                      ) : (
                        'Actualizar Campaña'
                      )
                    ) : (
                      actionLoading.creating ? (
                        <div className="flex items-center space-x-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                          <span>Creando...</span>
                        </div>
                      ) : (
                        'Crear Campaña'
                      )
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default GestionCampanhas; 