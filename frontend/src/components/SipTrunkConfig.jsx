import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const SipTrunkConfig = () => {
  const [trunks, setTrunks] = useState([]);
  const [selectedTrunk, setSelectedTrunk] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);

  const [trunkConfig, setTrunkConfig] = useState({
    nombre: '',
    tipo: 'friend', // friend, peer, user
    host: '',
    porta: 5060,
    usuario: '',
    senha: '',
    protocolo: 'UDP',
    contexto: 'from-trunk',
    
    // Codecs
    codec_preferido: 'ulaw',
    codecs_permitidos: ['ulaw', 'alaw', 'g729'],
    
    // Configuraciones de Enrutamiento y Códigos de Proveedor
    prefixo_discagem: '',
    sufixo_discagem: '',
    codigo_pais: '+1',
    codigo_area_default: '',
    
    // Configuraciones SIP
    nat: 'auto_force_rport',
    qualify: 'yes',
    canreinvite: 'no',
    dtmfmode: 'rfc2833',
    disallow: 'all',
    
    // Limitaciones
    call_limit: 10,
    max_forwards: 20,
    max_canais_simultaneos: 10,
    
    // Configuraciones avanzadas
    fromuser: '',
    fromdomain: '',
    outboundproxy: '',
    registertimeout: 20,
    registerattempts: 10,
    callerid_in_from: 'no',
    trustrpid: 'no',
    sendrpid: 'no',
    
    // Timeouts
    rtptimeout: 60,
    rtpholdtimeout: 300,
    
    // Seguridad
    encryption: 'no',
    auth_user: '',
    secret: '',
    
    // Status
    ativo: true,
    registro_obrigatorio: false
  });

  const codecOptions = [
    { value: 'ulaw', label: 'μ-law (G.711)', description: 'Buena calidad, alto ancho de banda' },
    { value: 'alaw', label: 'a-law (G.711)', description: 'Buena calidad, alto ancho de banda' },
    { value: 'g729', label: 'G.729', description: 'Bajo ancho de banda, licencia necesaria' },
    { value: 'g722', label: 'G.722', description: 'HD Audio, ancho de banda medio' },
    { value: 'gsm', label: 'GSM', description: 'Baja calidad, bajo ancho de banda' },
    { value: 'ilbc', label: 'iLBC', description: 'Bueno para conexiones inestables' },
    { value: 'opus', label: 'Opus', description: 'Codec moderno, adaptativo' }
  ];

  const tipoOptions = [
    { value: 'friend', label: 'Friend', description: 'Puede hacer y recibir llamadas' },
    { value: 'peer', label: 'Peer', description: 'Solo recibir llamadas' },
    { value: 'user', label: 'User', description: 'Solo hacer llamadas' }
  ];

  const natOptions = [
    { value: 'auto_force_rport', label: 'Auto Force RPort', description: 'Detectar NAT automáticamente' },
    { value: 'force_rport', label: 'Force RPort', description: 'Forzar uso de RPort' },
    { value: 'auto_comedia', label: 'Auto Comedia', description: 'Detectar media automáticamente' },
    { value: 'yes', label: 'Yes', description: 'NAT habilitado' },
    { value: 'no', label: 'No', description: 'NAT deshabilitado' }
  ];

  const loadTrunks = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/trunks');
      setTrunks(response.data || []);
    } catch (error) {
      // Sistema real - mostrar datos reales del backend
      setTrunks([]);
    } finally {
      setLoading(false);
    }
  };

  const loadTrunkConfig = async (trunkId) => {
    try {
      const response = await makeApiRequest(`/trunks/${trunkId}/sip-config`);
      setTrunkConfig(response || trunkConfig);
    } catch (error) {
      // Mantener configuración por defecto en caso de error
    }
  };

  const handleTrunkSelect = (trunk) => {
    setSelectedTrunk(trunk);
    setIsEditMode(false);
    loadTrunkConfig(trunk.id);
  };

  const handleNewTrunk = () => {
    setSelectedTrunk(null);
    setIsEditMode(true);
    setTrunkConfig({
      nombre: '',
      tipo: 'friend',
      host: '',
      porta: 5060,
      usuario: '',
      senha: '',
      protocolo: 'UDP',
      contexto: 'from-trunk',
      codec_preferido: 'ulaw',
      codecs_permitidos: ['ulaw', 'alaw', 'g729'],
      prefixo_discagem: '',
      sufixo_discagem: '',
      codigo_pais: '+1',
      codigo_area_default: '',
      nat: 'auto_force_rport',
      qualify: 'yes',
      canreinvite: 'no',
      dtmfmode: 'rfc2833',
      disallow: 'all',
      call_limit: 10,
      max_forwards: 20,
      max_canais_simultaneos: 10,
      fromuser: '',
      fromdomain: '',
      outboundproxy: '',
      registertimeout: 20,
      registerattempts: 10,
      callerid_in_from: 'no',
      trustrpid: 'no',
      sendrpid: 'no',
      rtptimeout: 60,
      rtpholdtimeout: 300,
      encryption: 'no',
      auth_user: '',
      secret: '',
      ativo: true,
      registro_obrigatorio: false
    });
  };

  const handleSaveConfig = async () => {
    try {
      setSaving(true);
      
      let endpoint = '';
      let method = 'PUT';
      
      if (isEditMode && !selectedTrunk) {
        // Creando nuevo trunk
        endpoint = '/trunks';
        method = 'POST';
      } else if (selectedTrunk) {
        // Actualizando trunk existente
        endpoint = `/trunks/${selectedTrunk.id}/sip-config`;
        method = 'PUT';
      }

      const response = await makeApiRequest(endpoint, {
        method: method,
        body: JSON.stringify(trunkConfig)
      });
      
      if (isEditMode && !selectedTrunk) {
        // Recargar la lista después de crear
        await loadTrunks();
        setIsEditMode(false);
        alert('Trunk creado con éxito!');
      } else {
        alert('Configuración SIP guardada con éxito!');
      }
    } catch (error) {
      alert('Error al guardar configuración. Inténtelo de nuevo.');
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    if (!selectedTrunk) return;

    try {
      setTesting(true);
      const response = await makeApiRequest(`/trunks/${selectedTrunk.id}/test-connection`, {
        method: 'POST'
      });
      
      if (response.resultado === 'sucesso') {
        alert(`✅ Prueba de conexión realizada con éxito!\nTiempo de respuesta: ${response.tempo_resposta}ms`);
      } else {
        alert(`❌ Falla en la prueba de conexión.\nMotivo: ${response.mensagem}`);
      }
    } catch (error) {
      alert('❌ Error al probar conexión. Verifique las configuraciones.');
    } finally {
      setTesting(false);
    }
  };

  const handleCodecToggle = (codec) => {
    setTrunkConfig(prev => ({
      ...prev,
      codecs_permitidos: prev.codecs_permitidos.includes(codec)
        ? prev.codecs_permitidos.filter(c => c !== codec)
        : [...prev.codecs_permitidos, codec]
    }));
  };

  const generateAsteriskConfig = () => {
    const config = `[${trunkConfig.nombre}]
type=${trunkConfig.tipo}
host=${trunkConfig.host}
port=${trunkConfig.porta}
username=${trunkConfig.usuario}
secret=${trunkConfig.senha}
context=${trunkConfig.contexto}
nat=${trunkConfig.nat}
qualify=${trunkConfig.qualify}
canreinvite=${trunkConfig.canreinvite}
dtmfmode=${trunkConfig.dtmfmode}
disallow=${trunkConfig.disallow}
${trunkConfig.codecs_permitidos.map(codec => `allow=${codec}`).join('\n')}
call-limit=${trunkConfig.call_limit}
${trunkConfig.fromuser ? `fromuser=${trunkConfig.fromuser}` : ''}
${trunkConfig.fromdomain ? `fromdomain=${trunkConfig.fromdomain}` : ''}
${trunkConfig.outboundproxy ? `outboundproxy=${trunkConfig.outboundproxy}` : ''}
registertimeout=${trunkConfig.registertimeout}
registerattempts=${trunkConfig.registerattempts}
callerid_in_from=${trunkConfig.callerid_in_from}
trustrpid=${trunkConfig.trustrpid}
sendrpid=${trunkConfig.sendrpid}
rtptimeout=${trunkConfig.rtptimeout}
rtpholdtimeout=${trunkConfig.rtpholdtimeout}
encryption=${trunkConfig.encryption}

; === Configuraciones de Enrutamiento ===
${trunkConfig.prefixo_discagem ? `; Prefijo de marcado: ${trunkConfig.prefixo_discagem}` : ''}
${trunkConfig.sufixo_discagem ? `; Sufijo de marcado: ${trunkConfig.sufixo_discagem}` : ''}
${trunkConfig.codigo_pais ? `; Código del país: ${trunkConfig.codigo_pais}` : ''}
${trunkConfig.codigo_area_default ? `; Código de área por defecto: ${trunkConfig.codigo_area_default}` : ''}

; === Configuraciones de Capacidad ===
max_channels=${trunkConfig.max_canais_simultaneos}

; === Configuraciones de Caller ID ===
${trunkConfig.callerid_padrao ? `callerid=${trunkConfig.callerid_padrao}` : ''}
${trunkConfig.permitir_callerid_personalizado ? '; Caller ID personalizado por campaña: habilitado' : '; Caller ID personalizado por campaña: deshabilitado'}`;

    return config;
  };

  useEffect(() => {
    loadTrunks();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Cargando trunks SIP...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Cabeçalho */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">📡 Configuração SIP Trunks</h2>
            <p className="text-gray-600 mt-1">Configure trunks SIP no Asterisk</p>
          </div>
          <button
            onClick={handleNewTrunk}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Novo Trunk
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Lista de Trunks */}
        <div className="lg:col-span-1">
          <h3 className="text-lg font-semibold mb-4">📋 Trunks SIP</h3>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {trunks.map((trunk) => (
              <div
                key={trunk.id}
                onClick={() => handleTrunkSelect(trunk)}
                className={`p-3 border rounded-lg cursor-pointer transition-all ${
                  selectedTrunk?.id === trunk.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="font-medium text-gray-800">{trunk.nombre}</div>
                <div className="text-sm text-gray-500">{trunk.host}:{trunk.porta}</div>
                <div className="flex items-center justify-between mt-2">
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-2 ${
                      trunk.status_conexao === 'online' ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    <span className="text-xs text-gray-400">
                      {trunk.canais_em_uso}/{trunk.max_canais_simultaneos}
                    </span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    trunk.ativo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {trunk.ativo ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Configuração */}
        <div className="lg:col-span-3">
          {(selectedTrunk || isEditMode) ? (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold">
                  🔧 {isEditMode && !selectedTrunk ? 'Nuevo Trunk SIP' : `Configuración - ${selectedTrunk?.nombre}`}
                </h3>
                <div className="flex space-x-2">
                  {selectedTrunk && !isEditMode && (
                    <button
                      onClick={handleTestConnection}
                      disabled={testing}
                      className="bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
                    >
                      {testing ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Probando...
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Probar
                        </>
                      )}
                    </button>
                  )}
                  <button
                    onClick={handleSaveConfig}
                    disabled={saving}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
                  >
                    {saving ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Guardando...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Guardar
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Configurações Básicas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-4">📋 Información Básica</h4>
                  
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nombre del Trunk
                      </label>
                      <input
                        type="text"
                        value={trunkConfig.nombre}
                        onChange={(e) => setTrunkConfig(prev => ({
                          ...prev,
                          nombre: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Ej: trunk_argentina"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tipo de Trunk
                      </label>
                      <select
                        value={trunkConfig.tipo}
                        onChange={(e) => setTrunkConfig(prev => ({
                          ...prev,
                          tipo: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        {tipoOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label} - {option.description}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Host/IP
                        </label>
                        <input
                          type="text"
                          value={trunkConfig.host}
                          onChange={(e) => setTrunkConfig(prev => ({
                            ...prev,
                            host: e.target.value
                          }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="136.243.32.61"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Puerto
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="65535"
                          value={trunkConfig.porta}
                          onChange={(e) => setTrunkConfig(prev => ({
                            ...prev,
                            porta: parseInt(e.target.value)
                          }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Usuario
                        </label>
                        <input
                          type="text"
                          value={trunkConfig.usuario}
                          onChange={(e) => setTrunkConfig(prev => ({
                            ...prev,
                            usuario: e.target.value
                          }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Contraseña
                        </label>
                        <input
                          type="password"
                          value={trunkConfig.senha}
                          onChange={(e) => setTrunkConfig(prev => ({
                            ...prev,
                            senha: e.target.value
                          }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-4">🎵 Configuración de Codecs</h4>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Codec Preferido
                    </label>
                    <select
                      value={trunkConfig.codec_preferido}
                      onChange={(e) => setTrunkConfig(prev => ({
                        ...prev,
                        codec_preferido: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {codecOptions.map(codec => (
                        <option key={codec.value} value={codec.value}>
                          {codec.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Codecs Permitidos
                    </label>
                    <div className="space-y-2">
                      {codecOptions.map(codec => (
                        <label key={codec.value} className="flex items-start space-x-2">
                          <input
                            type="checkbox"
                            checked={trunkConfig.codecs_permitidos.includes(codec.value)}
                            onChange={() => handleCodecToggle(codec.value)}
                            className="mt-1 rounded text-blue-600"
                          />
                          <div>
                            <span className="text-sm font-medium text-gray-700">
                              {codec.label}
                            </span>
                            <p className="text-xs text-gray-500">{codec.description}</p>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Configurações de Roteamento e Códigos de Proveedor */}
              <div className="bg-yellow-50 rounded-lg p-4 mb-6">
                <h4 className="font-semibold text-gray-800 mb-4">📞 Códigos de Proveedor y Enrutamiento</h4>
                <p className="text-sm text-gray-600 mb-4">
                  Configure códigos que su proveedor VOIP exige antes del número de destino
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Prefijo de Marcado
                      </label>
                      <input
                        type="text"
                        value={trunkConfig.prefixo_discagem}
                        onChange={(e) => setTrunkConfig(prev => ({
                          ...prev,
                          prefixo_discagem: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Ex: 9, 0, 00"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Código que el proveedor exige antes del número (ej: 9 para línea externa)
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Código del País
                      </label>
                      <input
                        type="text"
                        value={trunkConfig.codigo_pais}
                        onChange={(e) => setTrunkConfig(prev => ({
                          ...prev,
                          codigo_pais: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Ex: +55, +1, +54"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Código del país para llamadas internacionales
                      </p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Sufijo de Marcado
                      </label>
                      <input
                        type="text"
                        value={trunkConfig.sufixo_discagem}
                        onChange={(e) => setTrunkConfig(prev => ({
                          ...prev,
                          sufixo_discagem: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Ex: #, *, vazio"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Código que el proveedor exige después del número (opcional)
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Código de Área por Defecto
                      </label>
                      <input
                        type="text"
                        value={trunkConfig.codigo_area_default}
                        onChange={(e) => setTrunkConfig(prev => ({
                          ...prev,
                          codigo_area_default: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Ex: 11, 21, 47"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Código de área para números locales sin código de área
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <h5 className="font-medium text-blue-800 mb-2">💡 Ejemplo de Configuración:</h5>
                  <div className="text-sm text-blue-700">
                    <p><strong>Número original:</strong> 11987654321</p>
                    <p><strong>Con prefijo "9":</strong> 911987654321</p>
                    <p><strong>Con sufijo "#":</strong> 911987654321#</p>
                    <p className="text-xs mt-2 text-blue-600">
                      El sistema aplicará automáticamente estos códigos antes de marcar
                    </p>
                  </div>
                  
                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <h5 className="text-sm font-semibold text-blue-800 mb-2">💡 Casos de Uso Comunes</h5>
                    <ul className="text-xs text-blue-700 space-y-1">
                      <li><strong>Prefijo "0":</strong> Algunos proveedores requieren "0" antes del número</li>
                      <li><strong>Prefijo "9":</strong> Para acceso a línea externa en algunos sistemas</li>
                      <li><strong>Sufijo "#":</strong> Para indicar fin de marcado</li>
                      <li><strong>Código de país:</strong> Para normalizar números internacionales</li>
                      <li><strong>Área por defecto:</strong> Para completar números locales</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Configurações SIP */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="font-semibold text-gray-800">⚙️ Configuraciones SIP</h4>
                  <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="text-blue-600 hover:text-blue-800 text-sm flex items-center"
                  >
                    {showAdvanced ? 'Ocultar' : 'Mostrar'} Avanzadas
                    <svg className={`w-4 h-4 ml-1 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Protocolo
                    </label>
                    <select
                      value={trunkConfig.protocolo}
                      onChange={(e) => setTrunkConfig(prev => ({
                        ...prev,
                        protocolo: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="UDP">UDP</option>
                      <option value="TCP">TCP</option>
                      <option value="TLS">TLS</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      NAT
                    </label>
                    <select
                      value={trunkConfig.nat}
                      onChange={(e) => setTrunkConfig(prev => ({
                        ...prev,
                        nat: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {natOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      DTMF Mode
                    </label>
                    <select
                      value={trunkConfig.dtmfmode}
                      onChange={(e) => setTrunkConfig(prev => ({
                        ...prev,
                        dtmfmode: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="rfc2833">RFC2833</option>
                      <option value="inband">Inband</option>
                      <option value="info">SIP INFO</option>
                    </select>
                  </div>
                </div>

                {showAdvanced && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            From User
                          </label>
                          <input
                            type="text"
                            value={trunkConfig.fromuser}
                            onChange={(e) => setTrunkConfig(prev => ({
                              ...prev,
                              fromuser: e.target.value
                            }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            From Domain
                          </label>
                          <input
                            type="text"
                            value={trunkConfig.fromdomain}
                            onChange={(e) => setTrunkConfig(prev => ({
                              ...prev,
                              fromdomain: e.target.value
                            }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Outbound Proxy
                          </label>
                          <input
                            type="text"
                            value={trunkConfig.outboundproxy}
                            onChange={(e) => setTrunkConfig(prev => ({
                              ...prev,
                              outboundproxy: e.target.value
                            }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            RTP Timeout (s)
                          </label>
                          <input
                            type="number"
                            min="0"
                            max="3600"
                            value={trunkConfig.rtptimeout}
                            onChange={(e) => setTrunkConfig(prev => ({
                              ...prev,
                              rtptimeout: parseInt(e.target.value)
                            }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Call Limit
                          </label>
                          <input
                            type="number"
                            min="1"
                            max="1000"
                            value={trunkConfig.call_limit}
                            onChange={(e) => setTrunkConfig(prev => ({
                              ...prev,
                              call_limit: parseInt(e.target.value)
                            }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Máximo Canais Simultâneos
                          </label>
                          <input
                            type="number"
                            min="1"
                            max="1000"
                            value={trunkConfig.max_canais_simultaneos}
                            onChange={(e) => setTrunkConfig(prev => ({
                              ...prev,
                              max_canais_simultaneos: parseInt(e.target.value)
                            }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        <div className="space-y-2">
                          <label className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={trunkConfig.ativo}
                              onChange={(e) => setTrunkConfig(prev => ({
                                ...prev,
                                ativo: e.target.checked
                              }))}
                              className="rounded text-blue-600"
                            />
                            <span className="text-sm font-medium text-gray-700">
                              Trunk Ativo
                            </span>
                          </label>

                          <label className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={trunkConfig.registro_obrigatorio}
                              onChange={(e) => setTrunkConfig(prev => ({
                                ...prev,
                                registro_obrigatorio: e.target.checked
                              }))}
                              className="rounded text-blue-600"
                            />
                            <span className="text-sm font-medium text-gray-700">
                              Registro Obrigatório
                            </span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Configurações de Caller ID */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">📞 Configurações de Caller ID</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Caller ID Padrão
                      </label>
                      <input
                        type="text"
                        value={trunkConfig.callerid_padrao || ''}
                        onChange={(e) => setTrunkConfig(prev => ({
                          ...prev,
                          callerid_padrao: e.target.value
                        }))}
                        placeholder="Nome <numero>"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Exemplo: "Empresa LTDA" &lt;5511999999999&gt;
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Formato de Saída
                      </label>
                      <select
                        value={trunkConfig.formato_callerid || 'completo'}
                        onChange={(e) => setTrunkConfig(prev => ({
                          ...prev,
                          formato_callerid: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="completo">Nome e Número</option>
                        <option value="numero">Apenas Número</option>
                        <option value="nome">Apenas Nome</option>
                      </select>
                    </div>
                  </div>

                  <div className="mt-4">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={trunkConfig.permitir_callerid_personalizado || false}
                        onChange={(e) => setTrunkConfig(prev => ({
                          ...prev,
                          permitir_callerid_personalizado: e.target.checked
                        }))}
                        className="rounded text-blue-600"
                      />
                      <span className="text-sm font-medium text-gray-700">
                        Permitir Caller ID Personalizado por Campanha
                      </span>
                    </label>
                    <p className="text-xs text-gray-500 mt-1 ml-6">
                      Permite que cada campanha defina seu próprio Caller ID
                    </p>
                  </div>
                </div>
              </div>

              {/* Prévia da Configuração Asterisk */}
              <div className="bg-gray-900 rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-semibold text-white">📄 Configuração Asterisk (sip.conf)</h4>
                  <button
                    onClick={() => navigator.clipboard.writeText(generateAsteriskConfig())}
                    className="text-gray-300 hover:text-white text-sm flex items-center"
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copiar
                  </button>
                </div>
                <pre className="text-green-400 text-sm overflow-x-auto whitespace-pre-wrap">
                  {generateAsteriskConfig()}
                </pre>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <p className="text-lg font-medium">Selecione um trunk</p>
              <p>Escolha na lista ao lado para configurar ou crie um novo trunk</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SipTrunkConfig;