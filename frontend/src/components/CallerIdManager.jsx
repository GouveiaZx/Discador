import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const CallerIdManager = () => {
  const [trunks, setTrunks] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [selectedTrunk, setSelectedTrunk] = useState(null);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('trunk'); // 'trunk' ou 'campaign'

  const [callerIdConfig, setCallerIdConfig] = useState({
    caller_id_nome: '',
    caller_id_numero: '',
    randomizar_caller_id: false,
    pool_caller_ids: []
  });

  const [newCallerId, setNewCallerId] = useState({
    numero: '',
    nome: ''
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [trunksRes, campaignsRes] = await Promise.all([
        makeApiRequest('/trunks'),
        makeApiRequest('/campaigns')
      ]);
      
      setTrunks(trunksRes.data || []);
      setCampaigns(campaignsRes.data || []);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      // Dados mock para desenvolvimento
      setTrunks([
        { id: 1, nome: 'trunk_brasil', host: '136.243.32.61', ativo: true },
        { id: 2, nome: 'trunk_colombia', host: '136.243.32.62', ativo: true },
        { id: 3, nome: 'trunk_mexico', host: '136.243.32.63', ativo: true }
      ]);
      setCampaigns([
        { id: 1, name: 'Campanha Brasil', trunk_id: 1, active: true },
        { id: 2, name: 'Campanha Colombia', trunk_id: 2, active: true }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadCallerIdConfig = async (type, id) => {
    try {
      let endpoint = '';
      if (type === 'trunk') {
        endpoint = `/trunks/${id}/caller-id`;
      } else {
        endpoint = `/campaigns/${id}/caller-id`;
      }
      
      const response = await makeApiRequest(endpoint);
      setCallerIdConfig(response || {
        caller_id_nome: '',
        caller_id_numero: '',
        randomizar_caller_id: false,
        pool_caller_ids: []
      });
    } catch (error) {
      console.error('Erro ao carregar configuração Caller ID:', error);
      // Configuração mock
      setCallerIdConfig({
        caller_id_nome: 'Discador Preditivo',
        caller_id_numero: '1155000000',
        randomizar_caller_id: true,
        pool_caller_ids: [
          { numero: '1155000001', nome: 'Campanha A' },
          { numero: '1155000002', nome: 'Campanha B' },
          { numero: '1155000003', nome: 'Campanha C' }
        ]
      });
    }
  };

  const handleTrunkSelect = (trunk) => {
    setSelectedTrunk(trunk);
    setSelectedCampaign(null);
    setActiveTab('trunk');
    loadCallerIdConfig('trunk', trunk.id);
  };

  const handleCampaignSelect = (campaign) => {
    setSelectedCampaign(campaign);
    setSelectedTrunk(null);
    setActiveTab('campaign');
    loadCallerIdConfig('campaign', campaign.id);
  };

  const handleSaveConfig = async () => {
    try {
      setSaving(true);
      let endpoint = '';
      let targetId = null;

      if (activeTab === 'trunk' && selectedTrunk) {
        endpoint = `/trunks/${selectedTrunk.id}/caller-id`;
        targetId = selectedTrunk.id;
      } else if (activeTab === 'campaign' && selectedCampaign) {
        endpoint = `/campaigns/${selectedCampaign.id}/caller-id`;
        targetId = selectedCampaign.id;
      }

      if (endpoint) {
        await makeApiRequest(endpoint, {
          method: 'PUT',
          body: JSON.stringify(callerIdConfig)
        });
        
        alert('Configuração Caller ID salva com sucesso!');
      }
    } catch (error) {
      console.error('Erro ao salvar configuração:', error);
      alert('Erro ao salvar configuração. Tente novamente.');
    } finally {
      setSaving(false);
    }
  };

  const addToPool = () => {
    if (newCallerId.numero && newCallerId.nome) {
      setCallerIdConfig(prev => ({
        ...prev,
        pool_caller_ids: [...prev.pool_caller_ids, { ...newCallerId }]
      }));
      setNewCallerId({ numero: '', nome: '' });
    }
  };

  const removeFromPool = (index) => {
    setCallerIdConfig(prev => ({
      ...prev,
      pool_caller_ids: prev.pool_caller_ids.filter((_, i) => i !== index)
    }));
  };

  const formatPhoneNumber = (value) => {
    // Remover caracteres não numéricos
    const numbers = value.replace(/\D/g, '');
    
    // Formatar como (11) 55555-5555
    if (numbers.length <= 10) {
      return numbers.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    } else {
      return numbers.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Carregando configurações...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Cabeçalho */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">📞 Configuração de Caller ID</h2>
        <p className="text-gray-600 mt-1">Configure Caller ID por trunk ou campanha</p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-6">
        <button
          onClick={() => setActiveTab('trunk')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'trunk'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          📡 Por Trunk
        </button>
        <button
          onClick={() => setActiveTab('campaign')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'campaign'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          🎯 Por Campanha
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de Trunks/Campanhas */}
        <div className="lg:col-span-1">
          <h3 className="text-lg font-semibold mb-4">
            {activeTab === 'trunk' ? '📡 Trunks Disponíveis' : '🎯 Campanhas Ativas'}
          </h3>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {(activeTab === 'trunk' ? trunks : campaigns).map((item) => (
              <div
                key={item.id}
                onClick={() => activeTab === 'trunk' ? handleTrunkSelect(item) : handleCampaignSelect(item)}
                className={`p-3 border rounded-lg cursor-pointer transition-all ${
                  (activeTab === 'trunk' ? selectedTrunk?.id : selectedCampaign?.id) === item.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="font-medium text-gray-800">
                  {activeTab === 'trunk' ? item.nome : item.name}
                </div>
                <div className="text-sm text-gray-500">
                  {activeTab === 'trunk' ? item.host : `Trunk ID: ${item.trunk_id}`}
                </div>
                <div className="flex items-center mt-1">
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    (activeTab === 'trunk' ? item.ativo : item.active) ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <span className="text-xs text-gray-400">
                    {(activeTab === 'trunk' ? item.ativo : item.active) ? 'Ativo' : 'Inativo'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Configuração de Caller ID */}
        <div className="lg:col-span-2">
          {(selectedTrunk || selectedCampaign) ? (
            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">
                  🔧 Configuração Caller ID - {
                    activeTab === 'trunk' 
                      ? selectedTrunk?.nome 
                      : selectedCampaign?.name
                  }
                </h3>
                <button
                  onClick={handleSaveConfig}
                  disabled={saving}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
                >
                  {saving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Salvando...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Salvar
                    </>
                  )}
                </button>
              </div>

              {/* Configuração Básica */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h4 className="font-semibold text-gray-800 mb-4">📋 Configuração Básica</h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nome do Caller ID
                    </label>
                    <input
                      type="text"
                      value={callerIdConfig.caller_id_nome}
                      onChange={(e) => setCallerIdConfig(prev => ({
                        ...prev,
                        caller_id_nome: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Ex: Discador Preditivo"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Número do Caller ID
                    </label>
                    <input
                      type="text"
                      value={callerIdConfig.caller_id_numero}
                      onChange={(e) => setCallerIdConfig(prev => ({
                        ...prev,
                        caller_id_numero: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Ex: 1155000000"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={callerIdConfig.randomizar_caller_id}
                      onChange={(e) => setCallerIdConfig(prev => ({
                        ...prev,
                        randomizar_caller_id: e.target.checked
                      }))}
                      className="rounded text-blue-600"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      🎲 Randomizar Caller ID (usar pool de números)
                    </span>
                  </label>
                  <p className="text-xs text-gray-500 mt-1 ml-6">
                    Se ativado, o sistema escolherá aleatoriamente um número do pool abaixo
                  </p>
                </div>
              </div>

              {/* Pool de Caller IDs */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 mb-4">🎱 Pool de Caller IDs</h4>
                
                {/* Adicionar novo Caller ID */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                  <input
                    type="text"
                    value={newCallerId.numero}
                    onChange={(e) => setNewCallerId(prev => ({
                      ...prev,
                      numero: e.target.value
                    }))}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Número (ex: 1155000001)"
                  />
                  <input
                    type="text"
                    value={newCallerId.nome}
                    onChange={(e) => setNewCallerId(prev => ({
                      ...prev,
                      nome: e.target.value
                    }))}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Nome (ex: Campanha A)"
                  />
                  <button
                    onClick={addToPool}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center justify-center transition-colors"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Adicionar
                  </button>
                </div>

                {/* Lista do Pool */}
                <div className="space-y-2">
                  {callerIdConfig.pool_caller_ids.map((callerId, index) => (
                    <div key={index} className="flex items-center justify-between bg-white rounded-lg p-3 border">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-semibold text-sm">{index + 1}</span>
                        </div>
                        <div>
                          <div className="font-medium text-gray-800">{callerId.numero}</div>
                          <div className="text-sm text-gray-500">{callerId.nome}</div>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFromPool(index)}
                        className="text-red-600 hover:text-red-800 p-2 rounded-lg hover:bg-red-50 transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))}
                  
                  {callerIdConfig.pool_caller_ids.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                      </svg>
                      <p>Nenhum Caller ID no pool</p>
                      <p className="text-sm">Adicione números para randomização</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Prévia */}
              <div className="mt-6 bg-blue-50 rounded-lg p-4">
                <h4 className="font-semibold text-blue-800 mb-2">👁️ Prévia da Configuração</h4>
                <div className="text-sm text-blue-700">
                  <p><strong>Nome:</strong> {callerIdConfig.caller_id_nome || 'Não configurado'}</p>
                  <p><strong>Número:</strong> {callerIdConfig.caller_id_numero || 'Não configurado'}</p>
                  <p><strong>Randomização:</strong> {callerIdConfig.randomizar_caller_id ? 'Ativada' : 'Desativada'}</p>
                  <p><strong>Pool:</strong> {callerIdConfig.pool_caller_ids.length} números disponíveis</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <p className="text-lg font-medium">Selecione um {activeTab === 'trunk' ? 'trunk' : 'campanha'}</p>
              <p>Escolha na lista ao lado para configurar o Caller ID</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CallerIdManager; 