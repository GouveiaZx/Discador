import React from 'react';

export const Button = ({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'default', 
  size = 'md',
  className = "" 
}) => {
  const variants = {
    default: 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl',
    outline: 'bg-transparent border-2 border-gray-600 text-gray-300 hover:bg-gray-700 hover:border-gray-500',
    destructive: 'bg-red-600 hover:bg-red-700 text-white shadow-lg hover:shadow-xl',
    success: 'bg-green-600 hover:bg-green-700 text-white shadow-lg hover:shadow-xl',
    warning: 'bg-yellow-600 hover:bg-yellow-700 text-white shadow-lg hover:shadow-xl',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white shadow-lg hover:shadow-xl',
    ghost: 'bg-transparent text-gray-300 hover:bg-gray-800 hover:text-white'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95
        ${variants[variant]}
        ${sizes[size]}
        ${disabled ? 'opacity-50 cursor-not-allowed hover:scale-100' : 'cursor-pointer'}
        ${className}`}
    >
      {children}
    </button>
  );
}; 