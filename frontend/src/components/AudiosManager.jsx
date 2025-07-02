import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const AudiosManager = () => {
  const [audios, setAudios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingAudio, setEditingAudio] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'prompt',
    file: null
  });

  const audioTypes = [
    { value: 'prompt', label: 'Prompt/Saudação' },
    { value: 'hold', label: 'Música de Espera' },
    { value: 'voicemail', label: 'Caixa Postal' },
    { value: 'dtmf', label: 'Menu DTMF' },
    { value: 'error', label: 'Mensagem de Erro' }
  ];

  const loadAudios = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/audios');
      setAudios(response.data || []);
    } catch (error) {
      console.error('Erro ao carregar áudios:', error);
      setAudios([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAudios();
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
      if (file.type.startsWith('audio/')) {
        setFormData({...formData, file});
      } else {
        alert('Por favor, selecione apenas arquivos de áudio');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('type', formData.type);
      if (formData.file) {
        formDataToSend.append('file', formData.file);
      }

      if (editingAudio) {
        await makeApiRequest(`/audios/${editingAudio.id}`, {
          method: 'PUT',
          body: formDataToSend,
          headers: {} // Remove Content-Type header for FormData
        });
      } else {
        await makeApiRequest('/audios', {
          method: 'POST',
          body: formDataToSend,
          headers: {} // Remove Content-Type header for FormData
        });
      }
      
      setShowForm(false);
      setEditingAudio(null);
      resetForm();
      loadAudios();
    } catch (error) {
      console.error('Erro ao salvar áudio:', error);
      alert('Erro ao salvar áudio. Tente novamente.');
    } finally {
      setUploading(false);
    }
  };

  const handleEdit = (audio) => {
    setEditingAudio(audio);
    setFormData({
      name: audio.name,
      description: audio.description,
      type: audio.type,
      file: null
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir este áudio?')) {
      try {
        await makeApiRequest(`/audios/${id}`, { method: 'DELETE' });
        loadAudios();
      } catch (error) {
        console.error('Erro ao excluir áudio:', error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      type: 'prompt',
      file: null
    });
    setEditingAudio(null);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Carregando áudios...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Gerenciamento de Áudios</h2>
          <p className="text-gray-600 mt-1">Gerencie prompts, músicas de espera e mensagens do sistema</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 110 2h-1v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6H3a1 1 0 110-2h4zM6 6v12h12V6H6zm3-2V3h6v1H9z" />
          </svg>
          Novo Áudio
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <h3 className="text-lg font-semibold mb-4">
              {editingAudio ? 'Editar Áudio' : 'Novo Áudio'}
            </h3>
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({...formData, type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {audioTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Arquivo de Áudio</label>
                  <div 
                    className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
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
                        <svg className="mx-auto h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p className="text-sm font-medium text-gray-900">{formData.file.name}</p>
                        <p className="text-xs text-gray-500">{formatFileSize(formData.file.size)}</p>
                        <button
                          type="button"
                          onClick={() => setFormData({...formData, file: null})}
                          className="text-red-600 hover:text-red-700 text-sm"
                        >
                          Remover arquivo
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <svg className="mx-auto h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <p className="text-sm text-gray-600">
                          Arraste um arquivo de áudio aqui ou{' '}
                          <label className="text-blue-600 hover:text-blue-700 cursor-pointer">
                            clique para selecionar
                            <input
                              type="file"
                              accept="audio/*"
                              onChange={(e) => setFormData({...formData, file: e.target.files[0]})}
                              className="hidden"
                            />
                          </label>
                        </p>
                        <p className="text-xs text-gray-500">MP3, WAV, OGG até 10MB</p>
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
                  {uploading ? 'Salvando...' : (editingAudio ? 'Atualizar' : 'Criar')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {audios.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhum áudio configurado</h3>
            <p className="mt-1 text-sm text-gray-500">Comece fazendo upload do seu primeiro arquivo de áudio.</p>
          </div>
        ) : (
          audios.map((audio) => (
            <div key={audio.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-800 truncate">{audio.name}</h3>
                  <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full mt-1">
                    {audioTypes.find(t => t.value === audio.type)?.label || audio.type}
                  </span>
                </div>
                <div className="flex space-x-1">
                  <button
                    onClick={() => handleEdit(audio)}
                    className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="Editar"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(audio.id)}
                    className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="Excluir"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              
              {audio.description && (
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">{audio.description}</p>
              )}
              
              {audio.file_url && (
                <div className="mt-3">
                  <audio controls className="w-full h-8">
                    <source src={audio.file_url} type="audio/mpeg" />
                    Seu navegador não suporta reprodução de áudio.
                  </audio>
                </div>
              )}
              
              <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                <span>Criado: {new Date(audio.created_at).toLocaleDateString()}</span>
                {audio.file_size && <span>{formatFileSize(audio.file_size)}</span>}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AudiosManager; 