import React, { useState, useEffect } from 'react';
import performanceService from '../services/performanceService';

const DTMFCountryConfig = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [configs, setConfigs] = useState({});
  const [selectedCountry, setSelectedCountry] = useState('mexico');
  const [editingConfig, setEditingConfig] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  // Configurações padrão por país
  const countryDefaults = {
    mexico: {
      name: 'México',
      flag: '🇲🇽',
      connect_key: '3',
      disconnect_key: '9',
      repeat_key: '0',
      menu_timeout: 15,
      instructions: 'Presione 3 para conectar, 9 para desconectar, 0 para repetir',
      language: 'es-MX',
      reason: 'Tecla 3 evita transferências para secretárias eletrônicas'
    },
    usa: {
      name: 'Estados Unidos',
      flag: '🇺🇸',
      connect_key: '1',
      disconnect_key: '9',
      repeat_key: '0',
      menu_timeout: 10,
      instructions: 'Press 1 to connect, 9 to disconnect, 0 to repeat',
      language: 'en-US',
      reason: 'Configuração padrão para mercado norte-americano'
    },
    canada: {
      name: 'Canadá',
      flag: '🇨🇦',
      connect_key: '1',
      disconnect_key: '9',
      repeat_key: '0',
      menu_timeout: 10,
      instructions: 'Press 1 to connect, 9 to disconnect, 0 to repeat',
      language: 'en-CA',
      reason: 'Configuração padrão para mercado canadense'
    },
    brasil: {
      name: 'Brasil',
      flag: '🇧🇷',
      connect_key: '1',
      disconnect_key: '9',
      repeat_key: '0',
      menu_timeout: 10,
      instructions: 'Pressione 1 para conectar, 9 para desconectar, 0 para repetir',
      language: 'pt-BR',
      reason: 'Configuração padrão para mercado brasileiro'
    },
    colombia: {
      name: 'Colômbia',
      flag: '🇨🇴',
      connect_key: '1',
      disconnect_key: '9',
      repeat_key: '0',
      menu_timeout: 10,
      instructions: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      language: 'es-CO',
      reason: 'Configuração padrão para mercado colombiano'
    },
    argentina: {
      name: 'Argentina',
      flag: '🇦🇷',
      connect_key: '1',
      disconnect_key: '9',
      repeat_key: '0',
      menu_timeout: 10,
      instructions: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      language: 'es-AR',
      reason: 'Configuração padrão para mercado argentino'
    },
    chile: {
      name: 'Chile',
      flag: '🇨🇱',
      connect_key: '1',
      disconnect_key: '9',
      repeat_key: '0',
      menu_timeout: 10,
      instructions: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      language: 'es-CL',
      reason: 'Configuração padrão para mercado chileno'
    },
    peru: {
      name: 'Peru',
      flag: '🇵🇪',
      connect_key: '1',
      disconnect_key: '9',
      repeat_key: '0',
      menu_timeout: 10,
      instructions: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      language: 'es-PE',
      reason: 'Configuração padrão para mercado peruano'
    }
  };

  // Carregar configurações
  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await performanceService.getDTMFConfig();
      setConfigs(response.configs || {});

    } catch (err) {
      console.error('❌ Erro ao carregar configurações DTMF:', err);
      setError('Erro ao carregar configurações DTMF. Verifique a conexão com o servidor.');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (country) => {
    const currentConfig = configs[country] || countryDefaults[country];
    setEditingConfig({
      country,
      ...currentConfig
    });
  };

  const handleSave = async () => {
    if (!editingConfig) return;

    try {
      setSaving(true);
      setError(null);

      const configToSave = {
        country: editingConfig.country,
        connect_key: editingConfig.connect_key,
        disconnect_key: editingConfig.disconnect_key,
        repeat_key: editingConfig.repeat_key,
        menu_timeout: parseInt(editingConfig.menu_timeout, 10),
        instructions: editingConfig.instructions
      };

      await performanceService.updateDTMFConfig(editingConfig.country, configToSave);

      // Atualizar estado local
      setConfigs(prev => ({
        ...prev,
        [editingConfig.country]: configToSave
      }));

      setSuccessMessage(`Configuração DTMF atualizada para ${countryDefaults[editingConfig.country]?.name}`);
      setEditingConfig(null);

      // Recarregar configs
      setTimeout(() => {
        loadConfigs();
        setSuccessMessage('');
      }, 2000);

    } catch (err) {
      console.error('❌ Erro ao salvar configuração:', err);
      setError('Erro ao salvar configuração. Tente novamente.');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditingConfig(null);
  };

  const handleResetToDefault = (country) => {
    if (!confirm(`Tem certeza que deseja resetar ${countryDefaults[country]?.name} para a configuração padrão?`)) {
      return;
    }

    const defaultConfig = countryDefaults[country];
    setEditingConfig({
      country,
      ...defaultConfig
    });
  };

  const getKeyDisplay = (key) => {
    const keyMap = {
      '1': '1️⃣',
      '2': '2️⃣',
      '3': '3️⃣',
      '4': '4️⃣',
      '5': '5️⃣',
      '6': '6️⃣',
      '7': '7️⃣',
      '8': '8️⃣',
      '9': '9️⃣',
      '0': '0️⃣',
      '*': '⭐',
      '#': '#️⃣'
    };
    return keyMap[key] || key;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-secondary-400">Carregando configurações DTMF...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-2">
          📞 Configurações DTMF por País
        </h2>
        <p className="text-blue-100">
          Configure as teclas DTMF para cada país. México usa tecla 3 para evitar transferências para secretárias eletrônicas.
        </p>
      </div>

      {/* Mensagens de Status */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z"/>
            </svg>
            <span className="text-red-400">{error}</span>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span className="text-green-400">{successMessage}</span>
          </div>
        </div>
      )}

      {/* Modal de Edição */}
      {editingConfig && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-secondary-800 rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-white mb-4">
              Editar Configuração DTMF - {countryDefaults[editingConfig.country]?.flag} {countryDefaults[editingConfig.country]?.name}
            </h3>

            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-300 mb-1">
                    Conectar
                  </label>
                  <select
                    value={editingConfig.connect_key}
                    onChange={(e) => setEditingConfig({...editingConfig, connect_key: e.target.value})}
                    className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '*', '#'].map(key => (
                      <option key={key} value={key}>{getKeyDisplay(key)} {key}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-300 mb-1">
                    Desconectar
                  </label>
                  <select
                    value={editingConfig.disconnect_key}
                    onChange={(e) => setEditingConfig({...editingConfig, disconnect_key: e.target.value})}
                    className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '*', '#'].map(key => (
                      <option key={key} value={key}>{getKeyDisplay(key)} {key}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-300 mb-1">
                    Repetir
                  </label>
                  <select
                    value={editingConfig.repeat_key}
                    onChange={(e) => setEditingConfig({...editingConfig, repeat_key: e.target.value})}
                    className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '*', '#'].map(key => (
                      <option key={key} value={key}>{getKeyDisplay(key)} {key}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-300 mb-1">
                  Timeout (segundos)
                </label>
                <input
                  type="number"
                  value={editingConfig.menu_timeout}
                  onChange={(e) => setEditingConfig({...editingConfig, menu_timeout: e.target.value})}
                  min="5"
                  max="60"
                  className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-300 mb-1">
                  Instruções de Voz
                </label>
                <textarea
                  value={editingConfig.instructions}
                  onChange={(e) => setEditingConfig({...editingConfig, instructions: e.target.value})}
                  rows="3"
                  className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>

            <div className="flex justify-between mt-6">
              <button
                onClick={() => handleResetToDefault(editingConfig.country)}
                className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors"
              >
                Resetar Padrão
              </button>
              <div className="flex space-x-2">
                <button
                  onClick={handleCancel}
                  className="px-4 py-2 bg-secondary-600 hover:bg-secondary-700 text-white rounded-lg transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                >
                  {saving ? 'Salvando...' : 'Salvar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Lista de Configurações */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(countryDefaults).map(([country, defaultConfig]) => {
          const currentConfig = configs[country] || defaultConfig;
          const isModified = JSON.stringify(configs[country]) !== JSON.stringify(defaultConfig);

          return (
            <div key={country} className="glass-panel rounded-lg p-6 hover:border-primary-500/50 transition-all">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <span className="text-3xl mr-3">{defaultConfig.flag}</span>
                  <div>
                    <h3 className="font-semibold text-white">{defaultConfig.name}</h3>
                    <p className="text-xs text-secondary-400">{defaultConfig.language}</p>
                  </div>
                </div>
                {isModified && (
                  <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded-full">
                    Modificado
                  </span>
                )}
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-secondary-300">Conectar:</span>
                  <span className="text-lg">{getKeyDisplay(currentConfig.connect_key)}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm text-secondary-300">Desconectar:</span>
                  <span className="text-lg">{getKeyDisplay(currentConfig.disconnect_key)}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm text-secondary-300">Repetir:</span>
                  <span className="text-lg">{getKeyDisplay(currentConfig.repeat_key)}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm text-secondary-300">Timeout:</span>
                  <span className="text-sm text-white">{currentConfig.menu_timeout}s</span>
                </div>

                <div className="border-t border-secondary-700 pt-3">
                  <p className="text-xs text-secondary-400 mb-2">Instruções:</p>
                  <p className="text-sm text-secondary-300">{currentConfig.instructions}</p>
                </div>

                <div className="border-t border-secondary-700 pt-3">
                  <p className="text-xs text-secondary-400 mb-1">Motivo:</p>
                  <p className="text-sm text-secondary-300">{defaultConfig.reason}</p>
                </div>
              </div>

              <button
                onClick={() => handleEdit(country)}
                className="w-full mt-4 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
              >
                Editar Configuração
              </button>
            </div>
          );
        })}
      </div>

      {/* Informações Importantes */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <h4 className="font-medium text-blue-400 mb-2">ℹ️ Configurações Especiais</h4>
        <ul className="text-sm text-blue-300 space-y-1">
          <li>• <strong>México:</strong> Usa tecla 3 para evitar transferências para secretárias eletrônicas</li>
          <li>• <strong>USA/Canadá:</strong> Usa tecla 1 padrão do mercado norte-americano</li>
          <li>• <strong>Timeout:</strong> México usa 15s, outros países 10s</li>
          <li>• <strong>Instruções:</strong> Localizadas no idioma de cada país</li>
        </ul>
      </div>
    </div>
  );
};

export default DTMFCountryConfig; 