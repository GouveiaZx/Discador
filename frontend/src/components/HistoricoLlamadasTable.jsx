import React from 'react';
import PropTypes from 'prop-types';

/**
 * Tabla para mostrar historial de llamadas
 * 
 * @param {Object} props - Propiedades del componente
 * @returns {JSX.Element} Componente JSX
 */
const HistoricoLlamadasTable = ({ 
  llamadas, 
  totalItems,
  page,
  totalPages,
  onChangePage,
  onViewDetails
}) => {
  // Formatear fecha para visualización
  const formatarData = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('es-AR');
  };

  // Formatear duración de llamada
  const formatarDuracion = (inicio, fin) => {
    if (!inicio || !fin) return '-';
    
    const inicioDate = new Date(inicio);
    const finDate = new Date(fin);
    const diffInSeconds = Math.floor((finDate - inicioDate) / 1000);
    
    const hours = Math.floor(diffInSeconds / 3600);
    const minutes = Math.floor((diffInSeconds % 3600) / 60);
    const seconds = diffInSeconds % 60;
    
    return [
      hours.toString().padStart(2, '0'),
      minutes.toString().padStart(2, '0'),
      seconds.toString().padStart(2, '0')
    ].join(':');
  };

  // Renderizar estado con colores diferentes
  const renderizarEstado = (estado) => {
    let bgColorClass = 'bg-gray-100 text-gray-800';
    
    if (estado === 'en_progreso') {
      bgColorClass = 'bg-green-100 text-green-800';
    } else if (estado === 'pendiente') {
      bgColorClass = 'bg-yellow-100 text-yellow-800';
    } else if (estado === 'finalizada') {
      bgColorClass = 'bg-gray-100 text-gray-800';
    }
    
    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${bgColorClass}`}>
        {estado}
      </span>
    );
  };

  // Renderizar resultado con colores diferentes
  const renderizarResultado = (resultado) => {
    if (!resultado) return '-';
    
    let bgColorClass = 'bg-gray-100 text-gray-800';
    
    if (resultado.includes('exito')) {
      bgColorClass = 'bg-green-100 text-green-800';
    } else if (resultado.includes('ocupado') || resultado.includes('no_responde')) {
      bgColorClass = 'bg-yellow-100 text-yellow-800';
    } else if (resultado.includes('error') || resultado.includes('fallida')) {
      bgColorClass = 'bg-red-100 text-red-800';
    }
    
    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${bgColorClass}`}>
        {resultado}
      </span>
    );
  };

  // Renderizar paginación
  const renderPagination = () => {
    // Determinar qué botones de página mostrar
    const pageButtons = [];
    const maxVisiblePages = 5;
    
    let startPage = Math.max(1, page - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    // Ajustar startPage si estamos al final
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // Botón para primera página
    if (startPage > 1) {
      pageButtons.push(
        <button
          key="first"
          onClick={() => onChangePage(1)}
          className="px-3 py-1 rounded-md bg-gray-700 text-white hover:bg-gray-600"
          aria-label="Primera página"
        >
          1
        </button>
      );
      
      if (startPage > 2) {
        pageButtons.push(
          <span key="ellipsis1" className="px-2">...</span>
        );
      }
    }
    
    // Botones para páginas principales
    for (let i = startPage; i <= endPage; i++) {
      pageButtons.push(
        <button
          key={i}
          onClick={() => onChangePage(i)}
          className={`px-3 py-1 rounded-md ${
            i === page
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-white hover:bg-gray-600'
          }`}
        >
          {i}
        </button>
      );
    }
    
    // Botón para última página
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        pageButtons.push(
          <span key="ellipsis2" className="px-2">...</span>
        );
      }
      
      pageButtons.push(
        <button
          key="last"
          onClick={() => onChangePage(totalPages)}
          className="px-3 py-1 rounded-md bg-gray-700 text-white hover:bg-gray-600"
          aria-label="Última página"
        >
          {totalPages}
        </button>
      );
    }
    
    return (
      <div className="flex items-center space-x-1">
        <button
          onClick={() => onChangePage(page - 1)}
          disabled={page === 1}
          className={`px-3 py-1 rounded-md ${
            page === 1
              ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
              : 'bg-gray-700 text-white hover:bg-gray-600'
          }`}
          aria-label="Página anterior"
        >
          Anterior
        </button>
        
        <div className="flex items-center space-x-1 px-2">
          {pageButtons}
        </div>
        
        <button
          onClick={() => onChangePage(page + 1)}
          disabled={page === totalPages}
          className={`px-3 py-1 rounded-md ${
            page === totalPages
              ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
              : 'bg-gray-700 text-white hover:bg-gray-600'
          }`}
          aria-label="Siguiente página"
        >
          Siguiente
        </button>
      </div>
    );
  };

  // Si no hay llamadas, mostrar mensaje
  if (!llamadas || llamadas.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p className="text-xl">No se encontraron llamadas</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-lg shadow">
        <table className="min-w-full bg-gray-800 divide-y divide-gray-700">
          <thead className="bg-gray-700">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                ID
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                TELÉFONO
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                USUARIO
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                ESTADO
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                RESULTADO
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                INICIO
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                FIN
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                DURACIÓN
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {llamadas.map((llamada) => (
              <tr 
                key={llamada.id} 
                className="hover:bg-gray-700 cursor-pointer"
                onClick={() => onViewDetails(llamada.id)}
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                  {llamada.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  {llamada.numero_destino}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  {llamada.usuario_email || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {renderizarEstado(llamada.estado)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {renderizarResultado(llamada.resultado)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  {formatarData(llamada.fecha_asignacion)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  {formatarData(llamada.fecha_finalizacion)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  {formatarDuracion(llamada.fecha_asignacion, llamada.fecha_finalizacion || new Date())}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
        <div className="text-sm text-gray-400">
          Mostrando <span className="font-semibold">{llamadas.length}</span> de <span className="font-semibold">{totalItems}</span> llamadas
        </div>
        
        {totalPages > 1 && renderPagination()}
      </div>
    </div>
  );
};

HistoricoLlamadasTable.propTypes = {
  llamadas: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      numero_destino: PropTypes.string.isRequired,
      usuario_email: PropTypes.string,
      estado: PropTypes.string.isRequired,
      resultado: PropTypes.string,
      fecha_asignacion: PropTypes.string,
      fecha_finalizacion: PropTypes.string
    })
  ).isRequired,
  totalItems: PropTypes.number.isRequired,
  page: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  onChangePage: PropTypes.func.isRequired,
  onViewDetails: PropTypes.func.isRequired
};

export default HistoricoLlamadasTable; 