import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext.jsx';

/**
 * Componente de tela de login
 */
function Login() {
  const { login, loading, error } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loginError, setLoginError] = useState('');
  const [showCredentials, setShowCredentials] = useState(false);

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
      setLoginError('Por favor, completa todos los campos');
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

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-white">Discador</h2>
          <p className="mt-2 text-gray-400">Sistema de Discado Predictivo</p>
        </div>

        {/* Formulário de Login */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                Usuario
              </label>
              <input
                id="username"
                name="username"
                type="text"
                value={formData.username}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ingresa tu usuario"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Contraseña
              </label>
              <input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ingresa tu contraseña"
                disabled={loading}
              />
            </div>

            {/* Erro de login */}
            {(loginError || error) && (
              <div className="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded">
                {loginError || error}
              </div>
            )}

            {/* Botão de submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-semibold py-2 px-4 rounded-md transition-colors duration-200 flex items-center justify-center"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Ingresando...
                </>
              ) : (
                'Ingresar'
              )}
            </button>
          </form>

          {/* Credenciais de teste */}
          <div className="mt-6 pt-6 border-t border-gray-700">
            <button
              onClick={() => setShowCredentials(!showCredentials)}
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              {showCredentials ? 'Ocultar' : 'Ver'} credenciales de prueba
            </button>

            {showCredentials && (
              <div className="mt-4 space-y-3">
                <p className="text-xs text-gray-400 mb-3">
                  Usuarios de prueba (hacer clic para login automático):
                </p>
                
                <div className="space-y-2">
                  <button
                    onClick={() => quickLogin('admin', 'admin123')}
                    disabled={loading}
                    className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 rounded transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="text-sm font-medium text-white">admin / admin123</div>
                        <div className="text-xs text-gray-400">Administrador - Acceso completo</div>
                      </div>
                      <span className="bg-red-900 text-red-200 text-xs px-2 py-1 rounded">ADMIN</span>
                    </div>
                  </button>

                  <button
                    onClick={() => quickLogin('supervisor', 'super123')}
                    disabled={loading}
                    className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 rounded transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="text-sm font-medium text-white">supervisor / super123</div>
                        <div className="text-xs text-gray-400">Supervisor - Gestión de campanhas</div>
                      </div>
                      <span className="bg-yellow-900 text-yellow-200 text-xs px-2 py-1 rounded">SUPERVISOR</span>
                    </div>
                  </button>

                  <button
                    onClick={() => quickLogin('operador', 'oper123')}
                    disabled={loading}
                    className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 rounded transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="text-sm font-medium text-white">operador / oper123</div>
                        <div className="text-xs text-gray-400">Operador - Monitoreo básico</div>
                      </div>
                      <span className="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">OPERADOR</span>
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm">
          <p>&copy; 2025 Sistema Discador. Todos los derechos reservados.</p>
        </div>
      </div>
    </div>
  );
}

export default Login; 