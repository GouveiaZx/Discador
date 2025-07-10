import React, { useState, useEffect } from 'react';
import performanceService from '../services/performanceService';

const CliLimitsManager = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [limits, setLimits] = useState({});
  const [usage, setUsage] = useState({});
  const [selectedCountry, setSelectedCountry] = useState('usa');
  const [newLimit, setNewLimit] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Configuraciones por defecto de países
  const countryConfigs = {
    usa: {
      name: 'Estados Unidos',
      flag: '🇺🇸',
      defaultLimit: 100,
      description: 'Límite máximo de 100 usos por día para evitar bloqueos'
    },
    canada: {
      name: 'Canadá',
      flag: '🇨🇦',
      defaultLimit: 100,
      description: 'Límite máximo de 100 usos por día para evitar bloqueos'
    },
    mexico: {
      name: 'México',
      flag: '🇲🇽',
      defaultLimit: 0,
      description: 'Uso ilimitado - sin restricciones de operadora'
    },
    brasil: {
      name: 'Brasil',
      flag: '🇧🇷',
      defaultLimit: 0,
      description: 'Uso ilimitado - sin restricciones de operadora'
    },
    colombia: {
      name: 'Colombia',
      flag: '🇨🇴',
      defaultLimit: 0,
      description: 'Uso ilimitado - sin restricciones de operadora'
    },
    argentina: {
      name: 'Argentina',
      flag: '🇦🇷',
      defaultLimit: 0,
      description: 'Uso ilimitado - sin restricciones de operadora'
    },
    chile: {
      name: 'Chile',
      flag: '🇨🇱',
      defaultLimit: 0,
      description: 'Uso ilimitado - sin restricciones de operadora'
    },
    peru: {
      name: 'Perú',
      flag: '🇵🇪',
      defaultLimit: 0,
      description: 'Uso ilimitado - sin restricciones de operadora'
    }
  };

  // Cargar datos iniciales
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Cargar límites y uso en paralelo
      const [limitsResponse, usageResponse] = await Promise.all([
        performanceService.getCliLimits(),
        performanceService.getCliUsage()
      ]);

      setLimits(limitsResponse.limits || {});
      setUsage(usageResponse.usage || {});

    } catch (err) {
      console.error('❌ Error al cargar datos:', err);
      setError('Error al cargar datos de CLI. Verificá la conexión con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveLimit = async () => {
    if (!selectedCountry || newLimit === '') {
      setError('Seleccioná un país y definí un límite');
      return;
    }

    const limitValue = parseInt(newLimit, 10);
    if (isNaN(limitValue) || limitValue < 0) {
      setError('El límite debe ser un número entero positivo (0 para ilimitado)');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await performanceService.setCliLimit(selectedCountry, limitValue);

      // Actualizar estado local
      setLimits(prev => ({
        ...prev,
        [selectedCountry]: limitValue
      }));

      setSuccessMessage(`Límite de ${limitValue === 0 ? 'uso ilimitado' : `${limitValue} usos/día`} definido para ${countryConfigs[selectedCountry]?.name}`);
      setNewLimit('');

      // Recargar datos después de guardar
      setTimeout(() => {
        loadInitialData();
        setSuccessMessage('');
      }, 2000);

    } catch (err) {
      console.error('❌ Error al guardar límite:', err);
      setError('Error al guardar límite. Intentá nuevamente.');
    } finally {
      setSaving(false);
    }
  };

  const handleResetUsage = async () => {
    if (!confirm('¿Estás seguro que querés resetear todos los contadores de uso de CLI?')) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await performanceService.resetCliUsage();
      setSuccessMessage('Contadores de uso reseteados con éxito');

      // Recargar datos
      setTimeout(() => {
        loadInitialData();
        setSuccessMessage('');
      }, 2000);

    } catch (err) {
      console.error('❌ Error al resetear uso:', err);
      setError('Error al resetear contadores. Intentá nuevamente.');
    } finally {
      setSaving(false);
    }
  };

  const getUsagePercentage = (country) => {
    const limit = limits[country] || countryConfigs[country]?.defaultLimit || 0;
    const used = usage[country] || 0;
    
    if (limit === 0) return 0; // Ilimitado
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return 'text-red-400';
    if (percentage >= 70) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getUsageBarColor = (percentage) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-secondary-400">Cargando configuraciones de CLI...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-2">
          🌍 Gestión de Límites de CLI por País
        </h2>
        <p className="text-primary-100">
          Configurá límites diarios de uso de CLI para cada país. USA/Canadá tienen límite de 100/día para evitar bloqueos.
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

      {/* Configuración de Límites */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">
          ⚙️ Configurar Límites
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              Seleccionar País
            </label>
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
              disabled={saving}
            >
              {Object.entries(countryConfigs).map(([code, config]) => (
                <option key={code} value={code}>
                  {config.flag} {config.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              Límite Diario (0 = ilimitado)
            </label>
            <input
              type="number"
              min="0"
              value={newLimit}
              onChange={(e) => setNewLimit(e.target.value)}
              placeholder="Ej: 100"
              className="w-full px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
              disabled={saving}
            />
          </div>
          
          <div className="flex items-end">
            <button
              onClick={handleSaveLimit}
              disabled={saving}
              className={`w-full px-4 py-2 rounded-lg font-medium transition-all ${
                saving
                  ? 'bg-secondary-600 cursor-not-allowed'
                  : 'bg-primary-600 hover:bg-primary-700 text-white'
              }`}
            >
              {saving ? 'Guardando...' : '💾 Guardar Límite'}
            </button>
          </div>
        </div>

        {/* Información del País Seleccionado */}
        <div className="bg-secondary-800/50 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-2">
            <span className="text-2xl">{countryConfigs[selectedCountry]?.flag}</span>
            <span className="text-white font-medium">
              {countryConfigs[selectedCountry]?.name}
            </span>
          </div>
          <p className="text-sm text-secondary-300">
            {countryConfigs[selectedCountry]?.description}
          </p>
          <p className="text-xs text-secondary-400 mt-1">
            Límite actual: {
              (limits[selectedCountry] ?? countryConfigs[selectedCountry]?.defaultLimit) === 0
                ? 'Ilimitado'
                : `${limits[selectedCountry] ?? countryConfigs[selectedCountry]?.defaultLimit} usos/día`
            }
          </p>
        </div>
      </div>

      {/* Estado Actual de Límites */}
      <div className="glass-panel p-6 rounded-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">
            📊 Estado Actual de Límites
          </h3>
          <button
            onClick={handleResetUsage}
            disabled={saving}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              saving
                ? 'bg-secondary-600 cursor-not-allowed'
                : 'bg-warning-600 hover:bg-warning-700 text-white'
            }`}
          >
            {saving ? 'Reseteando...' : '🔄 Resetear Contadores'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Object.entries(countryConfigs).map(([countryCode, config]) => {
            const currentLimit = limits[countryCode] ?? config.defaultLimit;
            const currentUsage = usage[countryCode] || 0;
            const percentage = getUsagePercentage(countryCode);
            
            return (
              <div key={countryCode} className="bg-secondary-800/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{config.flag}</span>
                    <span className="text-white font-medium text-sm">
                      {config.name}
                    </span>
                  </div>
                  <span className={`text-xs font-medium ${getUsageColor(percentage)}`}>
                    {currentLimit === 0 ? 'Ilimitado' : `${Math.round(percentage)}%`}
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-secondary-300">Usado:</span>
                    <span className="text-white">{currentUsage}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-secondary-300">Límite:</span>
                    <span className="text-white">
                      {currentLimit === 0 ? 'Ilimitado' : currentLimit}
                    </span>
                  </div>
                  
                  {currentLimit > 0 && (
                    <div className="w-full bg-secondary-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${getUsageBarColor(percentage)}`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Estadísticas Generales */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">
          📈 Estadísticas Generales
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-400">
              {Object.values(usage).reduce((total, count) => total + count, 0)}
            </div>
            <div className="text-sm text-secondary-400">Total CLIs Usados Hoy</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-accent-400">
              {Object.keys(countryConfigs).filter(country => 
                limits[country] ?? countryConfigs[country].defaultLimit > 0
              ).length}
            </div>
            <div className="text-sm text-secondary-400">Países con Límites</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-success-400">
              {Object.keys(countryConfigs).filter(country => 
                (limits[country] ?? countryConfigs[country].defaultLimit) === 0
              ).length}
            </div>
            <div className="text-sm text-secondary-400">Países Ilimitados</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-warning-400">
              {Object.keys(countryConfigs).filter(country => 
                getUsagePercentage(country) >= 80
              ).length}
            </div>
            <div className="text-sm text-secondary-400">Países &gt;80% Límite</div>
          </div>
        </div>
      </div>

      {/* Información Importante */}
      <div className="glass-panel p-6 rounded-xl">
        <h4 className="font-medium text-blue-400 mb-2">ℹ️ Información sobre Límites de CLI</h4>
        <ul className="text-sm text-secondary-300 space-y-1">
          <li>• <strong>Estados Unidos y Canadá:</strong> Recomendado límite de 100 usos/día máximo</li>
          <li>• <strong>América Latina:</strong> Generalmente sin restricciones (uso ilimitado)</li>
          <li>• <strong>Reset Automático:</strong> Los contadores se resetean automáticamente a las 00:00 UTC</li>
          <li>• <strong>Monitoreo:</strong> El sistema bloquea automáticamente CLIs que exceden el límite</li>
          <li>• <strong>Recomendación:</strong> Configurá límites conservadores para evitar bloqueos de operadora</li>
        </ul>
      </div>
    </div>
  );
};

export default CliLimitsManager; 