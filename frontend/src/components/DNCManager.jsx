import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const DNCManager = () => {
  const [dncLists, setDncLists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingDnc, setEditingDnc] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    active: true,
    numbers: '',
    file: null
  });

  const loadDncLists = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/dnc');
      setDncLists(response.data || []);
    } catch (error) {
      console.error('Erro ao carregar listas DNC:', error);
      setDncLists([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDncLists();
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'text/csv' || file.name.endsWith('.csv') || file.name.endsWith('.txt')) {
        setFormData({...formData, file});
      } else {
        alert('Por favor, selecione apenas arquivos CSV ou TXT');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    
    try {
      const dataToSend = {
        name: formData.name,
        description: formData.description,
        active: formData.active,
        numbers: formData.numbers ? formData.numbers.split('\n').filter(n => n.trim()) : []
      };

      if (editingDnc) {
        await makeApiRequest(`/dnc/${editingDnc.id}`, {
          method: 'PUT',
          body: JSON.stringify(dataToSend)
        });
      } else {
        await makeApiRequest('/dnc', {
          method: 'POST',
          body: JSON.stringify(dataToSend)
        });
      }
      
      setShowForm(false);
      setEditingDnc(null);
      resetForm();
      loadDncLists();
    } catch (error) {
      console.error('Erro ao salvar lista DNC:', error);
      alert('Erro ao salvar lista DNC. Tente novamente.');
    } finally {
      setUploading(false);
    }
  };

  const handleEdit = (dnc) => {
    setEditingDnc(dnc);
    setFormData({
      name: dnc.name,
      description: dnc.description,
      active: dnc.active,
      numbers: dnc.numbers?.join('\n') || '',
      file: null
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Está seguro que desea eliminar esta lista DNC?')) {
      try {
        await makeApiRequest(`/dnc/${id}`, { method: 'DELETE' });
        loadDncLists();
      } catch (error) {
        console.error('Erro ao excluir lista DNC:', error);
      }
    }
  };

  const handleToggleActive = async (id, currentStatus) => {
    try {
      await makeApiRequest(`/dnc/${id}/toggle`, {
        method: 'PATCH',
        body: JSON.stringify({ active: !currentStatus })
      });
      loadDncLists();
    } catch (error) {
      console.error('Erro ao alterar status da lista DNC:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      active: true,
      numbers: '',
      file: null
    });
    setEditingDnc(null);
  };

  const formatNumberCount = (count) => {
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-gray-600">Cargando listas DNC...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
                      <h2 className="text-2xl font-bold text-gray-800">Gestión DNC</h2>
          <p className="text-gray-600 mt-1">Gestione listas de números que no deben ser contactados</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
          </svg>
          Nova Lista DNC
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">
              {editingDnc ? 'Editar Lista DNC' : 'Nueva Lista DNC'}
            </h3>
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nombre de la Lista</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                          placeholder="Descripción opcional de la lista DNC"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="active"
                    checked={formData.active}
                    onChange={(e) => setFormData({...formData, active: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
                    Lista ativa
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Números (uno por línea)</label>
                  <textarea
                    value={formData.numbers}
                    onChange={(e) => setFormData({...formData, numbers: e.target.value})}
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                    placeholder="55119999****&#10;55118888****&#10;..."
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {formData.numbers.split('\n').filter(n => n.trim()).length} números
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ou importe um arquivo</label>
                  <div 
                    className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
                      dragActive 
                        ? 'border-blue-400 bg-blue-50' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                  >
                    {formData.file ? (
                      <div className="space-y-2">
                        <svg className="mx-auto h-6 w-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p className="text-sm font-medium text-gray-900">{formData.file.name}</p>
                        <button
                          type="button"
                          onClick={() => setFormData({...formData, file: null})}
                          className="text-red-600 hover:text-red-700 text-sm"
                        >
                          Remover archivo
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-1">
                        <svg className="mx-auto h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <p className="text-xs text-gray-600">
                          Arraste CSV/TXT ou{' '}
                          <label className="text-blue-600 hover:text-blue-700 cursor-pointer">
                            clique aqui
                            <input
                              type="file"
                              accept=".csv,.txt"
                              onChange={(e) => setFormData({...formData, file: e.target.files[0]})}
                              className="hidden"
                            />
                          </label>
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? 'Guardando...' : (editingDnc ? 'Actualizar' : 'Crear')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {dncLists.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Ninguna lista DNC configurada</h3>
            <p className="mt-1 text-sm text-gray-500">Comience creando su primera lista de números bloqueados.</p>
          </div>
        ) : (
          dncLists.map((dnc) => (
            <div key={dnc.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-semibold text-gray-800 truncate">{dnc.name}</h3>
                    <button
                      onClick={() => handleToggleActive(dnc.id, dnc.active)}
                      className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full transition-colors ${
                        dnc.active 
                          ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                          : 'bg-red-100 text-red-800 hover:bg-red-200'
                      }`}
                    >
                      {dnc.active ? 'Activo' : 'Inactivo'}
                    </button>
                  </div>
                  {dnc.description && (
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">{dnc.description}</p>
                  )}
                </div>
                <div className="flex space-x-1">
                  <button
                    onClick={() => handleEdit(dnc)}
                    className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="Editar"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(dnc.id)}
                    className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                                          title="Eliminar"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-sm text-gray-500">
                <div className="flex items-center space-x-4">
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                    </svg>
                    {formatNumberCount(dnc.total_numbers || 0)} números
                  </span>
                  <span>Criado: {new Date(dnc.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DNCManager; 