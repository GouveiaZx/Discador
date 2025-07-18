import { createClient } from '@supabase/supabase-js';

// Configuração do Supabase
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {

}

// Criar cliente Supabase
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
});

// Funções utilitárias para autenticação
export const auth = {
  // Login com email e senha
  signIn: async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });
    return { data, error };
  },

  // Registro de novo usuário
  signUp: async (email, password, metadata = {}) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata
      }
    });
    return { data, error };
  },

  // Logout
  signOut: async () => {
    const { error } = await supabase.auth.signOut();
    return { error };
  },

  // Obter usuário atual
  getCurrentUser: () => {
    return supabase.auth.getUser();
  },

  // Obter sessão atual
  getCurrentSession: () => {
    return supabase.auth.getSession();
  },

  // Escutar mudanças de autenticação
  onAuthStateChange: (callback) => {
    return supabase.auth.onAuthStateChange(callback);
  }
};

// Funções utilitárias para banco de dados
export const database = {
  // Inserir dados
  insert: async (table, data) => {
    const { data: result, error } = await supabase
      .from(table)
      .insert(data)
      .select();
    return { data: result, error };
  },

  // Buscar dados
  select: async (table, columns = '*', filters = {}) => {
    let query = supabase.from(table).select(columns);
    
    // Aplicar filtros
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        query = query.in(key, value);
      } else {
        query = query.eq(key, value);
      }
    });
    
    const { data, error } = await query;
    return { data, error };
  },

  // Atualizar dados
  update: async (table, data, filters = {}) => {
    let query = supabase.from(table).update(data);
    
    // Aplicar filtros
    Object.entries(filters).forEach(([key, value]) => {
      query = query.eq(key, value);
    });
    
    const { data: result, error } = await query.select();
    return { data: result, error };
  },

  // Deletar dados
  delete: async (table, filters = {}) => {
    let query = supabase.from(table).delete();
    
    // Aplicar filtros
    Object.entries(filters).forEach(([key, value]) => {
      query = query.eq(key, value);
    });
    
    const { data, error } = await query;
    return { data, error };
  }
};

// Funções utilitárias para storage
export const storage = {
  // Upload de arquivo
  upload: async (bucket, path, file) => {
    const { data, error } = await supabase.storage
      .from(bucket)
      .upload(path, file);
    return { data, error };
  },

  // Download de arquivo
  download: async (bucket, path) => {
    const { data, error } = await supabase.storage
      .from(bucket)
      .download(path);
    return { data, error };
  },

  // Obter URL pública
  getPublicUrl: (bucket, path) => {
    const { data } = supabase.storage
      .from(bucket)
      .getPublicUrl(path);
    return data.publicUrl;
  },

  // Deletar arquivo
  remove: async (bucket, paths) => {
    const { data, error } = await supabase.storage
      .from(bucket)
      .remove(paths);
    return { data, error };
  }
};

// Funções utilitárias para realtime
export const realtime = {
  // Escutar mudanças em uma tabela
  subscribe: (table, callback, filters = {}) => {
    let channel = supabase
      .channel(`public:${table}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: table,
          ...filters
        },
        callback
      )
      .subscribe();
    
    return channel;
  },

  // Cancelar inscrição
  unsubscribe: (channel) => {
    return supabase.removeChannel(channel);
  }
};



export default supabase;