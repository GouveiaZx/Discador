import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext.jsx';
import { CampaignProvider } from './contexts/CampaignContext.jsx';
import ErrorBoundary from './components/ErrorBoundary';
import Login from './components/Login';
import DashboardProfessional from './components/DashboardProfessional';
import HistoricoLlamadas from './components/HistoricoLlamadas';
import GestionCampanhas from './components/GestionCampanhas';
import UploadListas from './components/UploadListas';
import MassiveUploadManager from './components/MassiveUploadManager';
import GestionBlacklist from './components/GestionBlacklist';
import ConfiguracionAvanzada from './components/ConfiguracionAvanzada';
import CampaignControl from './components/CampaignControl';
import RealtimeCallDisplay from './components/RealtimeCallDisplay';
import AudioManager from './components/AudioManager';
import MassiveAudioManager from './components/MassiveAudioManager';
import TransferConfigManager from './components/TransferConfigManager';
import OptimizedUpload from './components/OptimizedUpload';
import ExtensionManager from './components/ExtensionManager';

/**
 * Sistema de Íconos Profesional
 */
const Icons = {
  Dashboard: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"/>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2"/>
    </svg>
  ),
  Monitor: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
    </svg>
  ),
  Campaigns: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"/>
    </svg>
  ),
  Lists: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
    </svg>
  ),
  Blacklist: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636"/>
    </svg>
  ),
  Settings: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
    </svg>
  ),
  History: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </svg>
  ),
  Logout: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
    </svg>
  ),
  Menu: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"/>
    </svg>
  ),
  Close: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
    </svg>
  ),
  Phone: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
    </svg>
  ),
  RealTime: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
    </svg>
  ),
  Trunk: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/>
    </svg>
  ),
  Audio: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
    </svg>
  ),
  Performance: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
    </svg>
  ),
  Control: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"/>
    </svg>
  ),
  Calculator: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
    </svg>
  ),
  Admin: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
    </svg>
  ),
  Transfer: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
    </svg>
  ),
  Upload: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
    </svg>
  ),
  Extension: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
    </svg>
  )
  };

  /**
 * Componente de Carga Profesional
 */
const ProfessionalLoader = () => (
  <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
    {/* Background com gradiente animado */}
    <div className="absolute inset-0 bg-gradient-to-br from-secondary-900 via-dark-100 to-primary-950"></div>
    
    {/* Elementos decorativos */}
    <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-primary-500 rounded-full opacity-10 animate-pulse-slow"></div>
    <div className="absolute bottom-1/4 right-1/4 w-24 h-24 bg-accent-500 rounded-full opacity-10 animate-pulse-slow"></div>
    
    <div className="relative z-10 text-center">
      {/* Logo/Spinner animado */}
      <div className="relative mb-8">
        <div className="w-20 h-20 mx-auto relative">
          <div className="absolute inset-0 border-4 border-primary-500/30 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-transparent border-t-primary-500 rounded-full animate-spin"></div>
          <div className="absolute inset-2 border-2 border-transparent border-r-accent-400 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
        </div>
      </div>
      
      {/* Texto com gradiente */}
      <h2 className="text-2xl font-bold text-gradient-primary mb-2">
        Discador Predictivo
      </h2>
      <p className="text-secondary-400 text-sm animate-pulse">
        Inicializando sistema...
      </p>
      
      {/* Barra de progresso animada */}
      <div className="mt-6 w-64 mx-auto">
        <div className="h-1 bg-secondary-800 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-primary-500 to-accent-400 rounded-full animate-pulse"></div>
        </div>
      </div>
    </div>
  </div>
);

/**
 * Barra Lateral de Navegación Profesional
 */
