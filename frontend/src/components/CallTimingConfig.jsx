import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const CallTimingConfig = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [timingConfigs, setTimingConfigs] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activePreset, setActivePreset] = useState('balanced');

  const [formData, setFormData] = useState({
    wait_time: 30,
    sleep_time: 2,
    preset_name: 'balanced',
    progressive_delay: false,
    adaptive_timing: false,
    weekend_multiplier: 1.0,
    night_hours_multiplier: 1.0,
    retry_attempts: 3,
    retry_interval: 300,
    timeout_settings: {}
  });

  const presets = [
    {
      id: 'aggressive',
      name: 'Agressivo',
      icon: '🚀',
      description: 'Máximo de chamadas por minuto',
      color: 'red',
      settings: {
        wait_time: 20,
        sleep_time: 1,
        progressive_delay: false,
        adaptive_timing: false,
        retry_attempts: 5,
        retry_interval: 180
      }
    },
    {
      id: 'balanced',
      name: 'Balanceado',
      icon: '⚖️',
      description: 'Equilíbrio entre volume e qualidade',
      color: 'blue',
      settings: {
        wait_time: 30,
        sleep_time: 2,
        progressive_delay: true,
        adaptive_timing: false,
        retry_attempts: 3,
        retry_interval: 300
      }
    },
    {
      id: 'conservative',
      name: 'Conservador',
      icon: '🛡️',
      description: 'Prioriza qualidade de conexão',
      color: 'green',
      settings: {
        wait_time: 45,
        sleep_time: 5,
        progressive_delay: true,
        adaptive_timing: true,
        retry_attempts: 2,
        retry_interval: 600
      }
    }
  ];

  const fetchData = async () => {
    try {
      setError(null);
      setLoading(true);

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

      // Buscar configurações de timing
      try {
        const timingResponse = await makeApiRequest('/timing-configs');
        if (timingResponse?.configs) {
          setTimingConfigs(timingResponse.configs);
        }
      } catch (err) {
        console.log('Configurações de timing não disponíveis ainda');
        setTimingConfigs([]);
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

  const handleCampaignSelect = (campaign) => {
    setSelectedCampaign(campaign);
    
    // Buscar configuração existente para esta campanha
    const existing = timingConfigs.find(config => config.campaign_id === campaign.id);
    if (existing) {
      setFormData({
        wait_time: existing.wait_time || 30,
        sleep_time: existing.sleep_time || 2,
        preset_name: existing.preset_name || 'balanced',
        progressive_delay: existing.progressive_delay || false,
        adaptive_timing: existing.adaptive_timing || false,
        weekend_multiplier: existing.weekend_multiplier || 1.0,
        night_hours_multiplier: existing.night_hours_multiplier || 1.0,
        retry_attempts: existing.retry_attempts || 3,
        retry_interval: existing.retry_interval || 300,
        timeout_settings: existing.timeout_settings || {}
      });
      setActivePreset(existing.preset_name || 'balanced');
    } else {
      // Aplicar preset padrão
      applyPreset('balanced');
    }
  };

  const applyPreset = (presetId) => {
    const preset = presets.find(p => p.id === presetId);
    if (preset) {
      setFormData(prev => ({
        ...prev,
        ...preset.settings,
        preset_name: presetId
      }));
      setActivePreset(presetId);
    }
  };

  const handleSave = async () => {
    try {
      const configData = {
        ...formData,
        campaign_id: selectedCampaign?.id || null
      };

      // Verificar se já existe configuração
      const existingId = selectedCampaign 
        ? timingConfigs.find(c => c.campaign_id === selectedCampaign.id)?.id
        : null;

      const endpoint = existingId ? `/timing-configs/${existingId}` : '/timing-configs';
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

  const calculateCallsPerMinute = () => {
    const totalTime = formData.wait_time + formData.sleep_time;
    return Math.round(60 / totalTime);
  };

  const getPresetColor = (presetId) => {
    const preset = presets.find(p => p.id === presetId);
    const colors = {
      red: 'border-red-500 bg-red-600/20 text-red-300',
      blue: 'border-blue-500 bg-blue-600/20 text-blue-300',
      green: 'border-green-500 bg-green-600/20 text-green-300'
    };
    return colors[preset?.color] || colors.blue;
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
          ⏱️ Configuração de Timing de Chamadas
        </h1>
        <p className="text-secondary-400 mt-1">
          Configure Wait Time, Sleep Time e outras configurações de timing
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

      <div className="glass-panel">
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Lista de Campanhas */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">
                Selecione uma campanha
              </h3>
              
              <div className="space-y-3">
                {campaigns.length === 0 ? (
                  <div className="text-center py-8">
                    <span className="text-4xl mb-2 block">⏱️</span>
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
                        <div className="text-right">
                          <span className={`px-2 py-1 rounded text-xs ${
                            campaign.ativo ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'
                          }`}>
                            {campaign.ativo ? 'Ativa' : 'Inativa'}
                          </span>
                          {timingConfigs.find(c => c.campaign_id === campaign.id) && (
                            <p className="text-xs text-primary-400 mt-1">✓ Configurada</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Configuração */}
            <div>
              {selectedCampaign ? (
                <div className="space-y-6">
                  <div className="bg-secondary-800/30 rounded-lg p-4 border border-secondary-700">
                    <h4 className="font-medium text-white mb-2">
                      Configurando: {selectedCampaign.nome}
                    </h4>
                    <p className="text-sm text-secondary-400">
                      {selectedCampaign.description || 'Sem descrição'}
                    </p>
                  </div>

                  {/* Presets */}
                  <div>
                    <h4 className="font-medium text-white mb-3">Presets de Configuração</h4>
                    <div className="grid grid-cols-1 gap-3">
                      {presets.map((preset) => (
                        <div
                          key={preset.id}
                          onClick={() => applyPreset(preset.id)}
                          className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                            activePreset === preset.id
                              ? getPresetColor(preset.id)
                              : 'border-secondary-700 bg-secondary-800/30 hover:border-secondary-600'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <span className="text-2xl">{preset.icon}</span>
                              <div>
                                <h5 className="font-medium text-white">{preset.name}</h5>
                                <p className="text-sm text-secondary-400">{preset.description}</p>
                              </div>
                            </div>
                            {activePreset === preset.id && (
                              <span className="text-lg">✓</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Configurações Avançadas */}
                  <div className="space-y-4">
                    <h4 className="font-medium text-white">Configurações Detalhadas</h4>
                    
                    {/* Wait Time e Sleep Time */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-secondary-300 mb-2">
                          Wait Time (segundos)
                        </label>
                        <input
                          type="number"
                          value={formData.wait_time}
                          onChange={(e) => setFormData(prev => ({ ...prev, wait_time: parseInt(e.target.value) }))}
                          className="input-field"
                          min="5"
                          max="120"
                        />
                        <p className="text-xs text-secondary-400 mt-1">
                          Tempo de espera antes de desligar
                        </p>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-secondary-300 mb-2">
                          Sleep Time (segundos)
                        </label>
                        <input
                          type="number"
                          value={formData.sleep_time}
                          onChange={(e) => setFormData(prev => ({ ...prev, sleep_time: parseInt(e.target.value) }))}
                          className="input-field"
                          min="1"
                          max="60"
                        />
                        <p className="text-xs text-secondary-400 mt-1">
                          Pausa entre chamadas
                        </p>
                      </div>
                    </div>

                    {/* Retry Settings */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-secondary-300 mb-2">
                          Tentativas de Retry
                        </label>
                        <input
                          type="number"
                          value={formData.retry_attempts}
                          onChange={(e) => setFormData(prev => ({ ...prev, retry_attempts: parseInt(e.target.value) }))}
                          className="input-field"
                          min="0"
                          max="10"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-secondary-300 mb-2">
                          Intervalo de Retry (segundos)
                        </label>
                        <input
                          type="number"
                          value={formData.retry_interval}
                          onChange={(e) => setFormData(prev => ({ ...prev, retry_interval: parseInt(e.target.value) }))}
                          className="input-field"
                          min="60"
                          max="3600"
                        />
                      </div>
                    </div>

                    {/* Multiplicadores */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-secondary-300 mb-2">
                          Multiplicador Fins de Semana
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          value={formData.weekend_multiplier}
                          onChange={(e) => setFormData(prev => ({ ...prev, weekend_multiplier: parseFloat(e.target.value) }))}
                          className="input-field"
                          min="0.1"
                          max="5.0"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-secondary-300 mb-2">
                          Multiplicador Período Noturno
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          value={formData.night_hours_multiplier}
                          onChange={(e) => setFormData(prev => ({ ...prev, night_hours_multiplier: parseFloat(e.target.value) }))}
                          className="input-field"
                          min="0.1"
                          max="5.0"
                        />
                      </div>
                    </div>

                    {/* Switches */}
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 bg-secondary-800/30 rounded-lg border border-secondary-700">
                        <div>
                          <h5 className="font-medium text-white">Progressive Delay</h5>
                          <p className="text-sm text-secondary-400">Aumentar delays com falhas consecutivas</p>
                        </div>
                        <button
                          onClick={() => setFormData(prev => ({ ...prev, progressive_delay: !prev.progressive_delay }))}
                          className={`w-12 h-6 rounded-full transition-colors ${
                            formData.progressive_delay ? 'bg-primary-600' : 'bg-secondary-600'
                          }`}
                        >
                          <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                            formData.progressive_delay ? 'translate-x-6' : 'translate-x-0.5'
                          }`}></div>
                        </button>
                      </div>

                      <div className="flex items-center justify-between p-4 bg-secondary-800/30 rounded-lg border border-secondary-700">
                        <div>
                          <h5 className="font-medium text-white">Adaptive Timing</h5>
                          <p className="text-sm text-secondary-400">Ajustar automaticamente baseado na performance</p>
                        </div>
                        <button
                          onClick={() => setFormData(prev => ({ ...prev, adaptive_timing: !prev.adaptive_timing }))}
                          className={`w-12 h-6 rounded-full transition-colors ${
                            formData.adaptive_timing ? 'bg-primary-600' : 'bg-secondary-600'
                          }`}
                        >
                          <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                            formData.adaptive_timing ? 'translate-x-6' : 'translate-x-0.5'
                          }`}></div>
                        </button>
                      </div>
                    </div>

                    {/* Estatísticas Calculadas */}
                    <div className="bg-blue-900/20 border border-blue-600/30 rounded-lg p-4">
                      <h4 className="font-medium text-blue-400 mb-3">Estatísticas Calculadas</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-secondary-400 block">Chamadas/min</span>
                          <span className="text-white font-semibold text-lg">{calculateCallsPerMinute()}</span>
                        </div>
                        <div>
                          <span className="text-secondary-400 block">Tempo total/chamada</span>
                          <span className="text-white font-semibold text-lg">{formData.wait_time + formData.sleep_time}s</span>
                        </div>
                        <div>
                          <span className="text-secondary-400 block">Preset ativo</span>
                          <span className="text-white font-semibold capitalize">{activePreset}</span>
                        </div>
                        <div>
                          <span className="text-secondary-400 block">Retentativas</span>
                          <span className="text-white font-semibold text-lg">{formData.retry_attempts}x</span>
                        </div>
                      </div>
                    </div>

                    {/* Botão Salvar */}
                    <button
                      onClick={handleSave}
                      className="w-full btn-primary"
                    >
                      💾 Salvar Configuração de Timing
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <span className="text-6xl mb-4 block">⏱️</span>
                  <h3 className="text-xl font-semibold text-white mb-2">Selecione uma campanha</h3>
                  <p className="text-secondary-400">
                    Escolha na lista ao lado para configurar os timings
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

export default CallTimingConfig; 