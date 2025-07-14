import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { makeApiRequest } from '../config/api';

const CampaignContext = createContext(null);

export const useCampaigns = () => {
  const context = useContext(CampaignContext);
  if (!context) {
    throw new Error('useCampaigns deve ser usado dentro de um CampaignProvider');
  }
  return context;
};

export const CampaignProvider = ({ children }) => {
  const [campaigns, setCampaigns] = useState([]);
  const [activeCampaigns, setActiveCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Intervalo de atualização automática (30 segundos)
  const REFRESH_INTERVAL = 30000;

  /**
   * Buscar campanhas do servidor
   */
  const fetchCampaigns = useCallback(async () => {
    try {
      setError(null);
      console.log('🔄 [CampaignContext] Buscando campanhas...');
      
      const response = await makeApiRequest('/presione1/campanhas');
      const campaignsData = Array.isArray(response) ? response : (response.data || []);
      
      console.log('✅ [CampaignContext] Campanhas carregadas:', campaignsData.length);
      
      // Enriquecer dados das campanhas com informações das campanhas principais
      const enrichedCampaigns = await Promise.all(
        campaignsData.map(async (campaign) => {
          try {
            // Buscar dados da campanha principal se existir campaign_id
            if (campaign.campaign_id) {
              const mainCampaignsResponse = await makeApiRequest('/campaigns');
              const mainCampaigns = mainCampaignsResponse?.campaigns || [];
              const mainCampaign = mainCampaigns.find(c => c.id === campaign.campaign_id);
              
              return {
                ...campaign,
                // Dados básicos
                id: campaign.id,
                name: campaign.nombre,
                description: campaign.descripcion,
                // Status unificado
                status: campaign.activa ? 'active' : (campaign.pausada ? 'paused' : 'draft'),
                isActive: campaign.activa,
                isPaused: campaign.pausada,
                // Dados da campanha principal
                cli_number: mainCampaign?.cli_number || 'N/A',
                contacts_total: mainCampaign?.contacts_total || 0,
                // Timestamps
                created_at: campaign.fecha_creacion,
                updated_at: campaign.fecha_actualizacion,
                // Configurações específicas presione1
                llamadas_simultaneas: campaign.llamadas_simultaneas || 5,
                tiempo_entre_llamadas: campaign.tiempo_entre_llamadas || 1.0
              };
            }
            
            // Retornar dados básicos se não há campaign_id
            return {
              ...campaign,
              id: campaign.id,
              name: campaign.nombre,
              description: campaign.descripcion,
              status: campaign.activa ? 'active' : (campaign.pausada ? 'paused' : 'draft'),
              isActive: campaign.activa,
              isPaused: campaign.pausada,
              cli_number: 'N/A',
              contacts_total: 0,
              created_at: campaign.fecha_creacion,
              updated_at: campaign.fecha_actualizacion,
              llamadas_simultaneas: campaign.llamadas_simultaneas || 5,
              tiempo_entre_llamadas: campaign.tiempo_entre_llamadas || 1.0
            };
            
          } catch (err) {
            console.warn(`⚠️ [CampaignContext] Erro ao enriquecer campanha ${campaign.id}:`, err);
            return {
              ...campaign,
              name: campaign.nombre,
              status: 'error',
              isActive: false,
              isPaused: false
            };
          }
        })
      );
      
      setCampaigns(enrichedCampaigns);
      
      // Filtrar campanhas ativas
      const active = enrichedCampaigns.filter(campaign => campaign.isActive && !campaign.isPaused);
      setActiveCampaigns(active);
      
      setLastUpdate(new Date());
      console.log(`✅ [CampaignContext] ${active.length} campanhas ativas encontradas`);
      
    } catch (err) {
      console.error('❌ [CampaignContext] Erro ao buscar campanhas:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Atualizar status de uma campanha específica
   */
  const updateCampaignStatus = useCallback((campaignId, newStatus) => {
    setCampaigns(prev => {
      const updated = prev.map(campaign => 
        campaign.id === campaignId 
          ? { 
              ...campaign, 
              status: newStatus,
              isActive: newStatus === 'active',
              isPaused: newStatus === 'paused'
            }
          : campaign
      );
      
      // Atualizar campanhas ativas baseado no estado atualizado
      const active = updated.filter(campaign => campaign.isActive && !campaign.isPaused);
      setActiveCampaigns(active);
      
      return updated;
    });
    
    console.log(`🔄 [CampaignContext] Status da campanha ${campaignId} atualizado para: ${newStatus}`);
  }, []);

  /**
   * Forçar atualização das campanhas
   */
  const refreshCampaigns = useCallback(() => {
    setLoading(true);
    fetchCampaigns();
  }, [fetchCampaigns]);

  /**
   * Obter campanha por ID
   */
  const getCampaignById = useCallback((campaignId) => {
    return campaigns.find(campaign => campaign.id === campaignId);
  }, [campaigns]);

  /**
   * Verificar se há campanhas ativas
   */
  const hasActiveCampaigns = useCallback(() => {
    return activeCampaigns.length > 0;
  }, [activeCampaigns]);

  // Carregar campanhas na inicialização
  useEffect(() => {
    fetchCampaigns();
  }, [fetchCampaigns]);

  // Configurar atualização automática
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('🔄 [CampaignContext] Atualização automática das campanhas');
      fetchCampaigns();
    }, REFRESH_INTERVAL);

    return () => {
      clearInterval(interval);
    };
  }, [fetchCampaigns]);

  const value = {
    // Estados
    campaigns,
    activeCampaigns,
    loading,
    error,
    lastUpdate,
    
    // Métricas
    totalCampaigns: campaigns.length,
    activeCampaignsCount: activeCampaigns.length,
    pausedCampaignsCount: campaigns.filter(c => c.isPaused).length,
    draftCampaignsCount: campaigns.filter(c => c.status === 'draft').length,
    
    // Funções
    fetchCampaigns,
    refreshCampaigns,
    updateCampaignStatus,
    getCampaignById,
    hasActiveCampaigns
  };

  return (
    <CampaignContext.Provider value={value}>
      {children}
    </CampaignContext.Provider>
  );
};