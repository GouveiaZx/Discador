import React from 'react';

export const Select = ({ 
  value, 
  onValueChange, 
  children, 
  options = [],
  placeholder = 'Selecionar...',
  className = "",
  disabled = false
}) => {
  return (
    <select
      value={value || ''}
      onChange={(e) => onValueChange && onValueChange(e.target.value)}
      disabled={disabled}
      className={`w-full px-4 py-2.5 border border-gray-600 rounded-lg shadow-sm text-sm text-white bg-gray-700
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200
        hover:border-gray-500 appearance-none cursor-pointer
        ${disabled ? 'bg-gray-800 cursor-not-allowed opacity-60' : 'bg-gray-700'}
        ${className}`}
      style={{
        backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
        backgroundPosition: 'right 0.5rem center',
        backgroundRepeat: 'no-repeat',
        backgroundSize: '1.5em 1.5em'
      }}
    >
      {placeholder && <option value="" className="bg-gray-700 text-gray-400">{placeholder}</option>}
      {/* Renderizar opções como props */}
      {options.map((option, index) => (
        <option key={index} value={option.value} className="bg-gray-700 text-white">
          {option.label}
        </option>
      ))}
      {/* Renderizar children para compatibilidade */}
      {children}
    </select>
  );
}; 