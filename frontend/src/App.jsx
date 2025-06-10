import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext.jsx';
import Login from './components/Login';
import MonitorLlamadasEnProgreso from './components/MonitorLlamadasEnProgreso';
import HistoricoLlamadas from './components/HistoricoLlamadas';
import GestionCampanhas from './components/GestionCampanhas';
import UploadListas from './components/UploadListas';
import GestionBlacklist from './components/GestionBlacklist';
import ConfiguracionAvanzada from './components/ConfiguracionAvanzada';

/**
 * Componente principal da aplicação autenticada
 */
function AuthenticatedApp() {
  const [activeTab, setActiveTab] = useState('monitor');
  const { user, logout, hasPermission } = useAuth();

  /**
   * Obter inicial do usuário para avatar
   */
  const getUserInitial = () => {
    return user?.name?.charAt(0).toUpperCase() || user?.username?.charAt(0).toUpperCase() || 'U';
  };

  /**
   * Obter cor do badge baseada no role
   */
  const getRoleColor = () => {
    switch (user?.role) {
      case 'admin': return 'bg-red-900 text-red-200';
      case 'supervisor': return 'bg-yellow-900 text-yellow-200';
      case 'operator': return 'bg-blue-900 text-blue-200';
      default: return 'bg-gray-900 text-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold text-blue-400">
                Discador - Panel de Control
              </h1>
              <div className="text-sm text-gray-400">
                Sistema de monitoreo de llamadas
              </div>
            </div>
            
            {/* User info e logout */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                {/* Avatar */}
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">
                  {getUserInitial()}
                </div>
                
                {/* User info */}
                <div className="hidden md:block">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-white">{user?.name}</span>
                    <span className={`text-xs px-2 py-1 rounded ${getRoleColor()}`}>
                      {user?.role?.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400">{user?.email}</div>
                </div>
              </div>

              {/* Logout button */}
              <button
                onClick={logout}
                className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm font-semibold transition-colors"
                title="Cerrar sesión"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                </svg>
              </button>
            </div>
          </div>
          
          <nav className="mt-4">
            <ul className="flex space-x-1">
              <li>
                <button 
                  onClick={() => setActiveTab('monitor')}
                  className={`px-4 py-2 rounded-t-lg transition-colors ${
                    activeTab === 'monitor' 
                      ? 'bg-gray-900 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Monitoreo
                </button>
              </li>
              
              {/* Campanhas - Supervisor+ */}
              {hasPermission('supervisor') && (
                <li>
                  <button 
                    onClick={() => setActiveTab('campanhas')}
                    className={`px-4 py-2 rounded-t-lg transition-colors ${
                      activeTab === 'campanhas' 
                        ? 'bg-gray-900 text-white' 
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    Campañas
                  </button>
                </li>
              )}
              
              {/* Upload de Listas - Supervisor+ */}
              {hasPermission('supervisor') && (
                <li>
                  <button 
                    onClick={() => setActiveTab('listas')}
                    className={`px-4 py-2 rounded-t-lg transition-colors ${
                      activeTab === 'listas' 
                        ? 'bg-gray-900 text-white' 
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    Listas
                  </button>
                </li>
              )}
              
              {/* Blacklist - Admin */}
              {hasPermission('admin') && (
                <li>
                  <button 
                    onClick={() => setActiveTab('blacklist')}
                    className={`px-4 py-2 rounded-t-lg transition-colors ${
                      activeTab === 'blacklist' 
                        ? 'bg-gray-900 text-white' 
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    Blacklist
                  </button>
                </li>
              )}
              
              {/* Configuración Avanzada - Admin */}
              {hasPermission('admin') && (
                <li>
                  <button 
                    onClick={() => setActiveTab('configuracion')}
                    className={`px-4 py-2 rounded-t-lg transition-colors ${
                      activeTab === 'configuracion' 
                        ? 'bg-gray-900 text-white' 
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    ⚙️ Configuración
                  </button>
                </li>
              )}
              
              <li>
                <button 
                  onClick={() => setActiveTab('historico')}
                  className={`px-4 py-2 rounded-t-lg transition-colors ${
                    activeTab === 'historico' 
                      ? 'bg-gray-900 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Historial
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </header>
      
      <main>
        {activeTab === 'monitor' && <MonitorLlamadasEnProgreso />}
        {activeTab === 'campanhas' && hasPermission('supervisor') && <GestionCampanhas />}
        {activeTab === 'listas' && hasPermission('supervisor') && <UploadListas />}
        {activeTab === 'blacklist' && hasPermission('admin') && <GestionBlacklist />}
        {activeTab === 'configuracion' && hasPermission('admin') && <ConfiguracionAvanzada />}
        {activeTab === 'historico' && <HistoricoLlamadas />}
        
        {/* Mensaje de acceso denegado */}
        {((activeTab === 'campanhas' || activeTab === 'listas') && !hasPermission('supervisor')) && (
          <div className="container mx-auto px-4 py-12">
            <div className="bg-red-900 border border-red-700 rounded-lg p-8 text-center">
              <svg className="mx-auto h-16 w-16 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z"/>
              </svg>
              <h3 className="text-lg font-semibold text-red-100 mb-2">Acceso Denegado</h3>
              <p className="text-red-200">No tienes permisos para acceder a esta sección.</p>
              <p className="text-red-300 text-sm mt-2">Nivel requerido: Supervisor</p>
            </div>
          </div>
        )}
        
        {(activeTab === 'blacklist' && !hasPermission('admin')) && (
          <div className="container mx-auto px-4 py-12">
            <div className="bg-red-900 border border-red-700 rounded-lg p-8 text-center">
              <svg className="mx-auto h-16 w-16 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z"/>
              </svg>
              <h3 className="text-lg font-semibold text-red-100 mb-2">Acceso Denegado</h3>
              <p className="text-red-200">No tienes permisos para acceder a esta sección.</p>
              <p className="text-red-300 text-sm mt-2">Nivel requerido: Administrador</p>
            </div>
          </div>
        )}
      </main>
      
      <footer className="bg-gray-800 py-4 mt-8">
        <div className="container mx-auto px-4">
          <p className="text-center text-gray-400 text-sm">
            &copy; {new Date().getFullYear()} Discador - Todos los derechos reservados
          </p>
        </div>
      </footer>
    </div>
  );
}

/**
 * Componente principal da aplicação
 */
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

/**
 * Conteúdo condicional baseado na autenticação
 */
function AppContent() {
  const { user, loading } = useAuth();

  // Loading inicial
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Cargando...</p>
        </div>
      </div>
    );
  }

  // Se não estiver logado, mostrar tela de login
  if (!user) {
    return <Login />;
  }

  // Se estiver logado, mostrar aplicação
  return <AuthenticatedApp />;
}

export default App; 