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

/**
 * Componente para gestão de campanhas profissional
 */
function GestionCampanhas() {
  const [campanhas, setCampanhas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCampanha, setEditingCampanha] = useState(null);
  const [actionLoading, setActionLoading] = useState({});
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
      const response = await makeApiRequest('/campaigns');
      if (response.success) {
        setCampanhas(response.campaigns || []);
        updateMetrics(response.campaigns || []);
      } else {
        setError('Error al cargar campañas');
      }
    } catch (err) {
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
      setLoading(true);
      const response = await makeApiRequest('/campaigns', 'POST', formData);
      if (response.message) {
        setSuccess('Campaña creada con éxito');
        fetchCampanhas();
        handleCloseModal();
      } else {
        setError('Error al crear campaña');
      }
    } catch (err) {
      setError('Error al crear campaña');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingCampanha(null);
    setFormData({
      name: '',
      description: '',
      cli_number: '',
      max_concurrent_calls: 5,
      max_attempts: 3,
      retry_interval: 300
    });
  };

  const renderStatusBadge = (status) => {
    const statusConfig = {
      active: { color: 'text-success-400', bg: 'bg-success-500/20', label: 'Activa' },
      paused: { color: 'text-warning-400', bg: 'bg-warning-500/20', label: 'Pausada' },
      completed: { color: 'text-info-400', bg: 'bg-info-500/20', label: 'Completada' },
      draft: { color: 'text-secondary-400', bg: 'bg-secondary-500/20', label: 'Borrador' }
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
                          <button className="btn-sm btn-primary">
                            Editar
                          </button>
                          <button className="btn-sm btn-danger">
                            Eliminar
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
                  Nueva Campaña
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

              <form onSubmit={handleCreateCampaign} className="space-y-4">
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
                    className="btn-primary flex-1"
                  >
                    Crear Campaña
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