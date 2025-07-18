import React, { createContext, useContext, useState, useEffect } from 'react';
import { auth, supabase } from '../config/supabase';

const SupabaseAuthContext = createContext(null);

export const useSupabaseAuth = () => {
  const context = useContext(SupabaseAuthContext);
  if (!context) {
    throw new Error('useSupabaseAuth debe ser usado dentro de un SupabaseAuthProvider');
  }
  return context;
};

export const SupabaseAuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Obtener sesión inicial
    const getInitialSession = async () => {
      try {
        const { data: { session }, error } = await auth.getCurrentSession();
        if (error) {
        } else {
          setSession(session);
          setUser(session?.user || null);
        }
      } catch (err) {
      } finally {
        setLoading(false);
      }
    };

    getInitialSession();

    // Escuchar cambios de autenticación
    const { data: { subscription } } = auth.onAuthStateChange(
      async (event, session) => {
        setSession(session);
        setUser(session?.user || null);
        setLoading(false);
      }
    );

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  /**
   * Hacer login con email y contraseña
   */
  const signIn = async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const { data, error } = await auth.signIn(email, password);
      
      if (error) {
        setError(error.message);
        return {
          success: false,
          error: error.message
        };
      }

      return {
          success: true,
          message: 'Login realizado con éxito',
        user: data.user,
        session: data.session
      };
    } catch (err) {
      const errorMessage = err.message || 'Error al hacer login';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Registrar nuevo usuario
   */
  const signUp = async (email, password, metadata = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const { data, error } = await auth.signUp(email, password, metadata);
      
      if (error) {
        setError(error.message);
        return {
          success: false,
          error: error.message
        };
      }

      return {
          success: true,
          message: 'Usuario registrado con éxito. Verifique su email.',
        user: data.user
      };
    } catch (err) {
      const errorMessage = err.message || 'Error al registrar usuario';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Hacer logout
   */
  const signOut = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const { error } = await auth.signOut();
      
      if (error) {
        setError(error.message);
        return {
          success: false,
          error: error.message
        };
      }

      return {
          success: true,
          message: 'Logout realizado con éxito'
        };
    } catch (err) {
      const errorMessage = err.message || 'Error al hacer logout';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Verificar si usuario tiene permiso basado en metadata
   */
  const hasPermission = (requiredRole) => {
    if (!user) return false;
    
    const userRole = user.user_metadata?.role || 'demo';
    
    const roleHierarchy = {
      'admin': 4,
      'supervisor': 3,
      'operator': 2,
      'demo': 1
    };

    const userLevel = roleHierarchy[userRole] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;
    
    return userLevel >= requiredLevel;
  };

  /**
   * Obtener perfil del usuario
   */
  const getUserProfile = () => {
    if (!user) return null;
    
    return {
      id: user.id,
      email: user.email,
      name: user.user_metadata?.name || user.email,
      role: user.user_metadata?.role || 'demo',
      avatar_url: user.user_metadata?.avatar_url,
      created_at: user.created_at,
      last_sign_in_at: user.last_sign_in_at
    };
  };

  /**
   * Actualizar perfil del usuario
   */
  const updateProfile = async (updates) => {
    setLoading(true);
    setError(null);
    
    try {
      const { data, error } = await supabase.auth.updateUser({
        data: updates
      });
      
      if (error) {
        setError(error.message);
        return {
          success: false,
          error: error.message
        };
      }

      return {
          success: true,
          message: 'Perfil actualizado con éxito',
        user: data.user
      };
    } catch (err) {
      const errorMessage = err.message || 'Error al actualizar perfil';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Resetear contraseña
   */
  const resetPassword = async (email) => {
    setLoading(true);
    setError(null);
    
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`
      });
      
      if (error) {
        setError(error.message);
        return {
          success: false,
          error: error.message
        };
      }

      return {
          success: true,
          message: 'Email de recuperación enviado con éxito'
        };
    } catch (err) {
      const errorMessage = err.message || 'Error al enviar email de recuperación';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    session,
    loading,
    error,
    signIn,
    signUp,
    signOut,
    hasPermission,
    getUserProfile,
    updateProfile,
    resetPassword,
    // Aliases para compatibilidad
    login: signIn,
    logout: signOut,
    getUser: getUserProfile
  };

  return (
    <SupabaseAuthContext.Provider value={value}>
      {children}
    </SupabaseAuthContext.Provider>
  );
};

export default SupabaseAuthProvider;