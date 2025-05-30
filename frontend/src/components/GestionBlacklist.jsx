import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config/api';

/**
 * Componente para gestão de blacklist (números bloqueados)
 */
function GestionBlacklist() {
  const [blacklist, setBlacklist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newNumber, setNewNumber] = useState('');
  const [newReason, setNewReason] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');

  // Carregar blacklist
  useEffect(() => {
    fetchBlacklist();
  }, []);

  /**
   * Buscar lista de números bloqueados
   */
  const fetchBlacklist = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/blacklist`);
      if (!response.ok) throw new Error('Erro ao carregar blacklist');
      
      const data = await response.json();
      setBlacklist(data.blacklist || []);
    } catch (err) {
      setError('Erro ao carregar blacklist: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Adicionar número à blacklist
   */
  const handleAddNumber = async (e) => {
    e.preventDefault();
    
    if (!newNumber.trim()) {
      setError('Número de teléfono es requerido');
      return;
    }

    // Validar formato básico do telefone
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{8,20}$/;
    if (!phoneRegex.test(newNumber.trim())) {
      setError('Formato de teléfono inválido');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/blacklist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          phone_number: newNumber.trim(),
          reason: newReason.trim() || 'Bloqueado manualmente'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao adicionar número');
      }

      const result = await response.json();
      
      // Atualizar lista
      setBlacklist(prev => [result, ...prev]);
      
      // Reset form
      setNewNumber('');
      setNewReason('');
      setShowAddForm(false);
      
    } catch (err) {
      setError('Erro ao adicionar: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Remover número da blacklist
   */
  const handleRemoveNumber = async (id, phoneNumber) => {
    if (!confirm(`¿Desbloquear el número ${phoneNumber}?`)) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/blacklist/${id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao remover número');
      }

      // Remover da lista local
      setBlacklist(prev => prev.filter(item => item.id !== id));
      
    } catch (err) {
      setError('Erro ao remover: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Verificar se número está na blacklist
   */
  const handleCheckNumber = async () => {
    const checkNumber = prompt('Ingrese el número a verificar:');
    if (!checkNumber) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/blacklist/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ phone_number: checkNumber.trim() })
      });

      const result = await response.json();
      
      if (result.is_blacklisted) {
        alert(`❌ Número ${checkNumber} está BLOQUEADO\nMotivo: ${result.reason}\nFecha: ${new Date(result.created_at).toLocaleDateString()}`);
      } else {
        alert(`✅ Número ${checkNumber} está PERMITIDO`);
      }
    } catch (err) {
      setError('Erro na verificação: ' + err.message);
    }
  };

  /**
   * Filtrar lista baseado na busca e filtro
   */
  const filteredBlacklist = blacklist.filter(item => {
    const matchesSearch = item.phone_number.includes(searchTerm) || 
                         (item.reason && item.reason.toLowerCase().includes(searchTerm.toLowerCase()));
    
    if (filter === 'all') return matchesSearch;
    if (filter === 'manual') return matchesSearch && item.reason.includes('manual');
    if (filter === 'auto') return matchesSearch && !item.reason.includes('manual');
    
    return matchesSearch;
  });

  /**
   * Formatar data
   */
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-white">Gestión de Blacklist</h2>
            <p className="text-gray-400 mt-1">Administrá números bloqueados para evitar llamadas no deseadas</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleCheckNumber}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold transition-colors"
            >
              Verificar Número
            </button>
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded font-semibold transition-colors"
            >
              + Agregar Número
            </button>
          </div>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center">
            <div className="bg-red-900 p-3 rounded-full">
              <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"/>
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Total Bloqueados</p>
              <p className="text-2xl font-bold text-white">{blacklist.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center">
            <div className="bg-yellow-900 p-3 rounded-full">
              <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z"/>
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Bloqueos Manuales</p>
              <p className="text-2xl font-bold text-white">
                {blacklist.filter(item => item.reason.includes('manual')).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center">
            <div className="bg-blue-900 p-3 rounded-full">
              <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Bloqueos Automáticos</p>
              <p className="text-2xl font-bold text-white">
                {blacklist.filter(item => !item.reason.includes('manual')).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filtros e busca */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Busca */}
          <div className="flex-1">
            <input
              type="text"
              placeholder="Buscar por número o motivo..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
            />
          </div>

          {/* Filtro */}
          <div>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
            >
              <option value="all">Todos</option>
              <option value="manual">Manuales</option>
              <option value="auto">Automáticos</option>
            </select>
          </div>

          {/* Refresh */}
          <button
            onClick={fetchBlacklist}
            disabled={loading}
            className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-500 text-white px-4 py-2 rounded font-semibold transition-colors"
          >
            {loading ? 'Cargando...' : 'Actualizar'}
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-6 p-4 bg-red-900 border border-red-700 rounded">
          <p className="text-red-100">{error}</p>
        </div>
      )}

      {/* Modal para agregar número */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Agregar a Blacklist</h3>
            
            <form onSubmit={handleAddNumber}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Número de teléfono *
                </label>
                <input
                  type="text"
                  value={newNumber}
                  onChange={(e) => setNewNumber(e.target.value)}
                  placeholder="+54 11 1234-5678"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Motivo (opcional)
                </label>
                <input
                  type="text"
                  value={newReason}
                  onChange={(e) => setNewReason(e.target.value)}
                  placeholder="Cliente solicitó no ser contactado"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddForm(false);
                    setNewNumber('');
                    setNewReason('');
                    setError(null);
                  }}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded font-semibold transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white px-4 py-2 rounded font-semibold transition-colors"
                >
                  {loading ? 'Agregando...' : 'Agregar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lista de números bloqueados */}
      <div className="bg-gray-800 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Número
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Motivo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-gray-400">
                    Cargando...
                  </td>
                </tr>
              ) : filteredBlacklist.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-gray-400">
                    {searchTerm ? 'No se encontraron números con ese criterio' : 'No hay números en la blacklist'}
                  </td>
                </tr>
              ) : (
                filteredBlacklist.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-white font-mono">
                        {item.phone_number}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-300 max-w-xs truncate">
                        {item.reason || 'Sin motivo especificado'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-400">
                        {formatDate(item.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        item.reason.includes('manual') 
                          ? 'bg-yellow-900 text-yellow-200' 
                          : 'bg-blue-900 text-blue-200'
                      }`}>
                        {item.reason.includes('manual') ? 'Manual' : 'Automático'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleRemoveNumber(item.id, item.phone_number)}
                        disabled={loading}
                        className="text-red-400 hover:text-red-300 disabled:text-gray-500 transition-colors"
                      >
                        Desbloquear
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default GestionBlacklist; 