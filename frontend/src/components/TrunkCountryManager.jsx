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
    { code: '55', name: 'Brasil', flag: '🇧🇷' },
    { code: '57', name: 'Colombia', flag: '🇨🇴' },
    { code: '52', name: 'México', flag: '🇲🇽' },
    { code: '1', name: 'USA/Canadá', flag: '🇺🇸' },
    { code: '51', name: 'Perú', flag: '🇵🇪' },
    { code: '56', name: 'Chile', flag: '🇨🇱' },
    { code: '54', name: 'Argentina', flag: '🇦🇷' },
    { code: '34', name: 'España', flag: '🇪🇸' }
  ];

  const dvCodePresets = {
    '55': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10'], // Brasil
    '57': ['01', '02', '03', '04', '05'], // Colombia
    '52': ['01', '02', '03'], // México
    '1': ['011', '012', '013'], // USA
    '51': ['01', '02'], // Perú
    '56': ['01', '02'], // Chile
    '54': ['01', '02'], // Argentina
    '34': ['01', '02'] // España
  };

  const codecOptions = ['g729', 'ulaw', 'alaw', 'g722', 'gsm', 'ilbc', 'opus'];

  const fetchTrunks = async () => {
    try {
      setError(null);
      const response = await makeApiRequest('/trunks');
      if (response?.trunks) {
        setTrunks(response.trunks);
      }
    } catch (err) {
      console.error('Erro ao buscar trunks:', err);
      setError('Erro ao carregar trunks do servidor');
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
      const endpoint = editingTrunk ? `/trunks/${editingTrunk.id}` : '/trunks';
      const method = editingTrunk ? 'PUT' : 'POST';
      
      await makeApiRequest(endpoint, {
        method,
        data: formData
      });

      await fetchTrunks();
      resetForm();
      setShowModal(false);
    } catch (err) {
      setError('Erro ao salvar trunk');
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
    if (window.confirm('¿Está seguro de que desea eliminar este trunk?')) {
      try {
        await makeApiRequest(`/trunks/${trunkId}`, { method: 'DELETE' });
        await fetchTrunks();
      } catch (err) {
        setError('Erro ao deletar trunk');
      }
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

  const handleCountryChange = (countryCode) => {
    setFormData(prev => ({
      ...prev,
      country_code: countryCode,
      dv_codes: dvCodePresets[countryCode] || [],
      name: `trunk_${countryOptions.find(c => c.code === countryCode)?.name.toLowerCase() || 'unknown'}`
    }));
  };

  const addDvCode = () => {
    const newCode = prompt('Ingrese el código DV:');
    if (newCode && !formData.dv_codes.includes(newCode)) {
      setFormData(prev => ({
        ...prev,
        dv_codes: [...prev.dv_codes, newCode]
      }));
    }
  };

  const removeDvCode = (code) => {
    setFormData(prev => ({
      ...prev,
      dv_codes: prev.dv_codes.filter(c => c !== code)
    }));
  };

  const getCountryFlag = (countryCode) => {
    return countryOptions.find(c => c.code === countryCode)?.flag || '🌐';
  };

  const getStatusColor = (isActive) => {
    return isActive ? 'text-green-400' : 'text-red-400';
  };

  const generateAsteriskConfig = (trunk) => {
    const config = `[${trunk.name}]
type=${trunk.sip_config.type}
host=${trunk.host}
dtmfmode=${trunk.sip_config.dtmfmode}
disallow=${trunk.sip_config.disallow}
allow=${trunk.sip_config.allow.join(',')}
directmedia=${trunk.sip_config.directmedia}
qualify=${trunk.sip_config.qualify ? 'yes' : 'no'}
; Códigos DV: ${trunk.dv_codes?.join(', ') || 'N/A'}
; País: ${countryOptions.find(c => c.code === trunk.country_code)?.name || 'Desconocido'}`;

    navigator.clipboard.writeText(config);
    alert('Configuración copiada al portapapeles');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full"></div>
        <span className="ml-3 text-secondary-300">Cargando trunks...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gradient-primary flex items-center">
            🌐 Gerenciamento de Trunks por País
          </h1>
          <p className="text-secondary-400 mt-1">
            Configure trunks SIP com códigos de país e DV
          </p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setShowModal(true);
          }}
          className="btn-primary flex items-center space-x-2"
        >
          <span>+</span>
          <span>Novo Trunk</span>
        </button>
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

      {/* Trunks Grid */}
      {trunks.length === 0 ? (
        <div className="glass-panel p-12 text-center">
          <span className="text-6xl mb-4 block">🌐</span>
          <h3 className="text-xl font-semibold text-white mb-2">Nenhum trunk configurado</h3>
          <p className="text-secondary-400 mb-6">Comece criando seu primeiro trunk por país</p>
          <button
            onClick={() => {
              resetForm();
              setShowModal(true);
            }}
            className="btn-primary"
          >
            + Novo Trunk
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trunks.map((trunk) => (
            <div key={trunk.id} className="glass-panel p-6 hover:border-primary-500/30 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{getCountryFlag(trunk.country_code)}</span>
                  <div>
                    <h3 className="font-semibold text-white">{trunk.name}</h3>
                    <p className="text-sm text-secondary-400">{trunk.host}</p>
                  </div>
                </div>
                <span className={`w-3 h-3 rounded-full ${trunk.is_active ? 'bg-green-400' : 'bg-red-400'}`}></span>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">País:</span>
                  <span className="text-white">
                    {countryOptions.find(c => c.code === trunk.country_code)?.name || 'N/A'} (+{trunk.country_code})
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Canais:</span>
                  <span className="text-white">{trunk.max_channels}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Tipo:</span>
                  <span className="text-white uppercase">{trunk.trunk_type}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Status:</span>
                  <span className={getStatusColor(trunk.is_active)}>
                    {trunk.is_active ? 'Ativo' : 'Inativo'}
                  </span>
                </div>
              </div>

              {/* DV Codes */}
              {trunk.dv_codes && trunk.dv_codes.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-secondary-300 mb-2">Códigos DV:</h4>
                  <div className="flex flex-wrap gap-1">
                    {trunk.dv_codes.map((code, index) => (
                      <span key={index} className="px-2 py-1 bg-primary-600/20 text-primary-300 rounded text-xs">
                        {code}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(trunk)}
                  className="flex-1 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 px-3 py-2 rounded text-sm transition-colors"
                >
                  ✏️ Editar
                </button>
                <button
                  onClick={() => generateAsteriskConfig(trunk)}
                  className="flex-1 bg-green-600/20 hover:bg-green-600/30 text-green-300 px-3 py-2 rounded text-sm transition-colors"
                >
                  📋 Config
                </button>
                <button
                  onClick={() => handleDelete(trunk.id)}
                  className="bg-red-600/20 hover:bg-red-600/30 text-red-300 px-3 py-2 rounded text-sm transition-colors"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="glass-panel max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="border-b border-secondary-700 p-6">
              <h2 className="text-xl font-semibold text-white">
                {editingTrunk ? 'Editar Trunk' : 'Nuevo Trunk'}
              </h2>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* País */}
              <div>
                <label className="block text-sm font-medium text-secondary-300 mb-2">
                  País *
                </label>
                <select
                  value={formData.country_code}
                  onChange={(e) => handleCountryChange(e.target.value)}
                  className="input-field"
                  required
                >
                  <option value="">Seleccione un país</option>
                  {countryOptions.map((country) => (
                    <option key={country.code} value={country.code}>
                      {country.flag} {country.name} (+{country.code})
                    </option>
                  ))}
                </select>
              </div>

              {/* Nome e Host */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-300 mb-2">
                    Nome do Trunk *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="input-field"
                    placeholder="trunk_brasil"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-300 mb-2">
                    Host/IP *
                  </label>
                  <input
                    type="text"
                    value={formData.host}
                    onChange={(e) => setFormData(prev => ({ ...prev, host: e.target.value }))}
                    className="input-field"
                    placeholder="136.243.32.61"
                    required
                  />
                </div>
              </div>

              {/* Canais e Tipo */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-300 mb-2">
                    Máx. Canais
                  </label>
                  <input
                    type="number"
                    value={formData.max_channels}
                    onChange={(e) => setFormData(prev => ({ ...prev, max_channels: parseInt(e.target.value) }))}
                    className="input-field"
                    min="1"
                    max="100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-300 mb-2">
                    Tipo de Trunk
                  </label>
                  <select
                    value={formData.trunk_type}
                    onChange={(e) => setFormData(prev => ({ ...prev, trunk_type: e.target.value }))}
                    className="input-field"
                  >
                    <option value="dv_voip">DV VoIP</option>
                    <option value="standard_sip">SIP Padrão</option>
                    <option value="pstn">PSTN</option>
                  </select>
                </div>
              </div>

              {/* Códigos DV */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-secondary-300">
                    Códigos DV
                  </label>
                  <button
                    type="button"
                    onClick={addDvCode}
                    className="text-primary-400 hover:text-primary-300 text-sm"
                  >
                    + Adicionar
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.dv_codes.map((code, index) => (
                    <span key={index} className="flex items-center space-x-1 px-2 py-1 bg-primary-600/20 text-primary-300 rounded text-sm">
                      <span>{code}</span>
                      <button
                        type="button"
                        onClick={() => removeDvCode(code)}
                        className="text-red-400 hover:text-red-300"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Codecs */}
              <div>
                <label className="block text-sm font-medium text-secondary-300 mb-2">
                  Codecs Permitidos
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {codecOptions.map((codec) => (
                    <label key={codec} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.sip_config.allow.includes(codec)}
                        onChange={(e) => {
                          const newAllow = e.target.checked
                            ? [...formData.sip_config.allow, codec]
                            : formData.sip_config.allow.filter(c => c !== codec);
                          setFormData(prev => ({
                            ...prev,
                            sip_config: { ...prev.sip_config, allow: newAllow }
                          }));
                        }}
                        className="rounded bg-secondary-700 border-secondary-600 text-primary-500 focus:ring-primary-500"
                      />
                      <span className="text-sm text-secondary-300">{codec}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-4 pt-4 border-t border-secondary-700">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="btn-secondary flex-1"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="btn-primary flex-1"
                >
                  {editingTrunk ? 'Actualizar' : 'Crear'} Trunk
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