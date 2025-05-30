import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config/api';

/**
 * Componente para gestão de campanhas
 * Lista, cria e edita campanhas do sistema
 */
function GestionCampanhas() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState(null);

  // Form data para nova campanha
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    cli_number: '',
    max_concurrent_calls: 5,
    start_time: '09:00',
    end_time: '18:00',
    timezone: 'America/Argentina/Buenos_Aires'
  });

  // Carregar campanhas ao inicializar
  useEffect(() => {
    fetchCampaigns();
  }, []);

  /**
   * Buscar campanhas da API
   */
  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/campaigns`);
      if (!response.ok) throw new Error('Erro ao carregar campanhas');
      
      const data = await response.json();
      setCampaigns(data.campaigns || []);
    } catch (err) {
      setError('Erro ao carregar campanhas: ' + err.message);
      console.error('Erro:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Criar nova campanha
   */
  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/campaigns`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error('Erro ao criar campanha');
      
      const newCampaign = await response.json();
      setCampaigns([...campaigns, newCampaign]);
      
      // Reset form
      setFormData({
        name: '',
        description: '',
        cli_number: '',
        max_concurrent_calls: 5,
        start_time: '09:00',
        end_time: '18:00',
        timezone: 'America/Argentina/Buenos_Aires'
      });
      setShowCreateForm(false);
      
    } catch (err) {
      setError('Erro ao criar campanha: ' + err.message);
    }
  };

  /**
   * Render status badge da campanha
   */
  const renderStatusBadge = (status) => {
    const statusClasses = {
      'active': 'bg-green-600 text-white',
      'paused': 'bg-yellow-600 text-white', 
      'draft': 'bg-gray-600 text-white',
      'completed': 'bg-blue-600 text-white'
    };

    const statusLabels = {
      'active': 'Activa',
      'paused': 'Pausada',
      'draft': 'Borrador', 
      'completed': 'Completada'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusClasses[status] || 'bg-gray-500 text-white'}`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  /**
   * Formatar data
   */
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-AR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-6">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
          <span className="ml-3 text-gray-400">Cargando campanhas...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header con botão para criar campanha */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">Gestión de Campañas</h2>
          <p className="text-gray-400 mt-1">Administrá tus campañas de llamadas</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
        >
          + Nueva Campaña
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Lista de campanhas */}
      <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        {campaigns.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg">No hay campañas creadas</div>
            <p className="text-gray-500 mt-2">Creá tu primera campaña para comenzar</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Campaña
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    CLI
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Contactos
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Éxito
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Creada
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {campaigns.map((campaign) => (
                  <tr key={campaign.id} className="hover:bg-gray-700">
                    <td className="px-4 py-4">
                      <div>
                        <div className="text-sm font-medium text-white">
                          {campaign.name}
                        </div>
                        {campaign.description && (
                          <div className="text-sm text-gray-400">
                            {campaign.description}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      {renderStatusBadge(campaign.status)}
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-300">
                      {campaign.cli_number}
                    </td>
                    <td className="px-4 py-4">
                      <div className="text-sm">
                        <div className="text-white">{campaign.total_contacts || 0}</div>
                        <div className="text-gray-400 text-xs">
                          {campaign.contacted_count || 0} contactados
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="text-sm">
                        <div className="text-green-400 font-semibold">
                          {campaign.success_count || 0}
                        </div>
                        <div className="text-gray-400 text-xs">
                          {campaign.total_contacts > 0 
                            ? `${Math.round(((campaign.success_count || 0) / campaign.total_contacts) * 100)}%`
                            : '0%'
                          }
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-400">
                      {formatDate(campaign.created_at)}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex space-x-2">
                        <button 
                          className="text-blue-400 hover:text-blue-300 text-sm"
                          onClick={() => setEditingCampaign(campaign)}
                        >
                          Editar
                        </button>
                        <button className="text-green-400 hover:text-green-300 text-sm">
                          Iniciar
                        </button>
                        <button className="text-yellow-400 hover:text-yellow-300 text-sm">
                          Pausar
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

      {/* Modal para criar nova campanha */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md max-h-screen overflow-y-auto">
            <h3 className="text-lg font-semibold text-white mb-4">Nueva Campaña</h3>
            
            <form onSubmit={handleCreateCampaign} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Nombre *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
                  placeholder="Ej: Campaña Enero 2025"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Descripción
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
                  rows="3"
                  placeholder="Descripción de la campaña..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Número CLI *
                </label>
                <input
                  type="text"
                  required
                  value={formData.cli_number}
                  onChange={(e) => setFormData({...formData, cli_number: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
                  placeholder="+54 11 4567-8900"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Llamadas concurrentes
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={formData.max_concurrent_calls}
                  onChange={(e) => setFormData({...formData, max_concurrent_calls: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Hora inicio
                  </label>
                  <input
                    type="time"
                    value={formData.start_time}
                    onChange={(e) => setFormData({...formData, start_time: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Hora fin
                  </label>
                  <input
                    type="time"
                    value={formData.end_time}
                    onChange={(e) => setFormData({...formData, end_time: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded font-semibold transition-colors"
                >
                  Crear Campaña
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded font-semibold transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default GestionCampanhas; 