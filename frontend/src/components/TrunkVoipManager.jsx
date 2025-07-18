import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../services/api';

function TrunkVoipManager() {
  const [trunks, setTrunks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTrunk, setEditingTrunk] = useState(null);
  const [testingTrunk, setTestingTrunk] = useState(null);
  
  const [formData, setFormData] = useState({
    nome: '',
    host: '',
    porta: '5060',
    usuario: '',
    senha: '',
    contexto: 'from-trunk',
    codec: 'ulaw,alaw,g729',
    dtmf_mode: 'rfc2833',
    country_code: '',
    dial_prefix: '',
    max_channels: '30',
    qualify: 'yes',
    nat: 'force_rport,comedia',
    insecure: 'port,invite',
    type: 'peer',
    disallow: 'all',
    allow: 'ulaw,alaw,g729',
    fromuser: '',
    fromdomain: '',
    register_string: '',
    outbound_proxy: '',
    transport: 'udp',
    encryption: 'no',
    activo: true
  });

  useEffect(() => {
    fetchTrunks();
  }, []);

  const fetchTrunks = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/trunks');
      if (response?.trunks) {
        setTrunks(response.trunks);
      }
    } catch (err) {
      setError('Erro ao carregar trunks: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      if (editingTrunk) {
        await makeApiRequest(`/trunks/${editingTrunk.id}`, 'PUT', formData);
      } else {
        await makeApiRequest('/trunks', 'POST', formData);
      }
      
      await fetchTrunks();
      resetForm();
      setError(null);
    } catch (err) {
      setError('Erro ao salvar trunk: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (trunk) => {
    setEditingTrunk(trunk);
    setFormData({ ...trunk });
    setShowForm(true);
  };

  const handleDelete = async (trunkId) => {
    if (!confirm('Tem certeza que deseja excluir este trunk?')) return;
    
    try {
      setLoading(true);
      await makeApiRequest(`/trunks/${trunkId}`, 'DELETE');
      await fetchTrunks();
    } catch (err) {
      setError('Erro ao excluir trunk: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const testTrunkConnection = async (trunk) => {
    try {
      setTestingTrunk(trunk.id);
      const response = await makeApiRequest(`/trunks/${trunk.id}/test`, 'POST');
      
      if (response.success) {
        alert(`✅ Trunk ${trunk.nome} testado com sucesso!\n${response.message}`);
      } else {
        alert(`❌ Falha no teste do trunk ${trunk.nome}:\n${response.message}`);
      }
    } catch (err) {
      alert(`❌ Erro ao testar trunk: ${err.message}`);
    } finally {
      setTestingTrunk(null);
    }
  };

  const resetForm = () => {
    setFormData({
      nome: '',
      host: '',
      porta: '5060',
      usuario: '',
      senha: '',
      contexto: 'from-trunk',
      codec: 'ulaw,alaw,g729',
      dtmf_mode: 'rfc2833',
      country_code: '',
      dial_prefix: '',
      max_channels: '30',
      qualify: 'yes',
      nat: 'force_rport,comedia',
      insecure: 'port,invite',
      type: 'peer',
      disallow: 'all',
      allow: 'ulaw,alaw,g729',
      fromuser: '',
      fromdomain: '',
      register_string: '',
      outbound_proxy: '',
      transport: 'udp',
      encryption: 'no',
      activo: true
    });
    setEditingTrunk(null);
    setShowForm(false);
  };

  const generateSipConfig = (trunk) => {
    return `
[${trunk.nome}]
type=${trunk.type}
host=${trunk.host}
port=${trunk.porta}
username=${trunk.usuario}
secret=${trunk.senha}
context=${trunk.contexto}
dtmfmode=${trunk.dtmf_mode}
qualify=${trunk.qualify}
nat=${trunk.nat}
insecure=${trunk.insecure}
disallow=${trunk.disallow}
allow=${trunk.allow}
${trunk.fromuser ? `fromuser=${trunk.fromuser}` : ''}
${trunk.fromdomain ? `fromdomain=${trunk.fromdomain}` : ''}
${trunk.register_string ? `register => ${trunk.register_string}` : ''}
${trunk.outbound_proxy ? `outboundproxy=${trunk.outbound_proxy}` : ''}
transport=${trunk.transport}
`;
  };

  if (loading && trunks.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Gestão de Trunks VoIP</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          {showForm ? 'Cancelar' : 'Novo Trunk'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">
            {editingTrunk ? 'Editar Trunk' : 'Novo Trunk VoIP'}
          </h3>
          
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Informações Básicas */}
            <div className="col-span-full">
              <h4 className="font-medium text-gray-700 mb-2">📋 Informações Básicas</h4>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Trunk *</label>
              <input
                type="text"
                value={formData.nome}
                onChange={(e) => setFormData({...formData, nome: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                placeholder="Ex: Provedor_Principal"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Host/IP *</label>
              <input
                type="text"
                value={formData.host}
                onChange={(e) => setFormData({...formData, host: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                placeholder="sip.provedor.com ou 192.168.1.100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Porta</label>
              <input
                type="number"
                value={formData.porta}
                onChange={(e) => setFormData({...formData, porta: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="5060"
              />
            </div>

            {/* Autenticação */}
            <div className="col-span-full">
              <h4 className="font-medium text-gray-700 mb-2 mt-4">🔐 Autenticação</h4>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Usuário</label>
              <input
                type="text"
                value={formData.usuario}
                onChange={(e) => setFormData({...formData, usuario: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="username"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Senha</label>
              <input
                type="password"
                value={formData.senha}
                onChange={(e) => setFormData({...formData, senha: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="password"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">From User</label>
              <input
                type="text"
                value={formData.fromuser}
                onChange={(e) => setFormData({...formData, fromuser: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Opcional"
              />
            </div>

            {/* Configurações de Discagem */}
            <div className="col-span-full">
              <h4 className="font-medium text-gray-700 mb-2 mt-4">📞 Configurações de Discagem</h4>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Código do País</label>
              <input
                type="text"
                value={formData.country_code}
                onChange={(e) => setFormData({...formData, country_code: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: 52 (México), 1 (USA/Canadá)"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prefixo de Discagem</label>
              <input
                type="text"
                value={formData.dial_prefix}
                onChange={(e) => setFormData({...formData, dial_prefix: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: 9797 (código de saída)"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Máx. Canais</label>
              <input
                type="number"
                value={formData.max_channels}
                onChange={(e) => setFormData({...formData, max_channels: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="30"
              />
            </div>

            {/* Configurações Avançadas */}
            <div className="col-span-full">
              <h4 className="font-medium text-gray-700 mb-2 mt-4">⚙️ Configurações Avançadas</h4>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contexto</label>
              <input
                type="text"
                value={formData.contexto}
                onChange={(e) => setFormData({...formData, contexto: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="from-trunk"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Codecs</label>
              <input
                type="text"
                value={formData.allow}
                onChange={(e) => setFormData({...formData, allow: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="ulaw,alaw,g729"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">DTMF Mode</label>
              <select
                value={formData.dtmf_mode}
                onChange={(e) => setFormData({...formData, dtmf_mode: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="rfc2833">RFC2833</option>
                <option value="inband">Inband</option>
                <option value="info">SIP INFO</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Transport</label>
              <select
                value={formData.transport}
                onChange={(e) => setFormData({...formData, transport: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="udp">UDP</option>
                <option value="tcp">TCP</option>
                <option value="tls">TLS</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">NAT</label>
              <input
                type="text"
                value={formData.nat}
                onChange={(e) => setFormData({...formData, nat: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="force_rport,comedia"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">String de Registro</label>
              <input
                type="text"
                value={formData.register_string}
                onChange={(e) => setFormData({...formData, register_string: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="user:pass@host:port"
              />
            </div>

            <div className="col-span-full flex justify-end space-x-4 mt-6">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Salvando...' : (editingTrunk ? 'Atualizar' : 'Criar Trunk')}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de Trunks */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold">Trunks Configurados ({trunks.length})</h3>
        </div>
        
        {trunks.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>Nenhum trunk configurado ainda.</p>
            <p className="text-sm mt-2">Clique em "Novo Trunk" para começar.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Host</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">País</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prefixo</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {trunks.map((trunk) => (
                  <tr key={trunk.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{trunk.nome}</div>
                      <div className="text-sm text-gray-500">Canais: {trunk.max_channels || 'N/A'}</div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{trunk.host}:{trunk.porta}</div>
                      <div className="text-sm text-gray-500">{trunk.transport?.toUpperCase()}</div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      {trunk.country_code || 'N/A'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      {trunk.dial_prefix || 'N/A'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        trunk.activo 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {trunk.activo ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      <button
                        onClick={() => testTrunkConnection(trunk)}
                        disabled={testingTrunk === trunk.id}
                        className="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                        title="Testar Conexão"
                      >
                        {testingTrunk === trunk.id ? '🔄' : '🔍'}
                      </button>
                      <button
                        onClick={() => handleEdit(trunk)}
                        className="text-indigo-600 hover:text-indigo-900"
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => {
                          const config = generateSipConfig(trunk);
                          navigator.clipboard.writeText(config);
                          alert('Configuração SIP copiada para a área de transferência!');
                        }}
                        className="text-green-600 hover:text-green-900"
                        title="Copiar Config SIP"
                      >
                        📋
                      </button>
                      <button
                        onClick={() => handleDelete(trunk.id)}
                        className="text-red-600 hover:text-red-900"
                        title="Excluir"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default TrunkVoipManager;