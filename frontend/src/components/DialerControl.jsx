import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config/api';
import { useCampaigns } from '../contexts/CampaignContext';

const DialerControl = () => {
  const { campaigns } = useCampaigns();
  const [dialerStatus, setDialerStatus] = useState({
    running: false,
    active_campaigns: 0,
    total_calls: 0,
    concurrent_calls: 0,
    asterisk_connected: false
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [dialerConfig, setDialerConfig] = useState({
    max_calls_per_second: 10,
    min_calls_per_second: 1,
    target_answer_rate: 0.15,
    agent_capacity: 5
  });

  // Função para fazer requisições à API
  const makeApiRequest = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}/api/v1${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      // API Error
      throw error;
    }
  };

  // Mostrar mensagem temporária
  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  // Carregar status do discador
  const loadDialerStatus = async () => {
    try {
      const response = await makeApiRequest('/dialer/status');
      setDialerStatus(response);
    } catch (error) {
      // Erro ao carregar status
    }
  };



  // Iniciar discador
  const startDialer = async () => {
    try {
      setLoading(true);
      await makeApiRequest('/dialer/start', { method: 'POST' });
      showMessage('success', '🚀 Sistema de discagem iniciado com sucesso!');
      await loadDialerStatus();
    } catch (error) {
      showMessage('error', 'Erro ao iniciar discador: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Parar discador
  const stopDialer = async () => {
    try {
      setLoading(true);
      await makeApiRequest('/dialer/stop', { method: 'POST' });
      showMessage('success', '🛑 Sistema de discagem parado com sucesso!');
      await loadDialerStatus();
    } catch (error) {
      showMessage('error', 'Erro ao parar discador: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Atualizar configuração do discador
  const updateDialerConfig = async () => {
    try {
      setLoading(true);
      await makeApiRequest('/dialer/config', {
        method: 'POST',
        body: JSON.stringify(dialerConfig)
      });
      showMessage('success', '⚙️ Configuração atualizada com sucesso!');
    } catch (error) {
      showMessage('error', 'Erro ao atualizar configuração: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Controlar campanha
  const controlCampaign = async (campaignId, action) => {
    try {
      setLoading(true);
      await makeApiRequest('/dialer/campaign/control', {
        method: 'POST',
        body: JSON.stringify({
          campaign_id: campaignId,
          action: action
        })
      });
      showMessage('success', `Campanha ${action === 'start' ? 'iniciada' : action === 'pause' ? 'pausada' : action === 'resume' ? 'retomada' : 'parada'} com sucesso!`);
    } catch (error) {
      showMessage('error', 'Erro ao controlar campanha: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Carregar dados iniciais
  useEffect(() => {
    loadDialerStatus();
    
    // Atualizar status a cada 5 segundos
    const interval = setInterval(() => {
      loadDialerStatus();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white mb-4">🎛️ Control de Discado Predictivo</h2>
          <p className="text-gray-400">Gestión y control del sistema de discado automático</p>
        </div>

        {/* Mensajes de estado */}
        {message && (
          <div className={`p-4 rounded-lg border ${
            message.type === 'success' 
              ? 'bg-green-500/10 border-green-500/30 text-green-400' 
              : 'bg-red-500/10 border-red-500/30 text-red-400'
          }`}>
            <div className="flex items-center">
              <span className="mr-2">
                {message.type === 'success' ? '✅' : '❌'}
              </span>
              {message.text}
            </div>
          </div>
        )}

        {/* Status del Sistema */}
        <div className="bg-gray-800/40 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <span className="text-2xl mr-3">📊</span>
              <h3 className="text-xl font-semibold text-white">Status del Sistema</h3>
            </div>
            <div className={`px-4 py-2 rounded-full text-sm font-medium ${
              dialerStatus.running 
                ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                : 'bg-red-500/20 text-red-400 border border-red-500/30'
            }`}>
              {dialerStatus.running ? '🟢 Activo' : '🔴 Inactivo'}
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-700/30 p-4 rounded-lg">
              <div className="text-2xl font-bold text-white">{dialerStatus.active_campaigns || 0}</div>
              <div className="text-sm text-gray-400">Campañas Activas</div>
            </div>
            <div className="bg-gray-700/30 p-4 rounded-lg">
              <div className="text-2xl font-bold text-white">{dialerStatus.total_calls || 0}</div>
              <div className="text-sm text-gray-400">Total Llamadas</div>
            </div>
            <div className="bg-gray-700/30 p-4 rounded-lg">
              <div className="text-2xl font-bold text-white">{dialerStatus.concurrent_calls || 0}</div>
              <div className="text-sm text-gray-400">Llamadas Concurrentes</div>
            </div>
            <div className="bg-gray-700/30 p-4 rounded-lg">
              <div className={`text-2xl font-bold ${
                dialerStatus.asterisk_connected ? 'text-green-400' : 'text-red-400'
              }`}>
                {dialerStatus.asterisk_connected ? '🟢' : '🔴'}
              </div>
              <div className="text-sm text-gray-400">Asterisk</div>
            </div>
          </div>
          
          <div className="flex gap-4">
            <button
              onClick={startDialer}
              disabled={loading || dialerStatus.running}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors duration-200 flex items-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <span className="mr-2">🚀</span>
              )}
              Iniciar Discador
            </button>
            
            <button
              onClick={stopDialer}
              disabled={loading || !dialerStatus.running}
              className="px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors duration-200 flex items-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <span className="mr-2">🛑</span>
              )}
              Parar Discador
            </button>
          </div>
        </div>

        {/* Configuración del Discador */}
        <div className="bg-gray-800/40 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
          <div className="flex items-center mb-6">
            <span className="text-2xl mr-3">⚙️</span>
            <h3 className="text-xl font-semibold text-white">Configuración del Discador</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm text-gray-400 mb-2">CPS Máximo</label>
              <input
                type="number"
                min="1"
                max="50"
                value={dialerConfig.max_calls_per_second}
                onChange={(e) => setDialerConfig({...dialerConfig, max_calls_per_second: parseInt(e.target.value)})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:bg-gray-700/70 transition-all"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">CPS Mínimo</label>
              <input
                type="number"
                min="1"
                max="10"
                value={dialerConfig.min_calls_per_second}
                onChange={(e) => setDialerConfig({...dialerConfig, min_calls_per_second: parseInt(e.target.value)})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:bg-gray-700/70 transition-all"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">Taxa de Resposta Objetivo (%)</label>
              <input
                type="number"
                min="0.05"
                max="0.5"
                step="0.01"
                value={dialerConfig.target_answer_rate}
                onChange={(e) => setDialerConfig({...dialerConfig, target_answer_rate: parseFloat(e.target.value)})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:bg-gray-700/70 transition-all"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">Capacidade de Agentes</label>
              <input
                type="number"
                min="1"
                max="100"
                value={dialerConfig.agent_capacity}
                onChange={(e) => setDialerConfig({...dialerConfig, agent_capacity: parseInt(e.target.value)})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:bg-gray-700/70 transition-all"
              />
            </div>
          </div>
          
          <div className="mt-6">
            <button
              onClick={updateDialerConfig}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors duration-200 flex items-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <span className="mr-2">💾</span>
              )}
              Guardar Configuración
            </button>
          </div>
        </div>

        {/* Campanhas Ativas */}
        <div className="bg-gray-800/40 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
          <div className="flex items-center mb-6">
            <span className="text-2xl mr-3">📋</span>
            <h3 className="text-xl font-semibold text-white">Campañas Activas</h3>
          </div>
          
          {campaigns.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <span className="text-4xl block mb-2">📭</span>
              <p>No hay campañas activas</p>
              <p className="text-sm">Inicie una campaña desde la gestión de campañas</p>
            </div>
          ) : (
            <div className="space-y-4">
              {campaigns.map((campaign) => (
                <div key={campaign.campaign_id} className="flex items-center justify-between bg-gray-700/30 p-4 rounded-lg border border-gray-600/30">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <span className="text-white font-medium">{campaign.name}</span>
                      <span className="text-gray-400 text-sm ml-2">ID: {campaign.campaign_id}</span>
                    </div>
                    <div className="text-sm text-gray-400 mt-1">
                      CLI: {campaign.cli_number}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      campaign.status === 'active' 
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                        : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                    }`}>
                      {campaign.status === 'active' ? '● Activa' : '⏸ Pausada'}
                    </span>
                    
                    <div className="flex space-x-1">
                      {campaign.status === 'active' ? (
                        <button
                          onClick={() => controlCampaign(campaign.campaign_id, 'pause')}
                          disabled={loading}
                          className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white text-xs rounded transition-colors"
                        >
                          ⏸ Pausar
                        </button>
                      ) : (
                        <button
                          onClick={() => controlCampaign(campaign.campaign_id, 'resume')}
                          disabled={loading}
                          className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white text-xs rounded transition-colors"
                        >
                          ▶ Retomar
                        </button>
                      )}
                      
                      <button
                        onClick={() => controlCampaign(campaign.campaign_id, 'stop')}
                        disabled={loading}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white text-xs rounded transition-colors"
                      >
                        🛑 Parar
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DialerControl;