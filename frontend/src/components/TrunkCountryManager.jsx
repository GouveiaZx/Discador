import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const TrunkCountryManager = () => {
  const [trunks, setTrunks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTrunk, setEditingTrunk] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    host: '',
    country_code: '',
    dv_codes: [],
    trunk_type: 'dv_voip',
    sip_config: {
      type: 'friend',
      dtmfmode: 'rfc2833',
      allow: ['g729'],
      disallow: 'all',
      directmedia: 'nonat',
      qualify: true
    }
  });

  const countries = [
    { code: '55', name: 'Brasil', flag: '🇧🇷' },
    { code: '1', name: 'USA/Canadá', flag: '🇺🇸' },
    { code: '52', name: 'México', flag: '🇲🇽' },
    { code: '57', name: 'Colômbia', flag: '🇨🇴' },
    { code: '51', name: 'Peru', flag: '🇵🇪' },
    { code: '56', name: 'Chile', flag: '🇨🇱' },
    { code: '54', name: 'Argentina', flag: '🇦🇷' },
    { code: '58', name: 'Venezuela', flag: '🇻🇪' }
  ];

  const dvCodeOptions = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10'
  ];

  const loadTrunks = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/trunks');
      setTrunks(response.data || []);
    } catch (error) {
      console.error('Erro ao carregar trunks:', error);
      setTrunks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrunks();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const trunkData = {
        ...formData,
        name: formData.name || `trunk_${getCountryName(formData.country_code).toLowerCase()}`,
        sip_config: JSON.stringify(formData.sip_config)
      };

      if (editingTrunk) {
        await makeApiRequest(`/trunks/${editingTrunk.id}`, 'PUT', trunkData);
      } else {
        await makeApiRequest('/trunks', 'POST', trunkData);
      }
      
      setShowForm(false);
      setEditingTrunk(null);
      resetForm();
      loadTrunks();
    } catch (error) {
      console.error('Erro ao salvar trunk:', error);
      alert('Erro ao salvar trunk. Tente novamente.');
    }
  };

  const handleEdit = (trunk) => {
    setEditingTrunk(trunk);
    setFormData({
      name: trunk.name,
      host: trunk.host,
      country_code: trunk.country_code || '',
      dv_codes: trunk.dv_codes || [],
      trunk_type: trunk.trunk_type || 'dv_voip',
      sip_config: typeof trunk.sip_config === 'string' 
        ? JSON.parse(trunk.sip_config) 
        : trunk.sip_config || {}
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir este trunk?')) {
      try {
        await makeApiRequest(`/trunks/${id}`, 'DELETE');
        loadTrunks();
      } catch (error) {
        console.error('Erro ao excluir trunk:', error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      host: '',
      country_code: '',
      dv_codes: [],
      trunk_type: 'dv_voip',
      sip_config: {
        type: 'friend',
        dtmfmode: 'rfc2833',
        allow: ['g729'],
        disallow: 'all',
        directmedia: 'nonat',
        qualify: true
      }
    });
    setEditingTrunk(null);
  };

  const getCountryName = (code) => {
    const country = countries.find(c => c.code === code);
    return country ? country.name : 'Desconhecido';
  };

  const getCountryFlag = (code) => {
    const country = countries.find(c => c.code === code);
    return country ? country.flag : '🌐';
  };

  const generateSipConfig = (trunkData) => {
    const config = trunkData.sip_config || {};
    return `[${trunkData.name}]
type=${config.type || 'friend'}
host=${trunkData.host}
dtmfmode=${config.dtmfmode || 'rfc2833'}
disallow=${config.disallow || 'all'}
allow=${Array.isArray(config.allow) ? config.allow.join(',') : 'g729'}
directmedia=${config.directmedia || 'nonat'}
qualify=${config.qualify ? 'yes' : 'no'}
`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Carregando trunks...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">🌍 Gerenciamento de Trunks por País</h2>
          <p className="text-gray-600 mt-1">Configure trunks SIP com códigos de país e DV</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Novo Trunk
        </button>
      </div>

      {/* Formulário Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-90vh overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">
              {editingTrunk ? 'Editar Trunk' : 'Novo Trunk'}
            </h3>
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Trunk</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="trunk_brasil"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Host/IP</label>
                  <input
                    type="text"
                    value={formData.host}
                    onChange={(e) => setFormData({...formData, host: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="136.243.32.61"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">País</label>
                  <select
                    value={formData.country_code}
                    onChange={(e) => setFormData({...formData, country_code: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Selecione o país</option>
                    {countries.map(country => (
                      <option key={country.code} value={country.code}>
                        {country.flag} {country.name} (+{country.code})
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Trunk</label>
                  <select
                    value={formData.trunk_type}
                    onChange={(e) => setFormData({...formData, trunk_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="dv_voip">DV VoIP</option>
                    <option value="standard">Padrão</option>
                    <option value="residential">Residencial</option>
                    <option value="business">Empresarial</option>
                  </select>
                </div>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Códigos DV Disponíveis</label>
                <div className="grid grid-cols-5 gap-2">
                  {dvCodeOptions.map(code => (
                    <label key={code} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={formData.dv_codes.includes(code)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({
                              ...formData,
                              dv_codes: [...formData.dv_codes, code]
                            });
                          } else {
                            setFormData({
                              ...formData,
                              dv_codes: formData.dv_codes.filter(c => c !== code)
                            });
                          }
                        }}
                        className="rounded text-blue-600"
                      />
                      <span className="text-sm">{code}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Configuração SIP</label>
                <textarea
                  value={generateSipConfig(formData)}
                  readOnly
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                  rows={8}
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingTrunk ? 'Atualizar' : 'Criar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lista de Trunks */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {trunks.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <div className="text-6xl mb-4 opacity-50">🌐</div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhum trunk configurado</h3>
            <p className="mt-1 text-sm text-gray-500">Comece criando seu primeiro trunk por país</p>
          </div>
        ) : (
          trunks.map((trunk) => (
            <div key={trunk.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{getCountryFlag(trunk.country_code)}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">{trunk.name}</h3>
                    <p className="text-sm text-gray-500">+{trunk.country_code} {getCountryName(trunk.country_code)}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  trunk.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {trunk.is_active ? 'Ativo' : 'Inativo'}
                </span>
              </div>
              
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Host:</span>
                  <span className="font-mono">{trunk.host}</span>
                </div>
                <div className="flex justify-between">
                  <span>Tipo:</span>
                  <span className="capitalize">{trunk.trunk_type}</span>
                </div>
                {trunk.dv_codes && trunk.dv_codes.length > 0 && (
                  <div className="flex justify-between">
                    <span>Códigos DV:</span>
                    <span className="font-mono">{trunk.dv_codes.join(', ')}</span>
                  </div>
                )}
              </div>
              
              <div className="flex justify-between items-center mt-4 pt-3 border-t">
                <button
                  onClick={() => handleEdit(trunk)}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(trunk.id)}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Excluir
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TrunkCountryManager; 