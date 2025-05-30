import React from 'react';
import PropTypes from 'prop-types';

/**
 * Tabela para exibir histórico de chamadas
 * 
 * @param {Object} props - Propriedades do componente
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
  // Formatar data para exibição
  const formatarData = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('pt-BR');
  };

  // Formatar duração de chamada
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

  // Renderizar estado com cores diferentes
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

  // Renderizar resultado com cores diferentes
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

  // Renderizar paginação
  const renderPagination = () => {
    // Determinar quais botões de página mostrar
    const pageButtons = [];
    const maxVisiblePages = 5;
    
    let startPage = Math.max(1, page - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    // Ajustar startPage se estamos no final
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // Botão para primeira página
    if (startPage > 1) {
      pageButtons.push(
        <button
          key="first"
          onClick={() => onChangePage(1)}
          className="px-3 py-1 rounded-md bg-gray-700 text-white hover:bg-gray-600"
          aria-label="Primeira página"
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
    
    // Botões para páginas principais
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
    
    // Botão para última página
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
          aria-label="Próxima página"
        >
          Próxima
        </button>
      </div>
    );
  };

  // Se não houver chamadas, exibir mensagem
  if (!llamadas || llamadas.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p className="text-xl">Nenhuma chamada encontrada</p>
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
                Telefone
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Usuário
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Estado
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Resultado
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Início
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Fim
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Duração
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
          Mostrando <span className="font-semibold">{llamadas.length}</span> de <span className="font-semibold">{totalItems}</span> chamadas
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