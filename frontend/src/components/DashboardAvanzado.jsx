import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const DashboardAvanzado = () => {
  const [stats, setStats] = useState({
    campanasActivas: 0,
    llamadasHoy: 0,
    agentesOnline: 0,
    tasaExito: 0,
    tasaConexion: 0,
    llamadasEnProgreso: 0,
    promedioEspera: 0,
    llamadasCompletadas: 0,
    llamadasPerdidas: 0,
    tiempoPromedioLlamada: 0,
    agentesDisponibles: 0,
    agentesOcupados: 0
  });

  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    // Cargar datos de múltiples APIs en paralelo - apenas endpoints existentes
  const cargarDatos = async () => {
    try {
      setLoading(true);
      
        // Llamadas a APIs en paralelo
        const requests = [
          makeApiRequest('/campanhas'),
          makeApiRequest('/llamadas/stats'),
        makeApiRequest('/monitoring/dashboard'),
          makeApiRequest('/llamadas/en-progreso'),
          makeApiRequest('/api/v1/stats')
        ];

        // Esperar todas las respuestas con timeout y manejar errores
        const responses = await Promise.allSettled(requests);
        
        // Procesar respuestas con valores por defecto
        const [campanasResult, llamadasResult, monitoringResult, llamadasProgresoResult, globalStatsResult] = responses;

        // Calcular estadísticas combinadas de las APIs disponibles
        let calculatedStats = {
          campanasActivas: 0,
          llamadasHoy: 0,
          agentesOnline: 0,
          tasaExito: 0,
          tasaConexion: 0,
          llamadasEnProgreso: 0,
          promedioEspera: 0,
          llamadasCompletadas: 0,
          llamadasPerdidas: 0,
          tiempoPromedioLlamada: 0,
          agentesDisponibles: 0,
          agentesOcupados: 0
        };

        // Procesar datos reales de las APIs
        if (campanasResult.status === 'fulfilled' && campanasResult.value && campanasResult.value.campaigns) {
          calculatedStats.campanasActivas = campanasResult.value.campaigns.length || 0;
        }

        if (llamadasResult.status === 'fulfilled' && llamadasResult.value && llamadasResult.value.stats) {
          const stats = llamadasResult.value.stats;
          calculatedStats.llamadasHoy = stats.calls_today || 0;
          calculatedStats.tasaExito = stats.success_rate_today || 0;
          calculatedStats.tiempoPromedioLlamada = stats.avg_duration || 0;
        }

        if (monitoringResult.status === 'fulfilled' && monitoringResult.value && monitoringResult.value.monitoring) {
          const monitoring = monitoringResult.value.monitoring;
          calculatedStats.agentesOnline = monitoring.active_connections || 0;
          calculatedStats.agentesDisponibles = monitoring.available_agents || 0;
          calculatedStats.agentesOcupados = monitoring.busy_agents || 0;
        }

        if (llamadasProgresoResult.status === 'fulfilled' && llamadasProgresoResult.value && llamadasProgresoResult.value.calls) {
          calculatedStats.llamadasEnProgreso = llamadasProgresoResult.value.calls.length || 0;
          // Calcular algunas estadísticas adicionales basadas en las llamadas en progreso
          calculatedStats.llamadasCompletadas = Math.max(0, calculatedStats.llamadasHoy - calculatedStats.llamadasEnProgreso);
          calculatedStats.llamadasPerdidas = llamadasProgresoResult.value.lost_calls || 0;
        }

        if (globalStatsResult.status === 'fulfilled' && globalStatsResult.value && globalStatsResult.value.stats) {
          const gStats = globalStatsResult.value.stats;
          // Usar estadísticas globales si están disponibles
          calculatedStats.tasaConexion = gStats.success_rate || calculatedStats.tasaExito;
          calculatedStats.promedioEspera = gStats.average_wait_time || 0;
        }

        setStats(calculatedStats);
        setLastUpdate(new Date());

    } catch (error) {
      console.error('Error cargando dashboard avanzado:', error);
        // Sistema en modo real - mostrar datos reales del backend
        // En caso de error, mantenemos los stats en 0
    } finally {
      setLoading(false);
    }
  };

    cargarDatos();
    const interval = setInterval(cargarDatos, 30000); // Actualizar cada 30 segundos
    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-white">📊 Dashboard Avanzado</h2>
          <p className="text-gray-300 mt-2">
            Última actualización: {lastUpdate.toLocaleTimeString('es-AR')}
          </p>
          {loading && (
            <div className="inline-flex items-center mt-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mr-2"></div>
              <span className="text-blue-300 text-sm">Actualizando datos...</span>
            </div>
          )}
        </div>

        {/* Estadísticas principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Campañas Activas */}
          <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-gray-300">Campañas Activas</p>
                <p className="text-3xl font-bold text-white">{stats.campanasActivas}</p>
            </div>
              <div className="p-3 bg-blue-500/20 rounded-lg">
                <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
          </div>
        </div>

          {/* Llamadas Hoy */}
          <div className="bg-gradient-to-r from-green-500/20 to-green-600/20 border border-green-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-gray-300">Llamadas Hoy</p>
                <p className="text-3xl font-bold text-white">{stats.llamadasHoy}</p>
            </div>
              <div className="p-3 bg-green-500/20 rounded-lg">
                <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
          </div>
        </div>

          {/* Agentes Online */}
          <div className="bg-gradient-to-r from-purple-500/20 to-purple-600/20 border border-purple-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-gray-300">Agentes Online</p>
                <p className="text-3xl font-bold text-white">{stats.agentesOnline}</p>
              </div>
              <div className="p-3 bg-purple-500/20 rounded-lg">
                <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Tasa de Éxito */}
          <div className="bg-gradient-to-r from-yellow-500/20 to-yellow-600/20 border border-yellow-500/30 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between">
                  <div>
                <p className="text-sm font-medium text-gray-300">Tasa de Éxito</p>
                <p className="text-3xl font-bold text-white">{stats.tasaExito}%</p>
                  </div>
              <div className="p-3 bg-yellow-500/20 rounded-lg">
                <svg className="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Estadísticas detalladas */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          
          {/* Panel de Llamadas */}
          <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
            <h3 className="text-xl font-semibold text-white mb-6">📞 Estadísticas de Llamadas</h3>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-lg">
                <span className="text-gray-300">Llamadas en Progreso</span>
                <span className="text-2xl font-bold text-blue-400">{stats.llamadasEnProgreso}</span>
        </div>

              <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-lg">
                <span className="text-gray-300">Llamadas Completadas</span>
                <span className="text-2xl font-bold text-green-400">{stats.llamadasCompletadas}</span>
      </div>

              <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-lg">
                <span className="text-gray-300">Llamadas Perdidas</span>
                <span className="text-2xl font-bold text-red-400">{stats.llamadasPerdidas}</span>
            </div>
            
              <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-lg">
                <span className="text-gray-300">Tiempo Promedio</span>
                <span className="text-2xl font-bold text-yellow-400">{formatTime(stats.tiempoPromedioLlamada)}</span>
                  </div>
            </div>
          </div>

          {/* Panel de Agentes */}
          <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
            <h3 className="text-xl font-semibold text-white mb-6">👥 Estado de Agentes</h3>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-lg">
                <span className="text-gray-300">Agentes Disponibles</span>
                <span className="text-2xl font-bold text-green-400">{stats.agentesDisponibles}</span>
        </div>

              <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-lg">
                <span className="text-gray-300">Agentes Ocupados</span>
                <span className="text-2xl font-bold text-orange-400">{stats.agentesOcupados}</span>
                      </div>
              
              <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-lg">
                <span className="text-gray-300">Promedio de Espera</span>
                <span className="text-2xl font-bold text-blue-400">{formatTime(stats.promedioEspera)}</span>
                    </div>
              
              <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-lg">
                <span className="text-gray-300">Tasa de Conexión</span>
                <span className="text-2xl font-bold text-purple-400">{stats.tasaConexion}%</span>
                  </div>
                </div>
          </div>
        </div>

        {/* Acción de refresco */}
        <div className="text-center">
          <button 
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors inline-flex items-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            🔄 Recargar Página
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardAvanzado; 