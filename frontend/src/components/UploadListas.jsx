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

  /**
   * Buscar campañas de la API
   */
  const loadCampaigns = async () => {
    try {
      const data = await makeApiRequest('/api/v1/campaigns', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      setCampaigns(data.campaigns || []);
    } catch (err) {
      setError('Error al cargar campañas: ' + err.message);
    }
  };

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;

    setFile(selectedFile);
    setFileState(FileStates.READING);
    setError(null);
    setUploadResult(null);

    // Leer archivo para preview
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

        // Detectar headers automáticamente
        const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
        const preview = lines.slice(1, 6).map(line => {
          const values = line.split(',').map(v => v.trim().replace(/"/g, ''));
          const row = {};
          headers.forEach((header, index) => {
            row[header] = values[index] || '';
          });
          return row;
        });

        setPreviewData({
          headers,
          preview,
          totalRows: lines.length - 1
        });
        setFileState(FileStates.PREVIEW);
      } catch (err) {
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
    if (!file || !selectedCampaign) {
      setError('Seleccioná un archivo y una campaña');
      return;
    }

    setUploading(true);
    setFileState(FileStates.UPLOADING);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('campaign_id', selectedCampaign);

      const response = await makeApiRequest('/api/v1/lists/upload', {
        method: 'POST',
        body: formData,
        headers: {
          // No setear Content-Type para que el navegador lo haga automáticamente con boundary
        }
      });

      if (response.ok) {
        const result = await response.json();
        setUploadResult(result);
        setFileState(FileStates.SUCCESS);
        setFile(null);
        setPreviewData(null);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al subir archivo');
      }
    } catch (error) {
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
            
            <div className="bg-green-500/20 border border-green-500/50 text-green-200 px-6 py-4 rounded-xl text-center">
              <svg className="w-6 h-6 text-green-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Lista subida con éxito! {uploadResult.contacts_added} contactos procesados.
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-error-500/20 border border-error-500/50 text-error-200 px-6 py-4 rounded-xl text-sm backdrop-blur-sm animate-fade-in mb-6">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-error-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Main Upload Form */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 overflow-hidden">
          <div className="bg-gradient-to-r from-primary-600/20 to-primary-800/20 p-6 border-b border-gray-700/50">
            <h3 className="text-xl font-bold text-white">Cargar Nueva Lista</h3>
          </div>
          
          <div className="p-6 space-y-6">
            {/* Campaign Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Seleccionar Campaña
              </label>
              <select
                value={selectedCampaign}
                onChange={(e) => setSelectedCampaign(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                disabled={uploading}
              >
                <option value="">Elegí una campaña...</option>
                {campaigns.map((campaign) => (
                  <option key={campaign.id} value={campaign.id}>
                    {campaign.name} ({campaign.status})
                  </option>
                ))}
              </select>
            </div>

            {/* File Upload Area */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Archivo CSV
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
                    <p className="text-gray-300 text-lg font-medium mb-2">Arrastrá y soltá tu archivo CSV acá</p>
                    <p className="text-gray-500 mb-4">o</p>
                    <input
                      type="file"
                      accept=".csv"
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
                  disabled={uploading || !selectedCampaign}
                  className="px-8 py-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-medium rounded-lg transition-all duration-200 flex items-center"
                >
                  {uploading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Cargando...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {uploading ? 'Cargando...' : 'Subir Lista'}
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