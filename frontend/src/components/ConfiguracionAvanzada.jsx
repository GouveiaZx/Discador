import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config/api';

const makeMultiSipRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  console.log('🔧 Multi-SIP Request:', { url, method: config.method || 'GET' });

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Multi-SIP Success:', { url, data });
    return data;
  } catch (error) {
    console.error('❌ Multi-SIP Error:', { url, error: error.message });
    throw error;
  }
};

function ConfiguracionAvanzada() {
  const [provedores, setProvedores] = useState([]);
  const [nuevoProvedor, setNuevoProvedor] = useState({
    nombre: '',
    servidor_sip: '',
    puerto: 5060,
    usuario_sip: '',
    contraseña_sip: '',
    estado: 'activo'
  });

  const [clis, setClis] = useState([]);
  const [nuevoCLI, setNuevoCLI] = useState({
    numero: '',
    proveedor_id: '',
    activo: true
  });

  const [contextos, setContextos] = useState([]);
  const [nuevoContexto, setNuevoContexto] = useState({
    nombre: '',
    timeout_dtmf_predeterminado: 10,
    detectar_voicemail: true,
    audio_principal_url: ''
  });

  const [configuracion, setConfiguracion] = useState({});
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarProvedores();
    cargarCLIs();
    cargarContextos();
    cargarConfiguracion();
  }, []);

  const cargarProvedores = async () => {
    try {
      const response = await makeMultiSipRequest('/api/v1/multi-sip/provedores');
      if (response && response.provedores) {
        setProvedores(response.provedores);
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al cargar proveedores: ' + error.message });
    }
  };

  const crearProvedor = async () => {
    try {
      setLoading(true);
      const response = await makeMultiSipRequest('/api/v1/multi-sip/provedores', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(nuevoProvedor)
      });

      if (response && response.status === 'success') {
        setMessage({ type: 'success', text: 'Proveedor creado exitosamente!' });
        cargarProvedores();
        setNuevoProvedor({ nombre: '', servidor_sip: '', puerto: 5060, usuario_sip: '', contraseña_sip: '', estado: 'activo' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al crear proveedor: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const cargarCLIs = async () => {
    try {
      const response = await makeMultiSipRequest('/api/v1/code2base/clis');
      if (response && response.clis) {
        setClis(response.clis);
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al cargar CLIs: ' + error.message });
    }
  };

  const crearCLI = async () => {
    try {
      setLoading(true);
      const response = await makeMultiSipRequest('/api/v1/code2base/clis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(nuevoCLI)
      });

      if (response && response.status === 'success') {
        setMessage({ type: 'success', text: 'CLI creado exitosamente!' });
        cargarCLIs();
        setNuevoCLI({ numero: '', proveedor_id: '', activo: true });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al crear CLI: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const testarConexao = async () => {
    try {
      setLoading(true);
      const response = await makeMultiSipRequest('/api/v1/configuracion-avanzada/status');
      if (response && response.status === 'success') {
        setMessage({ type: 'success', text: 'Conexión exitosa! Sistema funcionando correctamente.' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error en test: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const cargarContextos = async () => {
    try {
      const response = await makeMultiSipRequest('/api/v1/audios/contextos');
      if (response && response.contextos) {
        setContextos(response.contextos);
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al cargar contextos: ' + error.message });
    }
  };

  const crearContexto = async () => {
    try {
      setLoading(true);
      const response = await makeMultiSipRequest('/api/v1/audio/contextos', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(nuevoContexto)
      });

      if (response && response.status === 'success') {
        setMessage({ type: 'success', text: 'Contexto creado exitosamente!' });
        cargarContextos();
        setNuevoContexto({ nombre: '', timeout_dtmf_predeterminado: 10, detectar_voicemail: true, audio_principal_url: '' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al crear contexto: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const setupAudioPredeterminado = async () => {
    try {
      setLoading(true);
      const response = await makeMultiSipRequest('/api/v1/audio/setup-padrao', {
        method: 'POST'
      });
      setMessage({ type: 'success', text: response.message || 'Setup de audio predeterminado realizado con éxito!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Error en setup: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const cargarConfiguracion = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/configuracion`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setConfiguracion(data);
      setError(null);
    } catch (err) {
      console.error('Erro ao carregar configuração:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-6">⚙️ Configuración Avanzada</h2>
        </div>

        {/* Mensajes */}
        {message && (
          <div className={`p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-500/20 border border-green-500/50 text-green-200' 
              : 'bg-red-500/20 border border-red-500/50 text-red-200'
          }`}>
            {message.text}
          </div>
        )}

        {/* Grid de configuraciones */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Gestión Multi-SIP */}
          <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">📡 Gestión Multi-SIP</h3>
            
            {/* Agregar Proveedor */}
            <div className="space-y-4 mb-6">
              <input
                type="text"
                placeholder="Nombre del Proveedor"
                value={nuevoProvedor.nombre}
                onChange={(e) => setNuevoProvedor({...nuevoProvedor, nombre: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
              />
              
              <input
                type="text"
                placeholder="Servidor SIP"
                value={nuevoProvedor.servidor_sip}
                onChange={(e) => setNuevoProvedor({...nuevoProvedor, servidor_sip: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
              />
              
              <input
                type="number"
                placeholder="Puerto"
                value={nuevoProvedor.puerto}
                onChange={(e) => setNuevoProvedor({...nuevoProvedor, puerto: parseInt(e.target.value)})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
              />
              
              <input
                type="text"
                placeholder="Usuario SIP"
                value={nuevoProvedor.usuario_sip}
                onChange={(e) => setNuevoProvedor({...nuevoProvedor, usuario_sip: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
              />
              
              <input
                type="password"
                placeholder="Contraseña SIP"
                value={nuevoProvedor.contraseña_sip}
                onChange={(e) => setNuevoProvedor({...nuevoProvedor, contraseña_sip: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
              />
              
              <button
                onClick={crearProvedor}
                disabled={loading}
                className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors"
              >
                {loading ? 'Creando...' : 'Crear Proveedor'}
              </button>
            </div>

            {/* Lista Proveedores */}
            <div className="space-y-2">
              <h4 className="text-white font-medium">Proveedores Configurados</h4>
              {provedores.map((proveedor, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-700/50 p-3 rounded-lg">
                  <div>
                    <span className="text-white font-medium">{proveedor.nombre}</span>
                    <span className="text-gray-400 text-sm ml-2">({proveedor.servidor_sip})</span>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    proveedor.estado === 'activo' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                  }`}>
                    {proveedor.estado}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Gestión de CLIs */}
          <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">📞 Gestión de CLIs</h3>
            
            {/* Agregar CLI */}
            <div className="space-y-4 mb-6">
              <input
                type="text"
                placeholder="Número del CLI"
                value={nuevoCLI.numero}
                onChange={(e) => setNuevoCLI({...nuevoCLI, numero: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
              />
              
              <select
                value={nuevoCLI.proveedor_id}
                onChange={(e) => setNuevoCLI({...nuevoCLI, proveedor_id: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white"
              >
                <option value="">Seleccionar Proveedor</option>
                {provedores.map((proveedor, index) => (
                  <option key={index} value={proveedor.id || index}>
                    {proveedor.nombre}
                  </option>
                ))}
              </select>
              
              <button
                onClick={crearCLI}
                disabled={loading}
                className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors"
              >
                {loading ? 'Creando...' : 'Crear CLI'}
              </button>

              <button
                onClick={testarConexao}
                disabled={loading}
                className="w-full px-4 py-3 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors"
              >
                {loading ? 'Probando...' : 'Probar Conexión'}
              </button>
            </div>

            {/* Lista CLIs */}
            <div className="space-y-2">
              <h4 className="text-white font-medium">CLIs Configurados</h4>
              {clis.map((cli, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-700/50 p-3 rounded-lg">
                  <div>
                    <span className="text-white font-medium">{cli.numero}</span>
                    <span className="text-gray-400 text-sm ml-2">({cli.proveedor_nome || 'Sin proveedor'})</span>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    cli.activo ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                  }`}>
                    {cli.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sistema de Audio */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">🎵 Sistema de Audio Inteligente</h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Setup Rápido */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <h4 className="text-blue-100 font-medium mb-2">⚡ Setup Rápido</h4>
              <p className="text-blue-200 text-sm mb-3">Configure automáticamente el sistema "Presione 1" predeterminado</p>
              <button
                onClick={setupAudioPredeterminado}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded transition-colors"
              >
                {loading ? 'Configurando...' : '🚀 Setup Automático'}
              </button>
            </div>

            {/* Crear contexto personalizado */}
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Nombre del Contexto"
                value={nuevoContexto.nombre}
                onChange={(e) => setNuevoContexto({...nuevoContexto, nombre: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
              />
              
              <input
                type="number"
                placeholder="Timeout DTMF (segundos)"
                value={nuevoContexto.timeout_dtmf_predeterminado}
                onChange={(e) => setNuevoContexto({...nuevoContexto, timeout_dtmf_predeterminado: parseInt(e.target.value)})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
              />
              
              <input
                type="url"
                placeholder="URL Audio Principal"
                value={nuevoContexto.audio_principal_url}
                onChange={(e) => setNuevoContexto({...nuevoContexto, audio_principal_url: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
              />
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="detectar_voicemail"
                  checked={nuevoContexto.detectar_voicemail}
                  onChange={(e) => setNuevoContexto({...nuevoContexto, detectar_voicemail: e.target.checked})}
                  className="rounded"
                />
                <label htmlFor="detectar_voicemail" className="text-white text-sm">
                  Detectar Voicemail
                </label>
              </div>
              
              <button
                onClick={crearContexto}
                disabled={loading}
                className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors"
              >
                {loading ? 'Creando...' : 'Crear Contexto'}
              </button>
            </div>
          </div>

          {/* Lista Contextos */}
          <div className="mt-6 space-y-2">
            <h4 className="text-white font-medium">Contextos de Audio</h4>
            {contextos.map((contexto, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-700/50 p-3 rounded-lg">
                <div>
                  <span className="text-white font-medium">{contexto.nombre}</span>
                  <span className="text-gray-400 text-sm ml-2">
                    (Timeout: {contexto.timeout_dtmf_predeterminado}s)
                  </span>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  contexto.detectar_voicemail ? 'bg-green-600 text-white' : 'bg-yellow-600 text-white'
                }`}>
                  {contexto.detectar_voicemail ? 'Con VM' : 'Sin VM'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ConfiguracionAvanzada; 