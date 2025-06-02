import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api.js';

/**
 * Componente para gestão de blacklist
 */
function GestionBlacklist() {
  const [blacklist, setBlacklist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEntry, setNewEntry] = useState({
    phone: '',
    reason: '',
    notes: ''
  });
  const [checkPhone, setCheckPhone] = useState('');
  const [checkResult, setCheckResult] = useState(null);

  // Carregar blacklist ao montar o componente
  useEffect(() => {
    fetchBlacklist();
  }, []);

  /**
   * Buscar blacklist da API
   */
  const fetchBlacklist = async () => {
    setLoading(true);
    try {
      const data = await makeApiRequest('/blacklist', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      // Mapear dados do backend real para formato esperado pelo frontend
      let blacklistData = data.blacklist || [];
      if (Array.isArray(blacklistData)) {
        blacklistData = blacklistData.map(item => ({
          ...item,
          phone: item.phone_number || item.phone, // Converter phone_number para phone
          reason: item.reason || 'Sin motivo especificado',
          notes: item.notes || '',
          created_at: item.created_at || new Date().toISOString(),
          created_by: item.created_by || 'sistema'
        }));
      }
      
      setBlacklist(blacklistData);
    } catch (err) {
      if (err.message.includes('Endpoint not implemented')) {
        console.info('ℹ️ Using mock blacklist data (backend not available)');
        
        // Dados mock de blacklist
        const mockBlacklist = [
          {
            id: 1,
            phone: '+5411987654321',
            reason: 'Solicitou para não ligar',
            notes: 'Cliente solicitou exclusão em 15/12/2023',
            created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            created_by: 'admin'
          },
          {
            id: 2,
            phone: '+5411555123456',
            reason: 'Número inválido',
            notes: 'Número fora de serviço, múltiplas tentativas falharam',
            created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
            created_by: 'operador1'
          },
          {
            id: 3,
            phone: '+5411444789123',
            reason: 'Reclamação',
            notes: 'Cliente fez reclamação formal',
            created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            created_by: 'supervisor'
          },
          {
            id: 4,
            phone: '+5411333222111',
            reason: 'Bloqueado manualmente',
            notes: '',
            created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
            created_by: 'admin'
          }
        ];

        setBlacklist(mockBlacklist);
      } else {
        setError('Erro ao carregar blacklist: ' + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Adicionar número à blacklist
   */
  const handleAddNumber = async (e) => {
    e.preventDefault();
    
    if (!newEntry.phone.trim()) {
      setError('Número de teléfono es requerido');
      return;
    }

    // Validar formato básico do telefone
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{8,20}$/;
    if (!phoneRegex.test(newEntry.phone.trim())) {
      setError('Formato de teléfono inválido');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await makeApiRequest('/blacklist', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          phone: newEntry.phone.trim(),
          reason: newEntry.reason.trim() || 'Bloqueado manualmente',
          notes: newEntry.notes.trim()
        })
      });
      
      // Atualizar lista
      setBlacklist(prev => [data, ...prev]);
      
      // Reset form
      setNewEntry({
        phone: '',
        reason: '',
        notes: ''
      });
      setShowAddForm(false);
      
    } catch (err) {
      if (err.message.includes('Endpoint not implemented')) {
        console.info('ℹ️ Simulating blacklist addition (backend not available)');
        
        // Simular adição bem-sucedida
        const newBlacklistEntry = {
          id: blacklist.length + 1,
          phone: newEntry.phone.trim(),
          reason: newEntry.reason.trim() || 'Bloqueado manualmente',
          notes: newEntry.notes.trim() || '',
          created_at: new Date().toISOString(),
          created_by: 'admin'
        };
        
        setBlacklist(prev => [newBlacklistEntry, ...prev]);
        
        // Reset form
        setNewEntry({
          phone: '',
          reason: '',
          notes: ''
        });
        setShowAddForm(false);
      } else {
        setError('Erro ao adicionar: ' + err.message);
      }
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
      await makeApiRequest(`/blacklist/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      // Remover da lista local
      setBlacklist(prev => prev.filter(item => item.id !== id));
      
    } catch (err) {
      if (err.message.includes('Endpoint not implemented')) {
        console.info(`ℹ️ Simulating blacklist removal for ${phoneNumber} (backend not available)`);
        
        // Simular remoção bem-sucedida
        setBlacklist(prev => prev.filter(item => item.id !== id));
      } else {
        setError('Erro ao remover: ' + err.message);
      }
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
      const data = await makeApiRequest('/blacklist/check', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ phone_number: checkNumber.trim() })
      });
      
      if (data.is_blacklisted) {
        alert(`❌ Número ${checkNumber} está BLOQUEADO\nMotivo: ${data.reason}\nFecha: ${new Date(data.created_at).toLocaleDateString()}`);
      } else {
        alert(`✅ Número ${checkNumber} está PERMITIDO`);
      }
    } catch (err) {
      if (err.message.includes('Endpoint not implemented')) {
        console.info(`ℹ️ Simulating blacklist check for ${checkNumber} (backend not available)`);
        
        // Verificar na lista local se o número existe
        const existsInBlacklist = blacklist.find(item => 
          item.phone && item.phone.includes(checkNumber.trim())
        );
        
        if (existsInBlacklist) {
          alert(`❌ Número ${checkNumber} está BLOQUEADO\nMotivo: ${existsInBlacklist.reason || 'Sin motivo especificado'}\nFecha: ${new Date(existsInBlacklist.created_at).toLocaleDateString()}`);
        } else {
          alert(`✅ Número ${checkNumber} está PERMITIDO`);
        }
      } else {
        setError('Erro na verificação: ' + err.message);
      }
    }
  };

  /**
   * Filtrar lista baseado na busca e filtro
   */
  const filteredBlacklist = blacklist.filter(item => {
    if (!item || !item.phone) return false; // Verificar se item é válido
    
    const matchesSearch = item.phone.includes(checkPhone) || 
                         (item.reason && item.reason.toLowerCase().includes(checkPhone.toLowerCase()));
    
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
              value={checkPhone}
              onChange={(e) => setCheckPhone(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
            />
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
                  value={newEntry.phone}
                  onChange={(e) => setNewEntry({ ...newEntry, phone: e.target.value })}
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
                  value={newEntry.reason}
                  onChange={(e) => setNewEntry({ ...newEntry, reason: e.target.value })}
                  placeholder="Cliente solicitó no ser contactado"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Notas (opcional)
                </label>
                <textarea
                  value={newEntry.notes}
                  onChange={(e) => setNewEntry({ ...newEntry, notes: e.target.value })}
                  placeholder="Notas adicionales"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddForm(false);
                    setNewEntry({
                      phone: '',
                      reason: '',
                      notes: ''
                    });
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
                    {checkPhone ? 'No se encontraron números con ese criterio' : 'No hay números en la blacklist'}
                  </td>
                </tr>
              ) : (
                filteredBlacklist.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-white font-mono">
                        {item.phone}
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
                        onClick={() => handleRemoveNumber(item.id, item.phone)}
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