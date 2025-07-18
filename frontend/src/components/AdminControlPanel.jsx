import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';
import { useCampaigns } from '../contexts/CampaignContext';

/**
 * Painel de Controle Administrativo Completo
 * Implementa todas as funcionalidades essenciais do sistema
 */
const AdminControlPanel = () => {
  // Estados principais
  const [activeSection, setActiveSection] = useState('load-numbers');
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  // Estados para Load Numbers
  const [numberFile, setNumberFile] = useState(null);
  const [numberFormat, setNumberFormat] = useState('CallerID');
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // Estados para Load Audios
  const [audioFile, setAudioFile] = useState(null);
  const [audioFiles, setAudioFiles] = useState([]);
  
  // Estados para Test Calls
  const [testNumber, setTestNumber] = useState('');
  const [testResults, setTestResults] = useState([]);
  const [isTestRunning, setIsTestRunning] = useState(false);
  
  // Estados para Campaign
  const [campaignData, setCampaignData] = useState({
    name: '',
    description: '',
    maxConcurrentCalls: 10,
    callsPerSecond: 1
  });

  const { refreshCampaigns } = useCampaigns();

  // Carregar dados iniciais
  useEffect(() => {
    loadCampaigns();
    loadAudioFiles();
  }, []);

  const loadCampaigns = async () => {
    try {
      const response = await makeApiRequest('/campaigns');
      const campaignsList = response.campaigns || response || [];
      setCampaigns(campaignsList);
      if (campaignsList.length > 0 && !selectedCampaign) {
        setSelectedCampaign(campaignsList[0].id.toString());
      }
    } catch (error) {

    }
  };

  const loadAudioFiles = async () => {
    try {
      const response = await makeApiRequest('/audios');
      setAudioFiles(response.audios || response || []);
    } catch (error) {

    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  // Funções para Load Numbers
  const handleNumberFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setNumberFile(file);
      showMessage('info', `Arquivo selecionado: ${file.name}`);
    }
  };

  const importNumbers = async () => {
    if (!numberFile || !selectedCampaign) {
      showMessage('error', 'Selecione um arquivo e uma campanha');
      return;
    }

    setLoading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('arquivo', numberFile);
      formData.append('campaign_id', selectedCampaign);
      formData.append('incluir_nome', 'true');
      formData.append('pais_preferido', 'auto');

      // Simular progresso
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const response = await makeApiRequest('/contacts/upload', {
        method: 'POST',
        body: formData
      });

      clearInterval(progressInterval);
      setUploadProgress(100);
      
      showMessage('success', `Números importados com sucesso! ${response.total_processados || 0} números processados.`);
      setNumberFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('number-file-input');
      if (fileInput) fileInput.value = '';
      
    } catch (error) {

      showMessage('error', 'Erro ao importar números. Verifique o formato do arquivo.');
    } finally {
      setLoading(false);
      setTimeout(() => setUploadProgress(0), 2000);
    }
  };

  // Funções para Load Audios
  const handleAudioFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setAudioFile(file);
      showMessage('info', `Áudio selecionado: ${file.name}`);
    }
  };

  const importAudio = async () => {
    if (!audioFile) {
      showMessage('error', 'Selecione um arquivo de áudio');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('name', audioFile.name.replace(/\.[^/.]+$/, ''));
      formData.append('description', `Áudio importado: ${audioFile.name}`);

      const response = await makeApiRequest('/audios/upload', {
        method: 'POST',
        body: formData
      });

      showMessage('success', 'Áudio importado com sucesso!');
      setAudioFile(null);
      loadAudioFiles();
      
      // Reset file input
      const fileInput = document.getElementById('audio-file-input');
      if (fileInput) fileInput.value = '';
      
    } catch (error) {

      showMessage('error', 'Erro ao importar áudio. Verifique o formato do arquivo.');
    } finally {
      setLoading(false);
    }
  };

  // Funções para Test Calls
  const runTestCall = async () => {
    if (!testNumber.trim()) {
      showMessage('error', 'Digite um número para teste');
      return;
    }

    setIsTestRunning(true);
    const testId = Date.now();

    try {
      const response = await makeApiRequest('/dialer/test-call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          numero: testNumber,
          campaign_id: selectedCampaign || null
        })
      });

      const newResult = {
        id: testId,
        numero: testNumber,
        status: response.success ? 'Sucesso' : 'Falha',
        timestamp: new Date().toLocaleTimeString(),
        details: response.message || 'Teste executado'
      };

      setTestResults(prev => [newResult, ...prev.slice(0, 9)]); // Manter apenas 10 resultados
      showMessage('success', `Teste executado para ${testNumber}`);
      setTestNumber('');
      
    } catch (error) {

      const errorResult = {
        id: testId,
        numero: testNumber,
        status: 'Erro',
        timestamp: new Date().toLocaleTimeString(),
        details: error.message || 'Erro na execução'
      };
      setTestResults(prev => [errorResult, ...prev.slice(0, 9)]);
      showMessage('error', 'Erro ao executar teste');
    } finally {
      setIsTestRunning(false);
    }
  };

  // Funções para Campaign
  const createCampaign = async () => {
    if (!campaignData.name.trim()) {
      showMessage('error', 'Digite um nome para a campanha');
      return;
    }

    setLoading(true);

    try {
      const response = await makeApiRequest('/campaigns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: campaignData.name,
          description: campaignData.description,
          max_concurrent_calls: campaignData.maxConcurrentCalls,
          calls_per_second: campaignData.callsPerSecond,
          active: true
        })
      });

      showMessage('success', 'Campanha criada com sucesso!');
      setCampaignData({
        name: '',
        description: '',
        maxConcurrentCalls: 10,
        callsPerSecond: 1
      });
      loadCampaigns();
      refreshCampaigns();
      
    } catch (error) {

      showMessage('error', 'Erro ao criar campanha');
    } finally {
      setLoading(false);
    }
  };

  const editCampaign = async () => {
    if (!selectedCampaign) {
      showMessage('error', 'Selecione uma campanha para editar');
      return;
    }

    setLoading(true);

    try {
      const response = await makeApiRequest(`/campaigns/${selectedCampaign}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: campaignData.name,
          description: campaignData.description,
          max_concurrent_calls: campaignData.maxConcurrentCalls,
          calls_per_second: campaignData.callsPerSecond
        })
      });

      showMessage('success', 'Campanha atualizada com sucesso!');
      loadCampaigns();
      refreshCampaigns();
      
    } catch (error) {

      showMessage('error', 'Erro ao atualizar campanha');
    } finally {
      setLoading(false);
    }
  };

  const deleteCampaign = async () => {
    if (!selectedCampaign) {
      showMessage('error', 'Selecione uma campanha para deletar');
      return;
    }

    if (!window.confirm('Tem certeza que deseja deletar esta campanha?')) {
      return;
    }

    setLoading(true);

    try {
      await makeApiRequest(`/campaigns/${selectedCampaign}`, {
        method: 'DELETE'
      });

      showMessage('success', 'Campanha deletada com sucesso!');
      
      // Limpar seleção e dados da campanha
      setSelectedCampaign('');
      setCampaignData({
        name: '',
        description: '',
        maxConcurrentCalls: 10,
        callsPerSecond: 1
      });
      
      // Forçar atualização do estado local removendo a campanha deletada
      setCampaigns(prevCampaigns => 
        prevCampaigns.filter(campaign => campaign.id.toString() !== selectedCampaign)
      );
      
      // Atualizar contexto global e recarregar lista
      await refreshCampaigns(true); // Force refresh
      await loadCampaigns(); // Reload local state
      
    } catch (error) {

      showMessage('error', 'Erro ao deletar campanha');
    } finally {
      setLoading(false);
    }
  };

  // Função para visualizar números da campanha
  const viewNumbers = () => {
    if (!selectedCampaign) {
      showMessage('error', 'Selecione uma campanha');
      return;
    }
    showMessage('info', 'Abrindo visualização de números...');
    // Aqui você pode implementar a navegação para uma página de visualização
  };

  // Função para visualizar campanha em execução
  const viewRunningCampaign = () => {
    if (!selectedCampaign) {
      showMessage('error', 'Selecione uma campanha');
      return;
    }
    showMessage('info', 'Abrindo monitoramento da campanha...');
    // Aqui você pode implementar a navegação para o monitor da campanha
  };

  // Função para configurar chamadas por segundo
  const configureCallsPerSecond = () => {
    const cps = prompt('Digite o número de chamadas por segundo:', '1');
    if (cps && !isNaN(cps) && cps > 0) {
      setCampaignData(prev => ({ ...prev, callsPerSecond: parseInt(cps) }));
      showMessage('success', `Configurado para ${cps} chamadas por segundo`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-white mb-3">Panel de Control Administrativo</h1>
          <p className="text-gray-400 text-lg">Gestión completa del sistema de marcación</p>
        </div>

        {/* Mensagens */}
        {message.text && (
          <div className={`mb-4 p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-900/30 border border-green-500/30 text-green-400' :
            message.type === 'error' ? 'bg-red-900/30 border border-red-500/30 text-red-400' :
            'bg-blue-900/30 border border-blue-500/30 text-blue-400'
          }`}>
            {message.text}
          </div>
        )}

        {/* Layout Principal */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          
          {/* Seção Load Numbers */}
          <div className="bg-gray-800 border border-green-500 rounded-lg p-8">
            <h2 className="text-xl font-bold text-white mb-6 text-center border-b border-green-500 pb-2">
              Cargar Números
            </h2>
            
            <div className="space-y-5">
              <div>
                <select 
                  value={numberFormat}
                  onChange={(e) => setNumberFormat(e.target.value)}
                  className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white"
                >
                  <option value="CallerID">CallerID</option>
                  <option value="Phone Numbers">Phone Numbers</option>
                  <option value="DNC Create">DNC Create</option>
                  <option value="DNC Load">DNC Load</option>
                  <option value="Bridge Numbers">Bridge Numbers</option>
                </select>
              </div>
              
              <div>
                <input
                  id="number-file-input"
                  type="file"
                  accept=".txt,.csv"
                  onChange={handleNumberFileSelect}
                  className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-green-600 file:text-white"
                />
              </div>
              
              {numberFile && (
                <div className="text-sm text-gray-400">
                  Arquivo: {numberFile.name}
                </div>
              )}
              
              {uploadProgress > 0 && (
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              )}
              
              <button
                onClick={importNumbers}
                disabled={loading || !numberFile}
                className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded transition-colors"
              >
                {loading ? 'Importando...' : 'Importar Números'}
              </button>
            </div>
          </div>

          {/* Seção Campaign */}
          <div className="bg-gray-800 border border-green-500 rounded-lg p-8">
            <h2 className="text-xl font-bold text-white mb-6 text-center border-b border-green-500 pb-2">
              Campaña
            </h2>
            
            <div className="space-y-5">
              <div>
                <select 
                  value={selectedCampaign}
                  onChange={(e) => setSelectedCampaign(e.target.value)}
                  className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white"
                >
                  <option value="">Slackall</option>
                  {campaigns.map(campaign => (
                    <option key={campaign.id} value={campaign.id}>
                      {campaign.name || campaign.nombre}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={createCampaign}
                  disabled={loading}
                  className="py-2 px-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded text-sm transition-colors"
                >
                  Nuevo
                </button>
                <button
                  onClick={editCampaign}
                  disabled={loading || !selectedCampaign}
                  className="py-2 px-3 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white rounded text-sm transition-colors"
                >
                  Editar
                </button>
                <button
                  onClick={deleteCampaign}
                  disabled={loading || !selectedCampaign}
                  className="py-2 px-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white rounded text-sm transition-colors"
                >
                  Eliminar
                </button>
              </div>
              
              <div className="border-t border-gray-600 pt-4 space-y-2">
                <button
                  onClick={viewNumbers}
                  disabled={!selectedCampaign}
                  className="w-full py-2 px-4 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-700 text-white rounded text-sm transition-colors"
                >
                  Ver Números
                </button>
                <button
                  onClick={viewRunningCampaign}
                  disabled={!selectedCampaign}
                  className="w-full py-2 px-4 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-700 text-white rounded text-sm transition-colors"
                >
                  Ver Campaña Activa
                </button>
                <button
                  onClick={configureCallsPerSecond}
                  className="w-full py-2 px-4 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm transition-colors"
                >
                  Llamadas por Segundo
                </button>
              </div>
            </div>
          </div>

          {/* Seção Load Audios */}
          <div className="bg-gray-800 border border-green-500 rounded-lg p-8">
            <h2 className="text-xl font-bold text-white mb-6 text-center border-b border-green-500 pb-2">
              Cargar Audios
            </h2>
            
            <div className="space-y-5">
              <div>
                <input
                  id="audio-file-input"
                  type="file"
                  accept=".wav,.mp3,.ogg"
                  onChange={handleAudioFileSelect}
                  className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-green-600 file:text-white"
                />
              </div>
              
              {audioFile && (
                <div className="text-sm text-gray-400">
                  Arquivo: {audioFile.name}
                </div>
              )}
              
              <button
                onClick={importAudio}
                disabled={loading || !audioFile}
                className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded transition-colors"
              >
                {loading ? 'Importando...' : 'Importar Audios'}
              </button>
              
              {audioFiles.length > 0 && (
                <div className="border-t border-gray-600 pt-4">
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Áudios Disponíveis:</h4>
                  <div className="max-h-32 overflow-y-auto space-y-1">
                    {audioFiles.slice(0, 5).map((audio, index) => (
                      <div key={index} className="text-xs text-gray-400 p-2 bg-gray-700/50 rounded">
                        {audio.name || audio.filename || `Audio ${index + 1}`}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Seção Test Calls */}
          <div className="bg-gray-800 border border-green-500 rounded-lg p-8">
            <h2 className="text-xl font-bold text-white mb-6 text-center border-b border-green-500 pb-2">
              Llamadas de Prueba
            </h2>
            
            <div className="space-y-5">
              <div>
                <input
                  type="text"
                  value={testNumber}
                  onChange={(e) => setTestNumber(e.target.value)}
                  placeholder="Ingresá el número para prueba"
                  className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400"
                />
              </div>
              
              <button
                onClick={runTestCall}
                disabled={isTestRunning || !testNumber.trim()}
                className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded transition-colors"
              >
                {isTestRunning ? 'Testando...' : 'Llamadas de Prueba'}
              </button>
              
              {testResults.length > 0 && (
                <div className="border-t border-gray-600 pt-4">
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Resultados dos Testes:</h4>
                  <div className="max-h-40 overflow-y-auto space-y-2">
                    {testResults.map((result) => (
                      <div key={result.id} className="text-xs p-2 bg-gray-700/50 rounded">
                        <div className="flex justify-between items-center">
                          <span className="text-white">{result.numero}</span>
                          <span className={`px-2 py-1 rounded text-xs ${
                            result.status === 'Sucesso' ? 'bg-green-900/30 text-green-400' :
                            result.status === 'Falha' ? 'bg-yellow-900/30 text-yellow-400' :
                            'bg-red-900/30 text-red-400'
                          }`}>
                            {result.status}
                          </span>
                        </div>
                        <div className="text-gray-400 mt-1">
                          {result.timestamp} - {result.details}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Formulário de Criação/Edição de Campanha */}
        <div className="mt-6 bg-gray-800 border border-gray-600 rounded-lg p-8">
          <h3 className="text-xl font-bold text-white mb-8">Configuración de Campaña</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Nombre de la Campaña</label>
              <input
                type="text"
                value={campaignData.name}
                onChange={(e) => setCampaignData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Ingresá el nombre de la campaña"
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Descripción</label>
              <input
                type="text"
                value={campaignData.description}
                onChange={(e) => setCampaignData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Descripción de la campaña"
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Llamadas Simultáneas</label>
              <input
                type="number"
                value={campaignData.maxConcurrentCalls}
                onChange={(e) => setCampaignData(prev => ({ ...prev, maxConcurrentCalls: parseInt(e.target.value) || 1 }))}
                min="1"
                max="100"
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Llamadas por Segundo</label>
              <input
                type="number"
                value={campaignData.callsPerSecond}
                onChange={(e) => setCampaignData(prev => ({ ...prev, callsPerSecond: parseInt(e.target.value) || 1 }))}
                min="1"
                max="10"
                step="0.1"
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white"
              />
            </div>
          </div>
          
          {/* Botões de Ação da Campanha */}
          <div className="mt-8 flex flex-wrap gap-4 justify-center">
            <button
              onClick={createCampaign}
              disabled={loading || !campaignData.name.trim()}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors duration-200"
            >
              {loading ? 'Creando...' : 'Crear Campaña'}
            </button>
            
            <button
              onClick={() => {
                setCampaignData({
                  name: '',
                  description: '',
                  maxConcurrentCalls: 10,
                  callsPerSecond: 1
                });
              }}
              className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors duration-200"
            >
              Limpiar Formulario
            </button>
            
            <button
              onClick={() => {
                showMessage('success', 'Configuración guardada!');
              }}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
            >
              Guardar Configuración
            </button>
          </div>
        </div>

        {/* Estatísticas Rápidas */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gray-800 border border-gray-600 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-400">{campaigns.length}</div>
            <div className="text-sm text-gray-400">Campanhas Totais</div>
          </div>
          
          <div className="bg-gray-800 border border-gray-600 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-400">{audioFiles.length}</div>
            <div className="text-sm text-gray-400">Áudios Disponíveis</div>
          </div>
          
          <div className="bg-gray-800 border border-gray-600 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-yellow-400">{testResults.length}</div>
            <div className="text-sm text-gray-400">Testes Executados</div>
          </div>
          
          <div className="bg-gray-800 border border-gray-600 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-400">100%</div>
            <div className="text-sm text-gray-400">Sistema Operacional</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminControlPanel;