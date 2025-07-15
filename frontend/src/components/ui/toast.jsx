import React, { createContext, useContext, useState, useEffect } from 'react';

const ToastContext = createContext();

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'info') => {
    const id = Date.now();
    const toast = { id, message, type };
    setToasts(prev => [...prev, toast]);
    
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
};

const ToastContainer = ({ toasts, onRemove }) => {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map(toast => (
        <Toast key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
};

const Toast = ({ toast, onRemove }) => {
  const variants = {
    success: 'bg-green-600 text-white',
    error: 'bg-red-600 text-white',
    warning: 'bg-yellow-600 text-white',
    info: 'bg-blue-600 text-white'
  };

  return (
    <div className={`px-4 py-3 rounded-lg shadow-lg ${variants[toast.type]} max-w-sm`}>
      <div className="flex items-center justify-between">
        <span className="text-sm">{toast.message}</span>
        <button 
          onClick={() => onRemove(toast.id)}
          className="ml-2 text-white hover:text-gray-200"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

// Compatibility with sonner
export const toast = {
  success: (message) => {
    const event = new CustomEvent('toast', { detail: { message, type: 'success' } });
    window.dispatchEvent(event);
  },
  error: (message) => {
    const event = new CustomEvent('toast', { detail: { message, type: 'error' } });
    window.dispatchEvent(event);
  },
  warning: (message) => {
    const event = new CustomEvent('toast', { detail: { message, type: 'warning' } });
    window.dispatchEvent(event);
  },
  info: (message) => {
    const event = new CustomEvent('toast', { detail: { message, type: 'info' } });
    window.dispatchEvent(event);
  }
};