import React from 'react';

export const Button = ({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'default', 
  className = "" 
}) => {
  const variants = {
    default: 'bg-blue-600 hover:bg-blue-700 text-white',
    outline: 'bg-transparent border border-gray-300 text-gray-700 hover:bg-gray-50',
    destructive: 'bg-red-600 hover:bg-red-700 text-white'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors
        ${variants[variant]}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}`}
    >
      {children}
    </button>
  );
}; 