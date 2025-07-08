import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Componente para seleção de intervalo de datas
 * 
 * @param {Object} props - Propriedades do componente
 * @returns {JSX.Element} Componente JSX
 */
const DateRangePicker = ({ 
  startDate, 
  endDate, 
  onChangeStartDate, 
  onChangeEndDate,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Formatar data para exibição
  const formatDateDisplay = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  // Texto a exibir no botão
  const buttonText = startDate || endDate
    ? `${startDate ? formatDateDisplay(startDate) : 'Início'} - ${endDate ? formatDateDisplay(endDate) : 'Fim'}`
    : 'Selecionar período';

  // Fecha o dropdown ao clicar fora
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Limpar datas
  const clearDates = (e) => {
    e.stopPropagation();
    onChangeStartDate('');
    onChangeEndDate('');
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        type="button"
        className="w-full px-4 py-2 text-left bg-gray-800 border border-gray-700 rounded-md 
                  hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex justify-between items-center"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="truncate">{buttonText}</span>
        <div className="flex items-center">
          {(startDate || endDate) && (
            <button 
              onClick={clearDates}
              className="mr-2 text-gray-400 hover:text-white"
              aria-label="Limpar datas"
            >
              ×
            </button>
          )}
          <svg 
            className={`w-4 h-4 transition-transform ${isOpen ? 'transform rotate-180' : ''}`}
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 20 20" 
            fill="currentColor"
          >
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </div>
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 p-4 bg-gray-800 border border-gray-700 rounded-md shadow-lg">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="start-date" className="block text-sm font-medium text-gray-300 mb-1">
                Data inicial
              </label>
              <input
                id="start-date"
                type="date"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={startDate || ''}
                onChange={(e) => onChangeStartDate(e.target.value)}
                max={endDate || undefined}
              />
            </div>
            <div>
              <label htmlFor="end-date" className="block text-sm font-medium text-gray-300 mb-1">
                Data final
              </label>
              <input
                id="end-date"
                type="date"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={endDate || ''}
                onChange={(e) => onChangeEndDate(e.target.value)}
                min={startDate || undefined}
              />
            </div>
          </div>
          
          <div className="flex justify-end mt-4">
            <button
              type="button"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              onClick={() => setIsOpen(false)}
            >
              Aplicar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

DateRangePicker.propTypes = {
  startDate: PropTypes.string,
  endDate: PropTypes.string,
  onChangeStartDate: PropTypes.func.isRequired,
  onChangeEndDate: PropTypes.func.isRequired,
  className: PropTypes.string
};

export default DateRangePicker; 