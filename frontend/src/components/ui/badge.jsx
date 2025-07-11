import React from 'react';

export const Badge = ({ children, variant = 'default', className = "" }) => {
  const variants = {
    default: 'bg-blue-600 text-blue-100 ring-1 ring-blue-500',
    secondary: 'bg-gray-600 text-gray-100 ring-1 ring-gray-500',
    destructive: 'bg-red-600 text-red-100 ring-1 ring-red-500',
    success: 'bg-green-600 text-green-100 ring-1 ring-green-500',
    warning: 'bg-yellow-600 text-yellow-100 ring-1 ring-yellow-500',
    outline: 'bg-transparent border border-gray-500 text-gray-300 hover:bg-gray-700'
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium shadow-sm transition-colors
      ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
}; 