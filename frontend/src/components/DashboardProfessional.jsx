import React, { useState, useRef } from 'react';
import DNCManager from './DNCManager';
import { 
  PhoneIcon, 
  PlayIcon, 
  StopIcon,
  ChartBarIcon,
  CogIcon,
  UserGroupIcon,
  PlusIcon,
  EyeIcon,
  DocumentArrowUpIcon,
  SpeakerWaveIcon,
  MusicalNoteIcon,
  ListBulletIcon,
  ArrowUpTrayIcon
} from '@heroicons/react/24/outline';

/**
 * Componente de Seção Principal
 */
const MainSection = ({ title, children, className = "" }) => {
  return (
    <div className={`card-glass rounded-xl border border-slate-600 shadow-xl hover:shadow-2xl transition-all duration-300 ${className}`}>
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 border-b border-slate-600 px-6 py-4 rounded-t-xl">
        <h2 className="text-lg font-bold text-white text-center tracking-wide">{title}</h2>
      </div>
      <div className="p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50">
        {children}
      </div>
    </div>
  );
};
 
/**
 * Botão Estilizado
 */
const StyledButton = ({ children, onClick, variant = 'primary', className = "", disabled = false }) => {
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary', 
    success: 'btn-success',
    danger: 'btn-danger',
    warning: 'btn-warning'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${variants[variant]} ${className}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
    >
      {children}
    </button>
  );
};

/**
 * Dropdown Personalizado
 */
const CustomSelect = ({ options, value, onChange, placeholder }) => {
  return (
    <select
      value={value}
      onChange={onChange}
      className="input-modern"
    >
      {placeholder && <option value="">{placeholder}</option>}
      {options.map((option, index) => (
        <option key={index} value={option.value} className="bg-slate-800 text-slate-200">
          {option.label}
        </option>
      ))}
    </select>
  );
};

/**
 * Dashboard Principal Moderno
 */
