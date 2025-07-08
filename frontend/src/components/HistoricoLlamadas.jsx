import React, { useState, useEffect, useCallback } from 'react';
import HistoricoLlamadasTable from './HistoricoLlamadasTable';
import HistoricoFilters from './HistoricoFilters';
import LlamadaDetalle from './LlamadaDetalle';
import SpinnerLoading from './SpinnerLoading';
import { obtenerHistoricoLlamadas, exportarHistoricoCSV } from '../services/llamadasService';

/**
 * Componente de Métrica de Histórico Profissional
 */
const HistoricoMetricCard = ({ title, value, subtitle, icon, trend, color = 'primary', loading = false }) => {
  const colorClasses = {
    primary: 'from-primary-500/20 to-accent-500/20 border-primary-500/30',
    success: 'from-success-500/20 to-success-600/20 border-success-500/30',
    warning: 'from-warning-500/20 to-warning-600/20 border-warning-500/30',
    info: 'from-accent-500/20 to-primary-500/20 border-accent-500/30'
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
      <div className="card-glass p-4 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="space-y-2 flex-1">
            <div className="h-3 bg-secondary-700 rounded w-16"></div>
            <div className="h-6 bg-secondary-700 rounded w-12"></div>
          </div>
          <div className="w-8 h-8 bg-secondary-700 rounded-lg"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="card-glass relative overflow-hidden group">
      <div className={`absolute inset-0 bg-gradient-to-br ${colorClasses[color]} opacity-40`}></div>
      
      <div className="relative p-4 z-10">
        <div className="flex items-center justify-between">
          <div className="space-y-1 flex-1">
            <p className="text-xs font-medium text-secondary-400 uppercase tracking-wider">
              {title}
            </p>
            <h3 className="text-xl font-bold text-white">
              {value}
            </h3>
            {subtitle && (
              <p className="text-xs text-secondary-300">{subtitle}</p>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="text-2xl opacity-70 group-hover:scale-110 transition-transform duration-300">
              {icon}
            </div>
            {trend && (
              <div className="flex items-center space-x-1">
                <span className="text-sm">{trendIcons[trend.direction]}</span>
                <span className={`text-xs font-medium ${trendColors[trend.direction]}`}>
                  {trend.value}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Componente principal para página de historial de llamadas profissional
 */
const HistoricoLlamadas = () => {
  // Estados para almacenar dados e estado da UI
  const [llamadas, setLlamadas] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExporting, setIsExporting] = useState(false);
  
  // Estados para modal de detalhes
  const [selectedLlamadaId, setSelectedLlamadaId] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  
  // Estados para filtros
  const [filters, setFilters] = useState({
    estados: [],
    resultados: [],
    usuario: '',
    fecha_inicio: '',
    fecha_fin: ''
  });
  
  // Lista de usuários para o filtro
  const [usuarios, setUsuarios] = useState([]);
  
  // Estados para métricas
  const [metrics, setMetrics] = useState({
    totalLlamadas: 0,
    completadas: 0,
    fallidas: 0,
    promedioDuracion: '00:00'
  });

  // Preparar parâmetros de filtro para a API
  const prepareApiFilters = useCallback(() => {
    const apiFilters = {};
    
    if (filters.estados && filters.estados.length > 0) {
      apiFilters.estados = filters.estados.join(',');
    }
    
    if (filters.resultados && filters.resultados.length > 0) {
      apiFilters.resultados = filters.resultados.join(',');
    }
    
    if (filters.usuario) {
      apiFilters.usuario = filters.usuario;
    }
    
    if (filters.fecha_inicio) {
      apiFilters.fecha_inicio = filters.fecha_inicio;
    }
    
    if (filters.fecha_fin) {
      apiFilters.fecha_fin = filters.fecha_fin;
    }
    
    return apiFilters;
  }, [filters]);
  
  // Calcular métricas dos dados
  const calcularMetricas = useCallback((llamadasData) => {
    const total = llamadasData.length;
    const completadas = llamadasData.filter(l => l.estado === 'finalizada' || l.estado === 'completada').length;
    const fallidas = llamadasData.filter(l => l.estado === 'fallida' || l.estado === 'error').length;
    
    // Calcular duração média (simulada)
    const duraciones = llamadasData.filter(l => l.duracion).map(l => parseInt(l.duracion) || 0);
    const promedioDuracion = duraciones.length > 0 
      ? Math.round(duraciones.reduce((a, b) => a + b, 0) / duraciones.length)
      : 0;
    
    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    setMetrics({
      totalLlamadas: total,
      completadas,
      fallidas,
      promedioDuracion: formatTime(promedioDuracion)
    });
  }, []);
  
  // Cargar dados da API
  const cargarHistorico = useCallback(async () => {
    setLoading(true);
    try {
      const apiFilters = prepareApiFilters();
      const data = await obtenerHistoricoLlamadas(apiFilters, currentPage, pageSize);
      
      setLlamadas(data.llamadas || []);
      setTotalItems(data.total || 0);
      setTotalPages(Math.ceil((data.total || 0) / pageSize));
      
      // Calcular métricas
      calcularMetricas(data.llamadas || []);
      
      // Extrair lista de usuários únicos para o filtro
      if (data.usuarios && !usuarios.length) {
        const usuariosOptions = data.usuarios.map(usuario => ({
          value: usuario.email,
          label: usuario.nombre ? `${usuario.nombre} (${usuario.email})` : usuario.email
        }));
        setUsuarios(usuariosOptions);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error al obtener historial de llamadas:', err);
      setError('Error al cargar historial de llamadas. Por favor, intentá nuevamente.');
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, prepareApiFilters, usuarios.length, calcularMetricas]);
  
  // Efeito para carregar dados quando a página ou filtros mudarem
  useEffect(() => {
    cargarHistorico();
  }, [cargarHistorico, currentPage, filters]);
  
  // Handler para mudança de página
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };
  
  // Handler para abrir modal de detalhes
  const handleViewDetails = (llamadaId) => {
    setSelectedLlamadaId(llamadaId);
    setDetailModalOpen(true);
  };
  
  // Handler para fechar modal de detalhes
  const handleCloseDetails = () => {
    setDetailModalOpen(false);
  };
  
  // Exportar dados para CSV
  const handleExportCSV = async () => {
    setIsExporting(true);
    try {
      const apiFilters = prepareApiFilters();
      const blob = await exportarHistoricoCSV(apiFilters);
      
      // Criar URL para download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      
      // Nome do arquivo com data atual
      const date = new Date().toISOString().split('T')[0];
      a.download = `historial-llamadas-${date}.csv`;
      
      // Ativar download e limpar
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error al exportar CSV:', err);
      alert('Error al exportar datos a CSV. Por favor, intentá nuevamente.');
    } finally {
      setIsExporting(false);
    }
  };
  
  // Resetar filtros
  const handleResetFilters = () => {
    setFilters({
      estados: [],
      resultados: [],
      usuario: '',
      fecha_inicio: '',
      fecha_fin: ''
    });
    setCurrentPage(1);
  };

  return (
    <div className="p-6 space-y-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header Principal */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center space-y-4 lg:space-y-0">
          <div className="space-y-2">
            <h1 className="text-3xl lg:text-4xl font-bold text-gradient-primary">
              Historial de Llamadas
            </h1>
            <p className="text-secondary-400 text-sm lg:text-base">
              Análisis completo y detallado de todas las comunicaciones
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-xs text-secondary-400">
              <div>Total registros:</div>
              <div className="font-mono text-primary-400">{totalItems.toLocaleString()}</div>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-primary-500/20 border border-primary-500/30">
              <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse"></div>
              <span className="text-xs text-primary-400 font-medium">ANÁLISIS AVANZADO</span>
            </div>
          </div>
        </div>

        {/* Métricas do Histórico */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <HistoricoMetricCard
            title="Total Llamadas"
            value={metrics.totalLlamadas.toLocaleString()}
            subtitle="En el período seleccionado"
            icon="📞"
            color="primary"
            loading={loading}
          />
          
          <HistoricoMetricCard
            title="Completadas"
            value={metrics.completadas.toLocaleString()}
            subtitle={`${metrics.totalLlamadas > 0 ? Math.round((metrics.completadas / metrics.totalLlamadas) * 100) : 0}% éxito`}
            icon="✅"
            color="success"
            trend={{ direction: 'up', value: '+15%' }}
            loading={loading}
          />
          
          <HistoricoMetricCard
            title="Fallidas"
            value={metrics.fallidas.toLocaleString()}
            subtitle={`${metrics.totalLlamadas > 0 ? Math.round((metrics.fallidas / metrics.totalLlamadas) * 100) : 0}% fallos`}
            icon="❌"
            color="warning"
            trend={{ direction: 'down', value: '-8%' }}
            loading={loading}
          />
          
          <HistoricoMetricCard
            title="Duración Promedio"
            value={metrics.promedioDuracion}
            subtitle="Tiempo por llamada"
            icon="⏱️"
            color="info"
            trend={{ direction: 'stable', value: '+2%' }}
            loading={loading}
          />
        </div>

        {/* Filtros Avançados */}
        <div className="card-glass p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🔍</span>
              <h3 className="text-lg font-bold text-white">Filtros Avanzados</h3>
            </div>
            <button
              onClick={handleResetFilters}
              className="btn-secondary text-xs px-3 py-1 flex items-center space-x-1"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span>Reset</span>
            </button>
          </div>
          
          <HistoricoFilters
            filters={filters}
            setFilters={setFilters}
            usuarios={usuarios}
            onExportCSV={handleExportCSV}
            isExporting={isExporting}
            onReset={handleResetFilters}
          />
        </div>
        
        {/* Error message */}
        {error && (
          <div className="bg-error-500/20 border border-error-500/50 text-error-200 px-6 py-4 rounded-xl text-sm backdrop-blur-sm animate-fade-in">
            <div className="flex items-center space-x-3">
              <svg className="w-5 h-5 text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Conteúdo Principal */}
        <div className="card-glass p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">📋</span>
              <h3 className="text-lg font-bold text-white">Registro de Llamadas</h3>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Paginação info */}
              <div className="text-xs text-secondary-400">
                Página {currentPage} de {totalPages}
              </div>
              
              {/* Botão Export */}
              <button
                onClick={handleExportCSV}
                disabled={isExporting || llamadas.length === 0}
                className="btn-secondary text-xs px-3 py-1 flex items-center space-x-1"
              >
                {isExporting ? (
                  <div className="w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin"></div>
                ) : (
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                )}
                <span>Exportar CSV</span>
              </button>
            </div>
          </div>
          
          {loading ? (
            <div className="flex justify-center py-16">
              <div className="text-center space-y-4">
                <div className="mx-auto w-16 h-16 bg-primary-500/20 rounded-2xl flex items-center justify-center">
                  <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-white mb-2">Cargando historial...</h3>
                  <p className="text-secondary-400">Analizando registros de llamadas</p>
                </div>
              </div>
          </div>
        ) : (
          <HistoricoLlamadasTable
            llamadas={llamadas}
            totalItems={totalItems}
            page={currentPage}
            totalPages={totalPages}
            onChangePage={handlePageChange}
            onViewDetails={handleViewDetails}
          />
        )}
      </div>
      
        {/* Estatísticas Adicionais */}
        {!loading && llamadas.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="card-glass p-6">
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-xl">📊</span>
                <h4 className="text-sm font-semibold text-white">Distribución por Estado</h4>
              </div>
              <div className="space-y-3">
                {['finalizada', 'fallida', 'en_progreso'].map(estado => {
                  const count = llamadas.filter(l => l.estado === estado).length;
                  const percentage = llamadas.length > 0 ? (count / llamadas.length) * 100 : 0;
                  const colors = {
                    finalizada: 'bg-success-500',
                    fallida: 'bg-error-500',
                    en_progreso: 'bg-warning-500'
                  };
                  
                  return (
                    <div key={estado} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-secondary-300 capitalize">{estado.replace('_', ' ')}</span>
                        <span className="text-white font-medium">{count}</span>
                      </div>
                      <div className="w-full bg-secondary-700 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-300 ${colors[estado] || 'bg-secondary-500'}`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            
            <div className="card-glass p-6">
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-xl">⏰</span>
                <h4 className="text-sm font-semibold text-white">Actividad por Hora</h4>
              </div>
              <div className="text-center py-8">
                <div className="text-4xl mb-2 opacity-50">📈</div>
                <p className="text-xs text-secondary-400">Gráfico disponible en próxima versión</p>
              </div>
            </div>
            
            <div className="card-glass p-6">
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-xl">🎯</span>
                <h4 className="text-sm font-semibold text-white">Performance</h4>
              </div>
              <div className="space-y-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary-400 mb-1">
                    {metrics.totalLlamadas > 0 ? Math.round((metrics.completadas / metrics.totalLlamadas) * 100) : 0}%
                  </div>
                  <p className="text-xs text-secondary-400">Taxa de éxito general</p>
                </div>
                
                <div className="pt-3 border-t border-secondary-700">
                  <div className="flex justify-between text-xs mb-2">
                    <span className="text-secondary-400">Objetivo:</span>
                    <span className="text-success-400">85%</span>
                  </div>
                  <div className="w-full bg-secondary-700 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full bg-gradient-to-r from-success-500 to-success-400 transition-all duration-300"
                      style={{ width: `${Math.min((metrics.completadas / metrics.totalLlamadas) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Modal de Detalhes */}
      <LlamadaDetalle
        llamadaId={selectedLlamadaId}
        isOpen={detailModalOpen}
        onClose={handleCloseDetails}
      />
    </div>
  );
};

export default HistoricoLlamadas; 