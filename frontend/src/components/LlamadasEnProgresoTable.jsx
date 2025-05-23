import React from 'react';
import PropTypes from 'prop-types';
import Timer from './Timer';

/**
 * Tabela que exibe as chamadas em andamento
 * 
 * @param {Array} llamadas - Lista de chamadas a serem exibidas
 * @param {Function} onFinalizarLlamada - Função para finalizar chamada
 * @returns {JSX.Element} Componente JSX
 */
const LlamadasEnProgresoTable = ({ llamadas, onFinalizarLlamada }) => {
  const handleFinalizar = (llamadaId) => {
    // Confirmação antes de finalizar
    if (window.confirm('¿Está seguro que desea finalizar esta llamada manualmente?')) {
      onFinalizarLlamada(llamadaId);
    }
  };

  // Se não houver chamadas, exibe mensagem
  if (!llamadas || llamadas.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p className="text-xl">No hay llamadas en progreso actualmente</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg shadow">
      <table className="min-w-full bg-gray-800 divide-y divide-gray-700">
        <thead className="bg-gray-700">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              ID
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Teléfono
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Usuario
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Inicio
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Duración
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Estado
            </th>
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-700">
          {llamadas.map((llamada) => (
            <tr key={llamada.id} className="hover:bg-gray-700">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                {llamada.id}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                {llamada.numero_destino}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                {llamada.usuario_email || 'Sin asignar'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                {new Date(llamada.fecha_asignacion).toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <Timer startTime={llamada.fecha_asignacion} />
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                  {llamada.estado}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => handleFinalizar(llamada.id)}
                  className="text-red-500 hover:text-red-400 bg-gray-700 hover:bg-gray-600 rounded px-3 py-1 transition-colors"
                >
                  Finalizar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

LlamadasEnProgresoTable.propTypes = {
  llamadas: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      numero_destino: PropTypes.string.isRequired,
      usuario_email: PropTypes.string,
      fecha_asignacion: PropTypes.string.isRequired,
      estado: PropTypes.string.isRequired
    })
  ).isRequired,
  onFinalizarLlamada: PropTypes.func.isRequired
};

export default LlamadasEnProgresoTable; 