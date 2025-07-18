import React, { useState, useEffect, useRef, useCallback } from 'react';
import { makeApiRequest } from '../config/api.js';
import { useCampaigns } from '../contexts/CampaignContext';

/**
 * Componente especializado para gestión masiva de audios
 * Interfaz completamente en español argentino
 */

const Icons = {
  Upload: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
    </svg>
  ),
  Audio: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 14.142M9 9a3 3 0 000 6h6a3 3 0 000-6H9z"/>
    </svg>
  ),
  Play: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15M9 10v4a2 2 0 002 2h2a2 2 0 002-2v-4M9 10V9a2 2 0 012-2h2a2 2 0 012 2v1"/>
    </svg>
  ),
  Stop: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>
    </svg>
  ),
  Delete: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
    </svg>
  ),
  Download: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
    </svg>
  ),
  Refresh: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
    </svg>
  ),
  Microphone: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
    </svg>
  ),
  Waveform: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19V6l2-2 2 2v13M9 19l-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2h2l2-2M9 19h10a2 2 0 002-2V9a2 2 0 00-2-2h-2l-2 2"/>
    </svg>
  ),
  Check: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"/>
    </svg>
  ),
  Warning: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z"/>
    </svg>
  )
};

// Estados del proceso de audio
const AudioStates = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  ERROR: 'error',
  PLAYING: 'playing'
};

// Configuraciones para audios
const AUDIO_CONFIG = {
  MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB por archivo
  MAX_BATCH_SIZE: 20, // Máximo 20 archivos por lote
  SUPPORTED_FORMATS: ['.mp3', '.wav', '.ogg', '.m4a', '.aac'],
  CHUNK_SIZE: 1024 * 1024, // 1MB chunks para upload
  QUALITY_PRESETS: {
    'alta': { bitrate: 128, sampleRate: 44100 },
    'media': { bitrate: 96, sampleRate: 22050 },
    'baja': { bitrate: 64, sampleRate: 16000 }
  }
};

