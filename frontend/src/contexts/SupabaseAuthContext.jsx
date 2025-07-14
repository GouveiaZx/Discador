import React, { createContext, useContext, useState, useEffect } from 'react';
import { auth, supabase } from '../config/supabase';

const SupabaseAuthContext = createContext(null);

export const useSupabaseAuth = () => {
  const context = useContext(SupabaseAuthContext);
  if (!context) {
    throw new Error('useSupabaseAuth deve ser usado dentro de um SupabaseAuthProvider');
  }
  return context;
};

export const SupabaseAuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Obter sessão inicial
    const getInitialSession = async () => {
      try {
        const { data: { session }, error } = await auth.getCurrentSession();
        if (error) {
          console.error('Erro ao obter sessão inicial:', error);
        } else {
          setSession(session);
          setUser(session?.user || null);
        }
      } catch (err) {
        console.error('Erro ao verificar sessão:', err);
      } finally {
        setLoading(false);
      }
    };

    getInitialSession();

    // Escutar mudanças de autenticação
    const { data: { subscription } } = auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email);
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
   * Fazer login com email e senha
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
        message: 'Login realizado com sucesso',
        user: data.user,
        session: data.session
      };
    } catch (err) {
      const errorMessage = err.message || 'Erro ao fazer login';
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
   * Registrar novo usuário
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
        message: 'Usuário registrado com sucesso. Verifique seu email.',
        user: data.user
      };
    } catch (err) {
      const errorMessage = err.message || 'Erro ao registrar usuário';
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
   * Fazer logout
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
        message: 'Logout realizado com sucesso'
      };
    } catch (err) {
      const errorMessage = err.message || 'Erro ao fazer logout';
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
   * Verificar se usuário tem permissão baseado em metadata
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
   * Obter perfil do usuário
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
   * Atualizar perfil do usuário
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
        message: 'Perfil atualizado com sucesso',
        user: data.user
      };
    } catch (err) {
      const errorMessage = err.message || 'Erro ao atualizar perfil';
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
   * Resetar senha
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
        message: 'Email de recuperação enviado com sucesso'
      };
    } catch (err) {
      const errorMessage = err.message || 'Erro ao enviar email de recuperação';
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
    // Aliases para compatibilidade
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