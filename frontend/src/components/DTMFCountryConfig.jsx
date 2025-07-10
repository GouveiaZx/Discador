import React, { useState, useEffect } from 'react';
import performanceService from '../services/performanceService';

const DTMFCountryConfig = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [editingConfig, setEditingConfig] = useState(null);
  const [configs, setConfigs] = useState({});

  // Configuraciones por defecto por país
  const countryDefaults = {
    mexico: {
      name: 'México',
      flag: '🇲🇽',
      dtmf_key: '3',
      message: 'Presione 3 para conectar, 9 para desconectar, 0 para repetir',
      menu_timeout: 15,
      language: 'es-MX',
      instructions: 'Presione 3 para conectar, 9 para desconectar, 0 para repetir',
      reason: 'Tecla 3 evita transferencias a contestadoras automáticas'
    },
    usa: {
      name: 'Estados Unidos',
      flag: '🇺🇸',
      dtmf_key: '1',
      message: 'Press 1 to connect, 9 to disconnect, 0 to repeat',
      menu_timeout: 10,
      language: 'en-US',
      instructions: 'Press 1 to connect, 9 to disconnect, 0 to repeat',
      reason: 'Configuración estándar para mercado norteamericano'
    },
    canada: {
      name: 'Canadá',
      flag: '🇨🇦',
      dtmf_key: '1',
      message: 'Press 1 to connect, 9 to disconnect, 0 to repeat',
      menu_timeout: 10,
      language: 'en-CA',
      instructions: 'Press 1 to connect, 9 to disconnect, 0 to repeat',
      reason: 'Configuración estándar para mercado canadiense'
    },
    brasil: {
      name: 'Brasil',
      flag: '🇧🇷',
      dtmf_key: '1',
      message: 'Pressione 1 para conectar, 9 para desconectar, 0 para repetir',
      menu_timeout: 10,
      language: 'pt-BR',
      instructions: 'Pressione 1 para conectar, 9 para desconectar, 0 para repetir',
      reason: 'Configuración estándar para mercado brasileño'
    },
    colombia: {
      name: 'Colombia',
      flag: '🇨🇴',
      dtmf_key: '1',
      message: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      menu_timeout: 10,
      language: 'es-CO',
      instructions: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      reason: 'Configuración estándar para mercado colombiano'
    },
    argentina: {
      name: 'Argentina',
      flag: '🇦🇷',
      dtmf_key: '1',
      message: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      menu_timeout: 10,
      language: 'es-AR',
      instructions: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      reason: 'Configuración estándar para mercado argentino'
    },
    chile: {
      name: 'Chile',
      flag: '🇨🇱',
      dtmf_key: '1',
      message: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      menu_timeout: 10,
      language: 'es-CL',
      instructions: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      reason: 'Configuración estándar para mercado chileno'
    },
    peru: {
      name: 'Perú',
      flag: '🇵🇪',
      dtmf_key: '1',
      message: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      menu_timeout: 10,
      language: 'es-PE',
      instructions: 'Presione 1 para conectar, 9 para desconectar, 0 para repetir',
      reason: 'Configuración estándar para mercado peruano'
    }
  };

  // Cargar configuraciones
  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Cargar configuraciones DTMF actuales
      const response = await performanceService.getDTMFConfigs();
      setConfigs(response.configs || {});
      
    } catch (err) {
      console.error('❌ Error al cargar configuraciones DTMF:', err);
      setError('Error al cargar configuraciones DTMF. Verificá la conexión con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  const handleEditConfig = (country) => {
    const currentConfig = configs[country] || countryDefaults[country];
    setEditingConfig({
      country,
      ...currentConfig
    });
  };

  const handleSaveConfig = async () => {
    if (!editingConfig) return;

    try {
      setSaving(true);
      setError(null);

      // Validar datos
      const configToSave = {
        country: editingConfig.country,
        dtmf_key: editingConfig.dtmf_key,
        message: editingConfig.message,
        menu_timeout: parseInt(editingConfig.menu_timeout, 10),
        language: editingConfig.language,
        instructions: editingConfig.instructions
      };

      // Validaciones
      if (!configToSave.dtmf_key || configToSave.dtmf_key.length !== 1) {
        throw new Error('Tecla DTMF debe ser un solo dígito');
      }

      if (configToSave.menu_timeout < 5 || configToSave.menu_timeout > 60) {
        throw new Error('Timeout debe estar entre 5 y 60 segundos');
      }

      await performanceService.saveDTMFConfig(configToSave);
      
      // Actualizar estado local
      setConfigs(prev => ({
        ...prev,
        [editingConfig.country]: configToSave
      }));

      setSuccessMessage(`Configuración DTMF actualizada para ${countryDefaults[editingConfig.country]?.name}`);
      setEditingConfig(null);

      // Recargar configuraciones
      setTimeout(() => {
        setSuccessMessage('');
        loadConfigs();
      }, 2000);

    } catch (err) {
      console.error('❌ Error al guardar configuración:', err);
      setError('Error al guardar configuración. Intentá nuevamente.');
    } finally {
      setSaving(false);
    }
  };

  const handleResetConfig = async (country) => {
    if (!confirm(`¿Estás seguro que querés resetear ${countryDefaults[country]?.name} a la configuración por defecto?`)) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await performanceService.resetDTMFConfig(country);
      
      // Actualizar estado local
      setConfigs(prev => ({
        ...prev,
        [country]: countryDefaults[country]
      }));

      setSuccessMessage(`Configuración reseteada para ${countryDefaults[country]?.name}`);

      setTimeout(() => {
        setSuccessMessage('');
        loadConfigs();
      }, 2000);

    } catch (err) {
      console.error('❌ Error al resetear configuración:', err);
      setError('Error al resetear configuración. Intentá nuevamente.');
    } finally {
      setSaving(false);
    }
  };

  const getCurrentConfig = (country) => {
    return configs[country] || countryDefaults[country];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-secondary-400">Cargando configuraciones DTMF...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-2">
          📞 Configuraciones DTMF por País
        </h2>
        <p className="text-primary-100">
          Configurá las teclas DTMF para cada país. México usa tecla 3 para evitar transferencias a contestadoras automáticas.
        </p>
      </div>

      {/* Alertas */}
      {error && (
        <div className="glass-panel p-4 rounded-xl border border-error-500/30">
          <div className="flex items-center space-x-2">
            <span className="text-error-400">❌</span>
            <span className="text-error-300">{error}</span>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="glass-panel p-4 rounded-xl border border-success-500/30">
          <div className="flex items-center space-x-2">
            <span className="text-success-400">✅</span>
            <span className="text-success-300">{successMessage}</span>
          </div>
        </div>
      )}

      {/* Modal de Edición */}
      {editingConfig && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="glass-panel p-6 rounded-xl w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-white mb-4">
              Editar Configuración DTMF - {countryDefaults[editingConfig.country]?.flag} {countryDefaults[editingConfig.country]?.name}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-300 mb-2">
                  Tecla DTMF
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    maxLength="1"
                    pattern="[0-9]"
                    value={editingConfig.dtmf_key}
                    onChange={(e) => setEditingConfig({...editingConfig, dtmf_key: e.target.value})}
                    className="w-16 text-center px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none text-xl font-mono"
                  />
                  <div className="flex space-x-1">
                    {['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'].map(key => (
                      <button
                        key={key}
                        onClick={() => setEditingConfig({...editingConfig, dtmf_key: key})}
                        className={`w-8 h-8 rounded text-sm font-medium transition-all ${
                          editingConfig.dtmf_key === key 
                            ? 'bg-primary-600 text-white' 
                            : 'bg-secondary-700 text-secondary-300 hover:bg-secondary-600'
                        }`}
                      >
                        {key}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-300 mb-2">
                  Mensaje de Voz
                </label>
                <textarea
                  value={editingConfig.message}
                  onChange={(e) => setEditingConfig({...editingConfig, message: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
                  placeholder="Ej: Presione 3 para conectar..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-300 mb-2">
                  Timeout (segundos)
                </label>
                <input
                  type="number"
                  min="5"
                  max="60"
                  value={editingConfig.menu_timeout}
                  onChange={(e) => setEditingConfig({...editingConfig, menu_timeout: e.target.value})}
                  className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-300 mb-2">
                  Idioma
                </label>
                <select
                  value={editingConfig.language}
                  onChange={(e) => setEditingConfig({...editingConfig, language: e.target.value})}
                  className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
                >
                  <option value="es-MX">Español (México)</option>
                  <option value="es-AR">Español (Argentina)</option>
                  <option value="es-CO">Español (Colombia)</option>
                  <option value="es-CL">Español (Chile)</option>
                  <option value="es-PE">Español (Perú)</option>
                  <option value="en-US">English (USA)</option>
                  <option value="en-CA">English (Canada)</option>
                  <option value="pt-BR">Português (Brasil)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-300 mb-2">
                  Instrucciones
                </label>
                <textarea
                  value={editingConfig.instructions}
                  onChange={(e) => setEditingConfig({...editingConfig, instructions: e.target.value})}
                  rows={2}
                  className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
                  placeholder="Instrucciones para el usuario..."
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setEditingConfig(null)}
                className="flex-1 px-4 py-2 bg-secondary-600 hover:bg-secondary-700 text-white rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveConfig}
                disabled={saving}
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                  saving 
                    ? 'bg-secondary-600 cursor-not-allowed' 
                    : 'bg-primary-600 hover:bg-primary-700 text-white'
                }`}
              >
                {saving ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Configuraciones por País */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {Object.entries(countryDefaults).map(([country, defaults]) => {
          const currentConfig = getCurrentConfig(country);
          const isCustom = JSON.stringify(currentConfig) !== JSON.stringify(defaults);
          
          return (
            <div key={country} className="glass-panel p-4 rounded-xl">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{defaults.flag}</span>
                  <div>
                    <h3 className="font-semibold text-white">{defaults.name}</h3>
                    <p className="text-xs text-secondary-400">
                      {isCustom ? 'Personalizado' : 'Por defecto'}
                    </p>
                  </div>
                </div>
                {isCustom && (
                  <span className="px-2 py-1 bg-accent-500/20 text-accent-400 text-xs rounded-full">
                    Personalizado
                  </span>
                )}
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-secondary-300">Tecla DTMF:</span>
                  <span className="text-lg font-mono bg-secondary-800 px-2 py-1 rounded text-white">
                    {currentConfig.dtmf_key}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-secondary-300">Timeout:</span>
                  <span className="text-sm text-white">{currentConfig.menu_timeout}s</span>
                </div>
                <div className="text-sm text-secondary-300">
                  <strong>Mensaje:</strong>
                  <p className="text-white text-xs mt-1 break-words">
                    {currentConfig.message}
                  </p>
                </div>
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => handleEditConfig(country)}
                  className="flex-1 px-3 py-1 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm transition-colors"
                >
                  Editar Configuración
                </button>
                {isCustom && (
                  <button
                    onClick={() => handleResetConfig(country)}
                    className="px-3 py-1 bg-secondary-600 hover:bg-secondary-700 text-white rounded-lg text-sm transition-colors"
                  >
                    Reset
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Información Importante */}
      <div className="glass-panel p-6 rounded-xl">
        <h4 className="font-medium text-blue-400 mb-2">ℹ️ Información sobre Configuraciones DTMF</h4>
        <ul className="text-sm text-secondary-300 space-y-1">
          <li>• <strong>México:</strong> Usa tecla 3 para evitar transferencias a contestadoras automáticas</li>
          <li>• <strong>USA/Canadá:</strong> Usa tecla 1 estándar del mercado norteamericano</li>
          <li>• <strong>Timeout:</strong> México usa 15s, otros países 10s</li>
          <li>• <strong>Instrucciones:</strong> Localizadas en el idioma de cada país</li>
          <li>• <strong>Personalización:</strong> Podés modificar cualquier configuración según tus necesidades</li>
        </ul>
      </div>
    </div>
  );
};

export default DTMFCountryConfig; 