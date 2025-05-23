import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Componente de seleção múltipla para filtros
 * 
 * @param {Object} props - Propriedades do componente
 * @returns {JSX.Element} Componente JSX
 */
const MultiSelect = ({ 
  options, 
  selectedValues = [], 
  onChange,
  placeholder = 'Selecionar...',
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

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

  // Alternar estado do dropdown
  const toggleDropdown = () => setIsOpen(!isOpen);

  // Alternar seleção de uma opção
  const toggleOption = (value) => {
    const isSelected = selectedValues.includes(value);
    let newValues;
    
    if (isSelected) {
      newValues = selectedValues.filter(val => val !== value);
    } else {
      newValues = [...selectedValues, value];
    }
    
    onChange(newValues);
  };

  // Limpar todas as seleções
  const clearAll = (e) => {
    e.stopPropagation();
    onChange([]);
  };

  // Texto a exibir no botão
  const buttonText = selectedValues.length > 0
    ? `${selectedValues.length} selecionado${selectedValues.length > 1 ? 's' : ''}`
    : placeholder;

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        type="button"
        className="w-full px-4 py-2 text-left bg-gray-800 border border-gray-700 rounded-md 
                  hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex justify-between items-center"
        onClick={toggleDropdown}
      >
        <span className="truncate">{buttonText}</span>
        <div className="flex items-center">
          {selectedValues.length > 0 && (
            <button 
              onClick={clearAll}
              className="mr-2 text-gray-400 hover:text-white"
              aria-label="Limpar seleção"
            >
              ×
            </button>
          )}
          <svg className={`w-4 h-4 transition-transform ${isOpen ? 'transform rotate-180' : ''}`} 
            xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </div>
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-700 rounded-md shadow-lg max-h-60 overflow-auto">
          {options.map((option) => (
            <div
              key={option.value}
              className="flex items-center px-4 py-2 cursor-pointer hover:bg-gray-700"
              onClick={() => toggleOption(option.value)}
            >
              <input
                type="checkbox"
                className="w-4 h-4 mr-2 rounded text-blue-500 focus:ring-blue-500 focus:ring-opacity-50 bg-gray-700 border-gray-600"
                checked={selectedValues.includes(option.value)}
                onChange={() => {}}
              />
              <span>{option.label}</span>
            </div>
          ))}
          {options.length === 0 && (
            <div className="px-4 py-2 text-gray-400">
              Nenhuma opção disponível
            </div>
          )}
        </div>
      )}
    </div>
  );
};

MultiSelect.propTypes = {
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      label: PropTypes.string.isRequired
    })
  ).isRequired,
  selectedValues: PropTypes.array,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  className: PropTypes.string
};

export default MultiSelect; 