import React, { createContext, useContext, useState } from 'react';

const TabsContext = createContext();

export const Tabs = ({ children, value, onValueChange, className = "" }) => {
  const [activeTab, setActiveTab] = useState(value);

  const handleTabChange = (newValue) => {
    setActiveTab(newValue);
    if (onValueChange) {
      onValueChange(newValue);
    }
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab: handleTabChange }}>
      <div className={className}>
        {children}
      </div>
    </TabsContext.Provider>
  );
};

export const TabsList = ({ children, className = "" }) => {
  return (
    <div className={`flex bg-gray-800 p-1 rounded-lg border border-gray-700 ${className}`}>
      {children}
    </div>
  );
};

export const TabsTrigger = ({ children, value, className = "" }) => {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  const isActive = activeTab === value;

  return (
    <button
      className={`flex-1 px-4 py-2.5 text-sm font-medium rounded-md transition-all duration-200 transform hover:scale-105
        ${isActive 
          ? 'bg-blue-600 text-white shadow-lg' 
          : 'text-gray-400 hover:text-white hover:bg-gray-700'
        } ${className}`}
      onClick={() => setActiveTab(value)}
    >
      {children}
    </button>
  );
};

export const TabsContent = ({ children, value, className = "" }) => {
  const { activeTab } = useContext(TabsContext);
  
  if (activeTab !== value) {
    return null;
  }

  return (
    <div className={`mt-6 ${className}`}>
      {children}
    </div>
  );
}; 