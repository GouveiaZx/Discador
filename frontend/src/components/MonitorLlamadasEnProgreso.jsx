import React, { useState, useEffect, useCallback } from 'react';
import LlamadasEnProgresoTable from './LlamadasEnProgresoTable';
import DashboardAvanzado from './DashboardAvanzado';
import SpinnerLoading from './SpinnerLoading';
import { obtenerLlamadasEnProgreso, finalizarLlamadaManualmente } from '../services/llamadasService';

/**
 * Componente principal para monitoreo de llamadas en curso
 * con actualización automática y dashboard avanzado
 * 
 * @returns {JSX.Element} Componente JSX
 */
const MonitorLlamadasEnProgreso = () => {
  const [llamadas, setLlamadas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [viewMode, setViewMode] = useState('dashboard'); // 'dashboard' ou 'table'

  // Intervalo de actualización (5 segundos)
  const POLLING_INTERVAL = 5000;

  /**
   * Carga las llamadas en curso desde la API
   */
  const cargarLlamadas = useCallback(async () => {
    setLoading(true);
    try {
      const data = await obtenerLlamadasEnProgreso();
      setLlamadas(data.llamadas || []);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      console.error('Error al cargar las llamadas:', err);
      setError('Error al cargar las llamadas. Intentá nuevamente.');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Finaliza una llamada manualmente
   * 
   * @param {number} llamadaId - ID de la llamada a finalizar
   */
  const handleFinalizarLlamada = async (llamadaId) => {
    try {
      await finalizarLlamadaManualmente(llamadaId);
      
      // Actualiza la lista removiendo la llamada finalizada
      setLlamadas(llamadas.filter(llamada => llamada.id !== llamadaId));
    } catch (err) {
      console.error(`Error al finalizar la llamada ID ${llamadaId}:`, err);
      alert(`Error al finalizar la llamada: ${err.message}`);
    }
  };

  // Efecto para cargar las llamadas inicialmente y configurar el polling
  useEffect(() => {
    // Carga las llamadas inmediatamente al montar el componente
    cargarLlamadas();
    
    // Configura el intervalo para actualización automática
    const intervalId = setInterval(() => {
      cargarLlamadas();
    }, POLLING_INTERVAL);
    
    // Limpia el intervalo cuando el componente se desmonta
    return () => clearInterval(intervalId);
  }, [cargarLlamadas]);

  // Se está no modo dashboard, renderizar dashboard avanzado
  if (viewMode === 'dashboard') {
    return (
      <div>
        {/* Toggle de visualização */}
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center mb-4">
            <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => setViewMode('dashboard')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'dashboard'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'table'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Tabla Detallada
              </button>
            </div>
          </div>
        </div>
        
        <DashboardAvanzado />
      </div>
    );
  }

  // Modo tabela clássico
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col space-y-4">
        {/* Toggle de visualização */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">Monitoreo de Llamadas en Curso</h1>
          <div className="flex items-center space-x-4">
            <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => setViewMode('dashboard')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'dashboard'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'table'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Tabla Detallada
              </button>
            </div>
            
            <SpinnerLoading isLoading={loading} />
            {lastUpdated && (
              <span className="text-xs text-gray-400">
                Última actualización: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
        
        {error && (
          <div className="bg-red-900 text-white p-4 rounded-lg">
            {error}
          </div>
        )}
        
        <LlamadasEnProgresoTable
          llamadas={llamadas}
          onFinalizarLlamada={handleFinalizarLlamada}
        />
        
        <div className="text-sm text-gray-400 mt-4">
          <p>Las llamadas se actualizan automáticamente cada 5 segundos.</p>
        </div>
      </div>
    </div>
  );
};

export default MonitorLlamadasEnProgreso; 