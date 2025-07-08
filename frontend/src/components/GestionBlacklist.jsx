import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

/**
 * Componente para gestión de blacklist
 */
function GestionBlacklist() {
  const [blacklist, setBlacklist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newNumber, setNewNumber] = useState('');
  const [newReason, setNewReason] = useState('');
  const [adding, setAdding] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');
  const [checkPhone, setCheckPhone] = useState('');
  const [checkResult, setCheckResult] = useState(null);
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    // Cargar blacklist al montar el componente
    fetchBlacklist();
  }, []);

  /**
   * Buscar blacklist de la API
   */
  const fetchBlacklist = async () => {
    try {
      setLoading(true);
      const data = await makeApiRequest('/api/v1/blacklist', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      let blacklistData = data.blacklist || [];
      if (Array.isArray(blacklistData)) {
        blacklistData = blacklistData.map(item => ({
          id: item.id || Date.now() + Math.random(),
          phone: item.phone || item.numero || '',
          reason: item.reason || item.motivo || 'Manual',
          created_at: item.created_at || item.fecha_agregado || new Date().toISOString(),
          type: item.type || 'manual'
        }));
      }
      setBlacklist(blacklistData);
    } catch (err) {
      setError('Error al cargar blacklist: ' + err.message);
      setBlacklist([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Agregar número a la blacklist
   */
  const handleAddNumber = async () => {
    if (!newNumber.trim()) {
      setError('Número de teléfono es requerido');
      return;
    }

    // Validar formato básico del teléfono
    const phoneRegex = /^\+?[1-9]\d{1,14}$/;
    if (!phoneRegex.test(newNumber.replace(/\s/g, ''))) {
      setError('Formato de teléfono inválido');
      return;
    }

    setAdding(true);
    setError(null);

    try {
      const data = await makeApiRequest('/api/v1/blacklist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          phone: newNumber.trim(),
          reason: newReason.trim() || 'Agregado manualmente'
        })
      });

      // Actualizar lista
      setBlacklist(prev => [data, ...prev]);
      
      // Limpiar formulario
      setNewNumber('');
      setNewReason('');
      
      // Mostrar mensaje de éxito
      setError(null);
    } catch (err) {
      setError('Error al agregar: ' + err.message);
    } finally {
      setAdding(false);
    }
  };

  /**
   * Remover número de la blacklist
   */
  const handleRemoveNumber = async (id) => {
    try {
      setError(null);
      
      await makeApiRequest(`/api/v1/blacklist/${id}`, {
        method: 'DELETE'
      });

      // Remover de la lista local
      setBlacklist(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      setError('Error al remover: ' + err.message);
    }
  };

  /**
   * Verificar si número está en la blacklist
   */
  const handleCheckPhone = async () => {
    if (!checkPhone.trim()) return;

    setChecking(true);
    setCheckResult(null);
    setError(null);

    try {
      const data = await makeApiRequest('/api/v1/blacklist/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          phone: checkPhone.trim()
        })
      });

      setCheckResult({
        phone: checkPhone.trim(),
        isBlocked: data.is_blacklisted,
        reason: data.reason,
        date: data.created_at,
        found: data.is_blacklisted
      });
    } catch (err) {
      setError('Error en la verificación: ' + err.message);
    } finally {
      setChecking(false);
    }
  };

  /**
   * Filtrar lista basado en la búsqueda y filtro
   */
  const filteredBlacklist = blacklist.filter(item => {
    const matchesSearch = !searchTerm || 
      item.phone?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.reason?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesFilter = filter === 'all' || 
      (filter === 'manual' && item.type === 'manual') ||
      (filter === 'auto' && item.type === 'auto');

    return matchesSearch && matchesFilter;
  });

  // Estadísticas
  const safeBlacklist = blacklist.filter(item => item && item.reason);
  const manualBlocks = safeBlacklist.filter(item =>
    item.type === 'manual' || 
    item.reason?.toLowerCase().includes('manual') ||
    item.reason?.toLowerCase().includes('agregado')
  ).length;
  
  const autoBlocks = safeBlacklist.length - manualBlocks;

  /**
   * Formatear fecha
   */
  const formatDate = (dateString) => {
    if (!dateString) return 'Fecha no disponible';
    try {
      return new Date(dateString).toLocaleDateString('es-AR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Fecha inválida';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4 bg-gradient-to-r from-red-400 to-red-600 bg-clip-text text-transparent">
            Gestión de Blacklist
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Control avanzado de números bloqueados con protección inteligente
          </p>
        </div>

        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* Total bloqueados */}
          <div className="bg-gradient-to-r from-red-500/20 to-red-600/20 border border-red-500/30 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Total Bloqueados</p>
                <p className="text-2xl font-bold text-white">{blacklist.length}</p>
              </div>
              <div className="p-3 bg-red-500/20 rounded-lg">
                <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
                </svg>
              </div>
            </div>
          </div>

          {/* Bloqueos manuales */}
          <div className="bg-gradient-to-r from-orange-500/20 to-orange-600/20 border border-orange-500/30 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Manuales</p>
                <p className="text-2xl font-bold text-white">{manualBlocks}</p>
              </div>
              <div className="p-3 bg-orange-500/20 rounded-lg">
                <svg className="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Bloqueos automáticos */}
          <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Automáticos</p>
                <p className="text-2xl font-bold text-white">{autoBlocks}</p>
              </div>
              <div className="p-3 bg-blue-500/20 rounded-lg">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Filtro activo */}
          <div className="bg-gradient-to-r from-green-500/20 to-green-600/20 border border-green-500/30 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Mostrando</p>
                <p className="text-2xl font-bold text-white">{filteredBlacklist.length}</p>
              </div>
              <div className="p-3 bg-green-500/20 rounded-lg">
                <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Herramientas */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Buscar y filtrar */}
          <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Buscar Números</h3>
            
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Buscar por número o motivo..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="all">Todos los bloqueos</option>
                <option value="manual">Solo manuales</option>
                <option value="auto">Solo automáticos</option>
              </select>
              
              <button
                onClick={fetchBlacklist}
                className="w-full px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Actualizar Lista
              </button>
            </div>
          </div>

          {/* Verificar número */}
          <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Verificar Número</h3>
            
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Ingresá un número para verificar..."
                value={checkPhone}
                onChange={(e) => setCheckPhone(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              
              <button
                onClick={handleCheckPhone}
                disabled={checking || !checkPhone.trim()}
                className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors flex items-center justify-center"
              >
                {checking ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Verificando...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    Verificar
                  </>
                )}
              </button>

              {/* Resultado de la verificación */}
              {checkResult && (
                <div className={`p-4 rounded-lg border ${
                  checkResult.isBlocked 
                    ? 'bg-red-500/20 border-red-500/50 text-red-200' 
                    : 'bg-green-500/20 border-green-500/50 text-green-200'
                }`}>
                  <div className="flex items-center mb-2">
                    {checkResult.isBlocked ? (
                      <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                    <span className="font-medium">
                      {checkResult.isBlocked ? 'Número BLOQUEADO' : 'Número NO bloqueado'}
                    </span>
                  </div>
                  
                  <p className="text-sm">
                    <strong>Número:</strong> {checkResult.phone}
                  </p>
                  
                  {checkResult.isBlocked && (
                    <>
                      <p className="text-sm">
                        <strong>Motivo:</strong> {checkResult.reason || 'No especificado'}
                      </p>
                      <p className="text-sm">
                        <strong>Fecha:</strong> {formatDate(checkResult.date)}
                      </p>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-error-500/20 border border-error-500/50 text-error-200 px-6 py-4 rounded-xl text-sm backdrop-blur-sm animate-fade-in mb-6">
            <p className="text-red-100">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-2 text-red-300 hover:text-red-100 underline text-xs"
            >
              Cerrar
            </button>
          </div>
        )}

        {/* Agregar nuevo número */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 mb-8">
          <div className="bg-gradient-to-r from-red-600/20 to-red-800/20 p-6 border-b border-gray-700/50">
            <h3 className="text-lg font-semibold text-white mb-4">Agregar a Blacklist</h3>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input
                type="text"
                placeholder="Número de teléfono (ej: +541198765432)"
                value={newNumber}
                onChange={(e) => setNewNumber(e.target.value)}
                className="px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
              
              <input
                type="text"
                placeholder="Motivo del bloqueo (opcional)"
                value={newReason}
                onChange={(e) => setNewReason(e.target.value)}
                className="px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
              
              <button
                onClick={handleAddNumber}
                disabled={adding || !newNumber.trim()}
                className="px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors flex items-center justify-center"
              >
                {adding ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Agregando...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Agregar
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Lista de números bloqueados */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50">
          <div className="bg-gradient-to-r from-gray-600/20 to-gray-800/20 p-6 border-b border-gray-700/50">
            <h3 className="text-lg font-semibold text-white">
              Lista de Números Bloqueados
              <span className="ml-2 text-sm text-gray-400">({filteredBlacklist.length} números)</span>
            </h3>
          </div>
          
          <div className="p-6">
            {blacklist.length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p className="text-gray-400 text-lg">No hay números en la blacklist</p>
                <p className="text-gray-500 text-sm">Agregá números para comenzar a proteger tu sistema</p>
              </div>
            ) : filteredBlacklist.length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <p className="text-gray-400 text-lg">
                  {checkPhone ? 'No se encontraron números con ese criterio' : 'No hay números en la blacklist'}
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left py-3 px-4 text-gray-300 font-medium">Número</th>
                      <th className="text-left py-3 px-4 text-gray-300 font-medium">Motivo</th>
                      <th className="text-left py-3 px-4 text-gray-300 font-medium">Fecha</th>
                      <th className="text-left py-3 px-4 text-gray-300 font-medium">Tipo</th>
                      <th className="text-right py-3 px-4 text-gray-300 font-medium">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredBlacklist.map((item) => (
                      <tr key={item.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors">
                        <td className="py-4 px-4">
                          <span className="font-mono text-white bg-gray-700/50 px-2 py-1 rounded">
                            {item.phone}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-gray-300">
                          {item.reason || 'Sin motivo especificado'}
                        </td>
                        <td className="py-4 px-4 text-gray-400 text-sm">
                          {formatDate(item.created_at)}
                        </td>
                        <td className="py-4 px-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            item.type === 'manual' 
                              ? 'bg-orange-500/20 text-orange-300'
                              : 'bg-blue-500/20 text-blue-300'
                          }`}>
                            {item.type === 'manual' ? 'Manual' : 'Automático'}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-right">
                          <button
                            onClick={() => handleRemoveNumber(item.id)}
                            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors flex items-center ml-auto"
                          >
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                            Remover
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default GestionBlacklist; 