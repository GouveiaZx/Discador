import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const DialingModeManager = () => {
  const [dialingModes, setDialingModes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingMode, setEditingMode] = useState(null);
  const [formData, setFormData] = useState({
    nome: '',
    tipo: 'masivo', // masivo, preditivo
    max_canais_simultaneos: 10,
    intervalo_entre_chamadas: 1000, // ms
    timeout_resposta: 30, // segundos
    max_tentativas: 3,
    reconhecedor_secretaria: true,
    tempo_deteccao_secretaria: 3, // segundos
    algoritmo_preditivo: 'basico', // basico, avancado
    ratio_agente_chamada: 1.5, // para modo preditivo
    tempo_abandono_maximo: 3, // segundos
    horario_inicio: '08:00',
    horario_fim: '18:00',
    dias_semana: ['segunda', 'terca', 'quarta', 'quinta', 'sexta'],
    pausar_sem_agentes: true,
    filtros_blacklist: true,
    usar_cli_dinamico: true,
    configuracao_cli: '',
    trunk_principal: '',
    trunk_backup: '',
    ativo: true
  });

  useEffect(() => {
    fetchDialingModes();
  }, []);

  const fetchDialingModes = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/dialing-modes');
      if (response.ok) {
        const data = await response.json();
        setDialingModes(data);
      } else {
        toast.error('Erro ao carregar modos de discagem');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const url = editingMode ? `/api/dialing-modes/${editingMode.id}` : '/api/dialing-modes';
      const method = editingMode ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        toast.success(editingMode ? 'Modo atualizado com sucesso!' : 'Modo criado com sucesso!');
        setShowForm(false);
        setEditingMode(null);
        resetForm();
        fetchDialingModes();
      } else {
        const errorData = await response.json();
        toast.error(errorData.message || 'Erro ao salvar modo');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (mode) => {
    setEditingMode(mode);
    setFormData({ ...mode });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir este modo?')) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/dialing-modes/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success('Modo excluído com sucesso!');
        fetchDialingModes();
      } else {
        toast.error('Erro ao excluir modo');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const toggleStatus = async (id, currentStatus) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/dialing-modes/${id}/toggle`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ativo: !currentStatus }),
      });

      if (response.ok) {
        toast.success('Status atualizado com sucesso!');
        fetchDialingModes();
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

  const resetForm = () => {
    setFormData({
      nome: '',
      tipo: 'masivo',
      max_canais_simultaneos: 10,
      intervalo_entre_chamadas: 1000,
      timeout_resposta: 30,
      max_tentativas: 3,
      reconhecedor_secretaria: true,
      tempo_deteccao_secretaria: 3,
      algoritmo_preditivo: 'basico',
      ratio_agente_chamada: 1.5,
      tempo_abandono_maximo: 3,
      horario_inicio: '08:00',
      horario_fim: '18:00',
      dias_semana: ['segunda', 'terca', 'quarta', 'quinta', 'sexta'],
      pausar_sem_agentes: true,
      filtros_blacklist: true,
      usar_cli_dinamico: true,
      configuracao_cli: '',
      trunk_principal: '',
      trunk_backup: '',
      ativo: true
    });
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleDaysChange = (day) => {
    setFormData(prev => ({
      ...prev,
      dias_semana: prev.dias_semana.includes(day)
        ? prev.dias_semana.filter(d => d !== day)
        : [...prev.dias_semana, day]
    }));
  };

  const getStatusColor = (status) => {
    return status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  };

  const getModeTypeColor = (tipo) => {
    const colors = {
      'masivo': 'bg-blue-100 text-blue-800',
      'preditivo': 'bg-purple-100 text-purple-800'
    };
    return colors[tipo] || 'bg-gray-100 text-gray-800';
  };

  const diasSemanaOptions = [
    { value: 'segunda', label: 'Segunda' },
    { value: 'terca', label: 'Terça' },
    { value: 'quarta', label: 'Quarta' },
    { value: 'quinta', label: 'Quinta' },
    { value: 'sexta', label: 'Sexta' },
    { value: 'sabado', label: 'Sábado' },
    { value: 'domingo', label: 'Domingo' }
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Modos de Discagem</h1>
        <button
          onClick={() => {
            setShowForm(true);
            setEditingMode(null);
            resetForm();
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Novo Modo
        </button>
      </div>

      {/* Lista de Modos */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Canais
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
              {dialingModes.map((mode) => (
                <tr key={mode.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{mode.nome}</div>
                    <div className="text-sm text-gray-500">
                      CLI: {mode.usar_cli_dinamico ? 'Dinâmico' : 'Fixo'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getModeTypeColor(mode.tipo)}`}>
                      {mode.tipo.charAt(0).toUpperCase() + mode.tipo.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {mode.max_canais_simultaneos}
                    {mode.tipo === 'preditivo' && (
                      <div className="text-xs text-gray-500">
                        Ratio: {mode.ratio_agente_chamada}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {mode.horario_inicio} - {mode.horario_fim}
                    <div className="text-xs text-gray-500">
                      {mode.dias_semana.length} dias/semana
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(mode.ativo)}`}>
                      {mode.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleEdit(mode)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => toggleStatus(mode.id, mode.ativo)}
                      className={`${mode.ativo ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'}`}
                    >
                      {mode.ativo ? 'Desativar' : 'Ativar'}
                    </button>
                    <button
                      onClick={() => handleDelete(mode.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {dialingModes.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 mb-4">Nenhum modo de discagem configurado</div>
            <button
              onClick={() => {
                setShowForm(true);
                setEditingMode(null);
                resetForm();
              }}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Criar Primeiro Modo
            </button>
          </div>
        )}
      </div>

      {/* Modal do Formulário */}
      {showForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                {editingMode ? 'Editar Modo de Discagem' : 'Novo Modo de Discagem'}
              </h3>
              <button
                onClick={() => {
                  setShowForm(false);
                  setEditingMode(null);
                  resetForm();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Configurações Básicas */}
                <div className="space-y-4">
                  <h4 className="text-md font-medium text-gray-900 border-b pb-2">Configurações Básicas</h4>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nome do Modo
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
                      Tipo de Discagem
                    </label>
                    <select
                      name="tipo"
                      value={formData.tipo}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="masivo">Masivo</option>
                      <option value="preditivo">Preditivo</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Máximo de Canais Simultâneos
                    </label>
                    <input
                      type="number"
                      name="max_canais_simultaneos"
                      value={formData.max_canais_simultaneos}
                      onChange={handleInputChange}
                      min="1"
                      max="100"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Intervalo entre Chamadas (ms)
                    </label>
                    <input
                      type="number"
                      name="intervalo_entre_chamadas"
                      value={formData.intervalo_entre_chamadas}
                      onChange={handleInputChange}
                      min="100"
                      step="100"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Timeout de Resposta (segundos)
                    </label>
                    <input
                      type="number"
                      name="timeout_resposta"
                      value={formData.timeout_resposta}
                      onChange={handleInputChange}
                      min="10"
                      max="120"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Máximo de Tentativas
                    </label>
                    <input
                      type="number"
                      name="max_tentativas"
                      value={formData.max_tentativas}
                      onChange={handleInputChange}
                      min="1"
                      max="10"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* Configurações Avançadas */}
                <div className="space-y-4">
                  <h4 className="text-md font-medium text-gray-900 border-b pb-2">Configurações Avançadas</h4>
                  
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        name="reconhecedor_secretaria"
                        checked={formData.reconhecedor_secretaria}
                        onChange={handleInputChange}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label className="ml-2 block text-sm text-gray-900">
                        Reconhecedor de Secretária Eletrônica
                      </label>
                    </div>

                    {formData.reconhecedor_secretaria && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Tempo de Detecção (segundos)
                        </label>
                        <input
                          type="number"
                          name="tempo_deteccao_secretaria"
                          value={formData.tempo_deteccao_secretaria}
                          onChange={handleInputChange}
                          min="1"
                          max="10"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    )}
                  </div>

                  {formData.tipo === 'preditivo' && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Algoritmo Preditivo
                        </label>
                        <select
                          name="algoritmo_preditivo"
                          value={formData.algoritmo_preditivo}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="basico">Básico</option>
                          <option value="avancado">Avançado</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Ratio Agente/Chamada
                        </label>
                        <input
                          type="number"
                          name="ratio_agente_chamada"
                          value={formData.ratio_agente_chamada}
                          onChange={handleInputChange}
                          min="1"
                          max="5"
                          step="0.1"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Tempo Máximo de Abandono (segundos)
                        </label>
                        <input
                          type="number"
                          name="tempo_abandono_maximo"
                          value={formData.tempo_abandono_maximo}
                          onChange={handleInputChange}
                          min="1"
                          max="10"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Horário de Início
                      </label>
                      <input
                        type="time"
                        name="horario_inicio"
                        value={formData.horario_inicio}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Horário de Fim
                      </label>
                      <input
                        type="time"
                        name="horario_fim"
                        value={formData.horario_fim}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Dias da Semana
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {diasSemanaOptions.map((dia) => (
                        <div key={dia.value} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={formData.dias_semana.includes(dia.value)}
                            onChange={() => handleDaysChange(dia.value)}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <label className="ml-2 block text-sm text-gray-900">
                            {dia.label}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Configurações de CLI e Trunks */}
              <div className="border-t pt-6">
                <h4 className="text-md font-medium text-gray-900 mb-4">CLI e Trunks</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        name="usar_cli_dinamico"
                        checked={formData.usar_cli_dinamico}
                        onChange={handleInputChange}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label className="ml-2 block text-sm text-gray-900">
                        Usar CLI Dinâmico
                      </label>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Configuração CLI
                      </label>
                      <input
                        type="text"
                        name="configuracao_cli"
                        value={formData.configuracao_cli}
                        onChange={handleInputChange}
                        placeholder="MXN, ALEATORIO, DID, etc."
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Trunk Principal
                      </label>
                      <input
                        type="text"
                        name="trunk_principal"
                        value={formData.trunk_principal}
                        onChange={handleInputChange}
                        placeholder="Nome do trunk principal"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Trunk Backup
                      </label>
                      <input
                        type="text"
                        name="trunk_backup"
                        value={formData.trunk_backup}
                        onChange={handleInputChange}
                        placeholder="Nome do trunk backup (opcional)"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Outras Configurações */}
              <div className="border-t pt-6">
                <h4 className="text-md font-medium text-gray-900 mb-4">Outras Configurações</h4>
                <div className="space-y-3">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="pausar_sem_agentes"
                      checked={formData.pausar_sem_agentes}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                      Pausar quando não há agentes disponíveis
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="filtros_blacklist"
                      checked={formData.filtros_blacklist}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                      Aplicar filtros de blacklist
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="ativo"
                      checked={formData.ativo}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                      Modo ativo
                    </label>
                  </div>
                </div>
              </div>

              {/* Botões */}
              <div className="flex justify-end space-x-3 pt-6 border-t">
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setEditingMode(null);
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
                  {loading ? 'Salvando...' : (editingMode ? 'Atualizar' : 'Criar')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DialingModeManager;