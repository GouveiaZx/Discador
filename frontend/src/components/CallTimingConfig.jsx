import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const CallTimingConfig = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [timingConfig, setTimingConfig] = useState({
    wait_time: 30, // segundos para ring antes de desligar
    sleep_time: 2,  // segundos entre chamadas
    max_retry_attempts: 3,
    retry_interval: 300, // 5 minutos em segundos
    answer_timeout: 60,
    busy_timeout: 30,
    no_answer_timeout: 45,
    progressive_delay: false, // aumentar delay após tentativas falhadas
    adaptive_timing: false,   // ajustar timing baseado na performance
    weekend_multiplier: 1.5,  // multiplicador para fins de semana
    night_hours_multiplier: 2.0 // multiplicador para horário noturno
  });

  const [presets, setPresets] = useState([
    {
      name: 'Agressivo',
      description: 'Máxima velocidade, ideal para listas grandes',
      config: {
        wait_time: 20,
        sleep_time: 1,
        max_retry_attempts: 2,
        retry_interval: 180,
        answer_timeout: 45,
        busy_timeout: 20,
        no_answer_timeout: 30,
        progressive_delay: false,
        adaptive_timing: false,
        weekend_multiplier: 1.0,
        night_hours_multiplier: 1.0
      }
    },
    {
      name: 'Balanceado',
      description: 'Equilibra velocidade e qualidade',
      config: {
        wait_time: 30,
        sleep_time: 2,
        max_retry_attempts: 3,
        retry_interval: 300,
        answer_timeout: 60,
        busy_timeout: 30,
        no_answer_timeout: 45,
        progressive_delay: true,
        adaptive_timing: true,
        weekend_multiplier: 1.5,
        night_hours_multiplier: 1.5
      }
    },
    {
      name: 'Conservador',
      description: 'Foco na qualidade e compliance',
      config: {
        wait_time: 45,
        sleep_time: 5,
        max_retry_attempts: 4,
        retry_interval: 600,
        answer_timeout: 90,
        busy_timeout: 45,
        no_answer_timeout: 60,
        progressive_delay: true,
        adaptive_timing: true,
        weekend_multiplier: 2.0,
        night_hours_multiplier: 3.0
      }
    }
  ]);

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/campaigns');
      setCampaigns(response.data || []);
    } catch (error) {
      console.error('Erro ao carregar campanhas:', error);
      // Dados mock para desenvolvimento
      setCampaigns([
        { id: 1, name: 'Campanha Brasil', active: true, calls_today: 1250, success_rate: 28.5 },
        { id: 2, name: 'Campanha Colombia', active: true, calls_today: 890, success_rate: 31.2 },
        { id: 3, name: 'Campanha Mexico', active: false, calls_today: 0, success_rate: 0 }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadTimingConfig = async (campaignId) => {
    try {
      const response = await makeApiRequest(`/campaigns/${campaignId}/timing-config`);
      setTimingConfig(response || timingConfig);
    } catch (error) {
      console.error('Erro ao carregar configuração de timing:', error);
      // Manter configuração padrão
    }
  };

  const handleCampaignSelect = (campaign) => {
    setSelectedCampaign(campaign);
    loadTimingConfig(campaign.id);
  };

  const handleSaveConfig = async () => {
    if (!selectedCampaign) return;

    try {
      setSaving(true);
      await makeApiRequest(`/campaigns/${selectedCampaign.id}/timing-config`, {
        method: 'PUT',
        body: JSON.stringify(timingConfig)
      });
      
      alert('Configuração de timing salva com sucesso!');
    } catch (error) {
      console.error('Erro ao salvar configuração:', error);
      alert('Erro ao salvar configuração. Tente novamente.');
    } finally {
      setSaving(false);
    }
  };

  const applyPreset = (preset) => {
    setTimingConfig({ ...preset.config });
  };

  const calculateCallsPerHour = () => {
    const totalCallTime = timingConfig.wait_time + timingConfig.sleep_time;
    return Math.round(3600 / totalCallTime);
  };

  const calculateDailyCapacity = () => {
    const callsPerHour = calculateCallsPerHour();
    const workingHours = 8; // assumindo 8h de trabalho por dia
    return callsPerHour * workingHours;
  };

  useEffect(() => {
    loadCampaigns();
  }, []);

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
        <h2 className="text-2xl font-bold text-gray-800">⏱️ Configuração de Timing de Chamadas</h2>
        <p className="text-gray-600 mt-1">Configure Wait Time, Sleep Time e outras configurações de timing</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Lista de Campanhas */}
        <div className="lg:col-span-1">
          <h3 className="text-lg font-semibold mb-4">🎯 Campanhas</h3>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {campaigns.map((campaign) => (
              <div
                key={campaign.id}
                onClick={() => handleCampaignSelect(campaign)}
                className={`p-3 border rounded-lg cursor-pointer transition-all ${
                  selectedCampaign?.id === campaign.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="font-medium text-gray-800">{campaign.name}</div>
                <div className="text-sm text-gray-500">
                  {campaign.calls_today} chamadas hoje
                </div>
                <div className="flex items-center mt-1">
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    campaign.active ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <span className="text-xs text-gray-400">
                    Taxa: {campaign.success_rate}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Configurações */}
        <div className="lg:col-span-3">
          {selectedCampaign ? (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold">
                  ⚙️ Configuração - {selectedCampaign.name}
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

              {/* Presets */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-800 mb-3">🎛️ Presets Rápidos</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {presets.map((preset, index) => (
                    <div
                      key={index}
                      onClick={() => applyPreset(preset)}
                      className="border border-gray-200 rounded-lg p-3 cursor-pointer hover:border-blue-300 hover:bg-blue-50 transition-all"
                    >
                      <div className="font-medium text-gray-800">{preset.name}</div>
                      <div className="text-sm text-gray-500 mt-1">{preset.description}</div>
                      <div className="text-xs text-blue-600 mt-2">
                        Wait: {preset.config.wait_time}s | Sleep: {preset.config.sleep_time}s
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Configurações Principais */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {/* Wait Time */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-4">📞 Wait Time (Ring Duration)</h4>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tempo de ring antes de desligar (segundos)
                    </label>
                    <div className="flex items-center space-x-3">
                      <input
                        type="range"
                        min="10"
                        max="120"
                        value={timingConfig.wait_time}
                        onChange={(e) => setTimingConfig(prev => ({
                          ...prev,
                          wait_time: parseInt(e.target.value)
                        }))}
                        className="flex-1"
                      />
                      <div className="w-16 text-center bg-white border border-gray-300 rounded px-2 py-1">
                        {timingConfig.wait_time}s
                      </div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Rápido (10s)</span>
                      <span>Lento (120s)</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Timeout para atendimento (s)
                      </label>
                      <input
                        type="number"
                        min="30"
                        max="180"
                        value={timingConfig.answer_timeout}
                        onChange={(e) => setTimingConfig(prev => ({
                          ...prev,
                          answer_timeout: parseInt(e.target.value)
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Timeout para ocupado (s)
                      </label>
                      <input
                        type="number"
                        min="10"
                        max="90"
                        value={timingConfig.busy_timeout}
                        onChange={(e) => setTimingConfig(prev => ({
                          ...prev,
                          busy_timeout: parseInt(e.target.value)
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                {/* Sleep Time */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-4">⏸️ Sleep Time (Intervalo)</h4>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Intervalo entre chamadas (segundos)
                    </label>
                    <div className="flex items-center space-x-3">
                      <input
                        type="range"
                        min="0"
                        max="30"
                        value={timingConfig.sleep_time}
                        onChange={(e) => setTimingConfig(prev => ({
                          ...prev,
                          sleep_time: parseInt(e.target.value)
                        }))}
                        className="flex-1"
                      />
                      <div className="w-16 text-center bg-white border border-gray-300 rounded px-2 py-1">
                        {timingConfig.sleep_time}s
                      </div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Imediato (0s)</span>
                      <span>Lento (30s)</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Máximo de tentativas
                      </label>
                      <select
                        value={timingConfig.max_retry_attempts}
                        onChange={(e) => setTimingConfig(prev => ({
                          ...prev,
                          max_retry_attempts: parseInt(e.target.value)
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value={1}>1 tentativa</option>
                        <option value={2}>2 tentativas</option>
                        <option value={3}>3 tentativas</option>
                        <option value={4}>4 tentativas</option>
                        <option value={5}>5 tentativas</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Intervalo para retry (minutos)
                      </label>
                      <select
                        value={timingConfig.retry_interval}
                        onChange={(e) => setTimingConfig(prev => ({
                          ...prev,
                          retry_interval: parseInt(e.target.value)
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value={180}>3 minutos</option>
                        <option value={300}>5 minutos</option>
                        <option value={600}>10 minutos</option>
                        <option value={900}>15 minutos</option>
                        <option value={1800}>30 minutos</option>
                        <option value={3600}>1 hora</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Configurações Avançadas */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h4 className="font-semibold text-gray-800 mb-4">🚀 Configurações Avançadas</h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={timingConfig.progressive_delay}
                        onChange={(e) => setTimingConfig(prev => ({
                          ...prev,
                          progressive_delay: e.target.checked
                        }))}
                        className="rounded text-blue-600"
                      />
                      <div>
                        <span className="text-sm font-medium text-gray-700">
                          🔄 Delay Progressivo
                        </span>
                        <p className="text-xs text-gray-500">
                          Aumentar delay após tentativas falhadas
                        </p>
                      </div>
                    </label>

                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={timingConfig.adaptive_timing}
                        onChange={(e) => setTimingConfig(prev => ({
                          ...prev,
                          adaptive_timing: e.target.checked
                        }))}
                        className="rounded text-blue-600"
                      />
                      <div>
                        <span className="text-sm font-medium text-gray-700">
                          🧠 Timing Adaptativo
                        </span>
                        <p className="text-xs text-gray-500">
                          Ajustar timing baseado na performance
                        </p>
                      </div>
                    </label>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Multiplicador fim de semana
                      </label>
                      <select
                        value={timingConfig.weekend_multiplier}
                        onChange={(e) => setTimingConfig(prev => ({
                          ...prev,
                          weekend_multiplier: parseFloat(e.target.value)
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value={1.0}>1.0x (normal)</option>
                        <option value={1.5}>1.5x (50% mais lento)</option>
                        <option value={2.0}>2.0x (2x mais lento)</option>
                        <option value={3.0}>3.0x (3x mais lento)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Multiplicador horário noturno
                      </label>
                      <select
                        value={timingConfig.night_hours_multiplier}
                        onChange={(e) => setTimingConfig(prev => ({
                          ...prev,
                          night_hours_multiplier: parseFloat(e.target.value)
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value={1.0}>1.0x (normal)</option>
                        <option value={1.5}>1.5x (50% mais lento)</option>
                        <option value={2.0}>2.0x (2x mais lento)</option>
                        <option value={3.0}>3.0x (3x mais lento)</option>
                        <option value={5.0}>5.0x (5x mais lento)</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Estatísticas e Previsões */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {calculateCallsPerHour()}
                  </div>
                  <div className="text-sm text-blue-700">Chamadas/hora</div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {calculateDailyCapacity()}
                  </div>
                  <div className="text-sm text-green-700">Capacidade diária</div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {timingConfig.wait_time + timingConfig.sleep_time}s
                  </div>
                  <div className="text-sm text-purple-700">Ciclo total</div>
                </div>
              </div>

              {/* Prévia */}
              <div className="mt-6 bg-yellow-50 rounded-lg p-4">
                <h4 className="font-semibold text-yellow-800 mb-2">📊 Análise da Configuração</h4>
                <div className="text-sm text-yellow-700 space-y-1">
                  <p>• Ring por {timingConfig.wait_time}s antes de desligar</p>
                  <p>• Aguardar {timingConfig.sleep_time}s entre chamadas</p>
                  <p>• Máximo de {timingConfig.max_retry_attempts} tentativas por número</p>
                  <p>• Retry após {Math.round(timingConfig.retry_interval / 60)} minutos</p>
                  <p>• Capacidade estimada: {calculateCallsPerHour()} chamadas/hora</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-lg font-medium">Selecione uma campanha</p>
              <p>Escolha na lista ao lado para configurar os timings</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CallTimingConfig; 