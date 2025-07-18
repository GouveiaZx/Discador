import React, { useState, useEffect, useRef } from 'react';
import { API_BASE_URL } from '../config/api';
import { useCampaigns } from '../contexts/CampaignContext';

// Ícones usando SVG simples (consistente con el resto del proyecto)
const Icons = {
  Upload: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
    </svg>
  ),
  Play: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15M9 10v4a2 2 0 002 2h2a2 2 0 002-2v-4M9 10V9a2 2 0 012-2h2a2 2 0 012 2v1"/>
    </svg>
  ),
  Stop: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>
    </svg>
  ),
  Delete: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
    </svg>
  ),
  Download: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
    </svg>
  ),
  AudioFile: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
    </svg>
  ),
  Refresh: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
    </svg>
  ),
  Close: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
    </svg>
  )
};

const makeApiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}/api/v1${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  // API Request

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    // API Success
    return data;
  } catch (error) {
    // API Error
    throw error;
  }
};

const AudioManager = () => {
  const { campaigns } = useCampaigns();
  const [audioFiles, setAudioFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
  const [openUploadDialog, setOpenUploadDialog] = useState(false);
  const [openStatsDialog, setOpenStatsDialog] = useState(false);
  const [stats, setStats] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Upload form state
  const [uploadForm, setUploadForm] = useState({
    file: null,
    name: '',
    description: '',
    campaign_id: '',
    audio_type: 'greeting'
  });

  const audioRef = useRef(null);

  useEffect(() => {
    loadAudioFiles();
  }, []);

  const loadAudioFiles = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/audio/list');
      setAudioFiles(response.files || response || []);
    } catch (error) {
              setError('Error al cargar archivos de audio');
    } finally {
      setLoading(false);
    }
  };



  const loadStats = async () => {
    try {
      const response = await makeApiRequest('/audio/stats');
      setStats(response.data || response || {});
    } catch (error) {
      // Error loading stats
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validar formato
      const allowedFormats = ['audio/wav', 'audio/mp3', 'audio/m4a', 'audio/aac', 'audio/flac'];
      if (!allowedFormats.includes(file.type)) {
        setError('Formato no soportado. Use: WAV, MP3, M4A, AAC, FLAC');
        return;
      }

      // Validar tamanho (50MB)
      if (file.size > 50 * 1024 * 1024) {
        setError('Archivo muy grande. Máximo: 50MB');
        return;
      }

      setUploadForm({
        ...uploadForm,
        file: file,
        name: uploadForm.name || file.name.split('.')[0]
      });
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!uploadForm.file) {
      setError('Seleccione un archivo');
      return;
    }

    try {
      setLoading(true);
      setUploadProgress(0);
      
      const formData = new FormData();
      formData.append('file', uploadForm.file);
      formData.append('name', uploadForm.name);
      formData.append('description', uploadForm.description);
      formData.append('campaign_id', uploadForm.campaign_id);
      formData.append('audio_type', uploadForm.audio_type);

      const response = await fetch(`${API_BASE_URL}/api/v1/audio/upload`, {
        method: 'POST',
        body: formData,
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });

      const data = await response.json();

      if (data.success) {
        setSuccess('¡Archivo enviado con éxito!');
        setOpenUploadDialog(false);
        setUploadForm({
          file: null,
          name: '',
          description: '',
          campaign_id: '',
          audio_type: 'greeting'
        });
        loadAudioFiles();
      } else {
        setError(data.message || 'Error al enviar archivo');
      }

    } catch (error) {
      setError(error.message || 'Error al enviar archivo');
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const handlePlay = async (audioFile) => {
    try {
      if (currentlyPlaying === audioFile.filename) {
        // Parar reprodução
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
        }
        setCurrentlyPlaying(null);
      } else {
        // Tocar áudio
      if (audioRef.current) {
          audioRef.current.src = audioFile.url || `/api/v1/audio/play/${audioFile.filename}`;
          await audioRef.current.play();
        setCurrentlyPlaying(audioFile.filename);
        }
      }
    } catch (error) {
              setError('Error al reproducir audio');
    }
  };

  const handleDelete = async (audioFile) => {
    if (!confirm(`¿Está seguro de eliminar "${audioFile.name}"?`)) {
      return;
    }

    try {
      const response = await makeApiRequest(`/audio/delete/${audioFile.id}`, {
        method: 'DELETE'
      });
      
      setSuccess('Archivo eliminado correctamente');
      loadAudioFiles();
    } catch (error) {
              setError('Error al eliminar archivo');
    }
  };

  const handleDownload = async (audioFile) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/audio/download/${audioFile.filename}`);
      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = audioFile.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
              setError('Error al descargar archivo');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getAudioTypeColor = (type) => {
    const colors = {
      greeting: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      voicemail: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      hold: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      dtmf: 'bg-green-500/20 text-green-400 border-green-500/30',
      transfer: 'bg-red-500/20 text-red-400 border-red-500/30'
    };
    return colors[type] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const showMessage = (type, text) => {
    if (type === 'success') {
      setSuccess(text);
      setError('');
    } else {
      setError(text);
      setSuccess('');
    }
    setTimeout(() => {
      setSuccess('');
      setError('');
    }, 5000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white mb-4">🎵 Gestión de Audios</h2>
          <p className="text-gray-400">Gestione archivos de audio para campañas y sistema de discado</p>
        </div>

        {/* Mensajes */}
      {error && (
          <div className="p-4 rounded-lg border bg-red-500/10 border-red-500/30 text-red-400">
            <div className="flex items-center">
              <span className="mr-2">❌</span>
          {error}
            </div>
          </div>
      )}
      
      {success && (
          <div className="p-4 rounded-lg border bg-green-500/10 border-green-500/30 text-green-400">
            <div className="flex items-center">
              <span className="mr-2">✅</span>
          {success}
            </div>
          </div>
      )}

        {/* Barra de Ações */}
        <div className="bg-gray-800/40 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
          <div className="flex flex-wrap gap-4 justify-between items-center">
            <div className="flex gap-4">
              <button
                onClick={() => setOpenUploadDialog(true)}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 flex items-center space-x-2"
              >
                <Icons.Upload />
                <span>Enviar Audio</span>
              </button>
              
              <button
                onClick={() => { loadStats(); setOpenStatsDialog(true); }}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors duration-200 flex items-center space-x-2"
              >
                <Icons.AudioFile />
                <span>Estadísticas</span>
              </button>
            </div>

            <button
              onClick={loadAudioFiles}
              disabled={loading}
              className="px-4 py-3 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors duration-200 flex items-center space-x-2"
            >
              <Icons.Refresh />
              <span>Actualizar</span>
            </button>
          </div>
        </div>

        {/* Lista de Archivos */}
        <div className="bg-gray-800/40 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
            <Icons.AudioFile />
            <span className="ml-2">Archivos de Audio ({audioFiles.length})</span>
          </h3>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-400">Cargando archivos...</p>
            </div>
          ) : audioFiles.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Icons.AudioFile />
              <p className="mt-4">No hay archivos de audio</p>
              <p className="text-sm">Suba el primer archivo de audio</p>
            </div>
        ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {audioFiles.map((audio, index) => (
                <div key={index} className="bg-gray-700/30 border border-gray-600/30 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-white font-medium truncate">{audio.name || audio.filename}</h4>
                      <p className="text-gray-400 text-sm truncate">{audio.description}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium border ${getAudioTypeColor(audio.audio_type)}`}>
                      {audio.audio_type}
                    </span>
                  </div>
                    
                  <div className="space-y-2 text-sm text-gray-400 mb-4">
                    <div className="flex justify-between">
                      <span>Tamaño:</span>
                      <span>{formatFileSize(audio.size)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Duración:</span>
                      <span>{formatDuration(audio.duration)}</span>
                    </div>
                    {audio.campaign_name && (
                      <div className="flex justify-between">
                        <span>Campaña:</span>
                        <span className="truncate ml-2">{audio.campaign_name}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => handlePlay(audio)}
                      className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors duration-200 flex items-center justify-center space-x-1 ${
                        currentlyPlaying === audio.filename
                          ? 'bg-red-600 hover:bg-red-700 text-white'
                          : 'bg-blue-600 hover:bg-blue-700 text-white'
                      }`}
                    >
                      {currentlyPlaying === audio.filename ? <Icons.Stop /> : <Icons.Play />}
                      <span>{currentlyPlaying === audio.filename ? 'Parar' : 'Tocar'}</span>
                    </button>
                    
                    <button
                      onClick={() => handleDownload(audio)}
                      className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium transition-colors duration-200"
                    >
                      <Icons.Download />
                    </button>
                    
                    <button
                      onClick={() => handleDelete(audio)}
                      className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm font-medium transition-colors duration-200"
                    >
                      <Icons.Delete />
                    </button>
                  </div>
                </div>
            ))}
            </div>
        )}
        </div>

      {/* Dialog de Upload */}
        {openUploadDialog && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 w-full max-w-md">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">Subir Archivo de Audio</h3>
                <button
                  onClick={() => setOpenUploadDialog(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <Icons.Close />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Archivo de Audio</label>
                  <input
                type="file"
                    accept="audio/*"
                onChange={handleFileSelect}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Nombre</label>
                  <input
                    type="text"
                  value={uploadForm.name}
                  onChange={(e) => setUploadForm({...uploadForm, name: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="Nombre del archivo"
                />
                </div>
              
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Descripción</label>
                  <textarea
                    value={uploadForm.description}
                    onChange={(e) => setUploadForm({...uploadForm, description: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="Descripción opcional"
                    rows="3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Tipo de Audio</label>
                  <select
                    value={uploadForm.audio_type}
                    onChange={(e) => setUploadForm({...uploadForm, audio_type: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="greeting">Saludo</option>
                    <option value="voicemail">Buzón de Voz</option>
                    <option value="hold">Espera</option>
                    <option value="dtmf">DTMF</option>
                    <option value="transfer">Transferencia</option>
                  </select>
                </div>

                {uploadProgress > 0 && (
                  <div>
                    <div className="flex justify-between text-sm text-gray-300 mb-1">
                      <span>Progreso</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                />
                    </div>
                  </div>
                )}

                <div className="flex space-x-3 pt-4">
                  <button
                    onClick={() => setOpenUploadDialog(false)}
                    className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleUpload}
                    disabled={loading || !uploadForm.file}
                    className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors duration-200"
                  >
            {loading ? 'Enviando...' : 'Enviar'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Dialog de Estadísticas */}
        {openStatsDialog && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 w-full max-w-lg">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">Estadísticas de Audio</h3>
                <button
                  onClick={() => setOpenStatsDialog(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <Icons.Close />
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700/30 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-400">{stats.total_files || 0}</div>
                  <div className="text-sm text-gray-400">Total de Archivos</div>
                </div>
                <div className="bg-gray-700/30 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-400">{formatFileSize(stats.total_size || 0)}</div>
                  <div className="text-sm text-gray-400">Tamaño Total</div>
                </div>
                <div className="bg-gray-700/30 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-400">{formatDuration(stats.total_duration || 0)}</div>
                  <div className="text-sm text-gray-400">Duración Total</div>
                </div>
                <div className="bg-gray-700/30 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-400">{stats.campaigns_with_audio || 0}</div>
                  <div className="text-sm text-gray-400">Campañas con Audio</div>
                </div>
              </div>

              <div className="mt-6">
                <button
                  onClick={() => setOpenStatsDialog(false)}
                  className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Audio Player Hidden */}
        <audio ref={audioRef} onEnded={() => setCurrentlyPlaying(null)} />
      </div>
    </div>
  );
};

export default AudioManager;