const ProfessionalSidebar = ({ activeTab, setActiveTab, user, logout, hasPermission, sidebarOpen, setSidebarOpen }) => {
  // Funcionalidades esenciales simplificadas
  const navigationSections = [
    {
      title: "📊 PANEL PRINCIPAL",
      items: [
        { id: 'dashboard', label: 'Panel Principal', icon: Icons.Dashboard, permission: null, essential: true },
        { id: 'realtime', label: 'Llamadas en Vivo', icon: Icons.RealTime, permission: null, essential: true },
      ]
    },
    {
      title: "📞 OPERACIONES",
      items: [
        { id: 'campanhas', label: 'Gestión de Campañas', icon: Icons.Campaigns, permission: 'supervisor', essential: true },
        { id: 'listas', label: 'Gestión de Listas', icon: Icons.Lists, permission: 'supervisor', essential: true },
        { id: 'massive-upload', label: 'Carga Masiva (700M+)', icon: Icons.Lists, permission: 'supervisor', essential: true },
        { id: 'optimized-upload', label: 'Upload Optimizado', icon: Icons.Upload, permission: 'supervisor', essential: true },
        { id: 'audios', label: 'Gestión de Audios', icon: Icons.Audio, permission: 'supervisor', essential: true },
        { id: 'massive-audio', label: 'Audio Masivo', icon: Icons.Audio, permission: 'supervisor', essential: true },
      ]
    },
    {
      title: "⚙️ CONFIGURACIÓN",
      items: [
        { id: 'extensions', label: 'Gestión de Extensiones', icon: Icons.Extension, permission: 'admin', essential: true },
        { id: 'transfer-config', label: 'Config. Transferencia', icon: Icons.Transfer, permission: 'admin', essential: true },
        { id: 'blacklist', label: 'Lista Negra', icon: Icons.Blacklist, permission: 'admin', essential: true },
        { id: 'configuracion', label: 'Configuración', icon: Icons.Settings, permission: 'admin', essential: true },
      ]
    },
    {
      title: "📈 MONITOREO",
      items: [
        { id: 'historico', label: 'Histórico', icon: Icons.History, permission: null, essential: true },
      ]
    }
  ];

  // Modo simplificado - solo funciones esenciales
  const [simpleMode, setSimpleMode] = useState(true);
  
  const getVisibleItems = () => {
    if (simpleMode) {
      return navigationSections.flatMap(section => 
        section.items.filter(item => item.essential)
      );
    }
    return navigationSections.flatMap(section => section.items);
  };

  const getRoleColor = () => {
    switch (user?.role) {
      case 'admin': return 'bg-error-500/20 text-error-300 border-error-500/30';
      case 'supervisor': return 'bg-warning-500/20 text-warning-300 border-warning-500/30';
      case 'operator': return 'bg-primary-500/20 text-primary-300 border-primary-500/30';
      default: return 'bg-secondary-500/20 text-secondary-300 border-secondary-500/30';
    }
  };

  const getUserInitial = () => {
    return user?.name?.charAt(0).toUpperCase() || user?.username?.charAt(0).toUpperCase() || 'U';
  };

  return (
    <>
      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-screen w-80 sidebar
        transform transition-transform duration-300 ease-in-out lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        glass-panel border-r border-white/10 overflow-hidden
      `}>
        <div className="flex flex-col h-full max-h-screen">
          {/* Header */}
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-glow">
                  <span className="text-white font-bold text-lg">D</span>
                </div>
                <div>
                  <h1 className="text-lg font-bold text-white">Discador</h1>
                  <p className="text-xs text-secondary-400">Sistema Predictivo</p>
                </div>
              </div>

              {/* Close button for mobile */}
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <Icons.Close />
              </button>
            </div>
          </div>
          
          {/* User Profile */}
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">{getUserInitial()}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{user?.name}</p>
                <p className="text-xs text-secondary-400 truncate">{user?.email}</p>
                <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full border mt-1 ${getRoleColor()}`}>
                  {user?.role?.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
          
          {/* Sistema simplificado - sin toggle de modo */}
          <div className="p-4 border-b border-white/10">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-white">Sistema Simplificado</span>
            </div>
            <p className="text-xs text-secondary-400 text-center">
              ✅ Funciones Esenciales Activas
            </p>
          </div>

          {/* Navigation - solo funciones esenciales */}
          <nav className="flex-1 p-4 space-y-4 overflow-y-auto custom-scrollbar">
            <div className="space-y-4">
              {navigationSections.map((section, sectionIndex) => {
                const visibleItems = section.items.filter(item => 
                  !item.permission || hasPermission(item.permission)
                );
                
                if (visibleItems.length === 0) return null;
                
                return (
                  <div key={sectionIndex} className="space-y-1">
                    <div className="px-3 py-2 bg-gray-800/50 rounded-lg">
                      <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wide">
                        {section.title}
                      </h4>
                    </div>
                    
                    <div className="space-y-1">
                      {visibleItems.map((item) => {
                        const isActive = activeTab === item.id;
                        const IconComponent = item.icon;
                        
                        return (
                          <button 
                            key={item.id}
                            onClick={() => {
                              setActiveTab(item.id);
                              setSidebarOpen(false);
                            }}
                            className={`
                              w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg
                              transition-all duration-150 text-left
                              ${isActive 
                                ? 'bg-blue-600 text-white shadow-md' 
                                : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
                              }
                            `}
                          >
                            <div className={`text-base ${isActive ? 'text-white' : 'text-gray-400'}`}>
                              <IconComponent />
                            </div>
                            <span className="font-medium text-sm flex-1">{item.label}</span>
                            
                            {isActive && (
                              <div className="w-2 h-2 bg-white rounded-full"></div>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </nav>
          
          {/* Logout Button */}
          <div className="flex-shrink-0 p-4 border-t border-white/10 bg-secondary-900/50 backdrop-blur-sm">
            <button
              onClick={logout}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl
                       bg-error-500/10 text-error-400 hover:bg-error-500/20 
                       transition-all duration-200 border border-error-500/20
                       hover:border-error-500/40 hover:shadow-lg hover:shadow-error-500/20
                       hover:scale-[1.02] active:scale-[0.98]"
            >
              <Icons.Logout />
              <span className="font-medium">Cerrar Sesión</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};

/**
 * Header Principal
 */
const ProfessionalHeader = ({ setSidebarOpen, activeTab }) => {
  const getPageTitle = () => {
    const titles = {
      dashboard: 'Panel Principal',
      realtime: 'Llamadas en Tiempo Real',
      campanhas: 'Gestión de Campañas',
      listas: 'Gestión de Listas',
      'massive-upload': 'Carga Masiva de Listas',
      'optimized-upload': 'Upload Optimizado',
      audios: 'Gestión de Audios',
      'massive-audio': 'Gestión Masiva de Audios',
      extensions: 'Gestión de Extensiones',
      'transfer-config': 'Configuración de Transferencia',
      blacklist: 'Lista Negra',
      configuracion: 'Configuración',
      historico: 'Histórico de Llamadas'
    };
    return titles[activeTab] || 'Panel de Control';
  };

  return (
    <header className="sticky top-0 z-30 w-full glass-panel border-b border-white/10 bg-secondary-900/80 backdrop-blur-xl">
      <div className="w-full max-w-none px-6 py-4">
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center space-x-4">
            {/* Mobile menu button */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-white/10 transition-colors text-white"
            >
              <Icons.Menu />
            </button>
            
            <div>
              <h1 className="text-xl font-bold text-white">{getPageTitle()}</h1>
              <p className="text-sm text-secondary-400">Sistema de Discado Predictivo</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Status indicator */}
            <div className="hidden md:flex items-center space-x-2 px-3 py-2 rounded-lg bg-success-500/20 border border-success-500/30">
              <div className="w-2 h-2 bg-success-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-success-300 font-medium">Sistema Activo</span>
            </div>
            
            {/* Current time */}
            <div className="hidden lg:block text-sm text-secondary-400">
              {new Date().toLocaleTimeString('es-AR', { 
                hour: '2-digit', 
                minute: '2-digit',
                timeZone: 'America/Argentina/Buenos_Aires'
              })}
            </div>
          </div>
        </div>
        </div>
      </header>
  );
};

/**
 * Componente de Acceso Denegado
 */
const AccessDenied = ({ requiredLevel }) => (
  <div className="max-w-md mx-auto mt-12">
    <div className="card-glass p-8 text-center">
      <div className="w-16 h-16 mx-auto mb-4 bg-error-500/20 rounded-full flex items-center justify-center">
        <svg className="w-8 h-8 text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z"/>
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">Acceso Denegado</h3>
      <p className="text-secondary-400 mb-4">No tenés permisos para acceder a esta sección.</p>
      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-warning-500/20 text-warning-300 border border-warning-500/30">
        Se requiere: {requiredLevel}
      </span>
    </div>
  </div>
);

/**
 * Componente principal de la aplicación autenticada
 */
function AuthenticatedApp() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [campaignControlId, setCampaignControlId] = useState(null);
  const { user, logout, hasPermission } = useAuth();

  // Cerrar sidebar al redimensionar para desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setSidebarOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-900 via-dark-100 to-secondary-900 full-width-container">
      {/* Sidebar */}
      <ProfessionalSidebar 
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        logout={logout}
        hasPermission={hasPermission}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />
      
      {/* Main Content */}
      <div className="lg:ml-80 min-h-screen flex flex-col">
        {/* Header */}
        <ProfessionalHeader 
          setSidebarOpen={setSidebarOpen}
          activeTab={activeTab}
        />
        
        {/* Page Content */}
        <main className="flex-1 animate-fade-in">
          <div className="container-max-width p-6">
            {/* Pantalla de Control de Campaña */}
            {campaignControlId && (
              <CampaignControl 
                campaignId={campaignControlId} 
                onClose={() => setCampaignControlId(null)} 
              />
            )}
            
            {/* Pantallas Principales - solo funciones esenciales */}
            {!campaignControlId && (
              <>
                {activeTab === 'dashboard' && <DashboardProfessional />}
                {activeTab === 'realtime' && <RealtimeCallDisplay />}
                {activeTab === 'campanhas' && hasPermission('supervisor') && (
                  <GestionCampanhas onOpenCampaignControl={setCampaignControlId} />
                )}
                {activeTab === 'listas' && hasPermission('supervisor') && <UploadListas />}
                {activeTab === 'massive-upload' && hasPermission('supervisor') && <MassiveUploadManager />}
                {activeTab === 'optimized-upload' && hasPermission('supervisor') && <OptimizedUpload />}
                {activeTab === 'audios' && hasPermission('supervisor') && <AudioManager />}
                {activeTab === 'massive-audio' && hasPermission('supervisor') && <MassiveAudioManager />}
                {activeTab === 'extensions' && hasPermission('admin') && <ExtensionManager />}
                {activeTab === 'transfer-config' && hasPermission('admin') && <TransferConfigManager />}
                {activeTab === 'blacklist' && hasPermission('admin') && <GestionBlacklist />}
                {activeTab === 'configuracion' && hasPermission('admin') && <ConfiguracionAvanzada />}
                {activeTab === 'historico' && <HistoricoLlamadas />}
              </>
            )}
        
            {/* Access Denied Messages */}
            {((activeTab === 'campanhas' || activeTab === 'listas' || activeTab === 'massive-upload' || activeTab === 'optimized-upload' || activeTab === 'audios' || activeTab === 'massive-audio') && !hasPermission('supervisor')) && (
              <AccessDenied requiredLevel="Supervisor" />
            )}
            {((activeTab === 'extensions' || activeTab === 'transfer-config' || activeTab === 'blacklist' || activeTab === 'configuracion') && !hasPermission('admin')) && (
              <AccessDenied requiredLevel="Administrador" />
            )}
          </div>
      </main>
        </div>
    </div>
  );
}

/**
 * Componente principal de la aplicación
 */
function App() {
  return (
    <ErrorBoundary>
    <AuthProvider>
      <AppContent />
    </AuthProvider>
    </ErrorBoundary>
  );
}

/**
 * Contenido condicional basado en la autenticación
 */
function AppContent() {
  const { user, loading } = useAuth();

  // Loading inicial
  if (loading) {
    return <ProfessionalLoader />;
  }

  // Se não estiver logado, mostrar tela de login
  if (!user) {
    return <Login />;
  }

  // Se estiver logado, mostrar aplicação com contexto de campanhas
  return (
    <CampaignProvider>
      <AuthenticatedApp />
    </CampaignProvider>
  );
}

export default App;