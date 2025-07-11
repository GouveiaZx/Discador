import React from 'react';

export const Alert = ({ children, variant = 'default', className = "" }) => {
  const variants = {
    default: 'bg-gray-800 border-gray-600 text-gray-100',
    destructive: 'bg-red-900/30 border-red-600 text-red-100',
    warning: 'bg-yellow-900/30 border-yellow-600 text-yellow-100',
    success: 'bg-green-900/30 border-green-600 text-green-100',
    info: 'bg-blue-900/30 border-blue-600 text-blue-100'
  };

  return (
    <div className={`rounded-lg border p-4 shadow-lg ${variants[variant]} ${className}`}>
      {children}
    </div>
  );
};

export const AlertDescription = ({ children, className = "" }) => {
  return (
    <div className={`text-sm mt-1 ${className}`}>
      {children}
    </div>
  );
}; 