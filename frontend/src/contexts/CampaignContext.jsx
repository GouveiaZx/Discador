import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { makeApiRequest } from '../config/api';
import { campaignSync, SYNC_CONFIG } from '../config/sync';

const CampaignContext = createContext(null);

export const useCampaigns = () => {
  const context = useContext(CampaignContext);
  if (!context) {
    throw new Error('useCampaigns debe ser usado dentro de un CampaignProvider');
  }
  return context;
};

export const CampaignProvider = ({ children }) => {
  const [campaigns, setCampaigns] = useState([]);
  const [activeCampaigns, setActiveCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Intervalo de actualización automática (30 segundos)
  const REFRESH_INTERVAL = 30000;

  /**
   * Buscar campañas del servidor
   */
  const fetchCampaigns = useCallback(async () => {
    try {
      setError(null);

      
      const response = await makeApiRequest('/presione1/campanhas');
      const campaignsData = Array.isArray(response) ? response : (response.data || []);
      

      
      // Enriquecer datos de las campañas con información de las campañas principales
      const enrichedCampaigns = await Promise.all(
        campaignsData.map(async (campaign) => {
          try {
            // Buscar datos de la campaña principal si existe campaign_id
            if (campaign.campaign_id) {
              const mainCampaignsResponse = await makeApiRequest('/campaigns');
              const mainCampaigns = mainCampaignsResponse?.campaigns || [];
              const mainCampaign = mainCampaigns.find(c => c.id === campaign.campaign_id);
              
              return {
                ...campaign,
                // Datos básicos
                id: campaign.id,
                name: campaign.nombre,
                description: campaign.descripcion,
                // Estado unificado
                status: campaign.activa ? 'active' : (campaign.pausada ? 'paused' : 'draft'),
                isActive: campaign.activa,
                isPaused: campaign.pausada,
                // Datos de la campaña principal
                cli_number: mainCampaign?.cli_number || 'N/A',
                contacts_total: mainCampaign?.contacts_total || 0,
                // Timestamps
                created_at: campaign.fecha_creacion,
                updated_at: campaign.fecha_actualizacion,
                // Configuraciones específicas presione1
                llamadas_simultaneas: campaign.llamadas_simultaneas || 5,
                tiempo_entre_llamadas: campaign.tiempo_entre_llamadas || 1.0
              };
            }
            
            // Retornar datos básicos si no hay campaign_id
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
      
      // Filtrar campañas activas
      const active = enrichedCampaigns.filter(campaign => campaign.isActive && !campaign.isPaused);
      setActiveCampaigns(active);
      
      setLastUpdate(new Date());

      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Actualizar estado de una campaña específica
   */
  const updateCampaignStatus = useCallback((campaignId, newStatus) => {
    setCampaigns(prev => {
      const updated = prev.map(campaign => 
        campaign.id === campaignId 
          ? { 
              ...campaign, 
              status: newStatus,
              isActive: newStatus === 'active',
              isPaused: newStatus === 'paused',
              activa: newStatus === 'active',
              pausada: newStatus === 'paused'
            }
          : campaign
      );
      
      // Actualizar campañas activas basado en el estado actualizado
      const active = updated.filter(campaign => campaign.isActive && !campaign.isPaused);
      setActiveCampaigns(active);
      
      return updated;
    });
    
    // Limpiar cache para garantizar sincronización
    campaignSync.clearCache();
    

  }, []);

  /**
   * Forzar actualización de las campañas
   */
  const refreshCampaigns = useCallback(async (forceRefresh = false) => {
    try {
      setLoading(true);

      
      // Usar el nuevo servicio de sincronización
      const campaigns = await campaignSync.listCampaigns(forceRefresh);
      
      setCampaigns(campaigns);

      setError(null); // Limpiar errores anteriores
    } catch (error) {
      setError('Error al cargar campañas: ' + error.message);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Obtener campaña por ID
   */
  const getCampaignById = useCallback((campaignId) => {
    return campaigns.find(campaign => campaign.id === campaignId);
  }, [campaigns]);

  /**
   * Verificar si hay campañas activas
   */
  const hasActiveCampaigns = useCallback(() => {
    return activeCampaigns.length > 0;
  }, [activeCampaigns]);

  // Cargar campañas en la inicialización
  useEffect(() => {
    fetchCampaigns();
  }, [fetchCampaigns]);

  // Configurar actualización automática
  useEffect(() => {
    const interval = setInterval(() => {
      if (!loading) {

        refreshCampaigns(false); // Usar cache cuando sea posible
      }
    }, SYNC_CONFIG.CAMPAIGN_REFRESH_INTERVAL);

    return () => {
      clearInterval(interval);
    };
  }, [loading, refreshCampaigns]);

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
    
    // Funciones
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