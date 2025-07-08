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
   * Hacer login
   */
  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    
    try {
      // Hacer petición de login al backend
      const response = await makeApiRequest('/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(response.message || 'Usuario o contraseña incorrectos');
      }

      const data = await response.json();
      
      if (data.token && data.user) {
        // Guardar token y usuario en localStorage
        localStorage.setItem('discador_token', data.token);
        localStorage.setItem('discador_user', JSON.stringify(data.user));
        
        setUser(data.user);
        setLoading(false);
        
        return {
          success: true,
          message: 'Login realizado con éxito'
        };
      }
    } catch (err) {
      // Fallback para usuarios estándar durante desarrollo
      console.warn('⚠️ Error en la autenticación vía API, usando fallback local:', err.message);
      
      // Usuarios estándar para desarrollo
      const defaultUsers = [
        { id: 1, username: 'admin', password: 'admin123', role: 'admin', name: 'Administrador' },
        { id: 2, username: 'supervisor', password: 'supervisor123', role: 'supervisor', name: 'Supervisor' },
        { id: 3, username: 'operador', password: 'operador123', role: 'operator', name: 'Operador' },
        { id: 4, username: 'demo', password: 'demo', role: 'demo', name: 'Demo' }
      ];

      console.log('🔍 Tentativa de login:', { username, password });
      console.log('👥 Usuários disponíveis:', defaultUsers);
      
      const foundUser = defaultUsers.find(u => 
        u.username === username && u.password === password
      );

      console.log('✅ Usuário encontrado:', foundUser);

      if (foundUser) {
        // Token simulado
        const fakeToken = btoa(JSON.stringify({
          userId: foundUser.id,
          username: foundUser.username,
          role: foundUser.role,
          exp: Date.now() + 24 * 60 * 60 * 1000 // 24 horas
        }));

        // Remover contraseña y guardar
        const userToSave = {
          id: foundUser.id,
          username: foundUser.username,
          role: foundUser.role,
          name: foundUser.name
        };

        localStorage.setItem('discador_token', fakeToken);
        localStorage.setItem('discador_user', JSON.stringify(userToSave));
        
        setUser(userToSave);
        setLoading(false);
        
        return {
          success: true,
          message: 'Login realizado con éxito (modo fallback)'
        };
      } else {
        setError('Usuario o contraseña incorrectos');
        setLoading(false);
        return {
          success: false,
          error: 'Usuario o contraseña incorrectos'
        };
      }
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