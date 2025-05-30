import React, { useState, useEffect, useCallback } from 'react';
import LlamadasEnProgresoTable from './LlamadasEnProgresoTable';
import SpinnerLoading from './SpinnerLoading';
import { obtenerLlamadasEnProgreso, finalizarLlamadaManualmente } from '../services/llamadasService';

/**
 * Componente principal para monitoramento de chamadas em andamento
 * com atualização automática
 * 
 * @returns {JSX.Element} Componente JSX
 */
const MonitorLlamadasEnProgreso = () => {
  const [llamadas, setLlamadas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Intervalo de atualização (5 segundos)
  const POLLING_INTERVAL = 5000;

  /**
   * Carrega as chamadas em andamento da API
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
      setError('Error al cargar las llamadas. Intente nuevamente.');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Finaliza uma chamada manualmente
   * 
   * @param {number} llamadaId - ID da chamada a finalizar
   */
  const handleFinalizarLlamada = async (llamadaId) => {
    try {
      await finalizarLlamadaManualmente(llamadaId);
      
      // Atualiza a lista removendo a chamada finalizada
      setLlamadas(llamadas.filter(llamada => llamada.id !== llamadaId));
    } catch (err) {
      console.error(`Error al finalizar la llamada ID ${llamadaId}:`, err);
      alert(`Error al finalizar la llamada: ${err.message}`);
    }
  };

  // Efeito para carregar as chamadas inicialmente e configurar o polling
  useEffect(() => {
    // Carrega as chamadas imediatamente ao montar o componente
    cargarLlamadas();
    
    // Configura o intervalo para atualização automática
    const intervalId = setInterval(() => {
      cargarLlamadas();
    }, POLLING_INTERVAL);
    
    // Limpa o intervalo quando o componente é desmontado
    return () => clearInterval(intervalId);
  }, [cargarLlamadas]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">Monitoramento de Chamadas em Andamento</h1>
          <div className="flex items-center space-x-4">
            <SpinnerLoading isLoading={loading} />
            {lastUpdated && (
              <span className="text-xs text-gray-400">
                Última atualização: {lastUpdated.toLocaleTimeString()}
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