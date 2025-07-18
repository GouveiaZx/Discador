import React, { useState, useEffect, useRef, useCallback } from 'react';
import { makeApiRequest } from '../config/api.js';
import { useCampaigns } from '../contexts/CampaignContext';

/**
 * Componente especializado para uploads masivos de hasta 700 millones de números
 * Interfaz completamente en español argentino
 */

const Icons = {
  Upload: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
    </svg>
  ),
  Database: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"/>
    </svg>
  ),
  Lightning: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
    </svg>
  ),
  Chart: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
    </svg>
  ),
  Warning: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z"/>
    </svg>
  ),
  Check: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"/>
    </svg>
  ),
  Clock: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </svg>
  )
};

// Estados del proceso de upload masivo
const UploadStates = {
  IDLE: 'idle',
  ANALYZING: 'analyzing',
  PREPARING: 'preparing',
  UPLOADING: 'uploading',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  ERROR: 'error',
  PAUSED: 'paused'
};

// Configuraciones para uploads masivos
const MASSIVE_CONFIG = {
  CHUNK_SIZE: 10000, // 10K números por chunk para archivos masivos
  MAX_CONCURRENT_CHUNKS: 3, // Máximo 3 chunks simultáneos
  RETRY_ATTEMPTS: 3,
  PAUSE_BETWEEN_CHUNKS: 2000, // 2 segundos entre chunks
  LARGE_FILE_THRESHOLD: 100 * 1024 * 1024, // 100MB
  MASSIVE_FILE_THRESHOLD: 1024 * 1024 * 1024, // 1GB
};

