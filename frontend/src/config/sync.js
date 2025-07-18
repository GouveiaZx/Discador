/**
 * Configuração de sincronização para o painel Discador
 * Resolve problemas de sincronização entre frontend e backend
 */

import { makeApiRequest } from './api.js';

// Configurações de sincronização
export const SYNC_CONFIG = {
  // Intervalos de atualização (em ms)
  CAMPAIGN_REFRESH_INTERVAL: 15000, // 15 segundos
  STATS_REFRESH_INTERVAL: 10000,    // 10 segundos
  CALLS_REFRESH_INTERVAL: 5000,     // 5 segundos
  
  // Timeouts para operações
  OPERATION_TIMEOUT: 30000,         // 30 segundos
  DELETE_TIMEOUT: 45000,            // 45 segundos para exclusões
  
  // Retry configuration
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000,                // 1 segundo
  
  // Cache TTL
  CACHE_TTL: 30000,                 // 30 segundos
};

// Cache para evitar requisições desnecessárias
class SyncCache {
  constructor() {
    this.cache = new Map();
    this.timestamps = new Map();
  }
  
  set(key, value, ttl = SYNC_CONFIG.CACHE_TTL) {
    this.cache.set(key, value);
    this.timestamps.set(key, Date.now() + ttl);
  }
  
  get(key) {
    const timestamp = this.timestamps.get(key);
    if (!timestamp || Date.now() > timestamp) {
      this.cache.delete(key);
      this.timestamps.delete(key);
      return null;
    }
    return this.cache.get(key);
  }
  
  clear(pattern = null) {
    if (pattern) {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key);
          this.timestamps.delete(key);
        }
      }
    } else {
      this.cache.clear();
      this.timestamps.clear();
    }
  }
}

const syncCache = new SyncCache();

// Utilitário para retry de operações
export const withRetry = async (operation, maxRetries = SYNC_CONFIG.MAX_RETRIES) => {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;

      
      if (attempt < maxRetries) {
        await new Promise(resolve => 
          setTimeout(resolve, SYNC_CONFIG.RETRY_DELAY * attempt)
        );
      }
    }
  }
  
  throw lastError;
};

// Serviço de sincronização de campanhas
export class CampaignSyncService {
  constructor() {
    this.isRefreshing = false;
    this.refreshPromise = null;
  }
  
  /**
   * Lista campanhas com cache e retry
   */
  async listCampaigns(forceRefresh = false) {
    const cacheKey = 'campaigns_list';
    
    if (!forceRefresh) {
      const cached = syncCache.get(cacheKey);
      if (cached) {
    
        return cached;
      }
    }
    
    // Evitar múltiplas requisições simultâneas
    if (this.isRefreshing && this.refreshPromise) {

      return await this.refreshPromise;
    }
    
    this.isRefreshing = true;
    this.refreshPromise = this._fetchCampaigns();
    
    try {
      const campaigns = await this.refreshPromise;
      syncCache.set(cacheKey, campaigns);
      return campaigns;
    } finally {
      this.isRefreshing = false;
      this.refreshPromise = null;
    }
  }
  
  async _fetchCampaigns() {
    return await withRetry(async () => {
  
      const response = await makeApiRequest('/presione1/campanhas');
      
      // Normalizar dados das campanhas
      const campaigns = Array.isArray(response) ? response : (response.data || []);
      
      return campaigns.map(campaign => ({
        ...campaign,
        id: campaign.id,
        name: campaign.nombre || campaign.name,
        description: campaign.descripcion || campaign.description,
        status: campaign.activa ? 'active' : (campaign.pausada ? 'paused' : 'draft'),
        isActive: campaign.activa || false,
        isPaused: campaign.pausada || false,
        created_at: campaign.fecha_creacion || campaign.created_at,
        updated_at: campaign.fecha_actualizacion || campaign.updated_at
      }));
    });
  }
  
  /**
   * Cria uma nova campanha com validação
   */
  async createCampaign(campaignData) {
    return await withRetry(async () => {
    
      
      const response = await makeApiRequest('/campaigns', 'POST', campaignData);
      
      // Validar resposta
      if (!response || !response.id) {
        throw new Error('Resposta inválida do servidor ao criar campanha');
      }
      
      // Limpar cache para forçar refresh
      syncCache.clear('campaigns');
      
      return response;
    });
  }
  