const MassiveAudioManager = () => {
  const { campaigns } = useCampaigns();
  const [selectedCampaign, setSelectedCampaign] = useState('');
  const [audioFiles, setAudioFiles] = useState([]);
  const [uploadState, setUploadState] = useState(AudioStates.IDLE);
  const [uploadProgress, setUploadProgress] = useState({});
  const [audioList, setAudioList] = useState([]);
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [qualityPreset, setQualityPreset] = useState('media');
  const [isLoading, setIsLoading] = useState(false);
  
  // Referencias
  const fileInputRef = useRef(null);
  const audioRefs = useRef({});
  const abortControllerRef = useRef(null);

  // Efecto para cargar lista de audios
  useEffect(() => {
    loadAudioList();
  }, []);

  // Efecto para seleccionar primera campaña
  useEffect(() => {
    if (campaigns.length > 0 && !selectedCampaign) {
      setSelectedCampaign(campaigns[0].id.toString());
    }
  }, [campaigns, selectedCampaign]);

  // Función para cargar lista de audios
  const loadAudioList = async () => {
    setIsLoading(true);
    try {
      const response = await makeApiRequest('/audio/list', 'GET');
      setAudioList(response.audios || []);
    } catch (err) {
      setError('Error al cargar la lista de audios');
    } finally {
      setIsLoading(false);
    }
  };

  // Función para validar archivos de audio
  const validateAudioFiles = (files) => {
    const validFiles = [];
    const errors = [];

    Array.from(files).forEach((file, index) => {
      // Validar formato
      const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      if (!AUDIO_CONFIG.SUPPORTED_FORMATS.includes(extension)) {
        errors.push(`${file.name}: Formato no soportado. Use ${AUDIO_CONFIG.SUPPORTED_FORMATS.join(', ')}`);
        return;
      }

      // Validar tamaño
      if (file.size > AUDIO_CONFIG.MAX_FILE_SIZE) {
        errors.push(`${file.name}: Archivo muy grande. Máximo ${AUDIO_CONFIG.MAX_FILE_SIZE / 1024 / 1024}MB`);
        return;
      }

      // Validar nombre
      if (!/^[a-zA-Z0-9_\-\s\.]+$/.test(file.name)) {
        errors.push(`${file.name}: Nombre contiene caracteres no válidos`);
        return;
      }

      validFiles.push({
        file,
        id: `${Date.now()}_${index}`,
        name: file.name,
        size: file.size,
        status: 'pending',
        progress: 0,
        error: null
      });
    });

    // Validar cantidad total
    if (validFiles.length > AUDIO_CONFIG.MAX_BATCH_SIZE) {
      errors.push(`Máximo ${AUDIO_CONFIG.MAX_BATCH_SIZE} archivos por lote`);
      return { validFiles: [], errors };
    }

    return { validFiles, errors };
  };

  // Función para manejar selección de archivos
  const handleFileSelect = (files) => {
    if (!files || files.length === 0) return;

    const { validFiles, errors } = validateAudioFiles(files);

    if (errors.length > 0) {
      setError(errors.join('\n'));
      return;
    }

    setAudioFiles(validFiles);
    setError(null);
    

  };

  // Función para subir un archivo individual
  const uploadSingleAudio = async (audioFile) => {
    const { file, id } = audioFile;
    
    try {

      
      // Actualizar estado del archivo
      setAudioFiles(prev => prev.map(af => 
        af.id === id ? { ...af, status: 'uploading', progress: 0 } : af
      ));

      const formData = new FormData();
      formData.append('audio', file);
      formData.append('name', file.name.replace(/\.[^/.]+$/, '')); // Sin extensión
      formData.append('quality', qualityPreset);
      formData.append('campaign_id', selectedCampaign);
      
      // Configurar progreso
      const onUploadProgress = (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setAudioFiles(prev => prev.map(af => 
          af.id === id ? { ...af, progress } : af
        ));
      };

      const response = await makeApiRequest('/audio/upload', 'POST', formData, {
        signal: abortControllerRef.current?.signal,
        onUploadProgress
      });

      // Marcar como completado
      setAudioFiles(prev => prev.map(af => 
        af.id === id ? { 
          ...af, 
          status: 'completed', 
          progress: 100,
          audioId: response.audio_id,
          url: response.audio_url
        } : af
      ));


      return response;
      
    } catch (err) {

      
      setAudioFiles(prev => prev.map(af => 
        af.id === id ? { 
          ...af, 
          status: 'error', 
          error: err.message || 'Error desconocido'
        } : af
      ));
      
      throw err;
    }
  };

  // Función para subir todos los archivos
  const uploadAllAudios = async () => {
    if (!selectedCampaign) {
      setError('Seleccioná una campaña primero');
      return;
    }

    if (audioFiles.length === 0) {
      setError('No hay archivos para subir');
      return;
    }

    setUploadState(AudioStates.UPLOADING);
    setError(null);
    abortControllerRef.current = new AbortController();
    
    let successCount = 0;
    let errorCount = 0;
    
    try {

      
      // Subir archivos secuencialmente para evitar sobrecarga
      for (const audioFile of audioFiles) {
        if (abortControllerRef.current?.signal.aborted) {
          break;
        }
        
        try {
          await uploadSingleAudio(audioFile);
          successCount++;
          
          // Pausa pequeña entre uploads
          await new Promise(resolve => setTimeout(resolve, 500));
          
        } catch (err) {
          errorCount++;
        }
      }
      
      // Recargar lista de audios
      await loadAudioList();
      
      if (successCount > 0) {
        setSuccess(`${successCount} archivo${successCount > 1 ? 's' : ''} subido${successCount > 1 ? 's' : ''} exitosamente`);
      }
      
      if (errorCount > 0) {
        setError(`${errorCount} archivo${errorCount > 1 ? 's' : ''} fallaron al subir`);
      }
      
      setUploadState(AudioStates.COMPLETED);
      
    } catch (err) {
      setError(`Error en la subida: ${err.message}`);
      setUploadState(AudioStates.ERROR);
    }
  };

  // Función para cancelar subida
  const cancelUpload = () => {
    abortControllerRef.current?.abort();
    setUploadState(AudioStates.IDLE);
    setAudioFiles([]);
    setError(null);
  };

  // Función para reproducir audio
  const playAudio = (audioId, url) => {
    // Parar audio actual si existe
    if (currentlyPlaying && audioRefs.current[currentlyPlaying]) {
      audioRefs.current[currentlyPlaying].pause();
      audioRefs.current[currentlyPlaying].currentTime = 0;
    }

    if (currentlyPlaying === audioId) {
      setCurrentlyPlaying(null);
      return;
    }

    // Crear o usar elemento de audio existente
    if (!audioRefs.current[audioId]) {
      audioRefs.current[audioId] = new Audio(url);
      audioRefs.current[audioId].addEventListener('ended', () => {
        setCurrentlyPlaying(null);
      });
    }

    audioRefs.current[audioId].play();
    setCurrentlyPlaying(audioId);
  };

  // Función para parar audio
  const stopAudio = () => {
    if (currentlyPlaying && audioRefs.current[currentlyPlaying]) {
      audioRefs.current[currentlyPlaying].pause();
      audioRefs.current[currentlyPlaying].currentTime = 0;
    }
    setCurrentlyPlaying(null);
  };

  // Función para eliminar audio
  const deleteAudio = async (audioId, audioName) => {
    if (!confirm(`¿Estás seguro de que querés eliminar "${audioName}"?`)) {
      return;
    }

    try {
      await makeApiRequest(`/audio/${audioId}`, 'DELETE');
      setSuccess(`Audio "${audioName}" eliminado exitosamente`);
      await loadAudioList();
    } catch (err) {
      setError(`Error al eliminar el audio: ${err.message}`);
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
    
    if (e.dataTransfer.files) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  // Función para formatear tamaño
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Función para formatear duración
  const formatDuration = (seconds) => {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4 bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">
            Gestión de Audios
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Subí y gestioná tus archivos de audio para las campañas de discado
          </p>
        </div>

        {/* Selección de Campaña y Calidad */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Seleccionar Campaña</h3>
            <select
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={uploadState === AudioStates.UPLOADING}
            >
              <option value="">Seleccionar campaña...</option>
              {campaigns.map(campaign => (
                <option key={campaign.id} value={campaign.id}>
                  {campaign.nombre || campaign.name || `Campaña ${campaign.id}`}
                </option>
              ))}
            </select>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Calidad de Audio</h3>
            <select
              value={qualityPreset}
              onChange={(e) => setQualityPreset(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={uploadState === AudioStates.UPLOADING}
            >
              <option value="alta">Alta Calidad (128 kbps)</option>
              <option value="media">Calidad Media (96 kbps)</option>
              <option value="baja">Calidad Básica (64 kbps)</option>
            </select>
          </div>
        </div>

        {/* Área de Upload */}
        {uploadState === AudioStates.IDLE && (
          <div className="mb-8">
            <div 
              className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
                dragOver 
                  ? 'border-purple-400 bg-purple-500/10' 
                  : 'border-gray-600 hover:border-gray-500'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <Icons.Audio />
              <h3 className="text-2xl font-semibold text-white mb-4">Arrastrá tus archivos de audio acá</h3>
              <p className="text-gray-400 mb-6">
                o hacé clic para seleccionar archivos MP3, WAV, OGG, M4A o AAC
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".mp3,.wav,.ogg,.m4a,.aac"
                multiple
                onChange={(e) => handleFileSelect(e.target.files)}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                disabled={!selectedCampaign}
              >
                Seleccionar Archivos
              </button>
              {!selectedCampaign && (
                <p className="text-yellow-400 mt-4 text-sm">
                  ⚠️ Primero seleccioná una campaña
                </p>
              )}
              
              {/* Información de formatos soportados */}
              <div className="mt-6 text-sm text-gray-400">
                <p className="mb-2">Formatos soportados: MP3, WAV, OGG, M4A, AAC</p>
                <p className="mb-2">Tamaño máximo por archivo: 50 MB</p>
                <p>Máximo {AUDIO_CONFIG.MAX_BATCH_SIZE} archivos por lote</p>
              </div>
            </div>
          </div>
        )}

        {/* Lista de archivos seleccionados */}
        {audioFiles.length > 0 && (
          <div className="mb-8">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">
                  Archivos Seleccionados ({audioFiles.length})
                </h3>
                <div className="flex gap-2">
                  {uploadState === AudioStates.IDLE && (
                    <>
                      <button
                        onClick={uploadAllAudios}
                        className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors flex items-center"
                      >
                        <Icons.Upload />
                        <span className="ml-2">Subir Todos</span>
                      </button>
                      <button
                        onClick={() => setAudioFiles([])}
                        className="px-4 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                      >
                        Limpiar
                      </button>
                    </>
                  )}
                  {uploadState === AudioStates.UPLOADING && (
                    <button
                      onClick={cancelUpload}
                      className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                    >
                      Cancelar
                    </button>
                  )}
                </div>
              </div>
              
              <div className="space-y-3">
                {audioFiles.map((audioFile) => (
                  <div key={audioFile.id} className="bg-gray-700/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <Icons.Audio />
                        <div className="ml-3">
                          <p className="text-white font-medium">{audioFile.name}</p>
                          <p className="text-gray-400 text-sm">{formatFileSize(audioFile.size)}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center">
                        {audioFile.status === 'pending' && (
                          <span className="text-gray-400">Pendiente</span>
                        )}
                        {audioFile.status === 'uploading' && (
                          <div className="flex items-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-400 mr-2"></div>
                            <span className="text-purple-400">{audioFile.progress}%</span>
                          </div>
                        )}
                        {audioFile.status === 'completed' && (
                          <div className="flex items-center text-green-400">
                            <Icons.Check />
                            <span className="ml-1">Completado</span>
                          </div>
                        )}
                        {audioFile.status === 'error' && (
                          <div className="flex items-center text-red-400">
                            <Icons.Warning />
                            <span className="ml-1">Error</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {audioFile.status === 'uploading' && (
                      <div className="w-full bg-gray-600 rounded-full h-2">
                        <div 
                          className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${audioFile.progress}%` }}
                        ></div>
                      </div>
                    )}
                    
                    {audioFile.error && (
                      <p className="text-red-400 text-sm mt-2">{audioFile.error}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Lista de audios existentes */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-white">Audios Disponibles</h3>
            <button
              onClick={loadAudioList}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors flex items-center"
              disabled={isLoading}
            >
              <Icons.Refresh />
              <span className="ml-2">Actualizar</span>
            </button>
          </div>
          
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400 mx-auto mb-4"></div>
              <p className="text-gray-400">Cargando audios...</p>
            </div>
          ) : audioList.length === 0 ? (
            <div className="text-center py-8">
              <Icons.Audio />
              <p className="text-gray-400 mt-4">No hay audios disponibles</p>
              <p className="text-gray-500 text-sm">Subí tu primer archivo de audio para comenzar</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {audioList.map((audio) => (
                <div key={audio.id} className="bg-gray-700/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <Icons.Waveform />
                      <div className="ml-3">
                        <p className="text-white font-medium truncate">{audio.name}</p>
                        <p className="text-gray-400 text-sm">
                          {formatFileSize(audio.size)} • {formatDuration(audio.duration)}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex gap-2">
                      <button
                        onClick={() => currentlyPlaying === audio.id ? stopAudio() : playAudio(audio.id, audio.url)}
                        className={`p-2 rounded-lg transition-colors ${
                          currentlyPlaying === audio.id
                            ? 'bg-red-600 hover:bg-red-700'
                            : 'bg-green-600 hover:bg-green-700'
                        } text-white`}
                      >
                        {currentlyPlaying === audio.id ? <Icons.Stop /> : <Icons.Play />}
                      </button>
                      
                      <a
                        href={audio.url}
                        download={audio.name}
                        className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                      >
                        <Icons.Download />
                      </a>
                    </div>
                    
                    <button
                      onClick={() => deleteAudio(audio.id, audio.name)}
                      className="p-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                    >
                      <Icons.Delete />
                    </button>
                  </div>
                  
                  {audio.campaign_name && (
                    <p className="text-gray-400 text-xs mt-2">
                      Campaña: {audio.campaign_name}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Mensajes de estado */}
        {error && (
          <div className="mt-6 bg-red-500/20 border border-red-500/50 rounded-xl p-4">
            <div className="flex items-center">
              <Icons.Warning />
              <span className="ml-2 text-red-300 font-semibold">Error</span>
            </div>
            <p className="text-red-300 mt-2 whitespace-pre-line">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-3 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-sm"
            >
              Cerrar
            </button>
          </div>
        )}

        {success && (
          <div className="mt-6 bg-green-500/20 border border-green-500/50 rounded-xl p-4">
            <div className="flex items-center">
              <Icons.Check />
              <span className="ml-2 text-green-300 font-semibold">Éxito</span>
            </div>
            <p className="text-green-300 mt-2">{success}</p>
            <button
              onClick={() => setSuccess(null)}
              className="mt-3 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors text-sm"
            >
              Cerrar
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MassiveAudioManager;