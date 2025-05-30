import React from 'react';
import PropTypes from 'prop-types';

/**
 * Componente de seleção dropdown simples
 * 
 * @param {Object} props - Propriedades do componente
 * @returns {JSX.Element} Componente JSX
 */
const Select = ({ 
  options, 
  value, 
  onChange, 
  placeholder = 'Selecionar...',
  className = '' 
}) => {
  return (
    <select
      value={value || ''}
      onChange={e => onChange(e.target.value)}
      className={`w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-md 
                  hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 
                  text-white appearance-none ${className}`}
    >
      <option value="">{placeholder}</option>
      {options.map(option => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
};

Select.propTypes = {
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      label: PropTypes.string.isRequired
    })
  ).isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  className: PropTypes.string
};

export default Select; 