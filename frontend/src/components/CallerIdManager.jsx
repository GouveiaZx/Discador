import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const CallerIdManager = () => {
  const [activeTab, setActiveTab] = useState('trunk');
  const [trunks, setTrunks] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [callerConfigs, setCallerConfigs] = useState([]);
  const [selectedTrunk, setSelectedTrunk] = useState(null);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    caller_name: '',
    caller_number: '',
    is_randomized: false,
    caller_pool: []
  });

  const fetchData = async () => {
    try {
      setError(null);
      setLoading(true);

      // Buscar trunks
      const trunksResponse = await makeApiRequest('/trunks');
      if (trunksResponse?.trunks) {
        setTrunks(trunksResponse.trunks);
      }

      // Buscar campanhas (se existir endpoint)
      try {
        const campaignsResponse = await makeApiRequest('/campaigns');
        if (campaignsResponse?.campaigns) {
          setCampaigns(campaignsResponse.campaigns);
        }
      } catch (err) {
        console.log('Campanhas não disponíveis ainda');
        setCampaigns([]);
      }

      // Buscar configurações de Caller ID
      try {
        const callerResponse = await makeApiRequest('/caller-id-configs');
        if (callerResponse?.configs) {
          setCallerConfigs(callerResponse.configs);
        }
      } catch (err) {
        console.log('Configurações de Caller ID não disponíveis ainda');
        setCallerConfigs([]);
      }

    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      setError('Erro ao carregar dados do servidor');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTrunkSelect = (trunk) => {
    setSelectedTrunk(trunk);
    setSelectedCampaign(null);
    
    // Buscar configuração existente para este trunk
    const existing = callerConfigs.find(config => config.trunk_id === trunk.id);
    if (existing) {
      setFormData({
        caller_name: existing.caller_name || '',
        caller_number: existing.caller_number || '',
        is_randomized: existing.is_randomized || false,
        caller_pool: existing.caller_pool || []
      });
    } else {
      // Valores padrão baseados no país do trunk
      const defaultName = getDefaultCallerName(trunk.country_code);
      setFormData({
        caller_name: defaultName,
        caller_number: '',
        is_randomized: false,
        caller_pool: []
      });
    }
  };

  const handleCampaignSelect = (campaign) => {
    setSelectedCampaign(campaign);
    setSelectedTrunk(null);
    
    // Buscar configuração existente para esta campanha
    const existing = callerConfigs.find(config => config.campaign_id === campaign.id);
    if (existing) {
      setFormData({
        caller_name: existing.caller_name || '',
        caller_number: existing.caller_number || '',
        is_randomized: existing.is_randomized || false,
        caller_pool: existing.caller_pool || []
      });
    } else {
      setFormData({
        caller_name: campaign.nome || 'Campanha',
        caller_number: '',
        is_randomized: false,
        caller_pool: []
      });
    }
  };

  const getDefaultCallerName = (countryCode) => {
    const defaults = {
      '55': 'Empresa Brasil',
      '57': 'Empresa Colombia', 
      '52': 'Empresa México',
      '1': 'Company USA',
      '51': 'Empresa Perú',
      '56': 'Empresa Chile',
      '54': 'Empresa Argentina',
      '34': 'Empresa España'
    };
    return defaults[countryCode] || 'Discador';
  };

  const addToPool = () => {
    const name = prompt('Nome do Caller ID:');
    const number = prompt('Número do Caller ID:');
    
    if (name && number) {
      setFormData(prev => ({
        ...prev,
        caller_pool: [...prev.caller_pool, { name, number }]
      }));
    }
  };

  const removeFromPool = (index) => {
    setFormData(prev => ({
      ...prev,
      caller_pool: prev.caller_pool.filter((_, i) => i !== index)
    }));
  };

  const handleSave = async () => {
    try {
      const configData = {
        ...formData,
        trunk_id: selectedTrunk?.id || null,
        campaign_id: selectedCampaign?.id || null
      };

      // Verificar se já existe configuração
      const existingId = selectedTrunk 
        ? callerConfigs.find(c => c.trunk_id === selectedTrunk.id)?.id
        : callerConfigs.find(c => c.campaign_id === selectedCampaign.id)?.id;

      const endpoint = existingId ? `/caller-id-configs/${existingId}` : '/caller-id-configs';
      const method = existingId ? 'PUT' : 'POST';

      await makeApiRequest(endpoint, {
        method,
        data: configData
      });

      await fetchData();
      alert('Configuração salva com sucesso!');
    } catch (err) {
      setError('Erro ao salvar configuração');
    }
  };

  const getCountryFlag = (countryCode) => {
    const flags = {
      '55': '🇧🇷', '57': '🇨🇴', '52': '🇲🇽', '1': '🇺🇸',
      '51': '🇵🇪', '56': '🇨🇱', '54': '🇦🇷', '34': '🇪🇸'
    };
    return flags[countryCode] || '🌐';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full"></div>
        <span className="ml-3 text-secondary-300">Cargando configuraciones...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gradient-primary flex items-center">
          📞 Configuração de Caller ID
        </h1>
        <p className="text-secondary-400 mt-1">
          Configure Caller ID por trunk ou campanha
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="glass-panel border-red-500/20 bg-red-900/10 p-4">
          <div className="flex items-center">
            <span className="text-red-400 text-xl mr-3">⚠️</span>
            <div>
              <h3 className="text-red-400 font-medium">Error</h3>
              <p className="text-red-300 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="glass-panel">
        <div className="border-b border-secondary-700">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('trunk')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'trunk'
                  ? 'border-primary-500 text-primary-400'
                  : 'border-transparent text-secondary-400 hover:text-secondary-300'
              }`}
            >
              📡 Por Trunk
            </button>
            <button
              onClick={() => setActiveTab('campaign')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'campaign'
                  ? 'border-primary-500 text-primary-400'
                  : 'border-transparent text-secondary-400 hover:text-secondary-300'
              }`}
            >
              🎯 Por Campanha
            </button>
          </nav>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Lista de Seleção */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">
                {activeTab === 'trunk' ? 'Selecione um Trunk' : 'Selecione uma Campanha'}
              </h3>
              
              {activeTab === 'trunk' ? (
                <div className="space-y-3">
                  {trunks.length === 0 ? (
                    <div className="text-center py-8">
                      <span className="text-4xl mb-2 block">📡</span>
                      <p className="text-secondary-400">Nenhum trunk configurado</p>
                    </div>
                  ) : (
                    trunks.map((trunk) => (
                      <div
                        key={trunk.id}
                        onClick={() => handleTrunkSelect(trunk)}
                        className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                          selectedTrunk?.id === trunk.id
                            ? 'bg-primary-600/20 border-primary-500'
                            : 'bg-secondary-800/50 border-secondary-700 hover:border-secondary-600'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <span className="text-xl">{getCountryFlag(trunk.country_code)}</span>
                            <div>
                              <h4 className="font-medium text-white">{trunk.name}</h4>
                              <p className="text-sm text-secondary-400">{trunk.host}</p>
                            </div>
                          </div>
                          <span className={`w-2 h-2 rounded-full ${trunk.is_active ? 'bg-green-400' : 'bg-red-400'}`}></span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              ) : (
                <div className="space-y-3">
                  {campaigns.length === 0 ? (
                    <div className="text-center py-8">
                      <span className="text-4xl mb-2 block">🎯</span>
                      <p className="text-secondary-400">Nenhuma campanha configurada</p>
                    </div>
                  ) : (
                    campaigns.map((campaign) => (
                      <div
                        key={campaign.id}
                        onClick={() => handleCampaignSelect(campaign)}
                        className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                          selectedCampaign?.id === campaign.id
                            ? 'bg-primary-600/20 border-primary-500'
                            : 'bg-secondary-800/50 border-secondary-700 hover:border-secondary-600'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium text-white">{campaign.nome}</h4>
                            <p className="text-sm text-secondary-400">{campaign.description}</p>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs ${
                            campaign.ativo ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'
                          }`}>
                            {campaign.ativo ? 'Ativa' : 'Inativa'}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* Configuração */}
            <div>
              {(selectedTrunk || selectedCampaign) ? (
                <div className="space-y-6">
                  <div className="bg-secondary-800/30 rounded-lg p-4 border border-secondary-700">
                    <h4 className="font-medium text-white mb-2">
                      Configurando: {selectedTrunk?.name || selectedCampaign?.nome}
                    </h4>
                    <p className="text-sm text-secondary-400">
                      {activeTab === 'trunk' 
                        ? `Host: ${selectedTrunk?.host} • País: +${selectedTrunk?.country_code}`
                        : `Campanha: ${selectedCampaign?.description || 'N/A'}`
                      }
                    </p>
                  </div>

                  {/* Configuração Básica */}
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-secondary-300 mb-2">
                        Nome do Caller ID
                      </label>
                      <input
                        type="text"
                        value={formData.caller_name}
                        onChange={(e) => setFormData(prev => ({ ...prev, caller_name: e.target.value }))}
                        className="input-field"
                        placeholder="Nome da empresa"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-secondary-300 mb-2">
                        Número do Caller ID
                      </label>
                      <input
                        type="text"
                        value={formData.caller_number}
                        onChange={(e) => setFormData(prev => ({ ...prev, caller_number: e.target.value }))}
                        className="input-field"
                        placeholder="+5511999999999"
                      />
                    </div>

                    {/* Randomização */}
                    <div className="flex items-center justify-between p-4 bg-secondary-800/30 rounded-lg border border-secondary-700">
                      <div>
                        <h4 className="font-medium text-white">Randomizar Caller ID</h4>
                        <p className="text-sm text-secondary-400">Usar pool de Caller IDs aleatoriamente</p>
                      </div>
                      <button
                        onClick={() => setFormData(prev => ({ ...prev, is_randomized: !prev.is_randomized }))}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          formData.is_randomized ? 'bg-primary-600' : 'bg-secondary-600'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                          formData.is_randomized ? 'translate-x-6' : 'translate-x-0.5'
                        }`}></div>
                      </button>
                    </div>

                    {/* Pool de Caller IDs */}
                    {formData.is_randomized && (
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <label className="block text-sm font-medium text-secondary-300">
                            Pool de Caller IDs
                          </label>
                          <button
                            onClick={addToPool}
                            className="text-primary-400 hover:text-primary-300 text-sm"
                          >
                            + Adicionar
                          </button>
                        </div>
                        
                        <div className="space-y-2">
                          {formData.caller_pool.length === 0 ? (
                            <div className="text-center py-4 border-2 border-dashed border-secondary-600 rounded-lg">
                              <p className="text-secondary-400 text-sm">Nenhum Caller ID no pool</p>
                              <button
                                onClick={addToPool}
                                className="text-primary-400 hover:text-primary-300 text-sm mt-1"
                              >
                                Adicionar primeiro Caller ID
                              </button>
                            </div>
                          ) : (
                            formData.caller_pool.map((caller, index) => (
                              <div key={index} className="flex items-center justify-between p-3 bg-secondary-800/50 rounded border border-secondary-700">
                                <div>
                                  <span className="text-white font-medium">{caller.name}</span>
                                  <span className="text-secondary-400 ml-2">{caller.number}</span>
                                </div>
                                <button
                                  onClick={() => removeFromPool(index)}
                                  className="text-red-400 hover:text-red-300"
                                >
                                  🗑️
                                </button>
                              </div>
                            ))
                          )}
                        </div>
                      </div>
                    )}

                    {/* Preview */}
                    <div className="bg-green-900/20 border border-green-600/30 rounded-lg p-4">
                      <h4 className="font-medium text-green-400 mb-2">Preview da Configuração</h4>
                      <div className="space-y-1 text-sm">
                        <p className="text-white">
                          <span className="text-secondary-400">Nome:</span> {formData.caller_name || 'Não configurado'}
                        </p>
                        <p className="text-white">
                          <span className="text-secondary-400">Número:</span> {formData.caller_number || 'Não configurado'}
                        </p>
                        <p className="text-white">
                          <span className="text-secondary-400">Randomização:</span> {formData.is_randomized ? 'Ativada' : 'Desativada'}
                        </p>
                        {formData.is_randomized && (
                          <p className="text-white">
                            <span className="text-secondary-400">Pool:</span> {formData.caller_pool.length} Caller ID(s)
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Botão Salvar */}
                    <button
                      onClick={handleSave}
                      disabled={!formData.caller_name || !formData.caller_number}
                      className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      💾 Salvar Configuração
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <span className="text-6xl mb-4 block">📞</span>
                  <h3 className="text-xl font-semibold text-white mb-2">Selecione um trunk</h3>
                  <p className="text-secondary-400">
                    Escolha na lista ao lado para configurar o Caller ID
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CallerIdManager; 