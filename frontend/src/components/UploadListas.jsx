import React, { useState, useEffect, useRef } from 'react';
import { makeApiRequest } from '../config/api.js';

/**
 * Componente de Estado Profesional para Upload
 */
const UploadStatusCard = ({ title, value, subtitle, icon, color = 'primary', loading = false }) => {
  const colorClasses = {
    primary: 'from-primary-500/20 to-primary-600/20 border-primary-500/30',
    success: 'from-green-500/20 to-green-600/20 border-green-500/30',
    warning: 'from-yellow-500/20 to-yellow-600/20 border-yellow-500/30',
    error: 'from-error-500/20 to-error-600/20 border-error-500/30'
  };

  const iconColorClasses = {
    primary: 'text-primary-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-error-400'
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} border backdrop-blur-sm rounded-xl p-6 transition-all duration-300 hover:scale-105`}>
      <div className="flex items-center justify-between mb-3">
        <div className={`p-2 rounded-lg bg-gray-800/50 ${iconColorClasses[color]}`}>
          {icon}
        </div>
        {loading && (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
        )}
      </div>
      <div className="space-y-1">
        <p className="text-sm font-medium text-gray-300">{title}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
        {subtitle && (
          <p className="text-xs text-gray-400">{subtitle}</p>
        )}
      </div>
    </div>
  );
};

/**
 * Estados del archivo
 */
const FileStates = {
  IDLE: 'idle',
  READING: 'reading',
  PREVIEW: 'preview',
  UPLOADING: 'uploading',
  SUCCESS: 'success',
  ERROR: 'error'
};

/**
 * Componente para upload y gestión de listas de contactos profesional
 */
function UploadListas() {
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState('');
  const [file, setFile] = useState(null);
  const [fileState, setFileState] = useState(FileStates.IDLE);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    // Cargar campañas disponibles
    loadCampaigns();
  }, []);

  // Debug: Log dos estados principais
  useEffect(() => {
    console.log('🔍 Estado atual:', {
      fileState,
      uploading,
      selectedCampaign,
      file: file?.name,
      campaigns: campaigns.length,
      previewData: !!previewData
    });
  }, [fileState, uploading, selectedCampaign, file, campaigns, previewData]);

  /**
   * Buscar campañas de la API
   */
  const loadCampaigns = async () => {
    try {
      const data = await makeApiRequest('/campaigns');
      console.log('📋 Campanhas carregadas:', data);
      const campaignsList = data.campaigns || [];
      setCampaigns(campaignsList);
      
      // Se não há campanhas, criar uma campanha padrão automaticamente
      if (campaignsList.length === 0) {
        console.log('🏗️ Criando campanha padrão...');
        await createDefaultCampaign();
      } else {
        // Se há campanhas, selecionar a primeira automaticamente
        setSelectedCampaign(campaignsList[0].id.toString());
      }
    } catch (err) {
      console.error('❌ Erro ao carregar campanhas:', err);
      // Se falhar ao carregar campanhas, criar uma padrão
      await createDefaultCampaign();
    }
  };

  /**
   * Criar campanha padrão para upload
   */
  const createDefaultCampaign = async () => {
    try {
      const defaultCampaign = {
        name: 'Campanha Upload Automático',
        description: 'Campanha criada automaticamente para uploads de listas',
        status: 'active',
        wait_time: 2.0
      };

      console.log('🎯 Criando campanha padrão:', defaultCampaign);
      const response = await makeApiRequest('/campaigns', 'POST', defaultCampaign);
      
      if (response && response.id) {
        const newCampaign = {
          id: response.id,
          name: defaultCampaign.name,
          status: defaultCampaign.status
        };
        
        setCampaigns([newCampaign]);
        setSelectedCampaign(response.id.toString());
        console.log('✅ Campanha padrão criada:', newCampaign);
      }
    } catch (err) {
      console.error('❌ Erro ao criar campanha padrão:', err);
      // Se falhar, permitir upload sem campanha
      setCampaigns([{
        id: 'default',
        name: 'Sem Campanha (Upload Direto)',
        status: 'active'
      }]);
      setSelectedCampaign('default');
    }
  };

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;

    console.log('📁 Arquivo selecionado:', {
      name: selectedFile.name,
      size: selectedFile.size,
      type: selectedFile.type
    });

    setFile(selectedFile);
    setFileState(FileStates.READING);
    setError(null);
    setUploadResult(null);

    // Leer arquivo para preview
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const lines = text.split('\n').filter(line => line.trim());
        
        if (lines.length === 0) {
          setError('El archivo está vacío');
          setFileState(FileStates.ERROR);
          return;
        }

        console.log('📋 Primeiras linhas do arquivo:', lines.slice(0, 3));

        // Detectar separador automaticamente
        const firstLine = lines[0];
        let separator = ',';
        
        if (firstLine.includes('\t')) {
          separator = '\t';
        } else if (firstLine.includes(';')) {
          separator = ';';
        } else if (firstLine.includes('|')) {
          separator = '|';
        } else if (!firstLine.includes(',')) {
          // Se não tem vírgula, pode ser um arquivo TXT com apenas números
          separator = null;
        }

        console.log('🔍 Separador detectado:', separator || 'linha única');

        let headers = [];
        let preview = [];

        if (separator) {
          // Arquivo com separadores (CSV, TSV, etc.)
          headers = firstLine.split(separator).map(h => h.trim().replace(/"/g, ''));
          preview = lines.slice(1, 6).map(line => {
            const values = line.split(separator).map(v => v.trim().replace(/"/g, ''));
            const row = {};
            headers.forEach((header, index) => {
              row[header] = values[index] || '';
            });
            return row;
          });
        } else {
          // Arquivo TXT simples (uma coluna por linha)
          headers = ['telefone'];
          preview = lines.slice(0, 5).map(line => ({
            telefone: line.trim()
          }));
        }

        console.log('📊 Preview processado:', { headers, preview });

        setPreviewData({
          headers,
          preview,
          totalRows: separator ? lines.length - 1 : lines.length,
          separator
        });
        setFileState(FileStates.PREVIEW);
      } catch (err) {
        console.error('❌ Erro ao processar arquivo:', err);
        setError('Error al leer el archivo: ' + err.message);
        setFileState(FileStates.ERROR);
      }
    };

    reader.onerror = () => {
      setError('Error al leer el archivo');
      setFileState(FileStates.ERROR);
    };

    reader.readAsText(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Seleccioná un archivo para subir');
      return;
    }

    // Se não há campanha selecionada, usar "default"
    const campaignId = selectedCampaign || 'default';

    setUploading(true);
    setFileState(FileStates.UPLOADING);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', file); // Usar 'arquivo' que é o que o endpoint espera
      formData.append('incluir_nome', 'true');
      formData.append('pais_preferido', 'auto');
      
      // CORREÇÃO CRÍTICA: Sempre incluir campaign_id se disponível
      if (campaignId && campaignId !== 'default') {
        formData.append('campaign_id', campaignId);
      }

      console.log('📤 Enviando upload:', {
        file: file.name,
        campaign: campaignId,
        size: file.size,
        campaign_id_included: !!(campaignId && campaignId !== 'default')
      });

      const response = await makeApiRequest('/contacts/upload', 'POST', formData);
      
      console.log('📥 Resposta do upload:', response);
      
      setUploadResult({
        total_lines: response.total_lineas_archivo || 0,
        contacts_added: response.contatos_validos || 0,
        errors_count: response.contatos_invalidos || 0,
        duplicates_count: response.contatos_duplicados || 0,
        message: response.mensaje || 'Upload realizado com sucesso'
      });
      setFileState(FileStates.SUCCESS);
      setFile(null);
      setPreviewData(null);
    } catch (error) {
      console.error('❌ Erro no upload:', error);
      setError('Error al cargar el archivo: ' + error.message);
      setFileState(FileStates.ERROR);
    } finally {
      setUploading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setFileState(FileStates.IDLE);
    setError(null);
    setUploadResult(null);
    setPreviewData(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4 bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
            Subida de Listas
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Subí tus listas de contactos con detección inteligente
          </p>
        </div>

        {/* Success Result */}
        {fileState === FileStates.SUCCESS && uploadResult && (
          <div className="mb-8 bg-gradient-to-r from-green-500/20 to-green-600/20 border border-green-500/50 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Resultado del Upload</h2>
              <button
                onClick={resetForm}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                Subir Otra Lista
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <UploadStatusCard
                title="Total Líneas"
                value={uploadResult.total_lines || 0}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                }
              />
              <UploadStatusCard
                title="Contactos Agregados"
                value={uploadResult.contacts_added || 0}
                subtitle="Importados con éxito"
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                  </svg>
                }
                color="success"
              />
              <UploadStatusCard
                title="Tasa de Éxito"
                value={`${uploadResult.total_lines > 0
                  ? Math.round((uploadResult.contacts_added / uploadResult.total_lines) * 100)
                  : 0}%`}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                }
                color="warning"
              />
              <UploadStatusCard
                title="Duplicados"
                value={uploadResult.duplicates_count || 0}
                subtitle="Removidos automáticamente"
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                }
                color="info"
              />
              <UploadStatusCard
                title="Errores"
                value={uploadResult.errors_count || 0}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                }
                color="error"
              />
            </div>
            
            <div className="bg-gray-700/50 rounded-lg p-4">
              <p className="text-green-400 font-medium">{uploadResult.message}</p>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mb-8 bg-gradient-to-r from-red-500/20 to-red-600/20 border border-red-500/50 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center">
              <svg className="w-6 h-6 text-red-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-red-400 font-medium">{error}</p>
            </div>
          </div>
        )}

        {/* Upload Form */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 p-8">
          <div className="space-y-6">
            {/* Campaign Status */}
            <div className="bg-gray-700/30 rounded-lg p-4 border border-gray-600/50">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-white">Status da Campanha</h3>
                <button
                  onClick={loadCampaigns}
                  className="px-3 py-1 bg-primary-600 hover:bg-primary-700 text-white text-sm rounded-lg transition-colors"
                  disabled={uploading}
                >
                  🔄 Atualizar
                </button>
              </div>
              {campaigns.length > 0 ? (
                <div className="flex items-center text-green-400">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Campanha ativa: {campaigns.find(c => c.id.toString() === selectedCampaign)?.name || 'Carregando...'}</span>
                </div>
              ) : (
                <div className="flex items-center text-yellow-400">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Criando campanha automática...</span>
                </div>
              )}
            </div>

            {/* Campaign Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Seleccionar Campaña {campaigns.length === 0 && <span className="text-gray-500">(Opcional - será criada automaticamente)</span>}
              </label>
              <select
                value={selectedCampaign}
                onChange={(e) => setSelectedCampaign(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                disabled={uploading}
              >
                {campaigns.length === 0 ? (
                  <option value="">Carregando campanhas...</option>
                ) : (
                  <>
                    {campaigns.map((campaign) => (
                      <option key={campaign.id} value={campaign.id}>
                        {campaign.name} ({campaign.status})
                      </option>
                    ))}
                  </>
                )}
              </select>
            </div>

            {/* File Upload Area */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Archivo CSV ou TXT
              </label>
              <div
                className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
                  dragOver
                    ? 'border-primary-500 bg-primary-500/10'
                    : fileState === FileStates.PREVIEW
                    ? 'border-green-500 bg-green-500/10'
                    : 'border-gray-600 hover:border-gray-500'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                {fileState === FileStates.READING ? (
                  <div className="flex flex-col items-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mb-4"></div>
                    <p className="text-gray-300">Leyendo archivo...</p>
                  </div>
                ) : fileState === FileStates.PREVIEW ? (
                  <div className="flex flex-col items-center">
                    <svg className="w-12 h-12 text-green-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-green-400 font-medium mb-2">{file?.name}</p>
                    <p className="text-gray-400">Archivo listo para subir</p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    <svg className="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 48 48">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" />
                    </svg>
                    <p className="text-gray-300 text-lg font-medium mb-2">Arrastrá tu archivo CSV ou TXT acá</p>
                    <p className="text-gray-500 mb-4">o</p>
                    <input
                      type="file"
                      accept=".csv,.txt,.tsv"
                      onChange={(e) => handleFileSelect(e.target.files?.[0])}
                      className="hidden"
                      id="file-upload"
                      disabled={uploading}
                    />
                    <label
                      htmlFor="file-upload"
                      className="inline-flex items-center px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg cursor-pointer transition-colors"
                    >
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      Seleccionar Archivo
                    </label>
                  </div>
                )}
              </div>
            </div>

            {/* Upload Button */}
            {fileState === FileStates.PREVIEW && (
              <div className="flex justify-between items-center">
                <button
                  onClick={resetForm}
                  className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors"
                  disabled={uploading}
                >
                  Cancelar
                </button>
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="px-8 py-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-medium rounded-lg transition-all duration-200 flex items-center"
                >
                  {uploading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Subiendo...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Subir Lista
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Preview Section */}
        {previewData && (
          <div className="mt-8 bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-600/20 to-blue-800/20 p-6 border-b border-gray-700/50">
              <h3 className="text-xl font-bold text-white">Vista Previa del Archivo</h3>
              <p className="text-gray-300 mt-2">
                {previewData.totalRows} líneas detectadas
              </p>
            </div>
            
            <div className="p-6">
              {previewData && (
                <div className="overflow-x-auto">
                  <table className="w-full border border-gray-700 rounded-lg overflow-hidden">
                    <thead>
                      <tr className="bg-gray-700">
                        <th className="px-4 py-3 text-left text-white font-medium border-b border-gray-600">
                          #
                        </th>
                        {previewData.headers?.map((header, index) => (
                          <th key={index} className="px-4 py-3 text-left text-white font-medium border-b border-gray-600">
                            {header}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {previewData.preview?.map((row, index) => (
                        <tr key={index} className="border-b border-gray-700 hover:bg-gray-700/30">
                          <td className="px-4 py-3 text-gray-300">{index + 1}</td>
                          <td className="px-4 py-3 text-gray-300">
                            {row[previewData.headers[0]] || '-'}
                          </td>
                          <td className="px-4 py-3 text-gray-300">
                            {row[previewData.headers[1]] || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Help Section */}
        <div className="mt-8 bg-gradient-to-r from-purple-600/10 to-purple-800/10 border border-purple-500/30 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">💡 Consejos para el Upload</h3>
          <ul className="space-y-2 text-gray-300">
            <li className="flex items-start">
              <svg className="w-5 h-5 text-purple-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              El sistema detecta automáticamente números de teléfono y nombres.
            </li>
            <li className="flex items-start">
              <svg className="w-5 h-5 text-purple-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Usá archivos CSV con headers en la primera línea.
            </li>
            <li className="flex items-start">
              <svg className="w-5 h-5 text-purple-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Los números duplicados se detectan y se evitan automáticamente.
            </li>
            <li className="flex items-start">
              <svg className="w-5 h-5 text-purple-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Formato recomendado: número,nombre (ejemplo: 1155667788,Juan Pérez).
            </li>
            <li className="flex items-start">
              <svg className="w-5 h-5 text-purple-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Tamaño máximo recomendado: 10,000 contactos por archivo.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default UploadListas; 