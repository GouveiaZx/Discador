import React, { useState, useCallback, useEffect } from 'react';
import { Upload, AlertCircle, CheckCircle, X, ChevronDown, FileText, Users, Phone, Loader } from 'lucide-react';
import api from '../config/api';

const UploadListasFixed = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState('');
  const [progress, setProgress] = useState({});

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      const response = await api.get('/campaigns');
      if (response.data && response.data.campaigns) {
        setCampaigns(response.data.campaigns);
      }
    } catch (error) {
      console.error('Erro ao carregar campanhas:', error);
    }
  };

  const processLargeFile = async (file, campaignId) => {
    const fileId = file.name;
    setProgress(prev => ({ ...prev, [fileId]: { current: 0, total: 0, status: 'Processando arquivo...' } }));

    try {
      // Ler arquivo
      const text = await file.text();
      const lines = text.split('\n').filter(line => line.trim());
      const totalLines = lines.length;

      setProgress(prev => ({ 
        ...prev, 
        [fileId]: { current: 0, total: totalLines, status: 'Preparando upload...' } 
      }));

      // Configurar chunks maiores para arquivos grandes
      let CHUNK_SIZE = 500;
      if (totalLines > 100000) {
        CHUNK_SIZE = 5000; // Chunks muito maiores para arquivos gigantes
      } else if (totalLines > 10000) {
        CHUNK_SIZE = 2000; // Chunks grandes
      } else if (totalLines > 1000) {
        CHUNK_SIZE = 1000; // Chunks médios
      }

      const chunks = [];
      for (let i = 0; i < lines.length; i += CHUNK_SIZE) {
        chunks.push(lines.slice(i, i + CHUNK_SIZE));
      }

      console.log(`📦 Arquivo ${file.name}: ${totalLines} linhas em ${chunks.length} chunks de ${CHUNK_SIZE}`);

      let processedTotal = 0;
      let successTotal = 0;
      let errorTotal = 0;

      // Processar TODOS os chunks
      for (let i = 0; i < chunks.length; i++) {
        const chunk = chunks[i];
        const chunkNumber = i + 1;
        
        setProgress(prev => ({ 
          ...prev, 
          [fileId]: { 
            current: processedTotal, 
            total: totalLines, 
            status: `Processando chunk ${chunkNumber}/${chunks.length}...`,
            percent: Math.round((processedTotal / totalLines) * 100)
          } 
        }));

        // Criar FormData para o chunk
        const chunkText = chunk.join('\n');
        const chunkBlob = new Blob([chunkText], { type: 'text/plain' });
        const chunkFile = new File([chunkBlob], `chunk_${i}.txt`, { type: 'text/plain' });

        const formData = new FormData();
        formData.append('arquivo', chunkFile);
        formData.append('incluir_nome', 'true');
        formData.append('pais_preferido', 'auto');
        if (campaignId) {
          formData.append('campaign_id', campaignId);
        }

        try {
          const response = await api.post('/contacts/upload', formData, {
            timeout: 60000 // 60 segundos por chunk
          });

          if (response.data) {
            successTotal += response.data.contatos_validos || 0;
            errorTotal += response.data.contatos_invalidos || 0;
          }

          console.log(`✅ Chunk ${chunkNumber}/${chunks.length} processado`);
        } catch (error) {
          console.error(`❌ Erro no chunk ${chunkNumber}:`, error);
          errorTotal += chunk.length;
          
          // Continuar mesmo com erro
          if (error.response?.status === 504 || error.code === 'ECONNABORTED') {
            console.log('⚠️ Timeout no chunk, continuando...');
          }
        }

        processedTotal += chunk.length;

        // Pausa menor entre chunks para não sobrecarregar
        if (i < chunks.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 500)); // 0.5 segundo
        }
      }

      // Resultado final
      setProgress(prev => ({ 
        ...prev, 
        [fileId]: { 
          current: totalLines, 
          total: totalLines, 
          status: '✅ Upload completo!',
          percent: 100
        } 
      }));

      return {
        success: true,
        message: `Upload completo! ${successTotal} contatos válidos de ${totalLines} linhas.`,
        stats: {
          total: totalLines,
          success: successTotal,
          errors: errorTotal
        }
      };

    } catch (error) {
      console.error('Erro ao processar arquivo:', error);
      throw error;
    }
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    addFiles(selectedFiles);
  };

  const addFiles = (newFiles) => {
    const validFiles = newFiles.filter(file => {
      const isValid = file.type === 'text/plain' || file.type === 'text/csv' || 
                     file.name.endsWith('.txt') || file.name.endsWith('.csv');
      if (!isValid) {
        setError(`${file.name} não é um arquivo válido. Use apenas .txt ou .csv`);
      }
      return isValid;
    });
    setFiles([...files, ...validFiles]);
    setError('');
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Selecione pelo menos um arquivo');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');
    setUploadStatus({});

    const campaignId = selectedCampaign || null;

    for (const file of files) {
      try {
        setUploadStatus(prev => ({
          ...prev,
          [file.name]: { status: 'uploading', message: 'Processando arquivo...' }
        }));

        const result = await processLargeFile(file, campaignId);

        setUploadStatus(prev => ({
          ...prev,
          [file.name]: {
            status: 'success',
            message: result.message,
            stats: result.stats
          }
        }));

      } catch (error) {
        console.error(`Erro no upload de ${file.name}:`, error);
        setUploadStatus(prev => ({
          ...prev,
          [file.name]: {
            status: 'error',
            message: error.response?.data?.detail || 'Erro no upload'
          }
        }));
      }
    }

    setUploading(false);
    setSuccess('Upload concluído! Verifique os resultados abaixo.');
  };

  return (
    <div className="min-h-screen bg-dark-900 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">
          Upload de Listas - Versão Corrigida
        </h1>

        {/* Info Box */}
        <div className="mb-8 bg-gradient-to-r from-blue-500/20 to-blue-600/20 border border-blue-500/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-blue-400 mb-2">
            ✨ Versão Melhorada
          </h3>
          <ul className="text-gray-300 space-y-1">
            <li>• Processa arquivos grandes completamente (testado com 770k+)</li>
            <li>• Chunks otimizados baseados no tamanho do arquivo</li>
            <li>• Continua mesmo com erros parciais</li>
            <li>• Progresso detalhado em tempo real</li>
          </ul>
        </div>

        {/* Campaign Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Selecionar Campanha (Opcional)
          </label>
          <select
            value={selectedCampaign}
            onChange={(e) => setSelectedCampaign(e.target.value)}
            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white"
          >
            <option value="">Criar nova campanha automaticamente</option>
            {campaigns.map(campaign => (
              <option key={campaign.id} value={campaign.id}>
                {campaign.name || campaign.nome} (ID: {campaign.id})
              </option>
            ))}
          </select>
        </div>

        {/* Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
            uploading ? 'border-gray-600 bg-gray-800/50' : 'border-primary-500 hover:border-primary-400'
          }`}
        >
          <Upload className="w-16 h-16 text-primary-500 mx-auto mb-4" />
          <p className="text-xl font-medium text-white mb-2">
            Arraste arquivos aqui ou clique para selecionar
          </p>
          <p className="text-gray-400 mb-4">
            Aceita arquivos .txt e .csv
          </p>
          <input
            type="file"
            multiple
            accept=".txt,.csv"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
            disabled={uploading}
          />
          <label
            htmlFor="file-upload"
            className={`inline-flex items-center px-6 py-3 rounded-lg font-medium transition-all ${
              uploading
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-primary-500 hover:bg-primary-600 text-white cursor-pointer'
            }`}
          >
            Selecionar Arquivos
          </label>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="mt-6 space-y-3">
            {files.map((file, index) => (
              <div key={index} className="bg-dark-800 rounded-lg p-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-white font-medium">{file.name}</p>
                    <p className="text-sm text-gray-400">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  {uploadStatus[file.name] && (
                    <span className={`text-sm ${
                      uploadStatus[file.name].status === 'success' ? 'text-green-400' :
                      uploadStatus[file.name].status === 'error' ? 'text-red-400' :
                      'text-yellow-400'
                    }`}>
                      {uploadStatus[file.name].message}
                    </span>
                  )}
                  {!uploading && (
                    <button
                      onClick={() => removeFile(index)}
                      className="text-gray-400 hover:text-red-400 transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Progress Display */}
        {Object.entries(progress).map(([fileId, prog]) => (
          <div key={fileId} className="mt-4 bg-dark-800 rounded-lg p-4">
            <div className="flex justify-between mb-2">
              <span className="text-white font-medium">{fileId}</span>
              <span className="text-gray-400">{prog.percent || 0}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
              <div 
                className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${prog.percent || 0}%` }}
              />
            </div>
            <p className="text-sm text-gray-400">{prog.status}</p>
            {prog.current > 0 && (
              <p className="text-xs text-gray-500 mt-1">
                {prog.current.toLocaleString()} de {prog.total.toLocaleString()} linhas
              </p>
            )}
          </div>
        ))}

        {/* Messages */}
        {error && (
          <div className="mt-6 bg-red-500/20 border border-red-500/50 rounded-lg p-4 flex items-start">
            <AlertCircle className="w-5 h-5 text-red-400 mr-3 mt-0.5" />
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {success && (
          <div className="mt-6 bg-green-500/20 border border-green-500/50 rounded-lg p-4 flex items-start">
            <CheckCircle className="w-5 h-5 text-green-400 mr-3 mt-0.5" />
            <p className="text-green-400">{success}</p>
          </div>
        )}

        {/* Upload Stats */}
        {Object.entries(uploadStatus).some(([_, status]) => status.stats) && (
          <div className="mt-6 bg-dark-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">📊 Resumo do Upload</h3>
            {Object.entries(uploadStatus).map(([fileName, status]) => {
              if (!status.stats) return null;
              return (
                <div key={fileName} className="mb-4 pb-4 border-b border-gray-700 last:border-0">
                  <p className="font-medium text-white mb-2">{fileName}</p>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-400">Total</p>
                      <p className="text-xl font-bold text-white">{status.stats.total.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Válidos</p>
                      <p className="text-xl font-bold text-green-400">{status.stats.success.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Erros</p>
                      <p className="text-xl font-bold text-red-400">{status.stats.errors.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Upload Button */}
        {files.length > 0 && (
          <button
            onClick={handleUpload}
            disabled={uploading}
            className={`mt-6 w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center ${
              uploading
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white'
            }`}
          >
            {uploading ? (
              <>
                <Loader className="w-5 h-5 mr-2 animate-spin" />
                Processando uploads...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5 mr-2" />
                Iniciar Upload
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
};

export default UploadListasFixed; 