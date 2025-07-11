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
      className={`w-full px-4 py-2.5 border border-gray-600 rounded-lg shadow-sm text-sm text-white bg-gray-700
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200
        placeholder:text-gray-400 hover:border-gray-500
        ${disabled ? 'bg-gray-800 cursor-not-allowed opacity-60' : 'bg-gray-700'}
        ${className}`}
    />
  );
}; 