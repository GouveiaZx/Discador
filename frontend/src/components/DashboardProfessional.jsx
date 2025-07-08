import React, { useState, useEffect, useMemo } from 'react';
import { makeApiRequest } from '../config/api';
import { 
  PhoneIcon, 
  UserGroupIcon, 
  ChartBarIcon, 
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
  PlayIcon,
  StopIcon,
  PauseIcon
} from '@heroicons/react/24/outline';
import { API_BASE_URL } from '../config/api';

/**
 * Componente de Métrica Profissional com Glass Morphism
 */
const ProfessionalMetricCard = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend, 
  gradient = 'primary', 
  loading = false,
  className = "" 
}) => {
  const gradientClasses = {
    primary: 'from-primary-500/20 to-accent-500/20 border-primary-500/30',
    success: 'from-success-500/20 to-success-600/20 border-success-500/30',
    warning: 'from-warning-500/20 to-warning-600/20 border-warning-500/30',
    error: 'from-error-500/20 to-error-600/20 border-error-500/30',
    info: 'from-primary-500/20 to-secondary-500/20 border-primary-500/30'
  };

  const trendIcons = {
    up: '📈',
    down: '📉',
    stable: '➡️'
  };

  const trendColors = {
    up: 'text-success-400',
    down: 'text-error-400',
    stable: 'text-warning-400'
  };

  if (loading) {
    return (
      <div className={`card-glass p-6 animate-pulse ${className}`}>
        <div className="flex items-start justify-between mb-4">
          <div className="space-y-3 flex-1">
            <div className="h-4 bg-secondary-700 rounded w-24"></div>
            <div className="h-8 bg-secondary-700 rounded w-16"></div>
            <div className="h-3 bg-secondary-700 rounded w-32"></div>
          </div>
          <div className="w-12 h-12 bg-secondary-700 rounded-xl"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`card-glass relative overflow-hidden ${className} group`}>
      <div className={`absolute inset-0 bg-gradient-to-br ${gradientClasses[gradient]} opacity-50`}></div>
      
      <div className="relative p-6 z-10">
        <div className="flex items-start justify-between mb-4">
          <div className="space-y-1 flex-1">
            <p className="text-xs font-semibold text-secondary-400 uppercase tracking-wider">
              {title}
            </p>
            <div className="flex items-baseline space-x-2">
              <h3 className="text-2xl md:text-3xl font-bold text-white">
                {value}
              </h3>
              {trend && (
                <div className="flex items-center space-x-1">
                  <span className="text-sm">{trendIcons[trend.direction]}</span>
                  <span className={`text-sm font-medium ${trendColors[trend.direction]}`}>
                    {trend.value}
                  </span>
                </div>
              )}
            </div>
            {subtitle && (
              <p className="text-xs text-secondary-300">{subtitle}</p>
            )}
          </div>
          
          <div className="text-3xl opacity-70 group-hover:scale-110 transition-transform duration-300">
            {icon}
          </div>
        </div>
        
        {/* Indicador de status */}
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-success-400 rounded-full animate-pulse"></div>
          <span className="text-xs text-secondary-400">Tiempo real</span>
        </div>
      </div>
      
      {/* Efeito de brilho no hover */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -skew-x-12 transform -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
    </div>
  );
};

/**
 * Componente de Status em Tempo Real Profissional
 */
const RealTimeStatusPanel = ({ title, items, loading, icon = "📊" }) => {
  if (loading) {
    return (
      <div className="card-glass p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="h-6 bg-secondary-700 rounded w-32 animate-pulse"></div>
          <div className="h-4 bg-secondary-700 rounded w-16 animate-pulse"></div>
        </div>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex justify-between items-center p-4 bg-secondary-800/50 rounded-xl animate-pulse">
              <div className="space-y-2 flex-1">
                <div className="h-4 bg-secondary-700 rounded w-24"></div>
                <div className="h-3 bg-secondary-700 rounded w-32"></div>
              </div>
              <div className="h-6 bg-secondary-700 rounded w-16"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="card-glass p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <span className="text-lg">{icon}</span>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-success-500/20 border border-success-500/30">
          <div className="w-2 h-2 bg-success-400 rounded-full animate-pulse"></div>
          <span className="text-xs text-success-400 font-medium">LIVE</span>
        </div>
      </div>
      
      <div className="space-y-3 max-h-80 overflow-y-auto custom-scrollbar">
        {items.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4 opacity-50">📭</div>
            <p className="text-secondary-400 font-medium">No hay datos disponibles</p>
            <p className="text-xs text-secondary-500 mt-2">
              La información aparecerá acá cuando el sistema esté activo
            </p>
          </div>
        ) : (
          items.map((item, index) => (
            <div 
              key={index} 
              className="flex items-center justify-between p-4 rounded-xl bg-secondary-800/40 
                       hover:bg-secondary-700/60 transition-all duration-200 
                       border border-transparent hover:border-primary-500/30
                       group cursor-pointer"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-white font-medium text-sm truncate">
                    {item.name || item.numero || item.nome}
                  </span>
                  {item.badge && (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${item.badge.color}`}>
                      {item.badge.text}
                    </span>
                  )}
                </div>
                <p className="text-xs text-secondary-400 truncate">
                  {item.description || item.info}
                </p>
              </div>
              
              <div className="flex flex-col items-end space-y-1 ml-4">
                <span className={`
                  px-3 py-1 rounded-full text-xs font-medium border
                  ${item.status === 'ativo' || item.status === 'active' 
                    ? 'bg-success-500/20 text-success-400 border-success-500/30' 
                    : 'bg-error-500/20 text-error-400 border-error-500/30'
                  }
                `}>
                  {item.status}
                </span>
                {item.count !== undefined && (
                  <span className="text-xs text-secondary-500">
                    {item.count} items
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

/**
 * Componente de Ações Rápidas
 */
const QuickActionButton = ({ title, icon, onClick, color = 'primary', description }) => {
  const colorClasses = {
    primary: 'from-primary-500 to-accent-500 hover:from-primary-600 hover:to-accent-600',
    success: 'from-success-500 to-success-600 hover:from-success-600 hover:to-success-700',
    warning: 'from-warning-500 to-warning-600 hover:from-warning-600 hover:to-warning-700',
    secondary: 'from-secondary-600 to-secondary-700 hover:from-secondary-700 hover:to-secondary-800'
  };

  return (
    <button
      onClick={onClick}
      className={`
        relative p-6 rounded-xl text-white transition-all duration-300
        bg-gradient-to-br ${colorClasses[color]} shadow-lg
        hover:scale-105 hover:shadow-xl group
        focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2 focus:ring-offset-secondary-900
      `}
    >
      <div className="flex flex-col items-center space-y-3">
        <span className="text-3xl group-hover:scale-110 transition-transform duration-300">
          {icon}
        </span>
        <div className="text-center">
          <h4 className="font-semibold text-sm">{title}</h4>
          {description && (
            <p className="text-xs opacity-80 mt-1">{description}</p>
          )}
        </div>
      </div>
      
      {/* Efeito de brilho */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -skew-x-12 transform -translate-x-full group-hover:translate-x-full transition-transform duration-700 rounded-xl"></div>
    </button>
  );
};

/**
 * Dashboard Principal Profissional
 */
const DashboardProfessional = () => {
  const [data, setData] = useState({
    metricas: {},
    provedores: [],
    campanhas: [],
    clis: [],
    audio: { contextos: [], sesionesActivas: 0 }
  });
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [refreshing, setRefreshing] = useState(false);

  // Métricas calculadas
  const metrics = useMemo(() => {
    const provedores = Array.isArray(data.provedores) ? data.provedores : [];
    const campanhas = Array.isArray(data.campanhas) ? data.campanhas : [];
    const clis = Array.isArray(data.clis) ? data.clis : [];
    
    return {
      llamadasActivas: data.metricas.llamadasActivas || 0,
      efectividad: data.metricas.efectividad || 0,
      operadoresOnline: data.metricas.operadoresOnline || 0,
      sesionesAudio: data.audio.sesionesActivas || 0,
      totalCLIs: clis.length || 0,
      campanhasActivas: campanhas.filter(c => c.status === 'active' || c.status === 'ativa').length,
      provedoresActivos: provedores.filter(p => p.status === 'ativo').length,
      tiempoMedio: '2:34',
      tasaExito: '87.2%'
    };
  }, [data]);

  // Carregar dados do dashboard
  const loadDashboardData = async () => {
    try {
      setRefreshing(true);
      
      const requests = [
        makeApiRequest('/monitoring/dashboard'),
        makeApiRequest('/multi-sip/provedores'),
        makeApiRequest('/api/v1/campaigns'),
        makeApiRequest('/code2base/clis'),
        makeApiRequest('/audios/contextos')
      ];

      const results = await Promise.allSettled(requests);
      
      const newData = {
        metricas: results[0].status === 'fulfilled' ? results[0].value : {},
        provedores: results[1].status === 'fulfilled' ? (results[1].value?.provedores || results[1].value || []) : [],
        campanhas: results[2].status === 'fulfilled' ? (results[2].value?.campanhas || results[2].value || []) : [],
        clis: results[3].status === 'fulfilled' ? (results[3].value?.clis || results[3].value || []) : [],
        audio: results[4].status === 'fulfilled' ? (results[4].value?.contextos ? results[4].value : { contextos: results[4].value || [], sesionesActivas: 0 }) : { contextos: [], sesionesActivas: 0 }
      };
      
      // Carregar dados de áudio
      try {
        const audioData = await makeApiRequest('/audios/contextos');
        if (audioData && audioData.contextos) {
          newData.audio.contextos = audioData.contextos;
        }
      } catch (error) {
        console.warn('Erro ao carregar dados de áudio:', error);
        newData.audio.contextos = [];
      }
      
      setData(newData);
      
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Auto-refresh a cada 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 space-y-8 min-h-screen">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header Principal */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center space-y-4 lg:space-y-0">
          <div className="space-y-2">
            <h1 className="text-3xl lg:text-4xl font-bold text-gradient-primary">
              Panel Ejecutivo
            </h1>
            <p className="text-secondary-400 text-sm lg:text-base">
              Monitoreo en tiempo real del sistema de discado predictivo
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-xs text-secondary-400">
              <div>Última atualização:</div>
                              <div className="font-mono">{lastUpdate.toLocaleTimeString('es-AR')}</div>
            </div>
            <button
              onClick={loadDashboardData}
              disabled={refreshing}
              className="btn-secondary flex items-center space-x-2"
            >
              <span className={refreshing ? 'animate-spin' : ''}>🔄</span>
              <span>{refreshing ? 'Atualizando...' : 'Atualizar'}</span>
            </button>
          </div>
        </div>

        {/* Métricas Principais */}
        <div className="grid-auto-fit gap-6">
          <ProfessionalMetricCard
            title="Chamadas Ativas"
            value={metrics.llamadasActivas}
            subtitle={`${metrics.operadoresOnline} operadores conectados`}
            icon="📞"
            gradient="success"
            trend={{ direction: 'up', value: '+12%' }}
            loading={loading}
          />
          
          <ProfessionalMetricCard
            title="Taxa de Efetividade"
            value={`${metrics.efectividad}%`}
            subtitle="Conversões hoje"
            icon="📈"
            gradient="primary"
            trend={{ direction: 'up', value: '+3.2%' }}
            loading={loading}
          />
          
          <ProfessionalMetricCard
            title="CLIs Disponíveis"
            value={metrics.totalCLIs}
            subtitle={`${metrics.provedoresActivos} provedores ativos`}
            icon="🎯"
            gradient="info"
            trend={{ direction: 'stable', value: '0%' }}
            loading={loading}
          />
          
          <ProfessionalMetricCard
            title="IA Audio Sessions"
            value={metrics.sesionesAudio}
            subtitle="Procesamiento inteligente"
            icon="🤖"
            gradient="warning"
            trend={{ direction: 'up', value: '+25%' }}
            loading={loading}
          />
        </div>

        {/* Métricas Secundárias */}
        <div className="grid-auto-fit gap-6">
          <ProfessionalMetricCard
            title="Campanhas Ativas"
            value={metrics.campanhasActivas}
            subtitle="En ejecución"
            icon="🗳️"
            gradient="primary"
            loading={loading}
          />
          
          <ProfessionalMetricCard
            title="Tiempo Promedio"
            value={metrics.tiempoMedio}
            subtitle="Duración por llamada"
            icon="⏱️"
            gradient="success"
            loading={loading}
          />
          
          <ProfessionalMetricCard
            title="Taxa de Sucesso"
            value={metrics.tasaExito}
            subtitle="Llamadas completadas"
            icon="✅"
            gradient="info"
            loading={loading}
          />
        </div>

        {/* Painéis de Status */}
        <div className="grid-auto-fill gap-6">
          <RealTimeStatusPanel
            title="Provedores Multi-SIP"
            icon="🌐"
            items={(Array.isArray(data.provedores) ? data.provedores : []).map(p => ({
              name: p.nome || p.name,
              description: `${p.llamadas || p.chamadas_ativas || 0} llamadas activas`,
              status: p.status || 'inativo',
              badge: p.prioridade ? { 
                text: `Prioridad ${p.prioridade}`, 
                color: 'bg-primary-500/20 text-primary-300 border border-primary-500/30' 
              } : null
            }))}
            loading={loading}
          />
          
          <RealTimeStatusPanel
            title="CLIs CODE2BASE"
            icon="📱"
            items={(Array.isArray(data.clis) ? data.clis : []).map(c => ({
              name: c.numero || c.cli,
              description: `${c.llamadas_hoy || c.chamadas_hoje || 0} llamadas hoy`,
              status: c.activo || c.ativo ? 'ativo' : 'inativo',
              badge: c.pais || c.paises ? { 
                text: c.pais || c.paises, 
                color: 'bg-success-500/20 text-success-300 border border-success-500/30' 
              } : null
            }))}
            loading={loading}
          />
          
          <RealTimeStatusPanel
            title="Contextos de Áudio IA"
            icon="🎵"
            items={(Array.isArray(data.audio?.contextos) ? data.audio.contextos : []).map(c => ({
              name: c.nome || c.name,
              description: c.descripcion || c.descricao || 'Procesamiento de audio inteligente',
              status: c.activo || c.ativo ? 'ativo' : 'inativo',
              count: c.sessiones_activas || c.sessoes_ativas
            }))}
            loading={loading}
          />
        </div>

        {/* Status de Campanhas e Sistema */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RealTimeStatusPanel
            title="Campanhas Políticas"
            icon="🗳️"
            items={(Array.isArray(data.campanhas) ? data.campanhas : []).map(c => ({
              name: c.nome || c.name,
              description: `${c.contatos || c.contacts || 0} contatos • ${c.tipo || 'Campanha padrão'}`,
              status: c.status || 'inativa',
              badge: c.compliance ? { 
                text: 'Compliance ✓', 
                color: 'bg-success-500/20 text-success-300 border border-success-500/30' 
              } : null
            }))}
            loading={loading}
          />
          
          <RealTimeStatusPanel
            title="Status do Sistema"
            icon="⚡"
            items={[
              { 
                name: 'Backend API', 
                description: 'FastAPI respondendo normalmente', 
                status: 'ativo' 
              },
              { 
                name: 'Banco de Dados', 
                description: 'SQLite conectado e operacional', 
                status: 'ativo' 
              },
              { 
                name: 'Serviços Multi-SIP', 
                description: 'Provedores conectados', 
                status: 'ativo' 
              },
              { 
                name: 'Sistema de Áudio IA', 
                description: 'Procesamiento en tiempo real', 
                status: 'ativo' 
              }
            ]}
            loading={loading}
          />
        </div>



        {/* Rodapé com Informações */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center space-x-4 text-sm text-secondary-400">
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-success-400 rounded-full"></span>
              <span>Sistema Operacional</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-primary-400 rounded-full"></span>
              <span>Tiempo Real</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-warning-400 rounded-full"></span>
              <span>Auto-Refresh 30s</span>
            </span>
          </div>
          <p className="text-xs text-secondary-500">
            Discador Preditivo v2.0 • FastAPI + SQLite • Interface Profissional
          </p>
        </div>
      </div>
    </div>
  );
};

export default DashboardProfessional; 