import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api.js';

/**
 * Componente para gestão de campanhas
 * Lista, cria e edita campanhas do sistema
 */
function GestionCampanhas() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState(null);

  // Form data para nova campanha
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'active',
    max_simultaneous_calls: 5,
    retry_attempts: 3,
    retry_delay: 300
  });

  // Estados para métricas
  const [metrics, setMetrics] = useState({
    total: 0,
    active: 0,
    paused: 0,
    completed: 0
  });

  // Carregar campanhas ao montar o componente
  useEffect(() => {
    fetchCampaigns();
  }, []);

  /**
   * Buscar campanhas da API
   */
  const fetchCampaigns = async () => {
    setLoading(true);
    try {
      const data = await makeApiRequest('/campaigns', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      setCampaigns(data.campaigns || []);
      updateMetrics(data.campaigns || []);
    } catch (err) {
      if (err.message.includes('Endpoint not implemented')) {
        console.info('ℹ️ Using mock campaigns data (backend not available)');
        
        // Dados mock de campanhas
        const mockCampaigns = [
          {
            id: 1,
            name: 'Campanha Vendas Q1',
            description: 'Campanha de vendas para o primeiro trimestre',
            status: 'active',
            max_simultaneous_calls: 8,
            retry_attempts: 3,
            retry_delay: 300,
            contacts_total: 1500,
            contacts_called: Math.floor(Math.random() * 500) + 400,
            contacts_remaining: 0,
            created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 2,
            name: 'Seguimiento Clientes',
            description: 'Seguimiento de clientes existentes',
            status: 'active',
            max_simultaneous_calls: 5,
            retry_attempts: 2,
            retry_delay: 600,
            contacts_total: 800,
            contacts_called: Math.floor(Math.random() * 300) + 200,
            contacts_remaining: 0,
            created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 3,
            name: 'Promoción Especial',
            description: 'Campanha promocional de produtos especiais',
            status: Math.random() > 0.5 ? 'active' : 'paused',
            max_simultaneous_calls: 10,
            retry_attempts: 4,
            retry_delay: 180,
            contacts_total: 2000,
            contacts_called: Math.floor(Math.random() * 800) + 600,
            contacts_remaining: 0,
            created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date().toISOString()
          }
        ];

        // Calcular contacts_remaining
        mockCampaigns.forEach(campaign => {
          campaign.contacts_remaining = campaign.contacts_total - campaign.contacts_called;
        });

        setCampaigns(mockCampaigns);
        updateMetrics(mockCampaigns);
      } else {
        setError('Erro ao carregar campanhas: ' + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Atualizar métricas das campanhas
   */
  const updateMetrics = (campaigns) => {
    const total = campaigns.length;
    const active = campaigns.filter(c => c.status === 'active').length;
    const paused = campaigns.filter(c => c.status === 'paused').length;
    const completed = campaigns.filter(c => c.status === 'completed').length;
    
    setMetrics({ total, active, paused, completed });
  };

  /**
   * Criar nova campanha
   */
  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setError('Nome da campanha é obrigatório');
      return;
    }

    try {
      const data = await makeApiRequest('/campaigns', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      });

      await fetchCampaigns(); // Recarregar lista
      
      // Reset form
      setFormData({
        name: '',
        description: '',
        status: 'active',
        max_simultaneous_calls: 5,
        retry_attempts: 3,
        retry_delay: 300
      });
      setShowModal(false);
      setEditingCampaign(null);
    } catch (err) {
      if (err.message.includes('Endpoint not implemented')) {
        console.info('ℹ️ Simulating campaign creation (backend not available)');
        
        // Simular criação bem-sucedida
        const newCampaign = {
          id: campaigns.length + 1,
          ...formData,
          contacts_total: 0,
          contacts_called: 0,
          contacts_remaining: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };

        const updatedCampaigns = [...campaigns, newCampaign];
        setCampaigns(updatedCampaigns);
        updateMetrics(updatedCampaigns);
        
        // Reset form
        setFormData({
          name: '',
          description: '',
          status: 'active',
          max_simultaneous_calls: 5,
          retry_attempts: 3,
          retry_delay: 300
        });
        setShowModal(false);
        setEditingCampaign(null);
      } else {
        setError('Erro ao criar campanha: ' + err.message);
      }
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
          onClick={() => setShowModal(true)}
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
                      {campaign.max_simultaneous_calls}
                    </td>
                    <td className="px-4 py-4">
                      <div className="text-sm">
                        <div className="text-white">{campaign.contacts_total || 0}</div>
                        <div className="text-gray-400 text-xs">
                          {campaign.contacts_called || 0} contactados
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="text-sm">
                        <div className="text-green-400 font-semibold">
                          {campaign.contacts_called || 0}
                        </div>
                        <div className="text-gray-400 text-xs">
                          {campaign.contacts_total > 0 
                            ? `${Math.round(((campaign.contacts_called || 0) / campaign.contacts_total) * 100)}%`
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
      {showModal && (
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
                  Llamadas concurrentes
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={formData.max_simultaneous_calls}
                  onChange={(e) => setFormData({...formData, max_simultaneous_calls: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
                />
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
                  onClick={() => setShowModal(false)}
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