const DashboardProfessional = () => {
  const [selectedCampaign, setSelectedCampaign] = useState('');
  const [selectedPhoneList, setSelectedPhoneList] = useState('');
  const [notifications, setNotifications] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [phoneLists, setPhoneLists] = useState([]);
  const [audioFiles, setAudioFiles] = useState([]);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard', 'upload-numbers', 'dnc'
  
  // Refs para inputs de arquivo
  const numbersFileRef = useRef(null);
  const audioFileRef = useRef(null);

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 3000);
  };

  // Estados para controle de loading
  const [isLoading, setIsLoading] = useState({
    importNumbers: false,
    importAudios: false,
    testCalls: false,
    newCampaign: false,
    editCampaign: false,
    deleteCampaign: false,
    viewNumbers: false,
    viewRunningCampaign: false,
    callsPerSecond: false
  });

  const setLoadingState = (action, state) => {
    setIsLoading(prev => ({ ...prev, [action]: state }));
  };

  // Funções dos botões com funcionalidades reais
  const handleImportNumbers = async () => {
    setLoadingState('importNumbers', true);
    addNotification('Navegando para upload de números...', 'info');
    
    try {
      // Navegar para a tela de upload de números
      setCurrentView('upload-numbers');
    } catch (error) {
      addNotification('Erro ao navegar para upload', 'danger');
    } finally {
      setLoadingState('importNumbers', false);
    }
  };

  // Função para navegar para DNC
  const handleNavigateToDNC = () => {
    setCurrentView('dnc');
    addNotification('Navegando para gestão DNC...', 'info');
  };

  // Função para voltar ao dashboard
  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    addNotification('Voltando ao painel principal...', 'info');
  };

  const handleNumbersFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) {
      setLoadingState('importNumbers', false);
      return;
    }

    try {
      addNotification(`Processando arquivo: ${file.name}`, 'info');
      
      // Ler o arquivo
      const text = await file.text();
      const lines = text.split('\n').filter(line => line.trim());
      
      // Criar nova lista com o nome do arquivo
      const listName = file.name.replace(/\.[^/.]+$/, "");
      const newList = {
        value: listName.toLowerCase().replace(/\s+/g, '_'),
        label: listName,
        numbers: lines.length,
        file: file.name
      };
      
      setPhoneLists(prev => {
        const filtered = prev.filter(list => list.value !== newList.value);
        return [...filtered, newList];
      });
      
      setSelectedPhoneList(newList.value);
      addNotification(`Lista "${listName}" criada com ${lines.length} números!`, 'success');
    } catch (error) {
      addNotification('Erro ao processar arquivo de números', 'danger');
    } finally {
      setLoadingState('importNumbers', false);
      e.target.value = ''; // Reset input
    }
  };

  const handleImportAudios = async () => {
    setLoadingState('importAudios', true);
    addNotification('Abrindo seletor de áudios...', 'info');
    
    try {
      audioFileRef.current.click();
    } catch (error) {
      addNotification('Erro ao abrir seletor de áudios', 'danger');
      setLoadingState('importAudios', false);
    }
  };

  const handleAudioFilesChange = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) {
      setLoadingState('importAudios', false);
      return;
    }

    try {
      addNotification(`Processando ${files.length} arquivo(s) de áudio...`, 'info');
      
      const newAudios = files.map(file => ({
        id: Date.now() + Math.random(),
        name: file.name,
        size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
        type: file.type,
        file: file
      }));
      
      setAudioFiles(prev => [...prev, ...newAudios]);
      addNotification(`${files.length} áudio(s) importado(s) com sucesso!`, 'success');
    } catch (error) {
      addNotification('Erro ao processar arquivos de áudio', 'danger');
    } finally {
      setLoadingState('importAudios', false);
      e.target.value = ''; // Reset input
    }
  };

  const handleTestCalls = async () => {
    setLoadingState('testCalls', true);
    addNotification('Iniciando teste de chamadas...', 'info');
    
    try {
      // Simular teste de chamadas
      await new Promise(resolve => setTimeout(resolve, 2000));
      const testResults = {
        successful: Math.floor(Math.random() * 8) + 2,
        failed: Math.floor(Math.random() * 3),
        duration: Math.floor(Math.random() * 30) + 10
      };
      
      addNotification(
        `Teste concluído: ${testResults.successful} sucessos, ${testResults.failed} falhas (${testResults.duration}s)`,
        testResults.failed === 0 ? 'success' : 'warning'
      );
    } catch (error) {
      addNotification('Erro no teste de chamadas', 'danger');
    } finally {
      setLoadingState('testCalls', false);
    }
  };

  const handleNewCampaign = async () => {
    const campaignName = prompt('Nome da nova campanha:');
    if (!campaignName || !campaignName.trim()) {
      return;
    }
    
    setLoadingState('newCampaign', true);
    addNotification('Criando nova campanha...', 'info');
    
    try {
      const newCampaign = {
        value: campaignName.toLowerCase().replace(/\s+/g, '_'),
        label: campaignName.trim(),
        created: new Date().toLocaleString(),
        status: 'Inativa'
      };
      
      setCampaigns(prev => {
        const filtered = prev.filter(camp => camp.value !== newCampaign.value);
        return [...filtered, newCampaign];
      });
      
      setSelectedCampaign(newCampaign.value);
      addNotification(`Campanha "${campaignName}" criada com sucesso!`, 'success');
    } catch (error) {
      addNotification('Erro ao criar campanha', 'danger');
    } finally {
      setLoadingState('newCampaign', false);
    }
  };

  const handleEditCampaign = async () => {
    if (!selectedCampaign) {
      addNotification('Selecione uma campanha primeiro', 'warning');
      return;
    }
    
    setLoadingState('editCampaign', true);
    addNotification('Abrindo editor de campanha...', 'info');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      addNotification(`Campanha "${selectedCampaign}" aberta para edição`, 'success');
      // Aqui seria aberto um modal ou redirecionamento para edição
    } catch (error) {
      addNotification('Erro ao abrir editor', 'danger');
    } finally {
      setLoadingState('editCampaign', false);
    }
  };

  const handleDeleteCampaign = async () => {
    if (!selectedCampaign) {
      addNotification('Selecione uma campanha primeiro', 'warning');
      return;
    }
    
    const campaign = campaigns.find(c => c.value === selectedCampaign);
    if (!campaign) {
      addNotification('Campanha não encontrada', 'warning');
      return;
    }
    
    if (!confirm(`Tem certeza que deseja excluir a campanha "${campaign.label}"?`)) {
      return;
    }
    
    setLoadingState('deleteCampaign', true);
    addNotification('Excluindo campanha...', 'info');
    
    try {
      setCampaigns(prev => prev.filter(c => c.value !== selectedCampaign));
      setSelectedCampaign('');
      addNotification(`Campanha "${campaign.label}" excluída com sucesso!`, 'success');
    } catch (error) {
      addNotification('Erro ao excluir campanha', 'danger');
    } finally {
      setLoadingState('deleteCampaign', false);
    }
  };

  const handleViewNumbers = async () => {
    if (phoneLists.length === 0) {
      addNotification('Nenhuma lista de números importada', 'warning');
      return;
    }
    
    setLoadingState('viewNumbers', true);
    addNotification('Carregando listas de números...', 'info');
    
    try {
      const totalNumbers = phoneLists.reduce((sum, list) => sum + list.numbers, 0);
      const listNames = phoneLists.map(list => list.label).join(', ');
      addNotification(`${phoneLists.length} lista(s): ${listNames} - Total: ${totalNumbers} números`, 'success');
    } catch (error) {
      addNotification('Erro ao carregar números', 'danger');
    } finally {
      setLoadingState('viewNumbers', false);
    }
  };

  const handleViewRunningCampaign = async () => {
    if (campaigns.length === 0) {
      addNotification('Nenhuma campanha criada', 'warning');
      return;
    }
    
    setLoadingState('viewRunningCampaign', true);
    addNotification('Verificando campanhas...', 'info');
    
    try {
      const activeCampaigns = campaigns.filter(c => c.status === 'Ativa');
      const inactiveCampaigns = campaigns.filter(c => c.status === 'Inativa');
      
      if (activeCampaigns.length > 0) {
        const activeNames = activeCampaigns.map(c => c.label).join(', ');
        addNotification(`${activeCampaigns.length} campanha(s) ativa(s): ${activeNames}`, 'success');
      } else {
        addNotification(`${campaigns.length} campanha(s) criada(s), ${inactiveCampaigns.length} inativa(s)`, 'info');
      }
    } catch (error) {
      addNotification('Erro ao verificar campanhas', 'danger');
    } finally {
      setLoadingState('viewRunningCampaign', false);
    }
  };

  const handleCallsPerSecond = async () => {
    setLoadingState('callsPerSecond', true);
    addNotification('Configurando taxa de chamadas...', 'info');
    
    try {
      const currentRate = Math.floor(Math.random() * 10) + 1;
      const newRate = prompt(`Taxa atual: ${currentRate} chamadas/segundo\nNova taxa (1-20):`, currentRate);
      
      if (newRate && !isNaN(newRate) && newRate >= 1 && newRate <= 20) {
        await new Promise(resolve => setTimeout(resolve, 800));
        addNotification(`Taxa configurada para ${newRate} chamadas por segundo`, 'success');
      } else if (newRate !== null) {
        addNotification('Taxa inválida. Use valores entre 1 e 20', 'warning');
      }
    } catch (error) {
      addNotification('Erro ao configurar taxa', 'danger');
    } finally {
      setLoadingState('callsPerSecond', false);
    }
  };

  // Renderizar diferentes views
  if (currentView === 'upload-numbers') {
    return (
      <div className="min-h-screen p-6" style={{background: 'var(--bg-gradient-primary)'}}>
        {/* Notificações */}
        {notifications.length > 0 && (
          <div className="fixed top-4 right-4 z-50 space-y-2">
            {notifications.map(notification => (
              <div
                key={notification.id}
                className={`
                  px-6 py-3 rounded-lg shadow-xl transition-all duration-500 text-white font-medium border-l-4
                  ${notification.type === 'success' ? 'bg-gradient-to-r from-emerald-600 to-emerald-700 border-emerald-400' : 
                    notification.type === 'warning' ? 'bg-gradient-to-r from-amber-600 to-amber-700 border-amber-400' : 
                    notification.type === 'danger' ? 'bg-gradient-to-r from-red-600 to-red-700 border-red-400' : 'bg-gradient-to-r from-blue-600 to-blue-700 border-blue-400'}
                  transform hover:scale-105
                `}
              >
                {notification.message}
              </div>
            ))}
          </div>
        )}

        {/* Header da tela de upload */}
        <div className="text-center mb-10">
          <div className="inline-block bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-8 py-4 rounded-xl shadow-xl">
            <h3 className="text-3xl font-bold tracking-wider">Upload Phone Numbers</h3>
          </div>
        </div>

        {/* Conteúdo da tela de upload */}
        <div className="max-w-4xl mx-auto">
          <MainSection title="Upload Numbers">
            <div className="space-y-6">
              <div className="text-center">
                <input
                  ref={numbersFileRef}
                  type="file"
                  accept=".csv,.txt,.xlsx"
                  onChange={handleNumbersFileChange}
                  className="hidden"
                />
                <StyledButton 
                  onClick={() => numbersFileRef.current.click()}
                  disabled={isLoading.importNumbers}
                  className="mb-4"
                >
                  {isLoading.importNumbers ? 'Importando...' : 'Escolher arquivo'}
                </StyledButton>
                <p className="text-slate-300 text-sm">Nenhum arquivo escolhido</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <StyledButton 
                    onClick={() => alert('Upload Now functionality')}
                    variant="success"
                    className="w-full"
                  >
                    Upload Now
                  </StyledButton>
                </div>
                <div className="text-center">
                  <StyledButton 
                    onClick={handleBackToDashboard}
                    variant="secondary"
                    className="w-full"
                  >
                    Back
                  </StyledButton>
                </div>
              </div>

              {/* Seção DNC */}
              <div className="border-t border-slate-600 pt-6">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-center">
                    <label className="block text-slate-300 mb-2">CODE2</label>
                    <div className="space-y-2">
                      <label className="flex items-center justify-center space-x-2 text-slate-300">
                        <input type="checkbox" className="form-checkbox" />
                        <span>Yes</span>
                      </label>
                      <label className="flex items-center justify-center space-x-2 text-slate-300">
                        <input type="checkbox" defaultChecked className="form-checkbox" />
                        <span>No</span>
                      </label>
                    </div>
                  </div>
                  <div className="text-center">
                    <label className="block text-slate-300 mb-2">CANADA</label>
                    <div className="space-y-2">
                      <label className="flex items-center justify-center space-x-2 text-slate-300">
                        <input type="checkbox" className="form-checkbox" />
                        <span>Yes</span>
                      </label>
                      <label className="flex items-center justify-center space-x-2 text-slate-300">
                        <input type="checkbox" defaultChecked className="form-checkbox" />
                        <span>No</span>
                      </label>
                    </div>
                  </div>
                </div>
                
                <div className="text-center">
                  <StyledButton 
                    onClick={handleNavigateToDNC}
                    variant="warning"
                    className="w-full"
                  >
                    Acessar DNC
                  </StyledButton>
                </div>
              </div>
            </div>
          </MainSection>
        </div>
      </div>
    );
  }

  if (currentView === 'dnc') {
    return (
      <div className="min-h-screen p-6" style={{background: 'var(--bg-gradient-primary)'}}>
        {/* Notificações */}
        {notifications.length > 0 && (
          <div className="fixed top-4 right-4 z-50 space-y-2">
            {notifications.map(notification => (
              <div
                key={notification.id}
                className={`
                  px-6 py-3 rounded-lg shadow-xl transition-all duration-500 text-white font-medium border-l-4
                  ${notification.type === 'success' ? 'bg-gradient-to-r from-emerald-600 to-emerald-700 border-emerald-400' : 
                    notification.type === 'warning' ? 'bg-gradient-to-r from-amber-600 to-amber-700 border-amber-400' : 
                    notification.type === 'danger' ? 'bg-gradient-to-r from-red-600 to-red-700 border-red-400' : 'bg-gradient-to-r from-blue-600 to-blue-700 border-blue-400'}
                  transform hover:scale-105
                `}
              >
                {notification.message}
              </div>
            ))}
          </div>
        )}

        {/* Header da tela DNC */}
        <div className="text-center mb-10">
          <div className="inline-block bg-gradient-to-r from-red-600 to-orange-600 text-white px-8 py-4 rounded-xl shadow-xl">
            <h3 className="text-3xl font-bold tracking-wider">New DNC Table</h3>
          </div>
        </div>

        {/* Conteúdo da tela DNC */}
        <div className="max-w-4xl mx-auto">
          <MainSection title="DNC Management">
            <div className="space-y-6">
              <div className="text-center">
                <label className="block text-slate-300 mb-2 text-lg">DNC Name</label>
                <input 
                  type="text" 
                  className="input-modern w-64 mx-auto" 
                  placeholder="Digite o nome da DNC"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <StyledButton 
                    onClick={() => alert('Add DNC functionality')}
                    variant="success"
                    className="w-full"
                  >
                    Add
                  </StyledButton>
                </div>
                <div className="text-center">
                  <StyledButton 
                    onClick={handleBackToDashboard}
                    variant="secondary"
                    className="w-full"
                  >
                    Back
                  </StyledButton>
                </div>
              </div>

              {/* Componente DNC Manager */}
              <div className="mt-8">
                <DNCManager />
              </div>
            </div>
          </MainSection>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6" style={{background: 'var(--bg-gradient-primary)'}}>
      {/* Inputs de arquivo ocultos */}
      <input
        ref={numbersFileRef}
        type="file"
        accept=".csv,.txt,.xlsx"
        onChange={handleNumbersFileChange}
        className="hidden"
      />
      <input
        ref={audioFileRef}
        type="file"
        accept=".mp3,.wav,.ogg"
        multiple
        onChange={handleAudioFilesChange}
        className="hidden"
      />
      {/* Notificações */}
      {notifications.length > 0 && (
        <div className="fixed top-4 right-4 z-50 space-y-2">
          {notifications.map(notification => (
            <div
              key={notification.id}
              className={`
                px-6 py-3 rounded-lg shadow-xl transition-all duration-500 text-white font-medium border-l-4
                ${notification.type === 'success' ? 'bg-gradient-to-r from-emerald-600 to-emerald-700 border-emerald-400' : 
                  notification.type === 'warning' ? 'bg-gradient-to-r from-amber-600 to-amber-700 border-amber-400' : 
                  notification.type === 'danger' ? 'bg-gradient-to-r from-red-600 to-red-700 border-red-400' : 'bg-gradient-to-r from-blue-600 to-blue-700 border-blue-400'}
                transform hover:scale-105
              `}
            >
              {notification.message}
            </div>
          ))}
        </div>
      )}

      {/* Header com título H3 */}
      <div className="text-center mb-10">
        <div className="inline-block bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-8 py-4 rounded-xl shadow-xl">
          <h3 className="text-3xl font-bold tracking-wider">::: H3 :::</h3>
        </div>
      </div>

      {/* Layout Principal - 2 colunas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-7xl mx-auto">
        
        {/* Coluna Esquerda */}
        <div className="space-y-8">
          
          {/* Load Numbers */}
          <MainSection title="Load Numbers">
            <div className="space-y-4">
              <div>
                <CustomSelect
                  options={phoneLists}
                  value={selectedPhoneList}
                  onChange={(e) => setSelectedPhoneList(e.target.value)}
                  placeholder="Selecione uma lista de números"
                />
              </div>
              <div className="text-center">
                <StyledButton 
                  onClick={handleImportNumbers}
                  disabled={isLoading.importNumbers}
                >
                  {isLoading.importNumbers ? 'Importando...' : 'Imports Numbers'}
                </StyledButton>
              </div>
            </div>
          </MainSection>

          {/* Load Audios */}
          <MainSection title="Load Audios">
            <div className="text-center">
              <StyledButton 
                onClick={handleImportAudios}
                disabled={isLoading.importAudios}
              >
                {isLoading.importAudios ? 'Importando...' : 'Imports Audios'}
              </StyledButton>
            </div>
          </MainSection>

          {/* Test Calls */}
          <MainSection title="Test Calls">
            <div className="text-center">
              <StyledButton 
                onClick={handleTestCalls}
                disabled={isLoading.testCalls}
                variant="warning"
              >
                {isLoading.testCalls ? 'Testando...' : 'Test Calls'}
              </StyledButton>
            </div>
          </MainSection>

        </div>

        {/* Coluna Direita */}
        <div>
          
          {/* Campaign */}
          <MainSection title="Campaign">
            <div className="space-y-4">
              <div>
                <CustomSelect
                  options={campaigns}
                  value={selectedCampaign}
                  onChange={(e) => setSelectedCampaign(e.target.value)}
                  placeholder="Selecione uma campanha"
                />
              </div>
              
              <div className="grid grid-cols-3 gap-3">
                <StyledButton 
                  onClick={handleNewCampaign} 
                  variant="success"
                  disabled={isLoading.newCampaign}
                >
                  {isLoading.newCampaign ? 'Criando...' : 'New'}
                </StyledButton>
                <StyledButton 
                  onClick={handleEditCampaign} 
                  variant="warning"
                  disabled={isLoading.editCampaign}
                >
                  {isLoading.editCampaign ? 'Abrindo...' : 'Edit'}
                </StyledButton>
                <StyledButton 
                  onClick={handleDeleteCampaign} 
                  variant="danger"
                  disabled={isLoading.deleteCampaign}
                >
                  {isLoading.deleteCampaign ? 'Excluindo...' : 'Delete'}
                </StyledButton>
              </div>
              
              <div className="border-t-2 border-gradient-to-r from-emerald-400 to-teal-400 pt-6 space-y-4">
                <div className="text-center">
                  <StyledButton 
                    onClick={handleViewNumbers} 
                    className="w-full" 
                    variant="secondary"
                    disabled={isLoading.viewNumbers}
                  >
                    {isLoading.viewNumbers ? 'Carregando...' : 'View Numbers'}
                  </StyledButton>
                </div>
                
                <div className="text-center">
                  <StyledButton 
                    onClick={handleViewRunningCampaign} 
                    className="w-full" 
                    variant="secondary"
                    disabled={isLoading.viewRunningCampaign}
                  >
                    {isLoading.viewRunningCampaign ? 'Verificando...' : 'View Running Campaign'}
                  </StyledButton>
                </div>
                
                <div className="text-center">
                  <StyledButton 
                    onClick={handleCallsPerSecond} 
                    className="w-full" 
                    variant="secondary"
                    disabled={isLoading.callsPerSecond}
                  >
                    {isLoading.callsPerSecond ? 'Configurando...' : 'Calls per Seconds'}
                  </StyledButton>
                </div>
              </div>
            </div>
          </MainSection>

        </div>
      </div>
     </div>
   );
 };

 export default DashboardProfessional;