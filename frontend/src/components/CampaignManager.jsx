import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const CampaignManager = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState(null);
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    lista_numeros: '',
    lista_dnc: '',
    audio_principal: '',
    audio_espera: '',
    contexto_dtmf: '',
    cli_config: {
      tipo: 'MXN', // MXN, ALEATORIO, ALEATORIO1, DID, DID1
      prefixo_trunk: '',
      digitos_aleatorios: 4,
      usar_prefixo_1: false,
      limite_diario: 100,
      codigos_area: [],
      lista_dids: [],
      regras_especiais: ''
    },
    trunk_config: {
      trunk_saida: '',
      trunk_transferencia: '',
      bridge_number: '',
      dial_string: ''
    },
    horario_config: {
      inicio: '08:00',
      fim: '18:00',
      almoco_inicio: '12:00',
      almoco_fim: '13:00',
      dias_semana: [1, 2, 3, 4, 5], // 0=domingo, 1=segunda, etc
      feriados_excluir: true
    },
    discagem_config: {
      modo: 'massivo', // massivo, preditivo
      canais_simultaneos: 10,
      tentativas_maximas: 3,
      intervalo_tentativas: 300, // segundos
      reconhecer_secretaria: true,
      tempo_espera_resposta: 30,
      tempo_maximo_chamada: 300
    },
    transferencia_config: {
      numeros_transferencia: '3,4', // números DTMF para transferir
      numeros_eliminacao: '9', // números DTMF para eliminar
      timeout_transferencia: 30,
      audio_pre_transferencia: ''
    },
    ativo: true,
    pausado: false
  });
  const [availableAudios, setAvailableAudios] = useState([]);
  const [availableTrunks, setAvailableTrunks] = useState([]);
  const [availableContexts, setAvailableContexts] = useState([]);
  const [availableLists, setAvailableLists] = useState([]);

  useEffect(() => {
    fetchCampaigns();
    fetchAvailableResources();
  }, []);

  const fetchCampaigns = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/campaigns');
      if (response.ok) {
        const data = await response.json();
        setCampaigns(data);
      } else {
        toast.error('Erro ao carregar campanhas');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableResources = async () => {
    try {
      // Buscar áudios disponíveis
      const audiosResponse = await fetch('/api/audios');
      if (audiosResponse.ok) {
        const audios = await audiosResponse.json();
        setAvailableAudios(audios);
      }

      // Buscar trunks disponíveis
      const trunksResponse = await fetch('/api/trunks');
      if (trunksResponse.ok) {
        const trunks = await trunksResponse.json();
        setAvailableTrunks(trunks);
      }

      // Buscar contextos DTMF disponíveis
      const contextsResponse = await fetch('/api/contexts');
      if (contextsResponse.ok) {
        const contexts = await contextsResponse.json();
        setAvailableContexts(contexts);
      }

      // Buscar listas disponíveis
      const listsResponse = await fetch('/api/lists');
      if (listsResponse.ok) {
        const lists = await listsResponse.json();
        setAvailableLists(lists);
      }
    } catch (error) {
      console.error('Erro ao carregar recursos:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const url = editingCampaign ? `/api/campaigns/${editingCampaign.id}` : '/api/campaigns';
      const method = editingCampaign ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        toast.success(editingCampaign ? 'Campanha atualizada com sucesso!' : 'Campanha criada com sucesso!');
        setShowForm(false);
        setEditingCampaign(null);
        resetForm();
        fetchCampaigns();
      } else {
        const errorData = await response.json();
        toast.error(errorData.message || 'Erro ao salvar campanha');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (campaign) => {
    setEditingCampaign(campaign);
    setFormData({ ...campaign });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir esta campanha?')) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/campaigns/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success('Campanha excluída com sucesso!');
        fetchCampaigns();
      } else {
        toast.error('Erro ao excluir campanha');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const toggleCampaignStatus = async (id, currentStatus) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/campaigns/${id}/toggle`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ativo: !currentStatus }),
      });

      if (response.ok) {
        toast.success('Status da campanha atualizado!');
        fetchCampaigns();
      } else {
        toast.error('Erro ao atualizar status');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const pauseResumeCampaign = async (id, currentPausedStatus) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/campaigns/${id}/pause`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pausado: !currentPausedStatus }),
      });

      if (response.ok) {
        toast.success(currentPausedStatus ? 'Campanha retomada!' : 'Campanha pausada!');
        fetchCampaigns();
      } else {
        toast.error('Erro ao pausar/retomar campanha');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      nome: '',
      descricao: '',
      lista_numeros: '',
      lista_dnc: '',
      audio_principal: '',
      audio_espera: '',
      contexto_dtmf: '',
      cli_config: {
        tipo: 'MXN',
        prefixo_trunk: '',
        digitos_aleatorios: 4,
        usar_prefixo_1: false,
        limite_diario: 100,
        codigos_area: [],
        lista_dids: [],
        regras_especiais: ''
      },
      trunk_config: {
        trunk_saida: '',
        trunk_transferencia: '',
        bridge_number: '',
        dial_string: ''
      },
      horario_config: {
        inicio: '08:00',
        fim: '18:00',
        almoco_inicio: '12:00',
        almoco_fim: '13:00',
        dias_semana: [1, 2, 3, 4, 5],
        feriados_excluir: true
      },
      discagem_config: {
        modo: 'massivo',
        canais_simultaneos: 10,
        tentativas_maximas: 3,
        intervalo_tentativas: 300,
        reconhecer_secretaria: true,
        tempo_espera_resposta: 30,
        tempo_maximo_chamada: 300
      },
      transferencia_config: {
        numeros_transferencia: '3,4',
        numeros_eliminacao: '9',
        timeout_transferencia: 30,
        audio_pre_transferencia: ''
      },
      ativo: true,
      pausado: false
    });
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleNestedInputChange = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleArrayInputChange = (section, field, value) => {
    const arrayValue = value.split(',').map(item => item.trim()).filter(item => item);
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: arrayValue
      }
    }));
  };

  const handleDaysChange = (day) => {
    const currentDays = formData.horario_config.dias_semana;
    const newDays = currentDays.includes(day)
      ? currentDays.filter(d => d !== day)
      : [...currentDays, day].sort();
    
    handleNestedInputChange('horario_config', 'dias_semana', newDays);
  };

  const getStatusColor = (status) => {
    return status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  };

  const getPausedColor = (paused) => {
    return paused ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800';
  };

  const getModeColor = (mode) => {
    const colors = {
      'massivo': 'bg-blue-100 text-blue-800',
      'preditivo': 'bg-purple-100 text-purple-800'
    };
    return colors[mode] || 'bg-gray-100 text-gray-800';
  };

  const getCliTypeColor = (type) => {
    const colors = {
      'MXN': 'bg-green-100 text-green-800',
      'ALEATORIO': 'bg-blue-100 text-blue-800',
      'ALEATORIO1': 'bg-indigo-100 text-indigo-800',
      'DID': 'bg-purple-100 text-purple-800',
      'DID1': 'bg-pink-100 text-pink-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const dayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Gerenciador de Campanhas</h1>
        <button
          onClick={() => {
            setShowForm(true);
            setEditingCampaign(null);
            resetForm();
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Nova Campanha
        </button>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-blue-600">{campaigns.length}</div>
          <div className="text-sm text-gray-500">Total de Campanhas</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-green-600">
            {campaigns.filter(c => c.ativo && !c.pausado).length}
          </div>
          <div className="text-sm text-gray-500">Campanhas Ativas</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-yellow-600">
            {campaigns.filter(c => c.pausado).length}
          </div>
          <div className="text-sm text-gray-500">Campanhas Pausadas</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-red-600">
            {campaigns.filter(c => !c.ativo).length}
          </div>
          <div className="text-sm text-gray-500">Campanhas Inativas</div>
        </div>
      </div>

      {/* Lista de Campanhas */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Campanha
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CLI/Modo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Horário
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {campaigns.map((campaign) => (
                <tr key={campaign.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{campaign.nome}</div>
                    <div className="text-sm text-gray-500">{campaign.descricao}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      Lista: {campaign.lista_numeros} | DNC: {campaign.lista_dnc}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="space-y-1">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getCliTypeColor(campaign.cli_config?.tipo)}`}>
                        CLI: {campaign.cli_config?.tipo || 'N/A'}
                      </span>
                      <br />
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getModeColor(campaign.discagem_config?.modo)}`}>
                        {campaign.discagem_config?.modo?.charAt(0).toUpperCase() + campaign.discagem_config?.modo?.slice(1) || 'N/A'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div>{campaign.horario_config?.inicio} - {campaign.horario_config?.fim}</div>
                    <div className="text-xs text-gray-500">
                      Almoço: {campaign.horario_config?.almoco_inicio} - {campaign.horario_config?.almoco_fim}
                    </div>
                    <div className="text-xs text-gray-400">
                      Dias: {campaign.horario_config?.dias_semana?.map(d => dayNames[d]).join(', ')}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="space-y-1">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(campaign.ativo)}`}>
                        {campaign.ativo ? 'Ativo' : 'Inativo'}
                      </span>
                      <br />
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPausedColor(campaign.pausado)}`}>
                        {campaign.pausado ? 'Pausado' : 'Rodando'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(campaign)}
                        className="text-indigo-600 hover:text-indigo-900"
                        title="Editar"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => pauseResumeCampaign(campaign.id, campaign.pausado)}
                        className={`${campaign.pausado ? 'text-green-600 hover:text-green-900' : 'text-yellow-600 hover:text-yellow-900'}`}
                        title={campaign.pausado ? 'Retomar' : 'Pausar'}
                      >
                        {campaign.pausado ? (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15a2 2 0 012 2v0a2 2 0 01-2 2h-1.586a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 0010 14H9a2 2 0 01-2-2v0a2 2 0 012-2z" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                      </button>
                      <button
                        onClick={() => toggleCampaignStatus(campaign.id, campaign.ativo)}
                        className={`${campaign.ativo ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'}`}
                        title={campaign.ativo ? 'Desativar' : 'Ativar'}
                      >
                        {campaign.ativo ? (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L5.636 5.636" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                      </button>
                      <button
                        onClick={() => handleDelete(campaign.id)}
                        className="text-red-600 hover:text-red-900"
                        title="Excluir"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {campaigns.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 mb-4">Nenhuma campanha encontrada</div>
            <button
              onClick={() => {
                setShowForm(true);
                setEditingCampaign(null);
                resetForm();
              }}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Criar Primeira Campanha
            </button>
          </div>
        )}
      </div>

      {/* Modal do Formulário */}
      {showForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                {editingCampaign ? 'Editar Campanha' : 'Nova Campanha'}
              </h3>
              <button
                onClick={() => {
                  setShowForm(false);
                  setEditingCampaign(null);
                  resetForm();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Informações Básicas */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-semibold text-gray-800 mb-4">Informações Básicas</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nome da Campanha *
                    </label>
                    <input
                      type="text"
                      name="nome"
                      value={formData.nome}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Descrição
                    </label>
                    <input
                      type="text"
                      name="descricao"
                      value={formData.descricao}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Lista de Números *
                    </label>
                    <select
                      name="lista_numeros"
                      value={formData.lista_numeros}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="">Selecione uma lista</option>
                      {availableLists.map(list => (
                        <option key={list.id} value={list.id}>{list.nome}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Lista DNC (Não Ligar)
                    </label>
                    <select
                      name="lista_dnc"
                      value={formData.lista_dnc}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Nenhuma</option>
                      {availableLists.filter(list => list.tipo === 'dnc').map(list => (
                        <option key={list.id} value={list.id}>{list.nome}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Configuração de Áudios */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-semibold text-gray-800 mb-4">Configuração de Áudios</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Áudio Principal *
                    </label>
                    <select
                      name="audio_principal"
                      value={formData.audio_principal}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="">Selecione um áudio</option>
                      {availableAudios.filter(audio => audio.tipo === 'principal').map(audio => (
                        <option key={audio.id} value={audio.id}>{audio.nome}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Áudio de Espera
                    </label>
                    <select
                      name="audio_espera"
                      value={formData.audio_espera}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Selecione um áudio</option>
                      {availableAudios.filter(audio => audio.tipo === 'espera').map(audio => (
                        <option key={audio.id} value={audio.id}>{audio.nome}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Contexto DTMF *
                    </label>
                    <select
                      name="contexto_dtmf"
                      value={formData.contexto_dtmf}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="">Selecione um contexto</option>
                      {availableContexts.map(context => (
                        <option key={context.id} value={context.id}>{context.nome}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Configuração de CLI Dinâmico */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-semibold text-gray-800 mb-4">Configuração de CLI Dinâmico</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tipo de CLI *
                    </label>
                    <select
                      value={formData.cli_config.tipo}
                      onChange={(e) => handleNestedInputChange('cli_config', 'tipo', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="MXN">MXN (México)</option>
                      <option value="ALEATORIO">ALEATORIO (EUA/Canadá)</option>
                      <option value="ALEATORIO1">ALEATORIO1 (EUA/Canadá com prefixo 1)</option>
                      <option value="DID">DID (DIDs próprios)</option>
                      <option value="DID1">DID1 (DIDs próprios com prefixo 1)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Prefixo do Trunk
                    </label>
                    <input
                      type="text"
                      value={formData.cli_config.prefixo_trunk}
                      onChange={(e) => handleNestedInputChange('cli_config', 'prefixo_trunk', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Ex: 52 para México, 1 para EUA/Canadá"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Dígitos Aleatórios
                    </label>
                    <input
                      type="number"
                      value={formData.cli_config.digitos_aleatorios}
                      onChange={(e) => handleNestedInputChange('cli_config', 'digitos_aleatorios', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="1"
                      max="10"
                    />
                  </div>
                </div>

                {(formData.cli_config.tipo === 'DID' || formData.cli_config.tipo === 'DID1') && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Limite Diário por DID
                    </label>
                    <input
                      type="number"
                      value={formData.cli_config.limite_diario}
                      onChange={(e) => handleNestedInputChange('cli_config', 'limite_diario', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="1"
                    />
                  </div>
                )}

                {(formData.cli_config.tipo === 'ALEATORIO' || formData.cli_config.tipo === 'ALEATORIO1') && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Códigos de Área (separados por vírgula)
                    </label>
                    <textarea
                      value={formData.cli_config.codigos_area.join(', ')}
                      onChange={(e) => handleArrayInputChange('cli_config', 'codigos_area', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={3}
                      placeholder="Ex: 305, 321, 407, 561, 727, 813..."
                    />
                  </div>
                )}

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Regras Especiais
                  </label>
                  <textarea
                    value={formData.cli_config.regras_especiais}
                    onChange={(e) => handleNestedInputChange('cli_config', 'regras_especiais', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={2}
                    placeholder="Regras específicas para geração de CLI..."
                  />
                </div>
              </div>

              {/* Configuração de Trunks */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-semibold text-gray-800 mb-4">Configuração de Trunks</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Trunk de Saída *
                    </label>
                    <select
                      value={formData.trunk_config.trunk_saida}
                      onChange={(e) => handleNestedInputChange('trunk_config', 'trunk_saida', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="">Selecione um trunk</option>
                      {availableTrunks.filter(trunk => trunk.tipo === 'saida').map(trunk => (
                        <option key={trunk.id} value={trunk.id}>{trunk.nome}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Trunk de Transferência
                    </label>
                    <select
                      value={formData.trunk_config.trunk_transferencia}
                      onChange={(e) => handleNestedInputChange('trunk_config', 'trunk_transferencia', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Selecione um trunk</option>
                      {availableTrunks.filter(trunk => trunk.tipo === 'transferencia').map(trunk => (
                        <option key={trunk.id} value={trunk.id}>{trunk.nome}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Bridge Number
                    </label>
                    <input
                      type="text"
                      value={formData.trunk_config.bridge_number}
                      onChange={(e) => handleNestedInputChange('trunk_config', 'bridge_number', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Número da extensão"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Dial String
                    </label>
                    <input
                      type="text"
                      value={formData.trunk_config.dial_string}
                      onChange={(e) => handleNestedInputChange('trunk_config', 'dial_string', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Ex: SIP/DV/97971"
                    />
                  </div>
                </div>
              </div>

              {/* Configuração de Horários */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-semibold text-gray-800 mb-4">Configuração de Horários</h4>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Início *
                    </label>
                    <input
                      type="time"
                      value={formData.horario_config.inicio}
                      onChange={(e) => handleNestedInputChange('horario_config', 'inicio', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fim *
                    </label>
                    <input
                      type="time"
                      value={formData.horario_config.fim}
                      onChange={(e) => handleNestedInputChange('horario_config', 'fim', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Início do Almoço
                    </label>
                    <input
                      type="time"
                      value={formData.horario_config.almoco_inicio}
                      onChange={(e) => handleNestedInputChange('horario_config', 'almoco_inicio', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fim do Almoço
                    </label>
                    <input
                      type="time"
                      value={formData.horario_config.almoco_fim}
                      onChange={(e) => handleNestedInputChange('horario_config', 'almoco_fim', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Dias da Semana
                  </label>
                  <div className="flex space-x-2">
                    {dayNames.map((day, index) => (
                      <label key={index} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={formData.horario_config.dias_semana.includes(index)}
                          onChange={() => handleDaysChange(index)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="ml-1 text-sm text-gray-700">{day}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="mt-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.horario_config.feriados_excluir}
                      onChange={(e) => handleNestedInputChange('horario_config', 'feriados_excluir', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Excluir feriados</span>
                  </label>
                </div>
              </div>

              {/* Configuração de Discagem */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-semibold text-gray-800 mb-4">Configuração de Discagem</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Modo de Discagem *
                    </label>
                    <select
                      value={formData.discagem_config.modo}
                      onChange={(e) => handleNestedInputChange('discagem_config', 'modo', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="massivo">Massivo</option>
                      <option value="preditivo">Preditivo</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Canais Simultâneos
                    </label>
                    <input
                      type="number"
                      value={formData.discagem_config.canais_simultaneos}
                      onChange={(e) => handleNestedInputChange('discagem_config', 'canais_simultaneos', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="1"
                      max="100"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tentativas Máximas
                    </label>
                    <input
                      type="number"
                      value={formData.discagem_config.tentativas_maximas}
                      onChange={(e) => handleNestedInputChange('discagem_config', 'tentativas_maximas', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="1"
                      max="10"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Intervalo entre Tentativas (seg)
                    </label>
                    <input
                      type="number"
                      value={formData.discagem_config.intervalo_tentativas}
                      onChange={(e) => handleNestedInputChange('discagem_config', 'intervalo_tentativas', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="60"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tempo Espera Resposta (seg)
                    </label>
                    <input
                      type="number"
                      value={formData.discagem_config.tempo_espera_resposta}
                      onChange={(e) => handleNestedInputChange('discagem_config', 'tempo_espera_resposta', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="10"
                      max="120"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tempo Máximo Chamada (seg)
                    </label>
                    <input
                      type="number"
                      value={formData.discagem_config.tempo_maximo_chamada}
                      onChange={(e) => handleNestedInputChange('discagem_config', 'tempo_maximo_chamada', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="60"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.discagem_config.reconhecer_secretaria}
                      onChange={(e) => handleNestedInputChange('discagem_config', 'reconhecer_secretaria', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Reconhecer secretária eletrônica</span>
                  </label>
                </div>
              </div>

              {/* Configuração de Transferência */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-semibold text-gray-800 mb-4">Configuração de Transferência</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Números para Transferência
                    </label>
                    <input
                      type="text"
                      value={formData.transferencia_config.numeros_transferencia}
                      onChange={(e) => handleNestedInputChange('transferencia_config', 'numeros_transferencia', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Ex: 3,4 ou 1,2,3,4,5"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Números para Eliminação
                    </label>
                    <input
                      type="text"
                      value={formData.transferencia_config.numeros_eliminacao}
                      onChange={(e) => handleNestedInputChange('transferencia_config', 'numeros_eliminacao', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Ex: 9"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Timeout Transferência (seg)
                    </label>
                    <input
                      type="number"
                      value={formData.transferencia_config.timeout_transferencia}
                      onChange={(e) => handleNestedInputChange('transferencia_config', 'timeout_transferencia', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="10"
                      max="120"
                    />
                  </div>
                </div>
              </div>

              {/* Status */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-semibold text-gray-800 mb-4">Status da Campanha</h4>
                <div className="flex space-x-6">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="ativo"
                      checked={formData.ativo}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Campanha ativa</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="pausado"
                      checked={formData.pausado}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Iniciar pausada</span>
                  </label>
                </div>
              </div>

              {/* Botões */}
              <div className="flex justify-end space-x-3 pt-6 border-t">
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setEditingCampaign(null);
                    resetForm();
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Salvando...' : (editingCampaign ? 'Atualizar' : 'Criar')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignManager;