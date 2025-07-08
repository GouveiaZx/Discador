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

      // Buscar campanhas (si existe el endpoint)
      try {
        const campaignsResponse = await makeApiRequest('/campaigns');
        if (campaignsResponse?.campaigns) {
          setCampaigns(campaignsResponse.campaigns);
        }
      } catch (err) {
        console.log('Campañas no disponibles aún');
        setCampaigns([]);
      }

      // Buscar configuraciones de Caller ID
      try {
        const callerResponse = await makeApiRequest('/caller-id-configs');
        if (callerResponse?.configs) {
          setCallerConfigs(callerResponse.configs);
        }
      } catch (err) {
        console.log('Configuraciones de Caller ID no disponibles aún');
        setCallerConfigs([]);
      }

    } catch (err) {
      console.error('Error al cargar datos:', err);
      setError('Error al cargar datos del servidor');
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
    
    // Buscar configuración existente para este trunk
    const existing = callerConfigs.find(config => config.trunk_id === trunk.id);
    if (existing) {
      setFormData({
        caller_name: existing.caller_name || '',
        caller_number: existing.caller_number || '',
        is_randomized: existing.is_randomized || false,
        caller_pool: existing.caller_pool || []
      });
    } else {
      // Valores por defecto basados en el país del trunk
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
    
    // Buscar configuración existente para esta campaña
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
        caller_name: campaign.nome || 'Campaña',
        caller_number: '',
        is_randomized: false,
        caller_pool: []
      });
    }
  };

  const getDefaultCallerName = (countryCode) => {
    const defaults = {
      '55': 'Empresa Argentina',
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
    const name = prompt('Nombre del Caller ID:');
    const number = prompt('Número del Caller ID:');
    
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

      // Verificar si ya existe configuración
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
      alert('¡Configuración guardada con éxito!');
    } catch (err) {
      setError('Error al guardar configuración');
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
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-400">Cargando configuraciones...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">📞</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Configuración de Caller ID</h1>
        </div>
        <p className="text-gray-400">Configure Caller ID por trunk o campaña</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 bg-red-900/20 border border-red-500/50 rounded-lg p-4 flex items-center gap-3">
          <span className="text-red-400">⚠️</span>
          <div>
            <div className="text-red-400 font-medium">Error</div>
            <div className="text-red-300 text-sm">{error}</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6">
        <div className="flex space-x-1 bg-gray-800/50 p-1 rounded-lg w-fit">
          <button
            onClick={() => setActiveTab('trunk')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'trunk'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            📡 Por Trunk
          </button>
          <button
            onClick={() => setActiveTab('campaign')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'campaign'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            🎯 Por Campaña
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Lista de Trunks/Campañas */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">
              {activeTab === 'trunk' ? 'Seleccione un Trunk' : 'Seleccione una Campaña'}
            </h3>
            
            {activeTab === 'trunk' ? (
              <div className="space-y-3">
                {trunks.length === 0 ? (
                  <div className="text-center py-8">
                    <span className="text-4xl mb-2 block">📡</span>
                    <p className="text-gray-400">Ningún trunk configurado</p>
                  </div>
                ) : (
                  trunks.map((trunk) => (
                    <div
                      key={trunk.id}
                      onClick={() => handleTrunkSelect(trunk)}
                      className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                        selectedTrunk?.id === trunk.id
                          ? 'bg-blue-600/20 border-blue-500'
                          : 'bg-gray-800/70 border-gray-700 hover:border-gray-600'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="text-2xl">{getCountryFlag(trunk.country_code)}</div>
                          <div>
                            <h4 className="font-medium text-white">{trunk.name}</h4>
                            <div className="text-sm text-gray-400">
                              {trunk.host} • +{trunk.country_code}
                            </div>
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
                    <p className="text-gray-400">Ninguna campaña configurada</p>
                  </div>
                ) : (
                  campaigns.map((campaign) => (
                    <div
                      key={campaign.id}
                      onClick={() => handleCampaignSelect(campaign)}
                      className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                        selectedCampaign?.id === campaign.id
                          ? 'bg-blue-600/20 border-blue-500'
                          : 'bg-gray-800/70 border-gray-700 hover:border-gray-600'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-white">{campaign.nome}</h4>
                          <p className="text-sm text-gray-400">{campaign.description}</p>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs ${
                          campaign.ativo ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'
                        }`}>
                          {campaign.ativo ? 'Activa' : 'Inactiva'}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Configuración */}
          <div>
            {(selectedTrunk || selectedCampaign) ? (
              <div className="space-y-6">
                <div className="bg-gray-800/70 rounded-lg p-4 border border-gray-700">
                  <h4 className="font-medium text-white mb-2">
                    Configurando: {selectedTrunk?.name || selectedCampaign?.nome}
                  </h4>
                  <p className="text-sm text-gray-400">
                    {activeTab === 'trunk' 
                      ? `Host: ${selectedTrunk?.host} • País: +${selectedTrunk?.country_code}`
                      : `Campaña: ${selectedCampaign?.description || 'N/A'}`
                    }
                  </p>
                </div>

                {/* Configuración Básica */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Nombre del Caller ID
                    </label>
                    <input
                      type="text"
                      value={formData.caller_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, caller_name: e.target.value }))}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Nombre de la empresa"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Número del Caller ID
                    </label>
                    <input
                      type="text"
                      value={formData.caller_number}
                      onChange={(e) => setFormData(prev => ({ ...prev, caller_number: e.target.value }))}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="+5411999999999"
                    />
                  </div>

                  {/* Randomización */}
                  <div className="flex items-center justify-between p-4 bg-gray-800/70 rounded-lg border border-gray-700">
                    <div>
                      <h4 className="font-medium text-white">Randomizar Caller ID</h4>
                      <p className="text-sm text-gray-400">Usar pool de Caller IDs aleatoriamente</p>
                    </div>
                    <button
                      onClick={() => setFormData(prev => ({ ...prev, is_randomized: !prev.is_randomized }))}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        formData.is_randomized ? 'bg-blue-600' : 'bg-gray-600'
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
                        <label className="block text-sm font-medium text-gray-300">
                          Pool de Caller IDs
                        </label>
                        <button
                          onClick={addToPool}
                          className="text-blue-400 hover:text-blue-300 text-sm"
                        >
                          + Agregar
                        </button>
                      </div>
                      
                      <div className="space-y-2">
                        {formData.caller_pool.length === 0 ? (
                          <div className="text-center py-4 border-2 border-dashed border-gray-600 rounded-lg">
                            <p className="text-gray-400 text-sm">Ningún Caller ID en el pool</p>
                            <button
                              onClick={addToPool}
                              className="text-blue-400 hover:text-blue-300 text-sm mt-1"
                            >
                              Agregar primer Caller ID
                            </button>
                          </div>
                        ) : (
                          formData.caller_pool.map((caller, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-gray-800/70 rounded border border-gray-700">
                              <div>
                                <span className="text-white font-medium">{caller.name}</span>
                                <span className="text-gray-400 ml-2">{caller.number}</span>
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
                    <h4 className="font-medium text-green-400 mb-2">Vista Previa de la Configuración</h4>
                    <div className="space-y-1 text-sm">
                      <p className="text-white">
                        <span className="text-gray-400">Nombre:</span> {formData.caller_name || 'No configurado'}
                      </p>
                      <p className="text-white">
                        <span className="text-gray-400">Número:</span> {formData.caller_number || 'No configurado'}
                      </p>
                      <p className="text-white">
                        <span className="text-gray-400">Randomización:</span> {formData.is_randomized ? 'Activada' : 'Desactivada'}
                      </p>
                      {formData.is_randomized && (
                        <p className="text-white">
                          <span className="text-gray-400">Pool:</span> {formData.caller_pool.length} Caller ID(s)
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Botón Guardar */}
                  <button
                    onClick={handleSave}
                    disabled={!formData.caller_name || !formData.caller_number}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors"
                  >
                    💾 Guardar Configuración
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <span className="text-6xl mb-4 block">📞</span>
                <h3 className="text-xl font-semibold text-white mb-2">Seleccione un trunk</h3>
                <p className="text-gray-400">
                  Elija de la lista para configurar el Caller ID
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CallerIdManager; 