const MassiveUploadManager = () => {
  const { campaigns } = useCampaigns();
  const [selectedCampaign, setSelectedCampaign] = useState('');
  const [file, setFile] = useState(null);
  const [uploadState, setUploadState] = useState(UploadStates.IDLE);
  const [progress, setProgress] = useState({
    current: 0,
    total: 0,
    percentage: 0,
    chunksCompleted: 0,
    totalChunks: 0,
    currentChunk: 0,
    speed: 0,
    eta: 0
  });
  const [stats, setStats] = useState({
    totalNumbers: 0,
    validNumbers: 0,
    invalidNumbers: 0,
    duplicates: 0,
    processed: 0
  });
  const [error, setError] = useState(null);
  const [isPaused, setIsPaused] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  
  // Referencias para control del proceso
  const abortControllerRef = useRef(null);
  const startTimeRef = useRef(null);
  const fileInputRef = useRef(null);
  const chunksQueueRef = useRef([]);
  const processedChunksRef = useRef(0);

  // Efecto para seleccionar primera campaña disponible
  useEffect(() => {
    if (campaigns.length > 0 && !selectedCampaign) {
      setSelectedCampaign(campaigns[0].id.toString());
    }
  }, [campaigns, selectedCampaign]);

  // Función para analizar archivo
  const analyzeFile = useCallback(async (selectedFile) => {
    setUploadState(UploadStates.ANALYZING);
    setError(null);
    
    try {


      // Leer una muestra del archivo para análisis
      const sampleSize = Math.min(1024 * 1024, selectedFile.size); // 1MB de muestra
      const sampleBlob = selectedFile.slice(0, sampleSize);
      const sampleText = await sampleBlob.text();
      
      const lines = sampleText.split('\n').filter(line => line.trim());
      
      if (lines.length === 0) {
        throw new Error('El archivo está vacío o no contiene datos válidos');
      }

      // Detectar formato y separador
      const firstLine = lines[0];
      let separator = null;
      
      if (firstLine.includes('\t')) {
        separator = '\t';
      } else if (firstLine.includes(';')) {
        separator = ';';
      } else if (firstLine.includes(',')) {
        separator = ',';
      } else if (firstLine.includes('|')) {
        separator = '|';
      }

      // Estimar total de líneas basado en el tamaño del archivo
      const avgLineLength = sampleText.length / lines.length;
      const estimatedTotalLines = Math.floor(selectedFile.size / avgLineLength);
      
      // Validar algunos números de muestra
      const sampleNumbers = lines.slice(0, 100).map(line => {
        if (separator) {
          return line.split(separator)[0]?.trim();
        }
        return line.trim();
      }).filter(num => num && /^[+]?[0-9\s\-\(\)]+$/.test(num));

      const validationRate = sampleNumbers.length / Math.min(100, lines.length);
      


      setStats({
        totalNumbers: estimatedTotalLines,
        validNumbers: Math.floor(estimatedTotalLines * validationRate),
        invalidNumbers: Math.floor(estimatedTotalLines * (1 - validationRate)),
        duplicates: 0,
        processed: 0
      });

      setUploadState(UploadStates.PREPARING);
      
    } catch (err) {

      setError(`Error al analizar el archivo: ${err.message}`);
      setUploadState(UploadStates.ERROR);
    }
  }, []);

  // Función para manejar selección de archivo
  const handleFileSelect = useCallback((selectedFile) => {
    if (!selectedFile) return;

    // Validar tipo de archivo
    const allowedTypes = ['.txt', '.csv', '.tsv'];
    const fileExtension = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'));
    
    if (!allowedTypes.includes(fileExtension)) {
      setError('Formato no soportado. Use archivos TXT, CSV o TSV');
      return;
    }

    // Validar tamaño máximo (10GB)
    const maxSize = 10 * 1024 * 1024 * 1024; // 10GB
    if (selectedFile.size > maxSize) {
      setError('Archivo demasiado grande. Máximo permitido: 10GB');
      return;
    }

    setFile(selectedFile);
    analyzeFile(selectedFile);
  }, [analyzeFile]);

  // Función para procesar archivo en chunks
  const processFileInChunks = useCallback(async () => {
    if (!file || !selectedCampaign) return;

    setUploadState(UploadStates.UPLOADING);
    setIsPaused(false);
    startTimeRef.current = Date.now();
    abortControllerRef.current = new AbortController();
    
    try {

      
      const text = await file.text();
      const lines = text.split('\n').filter(line => line.trim());
      
      const chunkSize = file.size > MASSIVE_CONFIG.MASSIVE_FILE_THRESHOLD 
        ? MASSIVE_CONFIG.CHUNK_SIZE * 2 // Chunks más grandes para archivos gigantes
        : MASSIVE_CONFIG.CHUNK_SIZE;
      
      // Dividir en chunks
      const chunks = [];
      for (let i = 0; i < lines.length; i += chunkSize) {
        chunks.push(lines.slice(i, i + chunkSize));
      }
      
      chunksQueueRef.current = chunks;
      processedChunksRef.current = 0;
      
      setProgress(prev => ({
        ...prev,
        total: lines.length,
        totalChunks: chunks.length,
        current: 0,
        chunksCompleted: 0
      }));
      

      
      // Procesar chunks con control de concurrencia
      await processChunksWithConcurrency(chunks);
      
    } catch (err) {
      if (err.name === 'AbortError') {

        setUploadState(UploadStates.PAUSED);
      } else {

        setError(`Error en el procesamiento: ${err.message}`);
        setUploadState(UploadStates.ERROR);
      }
    }
  }, [file, selectedCampaign]);

  // Función para procesar chunks con concurrencia controlada
  const processChunksWithConcurrency = async (chunks) => {
    const semaphore = new Array(MASSIVE_CONFIG.MAX_CONCURRENT_CHUNKS).fill(null);
    let chunkIndex = 0;
    let totalProcessed = 0;
    let totalErrors = 0;
    let totalDuplicates = 0;
    
    const processChunk = async (chunk, index) => {
      const chunkNumber = index + 1;
      
      try {

        
        const chunkContent = chunk.join('\n');
        const chunkBlob = new Blob([chunkContent], { type: 'text/plain' });
        const chunkFile = new File([chunkBlob], `chunk_${chunkNumber}_${file.name}`, { type: 'text/plain' });
        
        const formData = new FormData();
        formData.append('arquivo', chunkFile);
        formData.append('incluir_nome', 'true');
        formData.append('pais_preferido', 'auto');
        formData.append('campaign_id', selectedCampaign);
        formData.append('chunk_info', JSON.stringify({
          chunkNumber,
          totalChunks: chunks.length,
          isLastChunk: chunkNumber === chunks.length
        }));
        
        const response = await makeApiRequest('/contacts/upload', 'POST', formData, {
          signal: abortControllerRef.current?.signal
        });
        
        const processed = response.contatos_validos || 0;
        const errors = response.contatos_invalidos || 0;
        const duplicates = response.contatos_duplicados || 0;
        
        totalProcessed += processed;
        totalErrors += errors;
        totalDuplicates += duplicates;
        processedChunksRef.current++;
        
        // Actualizar progreso
        const currentProgress = totalProcessed + totalErrors;
        const percentage = Math.round((currentProgress / stats.totalNumbers) * 100);
        const elapsed = Date.now() - startTimeRef.current;
        const speed = currentProgress / (elapsed / 1000); // números por segundo
        const eta = speed > 0 ? (stats.totalNumbers - currentProgress) / speed : 0;
        
        setProgress({
          current: currentProgress,
          total: stats.totalNumbers,
          percentage,
          chunksCompleted: processedChunksRef.current,
          totalChunks: chunks.length,
          currentChunk: chunkNumber,
          speed: Math.round(speed),
          eta: Math.round(eta)
        });
        
        setStats(prev => ({
          ...prev,
          processed: totalProcessed,
          invalidNumbers: totalErrors,
          duplicates: totalDuplicates
        }));
        

        
        // Pausa entre chunks para no sobrecargar el servidor
        if (chunkNumber < chunks.length) {
          await new Promise(resolve => setTimeout(resolve, MASSIVE_CONFIG.PAUSE_BETWEEN_CHUNKS));
        }
        
      } catch (error) {

        totalErrors += chunk.length;
        throw error;
      }
    };
    
    // Procesar chunks con semáforo para controlar concurrencia
    const promises = [];
    
    for (let i = 0; i < chunks.length; i++) {
      if (isPaused || abortControllerRef.current?.signal.aborted) {
        break;
      }
      
      const promise = processChunk(chunks[i], i);
      promises.push(promise);
      
      // Limitar concurrencia
      if (promises.length >= MASSIVE_CONFIG.MAX_CONCURRENT_CHUNKS) {
        await Promise.race(promises);
        // Remover promesas completadas
        for (let j = promises.length - 1; j >= 0; j--) {
          if (await Promise.race([promises[j], Promise.resolve('pending')]) !== 'pending') {
            promises.splice(j, 1);
          }
        }
      }
    }
    
    // Esperar a que terminen todas las promesas restantes
    await Promise.all(promises);
    

    
    setUploadState(UploadStates.COMPLETED);
  };

  // Función para pausar/reanudar
  const togglePause = () => {
    if (uploadState === UploadStates.UPLOADING) {
      setIsPaused(true);
      setUploadState(UploadStates.PAUSED);
      abortControllerRef.current?.abort();
    } else if (uploadState === UploadStates.PAUSED) {
      processFileInChunks();
    }
  };

  // Función para cancelar
  const cancelUpload = () => {
    abortControllerRef.current?.abort();
    setUploadState(UploadStates.IDLE);
    setFile(null);
    setProgress({
      current: 0,
      total: 0,
      percentage: 0,
      chunksCompleted: 0,
      totalChunks: 0,
      currentChunk: 0,
      speed: 0,
      eta: 0
    });
    setStats({
      totalNumbers: 0,
      validNumbers: 0,
      invalidNumbers: 0,
      duplicates: 0,
      processed: 0
    });
    setError(null);
  };

  // Función para reiniciar
  const resetUpload = () => {
    cancelUpload();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handlers para drag & drop
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

  // Función para formatear tiempo
  const formatTime = (seconds) => {
    if (!seconds || seconds === Infinity) return '--';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  // Función para formatear números
  const formatNumber = (num) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4 bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
            Carga Masiva de Números
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Sistema optimizado para cargar hasta 700 millones de números telefónicos
          </p>
        </div>

        {/* Selección de Campaña */}
        <div className="mb-8">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Seleccionar Campaña</h3>
            <select
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={uploadState === UploadStates.UPLOADING}
            >
              <option value="">Seleccionar campaña...</option>
              {campaigns.map(campaign => (
                <option key={campaign.id} value={campaign.id}>
                  {campaign.nombre || campaign.name || `Campaña ${campaign.id}`}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Área de Upload */}
        {uploadState === UploadStates.IDLE && (
          <div className="mb-8">
            <div 
              className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
                dragOver 
                  ? 'border-primary-400 bg-primary-500/10' 
                  : 'border-gray-600 hover:border-gray-500'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <Icons.Upload />
              <h3 className="text-2xl font-semibold text-white mb-4">Arrastrá tu archivo acá</h3>
              <p className="text-gray-400 mb-6">
                o hacé clic para seleccionar un archivo TXT, CSV o TSV
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.csv,.tsv"
                onChange={(e) => handleFileSelect(e.target.files[0])}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                disabled={!selectedCampaign}
              >
                Seleccionar Archivo
              </button>
              {!selectedCampaign && (
                <p className="text-yellow-400 mt-4 text-sm">
                  ⚠️ Primero seleccioná una campaña
                </p>
              )}
            </div>
          </div>
        )}

        {/* Análisis del Archivo */}
        {uploadState === UploadStates.ANALYZING && (
          <div className="mb-8">
            <div className="bg-blue-500/20 border border-blue-500/50 rounded-xl p-6">
              <div className="flex items-center justify-center mb-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mr-3"></div>
                <h3 className="text-xl font-semibold text-white">Analizando archivo...</h3>
              </div>
              <p className="text-center text-gray-300">
                Detectando formato y estimando cantidad de números
              </p>
            </div>
          </div>
        )}

        {/* Preparación para Upload */}
        {uploadState === UploadStates.PREPARING && file && (
          <div className="mb-8">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-xl font-semibold text-white mb-6">Archivo Analizado</h3>
              
              {/* Info del archivo */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-700/50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Icons.Database />
                    <span className="ml-2 text-sm text-gray-400">Total Estimado</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{formatNumber(stats.totalNumbers)}</p>
                </div>
                
                <div className="bg-green-500/20 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Icons.Check />
                    <span className="ml-2 text-sm text-gray-400">Números Válidos</span>
                  </div>
                  <p className="text-2xl font-bold text-green-400">{formatNumber(stats.validNumbers)}</p>
                </div>
                
                <div className="bg-red-500/20 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Icons.Warning />
                    <span className="ml-2 text-sm text-gray-400">Inválidos</span>
                  </div>
                  <p className="text-2xl font-bold text-red-400">{formatNumber(stats.invalidNumbers)}</p>
                </div>
                
                <div className="bg-gray-600/50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Icons.Chart />
                    <span className="ml-2 text-sm text-gray-400">Tamaño</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                </div>
              </div>
              
              {/* Botones de acción */}
              <div className="flex gap-4">
                <button
                  onClick={processFileInChunks}
                  className="flex-1 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors flex items-center justify-center"
                >
                  <Icons.Lightning />
                  <span className="ml-2">Iniciar Carga Masiva</span>
                </button>
                
                <button
                  onClick={resetUpload}
                  className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                >
                  Cancelar
                </button>
              </div>
              
              {/* Advertencia para archivos muy grandes */}
              {file.size > MASSIVE_CONFIG.MASSIVE_FILE_THRESHOLD && (
                <div className="mt-4 p-4 bg-yellow-500/20 border border-yellow-500/50 rounded-lg">
                  <div className="flex items-center">
                    <Icons.Warning />
                    <span className="ml-2 text-yellow-400 font-semibold">Archivo Muy Grande Detectado</span>
                  </div>
                  <p className="text-yellow-300 mt-2 text-sm">
                    Este archivo será procesado en chunks más grandes para optimizar el rendimiento. 
                    El proceso puede tomar varias horas dependiendo del tamaño.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Progreso de Upload */}
        {(uploadState === UploadStates.UPLOADING || uploadState === UploadStates.PAUSED) && (
          <div className="mb-8">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">
                  {uploadState === UploadStates.PAUSED ? 'Carga Pausada' : 'Cargando Números...'}
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={togglePause}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      uploadState === UploadStates.PAUSED
                        ? 'bg-green-600 hover:bg-green-700'
                        : 'bg-yellow-600 hover:bg-yellow-700'
                    } text-white`}
                  >
                    {uploadState === UploadStates.PAUSED ? 'Reanudar' : 'Pausar'}
                  </button>
                  <button
                    onClick={cancelUpload}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
              
              {/* Barra de progreso principal */}
              <div className="mb-6">
                <div className="flex justify-between text-sm text-gray-400 mb-2">
                  <span>Progreso General</span>
                  <span>{progress.percentage}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${progress.percentage}%` }}
                  ></div>
                </div>
              </div>
              
              {/* Estadísticas en tiempo real */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-white">{formatNumber(progress.current)}</p>
                  <p className="text-sm text-gray-400">Procesados</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary-400">{progress.chunksCompleted}</p>
                  <p className="text-sm text-gray-400">Chunks Completados</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-400">{formatNumber(progress.speed)}</p>
                  <p className="text-sm text-gray-400">Números/seg</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-400">{formatTime(progress.eta)}</p>
                  <p className="text-sm text-gray-400">Tiempo Restante</p>
                </div>
              </div>
              
              {/* Progreso de chunks */}
              <div className="text-center text-gray-400">
                <p>Chunk {progress.currentChunk} de {progress.totalChunks}</p>
              </div>
            </div>
          </div>
        )}

        {/* Resultado Final */}
        {uploadState === UploadStates.COMPLETED && (
          <div className="mb-8">
            <div className="bg-green-500/20 border border-green-500/50 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-semibold text-white">¡Carga Completada!</h3>
                <button
                  onClick={resetUpload}
                  className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                >
                  Cargar Otro Archivo
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gray-800/50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-white">{formatNumber(stats.processed)}</p>
                  <p className="text-green-400">Números Cargados</p>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-red-400">{formatNumber(stats.invalidNumbers)}</p>
                  <p className="text-gray-400">Inválidos</p>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-yellow-400">{formatNumber(stats.duplicates)}</p>
                  <p className="text-gray-400">Duplicados</p>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-primary-400">{progress.totalChunks}</p>
                  <p className="text-gray-400">Chunks Procesados</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-8">
            <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-6">
              <div className="flex items-center mb-4">
                <Icons.Warning />
                <h3 className="text-xl font-semibold text-white ml-2">Error</h3>
              </div>
              <p className="text-red-300 mb-4">{error}</p>
              <button
                onClick={resetUpload}
                className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Reintentar
              </button>
            </div>
          </div>
        )}

        {/* Información del Sistema */}
        <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Información del Sistema</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-400">Tamaño máximo de archivo:</p>
              <p className="text-white font-semibold">10 GB</p>
            </div>
            <div>
              <p className="text-gray-400">Números por chunk:</p>
              <p className="text-white font-semibold">{MASSIVE_CONFIG.CHUNK_SIZE.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-gray-400">Chunks simultáneos:</p>
              <p className="text-white font-semibold">{MASSIVE_CONFIG.MAX_CONCURRENT_CHUNKS}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MassiveUploadManager;