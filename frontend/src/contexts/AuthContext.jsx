import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

// Mock de usuários para desenvolvimento
const MOCK_USERS = [
  {
    id: 1,
    username: 'admin',
    password: 'admin123',
    name: 'Administrador',
    email: 'admin@discador.com',
    role: 'admin',
    avatar: null
  },
  {
    id: 2,
    username: 'operador',
    password: 'oper123',
    name: 'Operador Principal',
    email: 'operador@discador.com',
    role: 'operator',
    avatar: null
  },
  {
    id: 3,
    username: 'supervisor',
    password: 'super123',
    name: 'Supervisor de Ventas',
    email: 'supervisor@discador.com',
    role: 'supervisor',
    avatar: null
  }
];

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Verificar se há usuário logado no localStorage
  useEffect(() => {
    const savedUser = localStorage.getItem('discador_user');
    if (savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
      } catch (err) {
        console.error('Erro ao recuperar usuário salvo:', err);
        localStorage.removeItem('discador_user');
      }
    }
    setLoading(false);
  }, []);

  /**
   * Fazer login
   */
  const login = async (username, password) => {
    setLoading(true);
    setError(null);

    try {
      // Simular delay de rede
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Buscar usuário mock
      const foundUser = MOCK_USERS.find(
        u => u.username === username && u.password === password
      );

      if (!foundUser) {
        throw new Error('Usuario o contraseña incorrectos');
      }

      // Remover senha antes de salvar
      const userToSave = { ...foundUser };
      delete userToSave.password;

      // Salvar no localStorage
      localStorage.setItem('discador_user', JSON.stringify(userToSave));
      
      // Atualizar estado
      setUser(userToSave);

      return {
        success: true,
        user: userToSave,
        message: 'Login realizado com sucesso'
      };

    } catch (err) {
      setError(err.message);
      return {
        success: false,
        error: err.message
      };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fazer logout
   */
  const logout = () => {
    localStorage.removeItem('discador_user');
    setUser(null);
    setError(null);
  };

  /**
   * Verificar se usuário tem permissão
   */
  const hasPermission = (requiredRole) => {
    if (!user) return false;
    
    const roleHierarchy = {
      'admin': 3,
      'supervisor': 2,
      'operator': 1
    };

    const userLevel = roleHierarchy[user.role] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;

    return userLevel >= requiredLevel;
  };

  /**
   * Verificar se está autenticado
   */
  const isAuthenticated = () => {
    return !!user;
  };

  /**
   * Obter informações do usuário
   */
  const getUserInfo = () => {
    return user;
  };

  /**
   * Atualizar informações do usuário
   */
  const updateUser = (userData) => {
    const updatedUser = { ...user, ...userData };
    localStorage.setItem('discador_user', JSON.stringify(updatedUser));
    setUser(updatedUser);
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    hasPermission,
    isAuthenticated,
    getUserInfo,
    updateUser,
    mockUsers: MOCK_USERS.map(u => ({ ...u, password: '***' })) // Para debugging
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
} 