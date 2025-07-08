import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext.jsx';

/**
 * Componente de Login Premium com Glass Morphism
 */
function Login() {
  const { login, loading, error } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loginError, setLoginError] = useState('');
  const [showCredentials, setShowCredentials] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  /**
   * Manipular mudanças no formulário
   */
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Limpar erro quando usuário digita
    if (loginError) setLoginError('');
  };

  /**
   * Submeter formulário de login
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoginError('');

    if (!formData.username.trim() || !formData.password.trim()) {
      setLoginError('Por favor, completá todos los campos');
      return;
    }

    const result = await login(formData.username, formData.password);
    
    if (!result.success) {
      setLoginError(result.error);
    }
  };

  /**
   * Login rápido com credenciais predefinidas
   */
  const quickLogin = (username, password) => {
    setFormData({ username, password });
    login(username, password);
  };

  const testAccounts = [
    {
      username: 'admin',
      password: 'admin123',
      role: 'Administrador',
      description: 'Acceso completo al sistema',
      badge: 'ADMIN',
      badgeColor: 'bg-error-500/20 text-error-300 border-error-500/30',
      icon: '👑'
    },
    {
      username: 'supervisor',
      password: 'supervisor123',
      role: 'Supervisor',
      description: 'Gestión de campañas y listas',
      badge: 'SUPERVISOR',
      badgeColor: 'bg-warning-500/20 text-warning-300 border-warning-500/30',
      icon: '👨‍💼'
    },
    {
      username: 'operador',
      password: 'operador123',
      role: 'Operador',
      description: 'Monitoreo y operación básica',
      badge: 'OPERADOR',
      badgeColor: 'bg-primary-500/20 text-primary-300 border-primary-500/30',
      icon: '👨‍💻'
    }
  ];

  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-4 sm:p-6 lg:p-8">
      {/* Background animado */}
      <div className="absolute inset-0 bg-gradient-to-br from-secondary-900 via-dark-100 to-primary-950"></div>
      
      {/* Elementos decorativos animados */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 sm:w-96 sm:h-96 bg-primary-500 rounded-full opacity-10 animate-pulse-slow blur-3xl"></div>
      <div className="absolute bottom-1/4 right-1/4 w-48 h-48 sm:w-80 sm:h-80 bg-accent-500 rounded-full opacity-10 animate-pulse-slow blur-3xl" style={{animationDelay: '1s'}}></div>
      <div className="absolute top-1/2 left-1/2 w-32 h-32 sm:w-64 sm:h-64 bg-warning-500 rounded-full opacity-5 animate-pulse-slow blur-3xl" style={{animationDelay: '2s'}}></div>
      
      <div className={`relative z-10 w-full max-w-md mx-auto transition-all duration-1000 ${mounted ? 'animate-fade-in-up' : 'opacity-0'}`}>
        
        {/* Header com logo animado */}
        <div className="text-center mb-6 sm:mb-8">
          <div className="relative mx-auto w-16 h-16 sm:w-20 sm:h-20 mb-4 sm:mb-6">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl shadow-glow animate-glow"></div>
            <div className="relative w-full h-full bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center">
              <svg className="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
            </svg>
            </div>
          </div>
          
          <h1 className="text-3xl sm:text-4xl font-bold text-gradient-primary mb-2">
            Discador Pro
          </h1>
          <p className="text-secondary-400 text-sm px-4">
            Sistema de Discado Preditivo Avanzado
          </p>
        </div>

        {/* Formulário de Login com Glass Morphism */}
        <div className="card-glass p-6 sm:p-8 mb-4 sm:mb-6">
          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
            
            {/* Campo Usuario */}
            <div className="space-y-2">
              <label htmlFor="username" className="block text-sm font-medium text-secondary-300">
                Usuario
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none z-10">
                  <svg className="w-4 h-4 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                </div>
                <input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="w-full pl-12 pr-4 py-3 text-white bg-secondary-800/60 border border-secondary-600/50 rounded-xl 
                           focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50
                           placeholder-secondary-500 transition-all duration-200 backdrop-blur-sm
                           disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="Ingresá tu usuario"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Campo Contraseña */}
            <div className="space-y-2">
              <label htmlFor="password" className="block text-sm font-medium text-secondary-300">
                Contraseña
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none z-10">
                  <svg className="w-4 h-4 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full pl-12 pr-12 py-3 text-white bg-secondary-800/60 border border-secondary-600/50 rounded-xl 
                           focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50
                           placeholder-secondary-500 transition-all duration-200 backdrop-blur-sm
                           disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="Ingresá tu contraseña"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-4 text-secondary-400 hover:text-white transition-colors z-10"
                >
                  {showPassword ? (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Erro de login */}
            {(loginError || error) && (
              <div className="bg-error-500/20 border border-error-500/50 text-error-200 px-4 py-3 rounded-xl text-sm backdrop-blur-sm animate-fade-in">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                  </svg>
                  <span>{loginError || error}</span>
                </div>
              </div>
            )}

            {/* Botão de submit */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full relative group h-12 sm:h-auto"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2 sm:space-x-3">
                  <div className="w-4 h-4 sm:w-5 sm:h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span className="text-sm sm:text-base">Ingresando...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-sm sm:text-base">Ingresar al Sistema</span>
                  <svg className="w-4 h-4 sm:w-5 sm:h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
                  </svg>
                </div>
              )}
            </button>
          </form>
        </div>

          {/* Credenciais de teste */}
        <div className="card-glass p-6">
            <button
              onClick={() => setShowCredentials(!showCredentials)}
            className="w-full flex items-center justify-between text-sm text-secondary-300 hover:text-white transition-colors group"
          >
            <div className="flex items-center space-x-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
              </svg>
              <span>Credenciales de prueba</span>
            </div>
            <svg className={`w-4 h-4 transition-transform ${showCredentials ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
            </svg>
            </button>

            {showCredentials && (
            <div className="mt-6 space-y-3 animate-fade-in">
              <p className="text-xs text-secondary-500 mb-4">
                Hacé clic en cualquier cuenta para login automático:
              </p>
                
              {testAccounts.map((account, index) => (
                  <button
                  key={account.username}
                  onClick={() => quickLogin(account.username, account.password)}
                    disabled={loading}
                  className="w-full p-3 sm:p-4 rounded-xl bg-secondary-800/40 hover:bg-secondary-700/60 
                           disabled:opacity-50 disabled:cursor-not-allowed
                           border border-transparent hover:border-primary-500/30
                           transition-all duration-200 group text-left
                           animate-slide-in-right"
                  style={{ animationDelay: `${index * 100}ms` }}
                  >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
                      <div className="text-xl sm:text-2xl flex-shrink-0">{account.icon}</div>
                      <div className="min-w-0 flex-1">
                        <div className="text-xs sm:text-sm font-medium text-white group-hover:text-primary-300 transition-colors truncate">
                          {account.username} / {account.password}
                      </div>
                        <div className="text-xs text-secondary-400 mt-1 hidden sm:block">
                          {account.role} • {account.description}
                    </div>
                        <div className="text-xs text-secondary-400 mt-1 sm:hidden">
                          {account.role}
                    </div>
                      </div>
                    </div>
                    <span className={`px-2 sm:px-3 py-1 rounded-full text-xs font-medium border flex-shrink-0 ${account.badgeColor}`}>
                      <span className="hidden sm:inline">{account.badge}</span>
                      <span className="sm:hidden">{account.badge.slice(0, 3)}</span>
                    </span>
                    </div>
                  </button>
              ))}
              </div>
            )}
        </div>

        {/* Footer */}
        <div className="text-center mt-8 space-y-2">
          <div className="flex items-center justify-center space-x-4 text-xs text-secondary-500">
            <span className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-success-400 rounded-full animate-pulse"></div>
              <span>Sistema Online</span>
            </span>
            <span className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse"></div>
              <span>Seguro</span>
            </span>
          </div>
          <p className="text-xs text-secondary-600">
            &copy; 2025 Discador Preditivo • Tecnología Avanzada
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login; 