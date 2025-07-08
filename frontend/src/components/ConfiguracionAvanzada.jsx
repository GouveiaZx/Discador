import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config/api';

const makeApiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}/api/v1${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  console.log('🔧 API Request:', { url, method: config.method || 'GET' });

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ API Success:', { url, data });
    return data;
  } catch (error) {
    console.error('❌ API Error:', { url, error: error.message });
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

  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarProvedores();
    cargarCLIs();
    cargarContextos();
  }, []);

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const cargarProvedores = async () => {
    try {
      const response = await makeApiRequest('/multi-sip/provedores');
      if (response && response.provedores) {
        setProvedores(response.provedores);
      }
    } catch (error) {
      showMessage('error', 'Error al cargar proveedores: ' + error.message);
    }
  };

  const crearProvedor = async () => {
    if (!nuevoProvedor.nombre || !nuevoProvedor.servidor_sip) {
      showMessage('error', 'Por favor, complete todos los campos obligatorios');
      return;
    }

    try {
      setLoading(true);
      const response = await makeApiRequest('/multi-sip/provedores', {
        method: 'POST',
        body: JSON.stringify(nuevoProvedor)
      });

      if (response && response.status === 'success') {
        showMessage('success', '¡Proveedor creado exitosamente!');
        cargarProvedores();
        setNuevoProvedor({ 
          nombre: '', 
          servidor_sip: '', 
          puerto: 5060, 
          usuario_sip: '', 
          contraseña_sip: '', 
          estado: 'activo' 
        });
      }
    } catch (error) {
      showMessage('error', 'Error al crear proveedor: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const cargarCLIs = async () => {
    try {
      const response = await makeApiRequest('/code2base/clis');
      if (response && response.clis) {
        setClis(response.clis);
      }
    } catch (error) {
      showMessage('error', 'Error al cargar CLIs: ' + error.message);
    }
  };

  const crearCLI = async () => {
    if (!nuevoCLI.numero) {
      showMessage('error', 'Por favor, ingrese un número de CLI');
      return;
    }

    try {
      setLoading(true);
      const response = await makeApiRequest('/code2base/clis', {
        method: 'POST',
        body: JSON.stringify(nuevoCLI)
      });

      if (response && response.status === 'success') {
        showMessage('success', '¡CLI creado exitosamente!');
        cargarCLIs();
        setNuevoCLI({ numero: '', proveedor_id: '', activo: true });
      }
    } catch (error) {
      showMessage('error', 'Error al crear CLI: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const cargarContextos = async () => {
    try {
      const response = await makeApiRequest('/audios/contextos');
      if (response && response.contextos) {
        setContextos(response.contextos);
      }
    } catch (error) {
      showMessage('error', 'Error al cargar contextos: ' + error.message);
    }
  };

  const crearContexto = async () => {
    if (!nuevoContexto.nombre) {
      showMessage('error', 'Por favor, ingrese un nombre para el contexto');
      return;
    }

    try {
      setLoading(true);
      const response = await makeApiRequest('/audio/contextos', {
        method: 'POST',
        body: JSON.stringify(nuevoContexto)
      });

      if (response && response.status === 'success') {
        showMessage('success', '¡Contexto creado exitosamente!');
        cargarContextos();
        setNuevoContexto({ 
          nombre: '', 
          timeout_dtmf_predeterminado: 10, 
          detectar_voicemail: true, 
          audio_principal_url: '' 
        });
      }
    } catch (error) {
      showMessage('error', 'Error al crear contexto: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const setupAudioPredeterminado = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/audio/setup-padrao', {
        method: 'POST'
      });
      showMessage('success', response.message || '¡Setup de audio predeterminado realizado con éxito!');
    } catch (error) {
      showMessage('error', 'Error en setup: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const testarConexao = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/configuracion-avanzada/status');
      if (response && response.status === 'success') {
        showMessage('success', '¡Conexión exitosa! Sistema funcionando correctamente.');
      }
    } catch (error) {
      showMessage('error', 'Error en test: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white mb-4">⚙️ Configuración Avanzada del Sistema</h2>
          <p className="text-gray-400">Gestión de proveedores SIP, CLIs y sistema de audio inteligente</p>
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

        {/* Grid de configuraciones principales */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Gestión Multi-SIP */}
          <div className="bg-gray-800/40 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">📡</span>
              <h3 className="text-xl font-semibold text-white">Gestión Multi-SIP</h3>
            </div>
            
            {/* Formulario de Proveedor */}
            <div className="space-y-4 mb-6">
              <input
                type="text"
                placeholder="Nombre del Proveedor *"
                value={nuevoProvedor.nombre}
                onChange={(e) => setNuevoProvedor({...nuevoProvedor, nombre: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:bg-gray-700/70 transition-all"
              />
              
              <input
                type="text"
                placeholder="Servidor SIP *"
                value={nuevoProvedor.servidor_sip}
                onChange={(e) => setNuevoProvedor({...nuevoProvedor, servidor_sip: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:bg-gray-700/70 transition-all"
              />
              
              <div className="grid grid-cols-2 gap-4">
                <input
                  type="number"
                  placeholder="Puerto"
                  value={nuevoProvedor.puerto}
                  onChange={(e) => setNuevoProvedor({...nuevoProvedor, puerto: parseInt(e.target.value) || 5060})}
                  className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:bg-gray-700/70 transition-all"
                />
                
                <select
                  value={nuevoProvedor.estado}
                  onChange={(e) => setNuevoProvedor({...nuevoProvedor, estado: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white focus:outline-none focus:border-blue-500 focus:bg-gray-700/70 transition-all"
                >
                  <option value="activo">Activo</option>
                  <option value="inactivo">Inactivo</option>
                </select>
              </div>
              
              <input
                type="text"
                placeholder="Usuario SIP"
                value={nuevoProvedor.usuario_sip}
                onChange={(e) => setNuevoProvedor({...nuevoProvedor, usuario_sip: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:bg-gray-700/70 transition-all"
              />
              
              <input
                type="password"
                placeholder="Contraseña SIP"
                value={nuevoProvedor.contraseña_sip}
                onChange={(e) => setNuevoProvedor({...nuevoProvedor, contraseña_sip: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:bg-gray-700/70 transition-all"
              />
              
              <button
                onClick={crearProvedor}
                disabled={loading}
                className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors duration-200 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creando...
                  </>
                ) : (
                  '+ Crear Proveedor'
                )}
              </button>
            </div>

            {/* Lista de Proveedores */}
            <div className="space-y-3">
              <h4 className="text-white font-medium text-sm uppercase tracking-wide">Proveedores Configurados</h4>
              {provedores.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <span className="text-4xl block mb-2">🌐</span>
                  <p>No hay proveedores configurados</p>
                  <p className="text-sm">Agregue el primer proveedor SIP</p>
                </div>
              ) : (
                provedores.map((proveedor, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-700/30 p-4 rounded-lg border border-gray-600/30">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <span className="text-white font-medium">{proveedor.nombre}</span>
                        <span className="text-gray-400 text-sm ml-2">({proveedor.servidor_sip}:{proveedor.puerto})</span>
                      </div>
                      {proveedor.usuario_sip && (
                        <p className="text-gray-400 text-sm mt-1">Usuario: {proveedor.usuario_sip}</p>
                      )}
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      proveedor.estado === 'activo' 
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                        : 'bg-red-500/20 text-red-400 border border-red-500/30'
                    }`}>
                      {proveedor.estado === 'activo' ? '● Activo' : '○ Inactivo'}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Gestión de CLIs */}
          <div className="bg-gray-800/40 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">📞</span>
              <h3 className="text-xl font-semibold text-white">Gestión de CLIs</h3>
            </div>
            
            {/* Formulario CLI */}
            <div className="space-y-4 mb-6">
              <input
                type="text"
                placeholder="Número del CLI (ej: +541123456789)"
                value={nuevoCLI.numero}
                onChange={(e) => setNuevoCLI({...nuevoCLI, numero: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-green-500 focus:bg-gray-700/70 transition-all"
              />
              
              <select
                value={nuevoCLI.proveedor_id}
                onChange={(e) => setNuevoCLI({...nuevoCLI, proveedor_id: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white focus:outline-none focus:border-green-500 focus:bg-gray-700/70 transition-all"
              >
                <option value="">Seleccionar Proveedor (opcional)</option>
                {provedores.map((proveedor, index) => (
                  <option key={index} value={proveedor.id || index}>
                    {proveedor.nombre}
                  </option>
                ))}
              </select>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="cli_activo"
                  checked={nuevoCLI.activo}
                  onChange={(e) => setNuevoCLI({...nuevoCLI, activo: e.target.checked})}
                  className="rounded border-gray-600 text-green-600 focus:ring-green-500"
                />
                <label htmlFor="cli_activo" className="text-white text-sm">
                  CLI activo por defecto
                </label>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={crearCLI}
                  disabled={loading}
                  className="px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors duration-200 flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Creando...
                    </>
                  ) : (
                    '+ Crear CLI'
                  )}
                </button>

                <button
                  onClick={testarConexao}
                  disabled={loading}
                  className="px-4 py-3 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors duration-200 flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Probando...
                    </>
                  ) : (
                    '🔍 Probar Conexión'
                  )}
                </button>
              </div>
            </div>

            {/* Lista CLIs */}
            <div className="space-y-3">
              <h4 className="text-white font-medium text-sm uppercase tracking-wide">CLIs Configurados</h4>
              {clis.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <span className="text-4xl block mb-2">📱</span>
                  <p>No hay CLIs configurados</p>
                  <p className="text-sm">Agregue el primer CLI</p>
                </div>
              ) : (
                clis.map((cli, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-700/30 p-4 rounded-lg border border-gray-600/30">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <span className="text-white font-medium">{cli.numero}</span>
                        {cli.proveedor_nome && (
                          <span className="text-gray-400 text-sm ml-2">({cli.proveedor_nome})</span>
                        )}
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      cli.activo 
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                        : 'bg-red-500/20 text-red-400 border border-red-500/30'
                    }`}>
                      {cli.activo ? '● Activo' : '○ Inactivo'}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Sistema de Audio Inteligente */}
        <div className="bg-gray-800/40 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
          <div className="flex items-center mb-6">
            <span className="text-2xl mr-3">🎵</span>
            <h3 className="text-xl font-semibold text-white">Sistema de Audio Inteligente</h3>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Setup Rápido */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
              <div className="text-center mb-4">
                <span className="text-3xl block mb-2">⚡</span>
                <h4 className="text-blue-100 font-medium text-lg">Setup Rápido</h4>
                <p className="text-blue-200/80 text-sm mt-2">
                  Configure automáticamente el sistema "Presione 1" con configuraciones predeterminadas optimizadas
                </p>
              </div>
              <button
                onClick={setupAudioPredeterminado}
                disabled={loading}
                className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors duration-200 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Configurando...
                  </>
                ) : (
                  '🚀 Configurar Automáticamente'
                )}
              </button>
            </div>

            {/* Crear contexto personalizado */}
            <div className="space-y-4">
              <h4 className="text-white font-medium text-lg">Crear Contexto Personalizado</h4>
              
              <input
                type="text"
                placeholder="Nombre del Contexto *"
                value={nuevoContexto.nombre}
                onChange={(e) => setNuevoContexto({...nuevoContexto, nombre: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:bg-gray-700/70 transition-all"
              />
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Timeout DTMF (seg)</label>
                  <input
                    type="number"
                    min="5"
                    max="60"
                    value={nuevoContexto.timeout_dtmf_predeterminado}
                    onChange={(e) => setNuevoContexto({...nuevoContexto, timeout_dtmf_predeterminado: parseInt(e.target.value) || 10})}
                    className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:bg-gray-700/70 transition-all"
                  />
                </div>
                
                <div className="flex items-end">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="detectar_voicemail"
                      checked={nuevoContexto.detectar_voicemail}
                      onChange={(e) => setNuevoContexto({...nuevoContexto, detectar_voicemail: e.target.checked})}
                      className="rounded border-gray-600 text-purple-600 focus:ring-purple-500"
                    />
                    <label htmlFor="detectar_voicemail" className="text-white text-sm">
                      Detectar Voicemail
                    </label>
                  </div>
                </div>
              </div>
              
              <input
                type="url"
                placeholder="URL Audio Principal (opcional)"
                value={nuevoContexto.audio_principal_url}
                onChange={(e) => setNuevoContexto({...nuevoContexto, audio_principal_url: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:bg-gray-700/70 transition-all"
              />
              
              <button
                onClick={crearContexto}
                disabled={loading}
                className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors duration-200 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creando...
                  </>
                ) : (
                  '+ Crear Contexto'
                )}
              </button>
            </div>
          </div>

          {/* Lista de Contextos */}
          <div className="mt-8 space-y-3">
            <h4 className="text-white font-medium text-sm uppercase tracking-wide">Contextos de Audio</h4>
            {contextos.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <span className="text-4xl block mb-2">🎼</span>
                <p>No hay contextos de audio configurados</p>
                <p className="text-sm">Use el setup rápido o cree un contexto personalizado</p>
              </div>
            ) : (
              contextos.map((contexto, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-700/30 p-4 rounded-lg border border-gray-600/30">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <span className="text-white font-medium">{contexto.nombre}</span>
                      <span className="text-gray-400 text-sm ml-2">
                        (Timeout: {contexto.timeout_dtmf_predeterminado}s)
                      </span>
                    </div>
                    {contexto.audio_principal_url && (
                      <p className="text-gray-400 text-sm mt-1 truncate">
                        Audio: {contexto.audio_principal_url}
                      </p>
                    )}
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    contexto.detectar_voicemail 
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                      : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                  }`}>
                    {contexto.detectar_voicemail ? '🔍 Con VM' : '📞 Sin VM'}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Nota informativa */}
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
          <div className="flex items-start">
            <span className="text-2xl mr-3">💡</span>
            <div>
              <h4 className="text-blue-100 font-medium mb-2">Información sobre la Configuración</h4>
              <ul className="text-blue-200/80 text-sm space-y-1">
                <li>• Los proveedores SIP permiten realizar llamadas a través de diferentes operadores</li>
                <li>• Los CLIs definen qué números aparecerán como identificador de llamada</li>
                <li>• Los contextos de audio gestionan cómo se reproducen los mensajes durante las llamadas</li>
                <li>• La gestión de Trunks SIP está disponible en la sección dedicada "Gestión Trunks"</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ConfiguracionAvanzada; 