  /**
   * Atualiza uma campanha existente
   */
  async updateCampaign(campaignId, updateData) {
    return await withRetry(async () => {
    
      
      const response = await makeApiRequest(`/campaigns/${campaignId}`, 'PUT', updateData);
      
      // Validar resposta
      if (!response || !response.id) {
        throw new Error('Resposta inválida do servidor ao atualizar campanha');
      }
      
      // Limpar cache
      syncCache.clear('campaigns');
      syncCache.clear(`campaign_${campaignId}`);
      
      return response;
    });
  }
  
  /**
   * Exclui uma campanha com método otimizado
   */
  async deleteCampaign(campaignId) {
    return await withRetry(async () => {
    
      
      try {
        // Tentar endpoint otimizado primeiro
        const response = await makeApiRequest(
          `/presione1/campanhas/${campaignId}`, 
          'DELETE'
        );
        
        if (response && response.success) {
      
          
          // Limpar cache
          syncCache.clear('campaigns');
          syncCache.clear(`campaign_${campaignId}`);
          
          return response;
        }
      } catch (error) {
    
        
        // Fallback para endpoint tradicional
        const fallbackResponse = await makeApiRequest(
          `/campaigns/${campaignId}`, 
          'DELETE'
        );
        
    
        
        // Limpar cache
        syncCache.clear('campaigns');
        syncCache.clear(`campaign_${campaignId}`);
        
        return {
          success: true,
          message: 'Campanha excluída com sucesso (método alternativo)',
          method: 'fallback'
        };
      }
    }, 2); // Menos tentativas para delete
  }
  
  /**
   * Controla status da campanha (iniciar/pausar/parar)
   */
  async controlCampaign(campaignId, action, data = {}) {
    return await withRetry(async () => {
    
      
      const endpoint = `/presione1/campanhas/${campaignId}/${action}`;
      const response = await makeApiRequest(endpoint, 'POST', data);
      
      // Limpar cache para refletir mudanças
      syncCache.clear('campaigns');
      syncCache.clear(`campaign_${campaignId}`);
      
      return response;
    });
  }
  
  /**
   * Obtém estatísticas de uma campanha
   */
  async getCampaignStats(campaignId, useCache = true) {
    const cacheKey = `campaign_stats_${campaignId}`;
    
    if (useCache) {
      const cached = syncCache.get(cacheKey);
      if (cached) {
        return cached;
      }
    }
    
    const stats = await withRetry(async () => {
      const response = await makeApiRequest(`/presione1/campanhas/${campaignId}/estatisticas`);
      return response;
    });
    
    syncCache.set(cacheKey, stats, SYNC_CONFIG.STATS_REFRESH_INTERVAL);
    return stats;
  }
  
  /**
   * Limpa todo o cache
   */
  clearCache() {
    syncCache.clear();
  
  }
}

// Instância singleton
export const campaignSync = new CampaignSyncService();

// Utilitários para debugging
export const debugSync = {
  getCacheInfo: () => {
    return {
      cacheSize: syncCache.cache.size,
      cacheKeys: Array.from(syncCache.cache.keys()),
      timestamps: Array.from(syncCache.timestamps.entries()).map(([key, timestamp]) => ({
        key,
        expiresAt: new Date(timestamp).toISOString(),
        isExpired: Date.now() > timestamp
      }))
    };
  },
  
  clearCache: () => {
    syncCache.clear();
  
  },
  
  testConnection: async () => {
    try {
      const start = Date.now();
      await makeApiRequest('/presione1/campanhas');
      const duration = Date.now() - start;
      
      return {
        success: true,
        duration,
        message: `Conexão OK (${duration}ms)`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        message: 'Falha na conexão'
      };
    }
  }
};

// Expor para debug no console
if (typeof window !== 'undefined') {
  window.debugSync = debugSync;
  window.campaignSync = campaignSync;
}

export default {
  SYNC_CONFIG,
  CampaignSyncService,
  campaignSync,
  withRetry,
  debugSync
};