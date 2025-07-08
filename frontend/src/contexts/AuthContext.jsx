import React, { createContext, useContext, useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Verificar si hay usuario logueado en localStorage
    try {
      const savedUser = localStorage.getItem('discador_user');
      const savedToken = localStorage.getItem('discador_token');
      
      if (savedUser && savedToken) {
        setUser(JSON.parse(savedUser));
      }
    } catch (err) {
      console.error('Error al recuperar usuario guardado:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Hacer login - VERSÃO SIMPLIFICADA E DIRETA
   */
  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    
    // FORÇAR AUTENTICAÇÃO LOCAL - SEM API
    console.log('🚀 LOGIN DIRETO - Dados recebidos:', { username, password });
    
    // Limpar espaços e normalizar
    const cleanUsername = username?.toString().trim().toLowerCase();
    const cleanPassword = password?.toString().trim();
    
    console.log('🧹 Dados limpos:', { cleanUsername, cleanPassword });
    
    // CREDENCIAIS HARDCODED - GARANTIDAS
    const validCredentials = {
      'admin': { password: 'admin123', role: 'admin', name: 'Administrador', id: 1 },
      'supervisor': { password: 'supervisor123', role: 'supervisor', name: 'Supervisor', id: 2 },
      'operador': { password: 'operador123', role: 'operator', name: 'Operador', id: 3 }
    };
    
    console.log('🔑 Credenciais válidas:', validCredentials);
    
    // Verificar se usuário existe
    const userConfig = validCredentials[cleanUsername];
    console.log('👤 Configuração do usuário encontrada:', userConfig);
    
    if (userConfig && userConfig.password === cleanPassword) {
      console.log('✅ LOGIN APROVADO!');
      
      // Criar usuário
      const authenticatedUser = {
        id: userConfig.id,
        username: cleanUsername,
        role: userConfig.role,
        name: userConfig.name,
        email: `${cleanUsername}@discador.com`
      };
      
      // Token simulado
      const token = btoa(JSON.stringify({
        userId: userConfig.id,
        username: cleanUsername,
        role: userConfig.role,
        exp: Date.now() + 24 * 60 * 60 * 1000
      }));
      
      // Salvar
      localStorage.setItem('discador_token', token);
      localStorage.setItem('discador_user', JSON.stringify(authenticatedUser));
      
      setUser(authenticatedUser);
      setLoading(false);
      
      console.log('💾 Usuário salvo:', authenticatedUser);
      
      return {
        success: true,
        message: `Login realizado com sucesso como ${userConfig.name}`
      };
    } else {
      console.log('❌ LOGIN NEGADO - Credenciais inválidas');
      const errorMsg = 'Usuário ou senha incorretos';
      setError(errorMsg);
      setLoading(false);
      return {
        success: false,
        error: errorMsg
      };
    }
  };

  /**
   * Hacer logout
   */
  const logout = () => {
    localStorage.removeItem('discador_token');
    localStorage.removeItem('discador_user');
    setUser(null);
    setError(null);
  };

  /**
   * Verificar si usuario tiene permiso
   */
  const hasPermission = (requiredRole) => {
    if (!user) return false;
    
    const roleHierarchy = {
      'admin': 4,
      'supervisor': 3,
      'operator': 2,
      'demo': 1
    };

    const userLevel = roleHierarchy[user.role] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;
    
    return userLevel >= requiredLevel;
  };

  /**
   * Obtener información del usuario
   */
  const getUser = () => user;

  /**
   * Actualizar información del usuario
   */
  const updateUser = (userData) => {
    const updatedUser = { ...user, ...userData };
    setUser(updatedUser);
    localStorage.setItem('discador_user', JSON.stringify(updatedUser));
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    hasPermission,
    getUser,
    updateUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 