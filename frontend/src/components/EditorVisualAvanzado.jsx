import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, Pause, Settings, Save, Download, Upload, 
  Plus, Trash2, Copy, Eye, EyeOff, Volume2, VolumeX,
  Monitor, Cpu, Network, Database, Phone, Mic,
  ArrowRight, ArrowLeft, RotateCcw, CheckCircle, AlertCircle
} from 'lucide-react';

const EditorVisualAvanzado = () => {
  const [configuracion, setConfiguracion] = useState({
    audio: {
      contextos: [],
      reglas: [],
      estados: ['iniciando', 'tocando', 'aguardando_dtmf', 'detectando_voicemail']
    },
    voip: {
      provedores: [],
      trunks: [],
      configuraciones: {}
    },
    campanhas: {
      activas: [],
      configuraciones: {}
    },
    tts: {
      idiomas: ['es', 'en', 'pt'],
      vozes: [],
      mensajes: {}
    }
  });

  const [panelActivo, setPanelActivo] = useState('audio');
  const [modoVisualizacion, setModoVisualizacion] = useState('diagrama'); // diagrama, codigo, hibrido
  const [simulandoFlujo, setSimulandoFlujo] = useState(false);
  const [estadoSimulacion, setEstadoSimulacion] = useState(null);
  const [historialCambios, setHistorialCambios] = useState([]);
  const [configuracionGuardada, setConfiguracionGuardada] = useState(true);

  const canvasRef = useRef(null);

  // Cargar configuración inicial
  useEffect(() => {
    cargarConfiguracionInicial();
  }, []);

  const cargarConfiguracionInicial = async () => {
    try {
      // Cargar configurações do backend
      const [audioRes, voipRes, ttsRes] = await Promise.all([
        fetch('/api/v1/audio/contextos'),
        fetch('/api/v1/multi-sip/provedores'),
        fetch('/api/v1/tts-dnc/idiomas')
      ]);

      const audioData = await audioRes.json();
      const voipData = await voipRes.json();
      const ttsData = await ttsRes.json();

      setConfiguracion(prev => ({
        ...prev,
        audio: {
          ...prev.audio,
          contextos: audioData.contextos || []
        },
        voip: {
          ...prev.voip,
          provedores: voipData.provedores || []
        },
        tts: {
          ...prev.tts,
          idiomas: ttsData.idiomas || []
        }
      }));
    } catch (error) {
      console.error('Erro ao carregar configuração:', error);
    }
  };

  const PanelAudio = () => (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Volume2 className="w-5 h-5 mr-2" />
          Sistema de Áudio Inteligente
        </h3>
        
        {/* Estados de Áudio */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Estados do Fluxo</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {configuracion.audio.estados.map((estado, index) => (
              <div 
                key={index}
                className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-3 text-center cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                onClick={() => editarEstado(estado)}
              >
                <div className="text-sm font-medium text-blue-800 dark:text-blue-200">
                  {estado.replace('_', ' ').toUpperCase()}
                </div>
              </div>
            ))}
            <button 
              className="bg-gray-50 dark:bg-gray-700 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-3 text-center hover:border-blue-500 transition-colors"
              onClick={adicionarEstado}
            >
              <Plus className="w-5 h-5 mx-auto text-gray-400" />
              <div className="text-sm text-gray-500 mt-1">Adicionar Estado</div>
            </button>
          </div>
        </div>

        {/* Regras de Áudio */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Regras de Reprodução</h4>
          <div className="space-y-3">
            {configuracion.audio.reglas.map((regra, index) => (
              <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-center justify-between">
                <div className="flex-1">
                  <div className="font-medium">{regra.nome}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Se {regra.condicao} → Então {regra.acao}
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button className="p-2 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded">
                    <Settings className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-red-600 hover:bg-red-100 dark:hover:bg-red-900/30 rounded">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            <button 
              className="w-full bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4 text-blue-800 dark:text-blue-200 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
              onClick={adicionarRegra}
            >
              <Plus className="w-5 h-5 mx-auto mb-1" />
              Adicionar Nova Regra
            </button>
          </div>
        </div>

        {/* Visualizador de Fluxo */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Fluxo de Estados</h4>
          <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4">
            <canvas 
              ref={canvasRef}
              className="w-full h-64 border border-gray-300 dark:border-gray-600 rounded"
              onClick={handleCanvasClick}
            />
          </div>
          <div className="flex justify-between mt-3">
            <button 
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors flex items-center"
              onClick={simularFlujo}
              disabled={simulandoFlujo}
            >
              {simulandoFlujo ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
              {simulandoFlujo ? 'Pausar' : 'Simular Fluxo'}
            </button>
            <button 
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors flex items-center"
              onClick={resetearFluxo}
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Resetear
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const PanelVoIP = () => (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Phone className="w-5 h-5 mr-2" />
          Configuração VoIP
        </h3>

        {/* Provedores SIP */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Provedores SIP</h4>
          <div className="grid gap-4">
            {configuracion.voip.provedores.map((provedor, index) => (
              <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      provedor.estado === 'conectado' ? 'bg-green-500' : 
                      provedor.estado === 'conectando' ? 'bg-yellow-500' : 'bg-red-500'
                    }`} />
                    <div>
                      <div className="font-medium">{provedor.nome}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {provedor.tipo} - {provedor.servidor}
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button className="p-2 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded">
                      <Settings className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-green-600 hover:bg-green-100 dark:hover:bg-green-900/30 rounded">
                      <CheckCircle className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  <div>
                    <div className="text-gray-600 dark:text-gray-400">Chamadas Ativas</div>
                    <div className="font-medium">{provedor.llamadas_activas || 0}</div>
                  </div>
                  <div>
                    <div className="text-gray-600 dark:text-gray-400">Qualidade</div>
                    <div className="font-medium">{provedor.calidad || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-gray-600 dark:text-gray-400">Custo/min</div>
                    <div className="font-medium">${provedor.costo_por_minuto || 0}</div>
                  </div>
                  <div>
                    <div className="text-gray-600 dark:text-gray-400">Uptime</div>
                    <div className="font-medium">{provedor.uptime || 100}%</div>
                  </div>
                </div>
              </div>
            ))}
            <button 
              className="w-full bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4 text-blue-800 dark:text-blue-200 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
              onClick={adicionarProvedor}
            >
              <Plus className="w-5 h-5 mx-auto mb-1" />
              Adicionar Provedor SIP
            </button>
          </div>
        </div>

        {/* Configurações FreeSWITCH */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">FreeSWITCH</h4>
          <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center">
                <Cpu className="w-5 h-5 mr-2 text-purple-600" />
                <span className="font-medium">FreeSWITCH ESL</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Conectado</span>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-600 dark:text-gray-400">Host</div>
                <div className="font-medium">localhost:8021</div>
              </div>
              <div>
                <div className="text-gray-600 dark:text-gray-400">Canais Ativos</div>
                <div className="font-medium">12 / 100</div>
              </div>
              <div>
                <div className="text-gray-600 dark:text-gray-400">Eventos/min</div>
                <div className="font-medium">245</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const PanelTTS = () => (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Mic className="w-5 h-5 mr-2" />
          Text-to-Speech DNC
        </h3>

        {/* Idiomas Suportados */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Idiomas Configurados</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {configuracion.tts.idiomas.map((idioma, index) => (
              <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium">
                    {idioma === 'es' ? '🇪🇸 Español' : 
                     idioma === 'en' ? '🇺🇸 English' : 
                     idioma === 'pt' ? '🇧🇷 Português' : idioma}
                  </div>
                  <div className="flex space-x-1">
                    <button className="p-1 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded">
                      <Volume2 className="w-4 h-4" />
                    </button>
                    <button className="p-1 text-green-600 hover:bg-green-100 dark:hover:bg-green-900/30 rounded">
                      <Settings className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  5 mensagens configuradas
                </div>
                <div className="mt-2">
                  <button className="w-full px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors">
                    Gerar Áudios
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Editor de Mensagens */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Editor de Mensagens DNC</h4>
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Tipo de Mensagem</label>
              <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800">
                <option value="opt_out">Opt-out (Sair da lista)</option>
                <option value="confirmacao">Confirmação</option>
                <option value="despedida">Despedida</option>
                <option value="error">Erro</option>
                <option value="timeout">Timeout</option>
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Idioma</label>
              <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800">
                <option value="es">Español</option>
                <option value="en">English</option>
                <option value="pt">Português</option>
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Texto da Mensagem</label>
              <textarea 
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
                rows="4"
                placeholder="Digite a mensagem para conversão em áudio..."
                defaultValue="Si no desea recibir más llamadas de nuestra empresa, presione 9 ahora o diga 'STOP'. Su número será removido de nuestra lista de contactos inmediatamente."
              />
            </div>
            <div className="flex space-x-3">
              <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex items-center">
                <Volume2 className="w-4 h-4 mr-2" />
                Gerar Áudio
              </button>
              <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors flex items-center">
                <Play className="w-4 h-4 mr-2" />
                Testar
              </button>
              <button className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors flex items-center">
                <Save className="w-4 h-4 mr-2" />
                Salvar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const PanelMonitoramento = () => (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Monitor className="w-5 h-5 mr-2" />
          Monitoramento em Tempo Real
        </h3>

        {/* Métricas Principais */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-800 dark:text-blue-200">245</div>
            <div className="text-sm text-blue-600 dark:text-blue-400">Chamadas Ativas</div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-800 dark:text-green-200">15.2</div>
            <div className="text-sm text-green-600 dark:text-green-400">CPS Atual</div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-800 dark:text-purple-200">8/12</div>
            <div className="text-sm text-purple-600 dark:text-purple-400">Trunks Ativos</div>
          </div>
          <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-700 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-orange-800 dark:text-orange-200">72.5%</div>
            <div className="text-sm text-orange-600 dark:text-orange-400">Taxa Conexão</div>
          </div>
        </div>

        {/* Gráfico de Fluxo em Tempo Real */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Fluxo de Chamadas (Últimos 30min)</h4>
          <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 h-48 flex items-center justify-center">
            <div className="text-gray-500">Gráfico de fluxo em tempo real aqui</div>
          </div>
        </div>

        {/* Estados dos Sistemas */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h5 className="font-medium mb-3 flex items-center">
              <Database className="w-4 h-4 mr-2" />
              Sistema de Áudio
            </h5>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Estados Ativos:</span>
                <span className="font-medium">4/10</span>
              </div>
              <div className="flex justify-between">
                <span>Regras Executando:</span>
                <span className="font-medium">12</span>
              </div>
              <div className="flex justify-between">
                <span>Cache Hit Rate:</span>
                <span className="font-medium text-green-600">94.2%</span>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h5 className="font-medium mb-3 flex items-center">
              <Network className="w-4 h-4 mr-2" />
              Conectividade VoIP
            </h5>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Provedores Online:</span>
                <span className="font-medium text-green-600">3/3</span>
              </div>
              <div className="flex justify-between">
                <span>Latência Média:</span>
                <span className="font-medium">45ms</span>
              </div>
              <div className="flex justify-between">
                <span>Packet Loss:</span>
                <span className="font-medium text-green-600">0.1%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Funções auxiliares
  const editarEstado = (estado) => {
    console.log('Editando estado:', estado);
  };

  const adicionarEstado = () => {
    const novoEstado = prompt('Nome do novo estado:');
    if (novoEstado) {
      setConfiguracion(prev => ({
        ...prev,
        audio: {
          ...prev.audio,
          estados: [...prev.audio.estados, novoEstado.toLowerCase().replace(' ', '_')]
        }
      }));
      setConfiguracionGuardada(false);
    }
  };

  const adicionarRegra = () => {
    const novaRegra = {
      nome: 'Nova Regra',
      condicao: 'DTMF = "1"',
      acao: 'Transferir para agente'
    };
    
    setConfiguracion(prev => ({
      ...prev,
      audio: {
        ...prev.audio,
        regras: [...prev.audio.reglas, novaRegra]
      }
    }));
    setConfiguracionGuardada(false);
  };

  const adicionarProvedor = () => {
    console.log('Adicionando novo provedor SIP');
  };

  const simularFlujo = () => {
    setSimulandoFlujo(!simulandoFlujo);
    if (!simulandoFlujo) {
      setEstadoSimulacion('iniciando');
      // Simular progressão pelos estados
      setTimeout(() => setEstadoSimulacion('tocando'), 1000);
      setTimeout(() => setEstadoSimulacion('aguardando_dtmf'), 3000);
      setTimeout(() => setEstadoSimulacion('detectando_voicemail'), 5000);
      setTimeout(() => {
        setEstadoSimulacion(null);
        setSimulandoFlujo(false);
      }, 7000);
    }
  };

  const resetearFluxo = () => {
    setSimulandoFlujo(false);
    setEstadoSimulacion(null);
  };

  const handleCanvasClick = (event) => {
    // Detectar clicks no canvas para edição interativa
    const rect = canvasRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    console.log('Canvas click:', x, y);
  };

  const salvarConfiguracion = async () => {
    try {
      // Salvar configuração no backend
      await fetch('/api/v1/configuracion/salvar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configuracion)
      });
      
      setConfiguracionGuardada(true);
      // Adicionar ao histórico
      setHistorialCambios(prev => [
        ...prev,
        {
          timestamp: new Date().toISOString(),
          tipo: 'salvar',
          descripcion: 'Configuração salva'
        }
      ]);
    } catch (error) {
      console.error('Erro ao salvar:', error);
    }
  };

  const exportarConfiguracion = () => {
    const dataStr = JSON.stringify(configuracion, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'configuracion_discador.json';
    link.click();
  };

  const importarConfiguracion = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const config = JSON.parse(e.target.result);
          setConfiguracion(config);
          setConfiguracionGuardada(false);
        } catch (error) {
          console.error('Erro ao importar:', error);
          alert('Erro ao importar configuração');
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">Editor Visual Avançado</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Configuração completa do sistema discador
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {!configuracionGuardada && (
              <div className="flex items-center text-orange-600">
                <AlertCircle className="w-4 h-4 mr-1" />
                <span className="text-sm">Mudanças não salvas</span>
              </div>
            )}
            <button
              onClick={salvarConfiguracion}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex items-center"
            >
              <Save className="w-4 h-4 mr-2" />
              Salvar
            </button>
            <button
              onClick={exportarConfiguracion}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Exportar
            </button>
            <label className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors flex items-center cursor-pointer">
              <Upload className="w-4 h-4 mr-2" />
              Importar
              <input
                type="file"
                accept=".json"
                onChange={importarConfiguracion}
                className="hidden"
              />
            </label>
          </div>
        </div>

        {/* Navegação entre painéis */}
        <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          {[
            { id: 'audio', label: 'Áudio Inteligente', icon: Volume2 },
            { id: 'voip', label: 'VoIP', icon: Phone },
            { id: 'tts', label: 'TTS DNC', icon: Mic },
            { id: 'monitor', label: 'Monitoramento', icon: Monitor }
          ].map((panel) => {
            const Icon = panel.icon;
            return (
              <button
                key={panel.id}
                onClick={() => setPanelActivo(panel.id)}
                className={`flex items-center px-4 py-2 rounded-md transition-colors ${
                  panelActivo === panel.id
                    ? 'bg-white dark:bg-gray-800 text-blue-600 shadow'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {panel.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Conteúdo do painel ativo */}
      <div>
        {panelActivo === 'audio' && <PanelAudio />}
        {panelActivo === 'voip' && <PanelVoIP />}
        {panelActivo === 'tts' && <PanelTTS />}
        {panelActivo === 'monitor' && <PanelMonitoramento />}
      </div>

      {/* Status Bar */}
      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 flex items-center justify-between text-sm">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
            <span>Sistema Online</span>
          </div>
          <div>Última atualização: {new Date().toLocaleTimeString()}</div>
        </div>
        <div className="flex items-center space-x-4">
          <span>Configurações: {Object.keys(configuracion).length} módulos</span>
          <span>|</span>
          <span>Histórico: {historialCambios.length} mudanças</span>
        </div>
      </div>
    </div>
  );
};

export default EditorVisualAvanzado; 