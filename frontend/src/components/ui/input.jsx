import React from 'react';

export const Input = ({ 
  type = 'text', 
  value, 
  onChange, 
  placeholder, 
  disabled = false,
  min,
  max,
  className = "" 
}) => {
  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      min={min}
      max={max}
      className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
        ${disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white'}
        ${className}`}
    />
  );
}; 