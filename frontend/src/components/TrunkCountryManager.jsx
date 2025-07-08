import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const TrunkCountryManager = () => {
  const [trunks, setTrunks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTrunk, setEditingTrunk] = useState(null);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    name: '',
    host: '',
    country_code: '',
    dv_codes: [],
    max_channels: 10,
    trunk_type: 'dv_voip',
    sip_config: {
      type: 'friend',
      allow: ['g729'],
      disallow: 'all',
      dtmfmode: 'rfc2833',
      directmedia: 'nonat',
      qualify: true
    }
  });

  const countryOptions = [
    { code: '55', name: '🇧🇷 Brasil', flag: '🇧🇷' },
    { code: '1', name: '🇺🇸 Estados Unidos', flag: '🇺🇸' },
    { code: '57', name: '🇨🇴 Colombia', flag: '🇨🇴' },
    { code: '52', name: '🇲🇽 México', flag: '🇲🇽' },
    { code: '54', name: '🇦🇷 Argentina', flag: '🇦🇷' },
    { code: '51', name: '🇵🇪 Peru', flag: '🇵🇪' },
    { code: '56', name: '🇨🇱 Chile', flag: '🇨🇱' },
    { code: '34', name: '🇪🇸 España', flag: '🇪🇸' }
  ];

  const codecOptions = [
    { value: 'g729', label: 'G.729 (baixa largura de banda)' },
    { value: 'g722', label: 'G.722 (alta qualidade)' },
    { value: 'ulaw', label: 'μ-law (padrão NA)' },
    { value: 'alaw', label: 'A-law (padrão EU)' },
    { value: 'gsm', label: 'GSM (compatibilidade)' },
    { value: 'ilbc', label: 'iLBC (baixa largura)' },
    { value: 'opus', label: 'Opus (moderno)' }
  ];

  const fetchTrunks = async () => {
    try {
      setError(null);
      setLoading(true);
      const response = await makeApiRequest('trunks', 'GET');
      setTrunks(response.trunks || []);
    } catch (error) {
      console.error('Erro ao buscar trunks:', error);
      setError('Erro ao carregar trunks do servidor');
      setTrunks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrunks();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError(null);
      
      // Validações
      if (!formData.name || !formData.host || !formData.country_code) {
        setError('Por favor, preencha todos os campos obrigatórios');
        return;
      }

      const submitData = {
        ...formData,
        max_channels: parseInt(formData.max_channels) || 10,
        sip_config: {
          ...formData.sip_config,
          allow: Array.isArray(formData.sip_config.allow) 
            ? formData.sip_config.allow 
            : [formData.sip_config.allow]
        }
      };

      if (editingTrunk) {
        await makeApiRequest(`trunks/${editingTrunk.id}`, 'PUT', submitData);
      } else {
        await makeApiRequest('trunks', 'POST', submitData);
      }

      await fetchTrunks();
      setShowModal(false);
      resetForm();
    } catch (error) {
      console.error('Erro ao salvar trunk:', error);
      setError('Erro ao salvar trunk. Verifique os dados e tente novamente.');
    }
  };

  const handleEdit = (trunk) => {
    setEditingTrunk(trunk);
    setFormData({
      name: trunk.name || '',
      host: trunk.host || '',
      country_code: trunk.country_code || '',
      dv_codes: trunk.dv_codes || [],
      max_channels: trunk.max_channels || 10,
      trunk_type: trunk.trunk_type || 'dv_voip',
      sip_config: trunk.sip_config || {
        type: 'friend',
        allow: ['g729'],
        disallow: 'all',
        dtmfmode: 'rfc2833',
        directmedia: 'nonat',
        qualify: true
      }
    });
    setShowModal(true);
  };

  const handleDelete = async (trunkId) => {
    if (!window.confirm('Tem certeza que deseja deletar este trunk?')) return;
    
    try {
      await makeApiRequest(`trunks/${trunkId}`, 'DELETE');
      await fetchTrunks();
    } catch (error) {
      console.error('Erro ao deletar trunk:', error);
      setError('Erro ao deletar trunk');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      host: '',
      country_code: '',
      dv_codes: [],
      max_channels: 10,
      trunk_type: 'dv_voip',
      sip_config: {
        type: 'friend',
        allow: ['g729'],
        disallow: 'all',
        dtmfmode: 'rfc2833',
        directmedia: 'nonat',
        qualify: true
      }
    });
    setEditingTrunk(null);
  };

  const handleAddDvCode = () => {
    const newCode = document.getElementById('new-dv-code').value.trim();
    if (newCode && !formData.dv_codes.includes(newCode)) {
      setFormData(prev => ({
        ...prev,
        dv_codes: [...prev.dv_codes, newCode]
      }));
      document.getElementById('new-dv-code').value = '';
    }
  };

  const handleRemoveDvCode = (code) => {
    setFormData(prev => ({
      ...prev,
      dv_codes: prev.dv_codes.filter(c => c !== code)
    }));
  };

  const handleCodecChange = (codec, checked) => {
    setFormData(prev => ({
      ...prev,
      sip_config: {
        ...prev.sip_config,
        allow: checked 
          ? [...(prev.sip_config.allow || []), codec]
          : (prev.sip_config.allow || []).filter(c => c !== codec)
      }
    }));
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">🌐</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Gerenciamento de Trunks por País</h1>
        </div>
        <p className="text-gray-400">Configure trunks SIP com códigos de país e DV</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 bg-red-900/20 border border-red-500/50 rounded-lg p-4 flex items-center gap-3">
          <span className="text-red-400">⚠️</span>
          <div>
            <div className="text-red-400 font-medium">Erro</div>
            <div className="text-red-300 text-sm">{error}</div>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span className="ml-3 text-gray-400">Carregando trunks...</span>
          </div>
        ) : trunks.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🌐</span>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Nenhum trunk configurado</h3>
            <p className="text-gray-400 mb-6">Comece criando seu primeiro trunk por país</p>
            <button
              onClick={() => setShowModal(true)}
              className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-medium transition-colors"
            >
              + Novo Trunk
            </button>
          </div>
        ) : (
          <>
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="text-lg font-semibold text-white">Trunks Configurados</h3>
                <p className="text-gray-400 text-sm">{trunks.length} trunk(s) encontrado(s)</p>
              </div>
              <button
                onClick={() => setShowModal(true)}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                + Novo Trunk
              </button>
            </div>

            <div className="grid gap-4">
              {trunks.map((trunk) => {
                const country = countryOptions.find(c => c.code === trunk.country_code);
                return (
                  <div key={trunk.id} className="bg-gray-800/70 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="text-2xl">{country?.flag || '🌐'}</div>
                        <div>
                          <h4 className="font-medium text-white">{trunk.name}</h4>
                          <div className="text-sm text-gray-400">
                            {trunk.host} • +{trunk.country_code} • {trunk.max_channels} canais
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {trunk.dv_codes?.length > 0 ? `Códigos DV: ${trunk.dv_codes.join(', ')}` : 'Sem códigos DV'}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          trunk.is_active 
                            ? 'bg-green-900/30 text-green-400 border border-green-700/50' 
                            : 'bg-gray-900/30 text-gray-400 border border-gray-700/50'
                        }`}>
                          {trunk.is_active ? 'Ativo' : 'Inativo'}
                        </span>
                        <button
                          onClick={() => handleEdit(trunk)}
                          className="text-blue-400 hover:text-blue-300 p-2 rounded-lg hover:bg-blue-900/20 transition-colors"
                          title="Editar"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleDelete(trunk.id)}
                          className="text-red-400 hover:text-red-300 p-2 rounded-lg hover:bg-red-900/20 transition-colors"
                          title="Deletar"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 border border-gray-700 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <h2 className="text-xl font-semibold text-white">
                {editingTrunk ? 'Editar Trunk' : 'Novo Trunk'}
              </h2>
              <button
                onClick={() => {
                  setShowModal(false);
                  resetForm();
                }}
                className="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-gray-700/50 transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* Informações Básicas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* País */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    País <span className="text-red-400">*</span>
                  </label>
                  <select
                    value={formData.country_code}
                    onChange={(e) => setFormData(prev => ({...prev, country_code: e.target.value}))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Selecione um país</option>
                    {countryOptions.map(country => (
                      <option key={country.code} value={country.code}>
                        {country.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Nome do Trunk */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Nome do Trunk <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({...prev, name: e.target.value}))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="ex: trunk_brasil"
                    required
                  />
                </div>

                {/* Host/IP */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Host/IP <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.host}
                    onChange={(e) => setFormData(prev => ({...prev, host: e.target.value}))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="ex: 192.168.1.100"
                    required
                  />
                </div>

                {/* Máx. Canais */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Máx. Canais</label>
                  <input
                    type="number"
                    value={formData.max_channels}
                    onChange={(e) => setFormData(prev => ({...prev, max_channels: parseInt(e.target.value)}))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    min="1"
                    max="100"
                  />
                </div>

                {/* Tipo de Trunk */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Tipo de Trunk</label>
                  <select
                    value={formData.trunk_type}
                    onChange={(e) => setFormData(prev => ({...prev, trunk_type: e.target.value}))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="dv_voip">DV VoIP</option>
                    <option value="sip_trunk">SIP Trunk</option>
                    <option value="analog">Analógico</option>
                    <option value="digital">Digital</option>
                  </select>
                </div>
              </div>

              {/* Códigos DV */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Códigos DV</label>
                <div className="space-y-3">
                  <div className="flex gap-2">
                    <input
                      id="new-dv-code"
                      type="text"
                      className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="ex: 11, 21, 31"
                    />
                    <button
                      type="button"
                      onClick={handleAddDvCode}
                      className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-white transition-colors"
                    >
                      + Adicionar
                    </button>
                  </div>
                  {formData.dv_codes.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {formData.dv_codes.map(code => (
                        <span
                          key={code}
                          className="bg-blue-900/30 text-blue-300 px-2 py-1 rounded-lg text-sm flex items-center gap-1"
                        >
                          {code}
                          <button
                            type="button"
                            onClick={() => handleRemoveDvCode(code)}
                            className="text-blue-400 hover:text-blue-200 ml-1"
                          >
                            ✕
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Codecs Permitidos */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3">Codecs Permitidos</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {codecOptions.map(codec => (
                    <label key={codec.value} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={(formData.sip_config.allow || []).includes(codec.value)}
                        onChange={(e) => handleCodecChange(codec.value, e.target.checked)}
                        className="rounded border-gray-600 bg-gray-700 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-300">{codec.value}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Buttons */}
              <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  {editingTrunk ? 'Atualizar' : 'Criar'} Trunk
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrunkCountryManager; 