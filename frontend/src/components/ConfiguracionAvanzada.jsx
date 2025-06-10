import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const ConfiguracionAvanzada = () => {
  const [activeSection, setActiveSection] = useState('multi-sip');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Estados para Multi-SIP
  const [provedores, setProvedores] = useState([]);
  const [nuevoProvedor, setNuevoProvedor] = useState({
    nome: '',
    servidor_sip: '',
    porta: 5060,
    usuario_sip: '',
    senha_sip: '',
    status: 'ativo'
  });

  // Estados para CODE2BASE
  const [clis, setClis] = useState([]);
  const [novoCli, setNovoCli] = useState({
    numero: '',
    nombre: '',
    prefijo_codigo: '',
    operadora: '',
    activo: true
  });

  // Estados para Áudio Inteligente
  const [contextosAudio, setContextosAudio] = useState([]);
  const [novoContexto, setNovoContexto] = useState({
    nome: '',
    timeout_dtmf_padrao: 10,
    detectar_voicemail: true,
    audio_principal_url: ''
  });

  useEffect(() => {
    if (activeSection === 'multi-sip') {
      cargarProvedores();
    } else if (activeSection === 'code2base') {
      cargarClis();
    } else if (activeSection === 'audio') {
      cargarContextosAudio();
    }
  }, [activeSection]);

  // MULTI-SIP Functions
  const cargarProvedores = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/multi-sip/provedores');
      setProvedores(response || []);
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al cargar provedores: ' + error.message });
      // Mock data for demo
      setProvedores([
        { id: 1, nome: 'Provedor Demo', servidor_sip: 'sip.demo.com', status: 'ativo' },
        { id: 2, nome: 'Backup SIP', servidor_sip: 'backup.sip.com', status: 'inativo' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const crearProvedor = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await makeApiRequest('/multi-sip/provedores', {
        method: 'POST',
        body: JSON.stringify(nuevoProvedor)
      });
      setMessage({ type: 'success', text: 'Provedor creado exitosamente!' });
      setNuevoProvedor({ nome: '', servidor_sip: '', porta: 5060, usuario_sip: '', senha_sip: '', status: 'ativo' });
      cargarProvedores();
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al crear provedor: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  // CODE2BASE Functions
  const cargarClis = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/code2base/clis');
      setClis(response || []);
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al cargar CLIs: ' + error.message });
      // Mock data for demo
      setClis([
        { id: 1, numero: '+5491112345678', nombre: 'CLI Principal', operadora: 'CLARO', activo: true },
        { id: 2, numero: '+5491187654321', nombre: 'CLI Secundario', operadora: 'MOVISTAR', activo: false }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const crearCli = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await makeApiRequest('/code2base/clis', {
        method: 'POST',
        body: JSON.stringify(novoCli)
      });
      setMessage({ type: 'success', text: 'CLI creado exitosamente!' });
      setNovoCli({ numero: '', nombre: '', prefijo_codigo: '', operadora: '', activo: true });
      cargarClis();
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al crear CLI: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const testarSeleccionCli = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/code2base/seleccionar', {
        method: 'POST',
        body: JSON.stringify({
          numero_destino: '+5491112345678',
          campaña_id: 1
        })
      });
      setMessage({ type: 'success', text: 'CLI seleccionado: ' + JSON.stringify(response) });
    } catch (error) {
      setMessage({ type: 'error', text: 'Error en test: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  // AUDIO Functions
  const cargarContextosAudio = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/audio/contextos');
      setContextosAudio(response || []);
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al cargar contextos: ' + error.message });
      // Mock data for demo
      setContextosAudio([
        { id: 1, nome: 'Presione 1 Padrao', detectar_voicemail: true, timeout_dtmf_padrao: 10 },
        { id: 2, nome: 'IVR Personalizado', detectar_voicemail: false, timeout_dtmf_padrao: 15 }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const crearContextoAudio = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await makeApiRequest('/audio/contextos', {
        method: 'POST',
        body: JSON.stringify(novoContexto)
      });
      setMessage({ type: 'success', text: 'Contexto de audio creado exitosamente!' });
      setNovoContexto({ nome: '', timeout_dtmf_padrao: 10, detectar_voicemail: true, audio_principal_url: '' });
      cargarContextosAudio();
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al crear contexto: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const setupAudioPadrao = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/audio/setup-padrao', {
        method: 'POST'
      });
      setMessage({ type: 'success', text: 'Setup de audio padrão realizado com sucesso!' });
      cargarContextosAudio();
    } catch (error) {
      setMessage({ type: 'error', text: 'Error en setup: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const renderMultiSip = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">📡 Gestão Multi-SIP</h3>
        
        {/* Formulário Novo Provedor */}
        <form onSubmit={crearProvedor} className="grid grid-cols-2 gap-4 mb-6">
          <input
            type="text"
            placeholder="Nome do Provedor"
            value={nuevoProvedor.nome}
            onChange={(e) => setNuevoProvedor({...nuevoProvedor, nome: e.target.value})}
            className="bg-gray-700 text-white p-2 rounded"
            required
          />
          <input
            type="text"
            placeholder="Servidor SIP"
            value={nuevoProvedor.servidor_sip}
            onChange={(e) => setNuevoProvedor({...nuevoProvedor, servidor_sip: e.target.value})}
            className="bg-gray-700 text-white p-2 rounded"
            required
          />
          <input
            type="number"
            placeholder="Porta"
            value={nuevoProvedor.porta}
            onChange={(e) => setNuevoProvedor({...nuevoProvedor, porta: parseInt(e.target.value)})}
            className="bg-gray-700 text-white p-2 rounded"
            required
          />
          <input
            type="text"
            placeholder="Usuário SIP"
            value={nuevoProvedor.usuario_sip}
            onChange={(e) => setNuevoProvedor({...nuevoProvedor, usuario_sip: e.target.value})}
            className="bg-gray-700 text-white p-2 rounded"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="col-span-2 bg-blue-600 hover:bg-blue-700 text-white p-2 rounded disabled:opacity-50"
          >
            {loading ? 'Criando...' : 'Criar Provedor'}
          </button>
        </form>

        {/* Lista Provedores */}
        <div className="bg-gray-700 rounded p-4">
          <h4 className="text-white font-medium mb-3">Provedores Configurados:</h4>
          {provedores.length === 0 ? (
            <p className="text-gray-400">Nenhum provedor configurado</p>
          ) : (
            provedores.map((provedor) => (
              <div key={provedor.id} className="flex justify-between items-center bg-gray-600 p-3 rounded mb-2">
                <div>
                  <span className="text-white font-medium">{provedor.nome}</span>
                  <span className="text-gray-300 ml-2">({provedor.servidor_sip})</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  provedor.status === 'ativo' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                }`}>
                  {provedor.status}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );

  const renderCode2base = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">🎯 CODE2BASE - Seleção Inteligente CLI</h3>
        
        {/* Formulário Novo CLI */}
        <form onSubmit={crearCli} className="grid grid-cols-2 gap-4 mb-6">
          <input
            type="text"
            placeholder="Número CLI (+5491112345678)"
            value={novoCli.numero}
            onChange={(e) => setNovoCli({...novoCli, numero: e.target.value})}
            className="bg-gray-700 text-white p-2 rounded"
            required
          />
          <input
            type="text"
            placeholder="Nome do CLI"
            value={novoCli.nombre}
            onChange={(e) => setNovoCli({...novoCli, nombre: e.target.value})}
            className="bg-gray-700 text-white p-2 rounded"
            required
          />
          <input
            type="text"
            placeholder="Prefixo Código"
            value={novoCli.prefijo_codigo}
            onChange={(e) => setNovoCli({...novoCli, prefijo_codigo: e.target.value})}
            className="bg-gray-700 text-white p-2 rounded"
          />
          <select
            value={novoCli.operadora}
            onChange={(e) => setNovoCli({...novoCli, operadora: e.target.value})}
            className="bg-gray-700 text-white p-2 rounded"
            required
          >
            <option value="">Selecionar Operadora</option>
            <option value="CLARO">CLARO</option>
            <option value="MOVISTAR">MOVISTAR</option>
            <option value="PERSONAL">PERSONAL</option>
            <option value="OTROS">OUTROS</option>
          </select>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded disabled:opacity-50"
          >
            {loading ? 'Criando...' : 'Criar CLI'}
          </button>
          <button
            type="button"
            onClick={testarSeleccionCli}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white p-2 rounded disabled:opacity-50"
          >
            🧪 Testar Seleção
          </button>
        </form>

        {/* Lista CLIs */}
        <div className="bg-gray-700 rounded p-4">
          <h4 className="text-white font-medium mb-3">CLIs Configurados:</h4>
          {clis.length === 0 ? (
            <p className="text-gray-400">Nenhum CLI configurado</p>
          ) : (
            clis.map((cli) => (
              <div key={cli.id} className="flex justify-between items-center bg-gray-600 p-3 rounded mb-2">
                <div>
                  <span className="text-white font-medium">{cli.numero}</span>
                  <span className="text-gray-300 ml-2">({cli.nombre})</span>
                  <span className="text-blue-300 ml-2">{cli.operadora}</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  cli.activo ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                }`}>
                  {cli.activo ? 'Ativo' : 'Inativo'}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );

  const renderAudioInteligente = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">🤖 Áudio Inteligente</h3>
        
        {/* Setup Rápido */}
        <div className="bg-blue-900 border border-blue-700 rounded p-4 mb-6">
          <h4 className="text-blue-100 font-medium mb-2">⚡ Setup Rápido</h4>
          <p className="text-blue-200 text-sm mb-3">Configure automaticamente o sistema "Presione 1" padrão</p>
          <button
            onClick={setupAudioPadrao}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {loading ? 'Configurando...' : '🚀 Setup Automático'}
          </button>
        </div>

        {/* Formulário Novo Contexto */}
        <form onSubmit={crearContextoAudio} className="grid grid-cols-2 gap-4 mb-6">
          <input
            type="text"
            placeholder="Nome do Contexto"
            value={novoContexto.nome}
            onChange={(e) => setNovoContexto({...novoContexto, nome: e.target.value})}
            className="bg-gray-700 text-white p-2 rounded"
            required
          />
          <input
            type="number"
            placeholder="Timeout DTMF (segundos)"
            value={novoContexto.timeout_dtmf_padrao}
            onChange={(e) => setNovoContexto({...novoContexto, timeout_dtmf_padrao: parseInt(e.target.value)})}
            className="bg-gray-700 text-white p-2 rounded"
            required
          />
          <input
            type="url"
            placeholder="URL do Áudio Principal"
            value={novoContexto.audio_principal_url}
            onChange={(e) => setNovoContexto({...novoContexto, audio_principal_url: e.target.value})}
            className="bg-gray-700 text-white p-2 rounded"
          />
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={novoContexto.detectar_voicemail}
              onChange={(e) => setNovoContexto({...novoContexto, detectar_voicemail: e.target.checked})}
              className="mr-2"
            />
            <label className="text-white">Detectar Voicemail</label>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="col-span-2 bg-purple-600 hover:bg-purple-700 text-white p-2 rounded disabled:opacity-50"
          >
            {loading ? 'Criando...' : 'Criar Contexto de Áudio'}
          </button>
        </form>

        {/* Lista Contextos */}
        <div className="bg-gray-700 rounded p-4">
          <h4 className="text-white font-medium mb-3">Contextos de Áudio:</h4>
          {contextosAudio.length === 0 ? (
            <p className="text-gray-400">Nenhum contexto configurado</p>
          ) : (
            contextosAudio.map((contexto) => (
              <div key={contexto.id} className="flex justify-between items-center bg-gray-600 p-3 rounded mb-2">
                <div>
                  <span className="text-white font-medium">{contexto.nome}</span>
                  <span className="text-gray-300 ml-2">Timeout: {contexto.timeout_dtmf_padrao}s</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  contexto.detectar_voicemail ? 'bg-purple-600 text-white' : 'bg-gray-600 text-white'
                }`}>
                  {contexto.detectar_voicemail ? '🎵 Detecta VM' : '📞 Só Voz'}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="container mx-auto px-4 py-6">
      <h2 className="text-2xl font-bold text-white mb-6">⚙️ Configuração Avançada</h2>
      
      {/* Message Display */}
      {message.text && (
        <div className={`p-4 rounded mb-6 ${
          message.type === 'success' ? 'bg-green-900 border border-green-700 text-green-100' :
          'bg-red-900 border border-red-700 text-red-100'
        }`}>
          {message.text}
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-6">
        <button
          onClick={() => setActiveSection('multi-sip')}
          className={`px-4 py-2 rounded-t-lg transition-colors ${
            activeSection === 'multi-sip' 
              ? 'bg-gray-800 text-white border-b-2 border-blue-500' 
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          📡 Multi-SIP
        </button>
        <button
          onClick={() => setActiveSection('code2base')}
          className={`px-4 py-2 rounded-t-lg transition-colors ${
            activeSection === 'code2base' 
              ? 'bg-gray-800 text-white border-b-2 border-green-500' 
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          🎯 CODE2BASE
        </button>
        <button
          onClick={() => setActiveSection('audio')}
          className={`px-4 py-2 rounded-t-lg transition-colors ${
            activeSection === 'audio' 
              ? 'bg-gray-800 text-white border-b-2 border-purple-500' 
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          🤖 Áudio Inteligente
        </button>
      </div>

      {/* Content */}
      <div className="bg-gray-900 rounded-lg p-6">
        {activeSection === 'multi-sip' && renderMultiSip()}
        {activeSection === 'code2base' && renderCode2base()}
        {activeSection === 'audio' && renderAudioInteligente()}
      </div>
    </div>
  );
};

export default ConfiguracionAvanzada; 