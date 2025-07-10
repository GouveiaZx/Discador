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

  // Configurações padrão dos países
  const countryConfigs = {
    usa: {
      name: 'Estados Unidos',
      flag: '🇺🇸',
      defaultLimit: 100,
      description: 'Limite máximo de 100 usos por dia para evitar bloqueios'
    },
    canada: {
      name: 'Canadá',
      flag: '🇨🇦',
      defaultLimit: 100,
      description: 'Limite máximo de 100 usos por dia para evitar bloqueios'
    },
    mexico: {
      name: 'México',
      flag: '🇲🇽',
      defaultLimit: 0,
      description: 'Uso ilimitado - sem restrições de operadora'
    },
    brasil: {
      name: 'Brasil',
      flag: '🇧🇷',
      defaultLimit: 0,
      description: 'Uso ilimitado - sem restrições de operadora'
    },
    colombia: {
      name: 'Colômbia',
      flag: '🇨🇴',
      defaultLimit: 0,
      description: 'Uso ilimitado - sem restrições de operadora'
    },
    argentina: {
      name: 'Argentina',
      flag: '🇦🇷',
      defaultLimit: 0,
      description: 'Uso ilimitado - sem restrições de operadora'
    },
    chile: {
      name: 'Chile',
      flag: '🇨🇱',
      defaultLimit: 0,
      description: 'Uso ilimitado - sem restrições de operadora'
    },
    peru: {
      name: 'Peru',
      flag: '🇵🇪',
      defaultLimit: 0,
      description: 'Uso ilimitado - sem restrições de operadora'
    }
  };

  // Carregar dados iniciais
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Carregar limites e uso em paralelo
      const [limitsResponse, usageResponse] = await Promise.all([
        performanceService.getCliLimits(),
        performanceService.getCliUsage()
      ]);

      setLimits(limitsResponse.limits || {});
      setUsage(usageResponse.usage || {});

    } catch (err) {
      console.error('❌ Erro ao carregar dados:', err);
      setError('Erro ao carregar dados de CLI. Verifique a conexão com o servidor.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveLimit = async () => {
    if (!selectedCountry || newLimit === '') {
      setError('Selecione um país e defina um limite');
      return;
    }

    const limitValue = parseInt(newLimit, 10);
    if (isNaN(limitValue) || limitValue < 0) {
      setError('Limite deve ser um número inteiro positivo (0 para ilimitado)');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await performanceService.setCliLimit(selectedCountry, limitValue);

      // Atualizar estado local
      setLimits(prev => ({
        ...prev,
        [selectedCountry]: limitValue
      }));

      setSuccessMessage(`Limite de ${limitValue === 0 ? 'uso ilimitado' : `${limitValue} usos/dia`} definido para ${countryConfigs[selectedCountry]?.name}`);
      setNewLimit('');

      // Recarregar dados após salvar
      setTimeout(() => {
        loadInitialData();
        setSuccessMessage('');
      }, 2000);

    } catch (err) {
      console.error('❌ Erro ao salvar limite:', err);
      setError('Erro ao salvar limite. Tente novamente.');
    } finally {
      setSaving(false);
    }
  };

  const handleResetUsage = async () => {
    if (!confirm('Tem certeza que deseja resetar todos os contadores de uso de CLI?')) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await performanceService.resetCliUsage();
      setSuccessMessage('Contadores de uso resetados com sucesso');

      // Recarregar dados
      setTimeout(() => {
        loadInitialData();
        setSuccessMessage('');
      }, 2000);

    } catch (err) {
      console.error('❌ Erro ao resetar uso:', err);
      setError('Erro ao resetar contadores. Tente novamente.');
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
          <p className="text-secondary-400">Carregando configurações de CLI...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-2">
          🌍 Gerenciamento de Limites de CLI por País
        </h2>
        <p className="text-primary-100">
          Configure limites diários de uso de CLI para cada país. USA/Canadá têm limite de 100/dia para evitar bloqueios.
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

      {/* Configurar Limite */}
      <div className="glass-panel rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          ⚙️ Configurar Limite de País
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-secondary-300 mb-2">
              País
            </label>
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
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
              Limite Diário (0 = ilimitado)
            </label>
            <input
              type="number"
              value={newLimit}
              onChange={(e) => setNewLimit(e.target.value)}
              placeholder="Ex: 100"
              min="0"
              className="w-full px-3 py-2 bg-secondary-700 border border-secondary-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleSaveLimit}
              disabled={saving}
              className="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              {saving ? 'Salvando...' : 'Salvar Limite'}
            </button>
          </div>
        </div>

        {selectedCountry && countryConfigs[selectedCountry] && (
          <div className="mt-4 p-4 bg-secondary-800 rounded-lg">
            <p className="text-sm text-secondary-300">
              <strong>{countryConfigs[selectedCountry].name}:</strong> {countryConfigs[selectedCountry].description}
            </p>
          </div>
        )}
      </div>

      {/* Status por País */}
      <div className="glass-panel rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">
            📊 Status de Uso por País
          </h3>
          <button
            onClick={handleResetUsage}
            disabled={saving}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            {saving ? 'Resetando...' : 'Resetar Contadores'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Object.entries(countryConfigs).map(([code, config]) => {
            const currentLimit = limits[code] ?? config.defaultLimit;
            const currentUsage = usage[code] || 0;
            const percentage = getUsagePercentage(code);
            const isUnlimited = currentLimit === 0;

            return (
              <div key={code} className="bg-secondary-800 rounded-lg p-4 border border-secondary-700">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">{config.flag}</span>
                    <div>
                      <h4 className="font-medium text-white">{config.name}</h4>
                      <p className="text-xs text-secondary-400">{code.toUpperCase()}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm font-medium ${getUsageColor(percentage)}`}>
                      {currentUsage} {isUnlimited ? 'usos' : `/ ${currentLimit}`}
                    </div>
                    <div className="text-xs text-secondary-400">
                      {isUnlimited ? 'Ilimitado' : `${percentage.toFixed(1)}%`}
                    </div>
                  </div>
                </div>

                {!isUnlimited && (
                  <div className="w-full bg-secondary-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${getUsageBarColor(percentage)}`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                )}

                {isUnlimited && (
                  <div className="w-full bg-green-500/20 rounded-full h-2">
                    <div className="h-2 rounded-full bg-green-500 opacity-50"></div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Estatísticas Gerais */}
      <div className="glass-panel rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          📈 Estatísticas Gerais
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-secondary-800 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-primary-400">
              {Object.keys(countryConfigs).filter(code => (limits[code] ?? countryConfigs[code].defaultLimit) > 0).length}
            </div>
            <div className="text-sm text-secondary-400">Países com Limite</div>
          </div>

          <div className="bg-secondary-800 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-400">
              {Object.keys(countryConfigs).filter(code => (limits[code] ?? countryConfigs[code].defaultLimit) === 0).length}
            </div>
            <div className="text-sm text-secondary-400">Países Ilimitados</div>
          </div>

          <div className="bg-secondary-800 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-yellow-400">
              {Object.values(usage).reduce((sum, count) => sum + count, 0)}
            </div>
            <div className="text-sm text-secondary-400">Usos Hoje</div>
          </div>

          <div className="bg-secondary-800 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-red-400">
              {Object.entries(countryConfigs).filter(([code]) => {
                const limit = limits[code] ?? countryConfigs[code].defaultLimit;
                const used = usage[code] || 0;
                return limit > 0 && (used / limit) >= 0.9;
              }).length}
            </div>
            <div className="text-sm text-secondary-400">Países > 90%</div>
          </div>
        </div>
      </div>

      {/* Informações Importantes */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <h4 className="font-medium text-blue-400 mb-2">ℹ️ Informações Importantes</h4>
        <ul className="text-sm text-blue-300 space-y-1">
          <li>• USA e Canadá têm limite padrão de 100 usos/dia para evitar bloqueios de operadora</li>
          <li>• Países da América Latina não têm restrições de uso</li>
          <li>• Contadores são resetados automaticamente à meia-noite (UTC)</li>
          <li>• CLIs próximos do limite são automaticamente substituídos na rotação</li>
        </ul>
      </div>
    </div>
  );
};

export default CliLimitsManager; 