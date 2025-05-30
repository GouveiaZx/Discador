import React from 'react';
import PropTypes from 'prop-types';

/**
 * Componente de spinner para indicar carregamento
 * 
 * @param {boolean} isLoading - Indica se está carregando
 * @returns {JSX.Element|null} Componente JSX ou null se não estiver carregando
 */
const SpinnerLoading = ({ isLoading }) => {
  if (!isLoading) return null;
  
  return (
    <div className="flex items-center justify-center space-x-2 text-sm text-gray-400">
      <svg className="animate-spin h-4 w-4 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>Atualizando...</span>
    </div>
  );
};

SpinnerLoading.propTypes = {
  isLoading: PropTypes.bool.isRequired
};

export default SpinnerLoading; 