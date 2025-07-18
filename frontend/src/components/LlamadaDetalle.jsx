import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { obtenerDetalleLlamada } from '../services/llamadasService';
import SpinnerLoading from './SpinnerLoading';
import { XMarkIcon } from '@heroicons/react/24/outline';

/**
 * Modal para mostrar detalles de una llamada
 * 
 * @param {Object} props - Propiedades del componente
 * @param {number} props.llamadaId - ID de la llamada
 * @param {boolean} props.isOpen - Estado del modal (abierto/cerrado)
 * @param {Function} props.onClose - Función para cerrar el modal
 */
const LlamadaDetalle = ({ llamadaId, isOpen, onClose }) => {
  const [llamada, setLlamada] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Cargar detalles de la llamada cuando el modal se abra
  useEffect(() => {
    if (isOpen && llamadaId) {
      fetchLlamadaDetails();
    }
  }, [isOpen, llamadaId]);

  const fetchLlamadaDetails = async () => {
    try {
      setLoading(true);
      const response = await obtenerDetalleLlamada(llamadaId);
      setLlamada(response);
    } catch (err) {
      setError('Error al obtener detalles de la llamada. Inténtelo nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  // Formatar data para exibição
  const formatarData = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('es-AR');
  };

  // Calcular duração entre duas datas
  const calcularDuracao = (inicio, fim) => {
    if (!inicio || !fim) return '-';
    
    const inicioDate = new Date(inicio);
    const fimDate = new Date(fim);
    const diffInSeconds = Math.floor((fimDate - inicioDate) / 1000);
    
    const hours = Math.floor(diffInSeconds / 3600);
    const minutes = Math.floor((diffInSeconds % 3600) / 60);
    const seconds = diffInSeconds % 60;
    
    return [
      hours.toString().padStart(2, '0'),
      minutes.toString().padStart(2, '0'),
      seconds.toString().padStart(2, '0')
    ].join(':');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
      <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between border-b border-gray-200 pb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Detalles de la Llamada
          </h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>
        
        <div className="p-6">
          {loading ? (
            <div className="flex justify-center py-8">
              <SpinnerLoading isLoading={true} />
            </div>
          ) : error ? (
            <div className="bg-red-900 text-white p-4 rounded-lg">
              {error}
            </div>
          ) : llamada ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-300 mb-4">Información General</h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-400">ID de la Llamada</p>
                      <p className="font-medium">{llamada.id}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Teléfono</p>
                      <p className="font-medium">{llamada.numero_destino}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Estado</p>
                      <p className="font-medium">
                        <span className={`px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full
                          ${llamada.estado === 'en_progreso' ? 'bg-green-100 text-green-800' : 
                            llamada.estado === 'finalizada' ? 'bg-gray-100 text-gray-800' : 
                            'bg-yellow-100 text-yellow-800'}`}>
                          {llamada.estado}
                        </span>
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Resultado</p>
                      <p className="font-medium">{llamada.resultado || '-'}</p>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium text-gray-300 mb-4">Tempos</h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-400">Fecha de Creación</p>
                      <p className="font-medium">{formatarData(llamada.fecha_creacion)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Início</p>
                      <p className="font-medium">{formatarData(llamada.fecha_asignacion)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Finalización</p>
                      <p className="font-medium">{formatarData(llamada.fecha_finalizacion)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Duración</p>
                      <p className="font-medium">{
                        calcularDuracao(llamada.fecha_asignacion, llamada.fecha_finalizacion || new Date())
                      }</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-300 mb-4">Atendimento</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-400">Usuario</p>
                    <p className="font-medium">{llamada.usuario_email || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Notas</p>
                    <p className="font-medium whitespace-pre-line">{llamada.notas || '-'}</p>
                  </div>
                </div>
              </div>
              
              {llamada.metadatos && (
                <div>
                  <h3 className="text-lg font-medium text-gray-300 mb-4">Metadatos</h3>
                  <pre className="bg-gray-900 p-4 rounded-lg overflow-x-auto text-sm">
                    {JSON.stringify(llamada.metadatos, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <p>No hay datos disponibles</p>
            </div>
          )}
        </div>
        
        <div className="px-6 py-4 border-t border-gray-700 flex justify-end">
          <button
            type="button"
            className="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            onClick={onClose}
          >
                          Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

LlamadaDetalle.propTypes = {
  llamadaId: PropTypes.number,
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired
};

export default LlamadaDetalle;