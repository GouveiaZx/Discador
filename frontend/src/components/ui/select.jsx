import React from 'react';

export const Select = ({ 
  value, 
  onValueChange, 
  children, 
  placeholder = 'Selecionar...',
  className = "" 
}) => {
  return (
    <select
      value={value || ''}
      onChange={(e) => onValueChange && onValueChange(e.target.value)}
      className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
        bg-white appearance-none ${className}`}
    >
      {placeholder && <option value="">{placeholder}</option>}
      {children}
    </select>
  );
}; 