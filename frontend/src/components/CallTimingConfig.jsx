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
      name: 'Agresivo',
      icon: '🚀',
      description: 'Máximo de llamadas por minuto',
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
      description: 'Equilibrio entre volumen y calidad',
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
      description: 'Prioriza calidad de conexión',
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

      // Buscar campañas (si existe el endpoint)
      try {
        const campaignsResponse = await makeApiRequest('/campaigns');
        if (campaignsResponse?.campaigns) {
          setCampaigns(campaignsResponse.campaigns);
        }
      } catch (err) {
        console.log('Campañas no disponibles aún');
        setCampaigns([]);
      }

      // Buscar configuraciones de timing
      try {
        const timingResponse = await makeApiRequest('/timing-configs');
        if (timingResponse?.configs) {
          setTimingConfigs(timingResponse.configs);
        }
      } catch (err) {
        console.log('Configuraciones de timing no disponibles aún');
        setTimingConfigs([]);
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

  const handleCampaignSelect = (campaign) => {
    setSelectedCampaign(campaign);
    
    // Buscar configuración existente para esta campaña
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
      // Aplicar preset por defecto
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

      // Verificar si ya existe configuración
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
      alert('¡Configuración guardada con éxito!');
    } catch (err) {
      setError('Error al guardar configuración');
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
            <span className="text-white font-bold">⏱️</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Configuración de Tiempos</h1>
        </div>
        <p className="text-gray-400">Configure tiempos de espera y pausa entre llamadas</p>
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

      {/* Content */}
      <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Lista de Campañas */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Seleccione una Campaña</h3>
            
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
          </div>

          {/* Configuración */}
          <div>
            {selectedCampaign ? (
              <div className="space-y-6">
                <div className="bg-gray-800/70 rounded-lg p-4 border border-gray-700">
                  <h4 className="font-medium text-white mb-2">
                    Configurando: {selectedCampaign.nome}
                  </h4>
                  <p className="text-sm text-gray-400">
                    Campaña: {selectedCampaign.description || 'N/A'}
                  </p>
                </div>

                {/* Presets */}
                <div>
                  <h4 className="font-medium text-white mb-3">Presets de Configuración</h4>
                  <div className="grid grid-cols-1 gap-3">
                    {presets.map((preset) => (
                      <div
                        key={preset.id}
                        onClick={() => applyPreset(preset.id)}
                        className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                          activePreset === preset.id
                            ? getPresetColor(preset.id)
                            : 'bg-gray-800/70 border-gray-700 hover:border-gray-600'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{preset.icon}</span>
                          <div>
                            <h5 className="font-medium text-white">{preset.name}</h5>
                            <p className="text-sm text-gray-400">{preset.description}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Configuración Manual */}
                <div className="space-y-4">
                  <h4 className="font-medium text-white">Configuración Manual</h4>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Tiempo de Espera (seg)
                      </label>
                      <input
                        type="number"
                        value={formData.wait_time}
                        onChange={(e) => setFormData(prev => ({ ...prev, wait_time: parseInt(e.target.value) }))}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        min="1"
                        max="300"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Tiempo de Pausa (seg)
                      </label>
                      <input
                        type="number"
                        value={formData.sleep_time}
                        onChange={(e) => setFormData(prev => ({ ...prev, sleep_time: parseInt(e.target.value) }))}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        min="0"
                        max="60"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Intentos de Reintento
                      </label>
                      <input
                        type="number"
                        value={formData.retry_attempts}
                        onChange={(e) => setFormData(prev => ({ ...prev, retry_attempts: parseInt(e.target.value) }))}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        min="0"
                        max="10"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Intervalo de Reintento (seg)
                      </label>
                      <input
                        type="number"
                        value={formData.retry_interval}
                        onChange={(e) => setFormData(prev => ({ ...prev, retry_interval: parseInt(e.target.value) }))}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        min="60"
                        max="3600"
                      />
                    </div>
                  </div>

                  {/* Opciones Avanzadas */}
                  <div className="space-y-3">
                    <h5 className="font-medium text-white">Opciones Avanzadas</h5>
                    
                    <div className="flex items-center justify-between p-3 bg-gray-800/70 rounded border border-gray-700">
                      <div>
                        <span className="text-white font-medium">Retraso Progresivo</span>
                        <p className="text-sm text-gray-400">Aumentar tiempos gradualmente</p>
                      </div>
                      <button
                        onClick={() => setFormData(prev => ({ ...prev, progressive_delay: !prev.progressive_delay }))}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          formData.progressive_delay ? 'bg-blue-600' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                          formData.progressive_delay ? 'translate-x-6' : 'translate-x-0.5'
                        }`}></div>
                      </button>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-800/70 rounded border border-gray-700">
                      <div>
                        <span className="text-white font-medium">Timing Adaptativo</span>
                        <p className="text-sm text-gray-400">Ajustar según respuesta del servidor</p>
                      </div>
                      <button
                        onClick={() => setFormData(prev => ({ ...prev, adaptive_timing: !prev.adaptive_timing }))}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          formData.adaptive_timing ? 'bg-blue-600' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                          formData.adaptive_timing ? 'translate-x-6' : 'translate-x-0.5'
                        }`}></div>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Estadísticas */}
                <div className="bg-blue-900/20 border border-blue-600/30 rounded-lg p-4">
                  <h4 className="font-medium text-blue-400 mb-2">Estadísticas Calculadas</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Llamadas/min:</span>
                      <span className="text-white ml-2 font-bold">{calculateCallsPerMinute()}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Tiempo total/llamada:</span>
                      <span className="text-white ml-2 font-bold">{formData.wait_time + formData.sleep_time}s</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Preset activo:</span>
                      <span className="text-white ml-2 font-bold">
                        {presets.find(p => p.id === activePreset)?.name || 'Personalizado'}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-400">Reintentos máx:</span>
                      <span className="text-white ml-2 font-bold">{formData.retry_attempts}</span>
                    </div>
                  </div>
                </div>

                {/* Botón Guardar */}
                <button
                  onClick={handleSave}
                  disabled={!selectedCampaign}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors"
                >
                  💾 Guardar Configuración
                </button>
              </div>
            ) : (
              <div className="text-center py-12">
                <span className="text-6xl mb-4 block">⏱️</span>
                <h3 className="text-xl font-semibold text-white mb-2">Seleccione una campaña</h3>
                <p className="text-gray-400">
                  Elija de la lista para configurar los tiempos
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CallTimingConfig; 